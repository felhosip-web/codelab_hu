# -*- coding: utf-8 -*-
"""
Központi ablak - PLUGIN RENDSZERŰ verzió
Az alaprendszer nem változik, csak pluginokat tölt be
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSplitter, QListWidget, QComboBox, QSlider,
    QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import random

from core.config import UI_TEXTS, LANGUAGES, APP_NAME
from core.plugin_system import PluginLoader
from ui.widgets import ArrayViewerWidget, CodeViewerWidget, StatsBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(UI_TEXTS["app_title"])
        self.resize(1366, 900)
        
        # PLUGIN BETÖLTÉS - ez a kulcs!
        self.plugin_loader = PluginLoader()
        self.plugin_loader.load_all()
        self.plugins_list = self.plugin_loader.list_plugins()
        
        # Adatok
        self.current_array = [3, 4, 6, 8, 9, 5, 2, 10, 7, 1]
        self.current_plugin = self.plugins_list[0] if self.plugins_list else None
        self.steps = []
        self.current_step_idx = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.is_playing = False
        
        # Központi widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5,5,5,5)
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # BAL OLDAL
        left_panel = QFrame()
        left_panel.setMaximumWidth(260)
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("📚 Algoritmusok (Pluginok)"))
        self.algo_list = QListWidget()
        for plugin in self.plugins_list:
            self.algo_list.addItem(f"{plugin.icon} {plugin.name}")
        if self.plugins_list:
            self.algo_list.setCurrentRow(0)
        self.algo_list.currentRowChanged.connect(self.on_algo_changed)
        left_layout.addWidget(self.algo_list)
        
        left_layout.addWidget(QLabel("💻 Nyelv"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANGUAGES)
        self.lang_combo.setCurrentText("C++")
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        left_layout.addWidget(self.lang_combo)
        
        left_layout.addWidget(QLabel("⚙️ Vezérlés"))
        btn_layout = QVBoxLayout()
        self.btn_play = QPushButton(f"▶ {UI_TEXTS['play']}")
        self.btn_step = QPushButton(f"⏭ {UI_TEXTS['step']}")
        self.btn_reset = QPushButton(f"↻ {UI_TEXTS['reset']}")
        self.btn_new = QPushButton(f"🎲 {UI_TEXTS['new_array']}")
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_step.clicked.connect(self.next_step)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_new.clicked.connect(self.new_array)
        for b in [self.btn_play, self.btn_step, self.btn_reset, self.btn_new]:
            btn_layout.addWidget(b)
        left_layout.addLayout(btn_layout)
        
        left_layout.addStretch()
        self.plugin_info = QLabel("")
        self.plugin_info.setWordWrap(True)
        self.plugin_info.setStyleSheet("background: #e8f4f8; padding: 6px; border-radius: 4px; font-size: 10px;")
        left_layout.addWidget(self.plugin_info)
        
        left_layout.addWidget(QLabel("Sebesség"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 1000)
        self.speed_slider.setValue(300)
        self.speed_slider.setInvertedAppearance(True)
        left_layout.addWidget(self.speed_slider)
        
        # JOBB OLDAL
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.stats_bar = StatsBar()
        right_layout.addWidget(self.stats_bar)
        
        center_splitter = QSplitter(Qt.Vertical)
        self.array_viewer = ArrayViewerWidget(self.current_array)
        self.code_viewer = CodeViewerWidget()
        center_splitter.addWidget(self.array_viewer)
        center_splitter.addWidget(self.code_viewer)
        center_splitter.setSizes([350, 500])
        right_layout.addWidget(center_splitter)
        
        self.explanation_label = QLabel("Készen áll a rendezésre. Nyomj Lejátszást!")
        self.explanation_label.setStyleSheet("background: #2d2d3d; color: white; padding: 10px; border-radius: 6px; font-size: 13px;")
        self.explanation_label.setWordWrap(True)
        right_layout.addWidget(self.explanation_label)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([260, 1100])
        
        self.reset()
        if self.current_plugin:
            self.on_language_changed("C++")
            self.update_plugin_info()
    
    def update_plugin_info(self):
        if self.current_plugin:
            self.plugin_info.setText(f"{self.current_plugin.icon} {self.current_plugin.name}\n{self.current_plugin.description}\n{self.current_plugin.time_complexity} / {self.current_plugin.space_complexity}")
            self.stats_bar.set_complexity(self.current_plugin.time_complexity, self.current_plugin.space_complexity)
    
    def on_language_changed(self, lang):
        if not self.current_plugin: return
        code = self.current_plugin.get_code(lang)
        self.code_viewer.set_code(code, lang)
        self.code_viewer.set_title(f"{self.current_plugin.id}.cpp - {lang}")
    
    def on_algo_changed(self, row):
        if row < 0 or row >= len(self.plugins_list): return
        self.current_plugin = self.plugins_list[row]
        self.on_language_changed(self.lang_combo.currentText())
        self.update_plugin_info()
        self.reset()
    
    def reset(self):
        self.timer.stop()
        self.is_playing = False
        self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
        self.current_step_idx = 0
        if self.current_plugin:
            self.steps = list(self.current_plugin.get_steps(self.current_array))
        else:
            self.steps = []
        if self.steps:
            self.show_step(self.steps[0])
    
    def new_array(self):
        self.current_array = [random.randint(1, 20) for _ in range(10)]
        self.reset()
    
    def toggle_play(self):
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
        else:
            self.timer.start(self.speed_slider.value())
            self.is_playing = True
            self.btn_play.setText(f"⏸ {UI_TEXTS['pause']}")
    
    def next_step(self):
        if self.current_step_idx < len(self.steps) - 1:
            self.current_step_idx += 1
            self.show_step(self.steps[self.current_step_idx])
        else:
            self.timer.stop()
            self.is_playing = False
            self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
            self.explanation_label.setText("✅ Kész! A tömb rendezve van.")
    
    def show_step(self, step):
        self.array_viewer.update_state(step.array, step.key, step.sorted_end, step.highlight)
        self.code_viewer.highlight_line(step.code_line)
        self.explanation_label.setText(f"{UI_TEXTS['pass']} {step.pass_num} | {step.explanation}")
        self.stats_bar.update_stats(step.comparisons, step.shifts, step.pass_num)
