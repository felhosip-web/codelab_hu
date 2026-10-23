# -*- coding: utf-8 -*-
"""
API 2.0 - konfigurálható, finomhangolható, feature flag, hookok, kompatibilitás
"""
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime

@dataclass
class APIFeature:
    name: str
    enabled: bool = True
    version: str = "1.0.0"
    description: str = ""
    deprecated: bool = False
    deprecated_since: str = ""
    replacement: str = ""
    performance_cost: str = "low"  # low, medium, high
    experimental: bool = False

@dataclass
class APIVersion:
    version: str
    features: List[str]
    breaking_changes: List[str] = field(default_factory=list)
    release_date: str = ""
    compatible_with: List[str] = field(default_factory=list)

@dataclass
class APIConfig:
    current_version: str = "3.0.0"
    min_supported_version: str = "1.0.0"
    max_supported_version: str = "3.0.0"
    
    # Teljesítmény finomhangolás
    enable_caching: bool = True
    cache_size: int = 100
    enable_lazy_loading: bool = True
    enable_async: bool = False
    max_steps_cache: int = 1000
    
    # Logolás, debug
    enable_logging: bool = False
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    enable_profiling: bool = False
    enable_performance_monitor: bool = True
    
    # Kompatibilitás
    enable_compatibility_layer: bool = True
    auto_migrate_old_plugins: bool = True
    strict_version_check: bool = False
    
    # Feature flag-ek
    enable_experimental: bool = False
    enable_deprecated: bool = True
    
    # Validáció, biztonság
    enable_validation: bool = True
    enable_sandbox: bool = False
    max_plugin_memory_mb: int = 100
    
    # UI, UX finomhangolás
    enable_animations: bool = True
    animation_speed: float = 1.0
    enable_tooltips: bool = True
    theme: str = "default"
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return APIConfig(**{k: v for k, v in data.items() if k in APIConfig.__dataclass_fields__})

class APIManager:
    def __init__(self, config_path="saves/api_config.json"):
        self.config_path = Path(config_path)
        self.config = APIConfig()
        self.features: Dict[str, APIFeature] = {}
        self.versions: Dict[str, APIVersion] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.middlewares: List[Callable] = []
        self.feature_usage: Dict[str, int] = {}
        self.hook_stats: Dict[str, int] = {}
        
        self.setup_default_features()
        self.setup_default_versions()
        self.setup_default_hooks()
        self.load_config()

    def setup_default_hooks(self):
        def log_hook_call(hook_name, *args, **kwargs):
            self.hook_stats[hook_name] = self.hook_stats.get(hook_name, 0) + 1
            if self.config.enable_logging:
                print(f"[APIManager Hook] {hook_name} (hívások: {self.hook_stats[hook_name]})")

        self.register_hook("before_plugin_load", lambda **kw: log_hook_call("before_plugin_load", **kw))
        self.register_hook("after_generate_steps", lambda **kw: log_hook_call("after_generate_steps", **kw))
        self.register_hook("on_feature_toggle", lambda **kw: log_hook_call("on_feature_toggle", **kw))
    
    def setup_default_features(self):
        default_features = [
            APIFeature("sorting", True, "1.0.0", "Rendezés pluginok", False, "", "", "low", False),
            APIFeature("search", True, "1.0.0", "Keresés pluginok", False, "", "", "low", False),
            APIFeature("graph", True, "1.0.0", "Gráf pluginok", False, "", "", "medium", False),
            APIFeature("tree", True, "1.0.0", "Fa pluginok", False, "", "", "medium", False),
            APIFeature("hash", True, "1.0.0", "Hash pluginok", False, "", "", "low", False),
            APIFeature("string", True, "1.0.0", "Szöveg pluginok", False, "", "", "low", False),
            APIFeature("encoding", True, "1.0.0", "Kódolás pluginok", False, "", "", "medium", False),
            APIFeature("crc", True, "1.9.0", "Hibajavító kódok", False, "", "", "medium", False),
            APIFeature("array", True, "2.4.0", "Tömbök, pointerek", False, "", "", "low", False),
            APIFeature("fifo_lifo", True, "2.5.0", "FIFO/LIFO", False, "", "", "low", False),
            APIFeature("dynamic_params", True, "1.1.0", "Dinamikus paraméterek", False, "", "", "low", False),
            APIFeature("breakpoints", True, "2.2.0", "Breakpointok", False, "", "", "low", False),
            APIFeature("advanced_breakpoints", True, "2.3.0", "Fejlett breakpointok", False, "", "", "low", False),
            APIFeature("state_manager", True, "2.0.0", "Állapotmentés", False, "", "", "low", False),
            APIFeature("engine", True, "2.0.0", "Core motor", False, "", "", "medium", False),
            APIFeature("performance_monitor", True, "2.0.0", "Teljesítmény mérés", False, "", "", "low", False),
            APIFeature("keybindings", True, "2.3.0", "Billentyűk", False, "", "", "low", False),
            APIFeature("playback", True, "2.1.0", "Lejátszás vezérlő", False, "", "", "low", False),
            APIFeature("menu", True, "2.2.0", "Menü rendszer", False, "", "", "low", False),
            APIFeature("fourier", True, "1.0.0", "Fourier transzformációk", False, "", "", "medium", False),
            APIFeature("general", True, "1.0.0", "Általános pluginok és funkciók", False, "", "", "low", False),
            # Kísérleti
            APIFeature("ai_assistant", False, "2.5.0", "AI asszisztens", False, "", "", "high", True),
            APIFeature("cloud_sync", False, "2.5.0", "Felhő szinkron", False, "", "", "high", True),
            APIFeature("plugin_marketplace", False, "2.5.0", "Plugin piactér", False, "", "", "medium", True),
            # Deprecated példa
            APIFeature("old_array_viewer", False, "1.0.0", "Régi tömb nézet", True, "2.0.0", "array", "low", False),
        ]
        for feat in default_features:
            self.features[feat.name] = feat
    
    def setup_default_versions(self):
        versions = [
            APIVersion("1.0.0", ["sorting", "search", "graph", "tree", "hash", "string"], [], "2024-01-01", []),
            APIVersion("1.1.0", ["sorting", "search", "graph", "tree", "hash", "string", "dynamic_params"], [], "2024-02-01", ["1.0.0"]),
            APIVersion("2.0.0", ["sorting", "search", "graph", "tree", "hash", "string", "encoding", "dynamic_params", "state_manager", "engine", "performance_monitor"], ["old_array_viewer"], "2024-06-01", ["1.0.0", "1.1.0"]),
            APIVersion("2.5.0", list(self.features.keys()), [], "2024-12-01", ["1.0.0", "1.1.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0"]),
            APIVersion("3.0.0", list(self.features.keys()), ["feature_flags_enforced"], "2025-01-01", ["1.0.0", "1.1.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0"]),
        ]
        for ver in versions:
            self.versions[ver.version] = ver
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        if feature_name not in self.features:
            return True
        feat = self.features[feature_name]
        if feat.deprecated and not self.config.enable_deprecated:
            return False
        if feat.experimental and not self.config.enable_experimental:
            return False
        self.feature_usage[feature_name] = self.feature_usage.get(feature_name, 0) + 1
        return feat.enabled
    
    def enable_feature(self, feature_name: str):
        if feature_name in self.features:
            self.features[feature_name].enabled = True
            self.call_hook("on_feature_toggle", feature_name=feature_name, enabled=True)
    
    def disable_feature(self, feature_name: str):
        if feature_name in self.features:
            self.features[feature_name].enabled = False
            self.call_hook("on_feature_toggle", feature_name=feature_name, enabled=False)
    
    def check_compatibility(self, plugin_api_version: str) -> tuple:
        """Returns (compatible, message, should_migrate)"""
        if plugin_api_version == self.config.current_version:
            return (True, "Kompatibilis", False)
        
        if plugin_api_version in self.versions:
            ver = self.versions[plugin_api_version]
            if self.config.current_version in ver.compatible_with or plugin_api_version in self.versions.get(self.config.current_version, APIVersion("", [])).compatible_with:
                return (True, f"Kompatibilis (kompatibilitási réteggel)", True)
        
        # Verzió összehasonlítás
        try:
            plugin_parts = [int(x) for x in plugin_api_version.split(".")]
            current_parts = [int(x) for x in self.config.current_version.split(".")]
            min_parts = [int(x) for x in self.config.min_supported_version.split(".")]
            max_parts = [int(x) for x in self.config.max_supported_version.split(".")]
            
            if plugin_parts < min_parts:
                return (False, f"Túl régi API: {plugin_api_version} < min {self.config.min_supported_version}", False)
            if plugin_parts > max_parts:
                return (False, f"Túl új API: {plugin_api_version} > max {self.config.max_supported_version}", False)
            
            # Major verzió egyezik?
            if plugin_parts[0] == current_parts[0]:
                return (True, f"Kompatibilis (major {plugin_parts[0]} egyezik)", True)
            else:
                if self.config.enable_compatibility_layer:
                    return (True, f"Kompatibilis réteggel (major {plugin_parts[0]} != {current_parts[0]})", True)
                else:
                    return (False, f"Major verzió nem egyezik: {plugin_api_version} vs {self.config.current_version}", False)
        except:
            pass
        
        if self.config.strict_version_check:
            return (False, f"Szigorú ellenőrzés: {plugin_api_version} != {self.config.current_version}", False)
        else:
            return (True, f"Engedélyezve (nem szigorú)", False)
    
    def register_hook(self, hook_name: str, func: Callable):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(func)
    
    def call_hook(self, hook_name: str, *args, **kwargs):
        results = []
        for func in self.hooks.get(hook_name, []):
            try:
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook {hook_name} hiba: {e}")
        return results
    
    def add_middleware(self, middleware: Callable):
        self.middlewares.append(middleware)
    
    def apply_middlewares(self, data: Any) -> Any:
        for mw in self.middlewares:
            try:
                data = mw(data)
            except Exception as e:
                print(f"Middleware hiba: {e}")
        return data
    
    def get_feature_stats(self) -> Dict[str, Any]:
        return {
            "total_features": len(self.features),
            "enabled": sum(1 for f in self.features.values() if f.enabled),
            "experimental": sum(1 for f in self.features.values() if f.experimental),
            "deprecated": sum(1 for f in self.features.values() if f.deprecated),
            "usage": self.feature_usage
        }
    
    def save_config(self):
        self.config_path.parent.mkdir(exist_ok=True)
        data = {
            "config": self.config.to_dict(),
            "features": {name: asdict(feat) for name, feat in self.features.items()},
            "versions": {ver: asdict(v) for ver, v in self.versions.items()},
            "feature_usage": self.feature_usage,
            "saved_at": datetime.now().isoformat()
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        if not self.config_path.exists():
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "config" in data:
                self.config = APIConfig.from_dict(data["config"])
            if "features" in data:
                for name, feat_data in data["features"].items():
                    if name in self.features:
                        # Csak enabled flag-et töltjük vissza, a többit default
                        self.features[name].enabled = feat_data.get("enabled", self.features[name].enabled)
            if "feature_usage" in data:
                self.feature_usage = data["feature_usage"]
        except Exception as e:
            print(f"API config load hiba: {e}")
    
    def export_api_docs(self, path="saves/api_docs.json"):
        docs = {
            "current_version": self.config.current_version,
            "features": {name: asdict(feat) for name, feat in self.features.items()},
            "versions": {ver: asdict(v) for ver, v in self.versions.items()},
            "config": self.config.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
        p = Path(path)
        p.parent.mkdir(exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        return p
