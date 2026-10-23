# -*- coding: utf-8 -*-
"""
Biztonságos REST API - nyílt részek védelemmel, illetéktelen használat ellen
"""
import json
import time
import hashlib
import secrets
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

@dataclass
class APIKey:
    key: str
    name: str
    permissions: List[str]  # read, write, execute, admin
    created_at: str
    expires_at: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0
    ip_whitelist: List[str] = field(default_factory=list)
    rate_limit_per_min: int = 60

@dataclass
class RESTConfig:
    enabled: bool = False  # Alapból tiltva! Biztonság
    host: str = "127.0.0.1"  # Csak localhost alapból, ne 0.0.0.0
    port: int = 8000
    require_api_key: bool = True  # Kötelező API kulcs
    enable_cors: bool = False  # CORS tiltva alapból
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    rate_limit_global_per_min: int = 100
    max_request_size_kb: int = 100
    enable_read_endpoints: bool = True
    enable_write_endpoints: bool = False  # Írás tiltva alapból
    enable_execute_endpoints: bool = False  # Futtatás tiltva alapból
    enable_admin_endpoints: bool = False  # Admin tiltva
    log_all_requests: bool = True
    log_file: str = "saves/api_access.log"
    enable_sandbox: bool = True
    sandbox_max_memory_mb: int = 50
    sandbox_timeout_sec: int = 10
    allowed_ips: List[str] = field(default_factory=lambda: ["127.0.0.1"])
    block_unknown_ips: bool = True
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return RESTConfig(**{k: v for k, v in data.items() if k in RESTConfig.__dataclass_fields__})

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str, limit_per_min: int) -> bool:
        now = time.time()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Töröljük a régi kéréseket (1 percnél régebbi)
        self.requests[identifier] = [t for t in self.requests[identifier] if now - t < 60]
        
        if len(self.requests[identifier]) >= limit_per_min:
            return False
        
        self.requests[identifier].append(now)
        return True

def _serialize_val(val):
    if isinstance(val, (int, float, str, bool, type(None))):
        return val
    elif isinstance(val, (list, tuple)):
        return [_serialize_val(x) for x in val]
    elif isinstance(val, dict):
        return {str(k): _serialize_val(v) for k, v in val.items()}
    elif hasattr(val, "to_dict") and callable(val.to_dict):
        return val.to_dict()
    elif hasattr(val, "__dict__"):
        return {k: _serialize_val(v) for k, v in val.__dict__.items() if not k.startswith("_")}
    else:
        return str(val)

def _run_with_timeout(func, timeout=10):
    result = []
    exception = []

    def target():
        try:
            res = func()
            result.append(res)
        except Exception as e:
            exception.append(e)

    t = threading.Thread(target=target)
    t.daemon = True
    t.start()
    t.join(timeout)

    if t.is_alive():
        return None, "Sandbox timeout: a futtatási idő túllépte a korlátot"
    if exception:
        return None, str(exception[0])
    return (result[0] if result else []), None

class SecureRESTHandler(BaseHTTPRequestHandler):
    api_manager = None
    rest_config = None
    api_keys: Dict[str, APIKey] = {}
    rate_limiter = RateLimiter()
    plugin_loader = None
    engine = None
    
    def log_message(self, format, *args):
        # Saját logolás
        if self.rest_config and self.rest_config.log_all_requests:
            log_path = Path(self.rest_config.log_file)
            log_path.parent.mkdir(exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} {self.client_address[0]} {format % args}\n")
    
    def do_OPTIONS(self):
        # CORS preflight
        if self.rest_config and self.rest_config.enable_cors:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', ', '.join(self.rest_config.cors_origins))
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
            self.end_headers()
        else:
            self.send_response(403)
            self.end_headers()
    
    def check_security(self) -> tuple:
        """Returns (allowed, error_message, api_key_obj)"""
        # IP ellenőrzés
        client_ip = self.client_address[0]
        if self.rest_config.block_unknown_ips and client_ip not in self.rest_config.allowed_ips:
            return (False, f"IP {client_ip} blokkolva", None)
        
        # Global rate limit
        if not self.rate_limiter.is_allowed(f"global:{client_ip}", self.rest_config.rate_limit_global_per_min):
            return (False, "Global rate limit túllépve", None)
        
        # API kulcs ellenőrzés
        api_key_value = self.headers.get('X-API-Key') or self.headers.get('x-api-key')
        if self.rest_config.require_api_key:
            if not api_key_value:
                return (False, "Hiányzó API kulcs (X-API-Key header)", None)
            
            if api_key_value not in self.api_keys:
                return (False, "Érvénytelen API kulcs", None)
            
            key_obj = self.api_keys[api_key_value]
            
            # Lejárat ellenőrzés
            if key_obj.expires_at:
                try:
                    exp = datetime.fromisoformat(key_obj.expires_at)
                    if datetime.now() > exp:
                        return (False, "API kulcs lejárt", None)
                except:
                    pass
            
            # IP whitelist a kulcshoz
            if key_obj.ip_whitelist and client_ip not in key_obj.ip_whitelist:
                return (False, f"IP {client_ip} nincs a kulcs whitelistjén", None)
            
            # Rate limit kulcsonként
            if not self.rate_limiter.is_allowed(f"key:{api_key_value}", key_obj.rate_limit_per_min):
                return (False, f"Rate limit túllépve a kulcshoz ({key_obj.rate_limit_per_min}/perc)", None)
            
            # Frissítjük használatot
            key_obj.last_used = datetime.now().isoformat()
            key_obj.usage_count += 1
            
            return (True, "", key_obj)
        
        return (True, "", None)
    
    def check_permission(self, key_obj: Optional[APIKey], required_perm: str) -> bool:
        if not self.rest_config.require_api_key:
            # Ha nincs kulcs követelmény, akkor config alapján döntünk
            if required_perm == "read":
                return self.rest_config.enable_read_endpoints
            elif required_perm == "write":
                return self.rest_config.enable_write_endpoints
            elif required_perm == "execute":
                return self.rest_config.enable_execute_endpoints
            elif required_perm == "admin":
                return self.rest_config.enable_admin_endpoints
            return False
        
        if not key_obj:
            return False
        
        return required_perm in key_obj.permissions
    
    def send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        if self.rest_config and self.rest_config.enable_cors:
            self.send_header('Access-Control-Allow-Origin', ', '.join(self.rest_config.cors_origins))
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def send_error_json(self, message: str, status: int = 400):
        self.send_json({"error": message, "status": status}, status)
    
    def do_GET(self):
        # Biztonság ellenőrzés
        allowed, error_msg, key_obj = self.check_security()
        if not allowed:
            self.send_error_json(error_msg, 403)
            return
        
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        # Endpointok - csak olvasás alapból engedélyezett
        if path == "/api/v2/status":
            if not self.check_permission(key_obj, "read"):
                self.send_error_json("Nincs olvasási jog", 403)
                return
            self.send_json({
                "status": "ok",
                "version": "2.6.0",
                "api_version": "2.0.0",
                "rest_config": {
                    "enabled": self.rest_config.enabled,
                    "host": self.rest_config.host,
                    "port": self.rest_config.port,
                    "require_api_key": self.rest_config.require_api_key
                },
                "timestamp": datetime.now().isoformat()
            })
        
        elif path == "/api/v2/plugins":
            if not self.check_permission(key_obj, "read"):
                self.send_error_json("Nincs olvasási jog", 403)
                return

            plugins = self.plugin_loader.list_plugins() if self.plugin_loader else []
            plugin_list = []
            for p in plugins:
                plugin_list.append({
                    "id": getattr(p, "id", ""),
                    "name": getattr(p, "name", ""),
                    "version": getattr(p, "version", "1.0.0"),
                    "type": getattr(p, "plugin_type", getattr(p, "type", "general")),
                    "time_complexity": getattr(p, "time_complexity", ""),
                    "space_complexity": getattr(p, "space_complexity", ""),
                    "description": getattr(p, "description", "")
                })
            self.send_json({
                "plugins": plugin_list,
                "count": len(plugin_list)
            })
        
        elif path == "/api/v2/config":
            if not self.check_permission(key_obj, "admin"):
                self.send_error_json("Nincs admin jog", 403)
                return
            self.send_json(self.rest_config.to_dict())
        
        else:
            self.send_error_json(f"Ismeretlen endpoint: {path}", 404)
    
    def do_POST(self):
        allowed, error_msg, key_obj = self.check_security()
        if not allowed:
            self.send_error_json(error_msg, 403)
            return
        
        # Méret ellenőrzés
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > self.rest_config.max_request_size_kb * 1024:
            self.send_error_json(f"Túl nagy kérés: {content_length} > {self.rest_config.max_request_size_kb}KB", 413)
            return
        
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        try:
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
        except:
            self.send_error_json("Érvénytelen JSON", 400)
            return
        
        if path == "/api/v2/run":
            if not self.check_permission(key_obj, "execute"):
                self.send_error_json("Nincs futtatási jog - engedélyezd a beállításokban és adj execute jogot a kulcshoz", 403)
                return
            
            plugin_id = data.get("plugin_id") or data.get("id") or ""
            if not plugin_id:
                self.send_error_json("Hiányzó plugin_id", 400)
                return

            plugin = None
            if self.plugin_loader:
                plugin = self.plugin_loader.get_plugin(plugin_id)
                if not plugin:
                    for p_id, p in self.plugin_loader.plugins.items():
                        if p_id == plugin_id or p_id.startswith(plugin_id) or plugin_id in p_id:
                            plugin = p
                            break
            
            if not plugin:
                self.send_error_json(f"Plugin nem található: {plugin_id}", 404)
                return

            params = data.get("params")
            if params and isinstance(params, dict):
                for k, v in params.items():
                    if hasattr(plugin, "set_param"):
                        try:
                            plugin.set_param(k, v)
                        except Exception:
                            pass

            array = data.get("array")
            if array is None:
                if hasattr(plugin, "generate_input") and callable(plugin.generate_input):
                    try:
                        array = plugin.generate_input()
                    except Exception:
                        array = [5, 3, 8, 1]
                else:
                    array = [5, 3, 8, 1]

            def run_func():
                if self.engine:
                    self.engine.set_plugin(plugin, array)
                    self.engine.generate_steps(array)
                    return self.engine.steps
                else:
                    return list(plugin.get_steps(array))

            if self.rest_config and self.rest_config.enable_sandbox:
                timeout_sec = getattr(self.rest_config, "sandbox_timeout_sec", 10)
                raw_steps, err = _run_with_timeout(run_func, timeout=timeout_sec)
                if err:
                    status = 408 if "timeout" in str(err).lower() else 500
                    self.send_error_json(f"Futtatási hiba / Sandbox: {err}", status)
                    return
            else:
                try:
                    raw_steps = run_func()
                except Exception as e:
                    self.send_error_json(f"Futtatási hiba: {e}", 500)
                    return

            if raw_steps is None:
                raw_steps = []

            total_steps = len(raw_steps)
            limited_steps = raw_steps[:200]
            serialized_steps = [_serialize_val(s) for s in limited_steps]

            self.send_json({
                "plugin_id": plugin.id,
                "plugin_name": getattr(plugin, "name", plugin.id),
                "array": array,
                "steps_count": len(serialized_steps),
                "total_steps": total_steps,
                "truncated": total_steps > 200,
                "steps": serialized_steps
            })
        
        elif path == "/api/v2/keys":
            if not self.check_permission(key_obj, "admin"):
                self.send_error_json("Nincs admin jog", 403)
                return
            
            name = data.get("name", "unnamed")
            perms = data.get("permissions", ["read"])
            new_key = secrets.token_urlsafe(32)
            api_key = APIKey(
                key=new_key,
                name=name,
                permissions=perms,
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(days=30)).isoformat() if data.get("expire_days") else None,
                rate_limit_per_min=data.get("rate_limit", 60)
            )
            self.api_keys[new_key] = api_key
            self.send_json({"api_key": new_key, "key_info": asdict(api_key)}, 201)
        
        else:
            self.send_error_json(f"Ismeretlen endpoint: {path}", 404)

class SecureRESTAPIServer:
    def __init__(self, config_path="saves/rest_config.json", keys_path="saves/api_keys.json", plugin_loader=None, engine=None):
        self.config_path = Path(config_path)
        self.keys_path = Path(keys_path)
        self.config = RESTConfig()
        self.api_keys: Dict[str, APIKey] = {}
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.plugin_loader = plugin_loader
        self.engine = engine
        self.load_config()
        self.load_keys()

    def set_plugin_loader(self, plugin_loader):
        self.plugin_loader = plugin_loader
        SecureRESTHandler.plugin_loader = plugin_loader

    def set_engine(self, engine):
        self.engine = engine
        SecureRESTHandler.engine = engine
    
    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = RESTConfig.from_dict(data)
            except Exception as e:
                print(f"REST config load hiba: {e}")
    
    def save_config(self):
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_keys(self):
        if self.keys_path.exists():
            try:
                with open(self.keys_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for key, info in data.items():
                    self.api_keys[key] = APIKey(**info)
            except Exception as e:
                print(f"API keys load hiba: {e}")
    
    def save_keys(self):
        self.keys_path.parent.mkdir(exist_ok=True)
        data = {k: asdict(v) for k, v in self.api_keys.items()}
        with open(self.keys_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_key(self, name: str, permissions: List[str] = None, expire_days: int = None, rate_limit: int = 60, ip_whitelist: List[str] = None) -> str:
        if permissions is None:
            permissions = ["read"]
        new_key = secrets.token_urlsafe(32)
        api_key = APIKey(
            key=new_key,
            name=name,
            permissions=permissions,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=expire_days)).isoformat() if expire_days else None,
            rate_limit_per_min=rate_limit,
            ip_whitelist=ip_whitelist or []
        )
        self.api_keys[new_key] = api_key
        self.save_keys()
        return new_key
    
    def revoke_key(self, key: str):
        if key in self.api_keys:
            del self.api_keys[key]
            self.save_keys()
    
    def list_keys(self) -> List[APIKey]:
        return list(self.api_keys.values())
    
    def start(self):
        if self.server:
            return False
        
        if not self.config.enabled:
            print("REST API tiltva a configban, nem indul")
            return False
        
        # Beállítjuk a handler osztály változóit
        SecureRESTHandler.rest_config = self.config
        SecureRESTHandler.api_keys = self.api_keys
        SecureRESTHandler.plugin_loader = self.plugin_loader
        SecureRESTHandler.engine = self.engine
        
        try:
            self.server = HTTPServer((self.config.host, self.config.port), SecureRESTHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"REST API indítva: http://{self.config.host}:{self.config.port}")
            return True
        except Exception as e:
            print(f"REST API indítási hiba: {e}")
            return False
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.thread = None
            print("REST API leállítva")
    
    def is_running(self) -> bool:
        return self.server is not None
