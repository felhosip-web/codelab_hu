# -*- coding: utf-8 -*-
import unittest
import random
import heapq
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

            random.seed(42)
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

    def test_dijkstra_shortest_path_distance_against_reference(self):
        """
        Verifies Dijkstra calculates the exact shortest path distance on a deterministic graph
        and compares the result against an independent reference shortest-path algorithm.
        """
        dijkstra = self.loader.get_plugin("dijkstra")
        random.seed(42)
        steps = list(dijkstra.get_steps([]))
        final_step = steps[-1]

        self.assertTrue(final_step.extra.get("found"), "Dijkstra failed to find path in deterministic graph")

        start = final_step.extra["start"]
        target = final_step.extra["target"]
        distances = final_step.extra["dist"]
        path = final_step.extra["path"]
        graph = final_step.extra["graph"]

        # Calculate path cost manually along the reported path, failing if edge is missing
        calc_cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            found_edge = False
            for nbr, weight in graph.nodes[u].neighbors:
                if nbr == v:
                    calc_cost += weight
                    found_edge = True
                    break
            self.assertTrue(found_edge, f"Path contains invalid edge ({u}, {v}) not in graph")

        self.assertEqual(distances[target], calc_cost)

        # Compute independent reference shortest path on graph.nodes
        ref_dist = {node_id: float('inf') for node_id in graph.nodes}
        ref_dist[start] = 0
        pq = [(0, start)]
        ref_visited = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in ref_visited:
                continue
            ref_visited.add(u)
            for v, w in graph.nodes[u].neighbors:
                if ref_dist[u] + w < ref_dist[v]:
                    ref_dist[v] = ref_dist[u] + w
                    heapq.heappush(pq, (ref_dist[v], v))

        expected_shortest_dist = ref_dist[target]
        self.assertEqual(distances[target], expected_shortest_dist)
        self.assertEqual(calc_cost, expected_shortest_dist)
        self.assertEqual(expected_shortest_dist, 19)


if __name__ == "__main__":
    unittest.main()
