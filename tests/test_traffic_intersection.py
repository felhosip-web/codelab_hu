# -*- coding: utf-8 -*-
"""
Automated unit and integration tests for Traffic Light Educational Plugin Phase 2:
Vehicle Traffic Intersection (plugins/traffic_light/plugin.py & ui/traffic_intersection_widget.py).
Focuses on deterministic safety invariants, semantic source-line execution tracking,
multi-language alignment, and UI lifecycle.
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
    """Belső logika, állapotgép és biztonsági tesztek a kereszteződés szimulációhoz."""

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

    def test_semantic_operation_tags_in_all_languages(self):
        """Minden szemantikai művelet címkéjének léteznie és illeszkednie kell mind a 6 nyelven."""
        langs = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
        required_semantic_tags = [
            "INIT", "LOOP_START", "SET_SIGNALS", "PROCESS_CROSSING",
            "CHECK_CONFLICT", "START_VEHICLES", "ADVANCE_QUEUE",
            "CLEAR_INTERSECTION", "COMPLETE"
        ]

        exact_python_statements = {
            "INIT": "intersection = init_intersection(queues=vehicles_count)",
            "LOOP_START": "for cycle in range(1, total_cycles + 1):",
            "SET_SIGNALS": "set_traffic_signals(ns=phase.ns_signal, ew=phase.ew_signal)",
            "PROCESS_CROSSING": "advance_crossing_vehicles(intersection)",
            "CHECK_CONFLICT": "has_conflict = check_intersection_conflict(intersection, phase.active_direction)",
            "START_VEHICLES": "start_waiting_vehicle(intersection, phase.active_direction)",
            "ADVANCE_QUEUE": "advance_approach_queue(intersection, phase.active_direction)",
            "CLEAR_INTERSECTION": "clear_or_hold_vehicles(intersection)",
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
            # Ellenőrizzük, hogy a kód sor megfelel a megadott műveletnek
            py_line = self.plugin.get_line_for_tag("Python", extra["tag"])
            self.assertEqual(step.code_line, py_line)

        # Ellenőrizzük, hogy az ADVANCE_QUEUE és START_VEHICLES is kibocsátásra került
        self.assertIn("ADVANCE_QUEUE", emitted_tags, "ADVANCE_QUEUE must be emitted when queue advances!")
        self.assertIn("START_VEHICLES", emitted_tags, "START_VEHICLES must be emitted when a vehicle enters!")
        self.assertIn("SET_SIGNALS", emitted_tags, "SET_SIGNALS must be emitted during signal changes!")
        self.assertIn("PROCESS_CROSSING", emitted_tags, "PROCESS_CROSSING must be emitted during crossing traversal!")

    def test_target_statements_in_all_six_languages(self):
        """Minden nyelven ellenőrizzük a szemantikai utasítások pontos szövegét, nemcsak Pythonban."""
        expected_fragments = {
            "Python": {
                "INIT": "init_intersection(queues=vehicles_count)",
                "LOOP_START": "for cycle in range(1, total_cycles + 1):",
                "SET_SIGNALS": "set_traffic_signals(",
                "PROCESS_CROSSING": "advance_crossing_vehicles(",
                "CHECK_CONFLICT": "check_intersection_conflict(",
                "START_VEHICLES": "start_waiting_vehicle(",
                "ADVANCE_QUEUE": "advance_approach_queue(",
                "CLEAR_INTERSECTION": "clear_or_hold_vehicles(",
                "COMPLETE": "finish_simulation(",
            },
            "C++": {
                "INIT": "initIntersection(vehiclesCount)",
                "LOOP_START": "for (int cycle = 1; cycle <= totalCycles; ++cycle)",
                "SET_SIGNALS": "setTrafficSignals(",
                "PROCESS_CROSSING": "advanceCrossingVehicles(",
                "CHECK_CONFLICT": "checkIntersectionConflict(",
                "START_VEHICLES": "startWaitingVehicle(",
                "ADVANCE_QUEUE": "advanceApproachQueue(",
                "CLEAR_INTERSECTION": "clearOrHoldVehicles(",
                "COMPLETE": "finishSimulation(",
            },
            "C": {
                "INIT": "init_intersection(vehicles_count)",
                "LOOP_START": "for (cycle = 1; cycle <= total_cycles; cycle++)",
                "SET_SIGNALS": "set_traffic_signals(",
                "PROCESS_CROSSING": "advance_crossing_vehicles(",
                "CHECK_CONFLICT": "check_intersection_conflict(",
                "START_VEHICLES": "start_waiting_vehicle(",
                "ADVANCE_QUEUE": "advance_approach_queue(",
                "CLEAR_INTERSECTION": "clear_or_hold_vehicles(",
                "COMPLETE": "finish_simulation(",
            },
            "BASIC": {
                "INIT": "CALL InitIntersection(VehiclesCount)",
                "LOOP_START": "FOR CYCLE = 1 TO TOTALCYCLES",
                "SET_SIGNALS": "CALL SetTrafficSignals(",
                "PROCESS_CROSSING": "CALL AdvanceCrossingVehicles",
                "CHECK_CONFLICT": "CheckIntersectionConflict(",
                "START_VEHICLES": "CALL StartWaitingVehicle(",
                "ADVANCE_QUEUE": "CALL AdvanceApproachQueue(",
                "CLEAR_INTERSECTION": "CALL ClearOrHoldVehicles",
                "COMPLETE": "CALL FinishSimulation",
            },
            "Java": {
                "INIT": "initIntersection(vehiclesCount)",
                "LOOP_START": "for (int cycle = 1; cycle <= totalCycles; cycle++)",
                "SET_SIGNALS": "setTrafficSignals(",
                "PROCESS_CROSSING": "advanceCrossingVehicles(",
                "CHECK_CONFLICT": "checkIntersectionConflict(",
                "START_VEHICLES": "startWaitingVehicle(",
                "ADVANCE_QUEUE": "advanceApproachQueue(",
                "CLEAR_INTERSECTION": "clearOrHoldVehicles(",
                "COMPLETE": "finishSimulation(",
            },
            "Pascal": {
                "INIT": "InitIntersection(vehiclesCount)",
                "LOOP_START": "for cycle := 1 to totalCycles do",
                "SET_SIGNALS": "SetTrafficSignals(",
                "PROCESS_CROSSING": "AdvanceCrossingVehicles(",
                "CHECK_CONFLICT": "CheckIntersectionConflict(",
                "START_VEHICLES": "StartWaitingVehicle(",
                "ADVANCE_QUEUE": "AdvanceApproachQueue(",
                "CLEAR_INTERSECTION": "ClearOrHoldVehicles(",
                "COMPLETE": "FinishSimulation(",
            },
        }

        for lang, tags in expected_fragments.items():
            code_lines = self.plugin.get_code(lang).splitlines()
            for tag, fragment in tags.items():
                line_no = self.plugin.get_line_for_tag(lang, tag)
                self.assertGreater(line_no, 0, f"Missing {tag} in {lang}")
                self.assertLessEqual(line_no, len(code_lines))
                line_text = code_lines[line_no - 1]
                self.assertIn(
                    fragment,
                    line_text,
                    f"Line {line_no} in {lang} does not contain expected fragment '{fragment}': '{line_text}'"
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

    def test_no_vehicle_enters_on_red_signal(self):
        """1. Safety Invariant: egyetlen jármű sem léphet be, ha az iránya PIROS."""
        steps = list(self.plugin.get_steps())
        for step in steps:
            extra = step.extra
            lights = extra.get("lights", {})
            vehicles = extra.get("vehicles", {})

            ns_red = lights.get("ns", {}).get("red", False)
            ns_green = lights.get("ns", {}).get("green", False)
            ew_red = lights.get("ew", {}).get("red", False)
            ew_green = lights.get("ew", {}).get("green", False)

            if ns_red and not ns_green:
                for d in ["north", "south"]:
                    for v in vehicles.get(d, []):
                        if v["status"] == "waiting":
                            self.assertEqual(v["queue_pos"], 0, "Waiting vehicle advanced past stopline on RED!")
                        self.assertNotEqual(v["crossing_progress"], 1, "Vehicle entered intersection on RED!")

            if ew_red and not ew_green:
                for d in ["east", "west"]:
                    for v in vehicles.get(d, []):
                        if v["status"] == "waiting":
                            self.assertEqual(v["queue_pos"], 0, "Waiting vehicle advanced past stopline on RED!")
                        self.assertNotEqual(v["crossing_progress"], 1, "Vehicle entered intersection on RED!")

    def test_crossing_vehicles_safely_clear_during_yellow_and_all_red(self):
        """2. Safety Invariant: a korábban belépett járművek biztonságosan kiürítenek sárga és piros fázis alatt."""
        steps = list(self.plugin.get_steps())
        for i in range(1, len(steps)):
            prev_step = steps[i - 1]
            cur_step = steps[i]
            prev_crossing = [
                v["id"] for d in prev_step.extra["vehicles"] for v in prev_step.extra["vehicles"][d]
                if v["status"] == "crossing"
            ]
            if prev_crossing:
                # A következő lépésben vagy halad előre (crossing_progress nő), vagy távozott (departed)
                for v_id in prev_crossing:
                    cur_v = next(
                        v for d in cur_step.extra["vehicles"] for v in cur_step.extra["vehicles"][d]
                        if v["id"] == v_id
                    )
                    self.assertIn(cur_v["status"], ("crossing", "departed"))
                    if cur_v["status"] == "crossing":
                        self.assertGreater(cur_v["crossing_progress"], 0)

    def test_no_conflicting_intersection_occupancy(self):
        """3. Safety Invariant: merőleges irányok (É-D és K-Ny) SOHA nem tartózkodhatnak egyszerre a kereszteződésben."""
        steps = list(self.plugin.get_steps())
        for step in steps:
            vehicles = step.extra.get("vehicles", {})
            ns_crossing = any(v["status"] == "crossing" for d in ["north", "south"] for v in vehicles.get(d, []))
            ew_crossing = any(v["status"] == "crossing" for d in ["east", "west"] for v in vehicles.get(d, []))
            self.assertFalse(
                ns_crossing and ew_crossing,
                f"Conflicting intersection occupancy! NS and EW both crossing at step: {step.explanation}"
            )

    def test_same_axis_opposing_movements_follow_lane_model(self):
        """4. Safety Invariant: az azonos tengelyen lévő szemközti járművek (pl. Észak és Dél) külön sávban haladnak."""
        steps = list(self.plugin.get_steps())
        for step in steps:
            vehicles = step.extra.get("vehicles", {})
            n_crossing = [v for v in vehicles.get("north", []) if v["status"] == "crossing"]
            s_crossing = [v for v in vehicles.get("south", []) if v["status"] == "crossing"]
            for nv in n_crossing:
                self.assertEqual(nv["direction"], "north")
            for sv in s_crossing:
                self.assertEqual(sv["direction"], "south")

    def test_queue_advancement_maintains_valid_contiguous_indices(self):
        """5. Safety Invariant: a járműsor sosem tartalmazhat duplikált, negatív pozíciókat, és tick végére rendezett."""
        steps = list(self.plugin.get_steps())
        for step in steps:
            vehicles = step.extra.get("vehicles", {})
            for d in ["north", "south", "east", "west"]:
                q_positions = [v["queue_pos"] for v in vehicles.get(d, []) if v["status"] in ("waiting", "queued")]
                self.assertEqual(len(q_positions), len(set(q_positions)), f"Duplicate queue positions in {d}")
                # A sorban álló járművek indexei nem lehetnek negatívak
                self.assertTrue(all(p >= 0 for p in q_positions))
                # Tick befejező állapotban (nem közbenső START_VEHICLES) a sor folytonos 0-tól kezdődően
                if step.extra.get("tag") != "START_VEHICLES" and q_positions:
                    self.assertEqual(sorted(q_positions), list(range(len(q_positions))), f"Non-contiguous queue in {d}")

    def test_ordered_semantic_events_within_simulation_tick(self):
        """Teszteli a szimulációs ticken belüli szemantikai események szigorú végrehajtási sorrendjét."""
        steps = list(self.plugin.get_steps())
        tags = [s.extra["tag"] for s in steps]

        # Keressünk egy zöld ciklust, ahol járművek mozognak és a sor előrelép
        # A sorrendnek PROCESS_CROSSING -> CHECK_CONFLICT -> START_VEHICLES -> ADVANCE_QUEUE kell lennie
        subseq = []
        for i in range(len(tags) - 3):
            window = tags[i:i+4]
            if window == ["PROCESS_CROSSING", "CHECK_CONFLICT", "START_VEHICLES", "ADVANCE_QUEUE"]:
                subseq.append(window)

        self.assertGreater(len(subseq), 0, "Ordered sub-events sequence not found in simulation run!")

    def test_transition_based_red_light_entry_prevention(self):
        """Szigorú átmenet-alapú teszt: ellenőrzi járműveket lépésről lépésre, hogy piros alatt nem lépnek be."""
        steps = list(self.plugin.get_steps())
        for i in range(1, len(steps)):
            prev_step = steps[i - 1]
            cur_step = steps[i]
            prev_vehicles = prev_step.extra["vehicles"]
            cur_vehicles = cur_step.extra["vehicles"]
            cur_lights = cur_step.extra["lights"]

            # Ha É-D piros (és nincs zöld/sárga)
            if cur_lights["ns"]["red"] and not cur_lights["ns"]["green"] and not cur_lights["ns"]["yellow"]:
                for d in ["north", "south"]:
                    for pv in prev_vehicles[d]:
                        if pv["status"] in ("waiting", "queued"):
                            cv = next(v for v in cur_vehicles[d] if v["id"] == pv["id"])
                            self.assertNotEqual(cv["status"], "crossing", f"Vehicle {cv['id']} entered intersection under RED!")
                            self.assertEqual(cv["crossing_progress"], 0)

            # Ha K-Ny piros (és nincs zöld/sárga)
            if cur_lights["ew"]["red"] and not cur_lights["ew"]["green"] and not cur_lights["ew"]["yellow"]:
                for d in ["east", "west"]:
                    for pv in prev_vehicles[d]:
                        if pv["status"] in ("waiting", "queued"):
                            cv = next(v for v in cur_vehicles[d] if v["id"] == pv["id"])
                            self.assertNotEqual(cv["status"], "crossing", f"Vehicle {cv['id']} entered intersection under RED!")
                            self.assertEqual(cv["crossing_progress"], 0)

    def test_no_conflicting_green_signals(self):
        """Kritikus jelzőlámpa teszt: merőleges irányok sosem kaphatnak egyszerre zöldet."""
        steps = list(self.plugin.get_steps())
        for step in steps:
            lights = step.extra.get("lights", {})
            ns = lights.get("ns", {})
            ew = lights.get("ew", {})
            self.assertFalse(ns.get("green", False) and ew.get("green", False))
            self.assertFalse(ns.get("green", False) and ew.get("yellow", False))
            self.assertFalse(ew.get("green", False) and ns.get("yellow", False))

    def test_all_vehicles_eventually_clear_with_sufficient_cycles(self):
        """8. Safety Invariant: elegendő zöldidő és ciklus esetén minden jármű átjut a kereszteződésen."""
        self.plugin.set_param("vehicles_per_approach", 2)
        self.plugin.set_param("ns_green_duration", 3)
        self.plugin.set_param("ew_green_duration", 3)
        self.plugin.set_param("cycles", 3)

        steps = list(self.plugin.get_steps())
        final_step = steps[-1]
        final_vehicles = final_step.extra["vehicles"]

        total_vehicles = sum(len(final_vehicles[d]) for d in final_vehicles)
        departed_vehicles = sum(
            1 for d in final_vehicles for v in final_vehicles[d] if v["status"] == "departed"
        )
        self.assertEqual(
            departed_vehicles,
            total_vehicles,
            f"Expected all {total_vehicles} vehicles to depart, but only {departed_vehicles} departed."
        )


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

    def test_engine_stepping_and_synchronization(self):
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
    def test_main_window_module_switching_and_language_tracking(self):
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

        # 3. Nyelvváltás ellenőrzése futás közben: szimulációs lépés nem változik, a kiemelt sor nyelvenként megfelel
        win.next_step()
        cur_idx = win.current_step_idx
        current_step = win.steps[cur_idx]
        cur_tag = current_step.extra["tag"]

        for lang in ["Python", "C++", "C", "BASIC", "Java", "Pascal"]:
            win.lang_combo.setCurrentText(lang)
            win.on_language_changed(lang)
            self.app.processEvents()
            # Index megmarad
            self.assertEqual(win.current_step_idx, cur_idx)
            # A feloldott sor az adott nyelvhez tartozó sorszám
            expected_line = p2.get_line_for_tag(lang, cur_tag)
            resolved_line = win.resolve_step_code_line(current_step, lang)
            self.assertEqual(resolved_line, expected_line)

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
