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
        Verifies non-empty memory structures, matrix dimensions, and pointer mappings.
        """
        # Array basics
        basics = self.loader.get_plugin("array_basics")
        basics_steps = list(basics.get_steps([]))
        self.assertEqual(basics_steps[-1].extra["phase"], "kesz")
        self.assertGreater(len(basics_steps[-1].extra["array"]), 0)

        # Array in array
        jagged = self.loader.get_plugin("array_in_array")
        jagged_steps = list(jagged.get_steps([]))
        self.assertEqual(jagged_steps[-1].extra["phase"], "kesz")
        self.assertEqual(len(jagged_steps[-1].extra["jagged"]), 3)

        # Array 2D
        arr2d = self.loader.get_plugin("array_2d")
        arr2d_steps = list(arr2d.get_steps([]))
        self.assertEqual(arr2d_steps[-1].extra["phase"], "kesz")
        self.assertEqual(len(arr2d_steps[-1].extra["matrix"]), 3)

        # Pointer
        ptr = self.loader.get_plugin("pointer")
        ptr_steps = list(ptr.get_steps([]))
        self.assertEqual(ptr_steps[-1].extra["phase"], "kesz")
        self.assertIn("pointers", ptr_steps[-1].extra)
        self.assertIn("memory", ptr_steps[-1].extra)

    def test_program_structure_plugins(self):
        """
        Tests program structure plugins: for_loop, while_loop, if_else, variables, function_def.
        Verifies exact variable state values and final results.
        """
        # For loop
        for_loop = self.loader.get_plugin("for_loop")
        for_steps = list(for_loop.get_steps([]))
        self.assertEqual(for_steps[-1].extra["phase"], "done")
        self.assertEqual(for_steps[-1].extra["n"], 5)

        # While loop
        while_loop = self.loader.get_plugin("while_loop")
        while_steps = list(while_loop.get_steps([]))
        self.assertEqual(while_steps[-1].extra["phase"], "done")
        self.assertEqual(while_steps[-1].extra["i"], 5)

        # If else
        if_else = self.loader.get_plugin("if_else")
        if_steps = list(if_else.get_steps([]))
        self.assertEqual(if_steps[-1].extra["phase"], "done")
        self.assertEqual(if_steps[-1].extra["result"], "Közepes")

        # Variables
        variables = self.loader.get_plugin("variables")
        var_steps = list(variables.get_steps([]))
        self.assertEqual(var_steps[-1].extra["phase"], "done")
        var_dict = var_steps[-1].extra["variables"]
        self.assertEqual(var_dict["age"], 25)
        self.assertEqual(var_dict["name"], "Péter")

        # Function def
        func_def = self.loader.get_plugin("function_def")
        func_steps = list(func_def.get_steps([]))
        self.assertEqual(func_steps[-1].extra["phase"], "done")
        self.assertEqual(func_steps[-1].extra["result"], 8)


if __name__ == "__main__":
    unittest.main()
