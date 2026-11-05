# -*- coding: utf-8 -*-
"""
Tests for Traffic Light Educational Plugin (Phase 1)
"""
import unittest
from core.plugin_system import PluginLoader
from core.engine import Engine
from core.step import VisualizationStep
from plugins.traffic_light.plugin import TrafficLightPlugin, CODE_TEMPLATES, LOGICAL_TAG_LINES


class TestTrafficLightPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = TrafficLightPlugin()

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.id, "traffic_light")
        self.assertEqual(self.plugin.plugin_type, "simulation")
        self.assertEqual(self.plugin.icon, "🚦")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertTrue("Jelzőlámpa" in self.plugin.name)

    def test_supported_languages(self):
        langs = self.plugin.get_supported_languages()
        self.assertEqual(sorted(langs), sorted(["Python", "C++", "C", "BASIC", "Java", "Pascal"]))
        for lang in langs:
            code = self.plugin.get_code(lang)
            self.assertIsInstance(code, str)
            self.assertGreater(len(code), 20)

    def test_logical_tag_lines_in_all_languages(self):
        langs = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
        required_tags = ["INIT", "LOOP_START", "RED", "RED_YELLOW", "GREEN", "YELLOW", "COMPLETE"]
        tag_expected_tokens = {
            "INIT": ["INIT"],
            "LOOP_START": ["for", "FOR", "cycle", "CYCLE"],
            "RED": ["red", "Red", "1, 0, 0", "true, false, false", "True, False, False"],
            "RED_YELLOW": ["ry", "Ry", "1, 1, 0", "true, true, false", "True, True, False"],
            "GREEN": ["green", "Green", "0, 0, 1", "false, false, true", "False, False, True"],
            "YELLOW": ["yellow", "Yellow", "0, 1, 0", "false, true, false", "False, True, False"],
            "COMPLETE": ["COMPLETED"],
        }
        for lang in langs:
            code_lines = self.plugin.get_code(lang).splitlines()
            for tag in required_tags:
                line_no = self.plugin.get_line_for_tag(lang, tag)
                self.assertGreaterEqual(line_no, 1, f"Tag {tag} invalid line in {lang}")
                self.assertLessEqual(line_no, len(code_lines), f"Tag {tag} out of bounds in {lang}")
                actual_line = code_lines[line_no - 1]
                expected_tokens = tag_expected_tokens[tag]
                has_token = any(token in actual_line for token in expected_tokens)
                self.assertTrue(
                    has_token,
                    f"Line {line_no} in {lang} ('{actual_line}') does not match expected tokens for tag {tag}"
                )

    def test_initial_step(self):
        steps = list(self.plugin.get_steps())
        self.assertGreater(len(steps), 0)
        init_step = steps[0]
        self.assertEqual(init_step.extra.get("state"), "INIT")
        self.assertEqual(init_step.extra.get("tag"), "INIT")
        lamps = init_step.extra.get("lamps")
        self.assertFalse(lamps["red"])
        self.assertFalse(lamps["yellow"])
        self.assertFalse(lamps["green"])

    def test_configurable_durations_and_remaining_time(self):
        self.plugin.set_param("red_duration", 2)
        self.plugin.set_param("red_yellow_duration", 1)
        self.plugin.set_param("green_duration", 2)
        self.plugin.set_param("yellow_duration", 1)
        self.plugin.set_param("cycles", 1)

        steps = list(self.plugin.get_steps())
        # Steps structure:
        # 1. INIT
        # 2. LOOP_START (cycle 1)
        # 3. RED (2 sec -> rem 2, rem 1) = 2 steps
        # 4. RED_YELLOW (1 sec -> rem 1) = 1 step
        # 5. GREEN (2 sec -> rem 2, rem 1) = 2 steps
        # 6. YELLOW (1 sec -> rem 1) = 1 step
        # 7. COMPLETE = 1 step
        # Total = 1 + 1 + 2 + 1 + 2 + 1 + 1 = 9 steps
        self.assertEqual(len(steps), 9)

        # Check transitions and countdowns in cycle 1
        phase_steps = steps[2:8]
        expected_phases = [
            ("RED", 2, {"red": True, "yellow": False, "green": False}),
            ("RED", 1, {"red": True, "yellow": False, "green": False}),
            ("RED_YELLOW", 1, {"red": True, "yellow": True, "green": False}),
            ("GREEN", 2, {"red": False, "yellow": False, "green": True}),
            ("GREEN", 1, {"red": False, "yellow": False, "green": True}),
            ("YELLOW", 1, {"red": False, "yellow": True, "green": False}),
        ]

        for step, (expected_st, expected_rem, expected_lamps) in zip(phase_steps, expected_phases):
            self.assertEqual(step.extra.get("state"), expected_st)
            self.assertEqual(step.extra.get("remaining_time"), expected_rem)
            self.assertEqual(step.extra.get("lamps"), expected_lamps)
            self.assertIn("mp", step.explanation)

        # Final step
        self.assertEqual(steps[-1].extra.get("state"), "COMPLETED")
        self.assertEqual(steps[-1].extra.get("tag"), "COMPLETE")

    def test_full_cycle_transition_sequence(self):
        self.plugin.set_param("red_duration", 1)
        self.plugin.set_param("red_yellow_duration", 1)
        self.plugin.set_param("green_duration", 1)
        self.plugin.set_param("yellow_duration", 1)
        self.plugin.set_param("cycles", 2)

        steps = list(self.plugin.get_steps())
        states_sequence = [s.extra.get("state") for s in steps if s.extra.get("state") in ["RED", "RED_YELLOW", "GREEN", "YELLOW"]]
        expected_sequence = [
            "RED", "RED_YELLOW", "GREEN", "YELLOW",
            "RED", "RED_YELLOW", "GREEN", "YELLOW",
        ]
        self.assertEqual(states_sequence, expected_sequence)

    def test_engine_single_step_and_controls(self):
        self.plugin.set_param("red_duration", 1)
        self.plugin.set_param("red_yellow_duration", 1)
        self.plugin.set_param("green_duration", 1)
        self.plugin.set_param("yellow_duration", 1)
        self.plugin.set_param("cycles", 1)

        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        self.assertEqual(len(engine.steps), 7)
        self.assertEqual(engine.step_idx, 0)
        self.assertEqual(engine.steps[0].extra.get("state"), "INIT")

        # Step forward
        s1 = engine.next_step()
        self.assertIsNotNone(s1)
        self.assertEqual(engine.step_idx, 1)
        self.assertEqual(s1.extra.get("state"), "CYCLE_START")

        s2 = engine.next_step()
        self.assertEqual(s2.extra.get("state"), "RED")

        # Step back
        prev = engine.prev_step()
        self.assertEqual(engine.step_idx, 1)
        self.assertEqual(prev.extra.get("state"), "CYCLE_START")

    def test_plugin_loader_discovery_and_category(self):
        loader = PluginLoader()
        loader.load_all()
        plugin = loader.get_plugin("traffic_light")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.id, "traffic_light")

        feature_name = loader._get_feature_name(plugin, "traffic_light")
        self.assertEqual(feature_name, "simulation")

        grouped = loader.list_plugins_grouped()
        self.assertIn("simulation", grouped)
        sim_ids = [p.id for p in grouped["simulation"]]
        self.assertIn("traffic_light", sim_ids)


class TestTrafficLightGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from PySide6.QtWidgets import QApplication
            import sys
            cls.app = QApplication.instance() or QApplication(sys.argv)
        except Exception:
            cls.app = None

    def setUp(self):
        if not self.app:
            self.skipTest("PySide6 is not available")

    def test_traffic_light_widget_rendering(self):
        from ui.traffic_light_widget import TrafficLightViewerWidget
        w = TrafficLightViewerWidget()
        w.show()
        self.app.processEvents()

        # Update step state: RED
        step = VisualizationStep(
            explanation="Test piros",
            code_line=5,
            extra={
                "tag": "RED",
                "state": "RED",
                "state_hu": "PIROS",
                "lamps": {"red": True, "yellow": False, "green": False},
                "remaining_time": 3,
                "cycle": 1,
                "total_cycles": 2,
                "next_state": "RED_YELLOW",
            }
        )
        w.update_state(step)
        self.app.processEvents()

        self.assertTrue(w.lamp_red.is_active)
        self.assertFalse(w.lamp_yellow.is_active)
        self.assertFalse(w.lamp_green.is_active)
        self.assertEqual(w.state_badge.text(), "PIROS")
        self.assertEqual(w.countdown_label.text(), "3 mp")
        self.assertIn("Test piros", w.status_detail.text())

        # Update step state: RED_YELLOW
        step_ry = VisualizationStep(
            explanation="Test piros-sárga",
            code_line=7,
            extra={
                "tag": "RED_YELLOW",
                "state": "RED_YELLOW",
                "state_hu": "PIROS-SÁRGA",
                "lamps": {"red": True, "yellow": True, "green": False},
                "remaining_time": 1,
                "cycle": 1,
                "total_cycles": 2,
                "next_state": "GREEN",
            }
        )
        w.update_state(step_ry)
        self.app.processEvents()

        self.assertTrue(w.lamp_red.is_active)
        self.assertTrue(w.lamp_yellow.is_active)
        self.assertFalse(w.lamp_green.is_active)
        self.assertEqual(w.state_badge.text(), "PIROS-SÁRGA")

        # Update step state: GREEN
        step_g = VisualizationStep(
            explanation="Test zöld",
            code_line=9,
            extra={
                "tag": "GREEN",
                "state": "GREEN",
                "state_hu": "ZÖLD",
                "lamps": {"red": False, "yellow": False, "green": True},
                "remaining_time": 2,
                "cycle": 1,
                "total_cycles": 2,
                "next_state": "YELLOW",
            }
        )
        w.update_state(step_g)
        self.app.processEvents()

        self.assertFalse(w.lamp_red.is_active)
        self.assertFalse(w.lamp_yellow.is_active)
        self.assertTrue(w.lamp_green.is_active)
        self.assertEqual(w.state_badge.text(), "ZÖLD")

        w.close()
        w.deleteLater()

    def test_main_window_switching_to_traffic_light(self):
        from ui.main_window import MainWindow
        win = MainWindow()
        win.show()
        self.app.processEvents()

        plugin = win.plugin_loader.get_plugin("traffic_light")
        self.assertIsNotNone(plugin)

        win.current_plugin = plugin
        win.update_active_visualizer()
        win.on_language_changed("Python")
        win.reset()
        self.app.processEvents()

        # The active widget in viz_stack should now be the custom visualizer
        active_viz = win.viz_stack.currentWidget()
        from ui.traffic_light_widget import TrafficLightViewerWidget
        self.assertIsInstance(active_viz, TrafficLightViewerWidget)

        # Advance step
        win.next_step()
        self.app.processEvents()

        # Switch language mid-simulation and test line update
        win.on_language_changed("Pascal")
        self.app.processEvents()

        win.close()
        win.deleteLater()


if __name__ == "__main__":
    unittest.main()
