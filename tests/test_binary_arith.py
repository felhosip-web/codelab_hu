# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestBinaryArithPlugins(unittest.TestCase):
    def setUp(self):
        self.loader = PluginLoader()
        self.loader.load_all()

    def test_plugins_loaded(self):
        plugins = self.loader.plugins
        self.assertIn("binary_add", plugins)
        self.assertIn("binary_sub", plugins)
        self.assertIn("binary_mul", plugins)
        self.assertIn("binary_bits", plugins)

    def test_supported_languages(self):
        expected_langs = {"Python", "C++", "C", "Java", "Pascal", "BASIC"}
        for pid in ["binary_add", "binary_sub", "binary_mul", "binary_bits"]:
            plugin = self.loader.get_plugin(pid)
            supported = set(plugin.get_supported_languages())
            self.assertTrue(expected_langs.issubset(supported), f"{pid} missing languages: {expected_langs - supported}")
            for lang in expected_langs:
                code = plugin.get_code(lang)
                self.assertTrue(len(code) > 0, f"{pid} code for {lang} is empty")

    def test_binary_add_steps_and_overflow(self):
        plugin = self.loader.get_plugin("binary_add")
        self.assertIsNotNone(plugin)

        # Normal case
        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_res = steps[-1].extra["result"]
        self.assertEqual(final_res & 0xFF, (13 + 7) & 0xFF)
        self.assertEqual(final_res, 20)

        # 8-bit overflow case (200 + 100 = 300, 300 & 0xFF = 44)
        overflow_steps = list(plugin.get_steps([200, 100]))
        self.assertEqual(overflow_steps[-1].extra["result"] & 0xFF, (200 + 100) & 0xFF)

    def test_binary_sub_steps_and_underflow(self):
        plugin = self.loader.get_plugin("binary_sub")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_res = steps[-1].extra["result"]
        self.assertEqual(final_res & 0xFF, (13 - 7) & 0xFF)
        self.assertEqual(final_res, 6)

        # Underflow case (7 - 13 = -6, -6 & 0xFF = 250)
        underflow_steps = list(plugin.get_steps([7, 13]))
        self.assertEqual(underflow_steps[-1].extra["result"] & 0xFF, (7 - 13) & 0xFF)

    def test_binary_mul_steps(self):
        plugin = self.loader.get_plugin("binary_mul")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_res = steps[-1].extra["result"]
        self.assertEqual(final_res, 13 * 7)
        self.assertEqual(final_res, 91)
        self.assertEqual(final_res & 0xFF, 91)

    def test_binary_bits_contract(self):
        """
        Tests Bitek - bináris varázs plugin for 5-bit representations
        and bit shift operations.
        """
        plugin = self.loader.get_plugin("binary_bits")
        self.assertIsNotNone(plugin)

        plugin.set_param("num", 13)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["num"], 13)
        self.assertEqual(final_step.extra["binary"], "01101")
        self.assertEqual(final_step.extra["ones"], 3)


if __name__ == "__main__":
    unittest.main()
