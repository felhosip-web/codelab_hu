# -*- coding: utf-8 -*-
"""
Traffic Light Educational Plugin - Phase 1 & Phase 2
Oktatási jelzőlámpa és forgalmi kereszteződés szimuláció valós idejű
kód- és végrehajtássor-követéssel mind a 6 támogatott programozási nyelven.
A forrássorok és logikai lépések összerendelése karbantartható inline címkékből
származtatott (nem törékeny, kézzel számolt sorpozíciókból).
"""
import re
from typing import Dict, Generator, List, Optional, Tuple, Any
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

TAG_PATTERN = re.compile(
    r"""(?:\s*(?:#|//|'|/\*)\s*\[TAG:([A-Za-z0-9_]+)\]\s*(?:\*/)?|\s*\[TAG:([A-Za-z0-9_]+)\])"""
)


def _process_code_templates(raw_templates: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, Dict[str, int]]]:
    """
    Feldolgozza a sablonokat: eltávolítja az inline [TAG:XYZ] címkéket,
    és felépíti a nyelvekhez tartozó címke -> 1-alapú sorszám szótárakat.
    """
    clean_templates: Dict[str, str] = {}
    derived_tag_lines: Dict[str, Dict[str, int]] = {}

    for lang, raw_code in raw_templates.items():
        clean_lines: List[str] = []
        tag_map: Dict[str, int] = {}
        for line_idx, line in enumerate(raw_code.splitlines(), start=1):
            match = TAG_PATTERN.search(line)
            if match:
                tag = match.group(1) or match.group(2)
                tag_map[tag] = line_idx
                clean_line = TAG_PATTERN.sub("", line).rstrip()
                clean_lines.append(clean_line)
            else:
                clean_lines.append(line)
        clean_templates[lang] = "\n".join(clean_lines) + ("\n" if raw_code.endswith("\n") else "")
        derived_tag_lines[lang] = tag_map

    return clean_templates, derived_tag_lines


# ============================================================================
# PHASE 1 - 3-LÁMPÁS JELZŐLÁMPA SABLONOK ÉS OSZTÁLY
# ============================================================================

RAW_CODE_TEMPLATES_P1: Dict[str, str] = {
    "Python": """# Oktatási Jelzőlámpa Szimuláció - 1. Fázis
state = "INIT"  # [TAG:INIT]

for cycle in range(1, total_cycles + 1):  # [TAG:LOOP_START]
    # 1. Piros jelzés: Megállás!
    state = set_signal(red=True, yellow=False, green=False, duration=red_sec)  # [TAG:RED]
    # 2. Piros-sárga jelzés: Felkészülés az indulásra
    state = set_signal(red=True, yellow=True, green=False, duration=ry_sec)  # [TAG:RED_YELLOW]
    # 3. Zöld jelzés: Szabad út, áthaladás
    state = set_signal(red=False, yellow=False, green=True, duration=green_sec)  # [TAG:GREEN]
    # 4. Sárga jelzés: Figyelem, felkészülés a megállásra
    state = set_signal(red=False, yellow=True, green=False, duration=yellow_sec)  # [TAG:YELLOW]

state = "COMPLETED"  # [TAG:COMPLETE]
""",
    "C++": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
#include <iostream>
std::string state = "INIT";  // [TAG:INIT]

for (int cycle = 1; cycle <= totalCycles; ++cycle) {  // [TAG:LOOP_START]
    // 1. Piros jelzés: Megállás!
    state = setSignal(true, false, false, redSec);  // [TAG:RED]
    // 2. Piros-sárga jelzés: Felkészülés az indulásra
    state = setSignal(true, true, false, rySec);  // [TAG:RED_YELLOW]
    // 3. Zöld jelzés: Szabad út, áthaladás
    state = setSignal(false, false, true, greenSec);  // [TAG:GREEN]
    // 4. Sárga jelzés: Figyelem, megállás előkészítése
    state = setSignal(false, true, false, yellowSec);  // [TAG:YELLOW]
}
state = "COMPLETED";  // [TAG:COMPLETE]
""",
    "C": """/* Oktatási Jelzőlámpa Szimuláció (Phase 1) */
#include <stdio.h>
int cycle;
const char* state = "INIT";  /* [TAG:INIT] */

for (cycle = 1; cycle <= total_cycles; cycle++) {  /* [TAG:LOOP_START] */
    /* 1. Piros jelzés: Megállás */
    state = set_signal(1, 0, 0, red_sec);  /* [TAG:RED] */
    /* 2. Piros-sárga jelzés: Felkészülés */
    state = set_signal(1, 1, 0, ry_sec);  /* [TAG:RED_YELLOW] */
    /* 3. Zöld jelzés: Áthaladás */
    state = set_signal(0, 0, 1, green_sec);  /* [TAG:GREEN] */
    /* 4. Sárga jelzés: Figyelem */
    state = set_signal(0, 1, 0, yellow_sec);  /* [TAG:YELLOW] */
}
state = "COMPLETED";  /* [TAG:COMPLETE] */
""",
    "BASIC": """' Oktatási Jelzőlámpa Szimuláció (Phase 1)
STATE$ = "INIT"  ' [TAG:INIT]

FOR CYCLE = 1 TO TOTALCYCLES  ' [TAG:LOOP_START]
    ' 1. Piros jelzés: Megállás!
    CALL SetSignal(1, 0, 0, RedSec)  ' [TAG:RED]
    ' 2. Piros-sárga: Felkészülés
    CALL SetSignal(1, 1, 0, RySec)  ' [TAG:RED_YELLOW]
    ' 3. Zöld jelzés: Szabad út
    CALL SetSignal(0, 0, 1, GreenSec)  ' [TAG:GREEN]
    ' 4. Sárga jelzés: Figyelem
    CALL SetSignal(0, 1, 0, YellowSec)  ' [TAG:YELLOW]
NEXT CYCLE
STATE$ = "COMPLETED"  ' [TAG:COMPLETE]
""",
    "Java": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
public class TrafficLight {
    public void runSimulation(int totalCycles) {
        String state = "INIT";  // [TAG:INIT]

        for (int cycle = 1; cycle <= totalCycles; cycle++) {  // [TAG:LOOP_START]
            // 1. Piros jelzés: Megállás!
            state = setSignal(true, false, false, redSec);  // [TAG:RED]
            // 2. Piros-sárga jelzés: Felkészülés
            state = setSignal(true, true, false, rySec);  // [TAG:RED_YELLOW]
            // 3. Zöld jelzés: Szabad út
            state = setSignal(false, false, true, greenSec);  // [TAG:GREEN]
            // 4. Sárga jelzés: Figyelem
            state = setSignal(false, true, false, yellowSec);  // [TAG:YELLOW]
        }
        state = "COMPLETED";  // [TAG:COMPLETE]
    }
}
""",
    "Pascal": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
program TrafficLightSimulation;
var
  cycle: Integer;
  state: String;
begin
  state := 'INIT';  // [TAG:INIT]
  for cycle := 1 to totalCycles do  // [TAG:LOOP_START]
  begin
    // 1. Piros jelzés: Megállás!
    state := SetSignal(True, False, False, redSec);  // [TAG:RED]
    // 2. Piros-sárga: Felkészülés
    state := SetSignal(True, True, False, rySec);  // [TAG:RED_YELLOW]
    // 3. Zöld jelzés: Szabad út
    state := SetSignal(False, False, True, greenSec);  // [TAG:GREEN]
    // 4. Sárga jelzés: Figyelem
    state := SetSignal(False, True, False, yellowSec);  // [TAG:YELLOW]
  end;
  state := 'COMPLETED';  // [TAG:COMPLETE]
end.
""",
}

CLEAN_CODE_TEMPLATES, DERIVED_TAG_LINES = _process_code_templates(RAW_CODE_TEMPLATES_P1)


class TrafficLightPlugin(AlgorithmPluginBase):
    """
    Oktatási Jelzőlámpa szimulációs plugin (Phase 1).
    3-lámpás ciklus, forráskód-követés, visszaszámlálás.
    """
    id = "traffic_light"
    name = "Jelzőlámpa szimuláció"
    description = "Klasszikus 3-lámpás forgalomirányító jelzőlámpa állapota és forráskód-szinkronja"
    time_complexity = "O(n × t)"
    space_complexity = "O(1)"
    icon = "🚦"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simulation"

    STATE_RED = "RED"
    STATE_RED_YELLOW = "RED_YELLOW"
    STATE_GREEN = "GREEN"
    STATE_YELLOW = "YELLOW"
    STATE_INIT = "INIT"
    STATE_COMPLETED = "COMPLETED"

    STATE_NAMES_HU = {
        STATE_INIT: "Kezdőállapot",
        STATE_RED: "PIROS",
        STATE_RED_YELLOW: "PIROS-SÁRGA",
        STATE_GREEN: "ZÖLD",
        STATE_YELLOW: "SÁRGA",
        STATE_COMPLETED: "Befejezve",
    }

    def __init__(self):
        """Inicializálja a szimulációs paramétereket és belső állapotot."""
        self.params = DynamicParams()
        self.params.add(Param("red_duration", "Piros idő (mp)", "int", 3, 1, 10, description="Piros fény időtartama"))
        self.params.add(Param("red_yellow_duration", "Piros-sárga idő (mp)", "int", 1, 1, 5, description="Piros-sárga átmenet időtartama"))
        self.params.add(Param("green_duration", "Zöld idő (mp)", "int", 3, 1, 10, description="Zöld fény időtartama"))
        self.params.add(Param("yellow_duration", "Sárga idő (mp)", "int", 1, 1, 5, description="Sárga fény időtartama"))
        self.params.add(Param("cycles", "Ciklusok száma", "int", 2, 1, 10, description="Hány teljes lámpaciklus fusson le"))
        self.complexity_level = "beginner"
        self._custom_visualizer = None

    def get_params(self) -> DynamicParams:
        """Visszaadja a konfigurálható dinamikus paramétereket."""
        return self.params

    def set_param(self, pid: str, val):
        """Beállítja a megadott azonosítójú paraméter értékét."""
        self.params.set(pid, val)

    def get_code(self, language: str) -> str:
        """Visszaadja a tiszta forráskódot a kért nyelven."""
        return CLEAN_CODE_TEMPLATES.get(language, CLEAN_CODE_TEMPLATES["Python"])

    def get_supported_languages(self) -> List[str]:
        """Visszaadja a támogatott nyelvek listáját."""
        return ["Python", "C++", "C", "BASIC", "Java", "Pascal"]

    @classmethod
    def get_line_for_tag(cls, language: str, tag: str) -> int:
        """Visszaadja a megadott címkéhez tartozó 1-alapú sorszámot a kért nyelven."""
        lang_tags = DERIVED_TAG_LINES.get(language, DERIVED_TAG_LINES.get("Python", {}))
        return lang_tags.get(tag, 1)

    def create_visualizer(self):
        """Létrehozza és visszaadja a dedikált TrafficLightViewerWidget példányt."""
        try:
            from ui.traffic_light_widget import TrafficLightViewerWidget
            if self._custom_visualizer is None:
                self._custom_visualizer = TrafficLightViewerWidget()
            return self._custom_visualizer
        except Exception as e:
            print(f"[TrafficLightPlugin] create_visualizer error: {e}")
            return None

    def get_steps(self, arr=None) -> Generator[VisualizationStep, None, None]:
        """
        Generates finely synchronized simulation steps.
        Each step represents a 1-second educational state slice with countdown,
        illuminated lamp states, line-tracking in source code, and localized explanation.
        """
        red_sec = max(1, int(self.params.get("red_duration") or 3))
        ry_sec = max(1, int(self.params.get("red_yellow_duration") or 1))
        green_sec = max(1, int(self.params.get("green_duration") or 3))
        yellow_sec = max(1, int(self.params.get("yellow_duration") or 1))
        total_cycles = max(1, int(self.params.get("cycles") or 2))

        yield VisualizationStep(
            explanation="🚦 Jelzőlámpa rendszer inicializálva. Készen áll a ciklus indítására.",
            code_line=self.get_line_for_tag("Python", "INIT"),
            metrics={"comparisons": 0, "pass_num": 0, "remaining_time": 0, "cycle": 0},
            array=[0, 0, 0],
            key="INIT",
            extra={
                "tag": "INIT",
                "state": self.STATE_INIT,
                "state_hu": self.STATE_NAMES_HU[self.STATE_INIT],
                "lamps": {"red": False, "yellow": False, "green": False},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": 0,
                "total_cycles": total_cycles,
                "phase_index": 0,
                "next_state": self.STATE_RED,
            }
        )

        total_step_counter = 0
        last_lamp_state = {"red": False, "yellow": False, "green": False}

        for cycle_idx in range(1, total_cycles + 1):
            loop_lamps = dict(last_lamp_state) if cycle_idx > 1 else {"red": False, "yellow": False, "green": False}

            yield VisualizationStep(
                explanation=f"🔄 {cycle_idx}. ciklus kezdete ({cycle_idx}/{total_cycles}). Ciklusfej kiértékelése.",
                code_line=self.get_line_for_tag("Python", "LOOP_START"),
                metrics={"comparisons": cycle_idx, "pass_num": cycle_idx, "remaining_time": 0, "cycle": cycle_idx},
                array=[int(cycle_idx), int(total_cycles)],
                key=f"Ciklus {cycle_idx}",
                extra={
                    "tag": "LOOP_START",
                    "state": "CYCLE_START",
                    "state_hu": f"{cycle_idx}. Ciklus",
                    "lamps": loop_lamps,
                    "remaining_time": 0,
                    "duration": 0,
                    "step_duration_ms": 0,
                    "cycle": cycle_idx,
                    "total_cycles": total_cycles,
                    "next_state": self.STATE_RED,
                }
            )

            yellow_next = None if cycle_idx == total_cycles else self.STATE_RED
            phases = [
                (self.STATE_RED, "RED", {"red": True, "yellow": False, "green": False}, red_sec, "⛔ PIROS jelzés: Megállás! A járműforgalom várakozik.", self.STATE_RED_YELLOW),
                (self.STATE_RED_YELLOW, "RED_YELLOW", {"red": True, "yellow": True, "green": False}, ry_sec, "⚠️ PIROS-SÁRGA jelzés: Felkészülés az indulásra! A motor felpörgethető, de még tilos behajtani.", self.STATE_GREEN),
                (self.STATE_GREEN, "GREEN", {"red": False, "yellow": False, "green": True}, green_sec, "🟢 ZÖLD jelzés: Szabad az út! A járművek áthaladhatnak a kereszteződésen.", self.STATE_YELLOW),
                (self.STATE_YELLOW, "YELLOW", {"red": False, "yellow": True, "green": False}, yellow_sec, "🟡 SÁRGA jelzés: Figyelem! A kereszteződés kiürítése, megállás a vonal előtt.", yellow_next),
            ]

            for state_code, tag, lamps, duration, desc_base, next_state in phases:
                last_lamp_state = dict(lamps)
                for rem in range(duration, 0, -1):
                    total_step_counter += 1
                    explanation = f"{desc_base} Hátralévő idő: {rem} mp."
                    arr_display = [int(lamps["red"]), int(lamps["yellow"]), int(lamps["green"])]

                    yield VisualizationStep(
                        explanation=explanation,
                        code_line=self.get_line_for_tag("Python", tag),
                        metrics={
                            "comparisons": total_step_counter,
                            "pass_num": cycle_idx,
                            "remaining_time": rem,
                            "cycle": cycle_idx,
                        },
                        array=arr_display,
                        key=self.STATE_NAMES_HU[state_code],
                        highlight=[i for i, val in enumerate(arr_display) if val],
                        extra={
                            "tag": tag,
                            "state": state_code,
                            "state_hu": self.STATE_NAMES_HU[state_code],
                            "lamps": dict(lamps),
                            "remaining_time": rem,
                            "duration": duration,
                            "step_duration_ms": 1000,
                            "cycle": cycle_idx,
                            "total_cycles": total_cycles,
                            "next_state": next_state,
                            "step_index": total_step_counter,
                        }
                    )

        yield VisualizationStep(
            explanation=f"✅ Jelzőlámpa szimuláció befejeződött: {total_cycles} ciklus sikeresen lefutott.",
            code_line=self.get_line_for_tag("Python", "COMPLETE"),
            metrics={"comparisons": total_step_counter, "pass_num": total_cycles, "remaining_time": 0, "cycle": total_cycles},
            array=[0, 0, 0],
            key="KÉSZ",
            extra={
                "tag": "COMPLETE",
                "state": self.STATE_COMPLETED,
                "state_hu": self.STATE_NAMES_HU[self.STATE_COMPLETED],
                "lamps": {"red": False, "yellow": False, "green": False},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": total_cycles,
                "total_cycles": total_cycles,
                "next_state": None,
            }
        )


# ============================================================================
# PHASE 2 - NÉGYIRÁNYÚ FORGALMI KERESZTEZŐDÉS SABLONOK ÉS OSZTÁLY
# ============================================================================

RAW_CODE_TEMPLATES_P2: Dict[str, str] = {
    "Python": """# Oktatási Kereszteződés Szimuláció - 2. Fázis
intersection = init_intersection(queues=vehicles_count)  # [TAG:INIT]

for cycle in range(1, total_cycles + 1):  # [TAG:LOOP_START]
    # Fázisok végrehajtása (É-D zöld, É-D sárga, kiürítés, K-Ny zöld, K-Ny sárga, kiürítés)
    for phase in get_phases(cycle):
        set_traffic_signals(ns=phase.ns_signal, ew=phase.ew_signal)  # [TAG:SET_SIGNALS]
        for sec in range(phase.duration, 0, -1):
            # 1. Kereszteződésben lévő járművek továbbhaladása és távozása
            advance_crossing_vehicles(intersection)  # [TAG:PROCESS_CROSSING]
            # 2. Ütközésmentesség ellenőrzése a belépés előtt
            has_conflict = check_intersection_conflict(intersection, phase.active_direction)  # [TAG:CHECK_CONFLICT]
            if not has_conflict and phase.is_green:
                # 3. Zöld jelzés esetén a sor elején álló jármű behajtása
                start_waiting_vehicle(intersection, phase.active_direction)  # [TAG:START_VEHICLES]
                # 4. Mögötte álló járműsor előreléptetése a stopvonal felé
                advance_approach_queue(intersection, phase.active_direction)  # [TAG:ADVANCE_QUEUE]
            else:
                # 5. Sárga/piros esetén felkészülés és biztonsági kiürítés
                clear_or_hold_vehicles(intersection)  # [TAG:CLEAR_INTERSECTION]

finish_simulation(intersection)  # [TAG:COMPLETE]
""",
    "C++": """// Oktatási Kereszteződés Szimuláció (Phase 2)
#include <iostream>
Intersection intersection = initIntersection(vehiclesCount);  // [TAG:INIT]

for (int cycle = 1; cycle <= totalCycles; ++cycle) {  // [TAG:LOOP_START]
    for (Phase phase : getPhases(cycle)) {
        setTrafficSignals(phase.nsSignal, phase.ewSignal);  // [TAG:SET_SIGNALS]
        for (int sec = phase.duration; sec > 0; --sec) {
            // 1. Kereszteződésben lévő járművek továbbhaladása és távozása
            advanceCrossingVehicles(intersection);  // [TAG:PROCESS_CROSSING]
            // 2. Ütközésmentesség ellenőrzése a belépés előtt
            bool hasConflict = checkIntersectionConflict(intersection, phase.activeDirection);  // [TAG:CHECK_CONFLICT]
            if (!hasConflict && phase.isGreen) {
                // 3. Zöld jelzés esetén a sor elején álló jármű behajtása
                startWaitingVehicle(intersection, phase.activeDirection);  // [TAG:START_VEHICLES]
                // 4. Mögötte álló járműsor előreléptetése a stopvonal felé
                advanceApproachQueue(intersection, phase.activeDirection);  // [TAG:ADVANCE_QUEUE]
            } else {
                // 5. Sárga/piros esetén felkészülés és biztonsági kiürítés
                clearOrHoldVehicles(intersection);  // [TAG:CLEAR_INTERSECTION]
            }
        }
    }
}
finishSimulation(intersection);  // [TAG:COMPLETE]
""",
    "C": """/* Oktatási Kereszteződés Szimuláció (Phase 2) */
#include <stdio.h>
init_intersection(vehicles_count);  /* [TAG:INIT] */

for (cycle = 1; cycle <= total_cycles; cycle++) {  /* [TAG:LOOP_START] */
    while (get_next_phase(&phase)) {
        set_traffic_signals(phase.ns_signal, phase.ew_signal);  /* [TAG:SET_SIGNALS] */
        for (sec = phase.duration; sec > 0; sec--) {
            /* 1. Kereszteződésben lévő járművek továbbhaladása és távozása */
            advance_crossing_vehicles();  /* [TAG:PROCESS_CROSSING] */
            /* 2. Ütközésmentesség ellenőrzése a belépés előtt */
            has_conflict = check_intersection_conflict(phase.active_dir);  /* [TAG:CHECK_CONFLICT] */
            if (!has_conflict && phase.is_green) {
                /* 3. Zöld jelzés esetén a sor elején álló jármű behajtása */
                start_waiting_vehicle(phase.active_dir);  /* [TAG:START_VEHICLES] */
                /* 4. Mögötte álló járműsor előreléptetése a stopvonal felé */
                advance_approach_queue(phase.active_dir);  /* [TAG:ADVANCE_QUEUE] */
            } else {
                /* 5. Sárga/piros esetén felkészülés és biztonsági kiürítés */
                clear_or_hold_vehicles();  /* [TAG:CLEAR_INTERSECTION] */
            }
        }
    }
}
finish_simulation();  /* [TAG:COMPLETE] */
""",
    "BASIC": """' Oktatási Kereszteződés Szimuláció (Phase 2)
CALL InitIntersection(VehiclesCount)  ' [TAG:INIT]

FOR CYCLE = 1 TO TOTALCYCLES  ' [TAG:LOOP_START]
    FOR PHASE_IDX = 1 TO 6
        CALL SetTrafficSignals(PhaseNsSignal, PhaseEwSignal)  ' [TAG:SET_SIGNALS]
        FOR SEC = PhaseDuration TO 1 STEP -1
            ' 1. Kereszteződésben lévő járművek továbbhaladása és távozása
            CALL AdvanceCrossingVehicles  ' [TAG:PROCESS_CROSSING]
            ' 2. Ütközésmentesség ellenőrzése a belépés előtt
            HasConflict = CheckIntersectionConflict(ActiveDir)  ' [TAG:CHECK_CONFLICT]
            IF HasConflict = 0 AND PhaseIsGreen = 1 THEN
                ' 3. Zöld jelzés esetén a sor elején álló jármű behajtása
                CALL StartWaitingVehicle(ActiveDir)  ' [TAG:START_VEHICLES]
                ' 4. Mögötte álló járműsor előreléptetése a stopvonal felé
                CALL AdvanceApproachQueue(ActiveDir)  ' [TAG:ADVANCE_QUEUE]
            ELSE
                ' 5. Sárga/piros esetén felkészülés és biztonsági kiürítés
                CALL ClearOrHoldVehicles  ' [TAG:CLEAR_INTERSECTION]
            END IF
        NEXT SEC
    NEXT PHASE_IDX
NEXT CYCLE
CALL FinishSimulation  ' [TAG:COMPLETE]
""",
    "Java": """// Oktatási Kereszteződés Szimuláció (Phase 2)
public class TrafficIntersection {
    public void runSimulation(int totalCycles) {
        initIntersection(vehiclesCount);  // [TAG:INIT]

        for (int cycle = 1; cycle <= totalCycles; cycle++) {  // [TAG:LOOP_START]
            for (Phase phase : getPhases(cycle)) {
                setTrafficSignals(phase.nsSignal, phase.ewSignal);  // [TAG:SET_SIGNALS]
                for (int sec = phase.duration; sec > 0; sec--) {
                    // 1. Kereszteződésben lévő járművek továbbhaladása és távozása
                    advanceCrossingVehicles(intersection);  // [TAG:PROCESS_CROSSING]
                    // 2. Ütközésmentesség ellenőrzése a belépés előtt
                    boolean hasConflict = checkIntersectionConflict(phase.activeDir);  // [TAG:CHECK_CONFLICT]
                    if (!hasConflict && phase.isGreen) {
                        // 3. Zöld jelzés esetén a sor elején álló jármű behajtása
                        startWaitingVehicle(phase.activeDir);  // [TAG:START_VEHICLES]
                        // 4. Mögötte álló járműsor előreléptetése a stopvonal felé
                        advanceApproachQueue(phase.activeDir);  // [TAG:ADVANCE_QUEUE]
                    } else {
                        // 5. Sárga/piros esetén felkészülés és biztonsági kiürítés
                        clearOrHoldVehicles(intersection);  // [TAG:CLEAR_INTERSECTION]
                    }
                }
            }
        }
        finishSimulation();  // [TAG:COMPLETE]
    }
}
""",
    "Pascal": """// Oktatási Kereszteződés Szimuláció (Phase 2)
program TrafficIntersectionSimulation;
begin
  InitIntersection(vehiclesCount);  // [TAG:INIT]
  for cycle := 1 to totalCycles do  // [TAG:LOOP_START]
  begin
    for phaseIdx := 1 to 6 do
    begin
      SetTrafficSignals(phase.nsSignal, phase.ewSignal);  // [TAG:SET_SIGNALS]
      for sec := phase.duration downto 1 do
      begin
        // 1. Kereszteződésben lévő járművek továbbhaladása és távozása
        AdvanceCrossingVehicles(intersection);  // [TAG:PROCESS_CROSSING]
        // 2. Ütközésmentesség ellenőrzése a belépés előtt
        hasConflict := CheckIntersectionConflict(phase.activeDir);  // [TAG:CHECK_CONFLICT]
        if (not hasConflict) and phase.isGreen then
        begin
          // 3. Zöld jelzés esetén a sor elején álló jármű behajtása
          StartWaitingVehicle(phase.activeDir);  // [TAG:START_VEHICLES]
          // 4. Mögötte álló járműsor előreléptetése a stopvonal felé
          AdvanceApproachQueue(phase.activeDir);  // [TAG:ADVANCE_QUEUE]
        end
        else
          // 5. Sárga/piros esetén felkészülés és biztonsági kiürítés
          ClearOrHoldVehicles(intersection);  // [TAG:CLEAR_INTERSECTION]
      end;
    end;
  end;
  FinishSimulation();  // [TAG:COMPLETE]
end.
""",
}

CLEAN_CODE_TEMPLATES_P2, DERIVED_TAG_LINES_P2 = _process_code_templates(RAW_CODE_TEMPLATES_P2)


class TrafficIntersectionPlugin(AlgorithmPluginBase):
    """
    Oktatási Forgalmi Kereszteződés szimulációs plugin (Phase 2).
    Négyirányú útkereszteződés, Észak-Dél és Kelet-Nyugat összehangolt
    jelzőlámpák, járműsorok mozgása, ütközésmentes forgalomirányítás,
    forráskód-végrehajtási sor szinkronizáció mind a 6 nyelven.
    """
    id = "traffic_intersection"
    name = "Kereszteződés szimuláció"
    description = "Négyirányú útkereszteződés járműforgalommal és koordinált jelzőlámpákkal (Phase 2)"
    time_complexity = "O(n × t)"
    space_complexity = "O(v)"
    icon = "🚦"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simulation"

    # Állapotnevek
    PHASE_INIT = "INIT"
    PHASE_NS_GREEN = "NS_GREEN"
    PHASE_NS_YELLOW = "NS_YELLOW"
    PHASE_CLEARANCE_1 = "CLEARANCE_1"
    PHASE_EW_GREEN = "EW_GREEN"
    PHASE_EW_YELLOW = "EW_YELLOW"
    PHASE_CLEARANCE_2 = "CLEARANCE_2"
    PHASE_COMPLETED = "COMPLETED"

    PHASE_NAMES_HU = {
        PHASE_INIT: "Kezdőállapot",
        PHASE_NS_GREEN: "Észak-Dél ZÖLD",
        PHASE_NS_YELLOW: "Észak-Dél SÁRGA",
        PHASE_CLEARANCE_1: "Kiürítés (Minden PIROS)",
        PHASE_EW_GREEN: "Kelet-Nyugat ZÖLD",
        PHASE_EW_YELLOW: "Kelet-Nyugat SÁRGA",
        PHASE_CLEARANCE_2: "Kiürítés (Minden PIROS)",
        PHASE_COMPLETED: "Befejezve",
    }

    def __init__(self):
        """Inicializálja a 2. fázis paramétereit és belső állapotát."""
        self.params = DynamicParams()
        self.params.add(Param("ns_green_duration", "Észak-Dél zöld idő (mp)", "int", 3, 1, 10, description="Észak-Dél irány zöld jelzésének időtartama"))
        self.params.add(Param("ew_green_duration", "Kelet-Nyugat zöld idő (mp)", "int", 3, 1, 10, description="Kelet-Nyugat irány zöld jelzésének időtartama"))
        self.params.add(Param("yellow_duration", "Sárga átmeneti idő (mp)", "int", 1, 1, 5, description="Sárga figyelmeztető fázis időtartama"))
        self.params.add(Param("all_red_duration", "Kiürítési piros idő (mp)", "int", 1, 1, 5, description="Teljes piros biztonsági kiürítési időköz"))
        self.params.add(Param("vehicles_per_approach", "Járművek száma irányonként", "int", 3, 1, 6, description="Kezdeti járműsor mérete megközelítési irányonként"))
        self.params.add(Param("cycles", "Ciklusok száma", "int", 2, 1, 10, description="Kereszteződési forgalmi ciklusok száma"))
        self.complexity_level = "intermediate"
        self._custom_visualizer = None

    def get_params(self) -> DynamicParams:
        """Visszaadja a konfigurálható dinamikus paramétereket."""
        return self.params

    def set_param(self, pid: str, val):
        """Beállítja a megadott azonosítójú paraméter értékét."""
        self.params.set(pid, val)

    def get_code(self, language: str) -> str:
        """Visszaadja a tiszta forráskódot a kért nyelven."""
        return CLEAN_CODE_TEMPLATES_P2.get(language, CLEAN_CODE_TEMPLATES_P2["Python"])

    def get_supported_languages(self) -> List[str]:
        """Visszaadja a támogatott nyelvek listáját."""
        return ["Python", "C++", "C", "BASIC", "Java", "Pascal"]

    @classmethod
    def get_line_for_tag(cls, language: str, tag: str) -> int:
        """Visszaadja a megadott címkéhez tartozó 1-alapú sorszámot a kért nyelven."""
        lang_tags = DERIVED_TAG_LINES_P2.get(language, DERIVED_TAG_LINES_P2.get("Python", {}))
        return lang_tags.get(tag, 1)

    def create_visualizer(self):
        """Létrehozza és visszaadja a dedikált TrafficIntersectionViewerWidget példányt."""
        try:
            from ui.traffic_intersection_widget import TrafficIntersectionViewerWidget
            if self._custom_visualizer is None:
                self._custom_visualizer = TrafficIntersectionViewerWidget()
            return self._custom_visualizer
        except Exception as e:
            print(f"[TrafficIntersectionPlugin] create_visualizer error: {e}")
            return None

    def get_steps(self, arr=None) -> Generator[VisualizationStep, None, None]:
        """
        Determinisztikus lépésgenerátor a négyirányú útkereszteződéshez.
        Minden lépés pontos szemantikai művelethez és forráskód-sorhoz rendelt:
        - INIT: Inicializálás
        - LOOP_START: Ciklusfej
        - SET_SIGNALS: Jelzőlámpák összehangolt beállítása a fázis kezdetén
        - PROCESS_CROSSING: A csomópontban lévő járművek továbbhaladása és távozása
        - CHECK_CONFLICT: Ütközésmentesség ellenőrzése
        - START_VEHICLES: Zöld jelzésnél a várakozó jármű belépése a kereszteződésbe
        - ADVANCE_QUEUE: A járműsor előrelépése
        - CLEAR_INTERSECTION: Sárga/piros biztonsági kiürítés
        - COMPLETE: Szimuláció befejezése
        """
        ns_green_sec = max(1, int(self.params.get("ns_green_duration") or 3))
        ew_green_sec = max(1, int(self.params.get("ew_green_duration") or 3))
        yellow_sec = max(1, int(self.params.get("yellow_duration") or 1))
        all_red_sec = max(1, int(self.params.get("all_red_duration") or 1))
        vehicles_count = max(1, int(self.params.get("vehicles_per_approach") or 3))
        total_cycles = max(1, int(self.params.get("cycles") or 2))

        def create_initial_vehicles(v_count: int) -> Dict[str, List[Dict[str, Any]]]:
            vehicles_by_dir: Dict[str, List[Dict[str, Any]]] = {}
            for d in ["north", "south", "east", "west"]:
                vehicles_by_dir[d] = []
                for i in range(v_count):
                    vehicles_by_dir[d].append({
                        "id": f"{d[0].upper()}{i+1}",
                        "direction": d,
                        "queue_pos": i,
                        "status": "waiting" if i == 0 else "queued",
                        "crossing_progress": 0,
                    })
            return vehicles_by_dir

        vehicles = create_initial_vehicles(vehicles_count)

        def count_active_vehicles():
            waiting_ns = sum(1 for d in ["north", "south"] for v in vehicles[d] if v["status"] in ("waiting", "queued"))
            waiting_ew = sum(1 for d in ["east", "west"] for v in vehicles[d] if v["status"] in ("waiting", "queued"))
            passed = sum(1 for d in vehicles for v in vehicles[d] if v["status"] == "departed")
            return waiting_ns, waiting_ew, passed

        init_lights = {
            "ns": {"red": True, "yellow": False, "green": False},
            "ew": {"red": True, "yellow": False, "green": False},
        }
        w_ns, w_ew, passed_cnt = count_active_vehicles()

        # 1. INIT LÉPÉS
        yield VisualizationStep(
            explanation="🚦 Négyirányú kereszteződés inicializálva: járműsorok felálltak a stopvonalak mögött.",
            code_line=self.get_line_for_tag("Python", "INIT"),
            metrics={"comparisons": 0, "pass_num": 0, "remaining_time": 0, "cycle": 0},
            array=[w_ns, w_ew, passed_cnt],
            key="INIT",
            extra={
                "tag": "INIT",
                "phase": self.PHASE_INIT,
                "phase_hu": self.PHASE_NAMES_HU[self.PHASE_INIT],
                "operation": "INIT",
                "right_of_way": "NONE",
                "right_of_way_hu": "Nincs elsőbbség (Minden irány áll)",
                "lights": init_lights,
                "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": 0,
                "total_cycles": total_cycles,
                "step_index": 0,
            }
        )

        total_step_counter = 0

        for cycle_idx in range(1, total_cycles + 1):
            # 2. CIKLUSFEJ LÉPÉS
            yield VisualizationStep(
                explanation=f"🔄 {cycle_idx}. forgalmi ciklus indítása ({cycle_idx}/{total_cycles}). Ciklus kiértékelése.",
                code_line=self.get_line_for_tag("Python", "LOOP_START"),
                metrics={"comparisons": total_step_counter, "pass_num": cycle_idx, "remaining_time": 0, "cycle": cycle_idx},
                array=[w_ns, w_ew, passed_cnt],
                key=f"Ciklus {cycle_idx}",
                extra={
                    "tag": "LOOP_START",
                    "phase": "CYCLE_START",
                    "phase_hu": f"{cycle_idx}. Ciklus",
                    "operation": "LOOP_START",
                    "right_of_way": "NONE",
                    "right_of_way_hu": "Ciklusváltás folyamatban",
                    "lights": init_lights,
                    "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                    "remaining_time": 0,
                    "duration": 0,
                    "step_duration_ms": 0,
                    "cycle": cycle_idx,
                    "total_cycles": total_cycles,
                    "step_index": total_step_counter,
                }
            )

            phase_definitions = [
                (
                    self.PHASE_NS_GREEN,
                    {"red": False, "yellow": False, "green": True},
                    {"red": True, "yellow": False, "green": False},
                    ns_green_sec,
                    "NORTH_SOUTH",
                    "Észak-Dél (Szabad út)",
                    ["north", "south"],
                    True,
                ),
                (
                    self.PHASE_NS_YELLOW,
                    {"red": False, "yellow": True, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    yellow_sec,
                    "NORTH_SOUTH",
                    "Észak-Dél (Átmenet / Lassítás)",
                    [],
                    False,
                ),
                (
                    self.PHASE_CLEARANCE_1,
                    {"red": True, "yellow": False, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    all_red_sec,
                    "NONE",
                    "Biztonsági kiürítés (Mindkét irány PIROS)",
                    [],
                    False,
                ),
                (
                    self.PHASE_EW_GREEN,
                    {"red": True, "yellow": False, "green": False},
                    {"red": False, "yellow": False, "green": True},
                    ew_green_sec,
                    "EAST_WEST",
                    "Kelet-Nyugat (Szabad út)",
                    ["east", "west"],
                    True,
                ),
                (
                    self.PHASE_EW_YELLOW,
                    {"red": True, "yellow": False, "green": False},
                    {"red": False, "yellow": True, "green": False},
                    yellow_sec,
                    "EAST_WEST",
                    "Kelet-Nyugat (Átmenet / Lassítás)",
                    [],
                    False,
                ),
                (
                    self.PHASE_CLEARANCE_2,
                    {"red": True, "yellow": False, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    all_red_sec,
                    "NONE",
                    "Biztonsági kiürítés (Mindkét irány PIROS)",
                    [],
                    False,
                ),
            ]

            for phase_id, ns_light, ew_light, duration, row_id, row_hu, moving_dirs, is_green in phase_definitions:
                cur_lights = {"ns": dict(ns_light), "ew": dict(ew_light)}
                init_lights = cur_lights

                for sec in range(duration, 0, -1):
                    total_step_counter += 1

                    # 1. Lépés: Kereszteződésben lévő járművek haladása
                    crossing_present = any(v["status"] == "crossing" for d in vehicles for v in vehicles[d])
                    for d in ["north", "south", "east", "west"]:
                        for v in vehicles[d]:
                            if v["status"] == "crossing":
                                v["crossing_progress"] += 1
                                # Show progress 2 at the far edge before hiding the vehicle.
                                if v["crossing_progress"] >= 3:
                                    v["status"] = "departed"

                    # 2. Ütközésmentesség ellenőrzése
                    conflicts_found = False
                    for d in moving_dirs:
                        conflicting_dirs = ["east", "west"] if d in ["north", "south"] else ["north", "south"]
                        if any(cv["status"] == "crossing" for cd in conflicting_dirs for cv in vehicles[cd]):
                            conflicts_found = True
                            break

                    # 3. Járművek indítása és sorok előrelépése
                    vehicles_started = False
                    queue_advanced = False
                    if is_green and not conflicts_found:
                        for d in moving_dirs:
                            for v in vehicles[d]:
                                if v["status"] == "waiting" and v["queue_pos"] == 0:
                                    v["status"] = "crossing"
                                    v["crossing_progress"] = 1
                                    vehicles_started = True
                                    break
                            for v in vehicles[d]:
                                if v["status"] == "queued":
                                    v["queue_pos"] -= 1
                                    queue_advanced = True
                                    if v["queue_pos"] == 0:
                                        v["status"] = "waiting"

                    w_ns, w_ew, passed_cnt = count_active_vehicles()

                    # Szemantikai művelet meghatározása a lépéshez:
                    # - Ha zöld és indult jármű:
                    #   * ha a sorban mögötte lévők előreléptek: ADVANCE_QUEUE
                    #   * ha nincs mögötte sor (utolsó autó indult): START_VEHICLES
                    # - Ha zöld de van konfliktus: CHECK_CONFLICT
                    # - Ha áthaladó jármű haladt bent: PROCESS_CROSSING
                    # - Ha sárga/piros kiürítés: CLEAR_INTERSECTION
                    # - Egyébként lámpaállapot: SET_SIGNALS
                    if is_green:
                        if vehicles_started:
                            if queue_advanced:
                                semantic_tag = "ADVANCE_QUEUE"
                                action_desc = f"🚗 Zöld jelzés: Elsőbbséget élvező jármű elindul, a várakozó sor előrelép ({row_hu})."
                            else:
                                semantic_tag = "START_VEHICLES"
                                action_desc = f"🚗 Zöld jelzés: Elsőbbséget élvező jármű behajt a csomópontba ({row_hu})."
                        elif conflicts_found:
                            semantic_tag = "CHECK_CONFLICT"
                            action_desc = f"⚠️ Ütközésvédelem: Belépés felfüggesztve, a csomópont kiürítésre vár."
                        elif crossing_present:
                            semantic_tag = "PROCESS_CROSSING"
                            action_desc = f"🛣️ Járművek haladnak át a kereszteződésen és biztonságosan elhagyják."
                        else:
                            semantic_tag = "SET_SIGNALS"
                            action_desc = f"🟢 Jelzőlámpa váltás: {row_hu}. Szabad az út."
                    else:
                        if crossing_present:
                            semantic_tag = "PROCESS_CROSSING"
                            action_desc = f"🚗 Áthaladó járművek kiürítik a kereszteződést a lámpaváltás előtt."
                        else:
                            semantic_tag = "CLEAR_INTERSECTION" if "kiürítés" in row_hu.lower() else "SET_SIGNALS"
                            action_desc = f"⛔ Jelzőlámpa állapot: {row_hu}. Stopvonalak előtt várakozás."

                    explanation = f"{action_desc} Hátralévő fázisidő: {sec} mp."

                    yield VisualizationStep(
                        explanation=explanation,
                        code_line=self.get_line_for_tag("Python", semantic_tag),
                        metrics={
                            "comparisons": total_step_counter,
                            "pass_num": cycle_idx,
                            "remaining_time": sec,
                            "cycle": cycle_idx,
                        },
                        array=[w_ns, w_ew, passed_cnt],
                        key=self.PHASE_NAMES_HU[phase_id],
                        extra={
                            "tag": semantic_tag,
                            "phase": phase_id,
                            "phase_hu": self.PHASE_NAMES_HU[phase_id],
                            "operation": semantic_tag,
                            "right_of_way": row_id,
                            "right_of_way_hu": row_hu,
                            "lights": cur_lights,
                            "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                            "remaining_time": sec,
                            "duration": duration,
                            "step_duration_ms": 1000,
                            "cycle": cycle_idx,
                            "total_cycles": total_cycles,
                            "step_index": total_step_counter,
                        }
                    )

        # 3. COMPLETE LÉPÉS
        yield VisualizationStep(
            explanation=f"✅ Kereszteződés szimuláció befejeződött: {total_cycles} ciklus sikeresen lefutott, forgalom koordinálva.",
            code_line=self.get_line_for_tag("Python", "COMPLETE"),
            metrics={"comparisons": total_step_counter, "pass_num": total_cycles, "remaining_time": 0, "cycle": total_cycles},
            array=[w_ns, w_ew, passed_cnt],
            key="KÉSZ",
            extra={
                "tag": "COMPLETE",
                "phase": self.PHASE_COMPLETED,
                "phase_hu": self.PHASE_NAMES_HU[self.PHASE_COMPLETED],
                "operation": "COMPLETE",
                "right_of_way": "NONE",
                "right_of_way_hu": "Szimuláció véget ért",
                "lights": {
                    "ns": {"red": True, "yellow": False, "green": False},
                    "ew": {"red": True, "yellow": False, "green": False},
                },
                "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": total_cycles,
                "total_cycles": total_cycles,
                "step_index": total_step_counter,
            }
        )
