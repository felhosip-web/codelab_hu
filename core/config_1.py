# -*- coding: utf-8 -*-
APP_NAME = "CodeLab HU"
APP_VERSION = "0.2.0 - Buborék + Beszúró"
AUTHOR = "Péter Felhősi"

# Magyar UI szótár - központi helyen, könnyen bővíthető
UI_TEXTS = {
    "app_title": "CodeLab HU - Algoritmus Műhely",
    "subtitle": "Vedd fel. Csúsztasd be.",
    "time": "Idő",
    "space": "Tár",
    "size": "Méret",
    "language": "Nyelv",
    "array_viewer": "Tömb Nézet",
    "code_viewer": "Kód Nézet",
    "key": "kulcs",
    "sorted": "rendezett",
    "unsorted": "rendezetlen",
    "pass": "Kör",
    "comparisons": "Összehasonlítások",
    "shifts": "Mozgatások",
    "play": "Lejátszás",
    "pause": "Szünet",
    "step": "Lépés",
    "reset": "Újrakezdés",
    "new_array": "Új tömb",
    "speed": "Sebesség",
    "explanation": "Magyarázat",
    "j_stop": "j < 0 → megáll",
}

# Algoritmusok listája - bővítéshez csak ide kell új elem
ALGORITHMS = {
    "insertion": {"name": "Beszúró rendezés", "file": "insertion_sort", "active": True},
    "bubble": {"name": "Buborék rendezés", "file": "bubble_sort", "active": True},
    "quick": {"name": "Gyors rendezés", "file": "quick_sort", "active": False},
    "merge": {"name": "Egyesítő rendezés", "file": "merge_sort", "active": False},
    "selection": {"name": "Kiválasztó rendezés", "file": "selection_sort", "active": False},
}

# Támogatott nyelvek - sablonok a languages/ mappában
LANGUAGES = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
