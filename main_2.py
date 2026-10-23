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
from core.config import APP_NAME
from core.version import MAIN_VERSION, PLUGIN_API_VERSION, get_version_string

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(str(MAIN_VERSION))
    
    print(f"=== {APP_NAME} ===")
    print(f"Verzió: {get_version_string()}")
    print("========================")
    
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
