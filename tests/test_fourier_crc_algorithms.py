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
        Tests Fourier transform plugins: dft and fft for spectrum computation
        and magnitude calculation.
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

            n = final_step.extra["N"]
            self.assertEqual(len(final_step.extra["spectrum"]), n)
            self.assertEqual(len(final_step.extra["magnitude"]), n)

            # Peak frequency bin magnitude test
            magnitudes = final_step.extra["magnitude"]
            peak_mag = max(magnitudes)
            self.assertAlmostEqual(peak_mag, 4.0, delta=1e-3)

    def test_crc_and_rs_error_detection_contracts(self):
        """
        Tests error detection / correction plugins: crc and reed_solomon.
        """
        # CRC
        crc_plugin = self.loader.get_plugin("crc")
        crc_steps = list(crc_plugin.get_steps([]))
        final_crc = crc_steps[-1]
        self.assertIn("has_error", final_crc.extra)
        self.assertTrue(final_crc.extra["has_error"], "CRC failed to detect corrupted bit error")

        # Reed-Solomon
        rs_plugin = self.loader.get_plugin("reed_solomon")
        rs_steps = list(rs_plugin.get_steps([]))
        final_rs = rs_steps[-1]
        self.assertIn("success", final_rs.extra)
        self.assertTrue(final_rs.extra["success"])
        self.assertIn("codeword", final_rs.extra)
        decoded_str = ",".join(map(str, final_rs.extra["decoded"]))
        self.assertEqual(decoded_str, final_rs.extra["data"])


if __name__ == "__main__":
    unittest.main()
