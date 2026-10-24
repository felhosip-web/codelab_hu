# -*- coding: utf-8 -*-
import unittest
import tempfile
import shutil
import json
from dataclasses import asdict
from pathlib import Path

from core.version import MAIN_VERSION, Version
from core.workspace_config import WorkspaceConfig


class TestWorkspaceConfig(unittest.TestCase):
    def test_version_bump_to_3_8_0(self):
        self.assertEqual(MAIN_VERSION, Version(3, 8, 0))

    def test_workspace_config_defaults_and_serialization(self):
        config = WorkspaceConfig()
        self.assertEqual(config.font_family, "Monospace")
        self.assertEqual(config.font_size, 11)
        self.assertEqual(config.theme, "light")
        self.assertTrue(config.syntax_highlight)
        self.assertTrue(config.show_line_numbers)
        self.assertEqual(config.splitter_orientation, "horizontal")

        temp_dir = tempfile.mkdtemp()
        try:
            config_file = Path(temp_dir) / "test_config.json"
            config.font_size = 14
            config.theme = "dark"
            config.splitter_orientation = "vertical"
            config.save(str(config_file))

            loaded = WorkspaceConfig.load(str(config_file))
            self.assertEqual(loaded.font_size, 14)
            self.assertEqual(loaded.theme, "dark")
            self.assertEqual(loaded.splitter_orientation, "vertical")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_ignores_unknown_keys_and_preserves_methods(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "workspace.json"
            config_file.write_text(json.dumps({
                "font_size": 16,
                "sidebar_collapsed": True,
                "splitter_sizes": [300, 700],
                "unknown": "ignored",
                "save": None,
                "load": False,
                "get_config_path": "invalid",
                "__dict__": {"theme": "dark"},
            }), encoding="utf-8")

            loaded = WorkspaceConfig.load(str(config_file))
            self.assertEqual(loaded.font_size, 16)
            self.assertTrue(loaded.sidebar_collapsed)
            self.assertEqual(loaded.splitter_sizes, [300, 700])
            self.assertFalse(hasattr(loaded, "unknown"))
            self.assertEqual(loaded.theme, "light")
            self.assertTrue(callable(loaded.load))
            self.assertTrue(callable(loaded.get_config_path))
            loaded.save(str(config_file))
            self.assertEqual(WorkspaceConfig.load(str(config_file)), loaded)

    def test_load_rejects_incompatible_field_types(self):
        defaults = asdict(WorkspaceConfig())
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "workspace.json"
            for key, default in defaults.items():
                for invalid in (None, True, 0, 1.5, "invalid", [], {}):
                    if type(invalid) is type(default):
                        continue
                    with self.subTest(field=key, value=invalid):
                        config_file.write_text(json.dumps({key: invalid}), encoding="utf-8")
                        loaded = WorkspaceConfig.load(str(config_file))
                        self.assertEqual(asdict(loaded), defaults)
                        self.assertIs(type(getattr(loaded, key)), type(default))

    def test_load_ignores_non_dictionary_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "workspace.json"
            for data in (None, True, 12, "text", [], ["font_size", 20]):
                with self.subTest(data=data):
                    config_file.write_text(json.dumps(data), encoding="utf-8")
                    self.assertEqual(WorkspaceConfig.load(str(config_file)), WorkspaceConfig())


if __name__ == "__main__":
    unittest.main()
