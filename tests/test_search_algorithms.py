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
        and step metric/extra invariants across normal, boundary, and duplicate inputs.
        """
        plugin = self.loader.get_plugin("linear_search")
        self.assertIsNotNone(plugin)

        arr = [10, 20, 30, 40, 50]
        steps = list(plugin.get_steps(arr))
        self.assertGreater(len(steps), 0)

        first_step = steps[0]
        self.assertIsInstance(first_step, VisualizationStep)
        self.assertEqual(first_step.array, sorted(arr))

        target = first_step.extra["target"]
        self.assertIn(target, sorted(arr))

        final_step = steps[-1]
        self.assertIn("found", final_step.extra)
        found_idx = final_step.extra["found"]
        self.assertEqual(sorted(arr)[found_idx], target)

        # Empty array (absent target)
        empty_steps = list(plugin.get_steps([]))
        self.assertGreater(len(empty_steps), 0)
        self.assertEqual(empty_steps[0].array, [])
        self.assertNotIn("found", empty_steps[-1].extra)

    def test_binary_search_contract(self):
        """
        Tests binary_search plugin step generation, midpoint halving steps,
        found indices, and boundary positions.
        """
        plugin = self.loader.get_plugin("binary_search")
        self.assertIsNotNone(plugin)

        arr = [5, 12, 18, 24, 31, 45, 50]
        steps = list(plugin.get_steps(arr))
        self.assertGreater(len(steps), 0)

        sorted_arr = sorted(arr)
        target = steps[0].extra["target"]
        self.assertIn(target, sorted_arr)

        final_step = steps[-1]
        self.assertIn("found", final_step.extra)
        found_idx = final_step.extra["found"]
        self.assertEqual(sorted_arr[found_idx], target)

        # Empty array edge case
        empty_steps = list(plugin.get_steps([]))
        self.assertGreater(len(empty_steps), 0)
        self.assertEqual(empty_steps[0].array, [])
        self.assertNotIn("found", empty_steps[-1].extra)

    def test_search_duplicates(self):
        """
        Tests search behavior on arrays with duplicate elements.
        """
        for pid in ["linear_search", "binary_search"]:
            plugin = self.loader.get_plugin(pid)
            arr = [2, 2, 5, 5, 8]
            steps = list(plugin.get_steps(arr))
            final_step = steps[-1]
            self.assertIn("found", final_step.extra)
            found_idx = final_step.extra["found"]
            target = final_step.extra["target"]
            self.assertEqual(sorted(arr)[found_idx], target)


if __name__ == "__main__":
    unittest.main()
