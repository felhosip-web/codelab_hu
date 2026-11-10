# -*- coding: utf-8 -*-
"""
Automated unit, safety invariant, and integration tests for
Phase 3: Full Traffic Intersection with Pedestrian Traffic
(plugins/traffic_light/plugin.py & ui/traffic_pedestrian_widget.py).
"""
import os
import unittest
from unittest.mock import patch, Mock
from core.plugin_system import PluginLoader
from core.engine import Engine
from core.step import VisualizationStep
from plugins.traffic_light.plugin import (
    TrafficLightPlugin,
    TrafficIntersectionPlugin,
    TrafficPedestrianIntersectionPlugin,
    CLEAN_CODE_TEMPLATES_P3,
    DERIVED_TAG_LINES_P3,
)

try:
    from PySide6.QtWidgets import QApplication
    from ui.traffic_pedestrian_widget import (
        PedestrianIntersectionCanvasWidget,
        TrafficPedestrianIntersectionViewerWidget,
    )
    HAS_QT = True
except ImportError:
    HAS_QT = False


class TestTrafficPedestrianPlugin(unittest.TestCase):
    """Belső logika, közlekedésbiztonsági invariánsok és állapotgép tesztek."""

    def setUp(self):
        self.plugin = TrafficPedestrianIntersectionPlugin()

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.id, "traffic_pedestrian_intersection")
        self.assertEqual(self.plugin.plugin_type, "simulation")
        self.assertEqual(self.plugin.icon, "🚶")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertTrue("Kereszteződés és gyalogos" in self.plugin.name)
        self.assertTrue("Phase 3" in self.plugin.description)

    def test_supported_languages(self):
        langs = self.plugin.get_supported_languages()
        self.assertEqual(sorted(langs), sorted(["Python", "C++", "C", "BASIC", "Java", "Pascal"]))
        for lang in langs:
            code = self.plugin.get_code(lang)
            self.assertIsInstance(code, str)
            self.assertGreater(len(code), 20)
            self.assertNotIn("[TAG:", code)

    def test_semantic_operation_tags_in_all_languages(self):
        """Minden szemantikai művelet címkéjének léteznie kell mind a 6 nyelven."""
        langs = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
        required_semantic_tags = [
            "INIT", "LOOP_START", "POLL_REQUESTS", "SET_SIGNALS",
            "PROCESS_CROSSINGS", "CHECK_CONFLICTS", "START_MOVEMENTS",
            "ADVANCE_QUEUES", "HOLD_TRAFFIC", "COMPLETE"
        ]

        exact_python_statements = {
            "INIT": "intersection = init_intersection_with_pedestrians()",
            "LOOP_START": "for cycle in range(1, total_cycles + 1):",
            "POLL_REQUESTS": "poll_pedestrian_requests(intersection)",
            "SET_SIGNALS": "set_all_signals(intersection, phase.vehicle_signals, phase.pedestrian_signals)",
            "PROCESS_CROSSINGS": "advance_crossing_entities(intersection)",
            "CHECK_CONFLICTS": "has_conflicts = check_traffic_conflicts(intersection, phase)",
            "START_MOVEMENTS": "start_permitted_movements(intersection, phase)",
            "ADVANCE_QUEUES": "advance_approach_queues(intersection, phase)",
            "HOLD_TRAFFIC": "hold_conflicting_traffic(intersection)",
            "COMPLETE": "finish_simulation(intersection)",
        }

        for lang in langs:
            for tag in required_semantic_tags:
                line_no = self.plugin.get_line_for_tag(lang, tag)
                self.assertIsInstance(line_no, int)
                self.assertGreater(line_no, 0, f"Missing semantic tag {tag} in {lang}")

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

    def test_semantic_step_metadata_tracking(self):
        """Minden szimulációs lépésnek konkrét szemantikai műveletet kell hordoznia."""
        steps = list(self.plugin.get_steps())
        emitted_tags = set()
        for step in steps:
            extra = step.extra
            self.assertIn("operation", extra)
            self.assertIn("tag", extra)
            self.assertEqual(extra["operation"], extra["tag"])
            emitted_tags.add(extra["tag"])
            py_line = self.plugin.get_line_for_tag("Python", extra["tag"])
            self.assertEqual(step.code_line, py_line)

        self.assertIn("INIT", emitted_tags)
        self.assertIn("LOOP_START", emitted_tags)
        self.assertIn("POLL_REQUESTS", emitted_tags)
        self.assertIn("SET_SIGNALS", emitted_tags)
        self.assertIn("PROCESS_CROSSINGS", emitted_tags)
        self.assertIn("CHECK_CONFLICTS", emitted_tags)
        self.assertIn("START_MOVEMENTS", emitted_tags)
        self.assertIn("ADVANCE_QUEUES", emitted_tags)
        self.assertIn("HOLD_TRAFFIC", emitted_tags)
        self.assertIn("COMPLETE", emitted_tags)

    def test_configurable_parameters(self):
        params = self.plugin.get_params()
        self.assertIsNotNone(params.get("ns_green_duration"))
        self.assertIsNotNone(params.get("ew_green_duration"))
        self.assertIsNotNone(params.get("yellow_duration"))
        self.assertIsNotNone(params.get("all_red_duration"))
        self.assertIsNotNone(params.get("ped_walk_duration"))
        self.assertIsNotNone(params.get("ped_clearance_duration"))
        self.assertIsNotNone(params.get("vehicles_per_approach"))
        self.assertIsNotNone(params.get("pedestrians_per_crossing"))
        self.assertIsNotNone(params.get("pedestrian_requests"))
        self.assertIsNotNone(params.get("cycles"))

        self.plugin.set_param("ped_walk_duration", 5)
        self.assertEqual(self.plugin.params.get("ped_walk_duration"), 5)

    def test_critical_safety_no_conflicting_vehicle_and_pedestrian_greens(self):
        """
        KRITIKUS BIZTONSÁGI INVARIÁNS:
        Egyetlen lépésben sem fordulhat elő, hogy egy járműirány és a vele ütköző
        gyalogosátkelő egyszerre zöld jelzést kap!
        NS jármű zöld esetén a North és South gyalogosátkelő SOHA nem kaphat zöldet.
        EW jármű zöld esetén az East és West gyalogosátkelő SOHA nem kaphat zöldet.
        Bármely gyalogos zöld jelzés esetén a konfliktáló járműirány SOHA nem kaphat zöldet/sárgát.
        """
        steps = list(self.plugin.get_steps())
        for step in steps:
            extra = step.extra
            v_lights = extra.get("vehicle_lights", {})
            p_lights = extra.get("pedestrian_lights", {})

            ns_veh_green = v_lights.get("ns", {}).get("green", False)
            ew_veh_green = v_lights.get("ew", {}).get("green", False)

            north_ped_green = p_lights.get("north", {}).get("green", False)
            south_ped_green = p_lights.get("south", {}).get("green", False)
            east_ped_green = p_lights.get("east", {}).get("green", False)
            west_ped_green = p_lights.get("west", {}).get("green", False)

            # 1. Jármű-jármű konfliktus kizárása
            self.assertFalse(
                ns_veh_green and ew_veh_green,
                f"Conflicting vehicle greens in step: {step.explanation}"
            )

            # 2. Jármű-gyalogos konfliktus kizárása
            if ns_veh_green:
                self.assertFalse(north_ped_green, f"Conflicting NS vehicle green and North ped green at {step.explanation}")
                self.assertFalse(south_ped_green, f"Conflicting NS vehicle green and South ped green at {step.explanation}")

            if ew_veh_green:
                self.assertFalse(east_ped_green, f"Conflicting EW vehicle green and East ped green at {step.explanation}")
                self.assertFalse(west_ped_green, f"Conflicting EW vehicle green and West ped green at {step.explanation}")

            # 3. Ha gyalogos zöld, a konfliktáló jármű kötelezően PIROS
            if north_ped_green or south_ped_green:
                self.assertTrue(v_lights.get("ns", {}).get("red", False))
                self.assertFalse(v_lights.get("ns", {}).get("green", False))
                self.assertFalse(v_lights.get("ns", {}).get("yellow", False))

            if east_ped_green or west_ped_green:
                self.assertTrue(v_lights.get("ew", {}).get("red", False))
                self.assertFalse(v_lights.get("ew", {}).get("green", False))
                self.assertFalse(v_lights.get("ew", {}).get("yellow", False))

    def test_pedestrian_cannot_enter_on_red_signal(self):
        """Gyalogos nem léphet be a zebrára (nem kezdheti meg az átkelést), ha a gyalogoslámpa PIROS."""
        steps = list(self.plugin.get_steps())
        for i in range(1, len(steps)):
            prev_peds = steps[i - 1].extra.get("pedestrians", {})
            cur_peds = steps[i].extra.get("pedestrians", {})
            cur_p_lights = steps[i].extra.get("pedestrian_lights", {})

            for c in ["north", "south", "east", "west"]:
                is_red = cur_p_lights.get(c, {}).get("red", False)
                is_green = cur_p_lights.get(c, {}).get("green", False)

                if is_red and not is_green:
                    for prev_p in prev_peds.get(c, []):
                        if prev_p["status"] in ("waiting", "queued"):
                            cur_p = next(p for p in cur_peds[c] if p["id"] == prev_p["id"])
                            self.assertNotEqual(
                                cur_p["status"],
                                "crossing",
                                f"Pedestrian {cur_p['id']} entered crosswalk {c} under RED signal!"
                            )

    def test_pedestrian_clearance_period_before_vehicle_release(self):
        """
        Biztonsági kiürítési időszak vizsgálata:
        A gyalogos zöld fázist gyalogos kiürítési fázis (PED_CLEARANCE) követi,
        ahol a gyalogos lámpa már piros, és a járművek még szigorúan pirosat kapnak.
        """
        steps = list(self.plugin.get_steps())
        ped_walk_seen = False
        ped_clear_seen = False

        for i, step in enumerate(steps):
            phase = step.extra.get("phase")
            if phase == "PED_WALK":
                ped_walk_seen = True
            elif phase == "PED_CLEARANCE":
                ped_clear_seen = True
                # A kiürítési időszak alatt az összes járműlámpának PIROSNAK kell lennie!
                v_lights = step.extra["vehicle_lights"]
                self.assertTrue(v_lights["ns"]["red"])
                self.assertTrue(v_lights["ew"]["red"])
                self.assertFalse(v_lights["ns"]["green"])
                self.assertFalse(v_lights["ew"]["green"])

        self.assertTrue(ped_walk_seen)
        self.assertTrue(ped_clear_seen)

    def test_deterministic_pedestrian_requests_and_duplicates(self):
        """Gyalogos igények kezelése: duplikációk szűrése, érvényes irányok rögzítése."""
        self.plugin.set_param("pedestrian_requests", "north,north,north, south , EAST,invalid_dir")
        steps = list(self.plugin.get_steps())
        init_step = steps[0]
        reqs = init_step.extra["pedestrian_requests"]

        self.assertTrue(reqs["north"])
        self.assertTrue(reqs["south"])
        self.assertTrue(reqs["east"])
        self.assertFalse(reqs["west"])
        self.assertNotIn("invalid_dir", reqs)

    def test_empty_requests_fallback(self):
        """Ha nincs megadva egyetlen igény sem, a szimuláció biztonságosan lefut hiba nélkül."""
        self.plugin.set_param("pedestrian_requests", "")
        steps = list(self.plugin.get_steps())
        self.assertGreater(len(steps), 0)
        self.assertEqual(steps[-1].extra["tag"], "COMPLETE")


class TestTrafficPedestrianIntegration(unittest.TestCase):
    """Integrációs és modulváltási tesztek a Phase 3-hoz."""

    def test_plugin_discovery_and_categorization(self):
        loader = PluginLoader()
        loader.load_all()

        p1 = loader.get_plugin("traffic_light")
        p2 = loader.get_plugin("traffic_intersection")
        p3 = loader.get_plugin("traffic_pedestrian_intersection")

        self.assertIsNotNone(p1, "Phase 1 plugin not found!")
        self.assertIsNotNone(p2, "Phase 2 plugin not found!")
        self.assertIsNotNone(p3, "Phase 3 plugin not found!")

        grouped = loader.list_plugins_grouped()
        self.assertIn("simulation", grouped)
        sim_ids = [p.id for p in grouped["simulation"]]
        self.assertIn("traffic_light", sim_ids)
        self.assertIn("traffic_intersection", sim_ids)
        self.assertIn("traffic_pedestrian_intersection", sim_ids)

    def test_engine_stepping_and_synchronization(self):
        loader = PluginLoader()
        loader.load_all()
        p3 = loader.get_plugin("traffic_pedestrian_intersection")

        engine = Engine()
        engine.set_plugin(p3)
        engine.generate_steps()
        self.assertGreater(len(engine.steps), 0)

        step1 = engine.next_step()
        self.assertIsNotNone(step1)
        self.assertEqual(engine.step_idx, 1)

        prev = engine.prev_step()
        self.assertIsNotNone(prev)
        self.assertEqual(engine.step_idx, 0)


if __name__ == "__main__":
    unittest.main()
