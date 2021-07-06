"""
Some fancy helper functions.
"""

import os
import ctypes
import operator
from distutils.sysconfig import get_python_lib
import re
import sys
import logging

import numpy

from .errors import AssimpError
from .structs import Node, Scene, ffi

logger = logging.getLogger("impasse")


def transform(vector3, matrix4x4):
    """ Apply a transformation matrix on a 3D vector.

    :param vector3: array with 3 elements
    :param matrix4x4: 4x4 matrix
    """
    return numpy.dot(matrix4x4, numpy.append(vector3, 1.))


def get_bounding_box(scene: Scene):
    bb_min = [1e10, 1e10, 1e10]  # x,y,z
    bb_max = [-1e10, -1e10, -1e10]  # x,y,z
    transformation = numpy.linalg.inv(scene.root_node.transformation)
    return get_bounding_box_for_node(scene, scene.root_node, bb_min, bb_max, transformation)


def get_bounding_box_for_node(scene: Scene, node: Node, bb_min, bb_max, transformation):
    transformation = numpy.dot(transformation, node.transformation)

    for mesh_idx in node.meshes:
        mesh = scene.meshes[mesh_idx]
        for v in mesh.vertices:
            v = transform(v, transformation)
            bb_min[0] = min(bb_min[0], v[0])
            bb_min[1] = min(bb_min[1], v[1])
            bb_min[2] = min(bb_min[2], v[2])
            bb_max[0] = max(bb_max[0], v[0])
            bb_max[1] = max(bb_max[1], v[1])
            bb_max[2] = max(bb_max[2], v[2])

    for child in node.children:
        bb_min, bb_max = get_bounding_box_for_node(scene, child, bb_min, bb_max, transformation)

    return bb_min, bb_max


def try_load_functions(library_path, dll):
    """
    Try to bind to aiImportFile and aiReleaseImport

    library_path: path to current lib
    dll:          ctypes handle to library
    """

    try:
        load = dll.aiImportFile
        release = dll.aiReleaseImport
        load_mem = dll.aiImportFileFromMemory
        export = dll.aiExportScene
        export2blob = dll.aiExportSceneToBlob
    except AttributeError:
        # OK, this is a library, but it doesn't have the functions we need
        return None

    return library_path, load, load_mem, export, export2blob, release, dll


def get_search_config():
    additional_dirs = []
    ext_whitelist = []
    # populate search directories and lists of allowed file extensions
    # depending on the platform we're running on.
    if os.name == 'posix':
        additional_dirs.append('./')
        additional_dirs.append('/usr/lib/')
        additional_dirs.append('/usr/lib/x86_64-linux-gnu/')
        additional_dirs.append('/usr/lib/aarch64-linux-gnu/')
        additional_dirs.append('/usr/local/lib/')

        if 'LD_LIBRARY_PATH' in os.environ:
            additional_dirs.extend([item for item in os.environ['LD_LIBRARY_PATH'].split(':') if item])

        # check if running from anaconda.
        if "conda" or "continuum" in sys.version.lower():
            cur_path = get_python_lib()
            pattern = re.compile(r'.*/lib/')
            conda_lib = pattern.match(cur_path).group()
            logger.info("Adding Anaconda lib path:" + conda_lib)
            additional_dirs.append(conda_lib)

        # note - this won't catch libassimp.so.N.n, but
        # currently there's always a symlink called
        # libassimp.so in /usr/local/lib.
        ext_whitelist.append('.so')
        # libassimp.dylib in /usr/local/lib
        ext_whitelist.append('.dylib')

    elif os.name == 'nt':
        ext_whitelist.append('.dll')
        path_dirs = os.environ['PATH'].split(';')
        additional_dirs.extend(path_dirs)
    return additional_dirs, ext_whitelist


def search_library():
    """
    Loads the assimp library.
    Throws exception AssimpError if no library_path is found

    Returns: tuple, (load from filename function,
                     load from memory function,
                     export to filename function,
                     export to blob function,
                     release function,
                     dll)
    """
    folder = os.path.dirname(__file__)
    additional_dirs, ext_whitelist = get_search_config()

    # silence 'DLL not found' message boxes on win
    try:
        ctypes.windll.kernel32.SetErrorMode(0x8007)
    except AttributeError:
        pass

    candidates = []
    # test every file
    for curfolder in [folder]+additional_dirs:
        if os.path.isdir(curfolder):
            for filename in os.listdir(curfolder):
                # our minimum requirement for candidates is that
                # they should contain 'assimp' somewhere in
                # their name
                if filename.lower().find('assimp') == -1:
                    continue

                # Not a whitelisted extension
                if not any(ext in filename.lower() for ext in ext_whitelist):
                    continue

                library_path = os.path.join(curfolder, filename)
                logger.debug('Try ' + library_path)
                try:
                    dll = ffi.dlopen(library_path)
                except Exception as e:
                    logger.warning(str(e))
                    # OK, this except is evil. But different OSs will throw different
                    # errors. So just ignore any errors.
                    continue
                # see if the functions we need are in the dll
                loaded = try_load_functions(library_path, dll)
                if loaded:
                    candidates.append(loaded)

    if not candidates:
        # no library found
        raise AssimpError("assimp library not found")
    else:
        # get the newest library_path
        candidates = map(lambda x: (os.lstat(x[0])[-2], x), candidates)
        res = max(candidates, key=operator.itemgetter(0))[1]
        logger.debug('Using assimp library located at ' + res[0])

        # XXX: if there are 1000 dll/so files containing 'assimp'
        # in their name, do we have all of them in our address
        # space now until gc kicks in?

        # XXX: take version postfix of the .so on linux?
        return res[1:]
