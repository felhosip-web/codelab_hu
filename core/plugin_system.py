# -*- coding: utf-8 -*-
"""
Plugin rendszer - Az alaphoz nem kell hozzányúlni!
Egy új algoritmus = egy új mappa a plugins/ alatt 1-2 fájllal
"""
import importlib.util
import pathlib
from typing import Dict, List, Type
from core.step import VisualizationStep

class AlgorithmPluginBase:
    """Minden pluginnek ezt kell implementálnia"""
    id: str = ""  # pl "bubble_sort"
    name: str = ""  # magyar név
    description: str = ""
    time_complexity: str = "O(n²)"
    space_complexity: str = "O(1)"
    icon: str = "🔹"
    
    def get_steps(self, arr):
        """Generátor - yield VisualizationStep objektumokat"""
        raise NotImplementedError
    
    def get_code(self, language: str) -> str:
        """Visszaadja a kódot a kért nyelven"""
        raise NotImplementedError
    
    def get_supported_languages(self) -> List[str]:
        return list(self.codes.keys()) if hasattr(self, 'codes') else []

FEATURE_MAPPINGS: Dict[str, str] = {
    # Sorting
    "bubble": "sorting",
    "bubble_sort": "sorting",
    "insertion": "sorting",
    "insertion_sort": "sorting",
    "selection": "sorting",
    "selection_sort": "sorting",
    "quick": "sorting",
    "quick_sort": "sorting",
    "merge": "sorting",
    "merge_sort": "sorting",
    "heap": "sorting",
    "sort": "sorting",
    "sorting": "sorting",

    # Search
    "search": "search",
    "binary_search": "search",
    "linear_search": "search",
    "searching": "search",

    # Graph
    "graph": "graph",
    "bfs": "graph",
    "dfs": "graph",
    "dijkstra": "graph",
    "astar": "graph",

    # Tree & Structures
    "tree": "tree",
    "balanced": "tree",
    "avl": "tree",
    "rbtree": "tree",
    "btree": "tree",
    "trie": "tree",
    "advanced": "tree",
    "structures": "tree",
    "traversal": "tree",

    # FIFO / LIFO
    "fifo_lifo": "fifo_lifo",
    "stack": "fifo_lifo",
    "queue": "fifo_lifo",
    "circular_queue": "fifo_lifo",
    "deque": "fifo_lifo",

    # Encoding & Crypto
    "encoding": "encoding",
    "base64": "encoding",
    "enigma": "encoding",

    # CRC
    "crc": "crc",
    "crc_rs": "crc",

    # Array & Simple Visuals
    "array": "array",
    "array_concepts": "array",
    "array_2d": "array",
    "matrix": "array",
    "binary_bits": "array",
    "simple_visual": "array",
    "wow_easy": "array",
    "factorial": "array",

    # String Search
    "string": "string",
    "string_search": "string",
    "kmp": "string",

    # Fourier
    "fourier": "fourier",
    "dft": "fourier",
    "fft": "fourier",

    # Program Structure
    "program_structure": "program_structure",
    "for_loop": "program_structure",
}

class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins", api_manager=None):
        self.plugins_dir = pathlib.Path(__file__).parent.parent / plugins_dir
        self.plugins: Dict[str, AlgorithmPluginBase] = {}
        self.plugin_features: Dict[str, str] = {}
        self.api_manager = api_manager

    def _get_feature_name(self, plugin: AlgorithmPluginBase, folder_name: str = "") -> str:
        ptype = getattr(plugin, "plugin_type", getattr(plugin, "type", "")).lower()
        pid = getattr(plugin, "id", "").lower()
        fname = folder_name.lower()

        # 1. Direct dictionary lookup
        for key in (ptype, pid, fname):
            if key in FEATURE_MAPPINGS:
                return FEATURE_MAPPINGS[key]

        # 2. Keyword check
        for key in (ptype, pid, fname):
            if "sort" in key:
                return "sorting"
            if "search" in key:
                return "search"
            if "graph" in key or "path" in key:
                return "graph"
            if "tree" in key or "node" in key:
                return "tree"
            if "queue" in key or "stack" in key or "fifo" in key:
                return "fifo_lifo"
            if "encod" in key or "cipher" in key:
                return "encoding"
            if "crc" in key:
                return "crc"
            if "array" in key or "matrix" in key:
                return "array"
            if "string" in key:
                return "string"
            if "fourier" in key:
                return "fourier"

        # 3. Default fallback
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
