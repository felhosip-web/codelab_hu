# -*- coding: utf-8 -*-
"""
Plugin rendszer - VERZIÓZOTT verzió
- Manifest támogatás (manifest.json vagy plugin.py-ban lévő meta)
- Kompatibilitás ellenőrzés
- Függőség kezelés alapja
"""
import importlib.util
import pathlib
import json
from typing import Dict, List, Type
from core.version import check_plugin_compatibility, PLUGIN_API_VERSION

class AlgorithmPluginBase:
    """Minden pluginnek ezt kell implementálnia - VERZIÓZOTT"""
    id: str = ""
    name: str = ""
    description: str = ""
    time_complexity: str = "O(n²)"
    space_complexity: str = "O(1)"
    icon: str = "🔹"
    
    # ÚJ: Verziózás
    version: str = "1.0.0"  # Plugin saját verziója
    api_version_required: str = "1.0.0"  # Milyen Plugin API kell neki
    author: str = "CodeLab HU"
    dependencies: List[str] = []  # Más pluginoktól függ-e
    
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
            
            # Manifest beolvasás (opcionális)
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
                        instance = attr()
                        
                        # Verzió ellenőrzés
                        is_compat, msg = check_plugin_compatibility(instance.api_version_required)
                        
                        if not is_compat:
                            self.failed_plugins.append({
                                "folder": plugin_folder.name,
                                "id": instance.id,
                                "reason": msg,
                                "version": instance.version
                            })
                            print(f"[PluginLoader] ❌ {instance.name} v{instance.version} NEM kompatibilis: {msg}")
                            continue
                        
                        # Manifest felülírhatja
                        if manifest:
                            instance.version = manifest.get("version", instance.version)
                        
                        self.plugins[instance.id] = instance
                        self.version_log.append(f"✓ {instance.name} v{instance.version} (API {instance.api_version_required}) - {msg}")
                        print(f"[PluginLoader] ✓ {instance.name} v{instance.version} betöltve")
                        break
                        
            except Exception as e:
                self.failed_plugins.append({
                    "folder": plugin_folder.name,
                    "reason": str(e)
                })
                print(f"[PluginLoader] ❌ Hiba {plugin_folder.name}: {e}")
    
    def get_plugin(self, plugin_id: str):
        return self.plugins.get(plugin_id)
    
    def list_plugins(self):
        # Verzió szerint rendezve, név szerint
        return sorted(self.plugins.values(), key=lambda p: p.name)
    
    def get_version_report(self):
        report = f"Fő program: {PLUGIN_API_VERSION}\n"
        report += "\n".join(self.version_log)
        if self.failed_plugins:
            report += "\n\nHibás pluginok:\n" + "\n".join([str(f) for f in self.failed_plugins])
        return report
