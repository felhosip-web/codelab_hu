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
    def __init__(self, plugins_dir: str = "plugins", api_manager=None):
        self.plugins_dir = pathlib.Path(__file__).parent.parent / plugins_dir
        self.plugins: Dict[str, AlgorithmPluginBase] = {}
        self.plugin_features: Dict[str, str] = {}
        self.api_manager = api_manager

    def _get_feature_name(self, plugin: AlgorithmPluginBase, folder_name: str = "") -> str:
        ptype = getattr(plugin, "plugin_type", getattr(plugin, "type", "")).lower()
        pid = getattr(plugin, "id", "").lower()

        if ptype in ("sorting", "sort") or "sort" in pid or "bubble" in pid or "insertion" in pid or "selection" in pid or "merge" in pid or "quick" in pid:
            return "sorting"
        if ptype in ("search", "searching") or "search" in pid or "binary_search" in pid:
            return "search"
        if ptype == "graph" or "graph" in pid or "astar" in pid or "dijkstra" in pid:
            return "graph"
        if ptype in ("tree", "btree", "trie", "traversal", "structure", "structures") or "avl" in pid or "rbtree" in pid or "btree" in pid or "tree" in pid:
            return "tree"
        if ptype in ("fifo_lifo", "stack", "queue", "circular_queue", "deque") or folder_name == "fifo_lifo":
            return "fifo_lifo"
        if ptype in ("encoding", "base64", "enigma") or folder_name in ("encoding", "enigma"):
            return "encoding"
        if ptype in ("crc", "crc_rs") or folder_name == "crc_rs":
            return "crc"
        if ptype in ("array", "array_concepts", "matrix", "array_2d", "binary_bits") or folder_name in ("array_concepts", "simple_visual", "wow_easy"):
            return "array"
        if ptype in ("string", "string_search", "kmp") or folder_name == "string_search":
            return "string"
        if ptype in ("fourier", "dft", "fft") or folder_name == "fourier":
            return "fourier"

        if folder_name:
            return folder_name.lower()
        return "general"
    
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

                        if self.api_manager:
                            api_ver = getattr(attr, "api_version_required", getattr(instance, "api_version_required", "1.0.0"))
                            compat, msg, _ = self.api_manager.check_compatibility(api_ver)
                            if not compat and getattr(self.api_manager.config, "strict_version_check", False):
                                print(f"[PluginLoader] Nem kompatibilis plugin skipped: {instance.id} ({msg})")
                                continue

                            self.api_manager.call_hook("before_plugin_load", plugin_id=instance.id, plugin=instance)

                        feat_name = self._get_feature_name(instance, plugin_folder.name)
                        self.plugin_features[instance.id] = feat_name
                        self.plugins[instance.id] = instance
                        print(f"[PluginLoader] Betöltve: {instance.name} ({instance.id}) [feature: {feat_name}]")
                        break
            except Exception as e:
                print(f"[PluginLoader] Hiba {plugin_folder.name} betöltésekor: {e}")
    
    def get_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return None
        if self.api_manager:
            feat_name = self.plugin_features.get(plugin_id, "general")
            if not self.api_manager.is_feature_enabled(feat_name):
                return None
        return plugin
    
    def list_plugins(self):
        if not self.api_manager:
            return list(self.plugins.values())

        enabled_plugins = []
        for p_id, p in self.plugins.items():
            feat_name = self.plugin_features.get(p_id, "general")
            if self.api_manager.is_feature_enabled(feat_name):
                enabled_plugins.append(p)
        return enabled_plugins
