#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeLab HU - Algoritmus Műhely
Platformfüggetlen (Linux-first) oktató app
Indítás: python3 main.py
Függőség: pip install PySide6
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.config import APP_NAME, APP_VERSION

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Sötét téma stílus
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
