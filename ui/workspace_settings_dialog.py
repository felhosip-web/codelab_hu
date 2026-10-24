# -*- coding: utf-8 -*-
"""
Munkaterület és kódnézet beállítások dialógusa
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QFormLayout, QGroupBox, QFrame
)
from core.workspace_config import WorkspaceConfig


class WorkspaceSettingsDialog(QDialog):
    def __init__(self, config: WorkspaceConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("⚙️ Munkaterület & Kód Beállításai")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        title = QLabel("⚙️ Munkaterület & Kód Munkaterület Beállításai")
        title.setStyleSheet("background: #2e86de; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)

        form = QFormLayout()

        # Font family
        self.font_combo = QComboBox()
        fonts = ["Monospace", "Consolas", "Cascadia Code", "DejaVu Sans Mono", "Courier New"]
        self.font_combo.addItems(fonts)
        if self.config.font_family in fonts:
            self.font_combo.setCurrentText(self.config.font_family)
        else:
            self.font_combo.setCurrentText("Monospace")
        form.addRow("Betűtípus:", self.font_combo)

        # Font size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 24)
        self.size_spin.setValue(self.config.font_size)
        form.addRow("Betűméret:", self.size_spin)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Világos (Light)", "light")
        self.theme_combo.addItem("Sötét (Dark)", "dark")
        idx = 1 if self.config.theme == "dark" else 0
        self.theme_combo.setCurrentIndex(idx)
        form.addRow("Kódnézet Téma:", self.theme_combo)

        # Syntax highlight
        self.syntax_check = QCheckBox("Szintaxiskiemelés bekapcsolva")
        self.syntax_check.setChecked(self.config.syntax_highlight)
        form.addRow("Szintaxiskiemelés:", self.syntax_check)

        # Line numbers
        self.line_num_check = QCheckBox("Sorszámok megjelenítése a bal oldalon")
        self.line_num_check.setChecked(self.config.show_line_numbers)
        form.addRow("Sorszámok:", self.line_num_check)

        # Auto scroll
        self.scroll_check = QCheckBox("Automatikus görgetés és középre igazítás az aktuális sorhoz")
        self.scroll_check.setChecked(self.config.auto_scroll_to_line)
        form.addRow("Auto görgetés:", self.scroll_check)

        # Splitter orientation
        self.orient_combo = QComboBox()
        self.orient_combo.addItem("Vízszintes (Vizualizáció | Kód)", "horizontal")
        self.orient_combo.addItem("Függőleges (Vizualizáció / Kód)", "vertical")
        o_idx = 1 if self.config.splitter_orientation == "vertical" else 0
        self.orient_combo.setCurrentIndex(o_idx)
        form.addRow("Elrendezés iránysa:", self.orient_combo)

        # Sidebar collapsed default
        self.sidebar_collapsed_check = QCheckBox("Plugin lista alapból összecsukva")
        self.sidebar_collapsed_check.setChecked(self.config.sidebar_collapsed)
        form.addRow("Sidebar állapot:", self.sidebar_collapsed_check)

        layout.addLayout(form)

        # Layout Presets Group
        preset_group = QGroupBox("Gyors elrendezési arányok (Viz vs Kód)")
        preset_layout = QHBoxLayout(preset_group)

        btn_viz = QPushButton("Viz fókusz (~70/30)")
        btn_viz.clicked.connect(lambda: self.set_preset("viz_focus"))
        preset_layout.addWidget(btn_viz)

        btn_equal = QPushButton("Egyenlő (50/50)")
        btn_equal.clicked.connect(lambda: self.set_preset("equal"))
        preset_layout.addWidget(btn_equal)

        btn_code = QPushButton("Kód fókusz (~30/70)")
        btn_code.clicked.connect(lambda: self.set_preset("code_focus"))
        preset_layout.addWidget(btn_code)

        layout.addWidget(preset_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Mégse")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Alkalmaz & Mentés")
        btn_save.setStyleSheet("background: #00b894; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.on_save)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        self.pending_preset_sizes = None

    def set_preset(self, preset_type: str):
        if preset_type == "viz_focus":
            self.pending_preset_sizes = [700, 300]
        elif preset_type == "code_focus":
            self.pending_preset_sizes = [300, 700]
        else:
            self.pending_preset_sizes = [500, 500]

    def on_save(self):
        self.config.font_family = self.font_combo.currentText()
        self.config.font_size = self.size_spin.value()
        self.config.theme = self.theme_combo.currentData()
        self.config.syntax_highlight = self.syntax_check.isChecked()
        self.config.show_line_numbers = self.line_num_check.isChecked()
        self.config.auto_scroll_to_line = self.scroll_check.isChecked()
        self.config.splitter_orientation = self.orient_combo.currentData()
        self.config.sidebar_collapsed = self.sidebar_collapsed_check.isChecked()

        if self.pending_preset_sizes:
            self.config.splitter_sizes = self.pending_preset_sizes

        self.config.save()
        self.accept()
