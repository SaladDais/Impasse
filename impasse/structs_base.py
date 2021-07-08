from __future__ import annotations

import abc
from typing import *

import cffi
import numpy

from .constants import MaterialPropertyType, MetadataType, TextureSemantic

if TYPE_CHECKING:
    from .structs import Texture, MaterialProperty, MetadataEntry, Material, Scene, Mesh

ffi = cffi.FFI()


class CSerializableBase(abc.ABC):
    __slots__ = ()

    @classmethod
    @abc.abstractmethod
    def from_c(cls, val, scene: Optional[Scene] = None):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def to_c(cls, instance, val):
        raise NotImplementedError()


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
        if self.C_TYPE == "struct aiScene":
            return self  # noqa
        return self._scene

    @property
    def readonly(self):
        return self._readonly

    def __eq__(self, other: Any):
        if not isinstance(other, SerializableStruct):
            return NotImplemented
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


class NumPyStruct(SerializableStruct):
    SHAPE: ClassVar[Tuple[int, ...]]
    DTYPE: ClassVar[numpy.dtype]
    NUM_ELEMS: int

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
    def to_c(cls, instance, val: Union[numpy.ndarray, NumPyStruct]):
        if isinstance(val, NumPyStruct):
            return super().to_c(instance, val)

        if val.size != cls.NUM_ELEMS:
            raise ValueError(f"{val.size} != {cls.NUM_ELEMS}")
        if val.dtype != cls.DTYPE:
            # Likely to happen if you didn't specify a dtype and your native dtype
            # is different from that of the struct.
            val = val.astype(cls.DTYPE)
        ffi.buffer(instance, cls.get_size())[:] = val.flatten().data

    @classmethod
    def struct_from_c(cls, struct_val, scene: Optional[Scene] = None):
        """
        Fetch the actual struct from cdata

        Should be infrequently needed, but there may be some functions that require
        passing the struct itself.
        """
        return super().from_c(struct_val, scene)


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


class MeshIndexAdapter(CSerializableBase):
    @classmethod
    def from_c(cls, val: int, scene: Optional[Scene] = None):
        if scene is None:
            raise ValueError("scene may not be None")
        return scene.meshes[val]

    @classmethod
    def to_c(cls, instance, val: Union[int, Mesh]):
        if not isinstance(val, int):
            val = val.get_scene().meshes.index(val)
        instance[0] = val


class MaterialIndexAdapter(CSerializableBase):
    @classmethod
    def from_c(cls, val: int, scene: Optional[Scene] = None):
        if scene is None:
            raise ValueError("scene may not be None")
        return scene.materials[val]

    @classmethod
    def to_c(cls, instance, val: Union[int, Material]):
        if not isinstance(val, int):
            val = val.get_scene().materials.index(val)
        instance[0] = val


class TextureIndexAdapter(CSerializableBase):
    @classmethod
    def from_c(cls, val: int, scene: Optional[Scene] = None):
        if scene is None:
            raise ValueError("scene may not be None")
        if not val:
            return None
        # "No texture" is specified by setting 0, so all indexes are shifted up by 1
        return scene.textures[val - 1]

    @classmethod
    def to_c(cls, instance, val: Union[int, Texture]):
        if val is None:
            val = 0
        elif not isinstance(val, int):
            val = val.get_scene().textures.index(val) + 1
        instance[0] = val


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
            if 0 > i or i >= len(self):
                raise IndexError(f"{i} is out of range")
            val = self.elems_ptr[i]
            return self.elem_adapter.from_c(val, self._scene)
        return [self[idx] for idx in range(*i.indices(len(self)))]

    def __setitem__(self, key: int, value: _T):
        if self._scene is not None and self._scene.readonly:
            raise KeyError("Refusing to write to Sequence belonging to readonly scene")
        if 0 > key or key >= len(self):
            raise IndexError(f"{key} is out of range")
        elem_addr = ffi.addressof(self.elems_ptr, key)
        self.elem_adapter.to_c(elem_addr, value)

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


_K = TypeVar("_K")
_V = TypeVar("_V")


class SerializableMapping(SerializableStruct, Mapping[_K, _V], abc.ABC):
    def __repr__(self):
        return f"{self.__class__.__name__}<{dict(self)!r}>"

    def __eq__(self, other):
        # Try to do a struct-wise compare first
        val = SerializableStruct.__eq__(self, other)
        if val is not NotImplemented:
            return val
        return Mapping.__eq__(self, other)


class BaseAccessor(Generic[_T], abc.ABC):
    __slots__ = ("name",)

    def __init__(self, name: Optional[str] = None):
        self.name = name

    def __set_name__(self, owner, name: str):
        if self.name is None:
            self.name = name


class SimpleAccessor(BaseAccessor[_T]):
    """Accessor that doesn't need any context outside its own value"""

    __slots__ = ("adapter",)

    def __init__(self, name: Optional[str] = None, adapter=None):
        super().__init__(name)
        self.adapter = adapter or IdentityAdapter

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


class StaticSequenceAccessor(BaseAccessor[_SEQ_T]):
    __slots__ = ("size", "elem_adapter")

    def __init__(self, name: str, size: int, elem_adapter: Type[_T]):
        super().__init__(name)
        self.size = size
        self.elem_adapter = elem_adapter

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> _SEQ_T:
        return StaticSequence(
            getattr(obj.struct, self.name),
            self.size,
            self.elem_adapter
        )


class DynamicSequenceAccessor(BaseAccessor[_SEQ_T]):
    __slots__ = ("num_name", "elem_adapter")

    def __init__(self, name: str, num_name: str, elem_adapter):
        super().__init__(name)
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


class TextureDataAccessor(SimpleAccessor[Union[bytes, numpy.ndarray]]):
    __slots__ = ()

    def __get__(self, obj: Texture, owner: Optional[Type] = None) -> Union[bytes, numpy.ndarray]:
        scene = obj.get_scene()
        pcdata = obj.struct.pcData
        assert pcdata
        if obj.height:
            # Uncompressed RGBA8888
            # This is actually an aiTexel, a struct of 4 bytes, but the structs
            # are explicitly packed so we can treat as a contiguous byte array.
            buf = ffi.buffer(pcdata, obj.height * obj.width * 4)
            val = numpy.ndarray(buffer=buf, dtype=numpy.ubyte, shape=(obj.height, obj.width, 4))
            val.flags.writeable = scene is None or not scene.readonly
            return val

        # Compressed data
        return bytes(ffi.buffer(pcdata, obj.width))

    def __set__(self, instance, value):
        raise NotImplementedError()


class BoundedBufferAccessor(SimpleAccessor[bytearray]):
    __slots__ = ("size_name",)

    def __init__(self, name: str, size_name: str):
        super().__init__(name)
        self.size_name = size_name

    def __get__(self, obj: SerializableStruct, owner: Optional[Type] = None) -> bytearray:
        # Compressed data
        buf_ptr = getattr(obj.struct, self.name)
        size = getattr(obj.struct, self.size_name)
        return bytearray(ffi.buffer(buf_ptr, size))

    def __set__(self, instance, value):
        raise NotImplementedError()


# Metadata-specific accessors and wrappers

METADATA_VAL = Union[float, int, bool, str, Any]  # How to represent cffi cdata?


class MetadataEntryDataAccessor(SimpleAccessor[METADATA_VAL]):
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
        elif meta_type == MetadataType.AISTRING:
            StringAdapter.to_c(ffi.cast("struct aiString*", data), value)
        else:
            raise NotImplementedError()


class MetadataMapping(SerializableMapping[str, METADATA_VAL], abc.ABC):
    num_properties: int
    meta_keys: BaseSequence[str]
    meta_values: BaseSequence[MetadataEntry]

    def __len__(self) -> int:
        return self.num_properties

    def __iter__(self) -> Iterator[str]:
        return iter(self.meta_keys)

    def __getitem__(self, item: str) -> METADATA_VAL:
        for i, k in enumerate(self.meta_keys):
            if k == item:
                return self.meta_values[i].data
        raise KeyError(repr(item))

    def __setitem__(self, item: str, value: METADATA_VAL):
        for i, k in enumerate(self.meta_keys):
            if k == item:
                self.meta_values[i].data = value
                return
        raise KeyError(repr(item))


# Materials-specific accessors and wrappers
MATERIAL_PROP_VALUE = Union[numpy.ndarray, str, bytes, int, float]
SETTABLE_MATERIAL_PROP_VALUE = Union[MATERIAL_PROP_VALUE, Sequence[float], Sequence[int]]


class MaterialPropertyDataAccessor(SimpleAccessor[MATERIAL_PROP_VALUE]):
    __slots__ = ()

    ARRAY_ELEM_TYPES = {
        MaterialPropertyType.FLOAT: (ffi.sizeof("float"), numpy.single),
        MaterialPropertyType.DOUBLE: (ffi.sizeof("double"), numpy.double),
        MaterialPropertyType.INT: (ffi.sizeof("int"), numpy.intc),
    }

    def __get__(self, obj: MaterialProperty, owner=None) -> MATERIAL_PROP_VALUE:
        size = obj.struct.mDataLength
        buf = ffi.buffer(obj.struct.mData, size)
        if obj.struct.mType in self.ARRAY_ELEM_TYPES:
            elem_size, numpy_elem_type = self.ARRAY_ELEM_TYPES[obj.struct.mType]
            arr_size = len(buf) // elem_size
            arr = numpy.ndarray(buffer=buf, dtype=numpy_elem_type, shape=(arr_size,))
            # There are only _arrays_ of floats and ints, unwrap single-element arrays
            # Since their array-ness isn't likely semantically significant.
            if arr_size == 1:
                return arr[0]
            arr.flags.writeable = not obj.readonly
            return arr
        elif obj.struct.mType == MaterialPropertyType.AISTRING:
            return StringAdapter.from_c(ffi.cast("struct aiMaterialPropertyString *", obj.struct.mData))
        elif obj.struct.mType == MaterialPropertyType.BINARY:
            if size == 1:
                # Probably a bool
                return buf[0][0]
            return bytes(buf)
        else:
            raise ValueError(f"Unknown material property type {obj.struct.mType}")

    def __set__(self, obj: MaterialProperty, value: SETTABLE_MATERIAL_PROP_VALUE):
        if obj.readonly:
            raise AttributeError("Trying to write to readonly material")

        buf = ffi.buffer(obj.struct.mData, obj.struct.mDataLength)
        if obj.struct.mType in self.ARRAY_ELEM_TYPES:
            if isinstance(value, (float, int)):
                value = [value]
            elem_size, numpy_elem_type = self.ARRAY_ELEM_TYPES[obj.struct.mType]
            arr_size = len(buf) // elem_size
            if len(value) != arr_size:
                raise ValueError(f"Expected array length mismatch, {len(value)} != {arr_size}")
            arr = numpy.array(value, dtype=numpy_elem_type)
            buf[:] = arr.flatten().data
            return arr
        elif obj.struct.mType == MaterialPropertyType.AISTRING:
            str_ptr = ffi.cast("struct aiMaterialPropertyString *", obj.struct.mData)
            StringAdapter.to_c(str_ptr, value)
            # data length only reflects the parts of the struct we're using,
            # not the actual alloc size.
            obj.struct.mDataLength = str_ptr.length + 1 + ffi.sizeof("int")
        elif obj.struct.mType == MaterialPropertyType.BINARY:
            if not isinstance(value, (bytes, memoryview, bytearray)):
                value = bytes((value,))
            # Will error if not the same length as the existing data
            # Seems like this type is mostly used for ints anyway.
            buf[:] = value
        else:
            raise ValueError(f"Unknown material property type {obj.struct.mType}")


REAL_PROPERTY_KEY = Tuple[str, Union[TextureSemantic, int]]
PROPERTY_KEY = Union[str, REAL_PROPERTY_KEY]


class MaterialMapping(SerializableMapping[PROPERTY_KEY, MATERIAL_PROP_VALUE], abc.ABC):
    properties: BaseSequence[MaterialProperty]

    def __len__(self) -> int:
        return len(self.properties)

    def __iter__(self) -> Iterator[REAL_PROPERTY_KEY]:
        return iter(((p.key, p.semantic) for p in self.properties))

    def _get_prop(self, key: PROPERTY_KEY) -> MaterialProperty:
        if isinstance(key, str):
            item, semantic = key, TextureSemantic.NONE
        else:
            item, semantic = key
        for prop in self.properties:
            if prop.semantic == semantic and prop.key == item:
                return prop
        raise KeyError(repr((item, semantic)))

    def __getitem__(self, item: PROPERTY_KEY) -> MATERIAL_PROP_VALUE:
        return self._get_prop(item).data

    def __setitem__(self, item: PROPERTY_KEY, value: SETTABLE_MATERIAL_PROP_VALUE):
        self._get_prop(item).data = value


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

void aiCopyScene(const struct aiScene *pIn,
        struct aiScene **pOut);

void aiFreeScene(const struct aiScene *pIn);
"""
