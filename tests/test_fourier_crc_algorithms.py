# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestFourierCRCAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_fourier_plugins(self):
        """
        Tests Fourier transform plugins: dft, fft.
        """
        fourier_pids = ["dft", "fft"]

        for pid in fourier_pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)

    def test_crc_and_rs_plugins(self):
        """
        Tests error detection / correction plugins: crc, reed_solomon.
        """
        crc_pids = ["crc", "reed_solomon"]

        for pid in crc_pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)


if __name__ == "__main__":
    unittest.main()
