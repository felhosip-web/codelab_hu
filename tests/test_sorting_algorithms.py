# -*- coding: utf-8 -*-
import unittest
import random
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestSortingAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_in_place_sorting_plugins_correctness(self):
        """
        Tests bubble_sort, insertion_sort, selection_sort, quick_sort, merge_sort
        across various input edge cases (empty, single element, sorted, reverse, duplicates, negatives).
        """
        sorting_pids = [
            "bubble_sort",
            "insertion_sort",
            "selection_sort",
            "quick_sort",
            "merge_sort",
        ]

        test_cases = [
            ("normal_mixed", [9, 1, 5, 3, 7, 2, 8, 4, 6]),
            ("empty", []),
            ("single_element", [42]),
            ("already_sorted", [1, 2, 3, 4, 5]),
            ("reverse_sorted", [5, 4, 3, 2, 1]),
            ("duplicates", [3, 1, 3, 2, 1]),
            ("negative_numbers", [-5, 3, 0, -2, 8]),
        ]

        for pid in sorting_pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            for name, arr in test_cases:
                with self.subTest(plugin=pid, test_case=name):
                    input_copy = list(arr)
                    steps = list(plugin.get_steps(input_copy))

                    self.assertGreater(len(steps), 0, f"No steps generated for {pid} on {name}")

                    for step in steps:
                        self.assertIsInstance(step, VisualizationStep)

                    final_step = steps[-1]
                    expected_sorted = sorted(arr)
                    self.assertEqual(
                        final_step.array, expected_sorted,
                        f"{pid} failed to sort {arr}: got {final_step.array}, expected {expected_sorted}"
                    )
                    # Verify multiset equality / element preservation
                    self.assertEqual(sorted(final_step.array), expected_sorted)

    def test_counting_sort_contract(self):
        """
        Tests counting_sort algorithm step generation, count buckets,
        and exact deterministic sorted array against known expected output.
        """
        plugin = self.loader.get_plugin("counting_sort")
        self.assertIsNotNone(plugin)

        size = 8
        max_val = 5
        plugin.set_param("size", size)
        plugin.set_param("max_val", max_val)

        # Seed random generator for deterministic internal array generation
        random.seed(42)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["phase"], "done")

        sorted_res = final_step.extra["sorted"]
        count_buckets = final_step.extra["count"]

        # Assert exact expected sorted result against seeded random array [5, 0, 1, 1, 2, 5, 1, 0]
        expected_sorted = [0, 0, 1, 1, 1, 2, 5, 5]
        expected_count = [2, 3, 1, 0, 0, 2]

        self.assertEqual(sorted_res, expected_sorted)
        self.assertEqual(count_buckets, expected_count)
        self.assertEqual(len(sorted_res), size)
        self.assertEqual(sum(count_buckets), size)


if __name__ == "__main__":
    unittest.main()
