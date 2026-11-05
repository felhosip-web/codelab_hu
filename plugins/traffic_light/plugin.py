# -*- coding: utf-8 -*-
"""
Traffic Light Educational Plugin - Phase 1
Oktatási jelzőlámpa szimuláció valós idejű kód- és végrehajtássor-követéssel.
"""
from typing import Dict, Generator, List, Optional
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

# 1-based logikai kód-fázis sorcímkék a 6 támogatott nyelvhez
LOGICAL_TAG_LINES: Dict[str, Dict[str, int]] = {
    "Python": {
        "INIT": 2,
        "LOOP_START": 4,
        "RED": 6,
        "RED_YELLOW": 8,
        "GREEN": 10,
        "YELLOW": 12,
        "COMPLETE": 14,
    },
    "C++": {
        "INIT": 3,
        "LOOP_START": 5,
        "RED": 7,
        "RED_YELLOW": 9,
        "GREEN": 11,
        "YELLOW": 13,
        "COMPLETE": 15,
    },
    "C": {
        "INIT": 4,
        "LOOP_START": 6,
        "RED": 8,
        "RED_YELLOW": 10,
        "GREEN": 12,
        "YELLOW": 14,
        "COMPLETE": 16,
    },
    "BASIC": {
        "INIT": 2,
        "LOOP_START": 4,
        "RED": 6,
        "RED_YELLOW": 8,
        "GREEN": 10,
        "YELLOW": 12,
        "COMPLETE": 14,
    },
    "Java": {
        "INIT": 4,
        "LOOP_START": 6,
        "RED": 8,
        "RED_YELLOW": 10,
        "GREEN": 12,
        "YELLOW": 14,
        "COMPLETE": 16,
    },
    "Pascal": {
        "INIT": 7,
        "LOOP_START": 8,
        "RED": 11,
        "RED_YELLOW": 13,
        "GREEN": 15,
        "YELLOW": 17,
        "COMPLETE": 19,
    },
}

CODE_TEMPLATES: Dict[str, str] = {
    "Python": """# Oktatási Jelzőlámpa Szimuláció - 1. Fázis
state = "INIT"

for cycle in range(1, total_cycles + 1):
    # 1. Piros jelzés: Megállás!
    state = set_signal(red=True, yellow=False, green=False, duration=red_sec)
    # 2. Piros-sárga jelzés: Felkészülés az indulásra
    state = set_signal(red=True, yellow=True, green=False, duration=ry_sec)
    # 3. Zöld jelzés: Szabad út, áthaladás
    state = set_signal(red=False, yellow=False, green=True, duration=green_sec)
    # 4. Sárga jelzés: Figyelem, felkészülés a megállásra
    state = set_signal(red=False, yellow=True, green=False, duration=yellow_sec)

state = "COMPLETED"
""",
    "C++": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
#include <iostream>
std::string state = "INIT";

for (int cycle = 1; cycle <= totalCycles; ++cycle) {
    // 1. Piros jelzés: Megállás!
    state = setSignal(true, false, false, redSec);
    // 2. Piros-sárga jelzés: Felkészülés az indulásra
    state = setSignal(true, true, false, rySec);
    // 3. Zöld jelzés: Szabad út, áthaladás
    state = setSignal(false, false, true, greenSec);
    // 4. Sárga jelzés: Figyelem, megállás előkészítése
    state = setSignal(false, true, false, yellowSec);
}
state = "COMPLETED";
""",
    "C": """/* Oktatási Jelzőlámpa Szimuláció (Phase 1) */
#include <stdio.h>
int cycle;
const char* state = "INIT";

for (cycle = 1; cycle <= total_cycles; cycle++) {
    /* 1. Piros jelzés: Megállás */
    state = set_signal(1, 0, 0, red_sec);
    /* 2. Piros-sárga jelzés: Felkészülés */
    state = set_signal(1, 1, 0, ry_sec);
    /* 3. Zöld jelzés: Áthaladás */
    state = set_signal(0, 0, 1, green_sec);
    /* 4. Sárga jelzés: Figyelem */
    state = set_signal(0, 1, 0, yellow_sec);
}
state = "COMPLETED";
""",
    "BASIC": """' Oktatási Jelzőlámpa Szimuláció (Phase 1)
STATE$ = "INIT"

FOR CYCLE = 1 TO TOTALCYCLES
    ' 1. Piros jelzés: Megállás!
    CALL SetSignal(1, 0, 0, RedSec)
    ' 2. Piros-sárga: Felkészülés
    CALL SetSignal(1, 1, 0, RySec)
    ' 3. Zöld jelzés: Szabad út
    CALL SetSignal(0, 0, 1, GreenSec)
    ' 4. Sárga jelzés: Figyelem
    CALL SetSignal(0, 1, 0, YellowSec)
NEXT CYCLE
STATE$ = "COMPLETED"
""",
    "Java": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
public class TrafficLight {
    public void runSimulation(int totalCycles) {
        String state = "INIT";

        for (int cycle = 1; cycle <= totalCycles; cycle++) {
            // 1. Piros jelzés: Megállás!
            state = setSignal(true, false, false, redSec);
            // 2. Piros-sárga jelzés: Felkészülés
            state = setSignal(true, true, false, rySec);
            // 3. Zöld jelzés: Szabad út
            state = setSignal(false, false, true, greenSec);
            // 4. Sárga jelzés: Figyelem
            state = setSignal(false, true, false, yellowSec);
        }
        state = "COMPLETED";
    }
}
""",
    "Pascal": """// Oktatási Jelzőlámpa Szimuláció (Phase 1)
program TrafficLightSimulation;
var
  cycle: Integer;
  state: String;
begin
  state := 'INIT';
  for cycle := 1 to totalCycles do
  begin
    // 1. Piros jelzés: Megállás!
    state := SetSignal(True, False, False, redSec);
    // 2. Piros-sárga: Felkészülés
    state := SetSignal(True, True, False, rySec);
    // 3. Zöld jelzés: Szabad út
    state := SetSignal(False, False, True, greenSec);
    // 4. Sárga jelzés: Figyelem
    state := SetSignal(False, True, False, yellowSec);
  end;
  state := 'COMPLETED';
end.
""",
}


class TrafficLightPlugin(AlgorithmPluginBase):
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

    # Állapotok és magyar megnevezések
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
        self.params = DynamicParams()
        self.params.add(Param("red_duration", "Piros idő (mp)", "int", 3, 1, 10, description="Piros fény időtartama"))
        self.params.add(Param("red_yellow_duration", "Piros-sárga idő (mp)", "int", 1, 1, 5, description="Piros-sárga átmenet időtartama"))
        self.params.add(Param("green_duration", "Zöld idő (mp)", "int", 3, 1, 10, description="Zöld fény időtartama"))
        self.params.add(Param("yellow_duration", "Sárga idő (mp)", "int", 1, 1, 5, description="Sárga fény időtartama"))
        self.params.add(Param("cycles", "Ciklusok száma", "int", 2, 1, 10, description="Hány teljes lámpaciklus fusson le"))
        self.complexity_level = "beginner"
        self._custom_visualizer = None

    def get_params(self) -> DynamicParams:
        return self.params

    def set_param(self, pid: str, val):
        self.params.set(pid, val)

    def get_code(self, language: str) -> str:
        return CODE_TEMPLATES.get(language, CODE_TEMPLATES["Python"])

    def get_supported_languages(self) -> List[str]:
        return ["Python", "C++", "C", "BASIC", "Java", "Pascal"]

    @classmethod
    def get_line_for_tag(cls, language: str, tag: str) -> int:
        lang_tags = LOGICAL_TAG_LINES.get(language, LOGICAL_TAG_LINES["Python"])
        return lang_tags.get(tag, 1)

    def create_visualizer(self):
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

        # Initial step
        yield VisualizationStep(
            explanation="🚦 Jelzőlámpa rendszer inicializálva. Készen áll a ciklus indítására.",
            code_line=LOGICAL_TAG_LINES["Python"]["INIT"],
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
                "cycle": 0,
                "total_cycles": total_cycles,
                "phase_index": 0,
                "next_state": self.STATE_RED,
            }
        )

        phases = [
            (self.STATE_RED, "RED", {"red": True, "yellow": False, "green": False}, red_sec, "⛔ PIROS jelzés: Megállás! A járműforgalom várakozik.", self.STATE_RED_YELLOW),
            (self.STATE_RED_YELLOW, "RED_YELLOW", {"red": True, "yellow": True, "green": False}, ry_sec, "⚠️ PIROS-SÁRGA jelzés: Felkészülés az indulásra! A motor felpörgethető, de még tilos behajtani.", self.STATE_GREEN),
            (self.STATE_GREEN, "GREEN", {"red": False, "yellow": False, "green": True}, green_sec, "🟢 ZÖLD jelzés: Szabad az út! A járművek áthaladhatnak a kereszteződésen.", self.STATE_YELLOW),
            (self.STATE_YELLOW, "YELLOW", {"red": False, "yellow": True, "green": False}, yellow_sec, "🟡 SÁRGA jelzés: Figyelem! A kereszteződés kiürítése, megállás a vonal előtt.", self.STATE_RED),
        ]

        total_step_counter = 0

        for cycle_idx in range(1, total_cycles + 1):
            # Loop header step
            yield VisualizationStep(
                explanation=f"🔄 {cycle_idx}. ciklus kezdete ({cycle_idx}/{total_cycles}). Ciklusfej kiértékelése.",
                code_line=LOGICAL_TAG_LINES["Python"]["LOOP_START"],
                metrics={"comparisons": cycle_idx, "pass_num": cycle_idx, "remaining_time": 0, "cycle": cycle_idx},
                array=[int(cycle_idx), int(total_cycles)],
                key=f"Ciklus {cycle_idx}",
                extra={
                    "tag": "LOOP_START",
                    "state": "CYCLE_START",
                    "state_hu": f"{cycle_idx}. Ciklus",
                    "lamps": {"red": False, "yellow": False, "green": False},
                    "remaining_time": 0,
                    "duration": 0,
                    "cycle": cycle_idx,
                    "total_cycles": total_cycles,
                    "next_state": self.STATE_RED,
                }
            )

            for state_code, tag, lamps, duration, desc_base, next_state in phases:
                for rem in range(duration, 0, -1):
                    total_step_counter += 1
                    explanation = f"{desc_base} Hátralévő idő: {rem} mp."
                    arr_display = [int(lamps["red"]), int(lamps["yellow"]), int(lamps["green"])]

                    yield VisualizationStep(
                        explanation=explanation,
                        code_line=LOGICAL_TAG_LINES["Python"][tag],
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
                            "cycle": cycle_idx,
                            "total_cycles": total_cycles,
                            "next_state": next_state,
                            "step_index": total_step_counter,
                        }
                    )

        # Completed step
        yield VisualizationStep(
            explanation=f"✅ Jelzőlámpa szimuláció befejeződött: {total_cycles} ciklus sikeresen lefutott.",
            code_line=LOGICAL_TAG_LINES["Python"]["COMPLETE"],
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
                "cycle": total_cycles,
                "total_cycles": total_cycles,
                "next_state": None,
            }
        )
