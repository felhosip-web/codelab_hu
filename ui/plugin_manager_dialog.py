# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem
)

class PluginManagerDialog(QDialog):
    def __init__(self, loader, parent=None):
        super().__init__(parent)
        self.loader = loader
        self.setWindowTitle("🔌 Pluginok - 28 plugin")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)
        title = QLabel("🔌 Pluginok - dinamikus, verziózott")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-family: monospace; font-size: 11px;")
        for plugin in self.loader.list_plugins():
            item = QListWidgetItem(f"{plugin.icon} {plugin.name} | {plugin.id} | v{plugin.version} | {plugin.time_complexity} | {plugin.plugin_type} | {plugin.description[:50]}")
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        btn = QPushButton("Bezár")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
