"""
This module demonstrates the functionality of Impasse.
"""

from __future__ import print_function

import sys
import logging

import numpy

import impasse
from impasse.constants import ProcessingStep

logging.basicConfig(level=logging.INFO)


def recur_node(node, level=0):
    print("  " + "\t" * level + "- " + str(node))
    for child in node.children:
        recur_node(child, level + 1)


def main(filename=None):
    scene = impasse.load(filename, processing=ProcessingStep.Triangulate)

    # the model we load
    print("MODEL:" + filename)
    print("")

    # write some statistics
    print("SCENE:")
    print("  meshes:" + str(len(scene.meshes)))
    print("  materials:" + str(len(scene.materials)))
    print("  textures:" + str(len(scene.textures)))
    print("")

    print("NODES:")
    recur_node(scene.root_node)

    print("")
    print("MESHES:")
    for index, mesh in enumerate(scene.meshes):
        print("  MESH" + str(index + 1))
        print("    material id:" + str(scene.materials.index(mesh.material) + 1))
        print("    vertices:" + str(len(mesh.vertices)))
        print("    first 3 verts:\n" + str(numpy.array(mesh.vertices[:3])))
        if mesh.normals:
            print("    first 3 normals:\n" + str(numpy.array(mesh.normals[:3])))
        else:
            print("    no normals")
        print("    colors:" + str(len(mesh.colors)))
        tcs = mesh.texture_coords
        if tcs:
            for tc_index, tc in enumerate(tcs):
                print("    texture-coords " + str(tc_index) + ":" + str(len(tcs[tc_index])) + "first3:\n" + str(
                    numpy.array(tcs[tc_index][:3])))

        else:
            print("    no texture coordinates")
        print("    uv-component-count:" + str(len(mesh.num_uv_components)))
        print("    faces:" + str(len(mesh.faces)) + " -> first:\n" + str([tuple(f.indices) for f in mesh.faces[:3]]))
        print("    bones:" + str(len(mesh.bones)) + " -> first:" + str([str(b) for b in mesh.bones[:3]]))
        print("")

    print("MATERIALS:")
    for index, material in enumerate(scene.materials):
        print("  MATERIAL (id:" + str(index + 1) + ")")
        for key, value in material.as_mapping().items():
            print("    %s: %s" % (key, value))
    print("")

    print("TEXTURES:")
    for index, texture in enumerate(scene.textures):
        print("  TEXTURE" + str(index + 1))
        print("    width:" + str(texture.width))
        print("    height:" + str(texture.height))
        print("    hint:" + str(texture.ach_format_hint))
        print("    data (size):" + str(len(texture.data)))
    print("")

    print("METADATA:")
    if scene.metadata:
        for key, value in scene.metadata.as_mapping().items():
            print("    %s: %s" % (key, value))


def usage():
    print("Usage: sample.py <3d model>")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
    else:
        main(sys.argv[1])
