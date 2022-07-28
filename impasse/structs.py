from __future__ import annotations

from .structs_base import *

C_SRC = ""


C_SRC += """
// See 'vector2.h' for details.
struct aiVector2D {
    float x;
    float y;
};
"""


class Vector2D(NumPyStruct):
    __slots__ = ()
    C_TYPE = "struct aiVector2D"
    SHAPE = (2,)
    DTYPE = numpy.single
    NUM_ELEMS = 2

    x: float = SimpleAccessor()
    y: float = SimpleAccessor()


C_SRC += """
// See 'matrix3x3.h' for details.
struct aiMatrix3x3 {
    float a1;
    float a2;
    float a3;
    float b1;
    float b2;
    float b3;
    float c1;
    float c2;
    float c3;
};
"""


class Matrix3x3(NumPyStruct):
    __slots__ = ()
    C_TYPE = "struct aiMatrix3x3"
    SHAPE = (3, 3)
    DTYPE = numpy.single
    NUM_ELEMS = 9

    a1: float = SimpleAccessor()
    a2: float = SimpleAccessor()
    a3: float = SimpleAccessor()
    b1: float = SimpleAccessor()
    b2: float = SimpleAccessor()
    b3: float = SimpleAccessor()
    c1: float = SimpleAccessor()
    c2: float = SimpleAccessor()
    c3: float = SimpleAccessor()


C_SRC += """
// See 'texture.h' for details.
struct aiTexel {
    unsigned char b;
    unsigned char g;
    unsigned char r;
    unsigned char a;
};
"""


class Texel(NumPyStruct):
    __slots__ = ()
    C_TYPE = "struct aiTexel"
    SHAPE = (4,)
    DTYPE = numpy.ubyte
    NUM_ELEMS = 4

    b: int = SimpleAccessor()
    g: int = SimpleAccessor()
    r: int = SimpleAccessor()
    a: int = SimpleAccessor()


C_SRC += """
// See 'color4.h' for details.
struct aiColor4D {
    float r;
    float g;
    float b;
    float a;
};
"""


class Color4D(NumPyStruct):
    """ Red, green, blue and alpha color values"""
    __slots__ = ()
    C_TYPE = "struct aiColor4D"
    SHAPE = (4,)
    DTYPE = numpy.single
    NUM_ELEMS = 4

    r: float = SimpleAccessor()
    g: float = SimpleAccessor()
    b: float = SimpleAccessor()
    a: float = SimpleAccessor()


C_SRC += """
// See 'types.h' for details.
struct aiPlane {
    float a;
    float b;
    float c;
    float d;
};
"""


class Plane(NumPyStruct):
    """ Plane equation"""
    __slots__ = ()
    C_TYPE = "struct aiPlane"
    SHAPE = (4,)
    DTYPE = numpy.single
    NUM_ELEMS = 4

    a: float = SimpleAccessor()
    b: float = SimpleAccessor()
    c: float = SimpleAccessor()
    d: float = SimpleAccessor()


C_SRC += """
// See 'types.h' for details.
struct aiColor3D {
    float r;
    float g;
    float b;
};
"""


class Color3D(NumPyStruct):
    """ Red, green and blue color values"""
    __slots__ = ()
    C_TYPE = "struct aiColor3D"
    SHAPE = (3,)
    DTYPE = numpy.single
    NUM_ELEMS = 3

    r: float = SimpleAccessor()
    g: float = SimpleAccessor()
    b: float = SimpleAccessor()


C_SRC += """
// See 'types.h' for details.
struct aiString {
    unsigned int length;
    char data[1024];
};
"""


class String(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiString"

    length: int = SimpleAccessor()
    """
    Binary length of the string excluding the terminal 0. This is NOT the
     logical length of strings containing UTF-8 multibyte sequences! It's
     the number of bytes from the beginning of the string to its end.
    """

    data: BaseSequence[int] = StaticSequenceAccessor('data', 1024, None)
    """String buffer. Size limit is MAXLEN (1024)"""


C_SRC += """
// See 'MaterialSystem.cpp' for details.
//
// The size of length is truncated to 4 bytes on 64-bit platforms when used as a
// material property (see MaterialSystem.cpp aiMaterial::AddProperty() for details).
struct aiMaterialPropertyString {
    unsigned int length;
    char data[1024];
};
"""


class MaterialPropertyString(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMaterialPropertyString"

    length: int = SimpleAccessor()
    """
    Binary length of the string excluding the terminal 0. This is NOT the
     logical length of strings containing UTF-8 multibyte sequences! It's
     the number of bytes from the beginning of the string to its end.
    """

    data: BaseSequence[int] = StaticSequenceAccessor('data', 1024, None)
    """String buffer. Size limit is MAXLEN"""


C_SRC += """
// See 'types.h' for details.
struct aiMemoryInfo {
    unsigned int textures;
    unsigned int materials;
    unsigned int meshes;
    unsigned int nodes;
    unsigned int animations;
    unsigned int cameras;
    unsigned int lights;
    unsigned int total;
};
"""


class MemoryInfo(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMemoryInfo"

    textures: int = SimpleAccessor()
    """Storage allocated for texture data"""

    materials: int = SimpleAccessor()
    """Storage allocated for material data"""

    meshes: int = SimpleAccessor()
    """Storage allocated for mesh data"""

    nodes: int = SimpleAccessor()
    """Storage allocated for node data"""

    animations: int = SimpleAccessor()
    """Storage allocated for animation data"""

    cameras: int = SimpleAccessor()
    """Storage allocated for camera data"""

    lights: int = SimpleAccessor()
    """Storage allocated for light data"""

    total: int = SimpleAccessor()
    """Total storage allocated for the full import."""


C_SRC += """
// See 'quaternion.h' for details.
struct aiQuaternion {
    float w;
    float x;
    float y;
    float z;
};
"""


class Quaternion(NumPyStruct):
    """ w,x,y,z components of the quaternion"""

    __slots__ = ()
    C_TYPE = "struct aiQuaternion"
    SHAPE = (4,)
    DTYPE = numpy.single
    NUM_ELEMS = 4

    w: float = SimpleAccessor()
    x: float = SimpleAccessor()
    y: float = SimpleAccessor()
    z: float = SimpleAccessor()


C_SRC += """
// See 'mesh.h' for details.
struct aiFace {
    unsigned int mNumIndices;
    unsigned int *mIndices;
};
"""


class Face(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiFace"

    indices: BaseSequence[int] = DynamicSequenceAccessor('mIndices', 'mNumIndices', None)
    """ Pointer to the indices array. Size of the array is given in numIndices."""


C_SRC += """
// See 'mesh.h' for details.
struct aiVertexWeight {
    unsigned int mVertexId;
    float mWeight;
};
"""


class VertexWeight(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiVertexWeight"

    vertex_id: int = SimpleAccessor(name='mVertexId')
    """ Index of the vertex which is influenced by the bone."""

    weight: float = SimpleAccessor(name='mWeight')
    """
     The strength of the influence in the range (0...1).
     The influence from all bones at one vertex amounts to 1.
    """


C_SRC += """
// See 'matrix4x4.h' for details.
struct aiMatrix4x4 {
    float a1;
    float a2;
    float a3;
    float a4;
    float b1;
    float b2;
    float b3;
    float b4;
    float c1;
    float c2;
    float c3;
    float c4;
    float d1;
    float d2;
    float d3;
    float d4;
};
"""


class Matrix4x4(NumPyStruct):
    __slots__ = ()
    C_TYPE = "struct aiMatrix4x4"
    SHAPE = (4, 4)
    DTYPE = numpy.single
    NUM_ELEMS = 16

    a1: float = SimpleAccessor()
    a2: float = SimpleAccessor()
    a3: float = SimpleAccessor()
    a4: float = SimpleAccessor()
    b1: float = SimpleAccessor()
    b2: float = SimpleAccessor()
    b3: float = SimpleAccessor()
    b4: float = SimpleAccessor()
    c1: float = SimpleAccessor()
    c2: float = SimpleAccessor()
    c3: float = SimpleAccessor()
    c4: float = SimpleAccessor()
    d1: float = SimpleAccessor()
    d2: float = SimpleAccessor()
    d3: float = SimpleAccessor()
    d4: float = SimpleAccessor()


C_SRC += """
// See 'vector3.h' for details.
struct aiVector3D {
    float x;
    float y;
    float z;
};
"""


class Vector3D(NumPyStruct):
    __slots__ = ()
    C_TYPE = "struct aiVector3D"
    SHAPE = (3,)
    DTYPE = numpy.single
    NUM_ELEMS = 3

    x: float = SimpleAccessor()
    y: float = SimpleAccessor()
    z: float = SimpleAccessor()


C_SRC += """
// See 'anim.h' for details.
struct aiMeshKey {
    double mTime;
    unsigned int mValue;
};
"""


class MeshKey(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMeshKey"

    time: float = SimpleAccessor(name='mTime')
    """The time of this key"""

    value: int = SimpleAccessor(name='mValue')
    """
    Index into the aiMesh::mAnimMeshes array of the
     mesh corresponding to the
    aiMeshAnim hosting this
     key frame. The referenced anim mesh is evaluated
     according to the rules defined in the docs for
    aiAnimMesh.
    """


C_SRC += """
// See 'metadata.h' for details
struct aiMetadataEntry {
    unsigned int mType;
    void *mData;
};
"""


class MetadataEntry(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMetadataEntry"

    type: int = SimpleAccessor(name='mType')
    """The type field uniquely identifies the underlying type of the data field"""

    data: Any = MetadataEntryDataAccessor()


C_SRC += """
// See 'metadata.h' for details
struct aiMetadata {
    unsigned int mNumProperties;
    struct aiString *mKeys;
    struct aiMetadataEntry *mValues;
};
"""


class Metadata(MetadataMapping):
    __slots__ = ()
    C_TYPE = "struct aiMetadata"

    num_properties: int = SimpleAccessor(name='mNumProperties')
    """Length of the mKeys and mValues arrays, respectively"""

    meta_keys: BaseSequence[str] = DynamicSequenceAccessor('mKeys', 'mNumProperties', StringAdapter)
    """
    Array of keys, may not be NULL. Entries in this array may not be NULL
    as well.
    """

    meta_values: BaseSequence[MetadataEntry] = DynamicSequenceAccessor('mValues', 'mNumProperties', MetadataEntry)
    """
    Array of values, may not be NULL. Entries in this array may be NULL
    if the corresponding property key has no assigned value.
    """


C_SRC += """
// See 'scene.h' for details.
struct aiNode {
    struct aiString mName;
    struct aiMatrix4x4 mTransformation;
    struct aiNode *mParent;
    unsigned int mNumChildren;
    struct aiNode **mChildren;
    unsigned int mNumMeshes;
    unsigned int *mMeshes;
    struct aiMetadata *mMetadata;
};
"""


class Node(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiNode"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    The name of the node.
    The name might be empty (length of zero) but all nodes which
    need to be accessed afterwards by bones or anims are usually named.
    Multiple nodes may have the same name, but nodes which are accessed
    by bones (see
    aiBone and
    aiMesh::mBones) *must* be unique.
    Cameras and lights are assigned to a specific node name - if there
    are multiple nodes with this name, they're assigned to each of them.
    <br>
    There are no limitations regarding the characters contained in
    this text. You should be able to handle stuff like whitespace, tabs,
    linefeeds, quotation marks, ampersands, ... .
    """

    transformation: numpy.ndarray = SimpleAccessor(name='mTransformation', adapter=Matrix4x4)
    """The transformation relative to the node's parent."""

    parent: Optional['Node'] = SimpleAccessor(name='mParent', adapter=LazyStruct(lambda: Node))
    """Parent node. NULL if this node is the root node."""

    children: BaseSequence['Node'] = DynamicSequenceAccessor('mChildren', 'mNumChildren', LazyStruct(lambda: Node))
    """The child nodes of this node. NULL if mNumChildren is 0."""

    meshes: BaseSequence[Mesh] = DynamicSequenceAccessor('mMeshes', 'mNumMeshes', MeshIndexAdapter)
    """The meshes of this node. Each entry is an index into the mesh"""

    metadata: Optional[Metadata] = SimpleAccessor(name='mMetadata', adapter=Metadata)
    """
    Metadata associated with this node or NULL if there is no metadata.
    Whether any metadata is generated depends on the source file format.
    """


C_SRC += """
// See 'light.h' for details.
struct aiLight {
    struct aiString mName;
    unsigned int mType;
    struct aiVector3D mPosition;
    struct aiVector3D mDirection;
    struct aiVector3D mUp;
    float mAttenuationConstant;
    float mAttenuationLinear;
    float mAttenuationQuadratic;
    struct aiColor3D mColorDiffuse;
    struct aiColor3D mColorSpecular;
    struct aiColor3D mColorAmbient;
    float mAngleInnerCone;
    float mAngleOuterCone;
    struct aiVector2D mSize;
};
"""


class Light(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiLight"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    The name of the light source.
     There must be a node in the scenegraph with the same name.
     This node specifies the position of the light in the scene
     hierarchy and can be animated.
    """

    type: int = SimpleAccessor(name='mType')
    """
    The type of the light source.
    aiLightSource_UNDEFINED is not a valid value for this member.
    """

    position: numpy.ndarray = SimpleAccessor(name='mPosition', adapter=Vector3D)
    """
    Position of the light source in space. Relative to the
     transformation of the node corresponding to the light.
     The position is undefined for directional lights.
    """

    direction: numpy.ndarray = SimpleAccessor(name='mDirection', adapter=Vector3D)
    """
    Direction of the light source in space. Relative to the
     transformation of the node corresponding to the light.
     The direction is undefined for point lights. The vector
     may be normalized, but it needn't.
    """

    up: numpy.ndarray = SimpleAccessor(name='mUp', adapter=Vector3D)
    """
    Up direction of the light source in space. Relative to the
     transformation of the node corresponding to the light.

    The direction is undefined for point lights. The vector
     may be normalized, but it needn't.
    """

    attenuation_constant: float = SimpleAccessor(name='mAttenuationConstant')
    """
    Constant light attenuation factor.
     The intensity of the light source at a given distance 'd' from
     the light's position is
     @code
     Atten = 1/( att0 + att1
    d + att2
    d*d)
     @endcode
     This member corresponds to the att0 variable in the equation.
     Naturally undefined for directional lights.
    """

    attenuation_linear: float = SimpleAccessor(name='mAttenuationLinear')
    """
    Linear light attenuation factor.
     The intensity of the light source at a given distance 'd' from
     the light's position is
     @code
     Atten = 1/( att0 + att1
    d + att2
    d*d)
     @endcode
     This member corresponds to the att1 variable in the equation.
     Naturally undefined for directional lights.
    """

    attenuation_quadratic: float = SimpleAccessor(name='mAttenuationQuadratic')
    """
    Quadratic light attenuation factor.
     The intensity of the light source at a given distance 'd' from
     the light's position is
     @code
     Atten = 1/( att0 + att1
    d + att2
    d*d)
     @endcode
     This member corresponds to the att2 variable in the equation.
     Naturally undefined for directional lights.
    """

    color_diffuse: numpy.ndarray = SimpleAccessor(name='mColorDiffuse', adapter=Color3D)
    """
    Diffuse color of the light source
     The diffuse light color is multiplied with the diffuse
     material color to obtain the final color that contributes
     to the diffuse shading term.
    """

    color_specular: numpy.ndarray = SimpleAccessor(name='mColorSpecular', adapter=Color3D)
    """
    Specular color of the light source
     The specular light color is multiplied with the specular
     material color to obtain the final color that contributes
     to the specular shading term.
    """

    color_ambient: numpy.ndarray = SimpleAccessor(name='mColorAmbient', adapter=Color3D)
    """
    Ambient color of the light source
     The ambient light color is multiplied with the ambient
     material color to obtain the final color that contributes
     to the ambient shading term. Most renderers will ignore
     this value it, is just a remaining of the fixed-function pipeline
     that is still supported by quite many file formats.
    """

    angle_inner_cone: float = SimpleAccessor(name='mAngleInnerCone')
    """
    Inner angle of a spot light's light cone.
     The spot light has maximum influence on objects inside this
     angle. The angle is given in radians. It is 2PI for point
     lights and undefined for directional lights.
    """

    angle_outer_cone: float = SimpleAccessor(name='mAngleOuterCone')
    """
    Outer angle of a spot light's light cone.
     The spot light does not affect objects outside this angle.
     The angle is given in radians. It is 2PI for point lights and
     undefined for directional lights. The outer angle must be
     greater than or equal to the inner angle.
     It is assumed that the application uses a smooth
     interpolation between the inner and the outer cone of the
     spot light.
    """

    size: numpy.ndarray = SimpleAccessor(name='mSize', adapter=Vector2D)
    """Size of area light source."""


C_SRC += """
// See 'texture.h' for details.
struct aiTexture {
    unsigned int mWidth;
    unsigned int mHeight;
    char achFormatHint[9];
    struct aiTexel *pcData;
    struct aiString mFilename;
};
"""


class Texture(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiTexture"

    width: int = SimpleAccessor(name='mWidth')
    """
    Width of the texture, in pixels
    If mHeight is zero the texture is compressed in a format
    like JPEG. In this case mWidth specifies the size of the
    memory area pcData is pointing to, in bytes.
    """

    height: int = SimpleAccessor(name='mHeight')
    """
    Height of the texture, in pixels
    If this value is zero, pcData points to an compressed texture
    in any format (e.g. JPEG).
    """

    ach_format_hint: str = SimpleAccessor(name='achFormatHint', adapter=CStrAdapter(9))
    """
    A hint from the loader to make it easier for applications
    to determine the type of embedded textures.

    If mHeight != 0 this member is show how data is packed. Hint will consist of
    two parts: channel order and channel bitness (count of the bits for every
    color channel). For simple parsing by the viewer it's better to not omit
    absent color channel and just use 0 for bitness. For example:
    1. Image contain RGBA and 8 bit per channel, achFormatHint == "rgba8888";
    2. Image contain ARGB and 8 bit per channel, achFormatHint == "argb8888";
    3. Image contain RGB and 5 bit for R and B channels and 6 bit for G channel,
       achFormatHint == "rgba5650";
    4. One color image with B channel and 1 bit for it, achFormatHint == "rgba0010";
    If mHeight == 0 then achFormatHint is set set to '\\0\\0\\0\\0' if the loader has no additional
    information about the texture file format used OR the
    file extension of the format without a trailing dot. If there
    are multiple file extensions for a format, the shortest
    extension is chosen (JPEG maps to 'jpg', not to 'jpeg').
    E.g. 'dds\\0', 'pcx\\0', 'jpg\\0'.  All characters are lower-case.
    The fourth character will always be '\\0'.
    """

    data: Union[bytearray, numpy.ndarray] = TextureDataAccessor()
    """
    Data of the texture.
    Points to an array of mWidth
    mHeight aiTexel's.
    The format of the texture data is always ARGB8888 to
    make the implementation for user of the library as easy
    as possible. If mHeight = 0 this is a pointer to a memory
    buffer of size mWidth containing the compressed texture
    data. Good luck, have fun!
    """

    filename: str = SimpleAccessor(name='mFilename', adapter=StringAdapter)
    """
    Texture original filename
    Used to get the texture reference
    """


C_SRC += """
// See 'types.h' for details.
struct aiRay {
    struct aiVector3D pos;
    struct aiVector3D dir;
};
"""


class Ray(SerializableStruct):
    """ Position and direction of the ray"""
    __slots__ = ()
    C_TYPE = "struct aiRay"

    pos: numpy.ndarray = SimpleAccessor(adapter=Vector3D)
    dir: numpy.ndarray = SimpleAccessor(adapter=Vector3D)


C_SRC += """
// See 'material.h' for details.
struct aiUVTransform {
    struct aiVector2D mTranslation;
    struct aiVector2D mScaling;
    float mRotation;
};
"""


class UVTransform(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiUVTransform"

    translation: numpy.ndarray = SimpleAccessor(name='mTranslation', adapter=Vector2D)
    """
    Translation on the u and v axes.
     The default value is (0|0).
    """

    scaling: numpy.ndarray = SimpleAccessor(name='mScaling', adapter=Vector2D)
    """
    Scaling on the u and v axes.
     The default value is (1|1).
    """

    rotation: float = SimpleAccessor(name='mRotation')
    """
    Rotation - in counter-clockwise direction.
     The rotation angle is specified in radians. The
     rotation center is 0.5f|0.5f. The default value
     0.f.
    """


C_SRC += """
// See 'material.h' for details.
struct aiMaterialProperty {
    struct aiString mKey;
    unsigned int mSemantic;
    unsigned int mIndex;
    unsigned int mDataLength;
    unsigned int mType;
    char *mData;
};
"""


class MaterialProperty(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMaterialProperty"

    key: str = SimpleAccessor(name='mKey', adapter=StringAdapter)
    """
    Specifies the name of the property (key)
     Keys are generally case insensitive.
    """

    semantic: int = SimpleAccessor(name='mSemantic')
    """
    Textures: Specifies their exact usage semantic.
    For non-texture properties, this member is always 0
    (or, better-said,
    aiTextureType_NONE).
    """

    texture: Optional[Texture] = SimpleAccessor(name='mIndex', adapter=TextureIndexAdapter)
    """
    Textures: Specifies the index of the texture.
     For non-texture properties, this member is always 0.
    """

    data_length: int = SimpleAccessor(name='mDataLength')
    """
    Size of the buffer mData is pointing to, in bytes.
     This value may not be 0.
    """

    type: int = SimpleAccessor(name='mType')
    """
    Type information for the property.
    Defines the data layout inside the data buffer. This is used
    by the library internally to perform debug checks and to
    utilize proper type conversions.
    (It's probably a hacky solution, but it works.)
    """

    data: Any = MaterialPropertyDataAccessor()
    """
    Binary buffer to hold the property's value.
    The size of the buffer is always mDataLength.
    """


C_SRC += """
// See 'material.h' for details.
struct aiMaterial {
    struct aiMaterialProperty **mProperties;
    unsigned int mNumProperties;
    unsigned int mNumAllocated;
};
"""


class Material(MaterialMapping):
    __slots__ = ()
    C_TYPE = "struct aiMaterial"

    properties: BaseSequence[MaterialProperty] = DynamicSequenceAccessor('mProperties', 'mNumProperties', MaterialProperty)
    """List of all material properties loaded."""

    num_allocated: int = SimpleAccessor(name='mNumAllocated')
    """Storage allocated"""


C_SRC += """
// See 'mesh.h' for details.
struct aiBone {
    struct aiString mName;
    unsigned int mNumWeights;
    struct aiVertexWeight *mWeights;
    struct aiMatrix4x4 mOffsetMatrix;
};
"""


class Bone(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiBone"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """ The name of the bone."""

    weights: BaseSequence[VertexWeight] = DynamicSequenceAccessor('mWeights', 'mNumWeights', VertexWeight)
    """ The vertices affected by this bone"""

    offset_matrix: numpy.ndarray = SimpleAccessor(name='mOffsetMatrix', adapter=Matrix4x4)
    """ Matrix that transforms from mesh space to bone space in bind pose"""


C_SRC += """
// See 'mesh.h' for details.
struct aiAnimMesh {
    struct aiString mName;
    struct aiVector3D *mVertices;
    struct aiVector3D *mNormals;
    struct aiVector3D *mTangents;
    struct aiVector3D *mBitangents;
    struct aiColor4D *mColors[8];
    struct aiVector3D *mTextureCoords[8];
    unsigned int mNumVertices;
    float mWeight;
};
"""


class AnimMesh(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiAnimMesh"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """ Anim Mesh name"""

    vertices: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mVertices', 'mNumVertices', Vector3D)
    """
    Replacement for aiMesh::mVertices. If this array is non-NULL,
    it *must* contain mNumVertices entries. The corresponding
    array in the host mesh must be non-NULL as well - animation
    meshes may neither add or nor remove vertex components (if
    a replacement array is NULL and the corresponding source
    array is not, the source data is taken instead)
    """

    normals: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mNormals', 'mNumVertices', Vector3D)
    """Replacement for aiMesh::mNormals."""

    tangents: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mTangents', 'mNumVertices', Vector3D)
    """Replacement for aiMesh::mTangents."""

    bitangents: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mBitangents', 'mNumVertices', Vector3D)
    """Replacement for aiMesh::mBitangents."""

    colors: Sequence[Optional[BaseSequence[numpy.ndarray]]] = VertexPropSequenceAccessor('mColors', 8, Color4D)
    """Replacement for aiMesh::mColors"""

    texture_coords: Sequence[Optional[BaseSequence[numpy.ndarray]]] = VertexPropSequenceAccessor('mTextureCoords', 8, Vector3D)
    """Replacement for aiMesh::mTextureCoords"""

    weight: float = SimpleAccessor(name='mWeight')
    """Weight of the AnimMesh."""


C_SRC += """
// See 'mesh.h' for details.
struct aiMesh {
    unsigned int mPrimitiveTypes;
    unsigned int mNumVertices;
    unsigned int mNumFaces;
    struct aiVector3D *mVertices;
    struct aiVector3D *mNormals;
    struct aiVector3D *mTangents;
    struct aiVector3D *mBitangents;
    struct aiColor4D *mColors[8];
    struct aiVector3D *mTextureCoords[8];
    unsigned int mNumUVComponents[8];
    struct aiFace *mFaces;
    unsigned int mNumBones;
    struct aiBone **mBones;
    unsigned int mMaterialIndex;
    struct aiString mName;
    unsigned int mNumAnimMeshes;
    struct aiAnimMesh **mAnimMeshes;
    unsigned int mMethod;
};
"""


class Mesh(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMesh"

    primitive_types: int = SimpleAccessor(name='mPrimitiveTypes')
    """
    Flags field with values from aiPrimitiveType enum.
    This specifies which types of primitives are present in the mesh.
    The "SortByPrimitiveType"-Step can be used to make sure the
    output meshes consist of one primitive type each.
    """

    vertices: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mVertices', 'mNumVertices', Vector3D)
    """
    Vertex positions.
    This array is always present in a mesh. The array is
    mNumVertices in size.
    """

    normals: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mNormals', 'mNumVertices', Vector3D)
    """
    Vertex normals.
    The array contains normalized vectors, NULL if not present.
    The array is mNumVertices in size. Normals are undefined for
    point and line primitives. A mesh consisting of points and
    lines only may not have normal vectors. Meshes with mixed
    primitive types (i.e. lines and triangles) may have normals,
    but the normals for vertices that are only referenced by
    point or line primitives are undefined and set to QNaN (WARN:
    qNaN compares to inequal to *everything*, even to qNaN itself.
    Using code like this to check whether a field is qnan is:
    @code
    define IS_QNAN(f) (f != f)
    @endcode
    still dangerous because even 1.f == 1.f could evaluate to false! (
    remember the subtleties of IEEE754 artithmetics). Use stuff like
    @c fpclassify instead.
    @note Normal vectors computed by Assimp are always unit-length.
    However, this needn't apply for normals that have been taken
      directly from the model file.
    """

    tangents: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mTangents', 'mNumVertices', Vector3D)
    """
    Vertex tangents.
    The tangent of a vertex points in the direction of the positive
    X texture axis. The array contains normalized vectors, NULL if
    not present. The array is mNumVertices in size. A mesh consisting
    of points and lines only may not have normal vectors. Meshes with
    mixed primitive types (i.e. lines and triangles) may have
    normals, but the normals for vertices that are only referenced by
    point or line primitives are undefined and set to qNaN.  See
    the
    mNormals member for a detailed discussion of qNaNs.
    @note If the mesh contains tangents, it automatically also
    contains bitangents (the bitangent is just the cross product of
    tangent and normal vectors).
    """

    bitangents: BaseSequence[numpy.ndarray] = DynamicSequenceAccessor('mBitangents', 'mNumVertices', Vector3D)
    """
    Vertex bitangents.
    The bitangent of a vertex points in the direction of the positive
    Y texture axis. The array contains normalized vectors, NULL if not
    present. The array is mNumVertices in size.
    @note If the mesh contains tangents, it automatically also contains
    bitangents.
    """

    colors: Sequence[Optional[BaseSequence[numpy.ndarray]]] = VertexPropSequenceAccessor('mColors', 8, Color4D)
    """
    Vertex color sets.
    A mesh may contain 0 to
    AI_MAX_NUMBER_OF_COLOR_SETS vertex
    colors per vertex. NULL if not present. Each array is
    mNumVertices in size if present.
    """

    texture_coords: Sequence[Optional[BaseSequence[numpy.ndarray]]] = VertexPropSequenceAccessor('mTextureCoords', 8, Vector3D)
    """
    Vertex texture coords, also known as UV channels.
    A mesh may contain 0 to AI_MAX_NUMBER_OF_TEXTURECOORDS per
    vertex. NULL if not present. The array is mNumVertices in size.
    """

    num_uv_components: BaseSequence[int] = StaticSequenceAccessor('mNumUVComponents', 8, None)
    """
    Specifies the number of components for a given UV channel.
    Up to three channels are supported (UVW, for accessing volume
    or cube maps). If the value is 2 for a given channel n, the
    component p.z of mTextureCoords[n][p] is set to 0.0f.
    If the value is 1 for a given channel, p.y is set to 0.0f, too.
    @note 4D coords are not supported
    """

    faces: BaseSequence[BaseSequence[int]] = DynamicSequenceAccessor('mFaces', 'mNumFaces', ProxyAdapter(Face, 'indices'))
    """
    The faces the mesh is constructed from.
    Each face refers to a number of vertices by their indices.
    This array is always present in a mesh, its size is given
    in mNumFaces. If the
    AI_SCENE_FLAGS_NON_VERBOSE_FORMAT
    is NOT set each face references an unique set of vertices.
    """

    bones: BaseSequence[Bone] = DynamicSequenceAccessor('mBones', 'mNumBones', Bone)
    """
    The bones of this mesh.
    A bone consists of a name by which it can be found in the
    frame hierarchy and a set of vertex weights.
    """

    material: Material = SimpleAccessor(name='mMaterialIndex', adapter=MaterialIndexAdapter)
    """
    The material used by this mesh.
    A mesh does use only a single material. If an imported model uses
    multiple materials, the import splits up the mesh. Use this value
    as index into the scene's material list.
    """

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    Name of the mesh. Meshes can be named, but this is not a
     requirement and leaving this field empty is totally fine.
     There are mainly three uses for mesh names:
      - some formats name nodes and meshes independently.
      - importers tend to split meshes up to meet the
         one-material-per-mesh requirement. Assigning
         the same (dummy) name to each of the result meshes
         aids the caller at recovering the original mesh
         partitioning.
      - Vertex animations refer to meshes by their names.
    """

    anim_meshes: BaseSequence[AnimMesh] = DynamicSequenceAccessor('mAnimMeshes', 'mNumAnimMeshes', AnimMesh)
    """
    Attachment meshes for this mesh, for vertex-based animation.
    Attachment meshes carry replacement data for some of the
    mesh'es vertex components (usually positions, normals).
    Note! Currently only works with Collada loader.
    """

    method: int = SimpleAccessor(name='mMethod')
    """Method of morphing when animeshes are specified."""


C_SRC += """
// See 'camera.h' for details.
struct aiCamera {
    struct aiString mName;
    struct aiVector3D mPosition;
    struct aiVector3D mUp;
    struct aiVector3D mLookAt;
    float mHorizontalFOV;
    float mClipPlaneNear;
    float mClipPlaneFar;
    float mAspect;
};
"""


class Camera(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiCamera"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    The name of the camera.
     There must be a node in the scenegraph with the same name.
     This node specifies the position of the camera in the scene
     hierarchy and can be animated.
    """

    position: numpy.ndarray = SimpleAccessor(name='mPosition', adapter=Vector3D)
    """
    Position of the camera relative to the coordinate space
     defined by the corresponding node.
     The default value is 0|0|0.
    """

    up: numpy.ndarray = SimpleAccessor(name='mUp', adapter=Vector3D)
    """
    'Up' - vector of the camera coordinate system relative to
     the coordinate space defined by the corresponding node.
     The 'right' vector of the camera coordinate system is
     the cross product of  the up and lookAt vectors.
     The default value is 0|1|0. The vector
     may be normalized, but it needn't.
    """

    look_at: numpy.ndarray = SimpleAccessor(name='mLookAt', adapter=Vector3D)
    """
    'LookAt' - vector of the camera coordinate system relative to
     the coordinate space defined by the corresponding node.
     This is the viewing direction of the user.
     The default value is 0|0|1. The vector
     may be normalized, but it needn't.
    """

    horizontal_fov: float = SimpleAccessor(name='mHorizontalFOV')
    """
    Half horizontal field of view angle, in radians.
     The field of view angle is the angle between the center
     line of the screen and the left or right border.
     The default value is 1/4PI.
    """

    clip_plane_near: float = SimpleAccessor(name='mClipPlaneNear')
    """
    Distance of the near clipping plane from the camera.
    The value may not be 0.f (for arithmetic reasons to prevent
    a division through zero). The default value is 0.1f.
    """

    clip_plane_far: float = SimpleAccessor(name='mClipPlaneFar')
    """
    Distance of the far clipping plane from the camera.
    The far clipping plane must, of course, be further away than the
    near clipping plane. The default value is 1000.f. The ratio
    between the near and the far plane should not be too
    large (between 1000-10000 should be ok) to avoid floating-point
    inaccuracies which could lead to z-fighting.
    """

    aspect: float = SimpleAccessor(name='mAspect')
    """
    Screen aspect ratio.
    This is the ration between the width and the height of the
    screen. Typical values are 4/3, 1/2 or 1/1. This value is
    0 if the aspect ratio is not defined in the source file.
    0 is also the default value.
    """


C_SRC += """
// See 'anim.h' for details.
struct aiVectorKey {
    double mTime;
    struct aiVector3D mValue;
};
"""


class VectorKey(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiVectorKey"

    time: float = SimpleAccessor(name='mTime')
    """The time of this key"""

    value: numpy.ndarray = SimpleAccessor(name='mValue', adapter=Vector3D)
    """The value of this key"""


C_SRC += """
// See 'anim.h' for details.
struct aiQuatKey {
    double mTime;
    struct aiQuaternion mValue;
};
"""


class QuatKey(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiQuatKey"

    time: float = SimpleAccessor(name='mTime')
    """The time of this key"""

    value: numpy.ndarray = SimpleAccessor(name='mValue', adapter=Quaternion)
    """The value of this key"""


C_SRC += """
// See 'anim.h' for details.
struct aiMeshMorphKey {
    double mTime;
    unsigned int *mValues;
    double *mWeights;
    unsigned int mNumValuesAndWeights;
};
"""


class MeshMorphKey(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMeshMorphKey"

    time: float = SimpleAccessor(name='mTime')
    """The time of this key"""

    values: BaseSequence[int] = DynamicSequenceAccessor('mValues', 'mNumValuesAndWeights', int)
    weights: BaseSequence[float] = DynamicSequenceAccessor('mWeights', 'mNumValuesAndWeights', float)

    num_values_and_weights: int = SimpleAccessor(name='mNumValuesAndWeights')
    """The number of values and weights"""


C_SRC += """
// See 'anim.h' for details.
struct aiNodeAnim {
    struct aiString mNodeName;
    unsigned int mNumPositionKeys;
    struct aiVectorKey *mPositionKeys;
    unsigned int mNumRotationKeys;
    struct aiQuatKey *mRotationKeys;
    unsigned int mNumScalingKeys;
    struct aiVectorKey *mScalingKeys;
    unsigned int mPreState;
    unsigned int mPostState;
};
"""


class NodeAnim(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiNodeAnim"

    node_name: str = SimpleAccessor(name='mNodeName', adapter=StringAdapter)
    """
    The name of the node affected by this animation. The node
     must exist and it must be unique.
    """

    position_keys: BaseSequence[VectorKey] = DynamicSequenceAccessor('mPositionKeys', 'mNumPositionKeys', VectorKey)
    """
    The position keys of this animation channel. Positions are
    specified as 3D vector. The array is mNumPositionKeys in size.
    If there are position keys, there will also be at least one
    scaling and one rotation key.
    """

    rotation_keys: BaseSequence[QuatKey] = DynamicSequenceAccessor('mRotationKeys', 'mNumRotationKeys', QuatKey)
    """
    The rotation keys of this animation channel. Rotations are
     given as quaternions,  which are 4D vectors. The array is
     mNumRotationKeys in size.
    If there are rotation keys, there will also be at least one
    scaling and one position key.
    """

    scaling_keys: BaseSequence[VectorKey] = DynamicSequenceAccessor('mScalingKeys', 'mNumScalingKeys', VectorKey)
    """
    The scaling keys of this animation channel. Scalings are
     specified as 3D vector. The array is mNumScalingKeys in size.
    If there are scaling keys, there will also be at least one
    position and one rotation key.
    """

    pre_state: int = SimpleAccessor(name='mPreState')
    """
    Defines how the animation behaves before the first
     key is encountered.
     The default value is aiAnimBehaviour_DEFAULT (the original
     transformation matrix of the affected node is used).
    """

    post_state: int = SimpleAccessor(name='mPostState')
    """
    Defines how the animation behaves after the last
     key was processed.
     The default value is aiAnimBehaviour_DEFAULT (the original
     transformation matrix of the affected node is taken).
    """


C_SRC += """
// See 'anim.h' for details.
struct aiMeshAnim {
    struct aiString mName;
    unsigned int mNumKeys;
    struct aiMeshKey *mKeys;
};
"""


class MeshAnim(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMeshAnim"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    Name of the mesh to be animated. An empty string is not allowed,
     animated meshes need to be named (not necessarily uniquely,
     the name can basically serve as wild-card to select a group
     of meshes with similar animation setup)
    """

    keys: BaseSequence[MeshKey] = DynamicSequenceAccessor('mKeys', 'mNumKeys', MeshKey)
    """Key frames of the animation. May not be NULL."""


C_SRC += """
// See 'anim.h' for details.
struct aiMeshMorphAnim {
    struct aiString mName;
    unsigned int mNumKeys;
    struct aiMeshMorphKey *mKeys;
};
"""


class MeshMorphAnim(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiMeshMorphAnim"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    Name of the mesh to be animated. An empty string is not allowed,
    animated meshes need to be named (not necessarily uniquely,
    the name can basically serve as wildcard to select a group
    of meshes with similar animation setup)
    """

    keys: BaseSequence[MeshMorphKey] = DynamicSequenceAccessor('mKeys', 'mNumKeys', MeshMorphKey)
    """Key frames of the animation. May not be NULL."""


C_SRC += """
// See 'anim.h' for details.
struct aiAnimation {
    struct aiString mName;
    double mDuration;
    double mTicksPerSecond;
    unsigned int mNumChannels;
    struct aiNodeAnim **mChannels;
    unsigned int mNumMeshChannels;
    struct aiMeshAnim **mMeshChannels;
    unsigned int mNumMorphMeshChannels;
    struct aiMeshMorphAnim **mMorphMeshChannels;
};
"""


class Animation(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiAnimation"

    name: str = SimpleAccessor(name='mName', adapter=StringAdapter)
    """
    The name of the animation. If the modeling package this data was
     exported from does support only a single animation channel, this
     name is usually empty (length is zero).
    """

    duration: float = SimpleAccessor(name='mDuration')
    """Duration of the animation in ticks."""

    ticks_per_second: float = SimpleAccessor(name='mTicksPerSecond')
    """Ticks per second. 0 if not specified in the imported file"""

    channels: BaseSequence[NodeAnim] = DynamicSequenceAccessor('mChannels', 'mNumChannels', NodeAnim)
    """
    The node animation channels. Each channel affects a single node.
     The array is mNumChannels in size.
    """

    mesh_channels: BaseSequence[MeshAnim] = DynamicSequenceAccessor('mMeshChannels', 'mNumMeshChannels', MeshAnim)
    """
    The mesh animation channels. Each channel affects a single mesh.
     The array is mNumMeshChannels in size.
    """

    morph_mesh_channels: BaseSequence[MeshMorphAnim] = DynamicSequenceAccessor('mMorphMeshChannels', 'mNumMorphMeshChannels', MeshMorphAnim)
    """
    The morph mesh animation channels. Each channel affects a single mesh.
    The array is mNumMorphMeshChannels in size.
    """


C_SRC += """
// See 'cexport.h' for details.
//
// Note that the '_fields_' definition is outside the class to allow the 'next' field to be recursive
struct aiExportDataBlob {
    unsigned long size;
    void *data;
    struct aiString name;
    struct aiExportDataBlob *next;
};
"""


class ExportDataBlob(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiExportDataBlob"

    size: int = SimpleAccessor()
    """Size of the data in bytes"""

    data: Union[bytearray] = BoundedBufferAccessor('data', 'size')
    """The data."""

    name: str = SimpleAccessor(adapter=StringAdapter)
    """
    Name of the blob. An empty string always
    indicates the first (and primary) blob,
    which contains the actual file data.
    Any other blobs are auxiliary files produced
    by exporters (i.e. material files). Existence
    of such files depends on the file format. Most
    formats don't split assets across multiple files.

    If used, blob names usually contain the file
    extension that should be used when writing
    the data to disc.
    """

    next: Optional['ExportDataBlob'] = SimpleAccessor(adapter=LazyStruct(lambda: ExportDataBlob))
    """Pointer to the next blob in the chain or NULL if there is none."""


C_SRC += """
// See 'aiScene.h' for details.
struct aiScene {
    unsigned int mFlags;
    struct aiNode *mRootNode;
    unsigned int mNumMeshes;
    struct aiMesh **mMeshes;
    unsigned int mNumMaterials;
    struct aiMaterial **mMaterials;
    unsigned int mNumAnimations;
    struct aiAnimation **mAnimations;
    unsigned int mNumTextures;
    struct aiTexture **mTextures;
    unsigned int mNumLights;
    struct aiLight **mLights;
    unsigned int mNumCameras;
    struct aiCamera **mCameras;
    struct aiMetadata *mMetadata;
    char *mPrivate;
};
"""


class Scene(SerializableStruct):
    __slots__ = ()
    C_TYPE = "struct aiScene"

    flags: int = SimpleAccessor(name='mFlags')
    """
    Any combination of the AI_SCENE_FLAGS_XXX flags. By default
    this value is 0, no flags are set. Most applications will
    want to reject all scenes with the AI_SCENE_FLAGS_INCOMPLETE
    bit set.
    """

    root_node: Optional[Node] = SimpleAccessor(name='mRootNode', adapter=Node)
    """
    The root node of the hierarchy.
    There will always be at least the root node if the import
    was successful (and no special flags have been set).
    Presence of further nodes depends on the format and content
    of the imported file.
    """

    meshes: BaseSequence[Mesh] = DynamicSequenceAccessor('mMeshes', 'mNumMeshes', Mesh)
    """
    The array of meshes.
    Use the indices given in the aiNode structure to access
    this array. The array is mNumMeshes in size. If the
    AI_SCENE_FLAGS_INCOMPLETE flag is not set there will always
    be at least ONE material.
    """

    materials: BaseSequence[Material] = DynamicSequenceAccessor('mMaterials', 'mNumMaterials', Material)
    """
    The array of materials.
    Use the index given in each aiMesh structure to access this
    array. The array is mNumMaterials in size. If the
    AI_SCENE_FLAGS_INCOMPLETE flag is not set there will always
    be at least ONE material.
    """

    animations: BaseSequence[Animation] = DynamicSequenceAccessor('mAnimations', 'mNumAnimations', Animation)
    """
    The array of animations.
    All animations imported from the given file are listed here.
    The array is mNumAnimations in size.
    """

    textures: BaseSequence[Texture] = DynamicSequenceAccessor('mTextures', 'mNumTextures', Texture)
    """
    The array of embedded textures.
    Not many file formats embed their textures into the file.
    An example is Quake's MDL format (which is also used by
    some GameStudio versions)
    """

    lights: BaseSequence[Light] = DynamicSequenceAccessor('mLights', 'mNumLights', Light)
    """
    The array of light sources.
    All light sources imported from the given file are
    listed here. The array is mNumLights in size.
    """

    cameras: BaseSequence[Camera] = DynamicSequenceAccessor('mCameras', 'mNumCameras', Camera)
    """
    The array of cameras.
    All cameras imported from the given file are listed here.
    The array is mNumCameras in size. The first camera in the
    array (if existing) is the default camera view into
    the scene.
    """

    metadata: Optional[Metadata] = SimpleAccessor(name='mMetadata', adapter=Metadata)
    """
    This data contains global metadata which belongs to the scene like
    unit-conversions, versions, vendors or other model-specific data. This
    can be used to store format-specific metadata as well.
    """

    private: Optional[Any] = SimpleAccessor(name='mPrivate')
    """Internal data, do not touch"""


ffi.cdef(FUNCTION_DECLS + C_SRC)
