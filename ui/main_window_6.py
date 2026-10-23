# -*- coding: utf-8 -*-
"""
Központi ablak - PLUGIN + KERESÉS + MANAGER
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSplitter, QListWidget, QComboBox, QSlider,
    QFrame, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import random

from core.config import UI_TEXTS, LANGUAGES, APP_NAME
from core.plugin_system import PluginLoader
from core.version import get_version_string, MAIN_VERSION
from ui.widgets import ArrayViewerWidget, CodeViewerWidget, StatsBar
from ui.plugin_manager import PluginManagerDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.license_manager.check_license()
        self.setWindowTitle(f"{UI_TEXTS['app_title']} - v{MAIN_VERSION}")
        self.resize(1366, 900)
        
        # PLUGIN BETÖLTÉS
        self.plugin_loader = PluginLoader()
        self.plugin_loader.load_all()
        self.plugins_list = self.plugin_loader.list_plugins()
        
        # Szétválasztjuk típus szerint
        self.sort_plugins = [p for p in self.plugins_list if getattr(p, 'plugin_type', 'sort') == 'sort']
        self.search_plugins = [p for p in self.plugins_list if getattr(p, 'plugin_type', 'sort') == 'search']
        
        self.current_array = [3, 4, 6, 8, 9, 5, 2, 10, 7, 1]
        self.current_plugin = self.plugins_list[0] if self.plugins_list else None
        self.steps = []
        self.current_step_idx = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.is_playing = False
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5,5,5,5)
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # BAL OLDAL
        left_panel = QFrame()
        left_panel.setMaximumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel(f"📚 Rendezés ({len(self.sort_plugins)})"))
        self.sort_list = QListWidget()
        for plugin in self.sort_plugins:
            item = QListWidgetItem(f"{plugin.icon} {plugin.name} v{plugin.version}")
            self.sort_list.addItem(item)
        if self.sort_plugins:
            self.sort_list.setCurrentRow(0)
        self.sort_list.currentRowChanged.connect(self.on_sort_changed)
        left_layout.addWidget(self.sort_list)
        
        left_layout.addWidget(QLabel(f"🔍 Keresés ({len(self.search_plugins)})"))
        self.search_list = QListWidget()
        self.search_list.setMaximumHeight(100)
        for plugin in self.search_plugins:
            item = QListWidgetItem(f"{plugin.icon} {plugin.name} v{plugin.version}")
            self.search_list.addItem(item)
        self.search_list.currentRowChanged.connect(self.on_search_changed)
        left_layout.addWidget(self.search_list)
        
        left_layout.addWidget(QLabel("💻 Nyelv"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANGUAGES)
        self.lang_combo.setCurrentText("Python")
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        left_layout.addWidget(self.lang_combo)
        
        left_layout.addWidget(QLabel("⚙️ Vezérlés"))
        btn_layout = QVBoxLayout()
        self.btn_play = QPushButton(f"▶ {UI_TEXTS['play']}")
        self.btn_step = QPushButton(f"⏭ {UI_TEXTS['step']}")
        self.btn_reset = QPushButton(f"↻ {UI_TEXTS['reset']}")
        self.btn_new = QPushButton(f"🎲 {UI_TEXTS['new_array']}")
        self.btn_manager = QPushButton(f"🔌 Plugin Kezelő")
        self.btn_manager.setStyleSheet("background: #6c5ce7; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_step.clicked.connect(self.next_step)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_new.clicked.connect(self.new_array)
        self.btn_manager.clicked.connect(self.open_plugin_manager)
        for b in [self.btn_play, self.btn_step, self.btn_reset, self.btn_new, self.btn_manager]:
            btn_layout.addWidget(b)
        left_layout.addLayout(btn_layout)
        
        left_layout.addStretch()
        self.plugin_info = QLabel("")
        self.plugin_info.setWordWrap(True)
        self.plugin_info.setStyleSheet("background: #e8f4f8; padding: 6px; border-radius: 4px; font-size: 10px;")
        left_layout.addWidget(self.plugin_info)
        
        self.ver_label = QLabel(get_version_string())
        self.ver_label.setStyleSheet("font-size: 9px; color: gray;")
        left_layout.addWidget(self.ver_label)
        
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
        center_splitter.setSizes([400, 500])
        right_layout.addWidget(center_splitter)
        
        self.explanation_label = QLabel("Készen áll! Válassz algoritmust.")
        self.explanation_label.setStyleSheet("background: #2d2d3d; color: white; padding: 10px; border-radius: 6px; font-size: 13px;")
        self.explanation_label.setWordWrap(True)
        right_layout.addWidget(self.explanation_label)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([280, 1100])
        
        self.reset()
        if self.current_plugin:
            self.on_language_changed("Python")
            self.update_plugin_info()
    
    def open_plugin_manager(self):
        dlg = PluginManagerDialog(self.plugin_loader, self)
        dlg.exec()
    
    def update_plugin_info(self):
        if self.current_plugin:
            self.plugin_info.setText(f"{self.current_plugin.icon} {self.current_plugin.name}\n v{self.current_plugin.version} | {self.current_plugin.author}\n{self.current_plugin.description}\n{self.current_plugin.time_complexity} / {self.current_plugin.space_complexity} | {self.current_plugin.plugin_type}")
            self.stats_bar.set_complexity(self.current_plugin.time_complexity, self.current_plugin.space_complexity)
    
    def on_language_changed(self, lang):
        if not self.current_plugin: return
        code = self.current_plugin.get_code(lang)
        self.code_viewer.set_code(code, lang)
        self.code_viewer.set_title(f"{self.current_plugin.id} - {lang} v{self.current_plugin.version}")
    
    def on_sort_changed(self, row):
        if row < 0 or row >= len(self.sort_plugins): return
        self.search_list.setCurrentRow(-1)
        self.current_plugin = self.sort_plugins[row]
        self.on_language_changed(self.lang_combo.currentText())
        self.update_plugin_info()
        self.reset()
    
    def on_search_changed(self, row):
        if row < 0 or row >= len(self.search_plugins): return
        self.sort_list.setCurrentRow(-1)
        self.current_plugin = self.search_plugins[row]
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
        if getattr(self.current_plugin, 'plugin_type', 'sort') == 'search':
            self.current_array = sorted([random.randint(1, 50) for _ in range(12)])
        else:
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
            last = self.steps[-1] if self.steps else None
            if last and getattr(last, 'found_index', None) is not None and last.found_index >=0:
                self.explanation_label.setText(f"✅ Megtalálva index {last.found_index}!")
            elif last and getattr(last, 'found_index', None) == -1:
                self.explanation_label.setText("❌ Nincs találat")
            else:
                self.explanation_label.setText("✅ Kész! Rendezve.")
    
    def show_step(self, step):
        extra = getattr(step, 'extra', {})
        self.array_viewer.update_state(step.array, step.key, step.sorted_end, step.highlight, extra)
        self.code_viewer.highlight_line(step.code_line)
        if extra.get('target') is not None:
            self.code_viewer.condition_label.setText(f"Cél: {extra.get('target')} | low={extra.get('low','-')} high={extra.get('high','-')} mid={extra.get('mid','-')}")
        elif extra.get('pivot') is not None:
            self.code_viewer.condition_label.setText(f"Pivot: index {extra.get('pivot')} | [{extra.get('low')},{extra.get('high')}]")
        self.explanation_label.setText(f"{UI_TEXTS['pass']} {step.pass_num} | {step.explanation}")
        self.stats_bar.update_stats(step.comparisons, step.shifts, step.pass_num)
