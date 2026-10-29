#!/bin/bash
# Hes Projects ® by FePe - CodeLab HU Setup
echo "© Hes Projects ® by FePe - CodeLab HU Setup"
echo "Telepítés..."

# Python check
python3 --version || { echo "Python3 kell!"; exit 1; }

# Pip install requirements
pip3 install -r requirements.txt || pip install -r requirements.txt

# Futtatás
echo "Indítás: python3 main.py"
python3 main.py

echo "✅ Kész!"
