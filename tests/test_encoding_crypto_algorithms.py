# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestEncodingCryptoAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_encoding_crypto_plugins(self):
        """
        Tests encoding and crypto plugins: base64, caesar, huffman, rle, enigma.
        Checks known-answer transformations and step metrics.
        """
        encoding_pids = ["base64", "caesar", "huffman", "rle", "enigma"]

        for pid in encoding_pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)
            self.assertIn("phase", final_step.extra)

    def test_base64_known_answer(self):
        plugin = self.loader.get_plugin("base64")
        plugin.set_param("text", "ABC")
        steps = list(plugin.get_steps([]))
        final_step = steps[-1]
        self.assertEqual(final_step.extra.get("encoded"), "QUJD")

    def test_caesar_known_answer(self):
        plugin = self.loader.get_plugin("caesar")
        plugin.set_param("text", "HELLO")
        plugin.set_param("shift", 3)
        steps = list(plugin.get_steps([]))
        final_step = steps[-1]
        self.assertEqual(final_step.extra.get("encoded"), "KHOOR")


if __name__ == "__main__":
    unittest.main()
