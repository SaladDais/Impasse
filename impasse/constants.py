import enum
from typing import NamedTuple

AI_MAX_NUMBER_OF_TEXTURECOORDS = 0x8
AI_MAX_NUMBER_OF_COLOR_SETS = 0x8

AI_MAX_FACE_INDICES = 0x7fff
AI_MAX_BONE_WEIGHTS = 0x7fffffff
AI_MAX_VERTICES = 0x7fffffff
AI_MAX_FACES = 0x7fffffff


class SceneFlags(enum.IntFlag):
    INCOMPLETE = 0x1
    VALIDATED = 0x2
    VALIDATION_WARNING = 0x4
    NON_VERBOSE_FORMAT = 0x8
    TERRAIN = 0x10
    ALLOW_SHARED = 0x20


class MetadataType(enum.IntEnum):
    BOOL = 0
    INT32 = 1
    UINT64 = 2
    FLOAT = 3
    DOUBLE = 4
    AISTRING = 5
    AIVECTOR3D = 6


class MaterialPropertyType(enum.IntEnum):
    FLOAT = 1
    DOUBLE = 2
    AISTRING = 3
    INT = 4
    BINARY = 5


class TextureSemantic(enum.IntEnum):
    # Dummy value.
    #
    #  No texture, but the value to be used as 'texture semantic'
    #  (#aiMaterialProperty::mSemantic) for all material properties
    # # not* related to textures.
    #
    NONE = 0x0

    # The texture is combined with the result of the diffuse
    #  lighting equation.
    #
    DIFFUSE = 0x1

    # The texture is combined with the result of the specular
    #  lighting equation.
    #
    SPECULAR = 0x2

    # The texture is combined with the result of the ambient
    #  lighting equation.
    #
    AMBIENT = 0x3

    # The texture is added to the result of the lighting
    #  calculation. It isn't influenced by incoming light.
    #
    EMISSIVE = 0x4

    # The texture is a height map.
    #
    #  By convention, higher gray-scale values stand for
    #  higher elevations from the base height.
    #
    HEIGHT = 0x5

    # The texture is a (tangent space) normal-map.
    #
    #  Again, there are several conventions for tangent-space
    #  normal maps. Assimp does (intentionally) not
    #  distinguish here.
    #
    NORMALS = 0x6

    # The texture defines the glossiness of the material.
    #
    #  The glossiness is in fact the exponent of the specular
    #  (phong) lighting equation. Usually there is a conversion
    #  function defined to map the linear color values in the
    #  texture to a suitable exponent. Have fun.
    #
    SHININESS = 0x7

    # The texture defines per-pixel opacity.
    #
    #  Usually 'white' means opaque and 'black' means
    #  'transparency'. Or quite the opposite. Have fun.
    #
    OPACITY = 0x8

    # Displacement texture
    #
    #  The exact purpose and format is application-dependent.
    #  Higher color values stand for higher vertex displacements.
    #
    DISPLACEMENT = 0x9

    # Lightmap texture (aka Ambient Occlusion)
    #
    #  Both 'Lightmaps' and dedicated 'ambient occlusion maps' are
    #  covered by this material property. The texture contains a
    #  scaling value for the final color value of a pixel. Its
    #  intensity is not affected by incoming light.
    #
    LIGHTMAP = 0xA

    # Reflection texture
    #
    # Contains the color of a perfect mirror reflection.
    # Rarely used, almost never for real-time applications.
    #
    REFLECTION = 0xB

    # Unknown texture
    #
    #  A texture reference that does not match any of the definitions
    #  above is considered to be 'unknown'. It is still imported
    #  but is excluded from any further postprocessing.
    #
    UNKNOWN = 0xC


class ProcessingStep(enum.IntFlag):
    # <hr>Calculates the tangents and bitangents for the imported meshes.
    #
    # Does nothing if a mesh does not have normals. You might want this post
    # processing step to be executed if you plan to use tangent space calculations
    # such as normal mapping  applied to the meshes. There's a config setting,
    # <tt>#AI_CONFIG_PP_CT_MAX_SMOOTHING_ANGLE<tt>, which allows you to specify
    # a maximum smoothing angle for the algorithm. However, usually you'll
    # want to leave it at the default value.
    #
    CalcTangentSpace = 0x1

    # <hr>Identifies and joins identical vertex data sets within all
    #  imported meshes.
    #
    # After this step is run, each mesh contains unique vertices,
    # so a vertex may be used by multiple faces. You usually want
    # to use this post processing step. If your application deals with
    # indexed geometry, this step is compulsory or you'll just waste rendering
    # time. <b>If this flag is not specified<b>, no vertices are referenced by
    # more than one face and <b>no index buffer is required<b> for rendering.
    #
    JoinIdenticalVertices = 0x2

    # <hr>Converts all the imported data to a left-handed coordinate space.
    #
    # By default the data is returned in a right-handed coordinate space (which
    # OpenGL prefers). In this space, +X points to the right,
    # +Z points towards the viewer, and +Y points upwards. In the DirectX
    # coordinate space +X points to the right, +Y points upwards, and +Z points
    # away from the viewer.
    #
    # You'll probably want to consider this flag if you use Direct3D for
    # rendering. The #ConvertToLeftHanded flag supersedes this
    # setting and bundles all conversions typically required for D3D-based
    # applications.
    #
    MakeLeftHanded = 0x4

    # <hr>Triangulates all faces of all meshes.
    #
    # By default the imported mesh data might contain faces with more than 3
    # indices. For rendering you'll usually want all faces to be triangles.
    # This post processing step splits up faces with more than 3 indices into
    # triangles. Line and point primitives are #not# modified! If you want
    # 'triangles only' with no other kinds of primitives, try the following
    # solution:
    # <ul>
    # <li>Specify both #Triangulate and #SortByPType <li>
    # <li>Ignore all point and line meshes when you process assimp's output<li>
    # <ul>
    #
    Triangulate = 0x8

    # <hr>Removes some parts of the data structure (animations, materials,
    #  light sources, cameras, textures, vertex components).
    #
    # The  components to be removed are specified in a separate
    # configuration option, <tt>#AI_CONFIG_PP_RVC_FLAGS<tt>. This is quite useful
    # if you don't need all parts of the output structure. Vertex colors
    # are rarely used today for example... Calling this step to remove unneeded
    # data from the pipeline as early as possible results in increased
    # performance and a more optimized output data structure.
    # This step is also useful if you want to force Assimp to recompute
    # normals or tangents. The corresponding steps don't recompute them if
    # they're already there (loaded from the source asset). By using this
    # step you can make sure they are NOT there.
    #
    # This flag is a poor one, mainly because its purpose is usually
    # misunderstood. Consider the following case: a 3D model has been exported
    # from a CAD app, and it has per-face vertex colors. Vertex positions can't be
    # shared, thus the #JoinIdenticalVertices step fails to
    # optimize the data because of these nasty little vertex colors.
    # Most apps don't even process them, so it's all for nothing. By using
    # this step, unneeded components are excluded as early as possible
    # thus opening more room for internal optimizations.
    #
    RemoveComponent = 0x10

    # <hr>Generates normals for all faces of all meshes.
    #
    # This is ignored if normals are already there at the time this flag
    # is evaluated. Model importers try to load them from the source file, so
    # they're usually already there. Face normals are shared between all points
    # of a single face, so a single point can have multiple normals, which
    # forces the library to duplicate vertices in some cases.
    # #JoinIdenticalVertices is #senseless# then.
    #
    # This flag may not be specified together with #GenSmoothNormals.
    #
    GenNormals = 0x20

    # <hr>Generates smooth normals for all vertices in the mesh.
    #
    # This is ignored if normals are already there at the time this flag
    # is evaluated. Model importers try to load them from the source file, so
    # they're usually already there.
    #
    # This flag may not be specified together with
    # #GenNormals. There's a configuration option,
    # <tt>#AI_CONFIG_PP_GSN_MAX_SMOOTHING_ANGLE<tt> which allows you to specify
    # an angle maximum for the normal smoothing algorithm. Normals exceeding
    # this limit are not smoothed, resulting in a 'hard' seam between two faces.
    # Using a decent angle here (e.g. 80 degrees) results in very good visual
    # appearance.
    #
    GenSmoothNormals = 0x40

    # <hr>Splits large meshes into smaller sub-meshes.
    #
    # This is quite useful for real-time rendering, where the number of triangles
    # which can be maximally processed in a single draw-call is limited
    # by the video driverhardware. The maximum vertex buffer is usually limited
    # too. Both requirements can be met with this step: you may specify both a
    # triangle and vertex limit for a single mesh.
    #
    # The split limits can (and should!) be set through the
    # <tt>#AI_CONFIG_PP_SLM_VERTEX_LIMIT<tt> and <tt>#AI_CONFIG_PP_SLM_TRIANGLE_LIMIT<tt>
    # settings. The default values are <tt>#AI_SLM_DEFAULT_MAX_VERTICES<tt> and
    # <tt>#AI_SLM_DEFAULT_MAX_TRIANGLES<tt>.
    #
    # Note that splitting is generally a time-consuming task, but only if there's
    # something to split. The use of this step is recommended for most users.
    #
    SplitLargeMeshes = 0x80

    # <hr>Removes the node graph and pre-transforms all vertices with
    # the local transformation matrices of their nodes.
    #
    # The output scene still contains nodes, however there is only a
    # root node with children, each one referencing only one mesh,
    # and each mesh referencing one material. For rendering, you can
    # simply render all meshes in order - you don't need to pay
    # attention to local transformations and the node hierarchy.
    # Animations are removed during this step.
    # This step is intended for applications without a scenegraph.
    # The step CAN cause some problems: if e.g. a mesh of the asset
    # contains normals and another, using the same material index, does not,
    # they will be brought together, but the first meshes's part of
    # the normal list is zeroed. However, these artifacts are rare.
    # @note The <tt>#AI_CONFIG_PP_PTV_NORMALIZE<tt> configuration property
    # can be set to normalize the scene's spatial dimension to the -1...1
    # range.
    #
    PreTransformVertices = 0x100

    # <hr>Limits the number of bones simultaneously affecting a single vertex
    #  to a maximum value.
    #
    # If any vertex is affected by more than the maximum number of bones, the least
    # important vertex weights are removed and the remaining vertex weights are
    # renormalized so that the weights still sum up to 1.
    # The default bone weight limit is 4 (defined as <tt>#AI_LMW_MAX_WEIGHTS<tt> in
    # config.h), but you can use the <tt>#AI_CONFIG_PP_LBW_MAX_WEIGHTS<tt> setting to
    # supply your own limit to the post processing step.
    #
    # If you intend to perform the skinning in hardware, this post processing
    # step might be of interest to you.
    #
    LimitBoneWeights = 0x200

    # <hr>Validates the imported scene data structure.
    # This makes sure that all indices are valid, all animations and
    # bones are linked correctly, all material references are correct .. etc.
    #
    # It is recommended that you capture Assimp's log output if you use this flag,
    # so you can easily find out what's wrong if a file fails the
    # validation. The validator is quite strict and will find #all#
    # inconsistencies in the data structure... It is recommended that plugin
    # developers use it to debug their loaders. There are two types of
    # validation failures:
    # <ul>
    # <li>Error: There's something wrong with the imported data. Further
    #   postprocessing is not possible and the data is not usable at all.
    #   The import fails. #Importer::GetErrorString() or #aiGetErrorString()
    #   carry the error message around.<li>
    # <li>Warning: There are some minor issues (e.g. 1000000 animation
    #   keyframes with the same time), but further postprocessing and use
    #   of the data structure is still safe. Warning details are written
    #   to the log file, <tt>#AI_SCENE_FLAGS_VALIDATION_WARNING<tt> is set
    #   in #aiScene::mFlags<li>
    # <ul>
    #
    # This post-processing step is not time-consuming. Its use is not
    # compulsory, but recommended.
    #
    ValidateDataStructure = 0x400

    # <hr>Reorders triangles for better vertex cache locality.
    #
    # The step tries to improve the ACMR (average post-transform vertex cache
    # miss ratio) for all meshes. The implementation runs in O(n) and is
    # roughly based on the 'tipsify' algorithm (see <a href="
    # http:www.cs.princeton.edugfxpubsSander_2007_%3ETRtipsy.pdf">this
    # paper<a>).
    #
    # If you intend to render huge models in hardware, this step might
    # be of interest to you. The <tt>#AI_CONFIG_PP_ICL_PTCACHE_SIZE<tt>config
    # setting can be used to fine-tune the cache optimization.
    #
    ImproveCacheLocality = 0x800

    # <hr>Searches for redundantunreferenced materials and removes them.
    #
    # This is especially useful in combination with the
    # #PretransformVertices and #OptimizeMeshes flags.
    # Both join small meshes with equal characteristics, but they can't do
    # their work if two meshes have different materials. Because several
    # material settings are lost during Assimp's import filters,
    # (and because many exporters don't check for redundant materials), huge
    # models often have materials which are are defined several times with
    # exactly the same settings.
    #
    # Several material settings not contributing to the final appearance of
    # a surface are ignored in all comparisons (e.g. the material name).
    # So, if you're passing additional information through the
    # content pipeline (probably using #magic# material names), don't
    # specify this flag. Alternatively take a look at the
    # <tt>#AI_CONFIG_PP_RRM_EXCLUDE_LIST<tt> setting.
    #
    RemoveRedundantMaterials = 0x1000

    # <hr>This step tries to determine which meshes have normal vectors
    # that are facing inwards and inverts them.
    #
    # The algorithm is simple but effective:
    # the bounding box of all vertices + their normals is compared against
    # the volume of the bounding box of all vertices without their normals.
    # This works well for most objects, problems might occur with planar
    # surfaces. However, the step tries to filter such cases.
    # The step inverts all in-facing normals. Generally it is recommended
    # to enable this step, although the result is not always correct.
    #
    FixInfacingNormals = 0x2000

    # <hr>This step splits meshes with more than one primitive type in
    #  homogeneous sub-meshes.
    #
    #  The step is executed after the triangulation step. After the step
    #  returns, just one bit is set in aiMesh::mPrimitiveTypes. This is
    #  especially useful for real-time rendering where point and line
    #  primitives are often ignored or rendered separately.
    #  You can use the <tt>#AI_CONFIG_PP_SBP_REMOVE<tt> option to specify which
    #  primitive types you need. This can be used to easily exclude
    #  lines and points, which are rarely used, from the import.
    #
    SortByPType = 0x8000

    # <hr>This step searches all meshes for degenerate primitives and
    #  converts them to proper lines or points.
    #
    # A face is 'degenerate' if one or more of its points are identical.
    # To have the degenerate stuff not only detected and collapsed but
    # removed, try one of the following procedures:
    # <br><b>1.<b> (if you support lines and points for rendering but don't
    #    want the degenerates)<br>
    # <ul>
    #   <li>Specify the #FindDegenerates flag.
    #   <li>
    #   <li>Set the <tt>AI_CONFIG_PP_FD_REMOVE<tt> option to 1. This will
    #       cause the step to remove degenerate triangles from the import
    #       as soon as they're detected. They won't pass any further
    #       pipeline steps.
    #   <li>
    # <ul>
    # <br><b>2.<b>(if you don't support lines and points at all)<br>
    # <ul>
    #   <li>Specify the #FindDegenerates flag.
    #   <li>
    #   <li>Specify the #SortByPType flag. This moves line and
    #     point primitives to separate meshes.
    #   <li>
    #   <li>Set the <tt>AI_CONFIG_PP_SBP_REMOVE<tt> option to
    #       @code aiPrimitiveType_POINTS | aiPrimitiveType_LINES
    #       @endcode to cause SortByPType to reject point
    #       and line meshes from the scene.
    #   <li>
    # <ul>
    # @note Degenerate polygons are not necessarily evil and that's why
    # they're not removed by default. There are several file formats which
    # don't support lines or points, and some exporters bypass the
    # format specification and write them as degenerate triangles instead.
    #
    FindDegenerates = 0x10000

    # <hr>This step searches all meshes for invalid data, such as zeroed
    #  normal vectors or invalid UV coords and removesfixes them. This is
    #  intended to get rid of some common exporter errors.
    #
    # This is especially useful for normals. If they are invalid, and
    # the step recognizes this, they will be removed and can later
    # be recomputed, i.e. by the #GenSmoothNormals flag.<br>
    # The step will also remove meshes that are infinitely small and reduce
    # animation tracks consisting of hundreds if redundant keys to a single
    # key. The <tt>AI_CONFIG_PP_FID_ANIM_ACCURACY<tt> config property decides
    # the accuracy of the check for duplicate animation tracks.
    #
    FindInvalidData = 0x20000

    # <hr>This step converts non-UV mappings (such as spherical or
    #  cylindrical mapping) to proper texture coordinate channels.
    #
    # Most applications will support UV mapping only, so you will
    # probably want to specify this step in every case. Note that Assimp is not
    # always able to match the original mapping implementation of the
    # 3D app which produced a model perfectly. It's always better to let the
    # modelling app compute the UV channels - 3ds max, Maya, Blender,
    # LightWave, and Modo do this for example.
    #
    # @note If this step is not requested, you'll need to process the
    # <tt>#AI_MATKEY_MAPPING<tt> material property in order to display all assets
    # properly.
    #
    GenUVCoords = 0x40000

    # <hr>This step applies per-texture UV transformations and bakes
    #  them into stand-alone vtexture coordinate channels.
    #
    # UV transformations are specified per-texture - see the
    # <tt>#AI_MATKEY_UVTRANSFORM<tt> material key for more information.
    # This step processes all textures with
    # transformed input UV coordinates and generates a new (pre-transformed) UV channel
    # which replaces the old channel. Most applications won't support UV
    # transformations, so you will probably want to specify this step.
    #
    # @note UV transformations are usually implemented in real-time apps by
    # transforming texture coordinates at vertex shader stage with a 3x3
    # (homogenous) transformation matrix.
    #
    TransformUVCoords = 0x80000

    # <hr>This step searches for duplicate meshes and replaces them
    #  with references to the first mesh.
    #
    #  This step takes a while, so don't use it if speed is a concern.
    #  Its main purpose is to workaround the fact that many export
    #  file formats don't support instanced meshes, so exporters need to
    #  duplicate meshes. This step removes the duplicates again. Please
    #  note that Assimp does not currently support per-node material
    #  assignment to meshes, which means that identical meshes with
    #  different materials are currently #not# joined, although this is
    #  planned for future versions.
    #
    FindInstances = 0x100000

    # <hr>A postprocessing step to reduce the number of meshes.
    #
    #  This will, in fact, reduce the number of draw calls.
    #
    #  This is a very effective optimization and is recommended to be used
    #  together with #OptimizeGraph, if possible. The flag is fully
    #  compatible with both #SplitLargeMeshes and #SortByPType.
    #
    OptimizeMeshes = 0x200000

    # <hr>A postprocessing step to optimize the scene hierarchy.
    #
    #  Nodes without animations, bones, lights or cameras assigned are
    #  collapsed and joined.
    #
    #  Node names can be lost during this step. If you use special 'tag nodes'
    #  to pass additional information through your content pipeline, use the
    #  <tt>#AI_CONFIG_PP_OG_EXCLUDE_LIST<tt> setting to specify a list of node
    #  names you want to be kept. Nodes matching one of the names in this list won't
    #  be touched or modified.
    #
    #  Use this flag with caution. Most simple files will be collapsed to a
    #  single node, so complex hierarchies are usually completely lost. This is not
    #  useful for editor environments, but probably a very effective
    #  optimization if you just want to get the model data, convert it to your
    #  own format, and render it as fast as possible.
    #
    #  This flag is designed to be used with #OptimizeMeshes for best
    #  results.
    #
    #  @note 'Crappy' scenes with thousands of extremely small meshes packed
    #  in deeply nested nodes exist for almost all file formats.
    #  #OptimizeMeshes in combination with #OptimizeGraph
    #  usually fixes them all and makes them renderable.
    #
    OptimizeGraph = 0x400000

    # <hr>This step flips all UV coordinates along the y-axis and adjusts
    # material settings and bitangents accordingly.
    #
    # <b>Output UV coordinate system:<b>
    # @code
    # 0y|0y ---------- 1x|0y
    # |                 |
    # |                 |
    # |                 |
    # 0x|1y ---------- 1x|1y
    # @endcode
    #
    # You'll probably want to consider this flag if you use Direct3D for
    # rendering. The #ConvertToLeftHanded flag supersedes this
    # setting and bundles all conversions typically required for D3D-based
    # applications.
    #
    FlipUVs = 0x800000

    # <hr>This step adjusts the output face winding order to be CW.
    #
    # The default face winding order is counter clockwise (CCW).
    #
    # <b>Output face order:<b>
    # @code
    #       x2
    #
    #                         x0
    #  x1
    # @endcode
    #
    FlipWindingOrder = 0x1000000

    # <hr>This step splits meshes with many bones into sub-meshes so that each
    # su-bmesh has fewer or as many bones as a given limit.
    #
    SplitByBoneCount = 0x2000000

    # <hr>This step removes bones losslessly or according to some threshold.
    #
    #  In some cases (i.e. formats that require it) exporters are forced to
    #  assign dummy bone weights to otherwise static meshes assigned to
    #  animated meshes. Full, weight-based skinning is expensive while
    #  animating nodes is extremely cheap, so this step is offered to clean up
    #  the data in that regard.
    #
    #  Use <tt>#AI_CONFIG_PP_DB_THRESHOLD<tt> to control this.
    #  Use <tt>#AI_CONFIG_PP_DB_ALL_OR_NONE<tt> if you want bones removed if and
    #  only if all bones within the scene qualify for removal.
    #
    Debone = 0x4000000

    GenEntityMeshes = 0x100000
    OptimizeAnimations = 0x200000
    FixTexturePaths = 0x200000
    EmbedTextures = 0x10000000


class ProcessingPreset:
    def __init__(self):
        raise NotImplementedError()

    # @def ConvertToLeftHanded
    #  @brief Shortcut flag for Direct3D-based applications.
    #
    #  Supersedes the MakeLeftHanded and FlipUVs and
    #  FlipWindingOrder flags.
    #  The output data matches Direct3D's conventions: left-handed geometry, upper-left
    #  origin for UV coordinates and finally clockwise face order, suitable for CCW culling.
    #
    #  @deprecated
    #
    ConvertToLeftHanded = (
        0
        | ProcessingStep.MakeLeftHanded
        | ProcessingStep.FlipUVs
        | ProcessingStep.FlipWindingOrder
    )

    # @def TargetRealtimeUse_Fast
    #  @brief Default postprocess configuration optimizing the data for real-time rendering.
    #
    #  Applications would want to use this preset to load models on end-user PCs,
    #  maybe for direct use in game.
    #
    # If you're using DirectX, don't forget to combine this value with
    # the ConvertToLeftHanded step. If you don't support UV transformations
    # in your application apply the TransformUVCoords step, too.
    #  @note Please take the time to read the docs for the steps enabled by this preset.
    #  Some of them offer further configurable properties, while some of them might not be of
    #  use for you so it might be better to not specify them.
    #
    TargetRealtime_Fast = (
        0
        | ProcessingStep.CalcTangentSpace
        | ProcessingStep.GenNormals
        | ProcessingStep.JoinIdenticalVertices
        | ProcessingStep.Triangulate
        | ProcessingStep.GenUVCoords
        | ProcessingStep.SortByPType
    )

    # @def TargetRealtime_Quality
    #  @brief Default postprocess configuration optimizing the data for real-time rendering.
    #
    #  Unlike #TargetRealtime_Fast, this configuration
    #  performs some extra optimizations to improve rendering speed and
    #  to minimize memory usage. It could be a good choice for a level editor
    #  environment where import speed is not so important.
    #
    #  If you're using DirectX, don't forget to combine this value with
    #  the ConvertToLeftHanded step. If you don't support UV transformations
    #  in your application apply the TransformUVCoords step, too.
    #  @note Please take the time to read the docs for the steps enabled by this preset.
    #  Some of them offer further configurable properties, while some of them might not be
    #  of use for you so it might be better to not specify them.
    #
    TargetRealtime_Quality = (
        0
        | ProcessingStep.CalcTangentSpace
        | ProcessingStep.GenSmoothNormals
        | ProcessingStep.JoinIdenticalVertices
        | ProcessingStep.ImproveCacheLocality
        | ProcessingStep.LimitBoneWeights
        | ProcessingStep.RemoveRedundantMaterials
        | ProcessingStep.SplitLargeMeshes
        | ProcessingStep.Triangulate
        | ProcessingStep.GenUVCoords
        | ProcessingStep.SortByPType
        | ProcessingStep.FindDegenerates
        | ProcessingStep.FindInvalidData
    )

    # @def TargetRealtime_MaxQuality
    #  @brief Default postprocess configuration optimizing the data for real-time rendering.
    #
    #  This preset enables almost every optimization step to achieve perfectly
    #  optimized data. It's your choice for level editor environments where import speed
    #  is not important.
    #
    #  If you're using DirectX, don't forget to combine this value with
    #  the ConvertToLeftHanded step. If you don't support UV transformations
    #  in your application, apply the TransformUVCoords step, too.
    #  @note Please take the time to read the docs for the steps enabled by this preset.
    #  Some of them offer further configurable properties, while some of them might not be
    #  of use for you so it might be better to not specify them.
    #
    TargetRealtime_MaxQuality = (
        0
        | TargetRealtime_Quality
        | ProcessingStep.FindInstances
        | ProcessingStep.ValidateDataStructure
        | ProcessingStep.OptimizeMeshes
    )


class MaterialPropertyTuple(NamedTuple):
    name: str
    semantic: int


class MaterialPropertyKey:
    def __init__(self):
        raise RuntimeError("Don't instantiate this")

    # https://github.com/assimp/assimp/blob/1d33131e902ff3f6b571ee3964c666698a99eb0f/include/assimp/material.h#L943
    # TODO: There should be some constants that also specify an index into
    #   the property's array after the semantic. Should add support for that.
    NAME = MaterialPropertyTuple("?mat.name", 0)
    TWOSIDED = MaterialPropertyTuple("$mat.twosided", 0)
    SHADING_MODEL = MaterialPropertyTuple("$mat.shadingm", 0)
    ENABLE_WIREFRAME = MaterialPropertyTuple("$mat.wireframe", 0)
    BLEND_FUNC = MaterialPropertyTuple("$mat.blend", 0)
    OPACITY = MaterialPropertyTuple("$mat.opacity", 0)
    TRANSPARENCYFACTOR = MaterialPropertyTuple("$mat.transparencyfactor", 0)
    BUMPSCALING = MaterialPropertyTuple("$mat.bumpscaling", 0)
    SHININESS = MaterialPropertyTuple("$mat.shininess", 0)
    REFLECTIVITY = MaterialPropertyTuple("$mat.reflectivity", 0)
    SHININESS_STRENGTH = MaterialPropertyTuple("$mat.shinpercent", 0)
    REFRACTI = MaterialPropertyTuple("$mat.refracti", 0)
    COLOR_DIFFUSE = MaterialPropertyTuple("$clr.diffuse", 0)
    COLOR_AMBIENT = MaterialPropertyTuple("$clr.ambient", 0)
    COLOR_SPECULAR = MaterialPropertyTuple("$clr.specular", 0)
    COLOR_EMISSIVE = MaterialPropertyTuple("$clr.emissive", 0)
    COLOR_TRANSPARENT = MaterialPropertyTuple("$clr.transparent", 0)
    COLOR_REFLECTIVE = MaterialPropertyTuple("$clr.reflective", 0)
    GLOBAL_BACKGROUND_IMAGE = MaterialPropertyTuple("?bg.global", 0)
    GLOBAL_SHADERLANG = MaterialPropertyTuple("?sh.lang", 0)
    SHADER_VERTEX = MaterialPropertyTuple("?sh.vs", 0)
    SHADER_FRAGMENT = MaterialPropertyTuple("?sh.fs", 0)
    SHADER_GEO = MaterialPropertyTuple("?sh.gs", 0)
    SHADER_TESSELATION = MaterialPropertyTuple("?sh.ts", 0)
    SHADER_PRIMITIVE = MaterialPropertyTuple("?sh.ps", 0)
    SHADER_COMPUTE = MaterialPropertyTuple("?sh.cs", 0)
    BASE_COLOR = MaterialPropertyTuple("$clr.base", 0)
    USE_METALLIC_MAP = MaterialPropertyTuple("$mat.useMetallicMap", 0)
    # Metallic factor. 0.0 = Full Dielectric, 1.0 = Full Metal
    METALLIC_FACTOR = MaterialPropertyTuple("$mat.metallicFactor", 0)

    USE_ROUGHNESS_MAP = MaterialPropertyTuple("$mat.useRoughnessMap", 0)
    # Roughness factor. 0.0 = Perfectly Smooth, 1.0 = Completely Rough
    ROUGHNESS_FACTOR = MaterialPropertyTuple("$mat.roughnessFactor", 0)
    # Specular/Glossiness Workflow
    # ---------------------------
    # Diffuse/Albedo Color. Note: Pure Metals have a diffuse of {0,0,0}
    # AI_MATKEY_COLOR_DIFFUSE
    # Specular Color.
    # Note: Metallic/Roughness may also have a Specular Color
    # AI_MATKEY_COLOR_SPECULAR
    SPECULAR_FACTOR = MaterialPropertyTuple("$mat.specularFactor", 0)
    # Glossiness factor. 0.0 = Completely Rough, 1.0 = Perfectly Smooth
    GLOSSINESS_FACTOR = MaterialPropertyTuple("$mat.glossinessFactor", 0)

    # Sheen
    # -----
    # Sheen base RGB color. Default {0,0,0}
    SHEEN_COLOR_FACTOR = MaterialPropertyTuple("$clr.sheen.factor", 0)
    # Sheen Roughness Factor.
    SHEEN_ROUGHNESS_FACTOR = MaterialPropertyTuple("$mat.sheen.roughnessFactor", 0)

    # Clearcoat
    # ---------
    # Clearcoat layer intensity. 0.0 = none (disabled)
    CLEARCOAT_FACTOR = MaterialPropertyTuple("$mat.clearcoat.factor", 0)
    CLEARCOAT_ROUGHNESS_FACTOR = MaterialPropertyTuple("$mat.clearcoat.roughnessFactor", 0)

    # Transmission
    # ------------
    # https:#github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_transmission
    # Base percentage of light transmitted through the surface. 0.0 = Opaque, 1.0 = Fully transparent
    TRANSMISSION_FACTOR = MaterialPropertyTuple("$mat.transmission.factor", 0)
    # Texture defining percentage of light transmitted through the surface.
    # Multiplied by AI_MATKEY_TRANSMISSION_FACTOR

    # Emissive
    # --------
    USE_EMISSIVE_MAP = MaterialPropertyTuple("$mat.useEmissiveMap", 0)
    EMISSIVE_INTENSITY = MaterialPropertyTuple("$mat.emissiveIntensity", 0)
    USE_AO_MAP = MaterialPropertyTuple("$mat.useAOMap", 0)

    TEXTURE = "$tex.file"
    UVWSRC = "$tex.uvwsrc"
    TEXOP = "$tex.op"
    MAPPING = "$tex.mapping"
    TEXBLEND = "$tex.blend"
    MAPPINGMODE_U = "$tex.mapmodeu"
    MAPPINGMODE_V = "$tex.mapmodev"
    TEXMAP_AXIS = "$tex.mapaxis"
    UVTRANSFORM = "$tex.uvtrafo"
    TEXFLAGS = "$tex.flags"
