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
        self.plugin.runtime_requests.clear()
        self.plugin.runtime_next_cycle_requests.clear()

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
        self.plugin.set_param("pedestrian_requests", "north,south")
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
        """
        self.plugin.set_param("pedestrian_requests", "north,south,east,west")
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

            # Jármű-jármű konfliktus kizárása
            self.assertFalse(ns_veh_green and ew_veh_green, f"Conflicting vehicle greens in step: {step.explanation}")

            # Jármű-gyalogos konfliktus kizárása
            if ns_veh_green:
                self.assertFalse(north_ped_green, f"Conflicting NS vehicle green and North ped green at {step.explanation}")
                self.assertFalse(south_ped_green, f"Conflicting NS vehicle green and South ped green at {step.explanation}")

            if ew_veh_green:
                self.assertFalse(east_ped_green, f"Conflicting EW vehicle green and East ped green at {step.explanation}")
                self.assertFalse(west_ped_green, f"Conflicting EW vehicle green and West ped green at {step.explanation}")

            # Ha gyalogos zöld, a konfliktáló jármű kötelezően PIROS
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
        self.plugin.set_param("pedestrian_requests", "north,east")
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
        self.plugin.set_param("pedestrian_requests", "north,south")
        steps = list(self.plugin.get_steps())
        ped_walk_seen = False
        ped_clear_seen = False

        for step in steps:
            phase = step.extra.get("phase")
            if phase == "PED_WALK":
                ped_walk_seen = True
            elif phase == "PED_CLEARANCE":
                ped_clear_seen = True
                v_lights = step.extra["vehicle_lights"]
                self.assertTrue(v_lights["ns"]["red"])
                self.assertTrue(v_lights["ew"]["red"])
                self.assertFalse(v_lights["ns"]["green"])
                self.assertFalse(v_lights["ew"]["green"])

        self.assertTrue(ped_walk_seen)
        self.assertTrue(ped_clear_seen)

    def test_no_request_policy_skips_pedestrian_phase(self):
        """Ha nincs gyalogos kérelem, a gyalogos fázis nem kerül ütemezésre."""
        self.plugin.set_param("pedestrian_requests", "")
        steps = list(self.plugin.get_steps())
        phases = set(s.extra.get("phase") for s in steps)
        self.assertNotIn("PED_WALK", phases)
        self.assertNotIn("PED_CLEARANCE", phases)
        self.assertIn("NS_GREEN", phases)
        self.assertIn("EW_GREEN", phases)
        self.assertEqual(steps[-1].extra["tag"], "COMPLETE")

    def test_runtime_request_delivery_and_future_regeneration(self):
        """
        P0 Teszt: Valós idejű kérelem érkezése az aktív szimulációhoz.
        Kezdetben nincs kérés -> szimuláció elindul -> kérés érkezik -> jövőbeli fázisban
        automatikusan megjelenik a gyalogos zöld fázis!
        """
        self.plugin.set_param("pedestrian_requests", "")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        init_len = len(engine.steps)
        self.assertFalse(any(s.extra.get("phase") == "PED_WALK" for s in engine.steps))

        # Haladunk 6 lépést (jármű fázisban járunk)
        for _ in range(6):
            engine.next_step()

        curr_phase = engine.steps[engine.step_idx].extra["phase"]
        self.assertEqual(curr_phase, "NS_GREEN")

        # Runtime hívógomb megnyomása Észak átkelőre
        success = self.plugin.register_pedestrian_request("north", engine=engine)
        self.assertTrue(success)

        # A jövőbeli lépések most már tartalmazzák a gyalogos fázist
        future_steps = engine.steps[engine.step_idx + 1:]
        future_phases = set(s.extra.get("phase") for s in future_steps)
        self.assertIn("PED_WALK", future_phases)
        self.assertIn("PED_CLEARANCE", future_phases)

        # Ellenőrizzük, hogy a hívógomb jelzése aktív a kiszolgálásig (1. ciklusban a PED_WALK előtt)
        for s in future_steps:
            if s.extra.get("cycle") == 1 and s.extra.get("phase") in ("NS_GREEN", "NS_YELLOW", "CLEARANCE_1", "EW_GREEN", "EW_YELLOW", "CLEARANCE_2"):
                self.assertTrue(s.extra.get("pedestrian_requests", {}).get("north", False))

    def test_repeated_and_simultaneous_requests(self):
        """Többszöri és egyidejű kérések determinisztikus kezelése."""
        self.plugin.set_param("pedestrian_requests", "")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Ismételt kattintás ugyanarra az átkelőre nem duplikál
        self.plugin.register_pedestrian_request("south", engine=engine)
        self.plugin.register_pedestrian_request("south", engine=engine)
        self.plugin.register_pedestrian_request("south", engine=engine)

        self.assertEqual(self.plugin.runtime_requests, {"south"})

        # Egyidejű kérések több átkelőről
        self.plugin.register_pedestrian_request("west", engine=engine)
        self.assertEqual(self.plugin.runtime_requests, {"south", "west"})

    def test_request_during_active_crossing_queued_for_next_cycle(self):
        """
        Ha egy átkelő már zöldben van (aktív átkelés zajlik), az újabb gombnyomást
        a következő ciklusra kell ütemezni, nem szakíthatja meg vagy hosszabbíthatja meg
        szabálytalanul a jelenlegi fázist.
        """
        self.plugin.set_param("pedestrian_requests", "north")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Megkeressük az első PED_WALK lépést
        walk_idx = next(i for i, s in enumerate(engine.steps) if s.extra.get("phase") == "PED_WALK")
        engine.step_idx = walk_idx

        # Kérés érkezik 'north' átkelőre az aktív zöld alatt
        self.plugin.register_pedestrian_request("north", engine=engine)
        self.assertIn("north", self.plugin.runtime_next_cycle_requests)


class TestTrafficPedestrianIntegration(unittest.TestCase):
    """Integrációs, motor és felületi tesztek."""

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

    def test_engine_register_pedestrian_request_method(self):
        """Engine.register_pedestrian_request() sikeresen delegál az aktív pluginhoz."""
        loader = PluginLoader()
        loader.load_all()
        p3 = loader.get_plugin("traffic_pedestrian_intersection")

        engine = Engine()
        engine.set_plugin(p3)
        engine.generate_steps()

        res = engine.register_pedestrian_request("east")
        self.assertTrue(res)
        self.assertIn("east", p3.runtime_requests)

    @unittest.skipUnless(HAS_QT, "PySide6 required for UI testing")
    def test_widget_interactive_buttons(self):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        app = QApplication.instance() or QApplication([])

        widget = TrafficPedestrianIntersectionViewerWidget()
        plugin = TrafficPedestrianIntersectionPlugin()
        engine = Engine()
        engine.set_plugin(plugin)
        engine.generate_steps()

        widget.set_plugin(plugin)
        widget.set_engine(engine)

        received_requests = []
        widget.request_made.connect(lambda c: received_requests.append(c))

        # Kattintunk a panelen lévő Észak gombra
        widget.btn_north.click()
        self.assertIn("north", received_requests)
        self.assertIn("north", plugin.runtime_requests)

        # Kattintunk a vászon gombra
        widget.canvas.crossing_requested.emit("south")
        self.assertIn("south", received_requests)
        self.assertIn("south", plugin.runtime_requests)

        widget.deleteLater()


if __name__ == "__main__":
    unittest.main()


class TestRealApplicationIntegration(unittest.TestCase):
    """
    Közvetlen alkalmazás-szintű integrációs tesztek a valós idejű
    gombnyomási eseményfolyamat (Button -> Plugin -> Engine -> MainWindow) igazolására.
    """

    def setUp(self):
        if HAS_QT:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            self.app = QApplication.instance() or QApplication([])
        else:
            self.app = None

    @unittest.skipUnless(HAS_QT, "PySide6 szükséges a MainWindow integrációs tesztekhez")
    def test_complete_button_to_engine_to_mainwindow_event_path(self):
        from ui.main_window import MainWindow

        win = MainWindow()
        win.show()
        self.app.processEvents()

        # Átváltunk a Phase 3 pluginra
        p3 = win.plugin_loader.get_plugin("traffic_pedestrian_intersection")
        self.assertIsNotNone(p3)
        win.current_plugin = p3
        win.update_active_visualizer()
        win.reset()
        self.app.processEvents()

        # 1. Kezdeti állapot: nincs kérés, steps nem tartalmaz PED_WALK-ot
        self.assertFalse(any(s.extra.get("phase") == "PED_WALK" for s in win.engine.steps))
        initial_steps_ref = win.engine.steps

        # 2. Elindítjuk a szimulációt és léptetünk néhányat jármű zöld fázisba
        for _ in range(5):
            win.next_step()
            self.app.processEvents()

        curr_idx = win.current_step_idx
        self.assertEqual(curr_idx, 5)
        self.assertEqual(win.engine.step_idx, 5)

        # 3. Valós gombkattintás a vezérlőpanelen (pl. Észak gomb)
        active_viewer = win.viz_stack.currentWidget()
        self.assertIsInstance(active_viewer, TrafficPedestrianIntersectionViewerWidget)

        # Kattintunk a valós QPushButton widgetre
        active_viewer.btn_north.click()
        self.app.processEvents()

        # 4. Ellenőrizzük az event ordering és synchronization szabályokat:
        # A plugin megkapta a kérést:
        self.assertIn("north", p3.runtime_requests)

        # Az Engine steps listája újragenerálódott a jövőre:
        self.assertIsNot(win.engine.steps, initial_steps_ref)
        self.assertIn("PED_WALK", [s.extra.get("phase") for s in win.engine.steps])

        # A MainWindow steps referenciája szinkronban van az Engine-nel:
        self.assertIs(win.steps, win.engine.steps)

        # A végrehajtási pozíció nem ugrott el, a jelenlegi lépésindex változatlan:
        self.assertEqual(win.current_step_idx, curr_idx)
        self.assertEqual(win.engine.step_idx, curr_idx)

        # A progress csúszka maximuma frissült az új jövőbeli lépések hosszára:
        self.assertEqual(win.bottom_progress_slider.maximum(), len(win.steps) - 1)

        # 5. Következő lépés végrehajtása az új jövőbeli sorozatból származik
        next_step = win.engine.next_step()
        win.show_step(next_step)
        self.app.processEvents()
        self.assertEqual(win.engine.step_idx, curr_idx + 1)
        self.assertIn(next_step, win.steps)

        win.close()
        win.deleteLater()


class TestPedestrianSchedulingAndLifecycle(unittest.TestCase):
    """
    Részletes tesztek a kérelmek életciklusára, kiszolgálására, újragenerálására,
    aktív átkelés alatti ütemezésére és befejezési határviselkedésére.
    """

    def setUp(self):
        self.plugin = TrafficPedestrianIntersectionPlugin()
        self.plugin.runtime_requests.clear()
        self.plugin.runtime_next_cycle_requests.clear()

    def test_request_served_exactly_once_and_not_resurrected(self):
        """1. és 2. és 3.: Kérelem pontosan egyszer fut le, nem éled újra újrageneráláskor."""
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # 1. ciklusban Észak kérése
        self.plugin.register_pedestrian_request("north", engine=engine)

        # Átlépünk a 2. ciklus NS_GREEN fázisába (ahol a cycle 1 PED_WALK már lefutott)
        while not (engine.steps[engine.step_idx].extra.get("cycle") == 2 and engine.steps[engine.step_idx].extra.get("phase") == "NS_GREEN"):
            engine.next_step()

        c2_idx = engine.step_idx
        self.assertEqual(engine.steps[c2_idx].extra["cycle"], 2)

        # Új kérés érkezik Keletre
        self.plugin.register_pedestrian_request("east", engine=engine)

        # A 2. ciklus PED_WALK fázisában KIZÁRÓLAG Kelet kap zöldet, Észak SOHA nem kap újra zöldet!
        c2_walk = [s for s in engine.steps[c2_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0)
        for s in c2_walk:
            p_lights = s.extra["pedestrian_lights"]
            self.assertTrue(p_lights["east"]["green"])
            self.assertFalse(p_lights["north"]["green"], "North must not be resurrected after being served in cycle 1!")

    def test_during_north_walk_south_request_queued_for_next_cycle(self):
        """5. és 7.: Északi gyalogos zöld alatt érkező Déli kérés a következő ciklusra kerül."""
        self.plugin.set_param("pedestrian_requests", "north")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Átlépünk PED_WALK-ba
        while engine.steps[engine.step_idx].extra.get("phase") != "PED_WALK":
            engine.next_step()

        curr_idx = engine.step_idx
        self.assertEqual(engine.steps[curr_idx].extra["phase"], "PED_WALK")
        self.assertTrue(engine.steps[curr_idx].extra["pedestrian_lights"]["north"]["green"])
        self.assertFalse(engine.steps[curr_idx].extra["pedestrian_lights"]["south"]["green"])

        # Kérés érkezik Délre az aktív átkelés alatt
        self.plugin.register_pedestrian_request("south", engine=engine)

        # Az aktuális 1. ciklus hátralévő lépéseiben Dél NEM kaphat zöldet
        rem_c1_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 1 and s.extra.get("phase") == "PED_WALK"]
        for s in rem_c1_walk:
            p_lights = s.extra["pedestrian_lights"]
            self.assertTrue(p_lights["north"]["green"])
            self.assertFalse(p_lights["south"]["green"])

        # A 2. ciklusban Dél megkapja a zöldet
        c2_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0)
        for s in c2_walk:
            self.assertTrue(s.extra["pedestrian_lights"]["south"]["green"])

    def test_during_north_walk_another_north_request_queued_for_next_cycle(self):
        """6.: Északi gyalogos zöld alatt érkező újabb Északi kérés a következő ciklusra kerül."""
        self.plugin.set_param("pedestrian_requests", "north")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        while engine.steps[engine.step_idx].extra.get("phase") != "PED_WALK":
            engine.next_step()

        curr_idx = engine.step_idx
        # Újabb északi kérés az aktív zöld alatt
        self.plugin.register_pedestrian_request("north", engine=engine)
        self.assertIn("north", self.plugin.runtime_next_cycle_requests)

        # A 2. ciklusban ismét zöldet kap Észak
        c2_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0)
        for s in c2_walk:
            self.assertTrue(s.extra["pedestrian_lights"]["north"]["green"])

    def test_no_request_discarded_at_final_cycle_boundary(self):
        """8. és 13.: A végső ciklusban vagy annak határán érkező kérések nem vesznek el, ciklusbővítéssel kiszolgálódnak."""
        self.plugin.set_param("pedestrian_requests", "")
        self.plugin.set_param("cycles", 2)
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Eljutunk a 2. ciklus CLEARANCE_2 fázisáig
        while not (engine.steps[engine.step_idx].extra.get("cycle") == 2 and engine.steps[engine.step_idx].extra.get("phase") == "CLEARANCE_2"):
            engine.next_step()

        curr_idx = engine.step_idx
        # A 2. ciklus legvégén kérés érkezik 'west'-re
        self.plugin.register_pedestrian_request("west", engine=engine)

        # A szimuláció azonnal ütemezi a gyalogos zöld fázist Nyugatra
        future_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(future_walk), 0)
        for s in future_walk:
            self.assertTrue(s.extra["pedestrian_lights"]["west"]["green"])

    def test_reset_does_not_resurrect_stale_requests(self):
        """10.: A reset / újragenerálás tiszta kezdőállapotot hoz létre."""
        self.plugin.set_param("pedestrian_requests", "")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Futás közben kérés érkezik
        self.plugin.register_pedestrian_request("east", engine=engine)
        self.assertIn("east", self.plugin.runtime_requests)

        # Meghívjuk a generate_steps() reset-et
        engine.generate_steps()

        # A futásidejű kérések kiürültek, nincsenek maradvány kérések
        self.assertEqual(len(self.plugin.runtime_requests), 0)
        self.assertFalse(any(s.extra.get("phase") == "PED_WALK" for s in engine.steps))


class TestClearancePhaseAndPersistentConsistency(unittest.TestCase):
    """
    Kifejezett regressziós tesztek a kiürítési fázisok alatt érkező kérelmekre (PED_CLEARANCE,
    CLEARANCE_3), valamint a perzisztens kérelemállapot és a jövőbeli lépések összhangjára.
    """

    def setUp(self):
        self.plugin = TrafficPedestrianIntersectionPlugin()
        self.plugin.runtime_requests.clear()
        self.plugin.runtime_next_cycle_requests.clear()

    def test_request_during_ped_clearance_queued_for_next_cycle(self):
        """
        PED_CLEARANCE alatt érkező kérelem:
        - A kérelem a következő ciklusra kerül (next_cycle_requests).
        - Nem módosítja a már lefutott gyalogos zöld fázist.
        - Nem vezet be gyalogos zöldet a kiürítés alatt (minden gyalogoslámpa PIROS marad).
        - A kérelem a következő ciklusban zöldet kap, és pontosan egyszer fut le.
        """
        self.plugin.set_param("pedestrian_requests", "north")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Eljutunk PED_CLEARANCE fázisba (ahol Észak már megkapta a zöldjét)
        while engine.steps[engine.step_idx].extra.get("phase") != "PED_CLEARANCE":
            engine.next_step()

        curr_idx = engine.step_idx
        curr_step = engine.steps[curr_idx]
        self.assertEqual(curr_step.extra["phase"], "PED_CLEARANCE")

        # PED_CLEARANCE alatt minden gyalogos jelzésnek pirosnak kell lennie
        for c in ["north", "south", "east", "west"]:
            self.assertFalse(curr_step.extra["pedestrian_lights"][c]["green"])

        # Kérelem érkezik Nyugatra (különbözik a korábban kiszolgált Északtól)
        self.plugin.register_pedestrian_request("west", engine=engine)

        # 1. A kérelem a következő ciklusra került
        self.assertIn("west", self.plugin.runtime_next_cycle_requests)

        # 2. A jelenlegi 1. ciklus hátralévő lépéseiben (beleértve a CLEARANCE_3-at) SEMMILYEN gyalogos zöld nem jelenhet meg!
        rem_steps_c1 = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 1]
        for s in rem_steps_c1:
            p_lights = s.extra["pedestrian_lights"]
            for c in ["north", "south", "east", "west"]:
                self.assertFalse(
                    p_lights[c]["green"],
                    f"Pedestrian green appeared during clearance in cycle 1: {s.extra['phase']}"
                )

        # 3. A következő 2. ciklusban Nyugat megkapja a zöldet
        c2_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0, "Cycle 2 must schedule PED_WALK for west!")
        for s in c2_walk:
            p_lights = s.extra["pedestrian_lights"]
            self.assertTrue(p_lights["west"]["green"], "West must receive green in cycle 2!")
            self.assertFalse(p_lights["north"]["green"], "North was already served in cycle 1, must not reappear!")

    def test_request_during_clearance_3_queued_for_next_cycle(self):
        """
        CLEARANCE_3 alatt érkező kérelem:
        - A kérelem a következő ciklusra kerül.
        - Nem vezet be gyalogos zöldet a kiürítés alatt (minden jelzés PIROS).
        - A kérelem a következő ciklusban zöldet kap, és pontosan egyszer fut le.
        """
        self.plugin.set_param("pedestrian_requests", "south")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        while engine.steps[engine.step_idx].extra.get("phase") != "CLEARANCE_3":
            engine.next_step()

        curr_idx = engine.step_idx
        curr_step = engine.steps[curr_idx]
        self.assertEqual(curr_step.extra["phase"], "CLEARANCE_3")

        # Kérelem érkezik Keletre
        self.plugin.register_pedestrian_request("east", engine=engine)
        self.assertIn("east", self.plugin.runtime_next_cycle_requests)

        # A jelenlegi CLEARANCE_3 alatt tilos bármilyen zöld fény
        rem_c1 = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 1]
        for s in rem_c1:
            for c in ["north", "south", "east", "west"]:
                self.assertFalse(s.extra["pedestrian_lights"][c]["green"])

        # A 2. ciklusban Kelet zöldet kap
        c2_walk = [s for s in engine.steps[curr_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0)
        for s in c2_walk:
            self.assertTrue(s.extra["pedestrian_lights"]["east"]["green"])
            self.assertFalse(s.extra["pedestrian_lights"]["south"]["green"])

    def test_persistent_state_and_future_steps_consistency_after_service(self):
        """
        Igazolja, hogy a kiszolgált kérelem kikerül a perzisztens runtime állapotból,
        és egy későbbi újragenerálás vagy regisztráció során nem jelenik meg újra.
        """
        self.plugin.set_param("pedestrian_requests", "north")
        engine = Engine()
        engine.set_plugin(self.plugin)
        engine.generate_steps()

        # Kezdetben Észak benne van a perzisztens runtime_requests-ben
        self.assertIn("north", self.plugin.runtime_requests)

        # Végrehajtjuk a lépéseket a PED_WALK-on keresztül
        while not (engine.steps[engine.step_idx].extra.get("cycle") == 2 and engine.steps[engine.step_idx].extra.get("phase") == "NS_GREEN"):
            s = engine.next_step()
            self.plugin.sync_from_executed_step(s)

        # A kiszolgálás után a perzisztens runtime_requests-ből Észak törlődött
        self.assertNotIn("north", self.plugin.runtime_requests)

        # Regisztrálunk egy új kérelmet Délre
        self.plugin.register_pedestrian_request("south", engine=engine)

        # A 2. ciklus gyalogos fázisában KIZÁRÓLAG Dél jelenik meg, Észak nem éled újra!
        c2_walk = [s for s in engine.steps[engine.step_idx:] if s.extra.get("cycle") == 2 and s.extra.get("phase") == "PED_WALK"]
        self.assertGreater(len(c2_walk), 0)
        for s in c2_walk:
            self.assertTrue(s.extra["pedestrian_lights"]["south"]["green"])
            self.assertFalse(s.extra["pedestrian_lights"]["north"]["green"])
