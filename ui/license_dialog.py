# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt

class LicenseDialog(QDialog):
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("Licenc - HES Projects® by FePe® - GNU nyílt")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("© HES Projects® by FePe® - CodeLab HU - GNU GPL v3 + saját feltételek")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # Rövid licenc
        short_tab = QWidget()
        short_layout = QVBoxLayout(short_tab)
        
        short_text = QTextEdit()
        short_text.setReadOnly(True)
        short_text.setStyleSheet("font-family: monospace; font-size: 11px; background: #2d2d3d; color: #f1f2f6;")
        short_text.setText(self.license_manager.get_short_license())
        short_layout.addWidget(short_text)
        
        tabs.addTab(short_tab, "Rövid licenc")
        
        # Teljes licenc
        full_tab = QWidget()
        full_layout = QVBoxLayout(full_tab)
        
        full_text = QTextEdit()
        full_text.setReadOnly(True)
        full_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        full_text.setText(self.license_manager.get_license_text())
        full_layout.addWidget(full_text)
        
        tabs.addTab(full_tab, "Teljes LICENSE.txt")
        
        # HES Projects info
        hes_tab = QWidget()
        hes_layout = QVBoxLayout(hes_tab)
        
        hes_text = QTextEdit()
        hes_text.setReadOnly(True)
        hes_text.setStyleSheet("font-family: sans-serif; font-size: 12px; background: #dfe6e9;")
        hes_text.setText(f"""
HES Projects® by FePe®
======================

Szerző: Péter Felhősi (FePe)
Cég: HES Projects®
Projekt: CodeLab HU - Algoritmus vizualizáló
Verzió: {self.license_manager.info.version}
Copyright: {self.license_manager.info.copyright}
Licenc: {self.license_manager.info.license_type}

Védjegyek:
- HES Projects®
- HES®
- FePe®
- CodeLab HU®

Minden védjegy Péter Felhősi tulajdona.

GNU GPL v3 + HES Projects® feltételek:
-------------------------------------
1. Nyílt forráskód - szabadon használható, módosítható
2. Védjegyek védve - használatuk engedélyhez kötött
3. Attribution kötelező: "HES Projects® by FePe®"
4. Kereskedelmi használat: GPL v3 szerint, de "Powered by HES Projects® by FePe®" feltüntetése kötelező
5. Módosítás: dokumentálni kell, eredeti licenc megtartandó
6. Garancia nincs - "as is"

Kapcsolat: {self.license_manager.info.contact}

Köszönjük hogy a HES Projects® by FePe® szoftvert használod!

36 plugin:
- Rendezés, Keresés, Gráf, Fa, Hash, Szöveg, Kódolás, Hibajavító, Tömbök, FIFO/LIFO
- Breakpointok, API 2.0, REST API biztonságos, Licenc kezelés
- 2.7.0 -> 3.0.0 Final

Powered by HES Projects® by FePe®
""")
        hes_layout.addWidget(hes_text)
        
        tabs.addTab(hes_tab, "HES Projects®")
        
        layout.addWidget(tabs)
        
        close_btn = QPushButton("Bezárás - Powered by HES Projects® by FePe®")
        close_btn.setStyleSheet("background: #6c5ce7; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
