# CodeLab HU — Átfogó Kezdeti Repozitórium Audit Jelentés (Pontosított Verzió)

**Repozitórium:** felhosip-web/codelab_hu
**Audit dátuma:** 2026. október 25.
**Audit Típusa:** Kizárólagos Audit Jelentés Felülvizsgálata és Pontosítása (PR #8 Audit Report Validation)

---

## 1. Audit Alapvonal (Audit Baseline)

Az audit során az alábbi két commit határozottan elkülönítésre került:

- **Vizsgált forráskód alapvonal (Inspected Source Baseline):** `589a6dd6eb7d2419565973be1399a2d36fd4cbc7` (`origin/main`, Pull Request #7 merge commit)
- **Audit jelentést tartalmazó PR HEAD commit:** `ba859f481b28517f26c068f451a1df5b432fbdcc` (A korábbi PR commit az audit riport dokumentációjával)
- **Munkaterület állapota (Working-tree status):** Az audit felülvizsgálat során kizárólag az `AUDIT_REPORT.md` kerül frissítésre, az alkalmazás forráskódja, tesztjei és konfigurációi sértetlenek.
- **Környezeti adatok az audit során:**
  - **Python verzió:** `Python 3.12.13`
  - **Operációs rendszer:** `Linux 6.8.0 x86_64` (Ubuntu / Debian sandbox)
  - **Függőségek és tesztkészlet:** PySide6 modul a sandbox környezetben nincs telepítve (`requirements.txt`: `PySide6>=6.5.0`), az egységteszt csomag (`tests/`) headless módban és szimulációkkal futtatható.
  - **Végrehajtott teszt parancs:** `python3 -m unittest discover -s tests -v` (43 teszt lefutott, 0 hiba).

---

## 2. Repozitórium Architektúra És Főbb Végrehajtási Útvonalak

A CodeLab HU egy moduláris, asztali GUI-ra (PySide6) és REST API-ra épülő algoritmus-vizualizációs és oktatási keretrendszer.

### Architekturális rétegek és felelősségek:
1. **Magréteg (`core/`):**
   - `core/engine.py`: A vizualizációs lépések generálása, léptetés (`next_step`, `prev_step`), állapot-rollback, undo/redo előzménytár (`StateManager`) és teljesítménymérés.
   - `core/plugin_system.py`: A `plugins/` könyvtár alatti modulok dinamikus felfedezése, betöltése (`importlib`), kategóriákba sorolása (`FEATURE_MAPPINGS`) és érvényesítése (`PluginLoader`).
   - `core/rest_api.py`: `BaseHTTPRequestHandler` alapú HTTP szerver (`SecureRESTServer`), amely X-API-Key alapon engedélyezi a státusz lekérdezést, pluginok listázását és sandboxolt algoritmus-futtatást (`/api/v2/run`).
   - `core/step.py`: Egységesített `VisualizationStep` leíró adatstruktúra immutable tömbsnapshot támogatással.
   - `core/api_manager.py` & `core/workspace_config.py`: Feature flag-ek, verzió-kompatibilitás és munkaterület-beállítások kezelése.

2. **Bővítmény / Plugin Réteg (`plugins/`):**
   - 22 különálló plugin könyvtár (pl. `bubble`, `quick`, `merge`, `graph`, `binary_arith`, `encoding`, `fourier`, stb.), amelyekben összesen 57 algoritmus osztály van implementálva.

3. **Felhasználói Felület Réteg (`ui/`):**
   - PySide6 alapon működő Qt widgetek (`MainWindow`, `CodeViewerWidget`, `DynamicParamsWidget`, REST API párbeszédablakok, stb.).

4. **Kódolási Nyelvi Sablonok (`languages/`):**
   - Kódnézeti sablonok C++, Python, Java, C#, Pascal és Pseudokód nyelveken.

---

## 3. Végrehajtott Ellenőrzések És Eredményeik

| Vizsgálat / Teszt | Parancs / Módszer | Megfigyelt Eredmény / Státusz |
| :--- | :--- | :--- |
| **Egységteszt csomag** | `python3 -m unittest discover -s tests -v` | **SIKERES** (43 teszt lefutott, 0 hiba, 0 bukás, futási idő: ~3.0 mp). |
| **Kód fordíthatóság** | `python3 -m compileall core plugins ui -q` | **SIKERES** (Minden szintaktikailag érvényes Python kód). |
| **Plugin betöltés audit** | `PluginLoader.load_all()` | **SIKERES** (Mind az 57 plugin hiba nélkül betöltődött). |
| **REST API szál-timeout teszt** | `_run_with_timeout` hívása végtelen ciklusra | **MERT BIZONYÍTÉK**: A függvény válaszolt a timeout-ra (408/500), de a Python `threading.Thread` szál tovább futott a háttérben. |
| **Licenc állományok összevetése** | `LICENSE` vs `LICENSE.txt` tartalmi összehasonlítás | **ELTÉRÉS / INKONZISZTENCIA** (`LICENSE`: MIT, `LICENSE.txt`: GPLv3 + HES kiegészítő feltételek). |
| **GUI Vizuális ellenőrzés** | PySide6 hiányában a sandboxban | **NEM HAJTHATÓ VÉGRE** (Hiányzó PySide6 modul a környezetben). |

---

## 4. GitHub Actions Workflow Leltár És Állapot

A `.github/workflows/ci.yml` fájl ellenőrzése alapján:

### Workflow leírása:
- **Név:** `CI`
- **Események (Triggers):** `push` a `main` és `master` ágakra, valamint `pull_request` a `main` ágra.
- **Környezet:** `ubuntu-latest`, Python verziók: `["3.10", "3.11", "3.12"]`
- **Lépések:** Checkout, Python setup (pip cache-sel), Qt OS függőségek (`libegl1`, `libxkbcommon0`, `libgl1`), `requirements.txt` telepítés, `compileall` és `unittest` offscreen Qt beállítással.

### Megfigyelt CI állapoti bizonyítékok:
- A `589a6dd6eb7d2419565973be1399a2d36fd4cbc7` commit felülvizsgálata a Pull Request #7 keretében sikeres CI lefutást mutatott mindhárom Python verzión (3.10, 3.11, 3.12).
- Korlátozás: A `requirements.txt` függőségei nincsenek verzióra pontosan lezárva (`PySide6>=6.5.0`), ami jövőbeli nem determinisztikus build-eket okozhat.

---

## 5. Részletes És Igazolt Audit Megállapítások (Findings)

### A. Igazolt Biztonsági Megállapítások (REST API)

#### `[SEC-01]` Medium — API Kulcsok Plaintext Tárolása JSON Fájlban
- **Kategória:** Biztonság / Adatvédelem és tárolás
- **Fájl és sorok:** `core/rest_api.py:321, 381-385`
- **Igazolt tények:** A `/api/v2/keys` endpointon a kulcsgenerálás a `secrets.token_urlsafe(32)` függvényt használja (kriptografikusan biztonságos), és ellenőrzi az `admin` jogosultságot (`check_permission(key_obj, "admin")`). Az eredeti jelentésben szereplő állítások a gyenge kulcsgenerálásról és az autorizáció hiányáról **alaptalanok voltak és törlésre kerültek**. A valós megállapítás az, hogy az API kulcsokat a szerver nyílt szöveges JSON fájlban (`saves/api_keys.json`) tárolja lemezre (`asdict(v)`).
- **Fenyegetési modell és hatás:** Ha a szerver helyi fájlrendszere vagy a `saves/` mappa kikerül (pl. nem megfelelő jogosultságok, biztonsági mentés kiszivárgása vagy directory traversal sérülékenység miatt), az API kulcsok kiolvashatók.
- **Súlyosság indoklása (Medium):** Helyi localhost használat és megfelelő fájlrendszer-jogosultságok esetén a közvetlen tetszőleges távoli hozzáférés nem lehetséges, így a kockázat nem Critical, hanem Medium.
- **Javasolt javítás:** Az API kulcsok lemezen történő tárolásakor csak azok kriptográfiai hash-ét (pl. SHA-256) szabad elmenteni, és az ellenőrzést a bejövő kulcs hash-ének összevetésével kell végezni.

#### `[SEC-02]` Medium — Inkonzisztens CORS Válaszlécek Kezelése
- **Kategória:** Biztonság / Hálózati konfiguráció
- **Fájl és sorok:** `core/rest_api.py:126-131, 192-194`
- **Igazolt tények:** A `do_OPTIONS` és `send_json` metódusokban, ha a `enable_cors` engedélyezve van, a szerver az `Access-Control-Allow-Origin` fejléc értékeként a `', '.join(self.rest_config.cors_origins)` sztringet küldi vissza.
- **Hatás:** A W3C CORS specifikáció szerint a böngészők nem fogadják el a vesszővel elválasztott origin listát a válaszfejlécben. Ez érvénytelen válaszléchez vezet a böngészőkben, így a konfigurált CORS nem működik megfelelően.
- **Súlyosság indoklása (Medium):** Ez konfigurációs/kompatibilitási hiba, nem közvetlen biztonsági átlépési lehetőség (exploit).
- **Javasolt javítás:** A bejövő `Origin` kérésfejlécet kell illeszteni az engedélyezett `cors_origins` listára, és a győztes match-et visszaadni az `Access-Control-Allow-Origin` fejlécben.

#### `[SEC-03]` High — Szál-szivárgás a REST API Sandbox Futtatásakor Timeout Eseten
- **Kategória:** Biztonság / Erőforrás-kezelés és DoS kockázat
- **Fájl és sorok:** `core/rest_api.py:69-87, 289-296`
- **Igazolt tények:** A REST API a pluginok futtatását a `_run_with_timeout` segédfüggvényen keresztül végzi, amely egy Python `threading.Thread`-et indít el és `t.join(timeout)` hívással vár rá. A teszt igazolta, hogy ha a target függvény végtelen ciklust tartalmaz, a `t.join(timeout)` visszatér ugyan időtúllépéssel (408/500 HTTP válasz), de **a Python szál leállítatlanul tovább fut a háttérben**.
- **Hatás és feltételek:** A Python GIL és a szál-szivárgás miatt, ha a felhasználó többször egymás után végtelen ciklust eredményező futtatási kérést küld (vagy nem megbízható plugin fut), a háttérszálak kimerítik a CPU-t és a memóriát.
- **Súlyosság indoklása (High):** Bár az endpoint alapértelmezetten tiltva van és `execute` jogosultságot igényel, a "sandbox" elnevezés hamis biztonságérzetet kelt, miközben nem biztosít valódi folyamat-izolációt.
- **Javasolt javítás:** A plugin-futtatást különálló folyamatban (`multiprocessing` vagy `subprocess`) kell végezni, amely időtúllépéskor `process.terminate()` vagy `process.kill()` segítségével garantáltan leállítható.

#### `[SEC-04]` Low / Informational — IP-cím Ellenőrzés Direct-Server Kontextusban
- **Kategória:** Biztonság / Hozzáférés-vezérlés
- **Fájl és sorok:** `core/rest_api.py:137-140`
- **Igazolt tények:** Az IP-cím ellenőrzése a `self.client_address[0]` alapján történik. Direct-serverként (localhoston) ez teljesen megfelelően működik. Fordított proxy (reverse proxy) mögé helyezés esetén az `X-Forwarded-For` fejléc hiánya miatt minden kérés `127.0.0.1`-nek látszódhat.
- **Súlyosság indoklása (Informational / Low):** Alapértelmezett stand-alone futtatásnál a jelenlegi logika helyes. Kiemelendő dokumentációs szempontként proxy mögötti telepítésekhez.

---

### B. Végrehajtó Motor És Algoritmus Megállapítások (Engine & Plugins)

#### `[ENG-01]` Informational / Design Question — Lépés-indexelési Logika és Kezdőállapot Kezelés
- **Kategória:** Architektúra / Kezdőállapot felépítés
- **Fájl és sorok:** `core/engine.py:206-250`
- **Igazolt tények:** A `generate_steps()` hívása után a `self.step_idx` értéke `0`. Az `Engine.next_step()` hívásakor az index `1`-re nő (`self.step_idx += 1`), és a 1-es indexű lépést adja vissza.
- **Működési kontextus és UI elemzés:** A GUI `MainWindow.sync_from_engine()` és `reset()` metódusai a `generate_steps()` után a `self.engine.steps[0]` lépést jelenítik meg mint **kezdőállapotot** (0. lépés - pl. a rendezetlen tömb beállítása). Amikor a felhasználó először rákatint az "Előre" (Next) gombra, a `next_step()` a 1-es indexű transzformációs lépést adja vissza.
- **Összegzés és Súlyosság (Informational):** Az eredeti audit állításával ellentétben **a 0. lépés nem veszik el**, hanem a kezdőállapotot képviseli az UI-ban. Ez az architektúra szándékos tervezési döntése. Amennyiben az API használat során az első transzformációt szeretnénk lekérni, a 0. lépés a kiinduló állapot.

#### `[ENG-02]` Medium — Inkonzisztens Plugin Állapot Munkamenet Betöltésekor (`load_state`)
- **Kategória:** Állapotkezelés / Ismételhetőség
- **Fájl és sorok:** `core/engine.py:280-300`
- **Igazolt tények:** A `load_state()` metódus betölti a fájlból az elmentett tömböt (`self.current_array = state.array`), majd meghívja a `_sync_steps_after_state_change(state.current_step_idx)`-et. Ha a betöltött fájlban szereplő `plugin_id` eltér az aktuálisan beállított `current_plugin.id`-tól, az engine beállítja a `state.plugin_mismatch = True` flag-et, de **nem váltja át automatikusan a plugint**.
- **Hatás:** Amennyiben a hívó nem kezeli a `plugin_mismatch` flag-et, az új tömbre a korábbi plugin algoritmusa fut le.
- **Javasolt javítás:** A `load_state()` esetén, ha `plugin_loader` elérhető, az engine automatikusan töltse be a mentésben szereplő plugint.

#### `[PLG-01]` Low / Coverage Gap — Szélsőérték-kezelés Hiánya Egyes Pluginokban
- **Kategória:** Bemenet-kezelés / Tesztlefedettség
- **Fájl és sorok:** `plugins/quick/plugin.py`, `plugins/merge/plugin.py`, `plugins/fourier/plugin.py`
- **Igazolt tények:** Az algoritmus-pluginok többsége feltételezi a legalább 1 vagy 2 elemet tartalmazó számtömböket. Üres tömb (`[]`) átadásakor egyes rekurzív vagy indexelő algoritmusok (pl. Quick Sort, Merge Sort) szélősérték-hibát vagy üres generátort adnak vissza.
- **Súlyosság (Low):** Az UI réteg (`input_parser.py`) érvényesíti és korlátozza a bemeneteket, így a GUI felől nem érkezik malformed tömb. A pluginok közvetlen API hívásánál azonban hasznos a védelmi ellenőrzés.

---

### C. Dokumentáció, Licenc És Projekt Higiénia

#### `[LIC-01]` Medium — Licenc Fájlok Ellentmondása (`LICENSE` vs `LICENSE.txt`)
- **Kategória:** Jogi & Licenc feltételek
- **Fájl és sorok:** `LICENSE` és `LICENSE.txt`
- **Igazolt tények:**
  - `LICENSE`: MIT Licenc szöveget tartalmaz.
  - `LICENSE.txt`: GNU General Public License v3.0 (GPLv3) szöveget és kiegészítő HES Projects® feltételeket tartalmaz.
  - `README.md`: GNU GPL v3 licencként hivatkozik a projektre.
- **Hatás:** Jogi bizonytalanságot teremt a szoftver újrafelhasználásakor. A döntés a projekt karbantartóinak felelőssége.

---

## 6. REST API Biztonsági Értékelés Összegzés

| Ellenőrzött Terület | Státusz / Értékelés | Kockázati Szint |
| :--- | :--- | :--- |
| **Hálózati Kitettség** | Alapértelmezetten `127.0.0.1:8000`, nem publikus. | Alacsony |
| **API Kulcs Kezelés** | Plaintext tárolás JSON fájlban (`api_keys.json`). | **Medium** |
| **Jogosultság-ellenőrzés** | Admin és X-API-Key ellenőrzés rendben működik. | Rendben |
| **CORS Konfiguráció** | Vesszővel elválasztott origin lécek összefűzése. | **Medium** |
| **Sandbox & Izoláció** | Python szálalapú "timeout" nem állítja le a háttérszálat. | **High** |
| **Rate Limiting** | Memóriabeli csúsztatott ablak működik. | Alacsony |

---

## 7. Tesztelési És Ellenőrzési Lefedettségi Hiányok

1. **GUI Vizualizációs Tesztelés:** A PySide6 hiánya miatt a tesztkörnyezetben a Qt felületi komponensek nem tölthetők be.
2. **Plugin Algoritmikus Egységtesztek:** A 43 meglévő egységteszt az alapvető keretrendszert és 3-4 kiválasztott plugint tesztel. A többi pluginhoz szélsőérték-tesztek (üres tömb, egyelemes tömb) hozzáadása javasolt.

---

## 8. Prioritásos Remediációs Ütemterv (Roadmap)

### P0 — Kritikus Biztonsági És Stabilitási Fejlesztések
1. **`[SEC-03]` Sandbox Átalakítása Folyamat-Alapúra:** A szálalapú timeout cseréje `multiprocessing.Process` vagy `subprocess` futtatásra a REST API `/api/v2/run` endpointjában a garantált leállíthatóság érdekében.

### P1 — Fontos Működési És Architekturális Helyreállítások
1. **`[SEC-01]` API Kulcs Hash-elés:** SHA-256 hash alapon történő mentés e-mail/JSON fájlba íráskor.
2. **`[SEC-02]` CORS Válaszlécek Javítása:** Pontos Origin-illesztés implementálása.
3. **`[ENG-02]` Munkamenet Betöltési Logika Továbbfejlesztése:** Betöltéskor automatikus plugin-váltás biztosítása.
4. **`[LIC-01]` Licenc Fájlok Egységesítése:** A maintainerek döntése alapján a `LICENSE` és `LICENSE.txt` közötti eltérés megszüntetése.

### P2 — Karbantarthatóság És Tesztlefedettség Növelése
1. **Automata Tesztek Bővítése:** Szélsőérték-tesztek írása az algoritmus-pluginokhoz.
2. **CI Workflow Finomítása:** Függőségek verzióinak rögzítése (`requirements.txt`).

---

## 9. Nem Végrehajtható Ellenőrzések Indoklása

- **PySide6 GUI Kirajzolási És Interakciós Tesztek:** A tesztkörnyezetben a PySide6 Python csomag hiányában a Qt widgetek vizuális renderelése nem volt futtatható.
- **Kölcsönös Hálózati Behatolási Tesztelés:** Külső hálózati támadások szimulálása nem történt meg.

---

## 10. Végső Ajánlás (Final Recommendation)

A CodeLab HU repozitórium **architektúrája moduláris, átgondolt és jól strukturált**. A meglévő 43 egységteszt sikeresen lefut.

A projekt **célzott stabilizálást igényel (Targeted Stabilization First)**:
1. A REST API sandbox szál-szivárgásának megszüntetése folyamat-izolációval (P0).
2. Az API kulcsok hash-elt tárolása és a CORS válaszlécek javítása (P1).
3. A licencfájlok egységesítése a maintainerek által (P1).

A repozitórium nem igényel teljes újraírást, a megjelölt P0/P1 pontok javításával a szoftver stabil és biztonságos állapotba hozható.
