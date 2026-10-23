# -*- coding: utf-8 -*-
"""
Dinamikus plugin paraméter rendszer - futás közben állítható értékek
"""
from dataclasses import dataclass, field
from typing import Any, List, Callable, Optional
import random

@dataclass
class Param:
    id: str  # pl "array_size"
    name: str  # Magyar név
    type: str  # "int", "float", "string", "choice", "bool"
    default: Any
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    choices: Optional[List[str]] = None
    description: str = ""
    on_change: Optional[Callable] = None  # callback ha változik
    
    def validate(self, value):
        if self.type == "int":
            v = int(value)
            if self.min_val is not None and v < self.min_val:
                return self.min_val
            if self.max_val is not None and v > self.max_val:
                return self.max_val
            return v
        elif self.type == "float":
            v = float(value)
            if self.min_val is not None and v < self.min_val:
                return self.min_val
            if self.max_val is not None and v > self.max_val:
                return self.max_val
            return v
        elif self.type == "choice":
            if value in (self.choices or []):
                return value
            return self.default
        elif self.type == "bool":
            return bool(value)
        return value

class DynamicParams:
    def __init__(self):
        self.params: dict[str, Param] = {}
        self.values: dict[str, Any] = {}
    
    def add(self, param: Param):
        self.params[param.id] = param
        self.values[param.id] = param.default
    
    def get(self, param_id: str):
        return self.values.get(param_id, self.params.get(param_id, {}).default if param_id in self.params else None)
    
    def set(self, param_id: str, value):
        if param_id in self.params:
            validated = self.params[param_id].validate(value)
            self.values[param_id] = validated
            if self.params[param_id].on_change:
                self.params[param_id].on_change(validated)
            return validated
        return None
    
    def list_params(self):
        return list(self.params.values())
    
    def to_dict(self):
        return dict(self.values)

# Előre definiált gyakori paraméterek
def common_params():
    p = DynamicParams()
    p.add(Param("array_size", "Tömb méret", "int", 10, 3, 20, description="Hány elem legyen"))
    p.add(Param("max_value", "Max érték", "int", 20, 5, 100, description="Elemek max értéke"))
    p.add(Param("graph_size", "Gráf méret", "int", 5, 3, 8))
    p.add(Param("hash_size", "Hash méret", "int", 6, 3, 12))
    p.add(Param("tree_values", "Fa értékek", "string", "8,3,10,1,6,14", description="Vesszővel elválasztva"))
    p.add(Param("text", "Szöveg", "string", "ABABDABACDABABCABAB", description="Keresendő szöveg"))
    p.add(Param("pattern", "Minta", "string", "ABABCABAB", description="Keresett minta"))
    p.add(Param("speed", "Sebesség", "int", 300, 50, 1000))
    return p
