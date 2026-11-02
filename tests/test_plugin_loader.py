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

    def test_targeted_reload_by_plugin_id_preserves_unrelated_instances(self):
        loader = PluginLoader()
        loader.load_all()

        bubble_before = loader.get_plugin("bubble_sort")
        linear_before = loader.get_plugin("linear_search")
        binary_before = loader.get_plugin("binary_search")
        insertion_before = loader.get_plugin("insertion_sort")

        # Mutate internal state on both unrelated and co-located plugins to verify state retention
        bubble_before.custom_state_tag = "preserved_bubble_state"
        linear_before.custom_co_located_tag = "preserved_linear_state"

        # Targeted reload for binary_search (shares module/folder with linear_search)
        loaded_ids, errors = loader.reload("binary_search")
        self.assertEqual(errors, [])

        bubble_after = loader.get_plugin("bubble_sort")
        insertion_after = loader.get_plugin("insertion_sort")
        linear_after = loader.get_plugin("linear_search")
        binary_after = loader.get_plugin("binary_search")

        # Unrelated plugins in different folders MUST be identical instances ('is') and retain state
        self.assertIs(bubble_after, bubble_before)
        self.assertEqual(getattr(bubble_after, "custom_state_tag", None), "preserved_bubble_state")
        self.assertIs(insertion_after, insertion_before)

        # Only the targeted plugin ID is reloaded; co-located plugin in the same folder is preserved
        self.assertIsNot(binary_after, binary_before)
        self.assertEqual(binary_after.id, "binary_search")
        self.assertIs(linear_after, linear_before)
        self.assertEqual(getattr(linear_after, "custom_co_located_tag", None), "preserved_linear_state")

    def test_targeted_reload_by_folder_name_reloads_all_in_folder(self):
        loader = PluginLoader()
        loader.load_all()

        bubble_before = loader.get_plugin("bubble_sort")
        linear_before = loader.get_plugin("linear_search")
        binary_before = loader.get_plugin("binary_search")

        # Targeted reload by folder name "search"
        loaded_ids, errors = loader.reload("search")
        self.assertEqual(errors, [])

        bubble_after = loader.get_plugin("bubble_sort")
        linear_after = loader.get_plugin("linear_search")
        binary_after = loader.get_plugin("binary_search")

        self.assertIs(bubble_after, bubble_before)
        self.assertIsNot(linear_after, linear_before)
        self.assertIsNot(binary_after, binary_before)

    def test_multi_plugin_folder_with_different_features_isolation(self):
        loader = PluginLoader()
        loader.load_all()

        btree_before = loader.get_plugin("btree")            # feature: tree
        boyer_before = loader.get_plugin("boyermoore")        # feature: string
        trie_before = loader.get_plugin("trie")              # feature: tree

        boyer_before.custom_tag = "string_tag"
        btree_before.custom_tag = "tree_tag"

        # Reload feature "string" -> should reload boyermoore but preserve btree and trie
        loaded_ids, errors = loader.reload("string")
        self.assertEqual(errors, [])

        btree_after = loader.get_plugin("btree")
        boyer_after = loader.get_plugin("boyermoore")
        trie_after = loader.get_plugin("trie")

        self.assertIsNot(boyer_after, boyer_before)
        self.assertIs(btree_after, btree_before)
        self.assertEqual(getattr(btree_after, "custom_tag", None), "tree_tag")
        self.assertIs(trie_after, trie_before)

    def test_targeted_reload_by_feature_preserves_unrelated_instances(self):
        loader = PluginLoader()
        loader.load_all()

        bubble_before = loader.get_plugin("bubble_sort")
        binary_before = loader.get_plugin("binary_search")
        linear_before = loader.get_plugin("linear_search")

        # Unrelated state
        bubble_before.custom_state_tag = "bubble_ok"

        # Targeted reload for feature/category "search"
        loaded_ids, errors = loader.reload("search")
        self.assertEqual(errors, [])

        bubble_after = loader.get_plugin("bubble_sort")
        binary_after = loader.get_plugin("binary_search")
        linear_after = loader.get_plugin("linear_search")

        # Sorting plugin untouched
        self.assertIs(bubble_after, bubble_before)
        self.assertEqual(bubble_after.custom_state_tag, "bubble_ok")

        # Search plugins reloaded
        self.assertIsNot(binary_after, binary_before)
        self.assertIsNot(linear_after, linear_before)
        self.assertEqual(binary_after.id, "binary_search")
        self.assertEqual(linear_after.id, "linear_search")

    def test_targeted_reload_does_not_reexecute_unrelated_module(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p1_dir = Path(temp_dir) / "p_one"
            p1_dir.mkdir()
            (p1_dir / "plugin.py").write_text(
                """
import sys
from core.plugin_system import AlgorithmPluginBase

exec_count = getattr(sys, '_test_exec_count_p1', 0) + 1
setattr(sys, '_test_exec_count_p1', exec_count)

class PluginOne(AlgorithmPluginBase):
    id = "p1_id"
    name = "Plugin 1"
    plugin_type = "cat_one"
""",
                encoding="utf-8"
            )

            p2_dir = Path(temp_dir) / "p_two"
            p2_dir.mkdir()
            (p2_dir / "plugin.py").write_text(
                """
import sys
from core.plugin_system import AlgorithmPluginBase

exec_count = getattr(sys, '_test_exec_count_p2', 0) + 1
setattr(sys, '_test_exec_count_p2', exec_count)

class PluginTwo(AlgorithmPluginBase):
    id = "p2_id"
    name = "Plugin 2"
    plugin_type = "cat_two"
""",
                encoding="utf-8"
            )

            import sys
            sys._test_exec_count_p1 = 0
            sys._test_exec_count_p2 = 0

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            self.assertEqual(sys._test_exec_count_p1, 1)
            self.assertEqual(sys._test_exec_count_p2, 1)

            p1_inst = loader.get_plugin("p1_id")
            p2_inst = loader.get_plugin("p2_id")

            # Targeted reload of p2_id only
            loader.reload("p2_id")

            # p1 module MUST NOT have re-executed
            self.assertEqual(sys._test_exec_count_p1, 1)
            # p2 module MUST have re-executed
            self.assertEqual(sys._test_exec_count_p2, 2)

            self.assertIs(loader.get_plugin("p1_id"), p1_inst)
            self.assertIsNot(loader.get_plugin("p2_id"), p2_inst)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            if hasattr(sys, "_test_exec_count_p1"):
                del sys._test_exec_count_p1
            if hasattr(sys, "_test_exec_count_p2"):
                del sys._test_exec_count_p2

    def test_missing_target_and_failed_target_reload_behavior(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p1_dir = Path(temp_dir) / "p_good"
            p1_dir.mkdir()
            (p1_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class GoodPlugin(AlgorithmPluginBase):
    id = "good_id"
    name = "Good"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            good_inst = loader.get_plugin("good_id")
            self.assertIsNotNone(good_inst)

            # Missing target: handles deterministically, does not corrupt registry
            loaded_ids, errors = loader.reload("non_existent_target")
            self.assertIn("good_id", loaded_ids)
            self.assertIs(loader.get_plugin("good_id"), good_inst)
            self.assertTrue(any("non_existent_target" in e for e in errors))

            # Introduce syntax error in target module
            (p1_dir / "plugin.py").write_text(
                "invalid python code !!! syntax error",
                encoding="utf-8"
            )

            loaded_ids, errors = loader.reload("good_id")
            # Target load failed: reported in errors deterministically
            self.assertTrue(len(errors) > 0)
            self.assertNotIn("good_id", loaded_ids)
            self.assertIsNone(loader.get_plugin("good_id"))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_targeted_reload_enforces_duplicate_id_and_api_checks(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # p_fixed folder
            pf_dir = Path(temp_dir) / "p_fixed"
            pf_dir.mkdir()
            (pf_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class FixedPlugin(AlgorithmPluginBase):
    id = "existing_id"
    name = "Fixed"
""",
                encoding="utf-8"
            )

            # p_target folder
            pt_dir = Path(temp_dir) / "p_target"
            pt_dir.mkdir()
            (pt_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class TargetPlugin(AlgorithmPluginBase):
    id = "target_id"
    name = "Target"
""",
                encoding="utf-8"
            )

            loader = PluginLoader(plugins_dir=temp_dir)
            loader.load_all()

            fixed_inst = loader.get_plugin("existing_id")
            self.assertIsNotNone(fixed_inst)

            # Modify p_target so it attempts to hijack existing_id
            (pt_dir / "plugin.py").write_text(
                """
from core.plugin_system import AlgorithmPluginBase

class TargetPluginHijack(AlgorithmPluginBase):
    id = "existing_id"
    name = "Hijack"
""",
                encoding="utf-8"
            )

            loaded_ids, errors = loader.reload("target_id")
            # Duplicate conflict detected and logged
            self.assertTrue(any("existing_id" in e for e in errors))
            # Existing plugin remains intact and unchanged
            self.assertIs(loader.get_plugin("existing_id"), fixed_inst)
            self.assertEqual(loader.get_plugin("existing_id").name, "Fixed")
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
