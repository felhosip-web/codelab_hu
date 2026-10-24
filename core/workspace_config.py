# -*- coding: utf-8 -*-
"""
Munkaterület és kódnézet beállítások kezelője
"""
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List


@dataclass
class WorkspaceConfig:
    font_family: str = "Monospace"
    font_size: int = 11
    theme: str = "light"  # "light" | "dark"
    syntax_highlight: bool = True
    auto_scroll_to_line: bool = True
    show_line_numbers: bool = True
    splitter_orientation: str = "horizontal"  # "horizontal" | "vertical"
    splitter_sizes: List[int] = field(default_factory=lambda: [400, 400])
    layout_preset: str = "equal"  # "viz_focus" | "equal" | "code_focus"
    sidebar_collapsed: bool = False
    sidebar_width: int = 240
    current_line_color: str = ""  # üres string esetén témaspecifikus alapértelmezett kiemelés

    @classmethod
    def get_config_path(cls, config_path: str = "saves/workspace_config.json") -> Path:
        return Path(config_path)

    @classmethod
    def load(cls, config_path: str = "saves/workspace_config.json") -> "WorkspaceConfig":
        path = cls.get_config_path(config_path)
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            instance = cls()
            for key, val in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, val)
            return instance
        except Exception as e:
            print(f"[WorkspaceConfig] Hiba a beállítások betöltésekor: {e}")
            return cls()

    def save(self, config_path: str = "saves/workspace_config.json"):
        path = self.get_config_path(config_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WorkspaceConfig] Hiba a beállítások mentésekor: {e}")
