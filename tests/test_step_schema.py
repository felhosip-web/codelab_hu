# -*- coding: utf-8 -*-
import unittest
from core.step import VisualizationStep
from core.engine import Engine
from plugins.bubble.plugin import BubbleSortPlugin
from plugins.insertion.plugin import InsertionSortPlugin
from plugins.quick.plugin import QuickSortPlugin
from plugins.search.plugin import LinearSearchPlugin, BinarySearchPlugin
from plugins.graph.plugin import BFSPlugin


class TestStepSchema(unittest.TestCase):
    def test_visualization_step_schema(self):
        step = VisualizationStep(
            explanation="Test step",
            code_line=5,
            metrics={"comparisons": 2, "swaps": 1},
            array=[1, 2, 3],
            highlight=[0, 1],
            key=2,
            sorted_end=0,
            extra={"custom": "value"}
        )

        d = step.to_dict()
        self.assertIn("code_line", d)
        self.assertIn("explanation", d)
        self.assertIn("metrics", d)
        self.assertEqual(d["code_line"], 5)
        self.assertEqual(d["explanation"], "Test step")
        self.assertEqual(d["metrics"]["comparisons"], 2)

        # Test backward compat properties
        self.assertEqual(step.comparisons, 2)
        self.assertEqual(step.swaps, 1)
        self.assertEqual(step.line, 5)
        self.assertEqual(step.highlight_indices, [0, 1])
        # Test extra attribute access via __getattr__
        self.assertEqual(step.custom, "value")

        # Test from_dict
        restored = VisualizationStep.from_dict(d)
        self.assertEqual(restored.code_line, 5)
        self.assertEqual(restored.explanation, "Test step")

    def test_bubble_sort_steps_isinstance_and_code_line(self):
        plugin = BubbleSortPlugin()
        arr = [4, 2, 5, 1]
        steps = list(plugin.get_steps(arr))

        self.assertGreater(len(steps), 0)
        has_code_line_gt_zero = False
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)
            self.assertTrue(hasattr(step, "code_line"))
            self.assertTrue(hasattr(step, "explanation"))
            if step.code_line > 0:
                has_code_line_gt_zero = True

        self.assertTrue(has_code_line_gt_zero, "Expected at least one step with code_line > 0")

    def test_insertion_sort_steps_isinstance(self):
        plugin = InsertionSortPlugin()
        arr = [3, 1, 4, 2]
        steps = list(plugin.get_steps(arr))

        self.assertGreater(len(steps), 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)
            self.assertTrue(hasattr(step, "code_line"))
            self.assertTrue(hasattr(step, "explanation"))

    def test_quick_sort_steps_isinstance(self):
        plugin = QuickSortPlugin()
        arr = [3, 1, 4, 2]
        steps = list(plugin.get_steps(arr))

        self.assertGreater(len(steps), 0)
        for step in steps:
            self.assertIsInstance(step, VisualizationStep)

    def test_engine_generate_and_next_step(self):
        engine = Engine()
        plugin = BubbleSortPlugin()
        engine.set_plugin(plugin, [3, 1, 2])
        engine.generate_steps([3, 1, 2])

        self.assertGreater(len(engine.steps), 0)
        first_step = engine.steps[0]
        self.assertIsInstance(first_step, VisualizationStep)

        next_step = engine.next_step()
        self.assertIsNotNone(next_step)
        self.assertIsInstance(next_step, VisualizationStep)


if __name__ == "__main__":
    unittest.main()
