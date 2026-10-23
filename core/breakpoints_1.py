# -*- coding: utf-8 -*-
"""
Fejlett breakpoint logika + billentyű hozzárendelés
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
import json
from pathlib import Path
import re

@dataclass
class Breakpoint:
    plugin_id: str
    line: int
    enabled: bool = True
    condition: str = ""  # pl "i==5", "i>10", "comparisons>100"
    hit_count: int = 0  # Hányszor találkoztunk vele
    hit_condition: str = ""  # pl "hit==5" vagy "hit%10==0" - minden 10. találatnál
    log_message: str = ""  # Logpoint: nem áll meg, csak logol
    is_logpoint: bool = False  # Ha True, nem áll meg, csak log
    description: str = ""
    predefined: bool = False
    
    def to_dict(self):
        return {
            "line": self.line, "enabled": self.enabled, "condition": self.condition,
            "hit_count": self.hit_count, "hit_condition": self.hit_condition,
            "log_message": self.log_message, "is_logpoint": self.is_logpoint,
            "description": self.description, "predefined": self.predefined
        }
    
    @staticmethod
    def from_dict(plugin_id, data):
        return Breakpoint(
            plugin_id=plugin_id, line=data["line"], enabled=data.get("enabled", True),
            condition=data.get("condition",""), hit_count=data.get("hit_count",0),
            hit_condition=data.get("hit_condition",""), log_message=data.get("log_message",""),
            is_logpoint=data.get("is_logpoint", False), description=data.get("description",""),
            predefined=data.get("predefined", False)
        )

class BreakpointManager:
    def __init__(self, save_path="saves/breakpoints.json"):
        self.save_path = Path(save_path)
        self.breakpoints: Dict[str, List[Breakpoint]] = {}
        self.predefined: Dict[str, List[int]] = {}
        self.load()
    
    def set_predefined(self, plugin_id: str, lines: List[int], descriptions: Dict[int, str]=None):
        self.predefined[plugin_id] = lines
        if plugin_id not in self.breakpoints:
            self.breakpoints[plugin_id] = []
        existing_lines = {bp.line for bp in self.breakpoints[plugin_id]}
        for line in lines:
            if line not in existing_lines:
                desc = descriptions.get(line, "") if descriptions else ""
                self.breakpoints[plugin_id].append(Breakpoint(
                    plugin_id=plugin_id, line=line, enabled=True, description=desc, predefined=True
                ))
    
    def add_breakpoint(self, plugin_id: str, line: int, condition="", hit_condition="", log_message="", is_logpoint=False, description=""):
        if plugin_id not in self.breakpoints:
            self.breakpoints[plugin_id] = []
        for bp in self.breakpoints[plugin_id]:
            if bp.line == line:
                bp.enabled = True
                bp.condition = condition
                bp.hit_condition = hit_condition
                bp.log_message = log_message
                bp.is_logpoint = is_logpoint
                bp.description = description
                self.save()
                return bp
        bp = Breakpoint(plugin_id=plugin_id, line=line, enabled=True, condition=condition,
                        hit_condition=hit_condition, log_message=log_message, is_logpoint=is_logpoint,
                        description=description, predefined=False)
        self.breakpoints[plugin_id].append(bp)
        self.save()
        return bp
    
    def remove_breakpoint(self, plugin_id: str, line: int):
        if plugin_id in self.breakpoints:
            self.breakpoints[plugin_id] = [bp for bp in self.breakpoints[plugin_id] if bp.line != line]
            self.save()
    
    def toggle_breakpoint(self, plugin_id: str, line: int):
        if plugin_id not in self.breakpoints:
            self.breakpoints[plugin_id] = []
        for bp in self.breakpoints[plugin_id]:
            if bp.line == line:
                bp.enabled = not bp.enabled
                self.save()
                return bp.enabled
        self.add_breakpoint(plugin_id, line)
        return True
    
    def get_breakpoints(self, plugin_id: str) -> List[Breakpoint]:
        return self.breakpoints.get(plugin_id, [])
    
    def get_enabled_lines(self, plugin_id: str) -> Set[int]:
        return {bp.line for bp in self.breakpoints.get(plugin_id, []) if bp.enabled}
    
    def evaluate_condition(self, condition: str, context: Dict) -> bool:
        if not condition:
            return True
        condition = condition.strip()
        try:
            # Egyszerű kifejezések: i==5, i>10, comparisons>=100, hit%10==0
            # Context kulcsok: i, j, comparisons, hit, line, etc.
            
            # hit%10==0 típus
            if "%" in condition and "==" in condition:
                left, right = condition.split("==", 1)
                left = left.strip()
                right = right.strip()
                if "%" in left:
                    var, mod = left.split("%", 1)
                    var = var.strip()
                    mod = mod.strip()
                    if var in context:
                        if int(context[var]) % int(mod) == int(right):
                            return True
                return False
            
            # Egyszerű összehasonlítások
            for op in ["==", ">=", "<=", ">", "<", "!="]:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    if left in context:
                        left_val = context[left]
                        try:
                            right_val = int(right)
                        except:
                            right_val = right
                        
                        if op == "==":
                            return str(left_val) == str(right_val)
                        elif op == "!=":
                            return str(left_val) != str(right_val)
                        elif op == ">":
                            return int(left_val) > int(right_val)
                        elif op == "<":
                            return int(left_val) < int(right_val)
                        elif op == ">=":
                            return int(left_val) >= int(right_val)
                        elif op == "<=":
                            return int(left_val) <= int(right_val)
                    return False
        except Exception as e:
            print(f"Condition eval error: {e} for {condition} with {context}")
            return False
        return False
    
    def should_break(self, plugin_id: str, line: int, context: Dict=None) -> tuple:
        """Returns (should_break, is_logpoint, log_message, breakpoint)"""
        if context is None:
            context = {}
        
        for bp in self.breakpoints.get(plugin_id, []):
            if bp.line == line and bp.enabled:
                # Hit count növelés
                bp.hit_count += 1
                context["hit"] = bp.hit_count
                
                # Hit condition ellenőrzés
                if bp.hit_condition:
                    if not self.evaluate_condition(bp.hit_condition, context):
                        # Hit condition nem teljesül, nem állunk meg, de hit count már nőtt
                        continue
                
                # Feltétel ellenőrzés
                if bp.condition:
                    if not self.evaluate_condition(bp.condition, context):
                        continue
                
                # Ha logpoint, nem áll meg, csak logol
                if bp.is_logpoint:
                    log_msg = bp.log_message or f"Logpoint {plugin_id}:{line} hit={bp.hit_count} context={context}"
                    # Helyettesítjük a context változókat a log üzenetben
                    for k, v in context.items():
                        log_msg = log_msg.replace(f"{{{k}}}", str(v))
                    return (False, True, log_msg, bp)
                
                # Normál breakpoint, megáll
                return (True, False, "", bp)
        
        return (False, False, "", None)
    
    def save(self):
        self.save_path.parent.mkdir(exist_ok=True)
        data = {}
        for plugin_id, bps in self.breakpoints.items():
            data[plugin_id] = [bp.to_dict() for bp in bps]
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        if not self.save_path.exists():
            return
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for plugin_id, bps in data.items():
                self.breakpoints[plugin_id] = [Breakpoint.from_dict(plugin_id, bp) for bp in bps]
        except Exception as e:
            print(f"Breakpoint load error: {e}")
    
    def clear_all(self, plugin_id: str=None):
        if plugin_id:
            if plugin_id in self.breakpoints:
                self.breakpoints[plugin_id] = [bp for bp in self.breakpoints[plugin_id] if bp.predefined]
                # Reset hit count
                for bp in self.breakpoints[plugin_id]:
                    bp.hit_count = 0
        else:
            for pid in list(self.breakpoints.keys()):
                self.breakpoints[pid] = [bp for bp in self.breakpoints[pid] if bp.predefined]
                for bp in self.breakpoints[pid]:
                    bp.hit_count = 0
        self.save()
    
    def reset_hit_counts(self, plugin_id: str=None):
        if plugin_id:
            for bp in self.breakpoints.get(plugin_id, []):
                bp.hit_count = 0
        else:
            for bps in self.breakpoints.values():
                for bp in bps:
                    bp.hit_count = 0
        self.save()

@dataclass
class KeyBinding:
    action: str
    default_key: str
    current_key: str
    description: str

class KeyBindingManager:
    def __init__(self, save_path="saves/keybindings.json"):
        self.save_path = Path(save_path)
        self.bindings: Dict[str, KeyBinding] = {}
        self.setup_defaults()
        self.load()
    
    def setup_defaults(self):
        defaults = [
            ("save", "Ctrl+S", "Mentés most"),
            ("save_as", "Ctrl+Shift+S", "Mentés másként"),
            ("load", "Ctrl+O", "Visszatöltés"),
            ("undo", "Ctrl+Z", "Undo"),
            ("redo", "Ctrl+Y", "Redo"),
            ("reset", "Ctrl+R", "Reset"),
            ("play", "F5", "Lejátszás"),
            ("pause", "F6", "Szünet"),
            ("step_forward", "F7", "Előre lépés"),
            ("step_back", "F8", "Hátra lépés"),
            ("toggle_breakpoint", "F9", "Breakpoint ki/be"),
            ("breakpoints_manager", "Ctrl+B", "Breakpointok kezelése"),
            ("settings", "Ctrl+,", "Beállítások"),
            ("plugins", "Ctrl+P", "Pluginok"),
            ("export", "Ctrl+E", "Session Export"),
            ("toggle_code", "Ctrl+K", "Kód nézet ki/be"),
        ]
        for action, key, desc in defaults:
            self.bindings[action] = KeyBinding(action=action, default_key=key, current_key=key, description=desc)
    
    def set_binding(self, action: str, key: str):
        if action in self.bindings:
            self.bindings[action].current_key = key
            self.save()
    
    def get_binding(self, action: str) -> str:
        return self.bindings.get(action, KeyBinding(action, "", "", "")).current_key
    
    def reset_to_default(self, action: str=None):
        if action:
            if action in self.bindings:
                self.bindings[action].current_key = self.bindings[action].default_key
        else:
            for binding in self.bindings.values():
                binding.current_key = binding.default_key
        self.save()
    
    def save(self):
        self.save_path.parent.mkdir(exist_ok=True)
        data = {action: {"current_key": kb.current_key, "default_key": kb.default_key, "description": kb.description}
                for action, kb in self.bindings.items()}
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        if not self.save_path.exists():
            return
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for action, info in data.items():
                if action in self.bindings:
                    self.bindings[action].current_key = info.get("current_key", info.get("default_key", ""))
        except:
            pass
    
    def list_bindings(self) -> List[KeyBinding]:
        return list(self.bindings.values())
