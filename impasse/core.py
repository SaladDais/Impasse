"""
Impasse

This is the main-module of Impasse.
"""
from __future__ import annotations

import os
import sys
from typing import Optional, Union, BinaryIO, List
import logging

from . import helper
from .constants import ProcessingStep
from .errors import AssimpError
from .structs import Scene, ExportDataBlob, ffi

logger = logging.getLogger("impasse")
# attach default null handler to logger so it doesn't complain
# even if you don't attach another handler to logger
logger.addHandler(logging.NullHandler())


_assimp_lib = helper.search_library()


class ImportedScene(Scene):
    def __init__(self, struct_val):
        # Will be released after the last reference to this Scene object dies
        # If you want to force an early release you can just set `ImportedScene.struct = None`
        # Since there are no other strong references to the actual struct.
        super().__init__(ffi.gc(struct_val, _assimp_lib.aiReleaseImport))
        self._readonly = True

    def copy_mutable(self) -> CopiedScene:
        """
        Return a mutable copy of the Scene

        import() returns a const pointer, if you want to mutate a scene you're
        supposed to copy it first.
        """
        copy_out = ffi.new("struct aiScene **")
        _assimp_lib.aiCopyScene(self.struct, copy_out)
        if not copy_out[0]:
            raise AssimpError("Unable to copy scene")
        return CopiedScene(copy_out[0])


class CopiedScene(Scene):
    def __init__(self, struct_val):
        super().__init__(ffi.gc(struct_val, _assimp_lib.aiFreeScene))
        self._readonly = False


class OwnedExportDataBlob(ExportDataBlob):
    """Export Data Blob that's owned by Python."""
    def __init__(self, struct_val):
        super().__init__(ffi.gc(struct_val, _assimp_lib.aiReleaseExportBlob))


def load(
    file_or_name: Union[str, BinaryIO],
    file_type: Optional[str] = None,
    processing=ProcessingStep.Triangulate,
) -> ImportedScene:
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
        model = _assimp_lib.aiImportFileFromMemory(
            data, len(data), processing, file_type)
    else:
        # a filename string has been passed
        model = _assimp_lib.aiImportFile(file_or_name.encode(sys.getfilesystemencoding()), processing)

    if not model:
        raise AssimpError('Could not import file!')
    return ImportedScene(model)


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

    export_status = _assimp_lib.aiExportScene(
        scene.struct,
        file_type.encode("ascii"),
        os.path.abspath(filename).encode(sys.getfilesystemencoding()),
        processing,
    )

    if export_status != 0:
        raise AssimpError('Could not export scene!')


def export_blob(
    scene: Scene,
    file_type: str,
    processing=ProcessingStep.Triangulate
) -> List[ExportDataBlob]:
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
                processing = (impasse.postprocess.ProcessingStep.Triangulate |
                              impasse.postprocess.ProcessingStep.OptimizeMeshes)
    Returns
    ---------
    ExportDataBlob
    """
    export_blob_ptr = _assimp_lib.aiExportSceneToBlob(
        scene.struct,
        file_type.encode("ascii"),
        processing
    )

    if not export_blob_ptr:
        raise AssimpError('Could not export scene to blob!')
    # TODO: assimp's API for blobs is a little funky. Rather than releasing blobs
    #  invidually you only release the head of the list. That means we should
    #  make sure the head doesn't die until the last child node has died.
    #  Should maybe replace struct `scene` member with an `owner` member.

    # Convert the linked list to a regular list
    blob = OwnedExportDataBlob(export_blob_ptr)
    blob_list = [blob]
    blob = blob.next
    while blob is not None:
        blob_list.append(blob.next)
        blob = blob.next
    return blob_list
