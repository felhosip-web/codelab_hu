# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QFormLayout, QTabWidget, QWidget,
    QLineEdit, QSpinBox, QGroupBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
import json
from pathlib import Path
from core.version import REST_API_VERSION, API_MANAGER_VERSION

class RESTAPIDialog(QDialog):
    def __init__(self, rest_server, plugin_loader=None, engine=None, parent=None):
        super().__init__(parent)
        self.rest_server = rest_server
        if plugin_loader:
            self.rest_server.set_plugin_loader(plugin_loader)
        if engine:
            self.rest_server.set_engine(engine)
        self.setWindowTitle("REST API - biztonságos, nyílt részek védelemmel")
        self.setMinimumSize(900, 650)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("🔒 REST API - biztonságos, illetéktelen használat ellen védve")
        title.setStyleSheet("background: #e74c3c; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        warning = QLabel("FIGYELEM: Alapból TILTVA! Csak localhost, API kulcs kötelező, írás/futtatás tiltva. Nyílt részek: /status, /plugins csak olvasás, de kulcs kell!")
        warning.setStyleSheet("background: #fdcb6e; color: #2d3436; padding: 6px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        tabs = QTabWidget()
        
        # 1. Beállítások tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        status_label = QLabel(f"Státusz: {'🟢 Fut' if self.rest_server.is_running() else '🔴 Áll'} | {self.rest_server.config.host}:{self.rest_server.config.port}")
        status_label.setStyleSheet("background: #2d2d3d; color: white; padding: 6px; border-radius: 4px; font-family: monospace;")
        settings_layout.addWidget(status_label)
        
        config_group = QGroupBox("Biztonsági beállítások")
        config_form = QFormLayout()
        
        self.enabled_check = QCheckBox("API engedélyezése (veszélyes, csak ha tudod mit csinálsz)")
        self.enabled_check.setChecked(self.rest_server.config.enabled)
        config_form.addRow(self.enabled_check)
        
        self.host_edit = QLineEdit(self.rest_server.config.host)
        self.host_edit.setPlaceholderText("127.0.0.1 = csak helyi, 0.0.0.0 = mindenki (veszélyes!)")
        config_form.addRow("Host:", self.host_edit)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(self.rest_server.config.port)
        config_form.addRow("Port:", self.port_spin)
        
        self.require_key_check = QCheckBox()
        self.require_key_check.setChecked(self.rest_server.config.require_api_key)
        config_form.addRow("API kulcs kötelező:", self.require_key_check)
        
        self.enable_cors_check = QCheckBox()
        self.enable_cors_check.setChecked(self.rest_server.config.enable_cors)
        config_form.addRow("CORS engedélyez:", self.enable_cors_check)
        
        self.rate_limit_spin = QSpinBox()
        self.rate_limit_spin.setRange(10, 1000)
        self.rate_limit_spin.setValue(self.rest_server.config.rate_limit_global_per_min)
        config_form.addRow("Global rate limit /perc:", self.rate_limit_spin)
        
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(10, 1000)
        self.max_size_spin.setValue(self.rest_server.config.max_request_size_kb)
        config_form.addRow("Max kérés KB:", self.max_size_spin)
        
        self.enable_read_check = QCheckBox()
        self.enable_read_check.setChecked(self.rest_server.config.enable_read_endpoints)
        config_form.addRow("Olvasás engedélyez:", self.enable_read_check)
        
        self.enable_write_check = QCheckBox()
        self.enable_write_check.setChecked(self.rest_server.config.enable_write_endpoints)
        config_form.addRow("Írás engedélyez (veszélyes):", self.enable_write_check)
        
        self.enable_exec_check = QCheckBox()
        self.enable_exec_check.setChecked(self.rest_server.config.enable_execute_endpoints)
        config_form.addRow("Futtatás engedélyez (veszélyes):", self.enable_exec_check)
        
        self.enable_admin_check = QCheckBox()
        self.enable_admin_check.setChecked(self.rest_server.config.enable_admin_endpoints)
        config_form.addRow("Admin engedélyez (veszélyes):", self.enable_admin_check)
        
        self.enable_sandbox_check = QCheckBox()
        self.enable_sandbox_check.setChecked(self.rest_server.config.enable_sandbox)
        config_form.addRow("Sandbox:", self.enable_sandbox_check)
        
        self.block_ips_check = QCheckBox()
        self.block_ips_check.setChecked(self.rest_server.config.block_unknown_ips)
        config_form.addRow("Ismeretlen IP blokkolás:", self.block_ips_check)

        self.enable_trusted_proxy_check = QCheckBox("Megbízható proxy (Trusted Proxy) engedélyezése")
        self.enable_trusted_proxy_check.setChecked(getattr(self.rest_server.config, "enable_trusted_proxy", False))
        config_form.addRow("Trusted Proxy támogatás:", self.enable_trusted_proxy_check)

        self.trusted_proxies_edit = QTextEdit()
        self.trusted_proxies_edit.setPlaceholderText("IP-címek és CIDR hálózatok soronként (pl. 127.0.0.1, 10.0.0.0/8, 2001:db8::/32)")
        self.trusted_proxies_edit.setMaximumHeight(80)
        self.trusted_proxies_edit.setPlainText("\n".join(getattr(self.rest_server.config, "trusted_proxies", []) or []))
        config_form.addRow("Megbízható proxy-k (IP/CIDR):", self.trusted_proxies_edit)

        proxy_warning = QLabel("⚠️ BIZTONSÁGI FIGYELMEZTETÉS: Csak az itt kifejezetten megadott megbízható proxy-k X-Forwarded-For fejlécében bízunk meg. A backend nem lehet közvetlenül elérhető publikus hálózatról! Ennek engedélyezése önmagában nem bízik meg egyetlen proxyban sem.")
        proxy_warning.setStyleSheet("background: #ffeaa7; color: #d63031; padding: 6px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        proxy_warning.setWordWrap(True)
        config_form.addRow(proxy_warning)
        
        config_group.setLayout(config_form)
        settings_layout.addWidget(config_group)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Mentés")
        self.btn_save.clicked.connect(self.on_save)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_start = QPushButton("▶️ Indítás")
        self.btn_start.clicked.connect(self.on_start)
        btn_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹️ Leállítás")
        self.btn_stop.clicked.connect(self.on_stop)
        btn_layout.addWidget(self.btn_stop)
        
        settings_layout.addLayout(btn_layout)
        
        tabs.addTab(settings_tab, "Beállítások")
        
        # 2. API kulcsok tab
        keys_tab = QWidget()
        keys_layout = QVBoxLayout(keys_tab)
        
        keys_info = QLabel("API kulcsok: név, jogok (read/write/execute/admin), lejárat, IP whitelist, rate limit. Kulcs nélkül nincs hozzáférés ha require_api_key=True!")
        keys_info.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-size: 11px;")
        keys_info.setWordWrap(True)
        keys_layout.addWidget(keys_info)
        
        self.keys_list = QListWidget()
        self.keys_list.setStyleSheet("font-family: monospace; font-size: 11px;")
        keys_layout.addWidget(self.keys_list)
        
        keys_btn_layout = QHBoxLayout()
        self.btn_create_key = QPushButton("➕ Új kulcs")
        self.btn_create_key.clicked.connect(self.on_create_key)
        keys_btn_layout.addWidget(self.btn_create_key)
        
        self.btn_revoke_key = QPushButton("🗑️ Visszavon")
        self.btn_revoke_key.clicked.connect(self.on_revoke_key)
        keys_btn_layout.addWidget(self.btn_revoke_key)
        
        self.btn_copy_key = QPushButton("📋 Másol")
        self.btn_copy_key.clicked.connect(self.on_copy_key)
        keys_btn_layout.addWidget(self.btn_copy_key)
        
        keys_layout.addLayout(keys_btn_layout)
        
        tabs.addTab(keys_tab, "API kulcsok")
        
        # 3. Dokumentáció tab
        docs_tab = QWidget()
        docs_layout = QVBoxLayout(docs_tab)
        
        docs_text = QTextEdit()
        docs_text.setReadOnly(True)
        docs_text.setStyleSheet("font-family: monospace; font-size: 11px; background: #2d2d3d; color: #f1f2f6;")
        docs_text.setText(f"""
🔒 BIZTONSÁGOS REST API v{REST_API_VERSION} (API Manager v{API_MANAGER_VERSION}) - VÉDELEM ILLETÉKTELEN HASZNÁLAT ELLEN

Nyílt részek és védelmük:

1. /api/v2/status (GET) - Státusz
   - Védve: IP whitelist, rate limit, API kulcs ha require_api_key=True
   - Jog: read
   - Alapból: csak localhost, kulcs kell
   - Válasz tartalmazza: "api_version" ({API_MANAGER_VERSION}), "rest_api_version" ({REST_API_VERSION}), "version" (app version)

2. /api/v2/plugins (GET) - Plugin lista
   - Védve: IP, rate limit, API kulcs
   - Jog: read
   - Csak olvasás, a PluginLoader által betöltött valódi plugineket adja vissza (id, name, version, type, time_complexity, space_complexity, description)

3. /api/v2/run (POST) - Futtatás
   - Védve: IP, rate limit, API kulcs, execute jog, sandbox, max méret
   - Jog: execute
   - Meghívja a valódi Engine / plugin get_steps() metódusát
   - Body példa: {{"plugin_id": "bubble", "params": {{...}}, "array": [5, 3, 8, 1]}}
   - Visszaadja a lépéseket JSON formátumban (max 200 lépés)
   - Ha a plugin nem található: 404
   - Ha execute jog nincs: 403
   - Sandbox timeout és max_request_size továbbra is érvényesül

4. /api/v2/config (GET) - Konfig
   - Védve: admin jog
   - Alapból TILTVA! enable_admin_endpoints=False

5. /api/v2/keys (POST) - Új kulcs
   - Védve: admin jog
   - Alapból TILTVA!

Biztonsági rétegek:
- Host: 127.0.0.1 csak helyi, 0.0.0.0 veszélyes
- IP whitelist: csak engedélyezett IP-k
- Trusted Proxy támogatás: Opt-in (enable_trusted_proxy=True, trusted_proxies=["127.0.0.1"])
- X-Forwarded-For lánc feloldás: Jobbról balra bejárás, megbízható proxy-k átlépése, fail-closed
- Rate limiting: global + kulcsonként feloldott IP alapján
- API kulcs: kötelező, lejárat, IP whitelist kulcsonként
- Jogok: read/write/execute/admin külön
- Sandbox: memória limit, timeout
- Max kérés méret: 100KB alapból
- Log: minden kérés logolva saves/api_access.log
- CORS: tiltva alapból
- Írás/futtatás/admin tiltva alapból

Példa biztonságos használat:
curl -H "X-API-Key: YOUR_KEY" http://127.0.0.1:8000/api/v2/plugins

Példa kulcs létrehozás (admin kell):
curl -X POST -H "X-API-Key: ADMIN_KEY" -H "Content-Type: application/json" 
  -d '{{"name":"myapp","permissions":["read"],"rate_limit":60}}'
  http://127.0.0.1:8000/api/v2/keys

Ajánlott beállítás éleshez:
- host=127.0.0.1 (ne 0.0.0.0)
- require_api_key=True
- enable_read=True, enable_write=False, enable_execute=False, enable_admin=False
- block_unknown_ips=True, allowed_ips=["127.0.0.1"]
- rate_limit_global=100, rate_limit per key=60
- enable_sandbox=True
- log_all_requests=True
""")
        docs_layout.addWidget(docs_text)
        
        tabs.addTab(docs_tab, "Dokumentáció + biztonság")
        
        # 4. Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        log_layout.addWidget(self.log_text)
        
        log_btn_layout = QHBoxLayout()
        self.btn_refresh_log = QPushButton("🔄 Frissít")
        self.btn_refresh_log.clicked.connect(self.on_refresh_log)
        log_btn_layout.addWidget(self.btn_refresh_log)
        
        self.btn_clear_log = QPushButton("🧹 Töröl")
        self.btn_clear_log.clicked.connect(self.on_clear_log)
        log_btn_layout.addWidget(self.btn_clear_log)
        
        log_layout.addLayout(log_btn_layout)
        
        tabs.addTab(log_tab, "Log")
        
        layout.addWidget(tabs)
        
        close_btn = QPushButton("Bezárás")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.refresh_keys()
        self.on_refresh_log()
    
    def refresh_keys(self):
        self.keys_list.clear()
        for key_obj in self.rest_server.list_keys():
            item = QListWidgetItem(f"{key_obj.name:15} | {key_obj.key[:20]}... | {','.join(key_obj.permissions):15} | rate={key_obj.rate_limit_per_min:3}/m | usage={key_obj.usage_count:4} | exp={key_obj.expires_at or 'soha'} | ips={key_obj.ip_whitelist}")
            item.setData(Qt.UserRole, key_obj.key)
            self.keys_list.addItem(item)
    
    def on_save(self):
        raw_proxies_text = self.trusted_proxies_edit.toPlainText().strip()
        raw_proxies = [line.strip() for line in raw_proxies_text.split('\n') if line.strip()]

        try:
            from core.rest_api import validate_trusted_proxies
            validated_proxies = validate_trusted_proxies(raw_proxies)
        except ValueError as e:
            QMessageBox.warning(self, "Hibás konfiguráció", f"Érvénytelen megbízható proxy IP/CIDR cím:\n{e}")
            return

        self.rest_server.config.enabled = self.enabled_check.isChecked()
        self.rest_server.config.host = self.host_edit.text() or "127.0.0.1"
        self.rest_server.config.port = self.port_spin.value()
        self.rest_server.config.require_api_key = self.require_key_check.isChecked()
        self.rest_server.config.enable_cors = self.enable_cors_check.isChecked()
        self.rest_server.config.rate_limit_global_per_min = self.rate_limit_spin.value()
        self.rest_server.config.max_request_size_kb = self.max_size_spin.value()
        self.rest_server.config.enable_read_endpoints = self.enable_read_check.isChecked()
        self.rest_server.config.enable_write_endpoints = self.enable_write_check.isChecked()
        self.rest_server.config.enable_execute_endpoints = self.enable_exec_check.isChecked()
        self.rest_server.config.enable_admin_endpoints = self.enable_admin_check.isChecked()
        self.rest_server.config.enable_sandbox = self.enable_sandbox_check.isChecked()
        self.rest_server.config.block_unknown_ips = self.block_ips_check.isChecked()
        self.rest_server.config.enable_trusted_proxy = self.enable_trusted_proxy_check.isChecked()
        self.rest_server.config.trusted_proxies = validated_proxies

        self.rest_server.save_config()
        QMessageBox.information(self, "Mentve", f"REST config mentve saves/rest_config.json\nÚjraindítás szükséges ha futott!")
    
    def on_start(self):
        if self.rest_server.start():
            QMessageBox.information(self, "Indítva", f"REST API indítva: http://{self.rest_server.config.host}:{self.rest_server.config.port}")
        else:
            QMessageBox.warning(self, "Hiba", "Nem indult - ellenőrizd hogy engedélyezve van-e és nem foglalt-e a port")
    
    def on_stop(self):
        self.rest_server.stop()
        QMessageBox.information(self, "Leállítva", "REST API leállítva")
    
    def on_create_key(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Új kulcs", "Név:")
        if not ok or not name:
            return
        perms_text, ok = QInputDialog.getText(self, "Jogok", "Jogok (read,write,execute,admin vesszővel):", text="read")
        if not ok:
            return
        perms = [p.strip() for p in perms_text.split(",") if p.strip()]
        
        rate, ok = QInputDialog.getInt(self, "Rate limit", "Kérések / perc:", 60, 1, 1000)
        if not ok:
            return
        
        new_key = self.rest_server.create_key(name=name, permissions=perms, rate_limit=rate)
        self.refresh_keys()
        QMessageBox.information(self, "Kulcs létrehozva", f"Kulcs: {new_key}\nMentsd el, csak most látszik teljesen!\nNév: {name}\nJogok: {perms}")
    
    def on_revoke_key(self):
        item = self.keys_list.currentItem()
        if not item:
            return
        key = item.data(Qt.UserRole)
        self.rest_server.revoke_key(key)
        self.refresh_keys()
        QMessageBox.information(self, "Visszavonva", f"Kulcs visszavonva: {key[:20]}...")
    
    def on_copy_key(self):
        item = self.keys_list.currentItem()
        if not item:
            return
        key = item.data(Qt.UserRole)
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(key)
        QMessageBox.information(self, "Másolva", "Kulcs vágólapra másolva")
    
    def on_refresh_log(self):
        log_path = Path(self.rest_server.config.log_file)
        if log_path.exists():
            try:
                text = log_path.read_text(encoding='utf-8', errors='ignore')
                # Utolsó 100 sor
                lines = text.split('\n')[-100:]
                self.log_text.setText('\n'.join(lines))
            except Exception as e:
                self.log_text.setText(f"Hiba: {e}")
        else:
            self.log_text.setText("Nincs log fájl még")
    
    def on_clear_log(self):
        log_path = Path(self.rest_server.config.log_file)
        if log_path.exists():
            log_path.unlink()
        self.log_text.setText("Log törölve")
