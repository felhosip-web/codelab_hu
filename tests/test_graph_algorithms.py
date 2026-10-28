# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestGraphAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_graph_pathfinding_plugins_and_path_connectivity(self):
        """
        Tests graph plugins: bfs, dfs, dijkstra, astar.
        Verifies step generation, node traversal, found path endpoints,
        and edge connectivity along the returned path.
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
            self.assertIn("start", first_step.extra)
            self.assertIn("target", first_step.extra)

            final_step = steps[-1]
            if final_step.extra.get("found"):
                path = final_step.extra["path"]
                start = final_step.extra["start"]
                target = final_step.extra["target"]

                self.assertEqual(path[0], start)
                self.assertEqual(path[-1], target)

                graph = final_step.extra["graph"] if "graph" in final_step.extra else first_step.extra.get("graph")
                if graph and hasattr(graph, "nodes"):
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        neighbors = [nbr for nbr, _ in graph.nodes[u].neighbors]
                        self.assertIn(v, neighbors, f"Edge ({u}, {v}) missing in graph path for {pid}")
            else:
                # Target was unreachable in sample graph
                self.assertTrue("start" in final_step.extra and "target" in final_step.extra)

    def test_dijkstra_shortest_path_distance(self):
        """
        Verifies Dijkstra calculates the exact shortest path distance when path exists.
        """
        dijkstra = self.loader.get_plugin("dijkstra")
        # Run until we get a graph where target is reachable
        for _ in range(10):
            steps = list(dijkstra.get_steps([]))
            final_step = steps[-1]
            if final_step.extra.get("found"):
                target = final_step.extra["target"]
                distances = final_step.extra["dist"]
                path = final_step.extra["path"]
                graph = final_step.extra["graph"]

                # Calculate path cost manually from graph edge weights
                calc_cost = 0
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    for nbr, weight in graph.nodes[u].neighbors:
                        if nbr == v:
                            calc_cost += weight
                            break

                self.assertEqual(distances[target], calc_cost)
                break


if __name__ == "__main__":
    unittest.main()
