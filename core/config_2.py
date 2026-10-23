# -*- coding: utf-8 -*-
APP_NAME = "CodeLab HU"
APP_VERSION = "0.3.0 - Plugin rendszer"
AUTHOR = "Péter Felhősi"

UI_TEXTS = {
    "app_title": "CodeLab HU - Algoritmus Műhely [PLUGIN]",
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

# Most már a plugin rendszer miatt ez csak legacy, de maradhat
ALGORITHMS = {
    "insertion": {"name": "Beszúró rendezés", "file": "insertion_sort", "active": True},
    "bubble": {"name": "Buborék rendezés", "file": "bubble_sort", "active": True},
}

LANGUAGES = ["Python", "C++", "C", "BASIC", "Java", "Pascal"]
