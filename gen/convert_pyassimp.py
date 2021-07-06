"""
Parse PyAssimp's structs.py and generate new-style struct definitions
for Impasse

TODO: Should be changed to parse the C headers directly. PyAssimp has
  a structsgen.py that's meant to do this, but it doesn't appear to
  work against assimp master, and its structs.py has actually been
  hand-edited.
"""

import ast
import collections
import inspect
import re
from typing import NamedTuple, Dict, Optional

import pyassimp.structs as s

TUPLE_STRUCTS = {
    "Matrix4x4": ("numpy.single", (4, 4), 16),
    "Matrix3x3": ("numpy.single", (3, 3), 9),
    "Vector2D": ("numpy.single", (2,), 2),
    "Vector3D": ("numpy.single", (3,), 3),
    "Color3D": ("numpy.single", (3,), 3),
    "Color4D": ("numpy.single", (4,), 4),
    "Quaternion": ("numpy.single", (4,), 4),
    "Plane": ("numpy.single", (2,), 2),
    "Texel": ("numpy.ubyte", (4,), 4),
}

SUPPORTS_MAPPING = {"Metadata", "Material"}


class FieldTypeData(NamedTuple):
    name: str
    base_name: str
    python_name: str
    full_sig: str
    pointer_type: str
    array_len: Optional[int]
    python_type_name: Optional[str]
    builtin: bool
    comments: str


class StructData(NamedTuple):
    name: str
    doc: str
    fields: Dict[str, FieldTypeData]


def scan_structs():
    # We need to read the AST if we want to pull comments and
    # figure out the original order of the structs.
    with open(s.__file__, "r") as f:
        source = f.read()

    field_locs = collections.defaultdict(dict)
    field_comments = collections.defaultdict(dict)
    structs_ast = ast.parse(source, s.__file__)
    struct_order = []

    def _process_fields(name, field_container):
        l: ast.List = field_container.value
        for o in l.elts:
            lineno = o.elts[0].lineno - 1
            locs = field_locs[name]
            # Already have an assignment on this line,
            # first assignment should get any of the comments.
            if lineno in locs.values():
                continue
            locs[o.elts[0].value] = lineno

    for ast_node in structs_ast.body:
        # Might be a Structure subclass
        if isinstance(ast_node, ast.ClassDef):
            struct_order.append(ast_node.name)
            for y in ast_node.body:
                if not isinstance(y, ast.Assign):
                    continue
                if y.targets[0].id != "_fields_":
                    continue
                _process_fields(ast_node.name, y)
        # Might be an assignment of `StructureSubclass._fields_`
        if isinstance(ast_node, ast.Assign):
            first_targ = ast_node.targets[0]
            if not isinstance(first_targ, ast.Attribute):
                continue
            if first_targ.attr != "_fields_":
                continue
            name: ast.Name = first_targ.value
            _process_fields(name.id, ast_node)

    split_lines = source.splitlines(keepends=False)
    for clazz, fields in field_locs.items():
        for field_name, lineno in fields.items():
            comment_lines = []
            while re.match(r"^\s*#", split_lines[lineno - 1]):
                comment_line = split_lines[lineno - 1].lstrip()
                if not comment_line.startswith("# "):
                    comment_line = re.sub(r"^#", "# ", comment_line)
                comment_line = comment_line.strip()
                if "_fields_" not in comment_line:
                    comment_lines.insert(0, comment_line)
                lineno -= 1
            field_comments[clazz][field_name] = comment_lines

    for struct_cls_name in struct_order:
        cls = getattr(s, struct_cls_name)
        fields = getattr(cls, "_fields_")
        cls_doc = inspect.getdoc(cls)

        fields_type_data: Dict[str, FieldTypeData] = {}
        for field_name, field_type in fields:
            split_name = field_type.__name__.split("_")
            ptr_prefix = ""
            builtin = False
            while split_name[0] == "LP":
                # LP_ classes are automatically generated pointer classes
                ptr_prefix += "*"
                split_name = split_name[1:]
            python_type_name = None
            if split_name[0] == "c":
                # from ctypes proper
                c_decl = split_name[1]
                if c_decl.startswith("u"):
                    c_decl = "unsigned " + c_decl[1:]
                if c_decl.endswith("byte"):
                    c_decl = c_decl.replace("byte", "char")
                split_name = [c_decl] + split_name[2:]
                while split_name[-1] == "p":
                    # _p suffix _also_ makes this a pointer
                    ptr_prefix += "*"
                    split_name = split_name[:-1]
                signless_type = c_decl.rpartition("unsigned ")[-1]
                if signless_type in ("int", "long", "long long"):
                    python_type_name = "int"
                elif signless_type == "char" and not ptr_prefix:
                    python_type_name = "int"
                elif signless_type in ("float", "double"):
                    python_type_name = "float"
                builtin = True
            else:
                # Not from ctypes, must be a struct from assimp.
                python_type_name = split_name[0]
                split_name = ["struct ai" + split_name[0]] + split_name[1:]
            suffix = ""
            array_len = None
            if len(split_name) > 1:
                if split_name[1] == "Array":
                    suffix = f"[{split_name[2]}]"
                    array_len = int(split_name[2])
                    split_name = [split_name[0]]
                else:
                    raise ValueError(split_name[1])
            full_sig = f"{split_name[0]} {ptr_prefix}{field_name}{suffix}"
            python_field_name = field_name
            base_name = field_name
            rewrite_name = False
            if field_name.startswith("m") and field_name[1].upper() == field_name[1]:
                base_name = field_name[1:]
                rewrite_name = True
            elif field_name == "achFormatHint":
                rewrite_name = True
            elif field_name == "pcData":
                base_name = "data"
                rewrite_name = True

            if rewrite_name:
                a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
                python_field_name = a.sub(r"_\1", base_name).lower()
            fields_type_data[field_name] = FieldTypeData(
                field_name,
                base_name,
                python_field_name,
                full_sig,
                ptr_prefix,
                array_len,
                python_type_name,
                builtin,
                field_comments[struct_cls_name].get(field_name, [])
            )
        yield StructData(struct_cls_name, cls_doc, fields_type_data)


def print_code():
    print("from .structs_base import *\n\nC_SRC = \"\"\n\n")

    for struct_data in scan_structs():
        struct_cls_name = struct_data.name
        fields_type_data = struct_data.fields
        print("C_SRC += \"\"\"")
        escaped_doc = struct_data.doc.replace('\n', '\n// ')
        print(f"// {escaped_doc}")
        print(f"struct ai{struct_cls_name} {{")
        for field in fields_type_data.values():
            print(f"    {field.full_sig};")
        print(f"}};")
        print("\"\"\"\n\n")
        base_wrapper_cls = "SerializableStruct"
        if struct_cls_name in TUPLE_STRUCTS:
            base_wrapper_cls = "NumPyAdapter"
        print(f"class {struct_cls_name}({base_wrapper_cls}):")
        print("    __slots__ = ()")
        print(f"    C_TYPE = \"struct ai{struct_cls_name}\"")
        if struct_cls_name in TUPLE_STRUCTS:
            tuple_dets = TUPLE_STRUCTS[struct_cls_name]
            print(f"    SHAPE = {tuple_dets[1]!r}")
            print(f"    DTYPE = {tuple_dets[0]}")
        print("")
        first_field = True
        for field_name, type_data in fields_type_data.items():
            # Pythonize the field names
            call_spec = ""
            if type_data.python_name != type_data.name:
                call_spec = f"name={field_name!r}"
            comment_lines = type_data.comments
            if comment_lines:
                if not first_field:
                    print()
                for comment_line in comment_lines:
                    print(f"    {comment_line}")
            type_sig = "Any"
            accessor_name = "SimpleAccessor"
            if type_data.python_type_name:
                type_sig = type_data.python_type_name
                if type_sig == struct_cls_name:
                    type_sig = repr(type_sig)
            adapter_name = type_data.python_type_name
            if adapter_name == struct_cls_name:
                adapter_name = f"LazyStruct(lambda: {adapter_name})"
            if type_data.python_type_name == "String":
                adapter_name = "StringAdapter"
                type_sig = "str"
            elif adapter_name in TUPLE_STRUCTS:
                type_sig = "numpy.ndarray"

            if type_data.builtin:
                adapter_name = "None"
            num_elem_field = None
            accessor = None
            if type_data.array_len:
                type_sig = f"Sequence[{type_sig}]"
                accessor = f"StaticSequenceAccessor({field_name!r}, {type_data.array_len}, {adapter_name})"
            elif "mNum" + type_data.base_name in fields_type_data:
                num_elem_field = "mNum" + type_data.base_name
            elif struct_cls_name in ("Mesh", "AnimMesh"):
                if field_name in ("mNormals", "mTangents", "mBitangents"):
                    num_elem_field = "mNumVertices"
            elif struct_cls_name == "Metadata":
                if field_name in ("mKeys", "mValues"):
                    num_elem_field = "mNumProperties"

            if num_elem_field:
                type_sig = f"Sequence[{type_sig}]"
                accessor = f"DynamicSequenceAccessor({field_name!r}, {num_elem_field!r}, {adapter_name})"
            elif type_data.pointer_type:
                type_sig = f"Optional[{type_sig}]"

            if struct_cls_name == "Texture" and field_name == "achFormatHint":
                type_sig = "str"
                accessor = f"SimpleAccessor(name={field_name!r}, adapter=CStrAdapter({type_data.array_len}))"

            if struct_cls_name == "Texture" and field_name == "pcData":
                type_sig = "Union[bytearray, numpy.ndarray]"
                accessor = "TextureDataAccessor()"
            elif struct_cls_name in ("Mesh", "AnimMesh") and field_name in ("mTextureCoords", "mColors"):
                # List of lists, so wrap again
                type_sig = f"Sequence[{type_sig}]"
                accessor = f"VertexPropSequenceAccessor({field_name!r}, {type_data.array_len}, {adapter_name})"
            elif struct_cls_name == "MaterialProperty" and field_name == "mData":
                type_sig = f"Any"
                accessor = "MaterialPropertyDataAccessor()"
            elif struct_cls_name == "MetadataEntry" and field_name == "mData":
                type_sig = f"Any"
                accessor = "MetadataEntryDataAccessor()"
            elif type_data.full_sig.startswith("struct "):
                if call_spec:
                    call_spec += ", "
                call_spec += f"adapter={adapter_name}"

            if accessor is None:
                accessor = f"{accessor_name}({call_spec})"
            print(f"    {type_data.python_name}: {type_sig} = {accessor}")
            first_field = False
        # TODO: Mix-in classes instead?
        if "mName" in fields_type_data:
            print("")
            print("    def __repr__(self):")
            print("        return f'{self.__class__.__name__}<name={self.name!r}>'")
        if struct_cls_name in SUPPORTS_MAPPING:
            print("")
            print(f"    def as_mapping(self) -> {struct_cls_name}Mapping:")
            print(f"        return {struct_cls_name}Mapping(self)")
        print("\n")
    print("ffi.cdef(FUNCTION_DECLS + C_SRC)")


if __name__ == "__main__":
    print_code()
