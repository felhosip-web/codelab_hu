# -*- coding: utf-8 -*-
"""
Core motor fejlesztés - állapotmentés, visszatöltés, undo/redo, snapshotok
"""
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, List, Dict, Optional
from datetime import datetime

@dataclass
class AppState:
    version: str
    plugin_id: str
    plugin_version: str
    array: List[int]
    current_step_idx: int
    params: Dict[str, Any]
    timestamp: str
    description: str = ""
    stats: Dict[str, Any] = None
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(d):
        return AppState(**d)

class StateManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.history: List[AppState] = []
        self.history_index = -1
        self.max_history = 50
        self.auto_save_enabled = True
        self.last_auto_save = time.time()
    
    def create_snapshot(self, plugin_id: str, plugin_version: str, array: List[int], 
                        step_idx: int, params: Dict[str, Any], description="",
                        stats: Dict[str, Any]=None, version="1.9.0") -> AppState:
        state = AppState(
            version=version,
            plugin_id=plugin_id,
            plugin_version=plugin_version,
            array=array[:],
            current_step_idx=step_idx,
            params=params or {},
            timestamp=datetime.now().isoformat(),
            description=description,
            stats=stats or {}
        )
        return state
    
    def save_to_file(self, state: AppState, filename=None) -> Path:
        if filename is None:
            safe_id = "".join(c if c.isalnum() else "_" for c in state.plugin_id)
            filename = f"{safe_id}_{state.timestamp.replace(':','-')}.json"
        path = self.save_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
        return path
    
    def load_from_file(self, path: Path) -> AppState:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return AppState.from_dict(data)
    
    def list_saves(self) -> List[Path]:
        return sorted(self.save_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    def push_history(self, state: AppState):
        if self.history_index < len(self.history)-1:
            self.history = self.history[:self.history_index+1]
        self.history.append(state)
        self.history_index = len(self.history)-1
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.history_index = len(self.history)-1
    
    def undo(self) -> Optional[AppState]:
        if self.history_index > 0:
            self.history_index -= 1
            return self.history[self.history_index]
        return None
    
    def redo(self) -> Optional[AppState]:
        if self.history_index < len(self.history)-1:
            self.history_index += 1
            return self.history[self.history_index]
        return None
    
    def can_undo(self) -> bool:
        return self.history_index > 0
    def can_redo(self) -> bool:
        return self.history_index < len(self.history)-1
    
    def auto_save(self, state: AppState):
        if not self.auto_save_enabled:
            return
        if time.time() - self.last_auto_save > 30:
            self.save_to_file(state, f"autosave_{state.plugin_id}.json")
            self.last_auto_save = time.time()
    
    def export_session(self, filename="session_export.json"):
        data = {
            "export_time": datetime.now().isoformat(),
            "history_count": len(self.history),
            "history": [s.to_dict() for s in self.history]
        }
        path = self.save_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path
    
    def import_session(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.history = [AppState.from_dict(d) for d in data.get("history", [])]
        self.history_index = len(self.history)-1
        return len(self.history)

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    def start(self, name: str):
        self.start_times[name] = time.perf_counter()
    def end(self, name: str) -> float:
        if name in self.start_times:
            elapsed = time.perf_counter() - self.start_times[name]
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(elapsed)
            del self.start_times[name]
            return elapsed
        return 0.0
    def get_stats(self, name: str) -> Dict[str, float]:
        if name not in self.metrics or not self.metrics[name]:
            return {}
        vals = self.metrics[name]
        return {"count": len(vals), "total": sum(vals), "avg": sum(vals)/len(vals), "min": min(vals), "max": max(vals), "last": vals[-1]}
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        return {name: self.get_stats(name) for name in self.metrics}

class Engine:
    def __init__(self):
        self.state_manager = StateManager()
        self.perf_monitor = PerformanceMonitor()
        self.current_plugin = None
        self.current_array = []
        self.steps = []
        self.step_idx = 0
    def set_plugin(self, plugin, array=None):
        self.perf_monitor.start("set_plugin")
        self.current_plugin = plugin
        if array is not None:
            self.current_array = array
        state = self.state_manager.create_snapshot(
            plugin_id=plugin.id, plugin_version=plugin.version, array=self.current_array,
            step_idx=0, params=plugin.get_params().to_dict() if hasattr(plugin, 'get_params') and plugin.get_params() else {},
            description=f"Plugin váltás: {plugin.name}", version=str(plugin.version))
        self.state_manager.push_history(state)
        self.perf_monitor.end("set_plugin")
    def generate_steps(self, input_data=None):
        self.perf_monitor.start("generate_steps")
        if input_data is None:
            input_data = self.current_array
        self.steps = list(self.current_plugin.get_steps(input_data))
        self.step_idx = 0
        elapsed = self.perf_monitor.end("generate_steps")
        return elapsed
    def next_step(self):
        if self.step_idx < len(self.steps)-1:
            self.step_idx+=1
            return self.steps[self.step_idx]
        return None
    def prev_step(self):
        if self.step_idx > 0:
            self.step_idx-=1
            return self.steps[self.step_idx]
        return None
    def get_current_state(self) -> AppState:
        params = {}
        if self.current_plugin and hasattr(self.current_plugin, 'get_params'):
            p = self.current_plugin.get_params()
            if p:
                params = p.to_dict()
        return self.state_manager.create_snapshot(
            plugin_id=self.current_plugin.id if self.current_plugin else "none",
            plugin_version=self.current_plugin.version if self.current_plugin else "0.0.0",
            array=self.current_array, step_idx=self.step_idx, params=params,
            description=f"Lépés {self.step_idx}/{len(self.steps)}",
            stats=self.perf_monitor.get_all_stats())
    def save_current(self, description=""):
        state = self.get_current_state()
        if description:
            state.description = description
        path = self.state_manager.save_to_file(state)
        return path
    def load_state(self, path: Path):
        state = self.state_manager.load_from_file(path)
        self.current_array = state.array
        self.step_idx = state.current_step_idx
        return state
    def undo(self):
        state = self.state_manager.undo()
        if state:
            self.current_array = state.array
            self.step_idx = state.current_step_idx
        return state
    def redo(self):
        state = self.state_manager.redo()
        if state:
            self.current_array = state.array
            self.step_idx = state.current_step_idx
        return state
