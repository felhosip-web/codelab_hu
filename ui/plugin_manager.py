# -*- coding: utf-8 -*-
"""
Plugin Manager - QT dialógus ami mutatja verziókat, kompatibilitást, engedélyezést
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from core.version import MAIN_VERSION, PLUGIN_API_VERSION, get_version_string

class PluginManagerDialog(QDialog):
    def __init__(self, plugin_loader, parent=None):
        super().__init__(parent)
        self.plugin_loader = plugin_loader
        self.setWindowTitle(f"🔌 Plugin Kezelő - {get_version_string()}")
        self.resize(800, 500)
        
        layout = QVBoxLayout(self)
        
        # Fejléc - verzió infó
        header = QFrame()
        header.setStyleSheet("background: #2d2d3d; color: white; border-radius: 8px; padding: 8px;")
        header_layout = QVBoxLayout(header)
        header_layout.addWidget(QLabel(f"<b>CodeLab HU {MAIN_VERSION}</b> | Plugin API {PLUGIN_API_VERSION}"))
        errors = plugin_loader.get_load_errors()
        header_layout.addWidget(QLabel(f"Betöltött pluginok: {len(plugin_loader.plugins)} | Hibák/Figyelmeztetések: {len(errors)}"))
        layout.addWidget(header)
        
        # Táblázat
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Ikon", "Név", "ID", "Verzió", "Típus", "API igény", "Állapot"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        
        self.refresh_table()
        
        layout.addWidget(self.table)
        
        # Hibás pluginok / figyelmeztetések
        errors = plugin_loader.get_load_errors()
        if errors:
            fail_label = QLabel("⚠️ Betöltési hibák és figyelmeztetések:")
            fail_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(fail_label)
            fail_text = "\n".join(errors)
            fail_detail = QLabel(fail_text)
            fail_detail.setStyleSheet("background: #fdecea; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
            fail_detail.setWordWrap(True)
            layout.addWidget(fail_detail)
        
        # Gombok
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Bezárás")
        btn_close.clicked.connect(self.accept)
        btn_refresh = QPushButton("🔄 Frissítés")
        btn_refresh.clicked.connect(self.refresh_table)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
    
    def refresh_table(self):
        plugins = self.plugin_loader.list_plugins()
        self.table.setRowCount(len(plugins))
        
        for row, plugin in enumerate(plugins):
            # Ikon
            self.table.setItem(row, 0, QTableWidgetItem(plugin.icon))
            # Név
            self.table.setItem(row, 1, QTableWidgetItem(plugin.name))
            # ID
            self.table.setItem(row, 2, QTableWidgetItem(plugin.id))
            # Verzió
            ver_item = QTableWidgetItem(f"v{plugin.version}")
            self.table.setItem(row, 3, ver_item)
            # Típus
            type_text = "🔍 Keresés" if plugin.plugin_type == "search" else "🔀 Rendezés"
            self.table.setItem(row, 4, QTableWidgetItem(type_text))
            # API
            self.table.setItem(row, 5, QTableWidgetItem(plugin.api_version_required))
            # Állapot
            status = QTableWidgetItem("✅ Aktív")
            status.setBackground(Qt.green)
            self.table.setItem(row, 6, status)
