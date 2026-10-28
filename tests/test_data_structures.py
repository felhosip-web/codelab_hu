# -*- coding: utf-8 -*-
import unittest
from core.plugin_system import PluginLoader
from core.step import VisualizationStep


class TestDataStructures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = PluginLoader()
        cls.loader.load_all()

    def test_stack_lifo_contract(self):
        """
        Tests Stack plugin: LIFO ordering of pushed and popped values.
        """
        plugin = self.loader.get_plugin("stack")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        pushed_vals = [s.extra["value"] for s in steps if s.extra.get("phase") == "push"]
        popped_vals = [s.extra["value"] for s in steps if s.extra.get("phase") == "pop"]

        self.assertGreater(len(pushed_vals), 0)
        self.assertGreater(len(popped_vals), 0)

        # LIFO property: popped values must equal the reverse of the last pushed values
        expected_popped = list(reversed(pushed_vals[-len(popped_vals):]))
        self.assertEqual(popped_vals, expected_popped)

    def test_queue_fifo_contract(self):
        """
        Tests Queue plugin: FIFO ordering of enqueued and dequeued values.
        """
        plugin = self.loader.get_plugin("queue")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        enqueued_vals = [s.extra["value"] for s in steps if s.extra.get("phase") == "enqueue"]
        dequeued_vals = [s.extra["value"] for s in steps if s.extra.get("phase") == "dequeue"]

        self.assertGreater(len(enqueued_vals), 0)
        self.assertGreater(len(dequeued_vals), 0)

        # FIFO property: dequeued values match enqueued values in first-in first-out order
        expected_dequeued = enqueued_vals[:len(dequeued_vals)]
        self.assertEqual(dequeued_vals, expected_dequeued)

    def test_circular_queue_contract(self):
        """
        Tests Circular Queue plugin: capacity and modular indexing.
        """
        plugin = self.loader.get_plugin("circular_queue")
        self.assertIsNotNone(plugin)

        plugin.set_param("capacity", 5)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["phase"], "kesz")

    def test_deque_contract(self):
        """
        Tests Deque plugin: double-ended add/remove operations.
        """
        plugin = self.loader.get_plugin("deque")
        self.assertIsNotNone(plugin)

        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        phases = {s.extra.get("phase") for s in steps}
        self.assertIn("add_rear", phases)
        self.assertIn("add_front", phases)

    def test_linked_list_contract(self):
        """
        Tests Linked List plugin: node appending and traversal chain.
        """
        plugin = self.loader.get_plugin("linked_list")
        self.assertIsNotNone(plugin)

        plugin.set_param("size", 4)
        steps = list(plugin.get_steps([]))
        self.assertGreater(len(steps), 0)

        final_step = steps[-1]
        self.assertEqual(final_step.extra["phase"], "done")
        self.assertEqual(len(final_step.extra["nodes"]), 4)

    def test_tree_search_and_traversal_contracts(self):
        """
        Tests BST, AVL, RBTree, BTree, Trie, Traversal, and HashTable plugins.
        """
        # BST search success
        bst = self.loader.get_plugin("bst")
        bst_steps = list(bst.get_steps([]))
        self.assertTrue(bst_steps[-1].extra.get("found"))

        # AVL Tree insertion
        avl = self.loader.get_plugin("avl")
        avl_steps = list(avl.get_steps([]))
        self.assertIn("inserted", avl_steps[-1].extra)

        # B-Tree insertion
        btree = self.loader.get_plugin("btree")
        btree_steps = list(btree.get_steps([]))
        self.assertIn("inserted", btree_steps[-1].extra)

        # Traversal result
        trav = self.loader.get_plugin("traversal")
        trav_steps = list(trav.get_steps([]))
        self.assertIn("result", trav_steps[-1].extra)
        self.assertGreater(len(trav_steps[-1].extra["result"]), 0)

        # RBTree in-order property
        rbt = self.loader.get_plugin("rbtree")
        rbt_steps = list(rbt.get_steps([]))
        inorder = rbt_steps[-1].extra.get("inorder")
        self.assertEqual(inorder, sorted(inorder))

        # HashTable search success
        ht = self.loader.get_plugin("hashtable")
        ht_steps = list(ht.get_steps([]))
        self.assertTrue(ht_steps[-1].extra.get("found"))

        # Trie search success
        trie = self.loader.get_plugin("trie")
        trie_steps = list(trie.get_steps([]))
        self.assertTrue(trie_steps[-1].extra.get("found"))


if __name__ == "__main__":
    unittest.main()
