# CodeLab HU v3.4.0 FINAL - HES Projects® by FePe® - Komplett GitHub csomag

© HES Projects® by FePe® - Péter Felhősi - 2024-2026
Licenc: GNU GPL v3 + HES Projects® Terms - LICENSE.txt

## 🚀 Telepítés - Kompletten újra

```bash
# 1. Letöltés
unzip codelab_hu_CLEAN_FINAL.zip
cd codelab_hu_CLEAN_FINAL

# 2. GitHub beállítás (első alkalom)
git init
git remote add origin https://github.com/FELHASZNALO/codelab-hu.git

# 3. Függőség
pip install PySide6
# vagy
./setup.sh

# 4. Futtatás
python3 main.py

# 5. GitHub push
./push.sh "feat: v3.4.0 Program Szerkezet" v3.4.0
```

## 📦 Tartalom - Komplett

- main.py - belépési pont
- LICENSE.txt - GNU GPL v3 + HES Projects®
- README.md, README_GITHUB.md
- push.sh - GitHub push script (message + tag)
- setup.sh - telepítés + indítás
- .gitignore - Python, saves, venv ignore
- .github/workflows/ci.yml - GitHub Actions CI
- core/ - 18 modul (api, engine, breakpoints, complexity, rest, license, fourier, fifo_lifo, array_concepts...)
- plugins/ - 20 plugin mappa, 54 plugin
- ui/ - 11 modul (main_window, widgets, dialogok, splash wow)
- languages/ - nyelvi sablonok

## 🎯 54 plugin - Bonyolultsági szintek

🟢 Kezdő (16): Változók, If Else, For, While, Faktoriális, Fibonacci, LNKO, Bitek, Palindrom, Hatvány...
🟡 Könnyű (20): Függvények, Prímszita, Hanoi, Verem, Sor, Számláló, Láncolt lista, Prímtényezős, Bitek...
🟠 Közepes (10): Quick, Merge, KMP, DFT...
🔴 Nehéz (8): BFS, DFS, Dijkstra, Huffman, Enigma...
⚫ Expert (7): FFT, CRC, RS...

Wow! Ez igen! - Splash induláskor, bitek villognak, palindrom tükör, láncolt lista nyilak!

## 🔌 GitHub scriptek

push.sh:
```bash
#!/bin/bash
git add .
git commit -m "$1 - HES Projects® by FePe®"
git tag -a "$2" -m "$2"
git push origin main
git push origin "$2"
```

setup.sh:
```bash
pip install PySide6
python3 main.py
```

## © Licenc

GNU GPL v3 + HES Projects® Terms
Powered by HES Projects® by FePe®
