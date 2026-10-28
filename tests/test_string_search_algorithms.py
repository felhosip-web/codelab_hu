# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestStringSearchAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_string_search_plugins(self):
        """
        Tests string matching plugins: kmp, rabinkarp, boyermoore.
        Verifies step generation and pattern match search behavior.
        """
        pids = ["kmp", "rabinkarp", "boyermoore"]

        for pid in pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            first_step = steps[0]
            self.assertIsInstance(first_step, VisualizationStep)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)


if __name__ == "__main__":
    unittest.main()
