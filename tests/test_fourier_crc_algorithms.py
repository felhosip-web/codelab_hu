# -*- coding: utf-8 -*-
import unittest
import math
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestFourierCRCAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_dft_and_fft_transform_contracts(self):
        """
        Tests Fourier transform plugins: dft and fft for spectrum computation.
        """
        for pid in ["dft", "fft"]:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIn("N", final_step.extra)
            self.assertIn("spectrum", final_step.extra)
            self.assertIn("magnitude", final_step.extra)

            # Spectrum and magnitude length equal N
            n = final_step.extra["N"]
            self.assertEqual(len(final_step.extra["spectrum"]), n)
            self.assertEqual(len(final_step.extra["magnitude"]), n)

    def test_crc_and_rs_error_detection_contracts(self):
        """
        Tests error detection / correction plugins: crc and reed_solomon.
        """
        # CRC
        crc_plugin = self.loader.get_plugin("crc")
        crc_steps = list(crc_plugin.get_steps([]))
        self.assertIn("has_error", crc_steps[-1].extra)

        # Reed-Solomon
        rs_plugin = self.loader.get_plugin("reed_solomon")
        rs_steps = list(rs_plugin.get_steps([]))
        self.assertIn("success", rs_steps[-1].extra)
        self.assertTrue(rs_steps[-1].extra["success"])
        self.assertIn("codeword", rs_steps[-1].extra)


if __name__ == "__main__":
    unittest.main()
