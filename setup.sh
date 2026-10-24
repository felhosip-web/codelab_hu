#!/bin/bash
# Hes Projects ® by FePe - CodeLab HU Setup
echo "© Hes Projects ® by FePe - CodeLab HU Setup"
echo "Telepítés..."

# Python check
python3 --version || { echo "Python3 kell!"; exit 1; }

# Pip install PySide6
pip3 install PySide6 || pip install PySide6

# Futtatás
echo "Indítás: python3 main.py"
python3 main.py

echo "✅ Kész!"
