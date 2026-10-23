# -*- coding: utf-8 -*-
"""
Egyedi widgetek - Array Viewer, Code Viewer, Stats
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from core.config import UI_TEXTS

class ArrayViewerWidget(QFrame):
    def __init__(self, initial_array):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #fef9e7; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        title = QLabel(f"🟩 {UI_TEXTS['array_viewer']}")
        self.title_label.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.title_label)
        
        self.key_label = QLabel(f"{UI_TEXTS['key']}: -")
        self.key_label.setStyleSheet("background: #f6b93b; padding: 8px; border-radius: 6px; font-weight: bold; font-size: 16px;")
        self.key_label.setMaximumWidth(80)
        layout.addWidget(self.key_label)
        
        self.array_container = QWidget()
        self.array_layout = QHBoxLayout(self.array_container)
        self.array_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.array_container)
        
        self.labels = []
        self.update_state(initial_array, None, 0, [])
    
    def update_state(self, array, key, sorted_end, highlights):
        # Töröljük a régi elemeket
        while self.array_layout.count():
            child = self.array_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels.clear()
        
        if key is not None:
            self.key_label.setText(f"{UI_TEXTS['key']}\n{key}")
            self.key_label.show()
        else:
            self.key_label.hide()
        
        for idx, val in enumerate(array):
            lbl = QLabel(str(val))
            lbl.setMinimumSize(45, 45)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(self._style_for(idx, sorted_end, highlights))
            font = QFont("Sans", 11, QFont.Bold)
            lbl.setFont(font)
            self.array_layout.addWidget(lbl)
            self.labels.append(lbl)
        
        # sorted / unsorted felirat
        legend = QLabel(f"<span style='color:green'>{UI_TEXTS['sorted']}</span> | <span style='color:gray'>{UI_TEXTS['unsorted']}</span>")
        legend.setAlignment(Qt.AlignCenter)
        self.array_layout.addWidget(legend)
    
    def _style_for(self, idx, sorted_end, highlights):
        base = "border-radius: 6px; border: 1px solid #333; font-weight: bold;"
        if idx in highlights:
            return base + " background: #f6b93b; color: black; border: 2px solid red;"
        if idx <= sorted_end:
            return base + " background: #6ab04c; color: white;"
        return base + " background: white; color: black;"

class CodeViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: white; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("📄 insertion_sort.cpp - Code Viewer")
        self.title_label.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.title_label)
        
        self.condition_label = QLabel("j < 0 → stop")
        self.condition_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 10px; font-weight: bold;")
        layout.addWidget(self.condition_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Monospace", 10))
        layout.addWidget(self.text_edit)
        
        self.status_bar = QLabel(f"{UI_TEXTS['pass']} 0 | {UI_TEXTS['comparisons']} 0 | {UI_TEXTS['shifts']} 0")
        self.status_bar.setStyleSheet("background: #f1f2f6; padding: 4px; font-size: 11px;")
        layout.addWidget(self.status_bar)
        
        self.current_code_lines = []
    
    def set_code(self, code, lang):
        self.current_code_lines = code.splitlines()
        self.text_edit.setPlainText(code)
    
    def highlight_line(self, line_num):
        if not self.current_code_lines:
            return
        html = ""
        for i, line in enumerate(self.current_code_lines, start=1):
            esc = line.replace("<", "&lt;").replace(">", "&gt;")
            if i == line_num:
                html += f"<div style='background: #2e86de; color: white;'><b>{i:2}: {esc}</b></div>"
            else:
                html += f"<div>{i:2}: {esc}</div>"
        self.text_edit.setHtml(f"<pre style='font-family: monospace;'>{html}</pre>")

    def set_title(self, title_text):
        self.title_label.setText(f"📄 {title_text} - Code Viewer")

class StatsBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #dfe6e9; border-radius: 8px; padding: 6px;")
        layout = QHBoxLayout(self)
        self.lbl_time = QLabel(f"{UI_TEXTS['time']}\nO(n²)")
        self.lbl_space = QLabel(f"{UI_TEXTS['space']}\nO(1)")
        self.lbl_size = QLabel(f"{UI_TEXTS['size']}\n10")
        self.lbl_lang = QLabel(f"{UI_TEXTS['language']}\nC++")
        for lbl in [self.lbl_time, self.lbl_space, self.lbl_size, self.lbl_lang]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            layout.addWidget(lbl)
    
    def set_complexity(self, time_c, space_c):
        self.lbl_time.setText(f"{UI_TEXTS['time']}\n{time_c}")
        self.lbl_space.setText(f"{UI_TEXTS['space']}\n{space_c}")

    def update_stats(self, comp, shifts, pass_num):
        self.lbl_size.setText(f"{UI_TEXTS['size']}\n10")
        # dinamikusan frissíthető lenne
