# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from core.api_manager import APIManager
from core.plugin_system import PluginLoader
from core.engine import Engine
from core.version import API_MANAGER_VERSION

class TestAPIManagerIntegration(unittest.TestCase):
    def test_version_constants(self):
        self.assertEqual(self.api_manager.config.current_version, str(API_MANAGER_VERSION))

    def setUp(self):
        self.api_manager = APIManager("saves/test_api_config.json")

    def tearDown(self):
        p = Path("saves/test_api_config.json")
        if p.exists():
            p.unlink()

    def test_feature_flag_hides_plugins(self):
        loader = PluginLoader(api_manager=self.api_manager)
        loader.load_all()

        all_plugins = loader.list_plugins()
        self.assertGreater(len(all_plugins), 0)

        # Disable sorting feature
        self.api_manager.disable_feature("sorting")
        filtered_plugins = loader.list_plugins()

        # Ensure no sorting plugins are listed
        sorting_plugin_ids = [p.id for p in all_plugins if loader.plugin_features.get(p.id) == "sorting"]
        self.assertGreater(len(sorting_plugin_ids), 0)

        for pid in sorting_plugin_ids:
            self.assertIsNone(loader.get_plugin(pid))
            self.assertNotIn(pid, [p.id for p in filtered_plugins])

    def test_hooks_trigger(self):
        toggle_hook_calls = []
        self.api_manager.register_hook("on_feature_toggle", lambda feature_name, enabled: toggle_hook_calls.append((feature_name, enabled)))

        self.api_manager.disable_feature("search")
        self.assertEqual(len(toggle_hook_calls), 1)
        self.assertEqual(toggle_hook_calls[0], ("search", False))

        self.api_manager.enable_feature("search")
        self.assertEqual(len(toggle_hook_calls), 2)
        self.assertEqual(toggle_hook_calls[1], ("search", True))

        # Test before_plugin_load hook during load_all
        loader = PluginLoader(api_manager=self.api_manager)
        loader.load_all()
        self.assertGreater(self.api_manager.hook_stats.get("before_plugin_load", 0), 0)

        # Test after_generate_steps hook during step generation
        engine = Engine(api_manager=self.api_manager)
        plugin = loader.list_plugins()[0]
        engine.set_plugin(plugin, [3, 1, 2])
        engine.generate_steps([3, 1, 2])
        self.assertGreater(self.api_manager.hook_stats.get("after_generate_steps", 0), 0)

    def test_strict_compatibility_check(self):
        self.api_manager.config.strict_version_check = True
        loader = PluginLoader(api_manager=self.api_manager)
        loader.load_all()
        # Non-matching api_version_required plugins should be skipped if incompatible
        # (All core plugins requiring 1.0.0 are compatible with 2.0.0 via major logic, so they load)
        compat, msg, _ = self.api_manager.check_compatibility("9.9.9")
        self.assertFalse(compat)

if __name__ == "__main__":
    unittest.main()
