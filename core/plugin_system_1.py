# -*- coding: utf-8 -*-
"""
Plugin rendszer - VERZIÓZOTT + több plugin per mappa
"""
import importlib.util
import pathlib
import json
from typing import Dict, List
from core.version import check_plugin_compatibility, PLUGIN_API_VERSION

class AlgorithmPluginBase:
    id: str = ""
    name: str = ""
    description: str = ""
    time_complexity: str = "O(n²)"
    space_complexity: str = "O(1)"
    icon: str = "🔹"
    version: str = "1.0.0"
    api_version_required: str = "1.0.0"
    author: str = "CodeLab HU"
    dependencies: List[str] = []
    plugin_type: str = "sort"  # sort vagy search
    
    def get_steps(self, arr):
        raise NotImplementedError
    def get_code(self, language: str) -> str:
        raise NotImplementedError
    def get_manifest(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "api_required": self.api_version_required,
            "author": self.author,
            "description": self.description,
            "time": self.time_complexity,
            "space": self.space_complexity,
            "type": self.plugin_type
        }

class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = pathlib.Path(__file__).parent.parent / plugins_dir
        self.plugins: Dict[str, AlgorithmPluginBase] = {}
        self.failed_plugins = []
        self.version_log = []
    
    def load_all(self):
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(exist_ok=True)
            return
        for plugin_folder in self.plugins_dir.iterdir():
            if not plugin_folder.is_dir():
                continue
            if plugin_folder.name.startswith("__") or plugin_folder.name.startswith("."):
                continue
            plugin_file = plugin_folder / "plugin.py"
            manifest_file = plugin_folder / "manifest.json"
            if not plugin_file.exists():
                continue
            manifest = {}
            if manifest_file.exists():
                try:
                    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                except:
                    pass
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{plugin_folder.name}.plugin", plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, AlgorithmPluginBase) and attr != AlgorithmPluginBase:
                        try:
                            instance = attr()
                            is_compat, msg = check_plugin_compatibility(instance.api_version_required)
                            if not is_compat:
                                self.failed_plugins.append({
                                    "folder": plugin_folder.name,
                                    "id": getattr(instance, 'id', 'unknown'),
                                    "reason": msg,
                                    "version": getattr(instance, 'version', '?')
                                })
                                print(f"[PluginLoader] ❌ {getattr(instance,'name','?')} v{getattr(instance,'version','?')} NEM kompatibilis: {msg}")
                                continue
                            if manifest and isinstance(manifest, dict) and manifest.get("id") == instance.id:
                                instance.version = manifest.get("version", instance.version)
                            self.plugins[instance.id] = instance
                            self.version_log.append(f"✓ {instance.name} v{instance.version} (API {instance.api_version_required}) [{instance.plugin_type}]")
                            print(f"[PluginLoader] ✓ {instance.name} v{instance.version} [{instance.plugin_type}]")
                        except Exception as inner_e:
                            print(f"[PluginLoader] Hiba plugin példányosításkor {attr_name}: {inner_e}")
                            import traceback; traceback.print_exc()
            except Exception as e:
                self.failed_plugins.append({"folder": plugin_folder.name, "reason": str(e)})
                print(f"[PluginLoader] ❌ Hiba {plugin_folder.name}: {e}")
                import traceback; traceback.print_exc()
    
    def get_plugin(self, plugin_id: str):
        return self.plugins.get(plugin_id)
    def list_plugins(self):
        # Rendezve: search után sort, név szerint
        return sorted(self.plugins.values(), key=lambda p: (p.plugin_type, p.name))
    def get_version_report(self):
        report = f"Fő API: {PLUGIN_API_VERSION}\n" + "\n".join(self.version_log)
        if self.failed_plugins:
            report += "\n\nHibás:\n" + "\n".join([str(f) for f in self.failed_plugins])
        return report
