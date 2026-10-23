# CodeLab HU - Algoritmus Műhely

Platformfüggetlen, Linux-first edukációs app.

## Szerkezet - többfájlos, bővíthető

```
codelab_hu/
├── main.py                 # Belépési pont
├── requirements.txt
├── core/
│   ├── config.py           # Magyar UI szövegek, algoritmus lista, nyelvek
│   ├── engine.py           # Algoritmus motor - generátoros lépések
│   └── __init__.py
├── languages/
│   ├── templates.py        # C, C++, Python, BASIC, Java, Pascal sablonok
│   └── __init__.py
├── ui/
│   ├── main_window.py      # NAGY központi ablak - QMainWindow + Splitterek
│   ├── widgets.py          # ArrayViewer, CodeViewer, StatsBar
│   └── __init__.py
└── assets/                 # Később: ikonok, hangok
```

## Indítás (Linux, Windows, Mac)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python3 main.py
```

## Bővítés menete

1. Új algoritmus: `core/engine.py`-ba új `*_steps` generátor + `core/config.py`-ba bejegyzés + `languages/templates.py`-ba kódminták
2. Új nyelv: `LANGUAGES` listába + `templates.py`-ba sablonok
3. Új viewer: `ui/widgets.py`-ba új widget osztály

A lényeg: minden modul független, a főablak csak összeköti őket.
