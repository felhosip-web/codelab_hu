# -*- coding: utf-8 -*-
"""
Központi ablak - PLUGIN RENDSZERŰ verzió
Az alaprendszer nem változik, csak pluginokat tölt be
"""
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.config import APP_NAME, LANGUAGES, UI_TEXTS
from core.plugin_system import PluginLoader
from core.engine import Engine
from core.api_manager import APIManager
from core.rest_api import SecureRESTAPIServer
from core.version import API_MANAGER_VERSION
from ui.rest_api_dialog import RESTAPIDialog
from ui.api_manager_dialog import APIManagerDialog
from ui.widgets import ArrayViewerWidget, CodeViewerWidget, StatsBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(UI_TEXTS["app_title"])
        self.resize(1366, 900)

        # API MANAGER, ENGINE ÉS PLUGIN BETÖLTÉS
        self.api_manager = APIManager()
        self.engine = Engine(api_manager=self.api_manager)
        self.plugin_loader = PluginLoader(api_manager=self.api_manager)
        self.plugin_loader.load_all()
        self.plugins_list = self.plugin_loader.list_plugins()
        self.rest_server = SecureRESTAPIServer(plugin_loader=self.plugin_loader, engine=self.engine)

        self.api_manager.register_hook("on_feature_toggle", self.refresh_plugin_list)

        # Menüsor
        menubar = self.menuBar()
        tools_menu = menubar.addMenu("🌐 API / Eszközök")
        rest_api_action = tools_menu.addAction("🔒 REST API Kezelő...")
        rest_api_action.triggered.connect(self.open_rest_api_dialog)
        api_manager_action = tools_menu.addAction(f"🔌 API Manager {API_MANAGER_VERSION}...")
        api_manager_action.triggered.connect(self.open_api_manager_dialog)

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
        main_layout.setContentsMargins(5, 5, 5, 5)

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
        self.plugin_info.setStyleSheet(
            "background: #e8f4f8; padding: 6px; border-radius: 4px; font-size: 10px;"
        )
        left_layout.addWidget(self.plugin_info)

        left_layout.addWidget(QLabel("Sebesség"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 1000)
        self.speed_slider.setValue(300)
        self.speed_slider.setInvertedAppearance(True)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        left_layout.addWidget(self.speed_slider)

        # JOBB OLDAL
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.stats_bar = StatsBar()
        right_layout.addWidget(self.stats_bar)

        center_splitter = QSplitter(Qt.Vertical)
        self.array_viewer = ArrayViewerWidget(self.current_array)
        self.code_viewer = CodeViewerWidget()

        # Bottom playback bar
        bottom_playback = QFrame()
        bottom_playback.setStyleSheet(
            "background: #2d3436; border-top: 3px solid #6c5ce7; padding: 4px;"
        )
        bottom_layout = QHBoxLayout(bottom_playback)
        self.bottom_btn_back = QPushButton("⏪")
        self.bottom_btn_back.setStyleSheet(
            "background: #fdcb6e; color: #2d3436; font-weight: bold; padding: 8px 16px; border-radius: 4px; font-size: 14px;"
        )
        self.bottom_btn_back.clicked.connect(self.on_step_back)
        bottom_layout.addWidget(self.bottom_btn_back)

        self.bottom_btn_play = QPushButton("▶")
        self.bottom_btn_play.setStyleSheet(
            "background: #00b894; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; font-size: 14px;"
        )
        self.bottom_btn_play.clicked.connect(self.on_play_pause)
        bottom_layout.addWidget(self.bottom_btn_play)

        self.bottom_btn_forward = QPushButton("⏩")
        self.bottom_btn_forward.setStyleSheet(
            "background: #74b9ff; color: #2d3436; font-weight: bold; padding: 8px 16px; border-radius: 4px; font-size: 14px;"
        )
        self.bottom_btn_forward.clicked.connect(self.on_step_forward)
        bottom_layout.addWidget(self.bottom_btn_forward)

        bottom_layout.addWidget(QLabel("|"))
        bottom_layout.addWidget(QLabel("Seb:"))
        self.bottom_speed_slider = QSlider(Qt.Horizontal)
        self.bottom_speed_slider.setRange(50, 1000)
        self.bottom_speed_slider.setValue(300)
        self.bottom_speed_slider.setInvertedAppearance(True)
        self.bottom_speed_slider.setMaximumWidth(150)
        self.bottom_speed_slider.valueChanged.connect(self.on_speed_changed)
        bottom_layout.addWidget(self.bottom_speed_slider)

        self.bottom_progress_slider = QSlider(Qt.Horizontal)
        self.bottom_progress_slider.setRange(0, 100)
        self.bottom_progress_slider.setValue(0)
        self.bottom_progress_slider.sliderMoved.connect(self.on_progress_slider_moved)
        self.bottom_progress_slider.sliderPressed.connect(self.on_progress_slider_pressed)
        self.bottom_progress_slider.sliderReleased.connect(self.on_progress_slider_released)
        bottom_layout.addWidget(self.bottom_progress_slider)

        self.bottom_progress_label = QLabel("0/0")
        self.bottom_progress_label.setStyleSheet(
            "color: white; font-family: monospace; font-weight: bold;"
        )
        bottom_layout.addWidget(self.bottom_progress_label)
        bottom_layout.addWidget(QLabel("|"))

        self.bottom_btn_breakpoint = QPushButton("BP")
        self.bottom_btn_breakpoint.setStyleSheet(
            "background: #e74c3c; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px;"
        )
        self.bottom_btn_breakpoint.clicked.connect(self.on_toggle_breakpoint)
        bottom_layout.addWidget(self.bottom_btn_breakpoint)

        self.bottom_playback = bottom_playback

        center_splitter.addWidget(self.array_viewer)
        center_splitter.addWidget(self.code_viewer)
        center_splitter.setSizes([350, 500])
        right_layout.addWidget(center_splitter)

        self.explanation_label = QLabel("Készen áll a rendezésre. Nyomj Lejátszást!")
        self.explanation_label.setStyleSheet(
            "background: #2d2d3d; color: white; padding: 10px; border-radius: 6px; font-size: 13px;"
        )
        self.explanation_label.setWordWrap(True)
        right_layout.addWidget(self.explanation_label)
        right_layout.addWidget(self.bottom_playback)

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([260, 1100])

        self.reset()
        if self.current_plugin:
            self.on_language_changed("C++")
            self.update_plugin_info()
        self.refresh_plugin_list()

    def update_plugin_info(self):
        if self.current_plugin:
            self.plugin_info.setText(
                f"{self.current_plugin.icon} {self.current_plugin.name}\n{self.current_plugin.description}\n{self.current_plugin.time_complexity} / {self.current_plugin.space_complexity}"
            )
            self.stats_bar.set_complexity(
                self.current_plugin.time_complexity, self.current_plugin.space_complexity
            )

    def on_language_changed(self, lang):
        if not self.current_plugin:
            return
        code = self.current_plugin.get_code(lang)
        self.code_viewer.set_code(code, lang)
        self.code_viewer.set_title(f"{self.current_plugin.id}.cpp - {lang}")

    def on_algo_changed(self, row):
        if row < 0 or row >= len(self.plugins_list):
            return
        self.current_plugin = self.plugins_list[row]
        self.on_language_changed(self.lang_combo.currentText())
        self.update_plugin_info()
        self.reset()

    def reset(self):
        self.timer.stop()
        self.is_playing = False
        self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
        self.bottom_btn_play.setText("▶")
        self.current_step_idx = 0
        if self.current_plugin:
            self.steps = list(self.current_plugin.get_steps(self.current_array))
        else:
            self.steps = []
        if self.steps:
            self.bottom_progress_slider.setRange(0, len(self.steps) - 1)
            self.show_step(self.steps[0])
        else:
            self.bottom_progress_slider.setRange(0, 0)
            self.bottom_progress_label.setText("0/0")

    def new_array(self):
        self.current_array = [random.randint(1, 20) for _ in range(10)]
        self.reset()

    def refresh_plugin_list(self, *args, **kwargs):
        self.plugins_list = self.plugin_loader.list_plugins()
        self.algo_list.blockSignals(True)
        self.algo_list.clear()
        for plugin in self.plugins_list:
            self.algo_list.addItem(f"{plugin.icon} {plugin.name}")
        self.algo_list.blockSignals(False)
        if self.plugins_list:
            if self.current_plugin not in self.plugins_list:
                self.algo_list.setCurrentRow(0)
                self.on_algo_changed(0)
            else:
                idx = self.plugins_list.index(self.current_plugin)
                self.algo_list.setCurrentRow(idx)
        else:
            self.current_plugin = None
            self.update_plugin_info()
            self.reset()

        # Update UI features (playback, breakpoints)
        playback_ok = self.api_manager.is_feature_enabled("playback") and self.api_manager.config.enable_animations
        self.btn_play.setEnabled(playback_ok)
        self.bottom_btn_play.setEnabled(playback_ok)
        if not playback_ok and self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
            self.bottom_btn_play.setText("▶")

        bp_ok = self.api_manager.is_feature_enabled("breakpoints") or self.api_manager.is_feature_enabled("advanced_breakpoints")
        self.bottom_btn_breakpoint.setEnabled(bp_ok)
        if not bp_ok:
            self.bottom_btn_breakpoint.setToolTip("Breakpoint funkció kikapcsolva (API Manager)")
        else:
            self.bottom_btn_breakpoint.setToolTip("Töréspont ki/be kapcsolása")

        perf_ok = self.api_manager.is_feature_enabled("performance_monitor")
        self.stats_bar.setVisible(perf_ok)

    def toggle_play(self):
        if not self.api_manager.is_feature_enabled("playback") or not self.api_manager.config.enable_animations:
            self.next_step()
            return

        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
            self.bottom_btn_play.setText("▶")
        else:
            anim_speed = max(0.1, self.api_manager.config.animation_speed)
            speed = int(self.speed_slider.value() / anim_speed)
            self.timer.start(speed)
            self.is_playing = True
            self.btn_play.setText(f"⏸ {UI_TEXTS['pause']}")
            self.bottom_btn_play.setText("⏸")

    def next_step(self):
        if self.current_step_idx < len(self.steps) - 1:
            self.current_step_idx += 1
            self.show_step(self.steps[self.current_step_idx])
        else:
            self.timer.stop()
            self.is_playing = False
            self.btn_play.setText(f"▶ {UI_TEXTS['play']}")
            self.bottom_btn_play.setText("▶")
            self.explanation_label.setText("✅ Kész! Az algoritmus végrehajtása befejeződött.")

    def on_step_back(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.show_step(self.steps[self.current_step_idx])

    def on_step_forward(self):
        self.next_step()

    def on_play_pause(self):
        self.toggle_play()

    def on_speed_changed(self, value):
        if self.speed_slider.value() != value:
            self.speed_slider.setValue(value)
        if self.bottom_speed_slider.value() != value:
            self.bottom_speed_slider.setValue(value)
        if self.is_playing:
            self.timer.setInterval(value)

    def on_progress_slider_moved(self, value):
        if 0 <= value < len(self.steps):
            self.current_step_idx = value
            self.show_step(self.steps[self.current_step_idx])

    def on_progress_slider_pressed(self):
        if self.is_playing:
            self.timer.stop()

    def on_progress_slider_released(self):
        val = self.bottom_progress_slider.value()
        if 0 <= val < len(self.steps):
            self.current_step_idx = val
            self.show_step(self.steps[self.current_step_idx])
        if self.is_playing:
            self.timer.start(self.speed_slider.value())

    def open_rest_api_dialog(self):
        dialog = RESTAPIDialog(self.rest_server, plugin_loader=self.plugin_loader, engine=self.engine, parent=self)
        dialog.exec()

    def open_api_manager_dialog(self):
        dialog = APIManagerDialog(self.api_manager, parent=self)
        dialog.exec()
        self.refresh_plugin_list()

    def on_toggle_breakpoint(self):
        # Breakpoint toggling for the current step line
        pass

    def show_step(self, step):
        self.array_viewer.update_state(step.array, step.key, step.sorted_end, step.highlight)
        self.code_viewer.highlight_line(step.code_line)
        self.explanation_label.setText(f"{UI_TEXTS['pass']} {step.pass_num} | {step.explanation}")
        self.stats_bar.update_stats(step.comparisons, step.shifts, step.pass_num)
        self.bottom_progress_slider.setValue(self.current_step_idx)
        self.bottom_progress_label.setText(f"{self.current_step_idx + 1}/{len(self.steps)}")
