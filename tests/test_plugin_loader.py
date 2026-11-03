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



    def test_reload_folder_with_multiple_classes_preserves_sibling_when_later_class_fails(self):
        """P0: When a later plugin class in a folder fails during reload, previously registered sibling plugins remain accessible and retain identity."""
        temp_dir = tempfile.mkdtemp()
        try:
            folder = Path(temp_dir) / "multi_mod"
            folder.mkdir()
            plugin_file = folder / "plugin.py"
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class SiblingWorkingPlugin(AlgorithmPluginBase):
    id = "sibling_working"
    name = "Sibling Working"
    plugin_type = "general"

class SecondWorkingPlugin(AlgorithmPluginBase):
    id = "second_working"
    name = "Second Working"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            sibling_before = loader.get_plugin("sibling_working")
            second_before = loader.get_plugin("second_working")
            self.assertIsNotNone(sibling_before)
            self.assertIsNotNone(second_before)
            sibling_before._custom_sibling_state = "sibling_state_intact"

            # Modify plugin.py so SiblingWorkingPlugin is still valid, but SecondWorkingPlugin raises during instantiation
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class SiblingWorkingPlugin(AlgorithmPluginBase):
    id = "sibling_working"
    name = "Sibling Working"
    plugin_type = "general"

class SecondWorkingPlugin(AlgorithmPluginBase):
    id = "second_working"
    name = "Second Working"
    plugin_type = "general"
    def __init__(self):
        super().__init__()
        raise RuntimeError("Instantiation error in second plugin")
""",
                encoding="utf-8"
            )

            loaded_ids, errors = loader.reload(target="second_working")
            self.assertGreater(len(errors), 0)

            # Sibling working plugin remains accessible and retains its original object identity
            sibling_after = loader.get_plugin("sibling_working")
            self.assertIs(sibling_after, sibling_before)
            self.assertEqual(getattr(sibling_after, "_custom_sibling_state", None), "sibling_state_intact")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_reload_missing_target_preserves_existing_errors_and_plugins(self):
        """P1: When reload is called with a nonexistent target, existing load errors and registrations are not cleared."""
        temp_dir = tempfile.mkdtemp()
        try:
            broken_folder = Path(temp_dir) / "broken_folder"
            broken_folder.mkdir()
            (broken_folder / "plugin.py").write_text("def broken_code(:\n", encoding="utf-8")

            good_folder = Path(temp_dir) / "good_folder"
            good_folder.mkdir()
            (good_folder / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class GoodPlugin(AlgorithmPluginBase):
    id = "good_id"
    name = "Good"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            initial_errors = list(loader.get_load_errors())
            self.assertGreater(len(initial_errors), 0)
            good_instance = loader.get_plugin("good_id")
            self.assertIsNotNone(good_instance)

            # Call reload with nonexistent target
            loaded_ids, errors = loader.reload(target="nonexistent_target_abc")

            # Existing errors must be preserved, NOT cleared or lost
            self.assertEqual(errors, initial_errors)
            self.assertEqual(loader.get_load_errors(), initial_errors)
            self.assertIs(loader.get_plugin("good_id"), good_instance)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_same_folder_plugin_id_targeting_with_different_features(self):
        """P1: Targeting a single plugin in a multi-plugin folder with different features updates target, preserves sibling instance and state, and leaves other folders unaffected."""
        temp_dir = tempfile.mkdtemp()
        try:
            same_dir = Path(temp_dir) / "multi_feature_folder"
            same_dir.mkdir()
            (same_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class FirstPlugin(AlgorithmPluginBase):
    id = "plugin_first"
    name = "First"
    plugin_type = "feature_alpha"

class SecondPlugin(AlgorithmPluginBase):
    id = "plugin_second"
    name = "Second"
    plugin_type = "feature_beta"
""",
                encoding="utf-8"
            )

            other_dir = Path(temp_dir) / "other_folder"
            other_dir.mkdir()
            (other_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class OtherPlugin(AlgorithmPluginBase):
    id = "plugin_other"
    name = "Other"
    plugin_type = "feature_gamma"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            first_old = loader.get_plugin("plugin_first")
            second_old = loader.get_plugin("plugin_second")
            other_old = loader.get_plugin("plugin_other")

            self.assertEqual(loader.plugin_features.get("plugin_first"), "feature_alpha")
            self.assertEqual(loader.plugin_features.get("plugin_second"), "feature_beta")
            second_old._custom_state = "second_intact"
            other_old._custom_state = "other_intact"

            # Reload specifically plugin_first
            loaded_ids, errors = loader.reload(target="plugin_first")
            self.assertEqual(len(errors), 0)

            first_new = loader.get_plugin("plugin_first")
            second_new = loader.get_plugin("plugin_second")
            other_new = loader.get_plugin("plugin_other")

            # Targeted plugin is replaced
            self.assertIsNot(first_old, first_new)
            self.assertEqual(first_new.id, "plugin_first")

            # Sibling plugin in the same folder remains identical instance (is) and state preserved
            self.assertIs(second_old, second_new)
            self.assertEqual(getattr(second_new, "_custom_state", None), "second_intact")

            # Other folder plugin is completely unaffected
            self.assertIs(other_old, other_new)
            self.assertEqual(getattr(other_new, "_custom_state", None), "other_intact")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


    def test_failed_reload_restores_sys_modules_and_registry(self):
        """Verify that failed module replacement restores exact previous sys.modules object identity ('is') and preserves previous working plugin instances."""
        import sys
        temp_dir = tempfile.mkdtemp()
        try:
            folder = Path(temp_dir) / "mod_rollback_test"
            folder.mkdir()
            plugin_file = folder / "plugin.py"
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class RollbackSiblingPlugin(AlgorithmPluginBase):
    id = "rollback_sibling"
    name = "Rollback Sibling"
    plugin_type = "general"

class RollbackTargetPlugin(AlgorithmPluginBase):
    id = "rollback_target"
    name = "Rollback Target"
    plugin_type = "general"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            mod_name = "plugins.mod_rollback_test.plugin"
            self.assertIn(mod_name, sys.modules)
            old_mod_obj = sys.modules[mod_name]
            sibling_old = loader.get_plugin("rollback_sibling")
            target_old = loader.get_plugin("rollback_target")
            self.assertIsNotNone(sibling_old)
            self.assertIsNotNone(target_old)

            sibling_old._custom_state = "sibling_state_intact"

            # 1. Break plugin.py with syntax error (module execution / spec load failure)
            plugin_file.write_text("def broken_code_syntax(:\n", encoding="utf-8")

            loaded_ids, errors = loader.reload(target="rollback_target")
            self.assertGreater(len(errors), 0)

            # Check that sys.modules has restored the EXACT old module object
            self.assertIn(mod_name, sys.modules)
            self.assertIs(sys.modules[mod_name], old_mod_obj)

            # Check that sibling plugin remains accessible and intact
            sibling_after = loader.get_plugin("rollback_sibling")
            self.assertIs(sibling_after, sibling_old)
            self.assertEqual(getattr(sibling_after, "_custom_state", None), "sibling_state_intact")

            # 2. Test failure during plugin instantiation/validation (runtime exception in class)
            plugin_file.write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class RollbackSiblingPlugin(AlgorithmPluginBase):
    id = "rollback_sibling"
    name = "Rollback Sibling"
    plugin_type = "general"

class RollbackTargetPlugin(AlgorithmPluginBase):
    id = "rollback_target"
    name = "Rollback Target"
    plugin_type = "general"
    def __init__(self):
        super().__init__()
        raise RuntimeError("Validation / initialization error in target plugin")
""",
                encoding="utf-8"
            )

            loaded_ids, errors = loader.reload(target="rollback_target")
            self.assertGreater(len(errors), 0)

            # sys.modules MUST still be restored to old_mod_obj
            self.assertIn(mod_name, sys.modules)
            self.assertIs(sys.modules[mod_name], old_mod_obj)

            # Sibling plugin remains accessible and identical
            sibling_after2 = loader.get_plugin("rollback_sibling")
            self.assertIs(sibling_after2, sibling_old)
            self.assertEqual(getattr(sibling_after2, "_custom_state", None), "sibling_state_intact")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
