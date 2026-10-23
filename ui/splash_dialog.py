# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from core.version import MAIN_VERSION, MAIN_CODENAME

class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"CodeLab HU v{MAIN_VERSION} - Wow!")
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6c5ce7, stop:1 #a29bfe);
                border-radius: 20px;
                border: 3px solid white;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        
        title = QLabel(f"CodeLab HU v{MAIN_VERSION}")
        title.setStyleSheet("color: white; font-size: 32px; font-weight: bold; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)
        
        subtitle = QLabel(f"{MAIN_CODENAME} - HES Projects® by FePe®")
        subtitle.setStyleSheet("color: #fdcb6e; font-size: 16px; font-weight: bold; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(subtitle)
        
        wow = QLabel("Wow! Ez igen! 🚀")
        wow.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent; padding: 10px;")
        wow.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(wow)
        
        features = QLabel("""
✨ 43+ plugin - Rendezés, Keresés, Gráf, Fa, Hash, Szöveg, Kódolás, Hibajavító, Tömbök, FIFO/LIFO, Fourier, Egyszerű wow!

🟢 Kezdő: Faktoriális, Fibonacci, LNKO, Palindrom, Bitek - 2-5 perc
🟡 Könnyű: Prímszita, Hanoi, Verem, Sor, Számláló rendezés, Láncolt lista, Prímtényezős - 5-10 perc
🟠 Közepes: Quick, Merge, KMP, DFT - 10-20 perc
🔴 Nehéz: BFS, DFS, Dijkstra, Huffman, Enigma - 20-40 perc
⚫ Expert: FFT, CRC, Reed-Solomon - 40+ perc

🎮 Vezérlők: AUTO sebesség + MANUAL előre/hátra + progress csúszka mindig látható alul!
🔴 Breakpointok: feltételes, hit count, logpoint
🔌 API 2.0 + 🔒 REST API biztonságos + © HES Projects® by FePe®

Indulj a zölddel! 🟢 Kezdő -> 🟡 Könnyű -> 🟠 Közepes -> ...
        """)
        features.setStyleSheet("color: white; font-size: 12px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 10px;")
        features.setWordWrap(True)
        frame_layout.addWidget(features)
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 Indítás - Wow!")
        self.btn_start.setStyleSheet("background: #00b894; color: white; font-weight: bold; padding: 12px; border-radius: 10px; font-size: 16px;")
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)
        
        frame_layout.addLayout(btn_layout)
        
        layout.addWidget(frame)
