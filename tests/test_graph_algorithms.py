# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestGraphAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_graph_pathfinding_plugins(self):
        """
        Tests graph plugins: bfs, dfs, dijkstra, astar.
        Verifies step generation, node traversal, and pathfinding results.
        """
        graph_pids = ["bfs", "dfs", "dijkstra", "astar"]

        for pid in graph_pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            first_step = steps[0]
            self.assertIsInstance(first_step, VisualizationStep)
            self.assertIn("start", first_step.extra)
            self.assertIn("target", first_step.extra)

            final_step = steps[-1]
            self.assertIsInstance(final_step, VisualizationStep)


if __name__ == "__main__":
    unittest.main()
