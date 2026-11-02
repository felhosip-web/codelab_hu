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

    def test_targeted_reload_by_plugin_id_isolates_unrelated_plugins(self):
        loader = PluginLoader()
        loader.load_all()

        bubble_old = loader.get_plugin("bubble_sort")
        linear_old = loader.get_plugin("linear_search")
        binary_old = loader.get_plugin("binary_search")

        # Mutate internal state on linear_search to ensure it is preserved
        linear_old._custom_test_marker = "preserved_state"

        loaded_ids, errors = loader.reload(target="bubble_sort")
        self.assertEqual(len(errors), 0)

        bubble_new = loader.get_plugin("bubble_sort")
        linear_new = loader.get_plugin("linear_search")
        binary_new = loader.get_plugin("binary_search")

        # Target plugin is re-instantiated
        self.assertIsNot(bubble_old, bubble_new)
        self.assertEqual(bubble_new.id, "bubble_sort")

        # Unrelated plugins are identical object instances ('is') and state preserved
        self.assertIs(linear_old, linear_new)
        self.assertIs(binary_old, binary_new)
        self.assertEqual(getattr(linear_new, "_custom_test_marker", None), "preserved_state")

    def test_targeted_reload_by_feature_category_reloads_only_category(self):
        loader = PluginLoader()
        loader.load_all()

        # "search" category contains "linear_search" and "binary_search"
        linear_old = loader.get_plugin("linear_search")
        binary_old = loader.get_plugin("binary_search")
        bubble_old = loader.get_plugin("bubble_sort")

        loaded_ids, errors = loader.reload(target="search")
        self.assertEqual(len(errors), 0)

        linear_new = loader.get_plugin("linear_search")
        binary_new = loader.get_plugin("binary_search")
        bubble_new = loader.get_plugin("bubble_sort")

        # Category plugins are re-instantiated
        self.assertIsNot(linear_old, linear_new)
        self.assertIsNot(binary_old, binary_new)

        # Unrelated plugin outside category is completely untouched
        self.assertIs(bubble_old, bubble_new)

    def test_targeted_reload_does_not_reexecute_unrelated_module_code(self):
        temp_dir = tempfile.mkdtemp()
        try:
            folder1 = Path(temp_dir) / "mod1"
            folder1.mkdir()
            (folder1 / "plugin.py").write_text(
                """
import sys
from core.plugin_system import AlgorithmPluginBase

if not hasattr(sys, '_test_mod1_exec_count'):
    sys._test_mod1_exec_count = 0
sys._test_mod1_exec_count += 1

class Plugin1(AlgorithmPluginBase):
    id = "plugin_1"
    name = "Plugin 1"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            folder2 = Path(temp_dir) / "mod2"
            folder2.mkdir()
            (folder2 / "plugin.py").write_text(
                """
import sys
from core.plugin_system import AlgorithmPluginBase

if not hasattr(sys, '_test_mod2_exec_count'):
    sys._test_mod2_exec_count = 0
sys._test_mod2_exec_count += 1

class Plugin2(AlgorithmPluginBase):
    id = "plugin_2"
    name = "Plugin 2"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            import sys
            self.assertEqual(sys._test_mod1_exec_count, 1)
            self.assertEqual(sys._test_mod2_exec_count, 1)

            # Reload plugin_1 only
            loader.reload(target="plugin_1")

            self.assertEqual(sys._test_mod1_exec_count, 2)
            # Unrelated mod2 code MUST NOT have been re-executed
            self.assertEqual(sys._test_mod2_exec_count, 1)
        finally:
            if hasattr(sys, '_test_mod1_exec_count'):
                del sys._test_mod1_exec_count
            if hasattr(sys, '_test_mod2_exec_count'):
                del sys._test_mod2_exec_count
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_targeted_reload_missing_target_is_deterministic(self):
        loader = PluginLoader()
        loader.load_all()

        initial_plugins = dict(loader.plugins)
        loaded_ids, errors = loader.reload(target="non_existent_target_xyz")

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(loaded_ids), len(initial_plugins))
        for pid, plugin_obj in initial_plugins.items():
            self.assertIs(loader.get_plugin(pid), plugin_obj)

    def test_targeted_reload_failed_target_retains_unrelated_plugins(self):
        temp_dir = tempfile.mkdtemp()
        try:
            folder_good = Path(temp_dir) / "good"
            folder_good.mkdir()
            (folder_good / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class GoodPlugin(AlgorithmPluginBase):
    id = "good_plugin"
    name = "Good"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            folder_target = Path(temp_dir) / "target_mod"
            folder_target.mkdir()
            target_file = folder_target / "plugin.py"
            target_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class TargetPlugin(AlgorithmPluginBase):
    id = "target_plugin"
    name = "Target"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            good_instance = loader.get_plugin("good_plugin")
            self.assertIsNotNone(good_instance)

            # Break target_file with syntax error
            target_file.write_text("def broken_syntax(:\n", encoding="utf-8")

            loaded_ids, errors = loader.reload(target="target_plugin")

            self.assertGreater(len(errors), 0)
            # Unrelated plugin remains loaded and identical
            self.assertIs(loader.get_plugin("good_plugin"), good_instance)
            # Target plugin was not successfully loaded
            self.assertIsNone(loader.get_plugin("target_plugin"))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

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
