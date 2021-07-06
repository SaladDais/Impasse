"""
Impasse

This is the main-module of Impasse.
"""
from __future__ import annotations

import sys
from typing import Optional, Union, Protocol, Callable
import logging

from . import helper
from .constants import ProcessingStep
from .errors import AssimpError
from .structs import Scene, ExportDataBlob

logger = logging.getLogger("impasse")
# attach default null handler to logger so it doesn't complain
# even if you don't attach another handler to logger
logger.addHandler(logging.NullHandler())


class AssimpLib:
    """
    Assimp-Singleton
    """
    # TODO: Get rid of this.
    load, load_mem, export, export_blob, release, dll = helper.search_library()


_assimp_lib = AssimpLib()


class LoadedScene(Scene):
    def __init__(self, struct_val):
        super().__init__(struct_val)
        self._readonly = True

    def __enter__(self) -> LoadedScene:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: ffi.gc() instead?
        release(self)


def release(scene: LoadedScene):
    """Release resources of a loaded scene."""
    _assimp_lib.release(scene.struct)


class _Readable(Protocol):
    read: Callable[[], bytes]


def load(
    file_or_name: Union[str, _Readable],
    file_type: Optional[str] = None,
    processing=ProcessingStep.Triangulate,
) -> LoadedScene:
    """
    Load a model into a scene. On failure throws AssimpError.

    Arguments
    ---------
    file_or_name:   Either a filename or a file object to load model from.
                    If a file object is passed, file_type MUST be specified
                    Otherwise Assimp has no idea which importer to use.
                    This is named 'filename' so as to not break legacy code.
    processing: assimp postprocessing parameters. Verbose keywords are imported
                from postprocessing, and the parameters can be combined bitwise to
                generate the final processing value. Note that the default value will
                triangulate quad faces. Example of generating other possible values:
                processing = (impasse.postprocess.aiProcess_Triangulate |
                              impasse.postprocess.aiProcess_OptimizeMeshes)
    file_type:  string of file extension, such as 'stl'

    Returns
    ---------
    Scene object with model data
    """

    if hasattr(file_or_name, 'read'):
        # This is the case where a file object has been passed to load.
        # It is calling the following function:
        # const aiScene* aiImportFileFromMemory(const char* pBuffer,
        #                                      unsigned int pLength,
        #                                      unsigned int pFlags,
        #                                      const char* pHint)
        if file_type is None:
            raise AssimpError('File type must be specified when passing file objects!')
        data = file_or_name.read()
        model = _assimp_lib.load_mem(data,
                                     len(data),
                                     processing,
                                     file_type)
    else:
        # a filename string has been passed
        model = _assimp_lib.load(file_or_name.encode(sys.getfilesystemencoding()), processing)

    if not model:
        raise AssimpError('Could not import file!')
    return LoadedScene(model)


def export(
    scene: Scene,
    filename: str,
    file_type: str,
    processing=ProcessingStep.Triangulate
):
    """
    Export a scene. On failure throws AssimpError.

    Arguments
    ---------
    scene: scene to export.
    filename: Filename that the scene should be exported to.
    file_type: string of file exporter to use. For example "collada".
    processing: assimp postprocessing parameters. Verbose keywords are imported
                from postprocessing, and the parameters can be combined bitwise to
                generate the final processing value. Note that the default value will
                triangulate quad faces. Example of generating other possible values:
                processing = (impasse.postprocess.aiProcess_Triangulate |
                              impasse.postprocess.aiProcess_OptimizeMeshes)

    """

    export_status = _assimp_lib.export(
        scene,
        file_type.encode("ascii"),
        filename.encode(sys.getfilesystemencoding()),
        processing,
    )

    if export_status != 0:
        raise AssimpError('Could not export scene!')


def export_blob(
    scene: Scene,
    file_type: str,
    processing=ProcessingStep.Triangulate
):
    """
    Export a scene and return a blob in the correct format. On failure throws AssimpError.

    Arguments
    ---------
    scene: scene to export.
    file_type: string of file exporter to use. For example "collada".
    processing: assimp postprocessing parameters. Verbose keywords are imported
                from postprocessing, and the parameters can be combined bitwise to
                generate the final processing value. Note that the default value will
                triangulate quad faces. Example of generating other possible values:
                processing = (impasse.postprocess.aiProcess_Triangulate |
                              impasse.postprocess.aiProcess_OptimizeMeshes)
    Returns
    ---------
    ExportDataBlob
    """
    export_blob_ptr = _assimp_lib.export_blob(
        scene.struct,
        file_type.encode("ascii"),
        processing
    )

    if not export_blob_ptr:
        raise AssimpError('Could not export scene to blob!')
    return ExportDataBlob(export_blob_ptr)
