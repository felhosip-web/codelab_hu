# -*- coding: utf-8 -*-
"""
Központi VisualizationStep séma - egységes lépésmodell a vizualizációkhoz
"""
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict, Optional


@dataclass
class VisualizationStep:
    # Közös, minden pluginnél kötelező szellemben
    explanation: str = ""
    code_line: int = 0          # 1-based a codes[] forrássorára; 0 = nincs highlight
    metrics: Dict[str, int] = field(default_factory=dict)  # comparisons, swaps, shifts, visits, ...

    # Tömb / lista alapú algoritmusok
    array: Optional[List[Any]] = None
    highlight: List[Any] = field(default_factory=list)  # indexek vagy azonosítók
    key: Any = None             # pl. keresési kulcs, pivot
    sorted_end: int = -1        # rendezett prefix vége; -1 = N/A

    # Általános extra (gráf, fa, string, stb.)
    extra: Dict[str, Any] = field(default_factory=dict)

    # Runtime (Engine/breakpoint töltheti)
    stopped: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VisualizationStep":
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)

    # Backward compatibility properties
    @property
    def comparisons(self) -> int:
        return self.metrics.get("comparisons", 0)

    @comparisons.setter
    def comparisons(self, val: int):
        self.metrics["comparisons"] = val

    @property
    def swaps(self) -> int:
        return self.metrics.get("swaps", 0)

    @swaps.setter
    def swaps(self, val: int):
        self.metrics["swaps"] = val

    @property
    def shifts(self) -> int:
        return self.metrics.get("shifts", self.metrics.get("swaps", 0))

    @shifts.setter
    def shifts(self, val: int):
        self.metrics["shifts"] = val

    @property
    def pass_num(self) -> int:
        return self.metrics.get("pass_num", 0)

    @pass_num.setter
    def pass_num(self, val: int):
        self.metrics["pass_num"] = val

    @property
    def highlight_indices(self) -> List[Any]:
        return self.highlight

    @highlight_indices.setter
    def highlight_indices(self, val: List[Any]):
        self.highlight = val or []

    @property
    def line(self) -> int:
        return self.code_line

    @line.setter
    def line(self, val: int):
        self.code_line = val

    def __getattr__(self, item: str) -> Any:
        if item != "extra" and "extra" in self.__dict__ and isinstance(self.__dict__["extra"], dict):
            if item in self.__dict__["extra"]:
                return self.__dict__["extra"][item]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")


# Visszakompatibilitási alias
SortStep = VisualizationStep
