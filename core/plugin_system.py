# -*- coding: utf-8 -*-
"""
Plugin rendszer - Az alaphoz nem kell hozzányúlni!
Egy új algoritmus = egy új mappa a plugins/ alatt 1-2 fájllal
"""
import importlib.util
import pathlib
import sys
from typing import Dict, List, Tuple, Type
from core.step import VisualizationStep


class AlgorithmPluginBase:
    """Minden pluginnek ezt kell implementálnia"""
    id: str = ""  # pl "bubble_sort"
    name: str = ""  # magyar név
    description: str = ""
    time_complexity: str = "O(n²)"
    space_complexity: str = "O(1)"
    icon: str = "🔹"
    plugin_type: str = "general"

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
    "binary_add": "array",
    "binary_sub": "array",
    "binary_mul": "array",
    "binary_arith": "array",
    "binary": "array",
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
        self.errors: List[str] = []

    @property
    def failed_plugins(self) -> List[Dict[str, str]]:
        return [{"folder": "load_error", "reason": e} for e in self.errors]

    def _get_feature_name(self, plugin: AlgorithmPluginBase, folder_name: str = "") -> str:
        ptype = getattr(plugin, "plugin_type", getattr(plugin, "type", "")).strip().lower()
        pid = getattr(plugin, "id", "").strip().lower()
        fname = folder_name.strip().lower()

        # 1. Direct dictionary lookup in order: ptype, pid, fname
        for key in (ptype, pid, fname):
            if key and key in FEATURE_MAPPINGS:
                return FEATURE_MAPPINGS[key]

        # 2. Keyword check
        for key in (ptype, pid, fname):
            if not key:
                continue
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

        # 3. Explicit non-general plugin_type fallback
        if ptype and ptype != "general":
            return ptype

        # 4. Default fallback
        return "general"

    def _load_plugin_folder(
        self,
        plugin_folder: pathlib.Path,
        registered_ids: set,
        target_plugins: Dict[str, AlgorithmPluginBase] = None,
        target_features: Dict[str, str] = None,
    ) -> List[str]:
        """
        Loads and validates all plugin classes from a specific plugin folder.
        Registers successfully loaded plugins into target dictionaries (defaulting to self.plugins).
        Returns a list of error messages encountered during loading.
        """
        errors: List[str] = []
        if target_plugins is None:
            target_plugins = self.plugins
        if target_features is None:
            target_features = self.plugin_features

        plugin_file = plugin_folder / "plugin.py"
        if not plugin_file.exists():
            return errors

        module_name = f"plugins.{plugin_folder.name}.plugin"
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(
                module_name, plugin_file
            )
            if spec is None or spec.loader is None:
                err_msg = f"[PluginLoader] Spec nem tölthető be: {plugin_folder.name}"
                errors.append(err_msg)
                print(err_msg)
                return errors

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Regisztráljuk az ÖSSZES AlgorithmPluginBase leszármazott osztályt a modulban
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, AlgorithmPluginBase)
                    and attr != AlgorithmPluginBase
                    and not getattr(attr, "__abstractmethods__", False)
                ):
                    if attr.__module__ != module.__name__:
                        continue

                    try:
                        instance = attr()
                    except Exception as inst_err:
                        err_msg = f"[PluginLoader] Példányosítási hiba ({plugin_folder.name}/{attr_name}): {inst_err}"
                        errors.append(err_msg)
                        print(err_msg)
                        continue

                    plugin_id = getattr(instance, "id", "")
                    if plugin_id is None or not str(plugin_id).strip():
                        err_msg = f"[PluginLoader] Üres plugin ID skipped ({plugin_folder.name}/{attr_name})"
                        errors.append(err_msg)
                        print(err_msg)
                        continue

                    plugin_id = str(plugin_id).strip()

                    if plugin_id in registered_ids:
                        existing_plugin = target_plugins.get(plugin_id, self.plugins.get(plugin_id))
                        existing_name = existing_plugin.__class__.__name__ if existing_plugin else "existing"
                        err_msg = f"[PluginLoader] Ütköző plugin id '{plugin_id}': a(z) {plugin_folder.name}/{attr_name} felülírná {existing_name}-t. Átugrás (első nyer)."
                        errors.append(err_msg)
                        print(err_msg)
                        continue

                    if self.api_manager:
                        api_ver = getattr(attr, "api_version_required", getattr(instance, "api_version_required", "1.0.0"))
                        compat, msg, _ = self.api_manager.check_compatibility(api_ver)
                        if not compat and getattr(self.api_manager.config, "strict_version_check", False):
                            err_msg = f"[PluginLoader] Nem kompatibilis plugin skipped: {plugin_id} ({msg})"
                            errors.append(err_msg)
                            print(err_msg)
                            continue

                        self.api_manager.call_hook("before_plugin_load", plugin_id=plugin_id, plugin=instance)

                    feat_name = self._get_feature_name(instance, plugin_folder.name)
                    target_features[plugin_id] = feat_name
                    target_plugins[plugin_id] = instance
                    registered_ids.add(plugin_id)
                    print(f"[PluginLoader] Betöltve: {instance.name} ({plugin_id}) [feature: {feat_name}]")
        except Exception as e:
            err_msg = f"[PluginLoader] Hiba {plugin_folder.name} betöltésekor: {e}"
            errors.append(err_msg)
            print(err_msg)

        return errors

    def load_all(self):
        """Automatikusan betölti az összes plugint a plugins/ mappából"""
        self.errors = []
        registered_ids = set()
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(exist_ok=True)
            return

        for plugin_folder in self.plugins_dir.iterdir():
            if not plugin_folder.is_dir():
                continue
            folder_errors = self._load_plugin_folder(plugin_folder, registered_ids)
            self.errors.extend(folder_errors)

    def reload(self, target: str = None) -> Tuple[List[str], List[str]]:
        """
        Újratölti a pluginokat.
        Ha target None, a meglévő teljes újratöltést hajtja végre (load_all()).
        Ha target meg van adva (plugin ID vagy kategória/feature név), csak a célzott
        plugin(oka)t tölti újra úgy, hogy az érintetlen pluginok példányai és állapota
        változatlan maradnak (is), és azok moduljai nem töltődnek újra.
        Visszaadja: (loaded_ids, errors)
        """
        if not target:
            self.plugins.clear()
            self.plugin_features.clear()
            self.load_all()
            return list(self.plugins.keys()), self.get_load_errors()

        self.errors = []
        target = str(target).strip()

        # 1. Azonosítsuk a meglévő célzott pluginokat target (id vagy feature) alapján
        targeted_pids = {
            pid for pid, inst in self.plugins.items()
            if pid == target or self.plugin_features.get(pid) == target
        }

        # 2. Határozzuk meg a célzott mappaneveket
        targeted_folders = set()
        for pid in targeted_pids:
            inst = self.plugins[pid]
            mod_name = getattr(inst.__class__, "__module__", "")
            if mod_name.startswith("plugins."):
                parts = mod_name.split(".")
                if len(parts) >= 2:
                    targeted_folders.add(parts[1])

        # Ha korábban még nem volt a registry-ben, feloldás könyvtárnév vagy feature alapján
        if not targeted_folders and self.plugins_dir.exists():
            direct_folder = self.plugins_dir / target
            if direct_folder.is_dir() and (direct_folder / "plugin.py").exists():
                targeted_folders.add(target)
            else:
                for folder in self.plugins_dir.iterdir():
                    if folder.is_dir() and (folder / "plugin.py").exists():
                        if FEATURE_MAPPINGS.get(folder.name.lower()) == target.lower():
                            targeted_folders.add(folder.name)

        if not targeted_folders:
            err_msg = f"[PluginLoader] Ismeretlen újratöltési célpont: '{target}'"
            self.errors.append(err_msg)
            print(err_msg)
            return list(self.plugins.keys()), self.get_load_errors()

        # 3. Érintett plugin ID-k a célzott mappákban
        pids_in_targeted_folders = set()
        for pid, inst in self.plugins.items():
            mod_name = getattr(inst.__class__, "__module__", "")
            if mod_name.startswith("plugins."):
                parts = mod_name.split(".")
                if len(parts) >= 2 and parts[1] in targeted_folders:
                    pids_in_targeted_folders.add(pid)

        # Regisztrált ID-k az egyéb (nem érintett) pluginokból
        unrelated_registered_ids = {
            pid for pid in self.plugins if pid not in pids_in_targeted_folders
        }

        # Staging a célzott mappák újratöltéséhez
        staging_plugins: Dict[str, AlgorithmPluginBase] = {}
        staging_features: Dict[str, str] = {}
        target_registered_ids = set(unrelated_registered_ids)
        target_errors: List[str] = []

        for folder_name in sorted(targeted_folders):
            folder_path = self.plugins_dir / folder_name
            f_errors = self._load_plugin_folder(
                folder_path,
                target_registered_ids,
                target_plugins=staging_plugins,
                target_features=staging_features,
            )
            target_errors.extend(f_errors)

        # 4. Frissítsük a nyilvántartást:
        # Ha a target nem direkt mappát célzott, akkor csak a célzott pluginokat/feature-öket
        # frissítjük vagy távolítjuk el. Az azonos mappában lévő, de célon kívüli pluginok
        # meglévő példányait és állapotát megőrizzük.
        is_direct_folder_target = (target in targeted_folders and target not in targeted_pids)

        if is_direct_folder_target:
            # Teljes mappa célzás: minden plugin a mappában újratöltődik
            for pid in pids_in_targeted_folders:
                self.plugins.pop(pid, None)
                self.plugin_features.pop(pid, None)
            self.plugins.update(staging_plugins)
            self.plugin_features.update(staging_features)
        else:
            # Specifikus plugin ID vagy feature/kategória célzás:
            # Csak a célzott ID-kat cseréljük le az újra, illetve távolítjuk el ha a betöltés meghiúsult.
            for pid in targeted_pids:
                self.plugins.pop(pid, None)
                self.plugin_features.pop(pid, None)
            for pid, inst in staging_plugins.items():
                if pid in targeted_pids or staging_features.get(pid) == target or not targeted_pids:
                    self.plugins[pid] = inst
                    self.plugin_features[pid] = staging_features[pid]
        self.errors.extend(target_errors)

        return list(self.plugins.keys()), self.get_load_errors()

    def get_load_errors(self) -> List[str]:
        return list(self.errors)

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

    def list_plugins_grouped(self) -> Dict[str, List[AlgorithmPluginBase]]:
        """Visszaadja a modulokat kategóriák (feature / plugin_type) szerint csoportosítva."""
        grouped: Dict[str, List[AlgorithmPluginBase]] = {}
        for plugin in self.list_plugins():
            feat_name = self.plugin_features.get(
                plugin.id, getattr(plugin, "plugin_type", "general")
            )
            if feat_name not in grouped:
                grouped[feat_name] = []
            grouped[feat_name].append(plugin)
        return grouped
