# -*- coding: utf-8 -*-
"""
Traffic Light Educational Plugin - Phase 1 & Phase 2
Oktatási jelzőlámpa és forgalmi kereszteződés szimuláció valós idejű
kód- és végrehajtássor-követéssel mind a 6 támogatott programozási nyelven.
A forrássorok és logikai lépések összerendelése karbantartható inline címkékből
származtatott (nem törékeny, kézzel számolt sorpozíciókból).
"""
import re
from typing import Dict, Generator, List, Optional, Tuple, Any, Set
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
        CALL LoadPhase(CYCLE, PHASE_IDX, PhaseNsSignal, PhaseEwSignal, PhaseDuration, ActiveDir, PhaseIsGreen)
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
      LoadPhase(cycle, phaseIdx, phase);
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
        Minden lépés pontos szemantikai művelethez és forráskód-sorhoz rendelt.
        A szimulációs tickeken belül lezajló szemantikai részfolyamatok (kereszteződés áthaladás,
        ütközésmentesség-ellenőrzés, járműindítás, sor-előrelépés, kiürítés) különálló,
        rendezett szemantikai eseményként kerülnek kibocsátásra.
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

        def count_active_vehicles(snapshot):
            waiting_ns = sum(1 for d in ["north", "south"] for v in snapshot[d] if v["status"] in ("waiting", "queued"))
            waiting_ew = sum(1 for d in ["east", "west"] for v in snapshot[d] if v["status"] in ("waiting", "queued"))
            passed = sum(1 for d in snapshot for v in snapshot[d] if v["status"] == "departed")
            return waiting_ns, waiting_ew, passed

        init_lights = {
            "ns": {"red": True, "yellow": False, "green": False},
            "ew": {"red": True, "yellow": False, "green": False},
        }
        w_ns, w_ew, passed_cnt = count_active_vehicles(vehicles)

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
                    # Egy szimulációs tick során végbemenő szemantikai részfolyamatok listája:
                    # (tag, action_desc, vehicles_snapshot)
                    tick_events: List[Tuple[str, str, Dict[str, List[Dict[str, Any]]]]] = []

                    # 1. Ha a fázis legelső másodperce: lámpaváltás művelet
                    if sec == duration:
                        tick_events.append((
                            "SET_SIGNALS",
                            f"🟢 Jelzőlámpa beállítása: {row_hu}. Fázisidő: {duration} mp.",
                            {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                        ))

                    # 2. Kereszteződésben lévő járművek továbbhaladása és távozása
                    for d in ["north", "south", "east", "west"]:
                        for v in vehicles[d]:
                            if v["status"] == "crossing":
                                v["crossing_progress"] += 1
                                if v["crossing_progress"] >= 3:
                                    v["status"] = "departed"
                    tick_events.append((
                        "PROCESS_CROSSING",
                        f"🛣️ Kereszteződésben lévő járművek továbbhaladása és távozása ({row_hu}).",
                        {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                    ))

                    # 3. Ütközésmentesség ellenőrzése a belépés előtt
                    conflicts_found = False
                    for d in moving_dirs:
                        conflicting_dirs = ["east", "west"] if d in ["north", "south"] else ["north", "south"]
                        if any(cv["status"] == "crossing" for cd in conflicting_dirs for cv in vehicles[cd]):
                            conflicts_found = True
                            break

                    tick_events.append((
                        "CHECK_CONFLICT",
                        f"🔍 Kereszteződés ellenőrzése: {'Ütközésveszély, belépés tiltva' if conflicts_found else ('Kereszteződés szabad a belépéshez' if is_green else 'Sárga/piros jelzés, belépés tiltva')}.",
                        {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                    ))

                    # 4. Zöld jelzés esetén várakozó jármű behajtása és sor előrelépése
                    if is_green and not conflicts_found:
                        for d in moving_dirs:
                            for v in vehicles[d]:
                                if v["status"] == "waiting" and v["queue_pos"] == 0:
                                    v["status"] = "crossing"
                                    v["crossing_progress"] = 1
                                    break
                        tick_events.append((
                            "START_VEHICLES",
                            f"🚗 Zöld jelzés: Várakozó jármű behajt a kereszteződésbe ({row_hu}).",
                            {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                        ))

                        for d in moving_dirs:
                            for v in vehicles[d]:
                                if v["status"] == "queued":
                                    v["queue_pos"] -= 1
                                    if v["queue_pos"] == 0:
                                        v["status"] = "waiting"
                        tick_events.append((
                            "ADVANCE_QUEUE",
                            f"➡️ Várakozó járműsor előrelép a stopvonal felé ({row_hu}).",
                            {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                        ))
                    elif not is_green:
                        tick_events.append((
                            "CLEAR_INTERSECTION",
                            f"⛔ Várakozás a stopvonal előtt: {row_hu}.",
                            {d: [dict(v) for v in vehicles[d]] for d in vehicles}
                        ))

                    # Bocsássuk ki a tick összes szemantikai részfolyamatát pontos sorrendben!
                    # Az utolsó esemény viszi a tick 1000 ms visszaszámlálási fázisidejét,
                    # a megelőző szemantikai részfolyamatok azonnali (0 ms) végrehajtási állapotok,
                    # garantálva a forráskód-sor finom, lépésről-lépésre történő követhetőségét.
                    for ev_idx, (sem_tag, act_desc, v_snapshot) in enumerate(tick_events):
                        total_step_counter += 1
                        is_last_in_tick = (ev_idx == len(tick_events) - 1)
                        step_duration = 1000 if is_last_in_tick else 0
                        rem_time = sec

                        w_ns, w_ew, passed_cnt = count_active_vehicles(v_snapshot)
                        explanation = f"{act_desc} Hátralévő fázisidő: {sec} mp."

                        yield VisualizationStep(
                            explanation=explanation,
                            code_line=self.get_line_for_tag("Python", sem_tag),
                            metrics={
                                "comparisons": total_step_counter,
                                "pass_num": cycle_idx,
                                "remaining_time": rem_time,
                                "cycle": cycle_idx,
                            },
                            array=[w_ns, w_ew, passed_cnt],
                            key=self.PHASE_NAMES_HU[phase_id],
                            extra={
                                "tag": sem_tag,
                                "phase": phase_id,
                                "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                "operation": sem_tag,
                                "right_of_way": row_id,
                                "right_of_way_hu": row_hu,
                                "lights": cur_lights,
                                "vehicles": v_snapshot,
                                "remaining_time": rem_time,
                                "duration": duration,
                                "step_duration_ms": step_duration,
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


# ============================================================================
# PHASE 3 - TELJES KERESZTEZŐDÉS ÉS GYALOGOS FORGALOM SABLONOK ÉS OSZTÁLY
# ============================================================================

RAW_CODE_TEMPLATES_P3: Dict[str, str] = {
    "Python": """# Oktatási Kereszteződés és Gyalogos Szimuláció - 3. Fázis
intersection = init_intersection_with_pedestrians()  # [TAG:INIT]

for cycle in range(1, total_cycles + 1):  # [TAG:LOOP_START]
    for phase in get_phases(cycle):
        poll_pedestrian_requests(intersection)  # [TAG:POLL_REQUESTS]
        set_all_signals(intersection, phase.vehicle_signals, phase.pedestrian_signals)  # [TAG:SET_SIGNALS]
        for sec in range(phase.duration, 0, -1):
            advance_crossing_entities(intersection)  # [TAG:PROCESS_CROSSINGS]
            has_conflicts = check_traffic_conflicts(intersection, phase)  # [TAG:CHECK_CONFLICTS]
            if not has_conflicts and phase.allows_movement:
                start_permitted_movements(intersection, phase)  # [TAG:START_MOVEMENTS]
                advance_approach_queues(intersection, phase)  # [TAG:ADVANCE_QUEUES]
            else:
                hold_conflicting_traffic(intersection)  # [TAG:HOLD_TRAFFIC]

finish_simulation(intersection)  # [TAG:COMPLETE]
""",
    "C++": """// Oktatási Kereszteződés és Gyalogos Szimuláció (Phase 3)
#include <iostream>
Intersection intersection = initIntersectionWithPedestrians();  // [TAG:INIT]

for (int cycle = 1; cycle <= totalCycles; ++cycle) {  // [TAG:LOOP_START]
    for (Phase phase : getPhases(cycle)) {
        pollPedestrianRequests(intersection);  // [TAG:POLL_REQUESTS]
        setAllSignals(intersection, phase.vehicleSignals, phase.pedestrianSignals);  // [TAG:SET_SIGNALS]
        for (int sec = phase.duration; sec > 0; --sec) {
            advanceCrossingEntities(intersection);  // [TAG:PROCESS_CROSSINGS]
            bool hasConflicts = checkTrafficConflicts(intersection, phase);  // [TAG:CHECK_CONFLICTS]
            if (!hasConflicts && phase.allowsMovement) {
                startPermittedMovements(intersection, phase);  // [TAG:START_MOVEMENTS]
                advanceApproachQueues(intersection, phase);  // [TAG:ADVANCE_QUEUES]
            } else {
                holdConflictingTraffic(intersection);  // [TAG:HOLD_TRAFFIC]
            }
        }
    }
}
finishSimulation(intersection);  // [TAG:COMPLETE]
""",
    "C": """/* Oktatási Kereszteződés és Gyalogos Szimuláció (Phase 3) */
#include <stdio.h>
init_intersection_with_pedestrians();  /* [TAG:INIT] */

for (cycle = 1; cycle <= total_cycles; cycle++) {  /* [TAG:LOOP_START] */
    while (get_next_phase(&phase)) {
        poll_pedestrian_requests();  /* [TAG:POLL_REQUESTS] */
        set_all_signals(phase.veh_signals, phase.ped_signals);  /* [TAG:SET_SIGNALS] */
        for (sec = phase.duration; sec > 0; sec--) {
            advance_crossing_entities();  /* [TAG:PROCESS_CROSSINGS] */
            has_conflicts = check_traffic_conflicts(phase);  /* [TAG:CHECK_CONFLICTS] */
            if (!has_conflicts && phase.allows_movement) {
                start_permitted_movements(phase);  /* [TAG:START_MOVEMENTS] */
                advance_approach_queues(phase);  /* [TAG:ADVANCE_QUEUES] */
            } else {
                hold_conflicting_traffic();  /* [TAG:HOLD_TRAFFIC] */
            }
        }
    }
}
finish_simulation();  /* [TAG:COMPLETE] */
""",
    "BASIC": """' Oktatási Kereszteződés és Gyalogos Szimuláció (Phase 3)
CALL InitIntersectionWithPedestrians  ' [TAG:INIT]

FOR CYCLE = 1 TO TOTALCYCLES  ' [TAG:LOOP_START]
    FOR PHASE_IDX = 1 TO TOTAL_PHASES
        CALL PollPedestrianRequests  ' [TAG:POLL_REQUESTS]
        CALL SetAllSignals(VehSignals, PedSignals)  ' [TAG:SET_SIGNALS]
        FOR SEC = PhaseDuration TO 1 STEP -1
            CALL AdvanceCrossingEntities  ' [TAG:PROCESS_CROSSINGS]
            HasConflicts = CheckTrafficConflicts(PHASE_IDX)  ' [TAG:CHECK_CONFLICTS]
            IF HasConflicts = 0 AND AllowsMovement = 1 THEN
                CALL StartPermittedMovements(PHASE_IDX)  ' [TAG:START_MOVEMENTS]
                CALL AdvanceApproachQueues(PHASE_IDX)  ' [TAG:ADVANCE_QUEUES]
            ELSE
                CALL HoldConflictingTraffic  ' [TAG:HOLD_TRAFFIC]
            END IF
        NEXT SEC
    NEXT PHASE_IDX
NEXT CYCLE
CALL FinishSimulation  ' [TAG:COMPLETE]
""",
    "Java": """// Oktatási Kereszteződés és Gyalogos Szimuláció (Phase 3)
public class TrafficPedestrianIntersection {
    public void runSimulation(int totalCycles) {
        initIntersectionWithPedestrians();  // [TAG:INIT]

        for (int cycle = 1; cycle <= totalCycles; cycle++) {  // [TAG:LOOP_START]
            for (Phase phase : getPhases(cycle)) {
                pollPedestrianRequests(intersection);  // [TAG:POLL_REQUESTS]
                setAllSignals(intersection, phase.vehicleSignals, phase.pedestrianSignals);  // [TAG:SET_SIGNALS]
                for (int sec = phase.duration; sec > 0; sec--) {
                    advanceCrossingEntities(intersection);  // [TAG:PROCESS_CROSSINGS]
                    boolean hasConflicts = checkTrafficConflicts(intersection, phase);  // [TAG:CHECK_CONFLICTS]
                    if (!hasConflicts && phase.allowsMovement) {
                        startPermittedMovements(intersection, phase);  // [TAG:START_MOVEMENTS]
                        advanceApproachQueues(intersection, phase);  // [TAG:ADVANCE_QUEUES]
                    } else {
                        holdConflictingTraffic(intersection);  // [TAG:HOLD_TRAFFIC]
                    }
                }
            }
        }
        finishSimulation();  // [TAG:COMPLETE]
    }
}
""",
    "Pascal": """// Oktatási Kereszteződés és Gyalogos Szimuláció (Phase 3)
program TrafficPedestrianSimulation;
begin
  InitIntersectionWithPedestrians();  // [TAG:INIT]
  for cycle := 1 to totalCycles do  // [TAG:LOOP_START]
  begin
    for phaseIdx := 1 to totalPhases do
    begin
      PollPedestrianRequests();  // [TAG:POLL_REQUESTS]
      SetAllSignals(phase.vehSignals, phase.pedSignals);  // [TAG:SET_SIGNALS]
      for sec := phase.duration downto 1 do
      begin
        AdvanceCrossingEntities();  // [TAG:PROCESS_CROSSINGS]
        hasConflicts := CheckTrafficConflicts(phase);  // [TAG:CHECK_CONFLICTS]
        if (not hasConflicts) and phase.allowsMovement then
        begin
          StartPermittedMovements(phase);  // [TAG:START_MOVEMENTS]
          AdvanceApproachQueues(phase);  // [TAG:ADVANCE_QUEUES]
        end
        else
          HoldConflictingTraffic();  // [TAG:HOLD_TRAFFIC]
      end;
    end;
  end;
  FinishSimulation();  // [TAG:COMPLETE]
end.
""",
}

CLEAN_CODE_TEMPLATES_P3, DERIVED_TAG_LINES_P3 = _process_code_templates(RAW_CODE_TEMPLATES_P3)


class TrafficPedestrianIntersectionPlugin(AlgorithmPluginBase):
    """
    Oktatási Forgalmi Kereszteződés és Gyalogosforgalom szimulációs plugin (Phase 3).
    Négyirányú útkereszteződés járműforgalommal, 4 gyalogosátkelővel, gyalogos jelzőlámpákkal,
    hívógombokkal és garantált konfliktusmentes közlekedésbiztonsági koordinációval.
    Valós idejű kód- és végrehajtássor-követés mind a 6 támogatott programozási nyelven.
    Támogatja a valós idejű gyalogos hívógomb kérelmeket menet közben és determinisztikus
    fázisütemezést.
    """
    id = "traffic_pedestrian_intersection"
    name = "Kereszteződés és gyalogos szimuláció"
    description = "Négyirányú forgalmi kereszteződés gyalogosátkelőkkel és hívógombokkal (Phase 3)"
    time_complexity = "O(n × t)"
    space_complexity = "O(v + p)"
    icon = "🚶"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simulation"

    # Fázisok és állapotnevek
    PHASE_INIT = "INIT"
    PHASE_NS_GREEN = "NS_GREEN"
    PHASE_NS_YELLOW = "NS_YELLOW"
    PHASE_CLEARANCE_1 = "CLEARANCE_1"
    PHASE_EW_GREEN = "EW_GREEN"
    PHASE_EW_YELLOW = "EW_YELLOW"
    PHASE_CLEARANCE_2 = "CLEARANCE_2"
    PHASE_PED_WALK = "PED_WALK"
    PHASE_PED_CLEARANCE = "PED_CLEARANCE"
    PHASE_CLEARANCE_3 = "CLEARANCE_3"
    PHASE_COMPLETED = "COMPLETED"

    PHASE_NAMES_HU = {
        PHASE_INIT: "Kezdőállapot",
        PHASE_NS_GREEN: "Észak-Dél jármű ZÖLD",
        PHASE_NS_YELLOW: "Észak-Dél jármű SÁRGA",
        PHASE_CLEARANCE_1: "Kiürítés (Minden PIROS)",
        PHASE_EW_GREEN: "Kelet-Nyugat jármű ZÖLD",
        PHASE_EW_YELLOW: "Kelet-Nyugat jármű SÁRGA",
        PHASE_CLEARANCE_2: "Kiürítés (Minden PIROS)",
        PHASE_PED_WALK: "Gyalogos ZÖLD (Szabad átkelés)",
        PHASE_PED_CLEARANCE: "Gyalogos kiürítés (PIROS)",
        PHASE_CLEARANCE_3: "Biztonsági kiürítés (Minden PIROS)",
        PHASE_COMPLETED: "Befejezve",
    }

    def __init__(self):
        """Inicializálja a 3. fázis dinamikus paramétereit és belső állapotát."""
        self.params = DynamicParams()
        self.params.add(Param("ns_green_duration", "É-D zöld idő (mp)", "int", 3, 1, 10, description="Észak-Dél irány jármű zöld ideje"))
        self.params.add(Param("ew_green_duration", "K-Ny zöld idő (mp)", "int", 3, 1, 10, description="Kelet-Nyugat irány jármű zöld ideje"))
        self.params.add(Param("yellow_duration", "Sárga idő (mp)", "int", 1, 1, 5, description="Sárga átmeneti figyelmeztető idő"))
        self.params.add(Param("all_red_duration", "Jármű kiürítési idő (mp)", "int", 1, 1, 5, description="Járművek közötti teljes piros biztonsági időköz"))
        self.params.add(Param("ped_walk_duration", "Gyalogos zöld idő (mp)", "int", 3, 1, 10, description="Gyalogos zöld (átkelési) fázis időtartama"))
        self.params.add(Param("ped_clearance_duration", "Gyalogos kiürítési idő (mp)", "int", 2, 1, 5, description="Gyalogos kiürítési piros időtartam járműindítás előtt"))
        self.params.add(Param("vehicles_per_approach", "Járművek száma irányonként", "int", 2, 0, 6, description="Kezdeti járműsor mérete megközelítési irányonként"))
        self.params.add(Param("pedestrians_per_crossing", "Gyalogosok átkelőnként", "int", 2, 0, 6, description="Kezdeti várakozó gyalogosok száma átkelőnként"))
        self.params.add(Param("pedestrian_requests", "Kezdeti igények (É,D,K,Ny)", "str", "", description="Kezdeti gyalogos hívógomb igények (vesszővel elválasztva: north,south,east,west, vagy üres)"))
        self.params.add(Param("cycles", "Ciklusok száma", "int", 2, 1, 10, description="Kereszteződési forgalmi ciklusok száma"))
        self.complexity_level = "advanced"
        self._custom_visualizer = None
        self.runtime_requests: Set[str] = set()
        self.runtime_next_cycle_requests: Set[str] = set()

    def get_params(self) -> DynamicParams:
        """Visszaadja a konfigurálható dinamikus paramétereket."""
        return self.params

    def set_param(self, pid: str, val):
        """Beállítja a megadott azonosítójú paraméter értékét."""
        self.params.set(pid, val)

    def get_code(self, language: str) -> str:
        """Visszaadja a tiszta forráskódot a kért nyelven."""
        return CLEAN_CODE_TEMPLATES_P3.get(language, CLEAN_CODE_TEMPLATES_P3["Python"])

    def get_supported_languages(self) -> List[str]:
        """Visszaadja a támogatott nyelvek listáját."""
        return ["Python", "C++", "C", "BASIC", "Java", "Pascal"]

    @classmethod
    def get_line_for_tag(cls, language: str, tag: str) -> int:
        """Visszaadja a megadott címkéhez tartozó 1-alapú sorszámot a kért nyelven."""
        lang_tags = DERIVED_TAG_LINES_P3.get(language, DERIVED_TAG_LINES_P3.get("Python", {}))
        return lang_tags.get(tag, 1)

    def create_visualizer(self):
        """Létrehozza és visszaadja a dedikált TrafficPedestrianIntersectionViewerWidget példányt."""
        try:
            from ui.traffic_pedestrian_widget import TrafficPedestrianIntersectionViewerWidget
            if self._custom_visualizer is None:
                self._custom_visualizer = TrafficPedestrianIntersectionViewerWidget()
                self._custom_visualizer.set_plugin(self)
            return self._custom_visualizer
        except Exception as e:
            print(f"[TrafficPedestrianIntersectionPlugin] create_visualizer error: {e}")
            return None

    def sync_from_executed_step(self, step: VisualizationStep):
        """
        Szinkronizálja a plugin perzisztens futásidejű kérelemállapotát (runtime_requests,
        runtime_next_cycle_requests) a ténylegesen végrehajtott VisualizationStep pillanatképpel.
        Ez garantálja, hogy a kiszolgált kérelmek azonnal törlődnek a perzisztens állapotból,
        és egy későbbi kérelemregisztráció vagy újragenerálás nem élesztheti újra azokat.
        """
        if step and hasattr(step, 'extra') and isinstance(step.extra, dict):
            extra = step.extra
            if 'pending_requests_set' in extra:
                self.runtime_requests = set(extra['pending_requests_set'])
            if 'next_cycle_requests_set' in extra:
                self.runtime_next_cycle_requests = set(extra['next_cycle_requests_set'])

    def register_pedestrian_request(self, crossing: str, engine=None) -> bool:
        """
        Valós idejű gyalogos hívógomb kérelem regisztrálása a futó szimulációhoz.
        Kezeli az ismételt, egyidejű és aktív átkelés alatti igényeket.
        A kérelmek állapotát az aktuális futási pont (current_step) érvényes
        kérelemhalmazaiból származtatja, így a már kiszolgált kérelmek nem éledhetnek újra.
        Ha bármilyen gyalogos fázis (PED_WALK, PED_CLEARANCE, CLEARANCE_3) aktív,
        minden új kérelem a következő ciklusra ütemeződik.
        """
        crossing = str(crossing).strip().lower()
        if crossing not in {"north", "south", "east", "west"}:
            return False

        current_step = None
        curr_idx = 0
        if engine and hasattr(engine, 'steps') and engine.steps:
            curr_idx = getattr(engine, 'step_idx', 0)
            if 0 <= curr_idx < len(engine.steps):
                current_step = engine.steps[curr_idx]

        # Határozzuk meg az aktuális lépés kérelem-állapotát
        if current_step:
            cur_extra = getattr(current_step, 'extra', {}) or {}
            cur_pending = set(cur_extra.get('pending_requests_set', self.runtime_requests))
            cur_next_cycle = set(cur_extra.get('next_cycle_requests_set', self.runtime_next_cycle_requests))
            cur_phase = cur_extra.get('phase', '')
        else:
            cur_pending = set(self.runtime_requests)
            cur_next_cycle = set(self.runtime_next_cycle_requests)
            cur_phase = ''

        # Ha éppen aktív gyalogos fázis (PED_WALK, PED_CLEARANCE, CLEARANCE_3) zajlik:
        # BÁRMELY átkelőre érkező új kérelmet a következő ciklusra kell ütemezni,
        # megőrizve a jelenlegi gyalogos fázis zöld átkelőit és idejét.
        is_in_ped_phase = cur_phase in (self.PHASE_PED_WALK, self.PHASE_PED_CLEARANCE, self.PHASE_CLEARANCE_3)

        if is_in_ped_phase:
            cur_next_cycle.add(crossing)
        else:
            cur_pending.add(crossing)

        self.runtime_requests = set(cur_pending)
        self.runtime_next_cycle_requests = set(cur_next_cycle)

        # Frissítsük az aktuális lépés kérelem-metaadatait is, hogy több egymást követő kérelem
        # vagy egyidejű gombnyomás esetén a kérések hibátlanul összeadódjanak
        if current_step and hasattr(current_step, 'extra') and isinstance(current_step.extra, dict):
            current_step.extra['pending_requests_set'] = list(cur_pending)
            current_step.extra['next_cycle_requests_set'] = list(cur_next_cycle)
            req_states = {c: (c in cur_pending or c in cur_next_cycle) for c in ["north", "south", "east", "west"]}
            current_step.extra['pedestrian_requests'] = req_states

        # Ha átadtuk az engine-t, újrageneráljuk a jövőbeli lépéseket a jelenlegi lépéstől
        if engine and hasattr(engine, 'steps') and engine.steps and current_step:
            new_future = self.generate_future_steps_from_step(current_step, curr_idx)
            engine.steps = engine.steps[:curr_idx + 1] + new_future

        return True

    def _build_initial_entities(self, v_count: int, p_count: int):
        vehicles: Dict[str, List[Dict[str, Any]]] = {}
        for d in ["north", "south", "east", "west"]:
            vehicles[d] = []
            for i in range(v_count):
                vehicles[d].append({
                    "id": f"{d[0].upper()}{i+1}",
                    "direction": d,
                    "queue_pos": i,
                    "status": "waiting" if i == 0 else "queued",
                    "crossing_progress": 0,
                })

        pedestrians: Dict[str, List[Dict[str, Any]]] = {}
        for c in ["north", "south", "east", "west"]:
            pedestrians[c] = []
            for i in range(p_count):
                pedestrians[c].append({
                    "id": f"P_{c[0].upper()}{i+1}",
                    "crossing": c,
                    "queue_pos": i,
                    "status": "waiting" if i == 0 else "queued",
                    "crossing_progress": 0,
                })
        return vehicles, pedestrians

    def get_steps(self, arr=None) -> Generator[VisualizationStep, None, None]:
        """
        Determinisztikus lépésgenerátor a négyirányú forgalmi kereszteződéshez
        gyalogosátkelőkkel és hívógombokkal.
        Kezeli a konfigurált kezdeti és a runtime igényeket is.
        """
        ns_green_sec = max(1, int(self.params.get("ns_green_duration") or 3))
        ew_green_sec = max(1, int(self.params.get("ew_green_duration") or 3))
        yellow_sec = max(1, int(self.params.get("yellow_duration") or 1))
        all_red_sec = max(1, int(self.params.get("all_red_duration") or 1))
        ped_walk_sec = max(1, int(self.params.get("ped_walk_duration") or 3))
        ped_clear_sec = max(1, int(self.params.get("ped_clearance_duration") or 2))
        vehicles_count = max(0, int(self.params.get("vehicles_per_approach") if self.params.get("vehicles_per_approach") is not None else 2))
        peds_count = max(0, int(self.params.get("pedestrians_per_crossing") if self.params.get("pedestrians_per_crossing") is not None else 2))
        total_cycles = max(1, int(self.params.get("cycles") or 2))
        raw_reqs = str(self.params.get("pedestrian_requests") or "")

        vehicles, pedestrians = self._build_initial_entities(vehicles_count, peds_count)

        # Kezdeti szimulációs indításkor / reset esetén tiszta kezdeti állapotot veszünk:
        # a dinamikus paraméterben beállított igények érvényesülnek, elkerülve a korábbi futásokból maradt igényeket
        pending_requests: Set[str] = set()
        for token in raw_reqs.split(","):
            cleaned = token.strip().lower()
            if cleaned in {"north", "south", "east", "west"}:
                pending_requests.add(cleaned)

        self.runtime_requests = set(pending_requests)
        self.runtime_next_cycle_requests = set()
        next_cycle_requests: Set[str] = set()

        def get_req_states():
            return {c: (c in pending_requests or c in next_cycle_requests) for c in ["north", "south", "east", "west"]}

        cur_veh_lights = {
            "ns": {"red": True, "yellow": False, "green": False},
            "ew": {"red": True, "yellow": False, "green": False},
        }
        cur_ped_lights = {
            c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]
        }

        def count_metrics(v_snap, p_snap):
            w_veh = sum(1 for d in v_snap for v in v_snap[d] if v["status"] in ("waiting", "queued"))
            w_ped = sum(1 for c in p_snap for p in p_snap[c] if p["status"] in ("waiting", "queued"))
            passed = sum(1 for d in v_snap for v in v_snap[d] if v["status"] == "departed") +                      sum(1 for c in p_snap for p in p_snap[c] if p["status"] == "departed")
            return w_veh, w_ped, passed

        w_v, w_p, passed_cnt = count_metrics(vehicles, pedestrians)

        # 1. INIT LÉPÉS
        yield VisualizationStep(
            explanation="🚦 Négyirányú kereszteződés és gyalogosátkelők inicializálva: hívógombok és stopvonalak aktívak.",
            code_line=self.get_line_for_tag("Python", "INIT"),
            metrics={"comparisons": 0, "pass_num": 0, "remaining_time": 0, "cycle": 0},
            array=[w_v, w_p, passed_cnt],
            key="INIT",
            extra={
                "tag": "INIT",
                "phase": self.PHASE_INIT,
                "phase_hu": self.PHASE_NAMES_HU[self.PHASE_INIT],
                "operation": "INIT",
                "right_of_way": "NONE",
                "right_of_way_hu": "Kezdőállapot (Minden forgalom áll)",
                "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                "pedestrian_requests": get_req_states(),
                "pending_requests_set": list(pending_requests),
                "next_cycle_requests_set": list(next_cycle_requests),
                "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
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
            # Ciklus elején a korábbi ciklus alatt átkelés közben érkezett igények érvényesülnek
            pending_requests.update(next_cycle_requests)
            next_cycle_requests.clear()

            # 2. CIKLUSFEJ LÉPÉS
            yield VisualizationStep(
                explanation=f"🔄 {cycle_idx}. forgalmi ciklus indítása ({cycle_idx}/{total_cycles}). Ciklus kiértékelése.",
                code_line=self.get_line_for_tag("Python", "LOOP_START"),
                metrics={"comparisons": total_step_counter, "pass_num": cycle_idx, "remaining_time": 0, "cycle": cycle_idx},
                array=[w_v, w_p, passed_cnt],
                key=f"Ciklus {cycle_idx}",
                extra={
                    "tag": "LOOP_START",
                    "phase": "CYCLE_START",
                    "phase_hu": f"{cycle_idx}. Ciklus",
                    "operation": "LOOP_START",
                    "right_of_way": "NONE",
                    "right_of_way_hu": "Ciklusváltás folyamatban",
                    "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                    "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                    "pedestrian_requests": get_req_states(),
                    "pending_requests_set": list(pending_requests),
                    "next_cycle_requests_set": list(next_cycle_requests),
                    "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                    "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
                    "remaining_time": 0,
                    "duration": 0,
                    "step_duration_ms": 0,
                    "cycle": cycle_idx,
                    "total_cycles": total_cycles,
                    "step_index": total_step_counter,
                }
            )

            # Standard jármű fázisok
            phases = [
                # Phase 1: NS Vehicle Green
                (
                    self.PHASE_NS_GREEN,
                    {"red": False, "yellow": False, "green": True},
                    {"red": True, "yellow": False, "green": False},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    ns_green_sec,
                    "NORTH_SOUTH",
                    "Észak-Dél járművek (Szabad út)",
                    ["north", "south"],
                    [],
                    True,
                    False,
                ),
                # Phase 2: NS Vehicle Yellow
                (
                    self.PHASE_NS_YELLOW,
                    {"red": False, "yellow": True, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    yellow_sec,
                    "NORTH_SOUTH",
                    "Észak-Dél járművek (Sárga átmenet / Lassítás)",
                    [],
                    [],
                    False,
                    False,
                ),
                # Phase 3: Clearance 1
                (
                    self.PHASE_CLEARANCE_1,
                    {"red": True, "yellow": False, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    all_red_sec,
                    "NONE",
                    "Biztonsági kiürítés (Minden lámpa PIROS)",
                    [],
                    [],
                    False,
                    False,
                ),
                # Phase 4: EW Vehicle Green
                (
                    self.PHASE_EW_GREEN,
                    {"red": True, "yellow": False, "green": False},
                    {"red": False, "yellow": False, "green": True},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    ew_green_sec,
                    "EAST_WEST",
                    "Kelet-Nyugat járművek (Szabad út)",
                    ["east", "west"],
                    [],
                    True,
                    False,
                ),
                # Phase 5: EW Vehicle Yellow
                (
                    self.PHASE_EW_YELLOW,
                    {"red": True, "yellow": False, "green": False},
                    {"red": False, "yellow": True, "green": False},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    yellow_sec,
                    "EAST_WEST",
                    "Kelet-Nyugat járművek (Sárga átmenet / Lassítás)",
                    [],
                    [],
                    False,
                    False,
                ),
                # Phase 6: Clearance 2
                (
                    self.PHASE_CLEARANCE_2,
                    {"red": True, "yellow": False, "green": False},
                    {"red": True, "yellow": False, "green": False},
                    {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    all_red_sec,
                    "NONE",
                    "Biztonsági kiürítés gyalogos fázis előtt (Minden PIROS)",
                    [],
                    [],
                    False,
                    False,
                ),
            ]

            # Futtassuk a járműfázisokat
            for phase_id, ns_light, ew_light, ped_light_map, duration, row_id, row_hu, moving_veh_dirs, moving_ped_crossings, veh_is_green, ped_is_green in phases:
                cur_veh_lights = {"ns": dict(ns_light), "ew": dict(ew_light)}
                cur_ped_lights = {c: dict(l) for c, l in ped_light_map.items()}

                for sec in range(duration, 0, -1):
                    tick_events = self._generate_tick_events(
                        sec, duration, row_hu, vehicles, pedestrians,
                        moving_veh_dirs, moving_ped_crossings,
                        veh_is_green, ped_is_green, pending_requests
                    )

                    for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(tick_events):
                        total_step_counter += 1
                        is_last_in_tick = (ev_idx == len(tick_events) - 1)
                        step_duration = 1000 if is_last_in_tick else 0
                        w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                        explanation = f"{act_desc} Hátralévő fázisidő: {sec} mp."

                        yield VisualizationStep(
                            explanation=explanation,
                            code_line=self.get_line_for_tag("Python", sem_tag),
                            metrics={
                                "comparisons": total_step_counter,
                                "pass_num": cycle_idx,
                                "remaining_time": sec,
                                "cycle": cycle_idx,
                            },
                            array=[w_v, w_p, passed_cnt],
                            key=self.PHASE_NAMES_HU[phase_id],
                            extra={
                                "tag": sem_tag,
                                "phase": phase_id,
                                "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                "operation": sem_tag,
                                "right_of_way": row_id,
                                "right_of_way_hu": row_hu,
                                "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                "pedestrian_requests": get_req_states(),
                                "pending_requests_set": list(pending_requests),
                                "next_cycle_requests_set": list(next_cycle_requests),
                                "vehicles": v_snap,
                                "pedestrians": p_snap,
                                "remaining_time": sec,
                                "duration": duration,
                                "step_duration_ms": step_duration,
                                "cycle": cycle_idx,
                                "total_cycles": total_cycles,
                                "step_index": total_step_counter,
                            }
                        )

            # Gyalogos fázis ütemezése:
            # Csak akkor ütemezzük a gyalogos zöld és kiürítési fázist, ha van aktív igény!
            # Ha nincs igény, kihagyjuk a felesleges várakozást.
            if pending_requests:
                active_crossings_to_service = set(pending_requests)
                # Kiszolgálás: a zöldet kapó átkelők kérése teljesül
                pending_requests.difference_update(active_crossings_to_service)

                ped_phases = [
                    # Phase 7: Pedestrian Walk
                    (
                        self.PHASE_PED_WALK,
                        {"red": True, "yellow": False, "green": False},
                        {"red": True, "yellow": False, "green": False},
                        {c: {"red": (c not in active_crossings_to_service), "green": (c in active_crossings_to_service)} for c in ["north", "south", "east", "west"]},
                        ped_walk_sec,
                        "PEDESTRIANS",
                        "Gyalogos forgalom (ZÖLD jelzés az igényelt átkelőkön)",
                        [],
                        list(active_crossings_to_service),
                        False,
                        True,
                    ),
                    # Phase 8: Pedestrian Clearance
                    (
                        self.PHASE_PED_CLEARANCE,
                        {"red": True, "yellow": False, "green": False},
                        {"red": True, "yellow": False, "green": False},
                        {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                        ped_clear_sec,
                        "PEDESTRIANS",
                        "Gyalogos kiürítés (Jelzőlámpák PIROSAK, átkelők befejezése)",
                        [],
                        [],
                        False,
                        False,
                    ),
                    # Phase 9: Clearance 3
                    (
                        self.PHASE_CLEARANCE_3,
                        {"red": True, "yellow": False, "green": False},
                        {"red": True, "yellow": False, "green": False},
                        {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                        all_red_sec,
                        "NONE",
                        "Biztonsági kiürítés új ciklus előtt (Minden PIROS)",
                        [],
                        [],
                        False,
                        False,
                    ),
                ]

                for phase_id, ns_light, ew_light, ped_light_map, duration, row_id, row_hu, moving_veh_dirs, moving_ped_crossings, veh_is_green, ped_is_green in ped_phases:
                    cur_veh_lights = {"ns": dict(ns_light), "ew": dict(ew_light)}
                    cur_ped_lights = {c: dict(l) for c, l in ped_light_map.items()}

                    for sec in range(duration, 0, -1):
                        tick_events = self._generate_tick_events(
                            sec, duration, row_hu, vehicles, pedestrians,
                            moving_veh_dirs, moving_ped_crossings,
                            veh_is_green, ped_is_green, pending_requests
                        )

                        for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(tick_events):
                            total_step_counter += 1
                            is_last_in_tick = (ev_idx == len(tick_events) - 1)
                            step_duration = 1000 if is_last_in_tick else 0
                            w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                            explanation = f"{act_desc} Hátralévő fázisidő: {sec} mp."

                            yield VisualizationStep(
                                explanation=explanation,
                                code_line=self.get_line_for_tag("Python", sem_tag),
                                metrics={
                                    "comparisons": total_step_counter,
                                    "pass_num": cycle_idx,
                                    "remaining_time": sec,
                                    "cycle": cycle_idx,
                                },
                                array=[w_v, w_p, passed_cnt],
                                key=self.PHASE_NAMES_HU[phase_id],
                                extra={
                                    "tag": sem_tag,
                                    "phase": phase_id,
                                    "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                    "operation": sem_tag,
                                    "right_of_way": row_id,
                                    "right_of_way_hu": row_hu,
                                    "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                    "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                    "pedestrian_requests": get_req_states(),
                                    "pending_requests_set": list(pending_requests),
                                    "next_cycle_requests_set": list(next_cycle_requests),
                                    "vehicles": v_snap,
                                    "pedestrians": p_snap,
                                    "remaining_time": sec,
                                    "duration": duration,
                                    "step_duration_ms": step_duration,
                                    "cycle": cycle_idx,
                                    "total_cycles": total_cycles,
                                    "step_index": total_step_counter,
                                }
                            )

        # 3. COMPLETE LÉPÉS
        yield VisualizationStep(
            explanation=f"✅ Kereszteződés és gyalogos szimuláció befejeződött: {total_cycles} ciklus sikeresen lefutott, teljes forgalom koordinálva.",
            code_line=self.get_line_for_tag("Python", "COMPLETE"),
            metrics={"comparisons": total_step_counter, "pass_num": total_cycles, "remaining_time": 0, "cycle": total_cycles},
            array=[w_v, w_p, passed_cnt],
            key="KÉSZ",
            extra={
                "tag": "COMPLETE",
                "phase": self.PHASE_COMPLETED,
                "phase_hu": self.PHASE_NAMES_HU[self.PHASE_COMPLETED],
                "operation": "COMPLETE",
                "right_of_way": "NONE",
                "right_of_way_hu": "Szimuláció véget ért",
                "vehicle_lights": {
                    "ns": {"red": True, "yellow": False, "green": False},
                    "ew": {"red": True, "yellow": False, "green": False},
                },
                "pedestrian_lights": {
                    c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]
                },
                "pedestrian_requests": get_req_states(),
                "pending_requests_set": list(pending_requests),
                "next_cycle_requests_set": list(next_cycle_requests),
                "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": total_cycles,
                "total_cycles": total_cycles,
                "step_index": total_step_counter,
            }
        )

    def _generate_tick_events(
        self,
        sec: int,
        duration: int,
        row_hu: str,
        vehicles: Dict[str, List[Dict[str, Any]]],
        pedestrians: Dict[str, List[Dict[str, Any]]],
        moving_veh_dirs: List[str],
        moving_ped_crossings: List[str],
        veh_is_green: bool,
        ped_is_green: bool,
        pending_requests: Set[str]
    ) -> List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]]:
        tick_events: List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]] = []

        # 1. Igények lekérdezése / ellenőrzése
        if sec == duration:
            req_str = ", ".join(sorted(list(pending_requests))) if pending_requests else "nincs aktív igény"
            tick_events.append((
                "POLL_REQUESTS",
                f"🔘 Gyalogos hívógomb igények kiértékelése: {req_str}.",
                {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
            ))

            # 2. Jelzőlámpák beállítása
            tick_events.append((
                "SET_SIGNALS",
                f"🚦 Összesített jelzőlámpák beállítása: {row_hu}. Fázisidő: {duration} mp.",
                {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
            ))

        # 3. Kereszteződésben lévő járművek és gyalogosok továbbhaladása és távozása
        for d in ["north", "south", "east", "west"]:
            for v in vehicles[d]:
                if v["status"] == "crossing":
                    v["crossing_progress"] += 1
                    if v["crossing_progress"] >= 3:
                        v["status"] = "departed"

        for c in ["north", "south", "east", "west"]:
            for p in pedestrians[c]:
                if p["status"] == "crossing":
                    p["crossing_progress"] += 1
                    if p["crossing_progress"] >= 3:
                        p["status"] = "departed"

        tick_events.append((
            "PROCESS_CROSSINGS",
            f"🚶🚗 Áthaladó járművek és gyalogosok továbbhaladása ({row_hu}).",
            {d: [dict(v) for v in vehicles[d]] for d in vehicles},
            {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
        ))

        # 4. Ütközés- és konfliktusmentesség ellenőrzése
        veh_conflicts = False
        for d in moving_veh_dirs:
            conflicting_veh_dirs = ["east", "west"] if d in ["north", "south"] else ["north", "south"]
            if any(cv["status"] == "crossing" for cd in conflicting_veh_dirs for cv in vehicles[cd]):
                veh_conflicts = True
                break
            conflicting_peds = ["north", "south"] if d in ["north", "south"] else ["east", "west"]
            if any(cp["status"] == "crossing" for c in conflicting_peds for cp in pedestrians[c]):
                veh_conflicts = True
                break

        ped_conflicts = False
        for c in moving_ped_crossings:
            conflicting_vdirs = ["north", "south"] if c in ["north", "south"] else ["east", "west"]
            if any(cv["status"] == "crossing" for cd in conflicting_vdirs for cv in vehicles[cd]):
                ped_conflicts = True
                break

        has_conflict = veh_conflicts or ped_conflicts
        movement_allowed = (veh_is_green and not has_conflict) or (ped_is_green and not has_conflict)

        conflict_desc = "Biztonsági ellenőrzés: Ütközésmentes áthaladás engedélyezve." if movement_allowed else "Biztonsági ellenőrzés: Konfliktus vagy tilos jelzés, belépés tiltva."
        tick_events.append((
            "CHECK_CONFLICTS",
            f"🔍 {conflict_desc}",
            {d: [dict(v) for v in vehicles[d]] for d in vehicles},
            {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
        ))

        # 5. Indítás és sor előreléptetés vagy megállítás
        if movement_allowed:
            if veh_is_green:
                for d in moving_veh_dirs:
                    for v in vehicles[d]:
                        if v["status"] == "waiting" and v["queue_pos"] == 0:
                            v["status"] = "crossing"
                            v["crossing_progress"] = 1
                            break

            if ped_is_green:
                for c in moving_ped_crossings:
                    for p in pedestrians[c]:
                        if p["status"] == "waiting" and p["queue_pos"] == 0:
                            p["status"] = "crossing"
                            p["crossing_progress"] = 1
                            break

            tick_events.append((
                "START_MOVEMENTS",
                f"🟢 Zöld jelzés: Engedélyezett forgalom belép az átkelőbe / kereszteződésbe ({row_hu}).",
                {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
            ))

            if veh_is_green:
                for d in moving_veh_dirs:
                    for v in vehicles[d]:
                        if v["status"] == "queued":
                            v["queue_pos"] -= 1
                            if v["queue_pos"] == 0:
                                v["status"] = "waiting"

            if ped_is_green:
                for c in moving_ped_crossings:
                    for p in pedestrians[c]:
                        if p["status"] == "queued":
                            p["queue_pos"] -= 1
                            if p["queue_pos"] == 0:
                                p["status"] = "waiting"

            tick_events.append((
                "ADVANCE_QUEUES",
                f"➡️ Várakozó sorok előrelépése a stopvonalhoz / járdaszegélyhez ({row_hu}).",
                {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
            ))
        else:
            tick_events.append((
                "HOLD_TRAFFIC",
                f"⛔ Tilos jelzés vagy kiürítés: Forgalom visszatartása a megállás vonalánál ({row_hu}).",
                {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
            ))

        return tick_events

    def generate_future_steps_from_step(self, current_step: VisualizationStep, current_index: int) -> List[VisualizationStep]:
        """
        Újragenerálja a jövőbeli szimulációs lépéseket az aktuális állapot pillanatképéből
        az újonnan beérkezett gyalogos igények azonnali figyelembevételével.
        Garantálja, hogy a már lefutott fázisok vagy másodpercek nem ismétlődnek meg,
        a hátralévő fázisidő pontosan megmarad, és nincsenek átfedő vagy elvesző események.
        """
        extra = getattr(current_step, 'extra', {}) or {}
        cur_tag = extra.get('tag', 'INIT')
        cur_phase = extra.get('phase', self.PHASE_INIT)
        cur_rem_time = extra.get('remaining_time', 0)
        cur_cycle = extra.get('cycle', 0)
        total_cycles = extra.get('total_cycles', 2)
        step_duration_ms = extra.get('step_duration_ms', 1000)

        vehicles = {
            d: [dict(v) for v in extra.get('vehicles', {}).get(d, [])]
            for d in ["north", "south", "east", "west"]
        }
        pedestrians = {
            c: [dict(p) for p in extra.get('pedestrians', {}).get(c, [])]
            for c in ["north", "south", "east", "west"]
        }

        pending_requests: Set[str] = set(self.runtime_requests)
        next_cycle_requests: Set[str] = set(self.runtime_next_cycle_requests)

        ns_green_sec = max(1, int(self.params.get("ns_green_duration") or 3))
        ew_green_sec = max(1, int(self.params.get("ew_green_duration") or 3))
        yellow_sec = max(1, int(self.params.get("yellow_duration") or 1))
        all_red_sec = max(1, int(self.params.get("all_red_duration") or 1))
        ped_walk_sec = max(1, int(self.params.get("ped_walk_duration") or 3))
        ped_clear_sec = max(1, int(self.params.get("ped_clearance_duration") or 2))

        future_steps: List[VisualizationStep] = []
        step_counter = current_index

        def count_metrics(v_snap, p_snap):
            w_veh = sum(1 for d in v_snap for v in v_snap[d] if v["status"] in ("waiting", "queued"))
            w_ped = sum(1 for c in p_snap for p in p_snap[c] if p["status"] in ("waiting", "queued"))
            passed = sum(1 for d in v_snap for v in v_snap[d] if v["status"] == "departed") +                      sum(1 for c in p_snap for p in p_snap[c] if p["status"] == "departed")
            return w_veh, w_ped, passed

        def get_req_states():
            return {c: (c in pending_requests or c in next_cycle_requests) for c in ["north", "south", "east", "west"]}

        def get_cycle_vehicle_phases():
            return [
                (self.PHASE_NS_GREEN, {"red": False, "yellow": False, "green": True}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, ns_green_sec, "NORTH_SOUTH", "Észak-Dél járművek (Szabad út)", ["north", "south"], [], True, False),
                (self.PHASE_NS_YELLOW, {"red": False, "yellow": True, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, yellow_sec, "NORTH_SOUTH", "Észak-Dél járművek (Sárga átmenet / Lassítás)", [], [], False, False),
                (self.PHASE_CLEARANCE_1, {"red": True, "yellow": False, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, all_red_sec, "NONE", "Biztonsági kiürítés (Minden lámpa PIROS)", [], [], False, False),
                (self.PHASE_EW_GREEN, {"red": True, "yellow": False, "green": False}, {"red": False, "yellow": False, "green": True}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, ew_green_sec, "EAST_WEST", "Kelet-Nyugat járművek (Szabad út)", ["east", "west"], [], True, False),
                (self.PHASE_EW_YELLOW, {"red": True, "yellow": False, "green": False}, {"red": False, "yellow": True, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, yellow_sec, "EAST_WEST", "Kelet-Nyugat járművek (Sárga átmenet / Lassítás)", [], [], False, False),
                (self.PHASE_CLEARANCE_2, {"red": True, "yellow": False, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, all_red_sec, "NONE", "Biztonsági kiürítés gyalogos fázis előtt (Minden PIROS)", [], [], False, False),
            ]

        def get_cycle_ped_phases(active_serviced):
            return [
                (self.PHASE_PED_WALK, {"red": True, "yellow": False, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": (c not in active_serviced), "green": (c in active_serviced)} for c in ["north", "south", "east", "west"]}, ped_walk_sec, "PEDESTRIANS", "Gyalogos forgalom (ZÖLD jelzés az igényelt átkelőkön)", [], list(active_serviced), False, True),
                (self.PHASE_PED_CLEARANCE, {"red": True, "yellow": False, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, ped_clear_sec, "PEDESTRIANS", "Gyalogos kiürítés (Jelzőlámpák PIROSAK, átkelők befejezése)", [], [], False, False),
                (self.PHASE_CLEARANCE_3, {"red": True, "yellow": False, "green": False}, {"red": True, "yellow": False, "green": False}, {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]}, all_red_sec, "NONE", "Biztonsági kiürítés új ciklus előtt (Minden PIROS)", [], [], False, False),
            ]

        # Kezdő ciklus meghatározása
        start_cycle = max(1, cur_cycle if cur_cycle > 0 else 1)

        # Ha INIT fázisban voltunk, kiadjuk a ciklusfejet
        if cur_tag == 'INIT':
            step_counter += 1
            w_v, w_p, passed_cnt = count_metrics(vehicles, pedestrians)
            future_steps.append(VisualizationStep(
                explanation=f"🔄 1. forgalmi ciklus indítása (1/{total_cycles}). Ciklus kiértékelése.",
                code_line=self.get_line_for_tag("Python", "LOOP_START"),
                metrics={"comparisons": step_counter, "pass_num": 1, "remaining_time": 0, "cycle": 1},
                array=[w_v, w_p, passed_cnt],
                key="Ciklus 1",
                extra={
                    "tag": "LOOP_START",
                    "phase": "CYCLE_START",
                    "phase_hu": "1. Ciklus",
                    "operation": "LOOP_START",
                    "right_of_way": "NONE",
                    "right_of_way_hu": "Ciklusváltás folyamatban",
                    "vehicle_lights": {"ns": {"red": True, "yellow": False, "green": False}, "ew": {"red": True, "yellow": False, "green": False}},
                    "pedestrian_lights": {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                    "pedestrian_requests": get_req_states(),
                    "pending_requests_set": list(pending_requests),
                    "next_cycle_requests_set": list(next_cycle_requests),
                    "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                    "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
                    "remaining_time": 0,
                    "duration": 0,
                    "step_duration_ms": 0,
                    "cycle": 1,
                    "total_cycles": total_cycles,
                    "step_index": step_counter,
                }
            ))

        c_idx = start_cycle
        while c_idx <= total_cycles or next_cycle_requests:
            effective_total_cycles = max(total_cycles, c_idx if not next_cycle_requests else c_idx + 1)
            if c_idx > start_cycle:
                pending_requests.update(next_cycle_requests)
                next_cycle_requests.clear()

                step_counter += 1
                w_v, w_p, passed_cnt = count_metrics(vehicles, pedestrians)
                future_steps.append(VisualizationStep(
                    explanation=f"🔄 {c_idx}. forgalmi ciklus indítása ({c_idx}/{total_cycles}). Ciklus kiértékelése.",
                    code_line=self.get_line_for_tag("Python", "LOOP_START"),
                    metrics={"comparisons": step_counter, "pass_num": c_idx, "remaining_time": 0, "cycle": c_idx},
                    array=[w_v, w_p, passed_cnt],
                    key=f"Ciklus {c_idx}",
                    extra={
                        "tag": "LOOP_START",
                        "phase": "CYCLE_START",
                        "phase_hu": f"{c_idx}. Ciklus",
                        "operation": "LOOP_START",
                        "right_of_way": "NONE",
                        "right_of_way_hu": "Ciklusváltás folyamatban",
                        "vehicle_lights": {"ns": {"red": True, "yellow": False, "green": False}, "ew": {"red": True, "yellow": False, "green": False}},
                        "pedestrian_lights": {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                        "pedestrian_requests": get_req_states(),
                        "pending_requests_set": list(pending_requests),
                        "next_cycle_requests_set": list(next_cycle_requests),
                        "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                        "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
                        "remaining_time": 0,
                        "duration": 0,
                        "step_duration_ms": 0,
                        "cycle": c_idx,
                        "total_cycles": total_cycles,
                        "step_index": step_counter,
                    }
                ))

            v_phases = get_cycle_vehicle_phases()
            v_phase_ids = [p[0] for p in v_phases]

            # Határozzuk meg a járműfázisok kezdőpontját az aktuális ciklusban
            start_v_idx = 0
            is_in_ped_phase_currently = False

            if c_idx == start_cycle and cur_phase in v_phase_ids:
                start_v_idx = v_phase_ids.index(cur_phase)
            elif c_idx == start_cycle and cur_phase in (self.PHASE_PED_WALK, self.PHASE_PED_CLEARANCE, self.PHASE_CLEARANCE_3):
                is_in_ped_phase_currently = True
                start_v_idx = len(v_phases)  # Járműfázisok ezen ciklusban már lefutottak

            if not is_in_ped_phase_currently:
                for p_idx in range(start_v_idx, len(v_phases)):
                    phase_id, ns_light, ew_light, ped_light_map, duration, row_id, row_hu, moving_veh_dirs, moving_ped_crossings, veh_is_green, ped_is_green = v_phases[p_idx]
                    cur_veh_lights = {"ns": dict(ns_light), "ew": dict(ew_light)}
                    cur_ped_lights = {c: dict(l) for c, l in ped_light_map.items()}

                    if c_idx == start_cycle and p_idx == start_v_idx and cur_phase == phase_id:
                        # Ugyanabban a fázisban vagyunk:
                        # 1. Ha a jelenlegi lépés a tick KÖZEPÉN állt (step_duration_ms == 0),
                        #    generáljuk le a jelenlegi másodperc HÁTRALÉVŐ rész-eseményeit!
                        if step_duration_ms == 0 and cur_rem_time >= 1:
                            tick_events = self._generate_tick_events(
                                cur_rem_time, duration, row_hu, vehicles, pedestrians,
                                moving_veh_dirs, moving_ped_crossings,
                                veh_is_green, ped_is_green, pending_requests
                            )
                            # Megkeressük, hol állt a jelenlegi esemény
                            cur_ev_idx = -1
                            for idx, (stag, _, _, _) in enumerate(tick_events):
                                if stag == cur_tag:
                                    cur_ev_idx = idx
                                    break
                            remaining_events = tick_events[cur_ev_idx + 1:] if cur_ev_idx >= 0 else []
                            for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(remaining_events):
                                step_counter += 1
                                is_last_in_tick = (ev_idx == len(remaining_events) - 1)
                                step_dur = 1000 if is_last_in_tick else 0
                                w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                                future_steps.append(VisualizationStep(
                                    explanation=f"{act_desc} Hátralévő fázisidő: {cur_rem_time} mp.",
                                    code_line=self.get_line_for_tag("Python", sem_tag),
                                    metrics={"comparisons": step_counter, "pass_num": c_idx, "remaining_time": cur_rem_time, "cycle": c_idx},
                                    array=[w_v, w_p, passed_cnt],
                                    key=self.PHASE_NAMES_HU[phase_id],
                                    extra={
                                        "tag": sem_tag, "phase": phase_id, "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                        "operation": sem_tag, "right_of_way": row_id, "right_of_way_hu": row_hu,
                                        "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                        "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                        "pedestrian_requests": get_req_states(),
                                        "pending_requests_set": list(pending_requests),
                                        "next_cycle_requests_set": list(next_cycle_requests),
                                        "vehicles": v_snap, "pedestrians": p_snap,
                                        "remaining_time": cur_rem_time, "duration": duration,
                                        "step_duration_ms": step_dur, "cycle": c_idx, "total_cycles": total_cycles,
                                        "step_index": step_counter,
                                    }
                                ))
                        # 2. A hátralévő teljes másodpercek
                        start_sec = cur_rem_time - 1
                    else:
                        start_sec = duration

                    for sec in range(start_sec, 0, -1):
                        tick_events = self._generate_tick_events(
                            sec, duration, row_hu, vehicles, pedestrians,
                            moving_veh_dirs, moving_ped_crossings,
                            veh_is_green, ped_is_green, pending_requests
                        )
                        for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(tick_events):
                            step_counter += 1
                            is_last_in_tick = (ev_idx == len(tick_events) - 1)
                            step_dur = 1000 if is_last_in_tick else 0
                            w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                            future_steps.append(VisualizationStep(
                                explanation=f"{act_desc} Hátralévő fázisidő: {sec} mp.",
                                code_line=self.get_line_for_tag("Python", sem_tag),
                                metrics={"comparisons": step_counter, "pass_num": c_idx, "remaining_time": sec, "cycle": c_idx},
                                array=[w_v, w_p, passed_cnt],
                                key=self.PHASE_NAMES_HU[phase_id],
                                extra={
                                    "tag": sem_tag, "phase": phase_id, "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                    "operation": sem_tag, "right_of_way": row_id, "right_of_way_hu": row_hu,
                                    "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                    "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                    "pedestrian_requests": get_req_states(),
                                    "pending_requests_set": list(pending_requests),
                                    "next_cycle_requests_set": list(next_cycle_requests),
                                    "vehicles": v_snap, "pedestrians": p_snap,
                                    "remaining_time": sec, "duration": duration,
                                    "step_duration_ms": step_dur, "cycle": c_idx, "total_cycles": total_cycles,
                                    "step_index": step_counter,
                                }
                            ))

            # Gyalogos fázisok lefutása: kizárólag érvényes, igényelt átkelők kaphatnak zöldet!
            # Ha éppen aktív gyalogos fázisban vagyunk (újragenerálás közben), a már zöld átkelőket tartjuk meg.
            # SOHA nem kapcsolunk be minden átkelőt alapértelmezetten (nincs all-four-green fallback)!
            if pending_requests or is_in_ped_phase_currently:
                if is_in_ped_phase_currently:
                    # Megőrizzük az éppen aktív gyalogos fázisban futó zöld átkelőket
                    active_serviced = set(extra.get('active_crossings', []))
                    if not active_serviced and cur_phase == self.PHASE_PED_WALK:
                        active_serviced = {c for c, l in extra.get('pedestrian_lights', {}).items() if l.get('green')}
                else:
                    active_serviced = set(pending_requests)
                    pending_requests.difference_update(active_serviced)

                ped_phases = get_cycle_ped_phases(active_serviced)
                ped_phase_ids = [p[0] for p in ped_phases]

                start_p_idx = 0
                if is_in_ped_phase_currently and cur_phase in ped_phase_ids:
                    start_p_idx = ped_phase_ids.index(cur_phase)

                for p_idx in range(start_p_idx, len(ped_phases)):
                    phase_id, ns_light, ew_light, ped_light_map, duration, row_id, row_hu, moving_veh_dirs, moving_ped_crossings, veh_is_green, ped_is_green = ped_phases[p_idx]
                    cur_veh_lights = {"ns": dict(ns_light), "ew": dict(ew_light)}
                    cur_ped_lights = {c: dict(l) for c, l in ped_light_map.items()}

                    if is_in_ped_phase_currently and p_idx == start_p_idx and cur_phase == phase_id:
                        if step_duration_ms == 0 and cur_rem_time >= 1:
                            tick_events = self._generate_tick_events(
                                cur_rem_time, duration, row_hu, vehicles, pedestrians,
                                moving_veh_dirs, moving_ped_crossings,
                                veh_is_green, ped_is_green, pending_requests
                            )
                            cur_ev_idx = -1
                            for idx, (stag, _, _, _) in enumerate(tick_events):
                                if stag == cur_tag:
                                    cur_ev_idx = idx
                                    break
                            remaining_events = tick_events[cur_ev_idx + 1:] if cur_ev_idx >= 0 else []
                            for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(remaining_events):
                                step_counter += 1
                                is_last_in_tick = (ev_idx == len(remaining_events) - 1)
                                step_dur = 1000 if is_last_in_tick else 0
                                w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                                future_steps.append(VisualizationStep(
                                    explanation=f"{act_desc} Hátralévő fázisidő: {cur_rem_time} mp.",
                                    code_line=self.get_line_for_tag("Python", sem_tag),
                                    metrics={"comparisons": step_counter, "pass_num": c_idx, "remaining_time": cur_rem_time, "cycle": c_idx},
                                    array=[w_v, w_p, passed_cnt],
                                    key=self.PHASE_NAMES_HU[phase_id],
                                    extra={
                                        "tag": sem_tag, "phase": phase_id, "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                        "operation": sem_tag, "right_of_way": row_id, "right_of_way_hu": row_hu,
                                        "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                        "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                        "pedestrian_requests": get_req_states(),
                                        "pending_requests_set": list(pending_requests),
                                        "next_cycle_requests_set": list(next_cycle_requests),
                                        "vehicles": v_snap, "pedestrians": p_snap,
                                        "remaining_time": cur_rem_time, "duration": duration,
                                        "step_duration_ms": step_dur, "cycle": c_idx, "total_cycles": total_cycles,
                                        "step_index": step_counter,
                                    }
                                ))
                        start_sec = cur_rem_time - 1
                    else:
                        start_sec = duration

                    for sec in range(start_sec, 0, -1):
                        tick_events = self._generate_tick_events(
                            sec, duration, row_hu, vehicles, pedestrians,
                            moving_veh_dirs, moving_ped_crossings,
                            veh_is_green, ped_is_green, pending_requests
                        )
                        for ev_idx, (sem_tag, act_desc, v_snap, p_snap) in enumerate(tick_events):
                            step_counter += 1
                            is_last_in_tick = (ev_idx == len(tick_events) - 1)
                            step_dur = 1000 if is_last_in_tick else 0
                            w_v, w_p, passed_cnt = count_metrics(v_snap, p_snap)
                            future_steps.append(VisualizationStep(
                                explanation=f"{act_desc} Hátralévő fázisidő: {sec} mp.",
                                code_line=self.get_line_for_tag("Python", sem_tag),
                                metrics={"comparisons": step_counter, "pass_num": c_idx, "remaining_time": sec, "cycle": c_idx},
                                array=[w_v, w_p, passed_cnt],
                                key=self.PHASE_NAMES_HU[phase_id],
                                extra={
                                    "tag": sem_tag, "phase": phase_id, "phase_hu": self.PHASE_NAMES_HU[phase_id],
                                    "operation": sem_tag, "right_of_way": row_id, "right_of_way_hu": row_hu,
                                    "vehicle_lights": {k: dict(v) for k, v in cur_veh_lights.items()},
                                    "pedestrian_lights": {k: dict(v) for k, v in cur_ped_lights.items()},
                                    "pedestrian_requests": get_req_states(),
                                    "pending_requests_set": list(pending_requests),
                                    "next_cycle_requests_set": list(next_cycle_requests),
                                    "vehicles": v_snap, "pedestrians": p_snap,
                                    "remaining_time": sec, "duration": duration,
                                    "step_duration_ms": step_dur, "cycle": c_idx, "total_cycles": total_cycles,
                                    "step_index": step_counter,
                                }
                            ))

            is_in_ped_phase_currently = False
            c_idx += 1

        # COMPLETE LÉPÉS
        step_counter += 1
        w_v, w_p, passed_cnt = count_metrics(vehicles, pedestrians)
        future_steps.append(VisualizationStep(
            explanation=f"✅ Kereszteződés és gyalogos szimuláció befejeződött: {total_cycles} ciklus sikeresen lefutott, teljes forgalom koordinálva.",
            code_line=self.get_line_for_tag("Python", "COMPLETE"),
            metrics={"comparisons": step_counter, "pass_num": total_cycles, "remaining_time": 0, "cycle": total_cycles},
            array=[w_v, w_p, passed_cnt],
            key="KÉSZ",
            extra={
                "tag": "COMPLETE",
                "phase": self.PHASE_COMPLETED,
                "phase_hu": self.PHASE_NAMES_HU[self.PHASE_COMPLETED],
                "operation": "COMPLETE",
                "right_of_way": "NONE",
                "right_of_way_hu": "Szimuláció véget ért",
                "vehicle_lights": {"ns": {"red": True, "yellow": False, "green": False}, "ew": {"red": True, "yellow": False, "green": False}},
                "pedestrian_lights": {c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]},
                "pedestrian_requests": get_req_states(),
                "pending_requests_set": list(pending_requests),
                "next_cycle_requests_set": list(next_cycle_requests),
                "vehicles": {d: [dict(v) for v in vehicles[d]] for d in vehicles},
                "pedestrians": {c: [dict(p) for p in pedestrians[c]] for c in pedestrians},
                "remaining_time": 0,
                "duration": 0,
                "step_duration_ms": 1000,
                "cycle": total_cycles,
                "total_cycles": total_cycles,
                "step_index": step_counter,
            }
        ))

        return future_steps
