# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestDataStructures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_fifo_lifo_plugins(self):
        """
        Tests LIFO/FIFO plugins: stack, queue, circular_queue, deque, linked_list.
        """
        pids = ["stack", "queue", "circular_queue", "deque", "linked_list"]

        for pid in pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            final_step = steps[-1]
            self.assertIn("phase", final_step.extra)
            self.assertIn(final_step.extra["phase"], ["kesz", "done"])

    def test_tree_and_structure_plugins(self):
        """
        Tests tree and structure plugins: bst, avl, rbtree, btree, hashtable, trie, traversal.
        """
        pids = ["bst", "avl", "rbtree", "btree", "hashtable", "trie", "traversal"]

        for pid in pids:
            plugin = self.loader.get_plugin(pid)
            self.assertIsNotNone(plugin, f"Plugin {pid} not found")

            steps = list(plugin.get_steps([]))
            self.assertGreater(len(steps), 0, f"No steps generated for {pid}")

            for step in steps:
                self.assertIsInstance(step, VisualizationStep)

            first_step = steps[0]
            self.assertIsInstance(first_step, VisualizationStep)


if __name__ == "__main__":
    unittest.main()
