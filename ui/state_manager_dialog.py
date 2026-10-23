# -*- coding: utf-8 -*-
"""
Állapotmentés UI - mentés, visszatöltés, undo/redo
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from pathlib import Path

class StateManagerDialog(QDialog):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("💾 Állapotmentés - Mentés / Visszatöltés / Undo-Redo")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("💾 Állapotkezelő - Core Engine v2.0")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 8px; font-weight: bold; font-size: 14px; border-radius: 4px;")
        layout.addWidget(title)
        
        # Gombok
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Mentés most")
        self.btn_save.setStyleSheet("background: #00b894; color: white; font-weight: bold; padding: 8px;")
        self.btn_save.clicked.connect(self.on_save)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_load = QPushButton("📂 Visszatöltés")
        self.btn_load.setStyleSheet("background: #0984e3; color: white; font-weight: bold; padding: 8px;")
        self.btn_load.clicked.connect(self.on_load)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_undo = QPushButton("↩️ Undo")
        self.btn_undo.setStyleSheet("background: #fdcb6e; color: #2d3436; font-weight: bold; padding: 8px;")
        self.btn_undo.clicked.connect(self.on_undo)
        btn_layout.addWidget(self.btn_undo)
        
        self.btn_redo = QPushButton("↪️ Redo")
        self.btn_redo.setStyleSheet("background: #e17055; color: white; font-weight: bold; padding: 8px;")
        self.btn_redo.clicked.connect(self.on_redo)
        btn_layout.addWidget(self.btn_redo)
        
        self.btn_export = QPushButton("📤 Session Export")
        self.btn_export.clicked.connect(self.on_export)
        btn_layout.addWidget(self.btn_export)
        
        layout.addLayout(btn_layout)
        
        # Info
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.list_widget)
        
        self.refresh_list()
        self.update_info()
    
    def refresh_list(self):
        self.list_widget.clear()
        saves = self.engine.state_manager.list_saves()
        for path in saves:
            try:
                state = self.engine.state_manager.load_from_file(path)
                item = QListWidgetItem(f"{path.name} | {state.plugin_id} v{state.plugin_version} | {state.description} | {state.timestamp[:19]} | array={state.array[:5]}...")
                item.setData(Qt.UserRole, str(path))
                self.list_widget.addItem(item)
            except Exception as e:
                item = QListWidgetItem(f"{path.name} | HIBA: {e}")
                self.list_widget.addItem(item)
    
    def update_info(self):
        sm = self.engine.state_manager
        perf = self.engine.perf_monitor.get_all_stats()
        info = f"History: {len(sm.history)} lépés | Index: {sm.history_index} | Undo: {sm.can_undo()} Redo: {sm.can_redo()} | Perf: {perf}"
        self.info_label.setText(info)
        self.btn_undo.setEnabled(sm.can_undo())
        self.btn_redo.setEnabled(sm.can_redo())
    
    def on_save(self):
        text, ok = QInputDialog.getText(self, "Mentés", "Leírás:")
        if ok:
            path = self.engine.save_current(description=text or "Kézi mentés")
            QMessageBox.information(self, "Mentve", f"Mentve: {path}")
            self.refresh_list()
            self.update_info()
    
    def on_load(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Nincs kiválasztva", "Válassz egy mentést!")
            return
        path_str = item.data(Qt.UserRole)
        if not path_str:
            return
        try:
            state = self.engine.load_state(Path(path_str))
            mismatch_msg = ""
            if getattr(state, 'plugin_mismatch', False):
                mismatch_msg = f"\n\nFigyelem: A mentett plugin ({state.plugin_id}) eltér a jelenlegi plugintól!"
            QMessageBox.information(self, "Betöltve", f"Betöltve: {state.plugin_id} | {state.description}\nArray: {state.array}\nParams: {state.params}{mismatch_msg}")
            if self.parent() and hasattr(self.parent(), 'sync_from_engine'):
                self.parent().sync_from_engine()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Betöltés hiba: {e}")
    
    def on_undo(self):
        state = self.engine.undo()
        if state:
            QMessageBox.information(self, "Undo", f"Undo: {state.description} | {state.plugin_id}")
            if self.parent() and hasattr(self.parent(), 'sync_from_engine'):
                self.parent().sync_from_engine()
            self.update_info()
            self.accept()
        else:
            QMessageBox.warning(self, "Undo", "Nincs több undo!")
    
    def on_redo(self):
        state = self.engine.redo()
        if state:
            QMessageBox.information(self, "Redo", f"Redo: {state.description} | {state.plugin_id}")
            if self.parent() and hasattr(self.parent(), 'sync_from_engine'):
                self.parent().sync_from_engine()
            self.update_info()
            self.accept()
        else:
            QMessageBox.warning(self, "Redo", "Nincs több redo!")
    
    def on_export(self):
        path = self.engine.state_manager.export_session()
        QMessageBox.information(self, "Export", f"Session exportálva: {path}")
        self.refresh_list()
