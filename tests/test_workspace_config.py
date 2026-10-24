# -*- coding: utf-8 -*-
import unittest
import tempfile
import shutil
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


if __name__ == "__main__":
    unittest.main()
