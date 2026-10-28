# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestSearchAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_linear_search_contract(self):
        """
        Tests linear_search plugin for step generation, target searching,
        and step metric/extra invariants.
        """
        plugin = self.loader.get_plugin("linear_search")
        self.assertIsNotNone(plugin)

        # Normal non-empty array
        arr = [10, 20, 30, 40, 50]
        steps = list(plugin.get_steps(arr))
        self.assertGreater(len(steps), 0)

        first_step = steps[0]
        self.assertIsInstance(first_step, VisualizationStep)
        self.assertEqual(first_step.array, sorted(arr))
        self.assertIn("target", first_step.extra)

        final_step = steps[-1]
        self.assertIsInstance(final_step, VisualizationStep)

        # Empty array
        empty_steps = list(plugin.get_steps([]))
        self.assertGreater(len(empty_steps), 0)
        self.assertEqual(empty_steps[0].array, [])

    def test_binary_search_contract(self):
        """
        Tests binary_search plugin step generation, midpoint halving steps,
        and boundary positions.
        """
        plugin = self.loader.get_plugin("binary_search")
        self.assertIsNotNone(plugin)

        arr = [5, 12, 18, 24, 31, 45, 50]
        steps = list(plugin.get_steps(arr))
        self.assertGreater(len(steps), 0)

        for step in steps:
            self.assertIsInstance(step, VisualizationStep)
            self.assertEqual(step.array, sorted(arr))

        first_step = steps[0]
        self.assertIn("target", first_step.extra)
        self.assertIn("low", first_step.extra)
        self.assertIn("high", first_step.extra)

        # Empty array edge case
        empty_steps = list(plugin.get_steps([]))
        self.assertGreater(len(empty_steps), 0)
        self.assertEqual(empty_steps[0].array, [])


if __name__ == "__main__":
    unittest.main()
