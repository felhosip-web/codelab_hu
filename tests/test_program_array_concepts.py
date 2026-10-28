# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestProgramArrayConcepts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_array_concepts_plugins(self):
        """
        Tests array concept plugins: array_basics, array_in_array, array_2d, pointer.
        """
        pids = ["array_basics", "array_in_array", "array_2d", "pointer"]

        for pid in pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([1, 2, 3]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)

    def test_program_structure_plugins(self):
        """
        Tests program structure plugins: for_loop, while_loop, if_else, variables, function_def.
        """
        pids = ["for_loop", "while_loop", "if_else", "variables", "function_def"]

        for pid in pids:
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
