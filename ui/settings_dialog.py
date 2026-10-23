# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QTabWidget, QWidget,
    QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, keybinding_manager, parent=None):
        super().__init__(parent)
        self.kb_manager = keybinding_manager
        self.setWindowTitle("Beallitasok - billentyu hozzarendeles")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Beallitasok - billentyuk")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # Billentyuk tab
        keys_tab = QWidget()
        keys_layout = QVBoxLayout(keys_tab)
        
        info = QLabel("Kattints egy muveletre es ird be az uj billentyut pl. Ctrl+S, F5, Alt+P. A valtozas azonnal mentodik saves/keybindings.json-be")
        info.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-size: 11px;")
        info.setWordWrap(True)
        keys_layout.addWidget(info)
        
        self.keys_list = QListWidget()
        self.keys_list.setStyleSheet("font-family: monospace; font-size: 11px;")
        keys_layout.addWidget(self.keys_list)
        
        keys_btn_layout = QHBoxLayout()
        self.btn_edit_key = QPushButton("Szerkesztes")
        self.btn_edit_key.clicked.connect(self.on_edit_key)
        keys_btn_layout.addWidget(self.btn_edit_key)
        
        self.btn_reset_key = QPushButton("Alaphelyzet")
        self.btn_reset_key.clicked.connect(self.on_reset_key)
        keys_btn_layout.addWidget(self.btn_reset_key)
        
        self.btn_reset_all = QPushButton("Osszes alaphelyzet")
        self.btn_reset_all.clicked.connect(self.on_reset_all)
        keys_btn_layout.addWidget(self.btn_reset_all)
        
        keys_layout.addLayout(keys_btn_layout)
        
        tabs.addTab(keys_tab, "Billentyuk")
        
        # Lejatszas tab
        playback_tab = QWidget()
        playback_layout = QVBoxLayout(playback_tab)
        playback_label = QLabel("Lejatszas beallitasok - AUTO sebesseg, MANUAL lepes, breakpointok")
        playback_label.setStyleSheet("background: #00b894; color: white; padding: 6px; border-radius: 4px;")
        playback_layout.addWidget(playback_label)
        
        form = QFormLayout()
        self.default_speed_edit = QLineEdit("300")
        form.addRow("Alapertelmezett sebesseg (ms):", self.default_speed_edit)
        
        self.auto_save_check = QLineEdit("30")
        form.addRow("Auto-save masodperc:", self.auto_save_check)
        
        playback_layout.addLayout(form)
        tabs.addTab(playback_tab, "Lejatszas")
        
        layout.addWidget(tabs)
        
        # Bezaras
        close_btn = QPushButton("Bezaras")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.refresh_keys()
    
    def refresh_keys(self):
        self.keys_list.clear()
        for kb in self.kb_manager.list_bindings():
            item = QListWidgetItem(f"{kb.action:20} | {kb.current_key:15} | alap: {kb.default_key:15} | {kb.description}")
            item.setData(Qt.UserRole, kb.action)
            self.keys_list.addItem(item)
    
    def on_edit_key(self):
        item = self.keys_list.currentItem()
        if not item:
            return
        action = item.data(Qt.UserRole)
        current = self.kb_manager.get_binding(action)
        new_key, ok = QInputDialog.getText(self, "Billentyu", f"Uj billentyu {action}-hoz:", text=current)
        if ok and new_key:
            self.kb_manager.set_binding(action, new_key)
            self.refresh_keys()
            QMessageBox.information(self, "Mentve", f"{action} -> {new_key}\nUjrainditas utan ervenyes a menu-ben")
    
    def on_reset_key(self):
        item = self.keys_list.currentItem()
        if not item:
            return
        action = item.data(Qt.UserRole)
        self.kb_manager.reset_to_default(action)
        self.refresh_keys()
    
    def on_reset_all(self):
        self.kb_manager.reset_to_default()
        self.refresh_keys()
        QMessageBox.information(self, "Reset", "Osszes billentyu alaphelyzetbe")
