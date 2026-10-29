# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestStringSearchAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_kmp_search_contract(self):
        plugin = self.loader.get_plugin("kmp")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([]))
        final_step = steps[-1]
        self.assertIn("found_positions", final_step.extra)
        self.assertEqual(final_step.extra["found_positions"], [10])
        self.assertIn("lps", final_step.extra)

    def test_rabinkarp_search_contract(self):
        plugin = self.loader.get_plugin("rabinkarp")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([]))
        final_step = steps[-1]
        self.assertIn("found_positions", final_step.extra)
        self.assertEqual(final_step.extra["found_positions"], [10])

    def test_boyermoore_search_contract(self):
        plugin = self.loader.get_plugin("boyermoore")
        self.assertIsNotNone(plugin)

        # Present pattern
        plugin.set_param("pattern", "ABABAA")
        steps = list(plugin.get_steps([]))
        final_step = steps[-1]
        self.assertIn("found", final_step.extra)
        self.assertEqual(final_step.extra["found"], [4, 10])

        # Absent pattern
        plugin.set_param("pattern", "XYZ")
        absent_steps = list(plugin.get_steps([]))
        self.assertEqual(absent_steps[-1].extra["found"], [])


if __name__ == "__main__":
    unittest.main()
