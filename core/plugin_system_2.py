# -*- coding: utf-8 -*-
"""
Plugin rendszer - Az alaphoz nem kell hozzányúlni!
Egy új algoritmus = egy új mappa a plugins/ alatt 1-2 fájllal
"""
import importlib.util
import pathlib
from typing import Dict, List, Type

class AlgorithmPluginBase:
    """Minden pluginnek ezt kell implementálnia"""
    id: str = ""  # pl "bubble_sort"
    name: str = ""  # magyar név
    description: str = ""
    time_complexity: str = "O(n²)"
    space_complexity: str = "O(1)"
    icon: str = "🔹"
    
    def get_steps(self, arr):
        """Generátor - yield SortStep objektumokat"""
        raise NotImplementedError
    
    def get_code(self, language: str) -> str:
        """Visszaadja a kódot a kért nyelven"""
        raise NotImplementedError
    
    def get_supported_languages(self) -> List[str]:
        return list(self.codes.keys()) if hasattr(self, 'codes') else []

class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = pathlib.Path(__file__).parent.parent / plugins_dir
        self.plugins: Dict[str, AlgorithmPluginBase] = {}
    
    def load_all(self):
        """Automatikusan betölti az összes plugint a plugins/ mappából"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(exist_ok=True)
            return
        
        for plugin_folder in self.plugins_dir.iterdir():
            if not plugin_folder.is_dir():
                continue
            plugin_file = plugin_folder / "plugin.py"
            if not plugin_file.exists():
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{plugin_folder.name}.plugin", plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Keresünk egy Plugin osztályt ami AlgorithmPluginBase-ből származik
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, AlgorithmPluginBase) and attr != AlgorithmPluginBase:
                        instance = attr()
                        self.plugins[instance.id] = instance
                        print(f"[PluginLoader] Betöltve: {instance.name} ({instance.id})")
                        break
            except Exception as e:
                print(f"[PluginLoader] Hiba {plugin_folder.name} betöltésekor: {e}")
    
    def get_plugin(self, plugin_id: str) -> AlgorithmPluginBase:
        return self.plugins.get(plugin_id)
    
    def list_plugins(self):
        return list(self.plugins.values())
