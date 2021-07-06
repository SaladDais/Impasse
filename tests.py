import os.path
import tempfile
import unittest

import impasse
from impasse.constants import TextureSemantic

# Find the root path of the test file so we can find the
# test models above our directory

HERE = os.path.abspath(os.path.dirname(__file__))
MODELS_DIR = os.path.abspath(os.path.join(HERE, 'test_data'))
TEST_SKINNED_MODEL = os.path.join(MODELS_DIR, 'glTF2', 'simple_skin', 'simple_skin.gltf')
TEST_COLLADA = os.path.join(MODELS_DIR, 'Collada', 'COLLADA.dae')


class ImpasseTests(unittest.TestCase):
    def test_skinned(self):
        with impasse.load(TEST_SKINNED_MODEL) as scene:
            self.assertIsNotNone(scene.root_node)
            self.assertEqual(len(scene.meshes), 1)
            bone_names = [b.name for b in scene.meshes[0].bones]
            self.assertEqual(["nodes_1", "nodes_2"], bone_names)

    def test_collada_parses(self):
        with impasse.load(TEST_COLLADA) as scene:
            self.assertIsNotNone(scene.root_node)

    def test_regular_load(self):
        scene = None
        try:
            scene = impasse.load(TEST_SKINNED_MODEL)
            self.assertIsNotNone(scene.root_node)
        finally:
            if scene:
                impasse.release_import(scene)

    def test_materials_mapping(self):
        with impasse.load(TEST_COLLADA) as scene:
            material_map = scene.materials[0].as_mapping()
            self.assertEqual(material_map["?mat.name"], "RedPlastic")
            self.assertEqual(material_map["?mat.name", TextureSemantic.NONE], "RedPlastic")

    def test_metadata_mapping(self):
        with impasse.load(TEST_COLLADA) as scene:
            metadata = scene.metadata.as_mapping()
            self.assertEqual(metadata['Created'], '2006-06-21T21:15:16Z')

    def test_export(self):
        with impasse.load(TEST_COLLADA) as scene:
            with tempfile.NamedTemporaryFile() as export_file:
                impasse.export(scene, export_file.name, "collada")
                self.assertNotEqual(os.lstat(export_file.name).st_size, 0)

    def test_export_blob(self):
        with impasse.load(TEST_COLLADA) as scene:
            with impasse.export_blob(scene, "collada") as blob:
                self.assertTrue(blob.data.startswith(b"<?xml"))


if __name__ == "__main__":
    unittest.main()
