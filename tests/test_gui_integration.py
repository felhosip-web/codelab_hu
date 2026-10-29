# -*- coding: utf-8 -*-
"""
GUI Integration and Visual Smoke Tests
Tests PySide6 application initialization, user interactions, dialogs, custom widgets,
and offscreen visual rendering.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure headless Qt execution environment
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QTreeWidget,
        QComboBox,
        QPushButton,
        QLineEdit,
        QSlider,
        QMessageBox,
        QDialog,
    )
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

if not HAS_PYSIDE6:
    raise unittest.SkipTest("PySide6 is not installed in this environment")

from ui.main_window import MainWindow
from ui.widgets import (
    ArrayViewerWidget,
    CodeViewerWidget,
    StatsBar,
    StringViewerWidget,
    ArrayConceptsViewerWidget,
)
from ui.workspace_settings_dialog import WorkspaceSettingsDialog
from ui.api_manager_dialog import APIManagerDialog
from ui.state_manager_dialog import StateManagerDialog
from ui.rest_api_dialog import RESTAPIDialog
from ui.settings_dialog import SettingsDialog
from ui.license_dialog import LicenseDialog
from ui.breakpoint_dialog import BreakpointDialog

from core.workspace_config import WorkspaceConfig
from core.api_manager import APIManager
from core.engine import Engine
from core.plugin_system import PluginLoader
from core.rest_api import SecureRESTAPIServer
from core.license_manager import LicenseManager
from core.breakpoints import BreakpointManager, KeyBindingManager
from core.input_parser import PRESETS


app = None


def get_qapp():
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def select_plugin_by_id(window: MainWindow, plugin_id: str):
    """Helper to select a specific plugin in algo_list tree."""
    tree = window.algo_list
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        for j in range(cat.childCount()):
            child = cat.child(j)
            if child.data(0, Qt.UserRole) == plugin_id:
                tree.setCurrentItem(child)
                return True
    return False


class TestMainWindowInitialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        if hasattr(self, 'window') and self.window:
            self.window.close()
            self.window.deleteLater()
            self.window = None
        self.app.processEvents()

    def test_main_window_initial_state_and_layout(self):
        """Verify MainWindow initializes essential widgets, title, and layout structure."""
        self.assertIsNotNone(self.window)
        self.assertTrue(self.window.windowTitle())
        self.assertIsNotNone(self.window.centralWidget())

        # Outer and workspace splitters
        self.assertIsNotNone(self.window.outer_splitter)
        self.assertIsNotNone(self.window.workspace_splitter)

        # Essential sidebar widgets
        self.assertIsInstance(self.window.algo_list, QTreeWidget)
        self.assertGreater(self.window.algo_list.topLevelItemCount(), 0)
        self.assertIsInstance(self.window.lang_combo, QComboBox)
        self.assertEqual(self.window.lang_combo.currentText(), "C++")

        # Control buttons
        self.assertIsInstance(self.window.btn_play, QPushButton)
        self.assertIsInstance(self.window.btn_step, QPushButton)
        self.assertIsInstance(self.window.btn_reset, QPushButton)
        self.assertIsInstance(self.window.btn_new, QPushButton)

        # Input panel controls
        self.assertIsInstance(self.window.input_edit, QLineEdit)
        self.assertIsInstance(self.window.btn_apply, QPushButton)
        self.assertIsInstance(self.window.preset_combo, QComboBox)

        # Speed slider
        self.assertIsInstance(self.window.speed_slider, QSlider)

        # Workspace widgets
        self.assertIsInstance(self.window.array_viewer, ArrayViewerWidget)
        self.assertIsInstance(self.window.code_viewer, CodeViewerWidget)
        self.assertIsInstance(self.window.stats_bar, StatsBar)

        # Menu bar sanity check
        menubar = self.window.menuBar()
        self.assertIsNotNone(menubar)
        menus = [action.text() for action in menubar.actions()]
        self.assertTrue(any("Állapot" in m for m in menus))
        self.assertTrue(any("API" in m or "Eszközök" in m for m in menus))

        # Initial plugin and steps check
        self.assertIsNotNone(self.window.current_plugin)
        self.assertIsNotNone(self.window.steps)
        self.assertGreater(len(self.window.steps), 0)


class TestMainWindowInteractions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        if hasattr(self, 'window') and self.window:
            self.window.close()
            self.window.deleteLater()
            self.window = None
        self.app.processEvents()

    def test_algo_tree_selection_change(self):
        """Selecting a different algorithm in the tree widget updates current plugin and UI state."""
        tree = self.window.algo_list

        target_child = None
        for i in range(tree.topLevelItemCount()):
            cat = tree.topLevelItem(i)
            for j in range(cat.childCount()):
                child = cat.child(j)
                plugin_id = child.data(0, Qt.UserRole)
                if plugin_id and plugin_id != self.window.current_plugin.id:
                    target_child = child
                    break
            if target_child:
                break

        self.assertIsNotNone(target_child)
        expected_plugin_id = target_child.data(0, Qt.UserRole)

        tree.setCurrentItem(target_child)
        self.app.processEvents()

        self.assertEqual(self.window.current_plugin.id, expected_plugin_id)
        self.assertIn(expected_plugin_id, self.window.code_viewer.title_label.text().lower())

    def test_language_combobox_change(self):
        """Changing language combo selection updates code viewer content and language."""
        self.window.lang_combo.setCurrentText("Python")
        self.app.processEvents()

        self.assertEqual(self.window.code_viewer.current_lang, "Python")
        self.assertIn("Python", self.window.code_viewer.title_label.text())
        self.assertTrue(len(self.window.code_viewer.current_code) > 0)

    def test_interactive_input_and_presets(self):
        """Applying custom input or selecting a preset updates current array and regenerates steps."""
        # Ensure an array-based plugin (e.g. bubble_sort) is active
        self.assertTrue(select_plugin_by_id(self.window, "bubble_sort"))
        self.app.processEvents()
        self.assertTrue(self.window.is_array_based_plugin())

        # 1. Custom string input
        self.window.input_edit.setText("12, 45, 7, 89, 23")
        self.window.btn_apply.click()
        self.app.processEvents()

        self.assertEqual(self.window.current_array, [12, 45, 7, 89, 23])
        self.assertGreater(len(self.window.steps), 0)

        # 2. Preset selection
        first_preset_key = list(PRESETS.keys())[0]
        self.window.preset_combo.setCurrentText(first_preset_key)
        self.app.processEvents()

        self.assertEqual(self.window.current_array, PRESETS[first_preset_key])

    @patch.object(QMessageBox, 'warning')
    def test_invalid_input_handling_boundary(self, mock_warning):
        """Entering invalid array input displays error label and pops up warning without crashing."""
        self.assertTrue(select_plugin_by_id(self.window, "bubble_sort"))
        self.app.processEvents()

        prev_array = list(self.window.current_array)
        self.window.input_edit.setText("invalid_number_string")
        self.window.btn_apply.click()
        self.app.processEvents()

        mock_warning.assert_called_once()
        self.assertEqual(self.window.current_array, prev_array)
        self.assertTrue(len(self.window.input_status_label.text()) > 0)

    def test_stepping_and_playback_controls(self):
        """Test step forward, step back, reset, new array, playback toggle, and slider controls."""
        self.assertTrue(select_plugin_by_id(self.window, "bubble_sort"))
        self.app.processEvents()

        self.assertEqual(self.window.current_step_idx, 0)

        # Playback toggle
        self.assertFalse(self.window.is_playing)
        self.window.btn_play.click()
        self.app.processEvents()
        self.assertTrue(self.window.is_playing)

        self.window.btn_play.click()
        self.app.processEvents()
        self.assertFalse(self.window.is_playing)

        # Step forward
        self.window.btn_step.click()
        self.app.processEvents()
        self.assertEqual(self.window.current_step_idx, 1)

        self.window.bottom_btn_forward.click()
        self.app.processEvents()
        self.assertEqual(self.window.current_step_idx, 2)

        # Step back
        self.window.bottom_btn_back.click()
        self.app.processEvents()
        self.assertEqual(self.window.current_step_idx, 1)

        # Reset
        self.window.btn_reset.click()
        self.app.processEvents()
        self.assertEqual(self.window.current_step_idx, 0)

        # Speed slider sync
        self.window.speed_slider.setValue(500)
        self.app.processEvents()
        self.assertEqual(self.window.bottom_speed_slider.value(), 500)

        # New array button
        self.window.btn_new.click()
        self.app.processEvents()
        self.assertEqual(len(self.window.current_array), 10)
        self.assertEqual(self.window.current_step_idx, 0)

    def test_breakpoint_and_undo_redo(self):
        """Test breakpoint toggling and state manager save/undo/redo execution."""
        self.assertTrue(select_plugin_by_id(self.window, "bubble_sort"))
        self.app.processEvents()

        # Toggle breakpoint
        self.window.bottom_btn_breakpoint.click()
        self.app.processEvents()
        self.assertIn("Töréspont", self.window.explanation_label.text())

        # Push a new snapshot state so undo is available
        snapshot = self.window.engine.get_current_state()
        snapshot.description = "Test snapshot"
        self.window.engine.state_manager.push_history(snapshot)

        self.window.on_undo_state()
        self.app.processEvents()
        self.assertIn("Undo", self.window.explanation_label.text())

        self.window.on_redo_state()
        self.app.processEvents()
        self.assertIn("Redo", self.window.explanation_label.text())


class TestCustomVisualizationWidgets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_array_viewer_widget(self):
        """Test ArrayViewerWidget initialization and state updates."""
        widget = ArrayViewerWidget([10, 20, 30])
        widget.show()
        self.app.processEvents()

        self.assertEqual(len(widget.labels), 3)

        # Update with key and highlights
        widget.update_state([10, 20, 30], key=15, sorted_end=1, highlights=[0])
        self.app.processEvents()
        self.assertFalse(widget.key_label.isHidden())
        self.assertIn("15", widget.key_label.text())

        # Update with no key
        widget.update_state([10, 20, 30], key=None, sorted_end=1, highlights=[0])
        self.app.processEvents()
        self.assertTrue(widget.key_label.isHidden())

        widget.close()
        widget.deleteLater()

    def test_code_viewer_widget(self):
        """Test CodeViewerWidget configuration and line highlighting."""
        config = WorkspaceConfig(theme="dark", font_size=12, show_line_numbers=True)
        viewer = CodeViewerWidget(workspace_config=config)
        viewer.show()
        self.app.processEvents()

        code = "def add(a, b):\n    return a + b"
        viewer.set_code(code, "Python")
        self.assertEqual(viewer.current_code, code)
        self.assertEqual(viewer.current_lang, "Python")

        viewer.highlight_line(2)
        self.assertEqual(len(viewer.code_editor.extraSelections()), 1)

        # Apply new theme configuration
        light_config = WorkspaceConfig(theme="light", font_size=14, show_line_numbers=False)
        viewer.apply_workspace_config(light_config)
        self.app.processEvents()
        self.assertEqual(viewer.config.theme, "light")

        viewer.close()
        viewer.deleteLater()

    def test_stats_bar(self):
        """Test StatsBar complexity text and metric updates."""
        bar = StatsBar()
        bar.show()
        self.app.processEvents()

        bar.set_complexity("O(n log n)", "O(n)")
        self.assertIn("O(n log n)", bar.lbl_time.text())
        self.assertIn("O(n)", bar.lbl_space.text())

        bar.update_stats(comp=10, shifts=5, pass_num=1)

        bar.close()
        bar.deleteLater()

    def test_string_viewer_widget(self):
        """Test StringViewerWidget state updates."""
        sv = StringViewerWidget()
        sv.show()
        self.app.processEvents()

        mock_step = MagicMock()
        mock_step.text = "ABABC"
        mock_step.pattern = "ABC"
        mock_step.text_pos = 2
        mock_step.pattern_pos = 0
        mock_step.highlight_text = [2]
        mock_step.highlight_pattern = [0]
        mock_step.lps = [0, 0, 1]
        mock_step.hash_pattern = None
        mock_step.hash_text = None
        mock_step.explanation = "Comparing pattern at index 2"
        mock_step.extra = {"phase": "compare", "i": 2, "j": 0}

        sv.update_state(mock_step)
        self.app.processEvents()

        self.assertIn("Comparing pattern", sv.info_label.text())

        sv.close()
        sv.deleteLater()

    def test_array_concepts_viewer_widget(self):
        """Test ArrayConceptsViewerWidget state updates for 1D, 2D, and pointer structures."""
        acv = ArrayConceptsViewerWidget()
        acv.show()
        self.app.processEvents()

        mock_step = MagicMock()
        mock_step.array = [5, 10, 15]
        mock_step.array_2d = [[1, 2], [3, 4]]
        mock_step.jagged = [[1], [2, 3]]
        mock_step.memory = {1000: 5, 1004: 10}
        mock_step.pointers = {"ptr": 1000}
        mock_step.current_index = 0
        mock_step.explanation = "Accessing array element 0"
        mock_step.extra = {"j": 0}

        acv.update_state(mock_step)
        self.app.processEvents()

        self.assertIn("Accessing array element", acv.info_label.text())

        acv.close()
        acv.deleteLater()


class TestApplicationDialogs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_workspace_settings_dialog(self):
        """Test WorkspaceSettingsDialog presets, form updates, and saving."""
        config = WorkspaceConfig(font_size=10, theme="light")
        dialog = WorkspaceSettingsDialog(config)
        dialog.show()
        self.app.processEvents()

        # Apply a preset size
        dialog.set_preset("code_focus")
        self.assertEqual(dialog.pending_preset_sizes, [300, 700])

        # Form change
        dialog.size_spin.setValue(16)
        dialog.on_save()

        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(config.font_size, 16)
        self.assertEqual(config.splitter_sizes, [300, 700])

        dialog.close()
        dialog.deleteLater()

    def test_api_manager_dialog(self):
        """Test APIManagerDialog initialization and feature checkboxes."""
        api_mgr = APIManager()
        dialog = APIManagerDialog(api_mgr)
        dialog.show()
        self.app.processEvents()

        self.assertGreater(dialog.features_list.count(), 0)
        self.assertIsNotNone(dialog.stats_label)

        dialog.close()
        dialog.deleteLater()

    def test_state_manager_dialog(self):
        """Test StateManagerDialog save list and info display."""
        engine = Engine()
        dialog = StateManagerDialog(engine)
        dialog.show()
        self.app.processEvents()

        self.assertIsNotNone(dialog.list_widget)
        self.assertTrue("History:" in dialog.info_label.text())

        dialog.close()
        dialog.deleteLater()

    def test_rest_api_dialog(self):
        """Test RESTAPIDialog tab interface, controls, and trusted proxy settings validation & persistence."""
        from pathlib import Path
        loader = PluginLoader()
        engine = Engine()
        server = SecureRESTAPIServer(config_path="saves/test_gui_rest_config.json", plugin_loader=loader, engine=engine)
        dialog = RESTAPIDialog(server, plugin_loader=loader, engine=engine)
        dialog.show()
        self.app.processEvents()

        self.assertIsNotNone(dialog.enabled_check)
        self.assertIsNotNone(dialog.keys_list)
        self.assertIsNotNone(dialog.enable_trusted_proxy_check)
        self.assertIsNotNone(dialog.trusted_proxies_edit)

        # 1. Invalid proxy settings save attempt -> warning dialog, config not saved
        dialog.enable_trusted_proxy_check.setChecked(True)
        dialog.trusted_proxies_edit.setPlainText("invalid_ip_300.300.300.300")
        with patch.object(QMessageBox, 'warning') as mock_warn:
            dialog.on_save()
            mock_warn.assert_called_once()
            self.assertIn("Érvénytelen megbízható proxy", mock_warn.call_args[0][1])

        # 2. Valid proxy settings save attempt -> saved to disk
        dialog.trusted_proxies_edit.setPlainText("10.0.0.0/8\n192.168.1.1")
        with patch.object(QMessageBox, 'information'):
            dialog.on_save()

        # Reload server config from disk file and verify persistence
        reloaded_server = SecureRESTAPIServer(config_path="saves/test_gui_rest_config.json")
        self.assertTrue(reloaded_server.config.enable_trusted_proxy)
        self.assertEqual(reloaded_server.config.trusted_proxies, ["10.0.0.0/8", "192.168.1.1"])

        dialog.close()
        dialog.deleteLater()

        # Cleanup test config file
        p = Path("saves/test_gui_rest_config.json")
        if p.exists():
            p.unlink()

    def test_settings_dialog(self):
        """Test SettingsDialog keybinding list rendering."""
        kb_manager = KeyBindingManager()
        dialog = SettingsDialog(kb_manager)
        dialog.show()
        self.app.processEvents()

        self.assertGreater(dialog.keys_list.count(), 0)

        dialog.close()
        dialog.deleteLater()

    def test_license_dialog(self):
        """Test LicenseDialog tab widget and content."""
        license_mgr = LicenseManager()
        dialog = LicenseDialog(license_mgr)
        dialog.show()
        self.app.processEvents()

        self.assertIsNotNone(dialog.windowTitle())

        dialog.close()
        dialog.deleteLater()

    def test_breakpoint_dialog(self):
        """Test BreakpointDialog list and controls."""
        bp_manager = BreakpointManager()
        dialog = BreakpointDialog(bp_manager, current_plugin_id="bubble_sort")
        dialog.show()
        self.app.processEvents()

        self.assertIsNotNone(dialog.list_widget)

        dialog.close()
        dialog.deleteLater()


class TestVisualOffscreenRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_main_window_offscreen_render(self):
        """Render MainWindow offscreen and assert valid rendered QImage."""
        window = MainWindow()
        window.resize(1200, 800)
        window.show()
        self.app.processEvents()

        pixmap = window.grab()
        image = pixmap.toImage()

        self.assertFalse(image.isNull())
        self.assertEqual(image.width(), window.width())
        self.assertEqual(image.height(), window.height())
        self.assertGreater(image.depth(), 0)

        window.close()
        window.deleteLater()

    def test_array_viewer_offscreen_render(self):
        """Render ArrayViewerWidget offscreen and assert valid rendered QImage."""
        viewer = ArrayViewerWidget([42, 18, 99, 3])
        viewer.resize(400, 200)
        viewer.show()
        self.app.processEvents()

        pixmap = viewer.grab()
        image = pixmap.toImage()

        self.assertFalse(image.isNull())
        self.assertGreater(image.width(), 0)
        self.assertGreater(image.height(), 0)

        viewer.close()
        viewer.deleteLater()

    def test_code_viewer_offscreen_render(self):
        """Render CodeViewerWidget offscreen and assert valid rendered QImage."""
        viewer = CodeViewerWidget()
        viewer.set_code("int x = 100;", "C++")
        viewer.resize(500, 300)
        viewer.show()
        self.app.processEvents()

        pixmap = viewer.grab()
        image = pixmap.toImage()

        self.assertFalse(image.isNull())
        self.assertGreater(image.width(), 0)
        self.assertGreater(image.height(), 0)

        viewer.close()
        viewer.deleteLater()

    def test_dialogs_offscreen_render(self):
        """Render WorkspaceSettingsDialog offscreen and assert valid rendered QImage."""
        dialog = WorkspaceSettingsDialog(WorkspaceConfig())
        dialog.show()
        self.app.processEvents()

        pixmap = dialog.grab()
        image = pixmap.toImage()

        self.assertFalse(image.isNull())
        self.assertGreater(image.width(), 0)
        self.assertGreater(image.height(), 0)

        dialog.close()
        dialog.deleteLater()


if __name__ == "__main__":
    unittest.main()
