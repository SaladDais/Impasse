import os.path
import tempfile
import unittest

import numpy

import impasse
from impasse.constants import TextureSemantic, MaterialPropertyKey

# Find the root path of the test file so we can find the
# test models above our directory

HERE = os.path.abspath(os.path.dirname(__file__))
MODELS_DIR = os.path.abspath(os.path.join(HERE, 'test_data'))
TEST_SKINNED_MODEL = os.path.join(MODELS_DIR, 'glTF2', 'simple_skin', 'simple_skin.gltf')
TEST_COLLADA = os.path.join(MODELS_DIR, 'Collada', 'COLLADA.dae')


class ImpasseTests(unittest.TestCase):
    def test_skinned(self):
        scene = impasse.load(TEST_SKINNED_MODEL)
        self.assertIsNotNone(scene.root_node)
        self.assertEqual(len(scene.meshes), 1)
        bone_names = [b.name for b in scene.meshes[0].bones]
        self.assertEqual(["nodes_1", "nodes_2"], bone_names)

    def test_collada_parses(self):
        self.assertIsNotNone(impasse.load(TEST_COLLADA).root_node)

    def test_materials_mapping(self):
        scene = impasse.load(TEST_COLLADA)
        material_map = scene.materials[0].as_mapping()
        self.assertEqual(material_map["?mat.name"], "RedPlastic")
        self.assertEqual(material_map["?mat.name", TextureSemantic.NONE], "RedPlastic")

    def test_materials_mapping_constant_access(self):
        scene = impasse.load(TEST_COLLADA)
        material_map = scene.materials[0].as_mapping()
        self.assertEqual(material_map[MaterialPropertyKey.NAME], "RedPlastic")

    def test_mutate_materials_mapping(self):
        scene = impasse.load(TEST_COLLADA).copy_mutable()
        material_map = scene.materials[0].as_mapping()
        material_map["?mat.name"] = "BluePlastic"
        self.assertEqual(material_map["?mat.name", TextureSemantic.NONE], "BluePlastic")

    def test_metadata_mapping(self):
        scene = impasse.load(TEST_COLLADA)
        metadata = scene.metadata.as_mapping()
        self.assertEqual(metadata['Created'], '2006-06-21T21:15:16Z')

    def test_mutate_metadata_mapping(self):
        scene = impasse.load(TEST_COLLADA).copy_mutable()
        metadata = scene.metadata.as_mapping()
        metadata['Created'] = '2026-06-21T21:15:16Z'
        self.assertEqual(metadata['Created'], '2026-06-21T21:15:16Z')

    def test_export(self):
        scene = impasse.load(TEST_COLLADA)
        with tempfile.NamedTemporaryFile() as export_file:
            impasse.export(scene, export_file.name, "collada")
            self.assertNotEqual(os.lstat(export_file.name).st_size, 0)

    def test_export_blob(self):
        scene = impasse.load(TEST_COLLADA)
        blob = impasse.export_blob(scene, "collada")
        self.assertTrue(blob[0].data.startswith(b"<?xml"))

    def test_scene_immutable(self):
        scene = impasse.load(TEST_COLLADA)
        with self.assertRaises(AttributeError):
            scene.root_node.name = "foobaz"

    def test_copy_scene(self):
        scene = impasse.load(TEST_COLLADA).copy_mutable()
        self.assertIsNotNone(scene.root_node)

    def test_scene_copies_mutable(self):
        scene = impasse.load(TEST_COLLADA)
        scene_copy = scene.copy_mutable()
        scene_copy.root_node.name = "foobaz"
        self.assertEqual(scene_copy.root_node.name, "foobaz")
        blob = impasse.export_blob(scene_copy, "collada")
        self.assertTrue(b"foobaz" in blob[0].data)
        # Original should not be changed
        self.assertNotEqual(scene.root_node.name, "foobaz")

    def test_accessing_material_index(self):
        scene = impasse.load(TEST_COLLADA)
        collada = None
        for child in scene.root_node.children:
            if child.name == "Collada":
                collada = child
        self.assertIsNotNone(collada)
        material_map = collada.meshes[0].material.as_mapping()
        self.assertEqual(material_map["?mat.name"], "RedPlastic")

    def test_mesh_numpy_properties(self):
        scene = impasse.load(TEST_COLLADA)
        self.assertListEqual([-400.0, 0.0, -200.0], list(scene.meshes[0].vertices[0]))

    def test_mutating_mesh_numpy_properties(self):
        scene = impasse.load(TEST_COLLADA).copy_mutable()
        verts_copy: numpy.ndarray = scene.meshes[0].vertices[0].copy()
        verts_copy[1] = 40.0
        scene.meshes[0].vertices[0] = verts_copy
        # Check that we actually mutated the underlying data
        self.assertEqual(40.0, scene.meshes[0].vertices[0][1])

    def test_mutating_mesh_numpy_array(self):
        scene = impasse.load(TEST_COLLADA).copy_mutable()
        scene.meshes[0].vertices[0][1] = 40.0
        # Check that we actually mutated the underlying data
        self.assertEqual(40.0, scene.meshes[0].vertices[0][1])


if __name__ == "__main__":
    unittest.main()
