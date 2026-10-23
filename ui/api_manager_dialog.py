# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QFormLayout, QTabWidget, QWidget,
    QSlider, QComboBox, QSpinBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from core.version import API_MANAGER_VERSION

class APIManagerDialog(QDialog):
    def __init__(self, api_manager, parent=None):
        super().__init__(parent)
        self.api_manager = api_manager
        self.setWindowTitle(f"API Manager {API_MANAGER_VERSION} - konfigurálható, finomhangolható")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        
        title = QLabel(f"🔌 API {API_MANAGER_VERSION} - konfigurálható, feature flag, hookok, kompatibilitás")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # 1. Feature-ek tab
        features_tab = QWidget()
        features_layout = QVBoxLayout(features_tab)
        
        features_info = QLabel("Feature flag-ek: ki/be kapcsolható funkciók, kísérleti, deprecated")
        features_info.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-size: 11px;")
        features_layout.addWidget(features_info)
        
        self.features_list = QListWidget()
        self.features_list.setStyleSheet("font-family: monospace; font-size: 11px;")
        features_layout.addWidget(self.features_list)
        
        features_btn_layout = QHBoxLayout()
        self.btn_enable_feat = QPushButton("✅ Engedélyez")
        self.btn_enable_feat.clicked.connect(self.on_enable_feature)
        features_btn_layout.addWidget(self.btn_enable_feat)
        
        self.btn_disable_feat = QPushButton("❌ Tilt")
        self.btn_disable_feat.clicked.connect(self.on_disable_feature)
        features_btn_layout.addWidget(self.btn_disable_feat)
        
        features_layout.addLayout(features_btn_layout)
        
        tabs.addTab(features_tab, "Feature-ek")
        
        # 2. Konfig tab
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        config_scroll = QGroupBox("Finomhangolás")
        config_form = QFormLayout()
        
        self.enable_caching_check = QCheckBox()
        self.enable_caching_check.setChecked(self.api_manager.config.enable_caching)
        config_form.addRow("Cache engedélyez:", self.enable_caching_check)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(self.api_manager.config.cache_size)
        config_form.addRow("Cache méret:", self.cache_size_spin)
        
        self.enable_lazy_check = QCheckBox()
        self.enable_lazy_check.setChecked(self.api_manager.config.enable_lazy_loading)
        config_form.addRow("Lazy loading:", self.enable_lazy_check)
        
        self.enable_logging_check = QCheckBox()
        self.enable_logging_check.setChecked(self.api_manager.config.enable_logging)
        config_form.addRow("Logolás:", self.enable_logging_check)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText(self.api_manager.config.log_level)
        config_form.addRow("Log szint:", self.log_level_combo)
        
        self.enable_profiling_check = QCheckBox()
        self.enable_profiling_check.setChecked(self.api_manager.config.enable_profiling)
        config_form.addRow("Profiling:", self.enable_profiling_check)
        
        self.enable_compat_check = QCheckBox()
        self.enable_compat_check.setChecked(self.api_manager.config.enable_compatibility_layer)
        config_form.addRow("Kompat réteg:", self.enable_compat_check)
        
        self.auto_migrate_check = QCheckBox()
        self.auto_migrate_check.setChecked(self.api_manager.config.auto_migrate_old_plugins)
        config_form.addRow("Auto migrálás:", self.auto_migrate_check)
        
        self.strict_check = QCheckBox()
        self.strict_check.setChecked(self.api_manager.config.strict_version_check)
        config_form.addRow("Szigorú verzió:", self.strict_check)
        
        self.enable_exp_check = QCheckBox()
        self.enable_exp_check.setChecked(self.api_manager.config.enable_experimental)
        config_form.addRow("Kísérleti:", self.enable_exp_check)
        
        self.enable_dep_check = QCheckBox()
        self.enable_dep_check.setChecked(self.api_manager.config.enable_deprecated)
        config_form.addRow("Deprecated:", self.enable_dep_check)
        
        self.enable_anim_check = QCheckBox()
        self.enable_anim_check.setChecked(self.api_manager.config.enable_animations)
        config_form.addRow("Animációk:", self.enable_anim_check)
        
        self.anim_speed_slider = QSlider(Qt.Horizontal)
        self.anim_speed_slider.setRange(10, 200)
        self.anim_speed_slider.setValue(int(self.api_manager.config.animation_speed*100))
        config_form.addRow("Anim sebesség:", self.anim_speed_slider)
        
        config_scroll.setLayout(config_form)
        config_layout.addWidget(config_scroll)
        
        config_btn_layout = QHBoxLayout()
        self.btn_save_config = QPushButton("💾 Mentés")
        self.btn_save_config.clicked.connect(self.on_save_config)
        config_btn_layout.addWidget(self.btn_save_config)
        
        self.btn_reset_config = QPushButton("🔄 Alaphelyzet")
        self.btn_reset_config.clicked.connect(self.on_reset_config)
        config_btn_layout.addWidget(self.btn_reset_config)
        
        config_layout.addLayout(config_btn_layout)
        
        tabs.addTab(config_tab, "Finomhangolás")
        
        # 3. Verziók tab
        versions_tab = QWidget()
        versions_layout = QVBoxLayout(versions_tab)
        
        self.versions_list = QListWidget()
        self.versions_list.setStyleSheet("font-family: monospace; font-size: 11px;")
        versions_layout.addWidget(self.versions_list)
        
        tabs.addTab(versions_tab, "Verziók")
        
        # 4. Statisztika tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        self.btn_export_docs = QPushButton("📄 API docs export")
        self.btn_export_docs.clicked.connect(self.on_export_docs)
        stats_layout.addWidget(self.btn_export_docs)
        
        tabs.addTab(stats_tab, "Statisztika")
        
        layout.addWidget(tabs)
        
        close_btn = QPushButton("Bezárás")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.refresh_all()
    
    def refresh_all(self):
        self.refresh_features()
        self.refresh_versions()
        self.refresh_stats()
    
    def refresh_features(self):
        self.features_list.clear()
        for name, feat in self.api_manager.features.items():
            status = "✅" if feat.enabled else "❌"
            exp = "🧪" if feat.experimental else ""
            dep = "⚠️ DEP" if feat.deprecated else ""
            item = QListWidgetItem(f"{status} {exp}{dep} {name:20} | v{feat.version:6} | cost={feat.performance_cost:6} | {feat.description}")
            item.setData(Qt.UserRole, name)
            if feat.deprecated:
                item.setBackground(Qt.yellow)
            if feat.experimental and not feat.enabled:
                item.setBackground(Qt.lightGray)
            self.features_list.addItem(item)
    
    def refresh_versions(self):
        self.versions_list.clear()
        for ver, vdata in self.api_manager.versions.items():
            item = QListWidgetItem(f"v{ver} | features={len(vdata.features)} | breaking={vdata.breaking_changes} | compat={vdata.compatible_with} | {vdata.release_date}")
            self.versions_list.addItem(item)
    
    def refresh_stats(self):
        stats = self.api_manager.get_feature_stats()
        config = self.api_manager.config
        text = f"""API Statisztika:
Összes feature: {stats['total_features']}
Engedélyezve: {stats['enabled']}
Kísérleti: {stats['experimental']}
Deprecated: {stats['deprecated']}

Használat:
{stats['usage']}

Konfig:
current={config.current_version} min={config.min_supported_version} max={config.max_supported_version}
cache={config.enable_caching} size={config.cache_size} lazy={config.enable_lazy_loading}
logging={config.enable_logging} level={config.log_level} profiling={config.enable_profiling}
compat={config.enable_compatibility_layer} auto_migrate={config.auto_migrate_old_plugins} strict={config.strict_version_check}
experimental={config.enable_experimental} deprecated={config.enable_deprecated}
animations={config.enable_animations} speed={config.animation_speed}
"""
        self.stats_label.setText(text)
    
    def on_enable_feature(self):
        item = self.features_list.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        self.api_manager.enable_feature(name)
        self.api_manager.save_config()
        self.refresh_all()
    
    def on_disable_feature(self):
        item = self.features_list.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        self.api_manager.disable_feature(name)
        self.api_manager.save_config()
        self.refresh_all()
    
    def on_save_config(self):
        # Frissítjük configot a UI-ból
        self.api_manager.config.enable_caching = self.enable_caching_check.isChecked()
        self.api_manager.config.cache_size = self.cache_size_spin.value()
        self.api_manager.config.enable_lazy_loading = self.enable_lazy_check.isChecked()
        self.api_manager.config.enable_logging = self.enable_logging_check.isChecked()
        self.api_manager.config.log_level = self.log_level_combo.currentText()
        self.api_manager.config.enable_profiling = self.enable_profiling_check.isChecked()
        self.api_manager.config.enable_compatibility_layer = self.enable_compat_check.isChecked()
        self.api_manager.config.auto_migrate_old_plugins = self.auto_migrate_check.isChecked()
        self.api_manager.config.strict_version_check = self.strict_check.isChecked()
        self.api_manager.config.enable_experimental = self.enable_exp_check.isChecked()
        self.api_manager.config.enable_deprecated = self.enable_dep_check.isChecked()
        self.api_manager.config.enable_animations = self.enable_anim_check.isChecked()
        self.api_manager.config.animation_speed = self.anim_speed_slider.value()/100.0
        
        self.api_manager.save_config()
        QMessageBox.information(self, "Mentve", "API konfig mentve saves/api_config.json")
        self.refresh_stats()
    
    def on_reset_config(self):
        from core.api_manager import APIConfig
        self.api_manager.config = APIConfig()
        self.api_manager.save_config()
        self.refresh_all()
        QMessageBox.information(self, "Reset", "API konfig alaphelyzetbe")
    
    def on_export_docs(self):
        path = self.api_manager.export_api_docs()
        QMessageBox.information(self, "Export", f"API docs exportálva: {path}")
