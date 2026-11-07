# -*- coding: utf-8 -*-
"""
Traffic Light Educational Plugin - Phase 1
Oktatási jelzőlámpa szimuláció valós idejű kód- és végrehajtássor-követéssel.
A forrássorok és logikai lépések összerendelése karbantartható inline címkékből
származtatott (nem törékeny, kézzel számolt sorpozíciókból).
"""
import re
from typing import Dict, Generator, List, Optional, Tuple
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

# Nyers sablonok inline [TAG:XYZ] jelölésekkel a végrehajtható utasításokon
RAW_CODE_TEMPLATES: Dict[str, str] = {
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

# Tisztított kódok és automatikusan levezetett 1-based sor-szótárak
CLEAN_CODE_TEMPLATES: Dict[str, str] = {}
DERIVED_TAG_LINES: Dict[str, Dict[str, int]] = {}

TAG_PATTERN = re.compile(
    r"""(?:\s*(?:#|//|'|/\*)\s*\[TAG:([A-Za-z0-9_]+)\]\s*(?:\*/)?|\s*\[TAG:([A-Za-z0-9_]+)\])"""
)


def _process_templates():
    """Feldolgozza a sablonokat: eltávolítja a címkéket és kinyeri a sorszámokat."""
    for lang, raw_code in RAW_CODE_TEMPLATES.items():
        clean_lines: List[str] = []
        tag_map: Dict[str, int] = {}
        for line_idx, line in enumerate(raw_code.splitlines(), start=1):
            match = TAG_PATTERN.search(line)
            if match:
                tag = match.group(1) or match.group(2)
                tag_map[tag] = line_idx
                # Eltávolítjuk az inline marker tag-et a tiszta megjelenítéshez
                clean_line = TAG_PATTERN.sub("", line).rstrip()
                clean_lines.append(clean_line)
            else:
                clean_lines.append(line)
        CLEAN_CODE_TEMPLATES[lang] = "\n".join(clean_lines) + ("\n" if raw_code.endswith("\n") else "")
        DERIVED_TAG_LINES[lang] = tag_map


_process_templates()


class TrafficLightPlugin(AlgorithmPluginBase):
    """
    Oktatási Jelzőlámpa szimulációs plugin.
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

        # Initial step
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
            # Ciklusfej kiértékelése: első ciklusban init lámpaállapot, továbbiakban az előző fázis lámpái
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
                    "step_duration_ms": 1000,
                    "cycle": cycle_idx,
                    "total_cycles": total_cycles,
                    "next_state": self.STATE_RED,
                }
            )

            # A 4 állapot fázis: ha ez az utolsó ciklus, a YELLOW után már nincs következő lámpaállapot (None)
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

        # Completed step
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
