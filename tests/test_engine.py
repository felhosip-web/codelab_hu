# -*- coding: utf-8 -*-
import unittest
import shutil
from pathlib import Path
import json

from core.engine import Engine, StateManager, AppState
from core.plugin_system import PluginLoader
from core.api_manager import APIManager
from core.breakpoints import BreakpointManager


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.save_dir = Path("saves_test_engine")
        if self.save_dir.exists():
            shutil.rmtree(self.save_dir)
        self.save_dir.mkdir(exist_ok=True)

        self.api_manager = APIManager()
        self.breakpoint_manager = BreakpointManager(save_path=self.save_dir / "breakpoints.json")
        self.engine = Engine(api_manager=self.api_manager, breakpoint_manager=self.breakpoint_manager)
        self.engine.state_manager.save_dir = self.save_dir

        self.plugin_loader = PluginLoader(api_manager=self.api_manager)
        self.plugin_loader.load_all()

    def tearDown(self):
        if self.save_dir.exists():
            shutil.rmtree(self.save_dir)

    def test_generate_steps_without_plugin(self):
        self.engine.current_plugin = None
        elapsed = self.engine.generate_steps([1, 2, 3])
        self.assertEqual(self.engine.steps, [])
        self.assertEqual(self.engine.step_idx, 0)
        self.assertEqual(elapsed, 0.0)

    def test_set_plugin_and_generate_steps(self):
        plugins = self.plugin_loader.list_plugins()
        self.assertTrue(len(plugins) > 0)
        plugin = plugins[0]

        arr = [5, 3, 1, 4, 2]
        self.engine.set_plugin(plugin, arr)
        self.engine.generate_steps(arr)

        self.assertTrue(len(self.engine.steps) > 0)
        self.assertEqual(self.engine.step_idx, 0)

    def test_undo_redo_steps_consistency(self):
        plugins = self.plugin_loader.list_plugins()
        plugin = plugins[0]
        arr = [4, 2, 1, 3]

        self.engine.set_plugin(plugin, arr)
        self.engine.generate_steps(arr)

        # State 0 was pushed during set_plugin (step_idx=0)
        self.assertEqual(self.engine.step_idx, 0)

        # Advance a few steps and push state 1
        self.engine.next_step()
        self.engine.next_step()
        idx_1 = self.engine.step_idx
        self.engine.state_manager.push_history(self.engine.get_current_state())

        # Advance more and push state 2
        self.engine.next_step()
        idx_2 = self.engine.step_idx
        self.engine.state_manager.push_history(self.engine.get_current_state())

        # Undo -> restores state 1 (idx_1)
        undone_state = self.engine.undo()
        self.assertIsNotNone(undone_state)
        self.assertEqual(self.engine.step_idx, idx_1)
        self.assertTrue(len(self.engine.steps) > 0)

        # Redo -> restores state 2 (idx_2)
        redone_state = self.engine.redo()
        self.assertIsNotNone(redone_state)
        self.assertEqual(self.engine.step_idx, idx_2)

    def test_list_saves_filters_config_files(self):
        # Create dummy config files in save_dir
        (self.save_dir / "api_config.json").write_text(json.dumps({"key": "val"}))
        (self.save_dir / "rest_config.json").write_text(json.dumps({"key": "val"}))
        (self.save_dir / "breakpoints.json").write_text(json.dumps({"key": "val"}))
        (self.save_dir / "random_non_state.json").write_text(json.dumps({"foo": "bar"}))

        # Create valid AppState save
        plugins = self.plugin_loader.list_plugins()
        plugin = plugins[0]
        self.engine.set_plugin(plugin, [1, 2, 3])
        saved_path = self.engine.save_current("Test save")

        saves = self.engine.state_manager.list_saves()
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].name, saved_path.name)

    def test_breakpoint_triggers_stop(self):
        plugins = self.plugin_loader.list_plugins()
        plugin = plugins[0]
        arr = [3, 1, 2]

        self.engine.set_plugin(plugin, arr)
        self.engine.generate_steps(arr)

        if not self.engine.steps or len(self.engine.steps) < 2:
            self.skipTest("Not enough steps in plugin to test breakpoints")

        # Find line of step 1
        target_step = self.engine.steps[1]
        line = getattr(target_step, 'code_line', getattr(target_step, 'line', None))
        if line is None:
            self.skipTest("Step does not contain line info")

        self.breakpoint_manager.add_breakpoint(plugin.id, line)
        step_result = self.engine.next_step()

        self.assertIsNotNone(step_result)
        self.assertTrue(getattr(step_result, 'stopped', False))


if __name__ == '__main__':
    unittest.main()
