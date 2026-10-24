# -*- coding: utf-8 -*-
import unittest
import tempfile
import shutil
from pathlib import Path

from core.plugin_system import PluginLoader, AlgorithmPluginBase
from core.api_manager import APIManager


class TestPluginLoader(unittest.TestCase):
    def test_load_all_loads_sorting_and_search_multiple_classes(self):
        loader = PluginLoader()
        loader.load_all()

        plugins = loader.list_plugins()
        plugin_ids = [p.id for p in plugins]

        # Check sorting plugin is loaded
        self.assertIn("bubble_sort", plugin_ids)

        # Check search folder loads both classes: linear_search and binary_search
        self.assertIn("linear_search", plugin_ids)
        self.assertIn("binary_search", plugin_ids)

    def test_duplicate_id_skips_second_and_logs_error(self):
        temp_dir = tempfile.mkdtemp()
        try:
            plugin_folder = Path(temp_dir) / "test_dup"
            plugin_folder.mkdir()
            plugin_file = plugin_folder / "plugin.py"
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class FirstPlugin(AlgorithmPluginBase):
    id = "dup_id"
    name = "First"
    plugin_type = "general"

class SecondPlugin(AlgorithmPluginBase):
    id = "dup_id"
    name = "Second"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            loaded = loader.list_plugins()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].name, "First")

            errors = loader.get_load_errors()
            self.assertGreater(len(errors), 0)
            self.assertTrue(any("dup_id" in err for err in errors))

            first_instance = loaded[0]
            loader.plugin_features["dup_id"] = "stale_feature"
            loader.load_all()

            self.assertIsNot(loader.get_plugin("dup_id"), first_instance)
            self.assertEqual(loader.get_plugin("dup_id").name, "First")
            self.assertEqual(loader.plugin_features["dup_id"], "general")
            self.assertEqual(len(loader.list_plugins()), 1)
            self.assertEqual(len(loader.get_load_errors()), 1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_empty_id_skipped_and_logs_error(self):
        temp_dir = tempfile.mkdtemp()
        try:
            plugin_folder = Path(temp_dir) / "test_empty_id"
            plugin_folder.mkdir()
            plugin_file = plugin_folder / "plugin.py"
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class EmptyIdPlugin(AlgorithmPluginBase):
    id = ""
    name = "No ID"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            loaded = loader.list_plugins()
            self.assertEqual(len(loaded), 0)

            errors = loader.get_load_errors()
            self.assertGreater(len(errors), 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_reload_keeps_plugins_listable(self):
        loader = PluginLoader()
        loader.load_all()
        initial_count = len(loader.list_plugins())

        loaded_ids, errors = loader.reload()
        self.assertEqual(len(loader.list_plugins()), initial_count)
        self.assertIn("bubble_sort", [p.id for p in loader.list_plugins()])

    def test_feature_disable_hides_plugin(self):
        config_path = "saves/test_loader_config.json"
        api_manager = APIManager(config_path=config_path)
        try:
            loader = PluginLoader(api_manager=api_manager)
            loader.load_all()

            self.assertIsNotNone(loader.get_plugin("bubble_sort"))

            api_manager.disable_feature("sorting")
            self.assertIsNone(loader.get_plugin("bubble_sort"))
            self.assertNotIn("bubble_sort", [p.id for p in loader.list_plugins()])
        finally:
            p = Path(config_path)
            if p.exists():
                p.unlink()

    def test_list_plugins_grouped_contains_sorting(self):
        loader = PluginLoader()
        loader.load_all()

        grouped = loader.list_plugins_grouped()
        self.assertIn("sorting", grouped)
        self.assertIn("search", grouped)

        sorting_ids = [p.id for p in grouped["sorting"]]
        self.assertIn("bubble_sort", sorting_ids)


if __name__ == "__main__":
    unittest.main()
