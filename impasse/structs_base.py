from __future__ import annotations

import abc
import math
from typing import *

import cffi
import numpy

from .constants import MaterialPropertyType, MetadataType, TextureSemantic

if TYPE_CHECKING:
    from .structs import Texture, MaterialProperty, MetadataEntry, Material, Metadata, Scene

ffi = cffi.FFI()


class CSerializableBase(abc.ABC):
    __slots__ = ()

    @classmethod
    @abc.abstractmethod
    def from_c(cls, val, scene: Optional[Scene] = None):
        pass

    @classmethod
    @abc.abstractmethod
    def to_c(cls, instance, val):
        pass


class IdentityAdapter(CSerializableBase):
    @classmethod
    def from_c(cls, val, scene: Optional[Scene] = None):
        return val

    @classmethod
    def to_c(cls, instance, val):
        instance[0] = val


class ExprAdapter(CSerializableBase):
    __slots__ = ("from_c_expr",)

    def __init__(self, from_c_expr=None):
        self.from_c_expr = from_c_expr

    def from_c(self, val, scene: Optional[Scene] = None):
        return self.from_c_expr(val, scene)

    def to_c(self, instance, val):
        raise NotImplementedError()


class SerializableStruct(CSerializableBase):
    C_TYPE: ClassVar[str]

    def __init__(self, struct_val, scene: Optional[Scene] = None):
        self.struct: Any = struct_val
        # Strong reference Scene has no strong references to its own children
        # and cleanup is managed through owning Scene's destruction.
        self._scene = scene
        self._readonly = scene.readonly if scene is not None else False

    @classmethod
    def from_c(cls, struct_val, scene: Optional[Scene] = None):
        # Null pointer
        if not struct_val:
            return None
        return cls(struct_val, scene)

    @classmethod
    def to_c(cls, instance, struct_val: Optional[SerializableStruct]):
        if struct_val is None:
            return None
        instance[0] = struct_val.struct

    @classmethod
    def from_address(cls, address: int):
        return cls.from_c(ffi.cast(ffi.getctype(cls.C_TYPE, "*"), address))

    def get_scene(self) -> Optional[Scene]:
        if self.__class__.__name__ == "Scene":
            return self  # noqa
        return self._scene

    @property
    def readonly(self):
        return self._readonly

    def __eq__(self, other: Any):
        if not isinstance(other, SerializableStruct):
            return False
        return other.struct == self.struct


class LazyStruct(NamedTuple):
    """Necessary wrapper for self-referential structs that force late binding"""
    lazy: Callable[[], Type[SerializableStruct]]


class CStrAdapter(CSerializableBase):
    __slots__ = ("max_len",)

    def __init__(self, max_len: int = -1):
        self.max_len = max_len

    def from_c(self, val, scene: Optional[Scene] = None):
        return ffi.string(val, self.max_len).decode("utf8")

    def to_c(self, instance, val):
        raise NotImplementedError()


class NumPyAdapter(SerializableStruct):
    SHAPE: ClassVar[Tuple[int, ...]]
    DTYPE: ClassVar[numpy.dtype]

    @classmethod
    def get_size(cls):
        ctype = ffi.getctype(cls.C_TYPE)
        return ffi.sizeof(ctype)

    @classmethod
    def from_c(cls, struct_val, scene: Optional[Scene] = None):
        buf = ffi.buffer(ffi.addressof(struct_val), cls.get_size())
        arr = numpy.ndarray(buffer=buf, shape=cls.SHAPE, dtype=cls.DTYPE)
        arr.flags.writeable = scene is None or not scene.readonly
        return arr

    @classmethod
    def to_c(cls, instance, val: numpy.ndarray):
        if val.dtype != cls.DTYPE:
            raise ValueError(f"{val.dtype} != {cls.DTYPE}")
        if val.size != math.prod(cls.SHAPE):
            raise ValueError(f"{val.size} != {math.prod(cls.SHAPE)}")
        ffi.buffer(instance, cls.get_size())[:] = val.flatten().data


class StringAdapter(SerializableStruct):
    @classmethod
    def from_c(cls, struct_val, scene: Optional[Scene] = None):
        return ffi.string(struct_val.data, struct_val.length).decode("utf8", errors="replace")

    @classmethod
    def to_c(cls, instance, value: Union[str, bytes]):
        length = len(value)
        if isinstance(value, str):
            value = value.encode("utf8") + b"\x00"
            length = len(value) - 1
        instance.data = value
        instance.length = length


_T = TypeVar("_T")
_SEQ_T = TypeVar("_SEQ_T", bound=Sequence)


class BaseSequence(Sequence[_T], abc.ABC):
    __slots__ = ("elems_ptr", "elem_adapter", "_scene")

    def __init__(self, elems_ptr, elem_adapter, scene: Optional[Scene] = None):
        super().__init__()
        self.elems_ptr = elems_ptr
        if isinstance(elem_adapter, LazyStruct):
            elem_adapter = elem_adapter.lazy()
        self.elem_adapter = elem_adapter or IdentityAdapter
        self._scene = scene

    def __getitem__(self, i: Union[slice, int]) -> Union[_T, List[_T]]:
        if isinstance(i, int):
            if i < len(self):
                val = self.elems_ptr[i]
                return self.elem_adapter.from_c(val, self._scene)
            raise IndexError(f"{i} is out of range")
        return [self[idx] for idx in range(*i.indices(len(self)))]

    def __repr__(self):
        return f"{self.__class__.__name__}<{tuple(self)!r}>"


class DynamicSequence(BaseSequence):
    __slots__ = ("size_ptr",)

    def __init__(self, elems_ptr, size_ptr, elem_adapter, scene: Optional[Scene] = None):
        super().__init__(elems_ptr, elem_adapter, scene)
        self.size_ptr = size_ptr

    def __len__(self) -> int:
        # null pointer means 0 len even if the size ptr says otherwise
        if not self.elems_ptr:
            return 0
        return self.size_ptr[0]


class StaticSequence(BaseSequence):
    __slots__ = ("size", "falsy_elem_terminates")

    def __init__(self, elems_ptr, size: int, elem_adapter,
                 scene: Optional[Scene] = None, falsy_elem_terminates=False):
        super().__init__(elems_ptr, elem_adapter, scene)
        self.size = size
        self.falsy_elem_terminates = falsy_elem_terminates

    def __len__(self) -> int:
        if self.falsy_elem_terminates:
            for i, val in enumerate(self.elems_ptr):
                if not val:
                    return i
        return self.size


class SimpleAccessor(Generic[_T]):
    """Accessor that doesn't need any context outside its own value"""

    __slots__ = ("name", "adapter")

    def __init__(self, name: Optional[str] = None, adapter=None):
        self.name = name
        self.adapter = adapter or IdentityAdapter

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

    def _unwrap_adapter(self):
        if isinstance(self.adapter, LazyStruct):
            self.adapter = self.adapter.lazy()

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> _T:
        self._unwrap_adapter()
        val = getattr(obj.struct, self.name)
        return self.adapter.from_c(val, scene=obj.get_scene())

    def __set__(self, obj: SerializableStruct, val: Any):
        if obj.readonly:
            raise AttributeError(f"{obj!r} belongs to a readonly scene, can't assign {self.name}")
        self._unwrap_adapter()
        self.adapter.to_c(ffi.addressof(obj.struct, self.name), val)


class StaticSequenceAccessor(Generic[_SEQ_T]):
    __slots__ = ("name", "size", "elem_adapter")

    def __init__(self, name: str, size: int, elem_adapter: Type[_T]):
        self.name = name
        self.size = size
        self.elem_adapter = elem_adapter

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> _SEQ_T:
        return StaticSequence(
            getattr(obj.struct, self.name),
            self.size,
            self.elem_adapter
        )


class DynamicSequenceAccessor(Generic[_SEQ_T]):
    __slots__ = ("name", "num_name", "elem_adapter")

    def __init__(self, name: str, num_name: str, elem_adapter):
        self.name = name
        self.num_name = num_name
        self.elem_adapter = elem_adapter

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> _SEQ_T:
        return DynamicSequence(
            getattr(obj.struct, self.name),
            # Get pointer of size field so we can take note of changes
            ffi.cast("unsigned int *", ffi.addressof(obj.struct, self.num_name)),
            self.elem_adapter,
            scene=obj.get_scene(),
        )


class VertexPropSequenceAccessor(StaticSequenceAccessor):
    __slots__ = ()

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> _SEQ_T:
        vertices_ptr = ffi.cast("unsigned int *", ffi.addressof(obj.struct, "mNumVertices"))
        serializer = ExprAdapter(
            lambda x, scene: DynamicSequence(x, vertices_ptr, self.elem_adapter, scene=scene)
        )
        return StaticSequence(
            getattr(obj.struct, self.name),
            self.size,
            serializer,
            scene=obj.get_scene(),
            falsy_elem_terminates=True,
        )


class TextureDataAccessor(SimpleAccessor):
    __slots__ = ()

    def __get__(self, obj: Texture, owner: Optional[Type] = None) -> Union[bytearray, numpy.array]:
        pcdata = obj.struct.pcData
        assert pcdata
        if obj.height:
            # Uncompressed RGBA8888
            pixels = []
            for i in range(obj.width * obj.height):
                p = pcdata[i]
                pixels.extend((p.r, p.g, p.b, p.a))
            return numpy.array(pixels, dtype=numpy.ubyte).reshape((obj.height, obj.width, 4))

        # Compressed data
        return bytearray(ffi.buffer(pcdata, obj.width))

    def __set__(self, instance, value):
        raise NotImplementedError()


# Metadata-specific accessors and wrappers

METADATA_VAL = Union[float, int, bool, str, Any]  # How to represent cffi cdata?


class MetadataEntryDataAccessor(SimpleAccessor):
    __slots__ = ()

    _BASIC_TYPES = {
        MetadataType.FLOAT: ffi.getctype("float*"),
        MetadataType.INT32: ffi.getctype("int32_t*"),
        MetadataType.DOUBLE: ffi.getctype("double*"),
        MetadataType.UINT64: ffi.getctype("uint64_t*"),
        MetadataType.BOOL: ffi.getctype("unsigned char*"),
    }

    def __get__(self, instance: MetadataEntry, owner=None) -> METADATA_VAL:
        meta_type = instance.struct.mType
        data = getattr(instance.struct, "mData")
        if meta_type in self._BASIC_TYPES:
            return ffi.cast(self._BASIC_TYPES[meta_type], data)[0]
        elif meta_type == MetadataType.AISTRING:
            return StringAdapter.from_c(ffi.cast("struct aiString*", data))
        else:
            return instance.struct.mData

    def __set__(self, instance: MetadataEntry, value: METADATA_VAL):
        if instance.readonly:
            raise AttributeError(f"{instance!r} belongs to a readonly scene, can't assign {self.name}")
        meta_type = instance.struct.mType
        data = getattr(instance.struct, "mData")
        if meta_type in self._BASIC_TYPES:
            ffi.cast(self._BASIC_TYPES[meta_type], data)[0] = value
        elif MetadataType == MetadataType.AISTRING:
            return StringAdapter.to_c(ffi.cast("struct aiString*", data), value)
        else:
            raise NotImplementedError()


class MetadataMapping(Mapping[str, METADATA_VAL]):
    __slots__ = ("metadata",)

    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def __len__(self) -> int:
        return self.metadata.num_properties

    def __iter__(self) -> Iterator[str]:
        return iter(self.metadata.keys)

    def __getitem__(self, item: str) -> METADATA_VAL:
        for i, k in enumerate(self.metadata.keys):
            if k == item:
                return self.metadata.values[i].data
        raise KeyError(repr(item))


# Materials-specific accessors and wrappers

class MaterialPropertyDataAccessor(SimpleAccessor):
    __slots__ = ()

    ARRAY_ELEM_TYPES = {
        MaterialPropertyType.FLOAT: (ffi.sizeof("float"), numpy.single),
        MaterialPropertyType.DOUBLE: (ffi.sizeof("double"), numpy.double),
        MaterialPropertyType.INT: (ffi.sizeof("int"), numpy.intc),
    }

    def __get__(self, obj: MaterialProperty, owner=None) -> Union[numpy.ndarray, str, bytes]:
        buf = ffi.buffer(obj.struct.mData, obj.struct.mDataLength)
        if obj.struct.mType in self.ARRAY_ELEM_TYPES:
            elem_size, numpy_elem_type = self.ARRAY_ELEM_TYPES[obj.struct.mType]
            arr = numpy.ndarray(buffer=buf, dtype=numpy_elem_type, shape=(len(buf) // elem_size,))
            arr.flags.writeable = not obj.readonly
            return arr
        elif obj.struct.mType == MaterialPropertyType.AISTRING:
            return StringAdapter.from_c(ffi.cast("struct aiMaterialPropertyString *", obj.struct.mData))
        elif obj.struct.mType == MaterialPropertyType.BINARY:
            return bytes(buf)
        else:
            raise ValueError(f"Unknown material property type {obj.struct.mType}")

    def __set__(self, instance, value):
        raise NotImplementedError()


REAL_PROPERTY_KEY = Tuple[str, Union[TextureSemantic, int]]
PROPERTY_KEY = Union[str, Tuple[str, REAL_PROPERTY_KEY]]
PROPERTY_VAL = Union[numpy.ndarray, str, bytes]


class MaterialMapping(Mapping[PROPERTY_KEY, PROPERTY_VAL]):
    __slots__ = ("material",)

    def __init__(self, material: Material):
        self.material = material

    def __len__(self) -> int:
        return self.material.num_properties

    def __iter__(self) -> Iterator[REAL_PROPERTY_KEY]:
        return iter(((p.key, p.semantic) for p in self.material.properties))

    def __getitem__(self, item: PROPERTY_KEY) -> PROPERTY_VAL:
        semantic = TextureSemantic.NONE
        if not isinstance(item, str):
            item, semantic = item
        for prop in self.material.properties:
            if prop.semantic == semantic and prop.key == item:
                return prop.data
        raise KeyError(repr((item, semantic)))


FUNCTION_DECLS = """
typedef enum aiReturn {
    aiReturn_SUCCESS = 0x0,
    aiReturn_FAILURE = -0x1,
    aiReturn_OUTOFMEMORY = -0x3,
    _AI_ENFORCE_ENUM_SIZE = 0x7fffffff
} aiReturn;

const struct aiScene *aiImportFile(
    const char *pFile,
    unsigned int pFlags
);

void aiReleaseImport(const struct aiScene *pScene);

const struct aiScene *aiImportFileFromMemory(
    const char *pBuffer,
    unsigned int pLength,
    unsigned int pFlags,
    const char *pHint
);

aiReturn aiExportScene(
    const struct aiScene *pScene,
    const char *pFormatId,
    const char *pFileName,
    unsigned int pPreprocessing
);

const struct aiExportDataBlob *aiExportSceneToBlob(
    const struct aiScene *pScene,
    const char *pFormatId,
    unsigned int pPreprocessing
);

void aiReleaseExportBlob(const struct aiExportDataBlob *pData);
"""
