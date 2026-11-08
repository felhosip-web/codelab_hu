# -*- coding: utf-8 -*-
"""
Automated unit and integration tests for Traffic Light Educational Plugin Phase 2:
Vehicle Traffic Intersection (plugins/traffic_light/plugin.py & ui/traffic_intersection_widget.py).
"""
import unittest
import os
from unittest.mock import patch
from core.plugin_system import PluginLoader
from core.engine import Engine
from core.step import VisualizationStep
from plugins.traffic_light.plugin import (
    TrafficLightPlugin,
    TrafficIntersectionPlugin,
    CLEAN_CODE_TEMPLATES_P2,
    DERIVED_TAG_LINES_P2,
)

try:
    from PySide6.QtWidgets import QApplication
    from ui.traffic_intersection_widget import TrafficIntersectionViewerWidget
    HAS_QT = True
except ImportError:
    HAS_QT = False


class TestTrafficIntersectionPlugin(unittest.TestCase):
    """Belső logika és állapotgép tesztek a kereszteződés szimulációhoz."""

    def setUp(self):
        self.plugin = TrafficIntersectionPlugin()

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.id, "traffic_intersection")
        self.assertEqual(self.plugin.plugin_type, "simulation")
        self.assertEqual(self.plugin.icon, "🚦")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertTrue("Kereszteződés" in self.plugin.name)
        self.assertTrue("Phase 2" in self.plugin.description)

    def test_supported_languages(self):
        langs = self.plugin.get_supported_languages()
        self.assertEqual(sorted(langs), sorted(["Python", "C++", "C", "BASIC", "Java", "Pascal"]))
        for lang in langs:
            code = self.plugin.get_code(lang)
            self.assertIsInstance(code, str)
            self.assertGreater(len(code), 20)
            self.assertNotIn("[TAG:", code)

    def test_logical_tag_lines_in_all_languages(self):
        langs = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
        required_tags = [
            "INIT", "LOOP_START", "NS_GREEN", "NS_YELLOW",
            "CLEARANCE_1", "EW_GREEN", "EW_YELLOW", "CLEARANCE_2", "COMPLETE"
        ]

        exact_python_statements = {
            "INIT": "intersection = init_intersection(queues=vehicles_count)",
            "LOOP_START": "for cycle in range(1, total_cycles + 1):",
            "NS_GREEN": 'set_lights(ns="GREEN", ew="RED", duration=ns_green_sec)',
            "NS_YELLOW": 'set_lights(ns="YELLOW", ew="RED", duration=yellow_sec)',
            "CLEARANCE_1": 'set_lights(ns="RED", ew="RED", duration=all_red_sec)',
            "EW_GREEN": 'set_lights(ns="RED", ew="GREEN", duration=ew_green_sec)',
            "EW_YELLOW": 'set_lights(ns="RED", ew="YELLOW", duration=yellow_sec)',
            "CLEARANCE_2": 'set_lights(ns="RED", ew="RED", duration=all_red_sec)',
            "COMPLETE": "finish_simulation()",
        }

        for lang in langs:
            for tag in required_tags:
                line_no = self.plugin.get_line_for_tag(lang, tag)
                self.assertIsInstance(line_no, int)
                self.assertGreater(line_no, 0, f"Missing tag {tag} in {lang}")

                code_lines = self.plugin.get_code(lang).splitlines()
                self.assertLessEqual(line_no, len(code_lines), f"Line {line_no} out of bounds for {lang}")
                target_line_text = code_lines[line_no - 1].strip()

                if lang == "Python" and tag in exact_python_statements:
                    expected = exact_python_statements[tag]
                    self.assertEqual(
                        target_line_text,
                        expected,
                        f"Python tag {tag} at line {line_no} is '{target_line_text}', expected '{expected}'"
                    )

    def test_configurable_parameters(self):
        params = self.plugin.get_params()
        self.assertIsNotNone(params.get("ns_green_duration"))
        self.assertIsNotNone(params.get("ew_green_duration"))
        self.assertIsNotNone(params.get("yellow_duration"))
        self.assertIsNotNone(params.get("all_red_duration"))
        self.assertIsNotNone(params.get("vehicles_per_approach"))
        self.assertIsNotNone(params.get("cycles"))

        self.plugin.set_param("ns_green_duration", 5)
        self.assertEqual(self.plugin.params.get("ns_green_duration"), 5)

    def test_no_conflicting_green_signals(self):
        steps = list(self.plugin.get_steps())
        self.assertGreater(len(steps), 10)

        for step in steps:
            extra = step.extra
            lights = extra.get("lights", {})
            ns = lights.get("ns", {})
            ew = lights.get("ew", {})

            ns_green = ns.get("green", False)
            self.assertFalse(
                ns_green and ew.get("green", False),
                f"Conflicting green signals detected in step: {step.explanation}"
            )
            self.assertFalse(
                ns.get("green", False) and ew.get("yellow", False),
                "Conflicting NS green with EW yellow!"
            )
            self.assertFalse(
                ew.get("green", False) and ns.get("yellow", False),
                "Conflicting EW green with NS yellow!"
            )

    def test_vehicles_stop_at_red_and_never_enter(self):
        steps = list(self.plugin.get_steps())

        for step in steps:
            extra = step.extra
            lights = extra.get("lights", {})
            vehicles = extra.get("vehicles", {})

            ns_red = lights.get("ns", {}).get("red", False)
            ew_red = lights.get("ew", {}).get("red", False)

            if ns_red and not lights.get("ns", {}).get("green", False) and not lights.get("ns", {}).get("yellow", False):
                for d in ["north", "south"]:
                    waiting_v = [v for v in vehicles.get(d, []) if v["status"] == "waiting"]
                    for v in waiting_v:
                        self.assertEqual(v["queue_pos"], 0)

            if ew_red and not lights.get("ew", {}).get("green", False) and not lights.get("ew", {}).get("yellow", False):
                for d in ["east", "west"]:
                    waiting_v = [v for v in vehicles.get(d, []) if v["status"] == "waiting"]
                    for v in waiting_v:
                        self.assertEqual(v["queue_pos"], 0)

    def test_safe_vehicle_spacing_and_queue_progression(self):
        steps = list(self.plugin.get_steps())

        for step in steps:
            extra = step.extra
            vehicles = extra.get("vehicles", {})
            for d in ["north", "south", "east", "west"]:
                dir_vehicles = vehicles.get(d, [])
                queue_positions = [v["queue_pos"] for v in dir_vehicles if v["status"] in ("waiting", "queued")]
                self.assertEqual(len(queue_positions), len(set(queue_positions)))
                if queue_positions:
                    self.assertEqual(sorted(queue_positions), list(range(len(queue_positions))))

    def test_all_red_clearance_phases(self):
        steps = list(self.plugin.get_steps())
        clearance_steps = [s for s in steps if s.extra.get("phase") in (TrafficIntersectionPlugin.PHASE_CLEARANCE_1, TrafficIntersectionPlugin.PHASE_CLEARANCE_2)]
        self.assertGreater(len(clearance_steps), 0)

        for s in clearance_steps:
            lights = s.extra.get("lights", {})
            self.assertTrue(lights.get("ns", {}).get("red"))
            self.assertFalse(lights.get("ns", {}).get("green"))
            self.assertTrue(lights.get("ew", {}).get("red"))
            self.assertFalse(lights.get("ew", {}).get("green"))

    def test_step_count_matches_duration_math(self):
        self.plugin.set_param("ns_green_duration", 2)
        self.plugin.set_param("ew_green_duration", 2)
        self.plugin.set_param("yellow_duration", 1)
        self.plugin.set_param("all_red_duration", 1)
        self.plugin.set_param("cycles", 3)

        steps = list(self.plugin.get_steps())
        self.assertEqual(len(steps), 29)


class TestTrafficIntersectionIntegration(unittest.TestCase):
    """Integrációs és felületi tesztek."""

    def setUp(self):
        if HAS_QT:
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            self.app = QApplication.instance() or QApplication([])

    def test_plugin_discovery_and_categorization(self):
        loader = PluginLoader()
        loader.load_all()

        p1 = loader.get_plugin("traffic_light")
        p2 = loader.get_plugin("traffic_intersection")

        self.assertIsNotNone(p1, "Phase 1 plugin not found in loader!")
        self.assertIsNotNone(p2, "Phase 2 plugin not found in loader!")

        grouped = loader.list_plugins_grouped()
        self.assertIn("simulation", grouped)
        sim_ids = [p.id for p in grouped["simulation"]]
        self.assertIn("traffic_light", sim_ids)
        self.assertIn("traffic_intersection", sim_ids)

    def test_engine_integration(self):
        loader = PluginLoader()
        loader.load_all()
        p2 = loader.get_plugin("traffic_intersection")

        engine = Engine()
        engine.set_plugin(p2)
        engine.generate_steps()
        self.assertGreater(len(engine.steps), 0)

        # Step through engine
        step1 = engine.next_step()
        self.assertIsNotNone(step1)
        self.assertEqual(engine.step_idx, 1)

        # Step back
        prev = engine.prev_step()
        self.assertIsNotNone(prev)
        self.assertEqual(engine.step_idx, 0)

    @unittest.skipUnless(HAS_QT, "PySide6 required for UI testing")
    def test_traffic_intersection_widget_rendering(self):
        widget = TrafficIntersectionViewerWidget()
        plugin = TrafficIntersectionPlugin()
        steps = list(plugin.get_steps())

        for step in steps[:10]:
            widget.update_state(step)
            self.assertTrue(len(widget.right_of_way_badge.text()) > 0)
            self.assertTrue(len(widget.ns_light_status.text()) > 0)
            self.assertTrue(len(widget.ew_light_status.text()) > 0)

        widget.deleteLater()

    @unittest.skipUnless(HAS_QT, "PySide6 required for UI testing")
    def test_main_window_module_switching_and_visualizer_cleanup(self):
        from ui.main_window import MainWindow
        win = MainWindow()
        win.show()
        self.app.processEvents()

        # 1. Betöltjük a Phase 1 plugint
        p1 = win.plugin_loader.get_plugin("traffic_light")
        self.assertIsNotNone(p1)
        win.current_plugin = p1
        win.update_active_visualizer()
        win.on_language_changed("Python")
        win.reset()
        self.assertEqual(win.current_plugin.id, "traffic_light")
        self.assertIn("traffic_light", win.plugin_visualizers)

        # 2. Átváltunk a Phase 2 pluginra
        p2 = win.plugin_loader.get_plugin("traffic_intersection")
        self.assertIsNotNone(p2)
        win.current_plugin = p2
        win.update_active_visualizer()
        win.on_language_changed("Python")
        win.reset()
        self.assertEqual(win.current_plugin.id, "traffic_intersection")
        self.assertIn("traffic_intersection", win.plugin_visualizers)

        # 3. Visszaváltunk Phase 1-re: Phase 1 még mindig tökéletesen működik
        win.current_plugin = p1
        win.update_active_visualizer()
        win.on_language_changed("Python")
        win.reset()
        self.assertEqual(win.current_plugin.id, "traffic_light")
        self.assertEqual(len(win.steps), len(list(p1.get_steps())))

        # 4. Újratöltjük a pluginokat, ellenőrizve a tiszta cleanupot
        with patch("ui.main_window.QMessageBox.information"), patch("ui.main_window.QMessageBox.warning"):
            with patch.object(win, 'refresh_plugin_list'):
                win.on_reload_plugins()
                self.app.processEvents()
                self.assertEqual(len(win.plugin_visualizers), 0)
                self.assertEqual(win.viz_stack.currentWidget(), win.array_viewer)

        win.close()
        win.deleteLater()


if __name__ == "__main__":
    unittest.main()
