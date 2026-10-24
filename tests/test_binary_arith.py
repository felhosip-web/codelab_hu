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

    def test_supported_languages(self):
        expected_langs = {"Python", "C++", "C", "Java", "Pascal", "BASIC"}
        for pid in ["binary_add", "binary_sub", "binary_mul"]:
            plugin = self.loader.get_plugin(pid)
            supported = set(plugin.get_supported_languages())
            self.assertTrue(expected_langs.issubset(supported), f"{pid} missing languages: {expected_langs - supported}")
            for lang in expected_langs:
                code = plugin.get_code(lang)
                self.assertTrue(len(code) > 0, f"{pid} code for {lang} is empty")

    def test_binary_add_steps(self):
        plugin = self.loader.get_plugin("binary_add")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        final_res = final_step.extra["result"]
        self.assertEqual(final_res & 0xFF, (13 + 7) & 0xFF)
        self.assertEqual(final_res, 20)

    def test_binary_sub_steps(self):
        plugin = self.loader.get_plugin("binary_sub")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        final_res = final_step.extra["result"]
        self.assertEqual(final_res & 0xFF, (13 - 7) & 0xFF)
        self.assertEqual(final_res, 6)

    def test_binary_mul_steps(self):
        plugin = self.loader.get_plugin("binary_mul")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([13, 7]))
        self.assertTrue(len(steps) > 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        final_res = final_step.extra["result"]
        self.assertEqual(final_res, 13 * 7)
        self.assertEqual(final_res, 91)
        self.assertEqual(final_res & 0xFF, 91)


if __name__ == "__main__":
    unittest.main()
