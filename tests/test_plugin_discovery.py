# -*- coding: utf-8 -*-
import unittest
import pathlib
import importlib.util
from core.plugin_system import PluginLoader, AlgorithmPluginBase


class TestPluginDiscovery(unittest.TestCase):
    def setUp(self):
        self.loader = PluginLoader()
        self.loader.load_all()

    def test_all_plugin_folders_and_classes_loaded_without_errors(self):
        """
        Dynamically scans the plugins/ directory, discovers all algorithm classes,
        asserts no duplicate plugin IDs exist, and verifies set equality between
        discovered plugin IDs and PluginLoader registered plugin IDs.
        """
        plugins_dir = pathlib.Path(__file__).parent.parent / "plugins"
        plugin_folders = [
            f for f in plugins_dir.iterdir()
            if f.is_dir() and f.name != "__pycache__" and (f / "plugin.py").exists()
        ]

        self.assertGreater(len(plugin_folders), 0, "No plugin folders found in plugins/")

        # Find all valid AlgorithmPluginBase subclasses in plugin files
        discovered_plugins = {}
        for folder in plugin_folders:
            plugin_file = folder / "plugin.py"
            module_name = f"plugins.{folder.name}.plugin"
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            self.assertIsNotNone(spec, f"Could not create spec for {folder.name}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, AlgorithmPluginBase)
                    and attr != AlgorithmPluginBase
                    and not getattr(attr, "__abstractmethods__", False)
                    and attr.__module__ == module.__name__
                ):
                    inst = attr()
                    pid = str(getattr(inst, "id", "")).strip()
                    if pid:
                        self.assertNotIn(
                            pid, discovered_plugins,
                            f"Duplicate plugin ID '{pid}' discovered in {folder.name}/{attr_name}"
                        )
                        discovered_plugins[pid] = (folder.name, attr_name, attr)

        # Check zero loading errors
        load_errors = self.loader.get_load_errors()
        self.assertEqual(
            len(load_errors), 0,
            f"PluginLoader reported load errors: {load_errors}"
        )

        # Assert set equality between discovered plugin IDs and loader registered plugin IDs
        self.assertEqual(
            set(discovered_plugins.keys()),
            set(self.loader.plugins.keys()),
            f"Discovered plugin IDs do not match registered plugin IDs in loader"
        )

        # Assert class name match for each plugin
        for pid, (folder_name, cls_name, cls) in discovered_plugins.items():
            with self.subTest(plugin_id=pid, class_name=cls_name):
                plugin_inst = self.loader.get_plugin(pid)
                self.assertIsNotNone(plugin_inst)
                self.assertEqual(plugin_inst.__class__.__name__, cls_name)

    def test_plugin_metadata_contracts(self):
        """
        Verifies that every loaded plugin satisfies contract requirements:
        non-empty id, name, description, complexity strings, and non-empty code
        samples for all 6 standard languages.
        """
        expected_langs = ["Python", "C++", "C", "Java", "Pascal", "BASIC"]
        for pid, plugin in self.loader.plugins.items():
            with self.subTest(plugin_id=pid):
                self.assertTrue(bool(plugin.id and plugin.id.strip()), f"Plugin {pid} has empty ID")
                self.assertTrue(bool(plugin.name and plugin.name.strip()), f"Plugin {pid} has empty name")
                self.assertTrue(bool(plugin.description and plugin.description.strip()), f"Plugin {pid} has empty description")
                self.assertTrue(hasattr(plugin, "time_complexity"), f"Plugin {pid} missing time_complexity")
                self.assertTrue(hasattr(plugin, "space_complexity"), f"Plugin {pid} missing space_complexity")

                supported = plugin.get_supported_languages()
                for lang in expected_langs:
                    self.assertIn(lang, supported, f"Plugin {pid} missing supported language: {lang}")
                    code = plugin.get_code(lang)
                    self.assertIsInstance(code, str, f"Plugin {pid} code for {lang} is not string")
                    self.assertGreater(len(code.strip()), 0, f"Plugin {pid} code for {lang} is empty")


if __name__ == "__main__":
    unittest.main()
