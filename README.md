# CodeLab HU

![Version](https://img.shields.io/badge/version-3.4.0-blue.svg)
![License](https://img.shields.io/badge/license-GNU%20GPL%20v3-green.svg)
![Plugins](https://img.shields.io/badge/plugins-20%2B-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

**CodeLab HU** egy magyar nyelvű, moduláris, interaktív algoritmus-vizualizáló és programstruktúra-oktató alkalmazás. Célja, hogy látványos és lépésről lépésre követhető módon mutassa be az alapvető és haladó informatikai koncepciókat, algoritmusokat, adatstruktúrákat, kódolási eljárásokat és vezérlési szerkezeteket.

---

## 🚀 Gyors indítás

### 1. Kónozás
```bash
git clone https://github.com/felhosi/codelab-hu.git
cd codelab-hu
```

### 2. Függőségek telepítése
```bash
pip install -r requirements.txt
```

### 3. Alkalmazás indítása
```bash
python main.py
```

---

## ✨ Főbb funkciók

- **Interaktív vizualizáció**: Lépésről lépésre követhető algoritmus-végrehajtás valós idejű kiemeléssel.
- **Többnyelvű kódnézet**: C++, Python, Java, C#, Pascal és Pseudokód nézetek az algoritmusokhoz.
- **Vezérlési gombok**: Lejátszás/szünet, manuális léptetés előre/hátra, sebességállítás és csúszka.
- **Dinamikus paraméterezés**: Bemeneti adatok, tömbméretek és egyéb paraméterek finomhangolása.
- **Breakpoint rendszer**: Feltételes és hit-count töréspontok támogatása.
- **Állapotkezelés & Mentés**: Munkamenetek mentése, visszatöltése, undo/redo támogatás.
- **REST API & API Kezelő**: Biztonságos API felület beépített engedélyezési és tesztelési lehetőségekkel.
- **Bővíthető Plugin-architektúra**: Ismert interfészre épülő, függetlenül tölthető modulok.

---

## 🔌 Plugin kategóriák és bonyolultsági szintek

Az alkalmazásban található modulok a kezdő szinttől az oktatási és szakértői szintekig terjednek:

| Bonyolultsági szint | Kategória | Tartalom / Modulok |
| :--- | :--- | :--- |
| **🟢 Kezdő (Beginner)** | **Programstruktúra & Vizualizáció** | Szekvencia, elágazás, ciklusok, függvények, moduláris felépítés (`program_structure`, `simple_visual`, `wow_easy`) |
| | **Tömb alapok** | Tömbök, pointerek, 2D tömbök és beágyazott struktúrák (`array_concepts`) |
| | **Alapvető rendezések** | Buborék rendezés, beszúró rendezés, kiválasztó rendezés (`bubble`, `insertion`, `selection`) |
| | **Alapvető keresések** | Lineáris és bináris keresés (`search`) |
| **🟡 Középhaladó (Intermediate)** | **Hatékony rendezések** | Gyors rendezés (Quick Sort), összefésülő rendezés (Merge Sort) (`quick`, `merge`) |
| | **Adatstruktúrák** | Verem (LIFO), sor (FIFO), körkörös sor, deque, láncolt lista (`fifo_lifo`, `structures`) |
| | **Gráfok és Fák** | Szélességi (BFS) és mélységi (DFS) keresés, Gráf alapok (`graph`) |
| **🔴 Haladó (Advanced)** | **Kiegyensúlyozott Fák** | AVL-fák, B-fák, Bináris keresőfák (`balanced`) |
| | **Szövegkeresés** | KMP (Knuth-Morris-Pratt), Rabin-Karp algoritmusok (`string_search`) |
| | **Kódolás & Tömörítés** | Huffman-kódolás, RLE (Run-Length Encoding) (`encoding`) |
| | **Haladó algoritmusok** | A* útvonaltervezés, dinamikus programozás (`advanced`) |
| **🟣 Mester / Expert** | **Hibajavítás & Ellenőrzés** | CRC32 és Reed-Solomon hibajavító kódok (`crc_rs`) |
| | **Jelfeldolgozás** | Diszkrét Fourier Transzformáció (DFT/FFT) (`fourier`) |
| | **Kriptográfia** | Enigma rejtjelező gép szimuláció (`enigma`) |

---

## 🤝 Hozzájárulás (Contribution)

Bármilyen hozzájárulást örömmel fogadunk!
1. Forkold a repót.
2. Hozz létre egy új feature branch-et (`git checkout -b feature/uj-plugin`).
3. Commitold a változtatásaidat (`git commit -m 'feat: új plugin hozzáadása'`).
4. Pushold a branch-et (`git push origin feature/uj-plugin`).
5. Nyiss egy Pull Requestet.

A részletes plugin-készítési útmutatót és szabályokat a [CONTRIBUTING.md](CONTRIBUTING.md) fájlban találod.

---

## 📜 Licenc és Szerző

- **Szerző**: Péter Felhősi (FePe) / **HES Projects® by FePe®** (2024-2026)
- **Licenc**: GNU General Public License v3.0 (GNU GPL v3) + HES Projects® feltételek (lásd: [LICENSE](LICENSE) és [LICENSE.txt](LICENSE.txt)).

*Powered by HES Projects® by FePe®*
