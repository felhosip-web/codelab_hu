# -*- coding: utf-8 -*-
import unittest
from core.version import MAIN_VERSION, Version
from core.input_parser import parse_array_input, PRESETS
from core.engine import Engine
from plugins.bubble.plugin import BubbleSortPlugin


class TestInteractiveInput(unittest.TestCase):
    def test_version_bump(self):
        self.assertGreaterEqual(MAIN_VERSION, Version(3, 6, 0))

    def test_parse_valid_inputs(self):
        arr, err = parse_array_input("5, 3, 1")
        self.assertIsNone(err)
        self.assertEqual(arr, [5, 3, 1])

        arr, err = parse_array_input("[5, 3, 8, 1, 9]")
        self.assertIsNone(err)
        self.assertEqual(arr, [5, 3, 8, 1, 9])

        arr, err = parse_array_input("5; 3; 8; 1")
        self.assertIsNone(err)
        self.assertEqual(arr, [5, 3, 8, 1])

        arr, err = parse_array_input("10 20 30")
        self.assertIsNone(err)
        self.assertEqual(arr, [10, 20, 30])

    def test_parse_invalid_inputs(self):
        arr, err = parse_array_input("")
        self.assertIsNotNone(err)
        self.assertIsNone(arr)

        arr, err = parse_array_input("   ")
        self.assertIsNotNone(err)
        self.assertIsNone(arr)

        arr, err = parse_array_input("5, abc, 3")
        self.assertIsNotNone(err)
        self.assertIsNone(arr)

    def test_parse_max_items_limit(self):
        long_str = ", ".join(map(str, range(60)))
        arr, err = parse_array_input(long_str, max_items=50)
        self.assertIsNotNone(err)
        self.assertIsNone(arr)

    def test_presets_exist(self):
        self.assertIn("Majdnem rendezett", PRESETS)
        self.assertIn("Fordított", PRESETS)
        self.assertEqual(PRESETS["Fordított"], [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_engine_generate_steps_with_custom_input(self):
        engine = Engine()
        plugin = BubbleSortPlugin()
        manual_array = [9, 2, 7, 4]
        engine.set_plugin(plugin, manual_array)
        engine.generate_steps(manual_array)

        self.assertGreater(len(engine.steps), 0)
        self.assertEqual(engine.current_array, manual_array)


if __name__ == "__main__":
    unittest.main()
