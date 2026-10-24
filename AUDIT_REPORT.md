# CodeLab HU — Átfogó Kezdeti Repozitórium Audit Jelentés (Pontosított Verzió)

**Repozitórium:** felhosip-web/codelab_hu
**Audit dátuma:** 2026. október 25.
**Audit Típusa:** Kizárólagos Audit Jelentés Felülvizsgálata és Pontosítása (PR #8 Final Evidence & Metadata Pass)

---

## 1. Audit Alapvonal És Metaadatok (Audit Baseline)

Az audit során az alábbi elkülönített commit metaadatok érvényesek:

- **Vizsgált forráskód alapvonal (Inspected Source Baseline):** `589a6dd6eb7d2419565973be1399a2d36fd4cbc7` (`origin/main`, Pull Request #7 merge commit)
- **Előző felülvizsgálat indításkori PR HEAD commitja:** `bab1f321521dfbcc05d370e9343666f005469c37`
- **Jelen audit feladat indításkori PR HEAD commitja (Inspected PR HEAD):** `fb8bb20e4f1372cb73cb2254506ad3f5d4716877`
- **Munkaterület állapota (Working-tree status):** Az audit során kizárólag az `AUDIT_REPORT.md` kerül frissítésre, az alkalmazás forráskódja, tesztjei és konfigurációi sértetlenek.
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
| **Egységteszt csomag** | `python3 -m unittest discover -s tests -v` | **SIKERES** (43 teszt lefutott, 0 hiba, 0 bukás, futási idő: ~3.5 mp). |
| **Kód fordíthatóság** | `python3 -m compileall core plugins ui -q` | **SIKERES** (Minden szintaktikailag érvényes Python kód). |
| **Plugin betöltés audit** | `PluginLoader.load_all()` | **SIKERES** (Mind az 57 plugin hiba nélkül betöltődött). |
| **Plugin reprodukciós mérések** | `QuickSort`, `MergeSort`, `DFT`, `FFT` tesztelése `[]`, `[5]`, `[5, 3]`, `['a', 'b']` adatokkal | **DOKUMENTÁLT KÍSÉRLETI BIZONYÍTÉK**: Lásd 5/B szakasz (egyik sem dobott nem kezelt kivételt). |
| **REST API szál-timeout teszt** | `_run_with_timeout` hívása végtelen ciklusra | **KÍSÉRLETI BIZONYÍTÉK**: A függvény válaszolt a timeout-ra (408/500), de a daemon Python `threading.Thread` szál tovább futott a háttérben. |
| **REST API memória korlát ellenőrzése** | `sandbox_max_memory_mb` keresése a kód útvonalain | **IBA**: A `sandbox_max_memory_mb: int = 50` beállítás szerepel a `core/rest_api.py:47`-ben, de **sehol sincs érvényesítve** a futtatási útvonalon. |
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
- **Igazolt tények:** A `/api/v2/keys` endpointon a kulcsgenerálás a `secrets.token_urlsafe(32)` függvényt használja (kriptografikusan biztonságos), és ellenőrzi az `admin` jogosultságot (`check_permission(key_obj, "admin")`). Az API kulcsokat a szerver nyílt szöveges JSON fájlban (`saves/api_keys.json`) tárolja lemezre (`asdict(v)`).
- **Fenyegetési modell és hatás:** Ha a szerver helyi fájlrendszere vagy a `saves/` mappa kikerül (pl. nem megfelelő jogosultságok, biztonsági mentés kiszivárgása vagy directory traversal sérülékenység miatt), az API kulcsok kiolvashatók.
- **Súlyosság indoklása (Medium):** Helyi localhost használat és megfelelő fájlrendszer-jogosultságok esetén a közvetlen tetszőleges távoli hozzáférés nem lehetséges.
- **Javasolt fejlesztési opció:** Az API-kulcsok lemezen történő tárolásakor megfontolandó a kriptográfiai hash-elés (pl. SHA-256), szem előtt tartva az API-kulcsok egyszeri megtekintési folyamatát és visszavonási architektúráját.

#### `[SEC-02]` Low — CORS Válaszlécek Összefűzési Formátumhibája
- **Kategória:** Biztonság / Hálózati konfiguráció
- **Fájl és sorok:** `core/rest_api.py:126-131, 192-194`
- **Igazolt tények:** A `do_OPTIONS` és `send_json` metódusokban, ha a `enable_cors` engedélyezve van, a szerver az `Access-Control-Allow-Origin` fejléc értékeként a `', '.join(self.rest_config.cors_origins)` sztringet küldi vissza.
- **Hatás:** A W3C CORS specifikáció szerint a böngészők nem fogadják el a vesszővel elválasztott origin listát a válaszfejlécben. Ez böngészőoldali konfigurációs és kompatibilitási hibát eredményez. Ez nem jelent autorizációs bypass-t!
- **Súlyosság indoklása (Low):** Tényleges biztonsági átlépési lehetőséget nem biztosít, csupán böngészőoldali működési akadályt okoz a beállított origins esetén.
- **Javasolt javítás:** A bejövő `Origin` kérésfejlécet illeszteni kell az engedélyezett `cors_origins` listára, és a győztes match-et kell visszaadni az `Access-Control-Allow-Origin` fejlécben.

#### `[SEC-03]` Medium / Conditional Risk — Szál-szivárgás Timeout Esetén és Nem Érvényesített Memórialimit
- **Kategória:** Biztonság / Erőforrás-kezelés
- **Fájl és sorok:** `core/rest_api.py:47, 69-87, 289-296`
- **Igazolt tények:**
  1. A REST API a pluginok futtatását a `_run_with_timeout` segédfüggvényen keresztül végzi (`threading.Thread` + `t.join(timeout)`). Kísérletileg igazolt, hogy végtelen ciklus esetén a HTTP kérés válaszol ugyan időtúllépéssel, de a háttérszál tovább fut.
  2. A `RESTConfig` osztályban definiált `sandbox_max_memory_mb: int = 50` beállítás **sehol sincs érvényesítve a végrehajtási útvonalon**.
- **Fenyegetési modell és előfeltételek:** A REST API alapértelmezetten tiltva van (`enabled: False`), csak localhoston hallgat (`127.0.0.1`), és az `/api/v2/run` endpoint használatához `execute` jogosultságú API-kulcs szükséges.
- **Súlyosság indoklása (Medium / Conditional Risk):** A szál nem áll le, és a memórialimit nincs kikényszerítve, de a beállított előfeltételek (kikapcsolt állapot, jogosultság) miatt a tetszőleges távoli DoS közvetlenül nem hívható elő. Ezért a kockázat nem P0, hanem P1 prioritású közepes kockázat.
- **Javasolt javítás (P1):** Folyamat-alapú futtatásra (`multiprocessing` vagy `subprocess`) való áttérés, amellyel az időtúllépéskor a munkamenet leállítható (`process.terminate()`), és a memórialimit is kikényszeríthető.

#### `[SEC-04]` Informational — IP-cím Ellenőrzés Direct-Server Kontextusban
- **Kategória:** Biztonság / Hozzáférés-vezérlés
- **Fájl és sorok:** `core/rest_api.py:137-140`
- **Igazolt tények:** Az IP-cím ellenőrzése a `self.client_address[0]` alapján történik. Direct-serverként (localhoston) ez teljesen megfelelően működik. Reverse proxy mögötti telepítésnél dokumentációs megjegyzést igényel.

---

### B. Végrehajtó Motor És Algoritmus Megállapítások (Engine & Plugins)

#### `[ENG-01]` Informational / Architecture Design — Lépés-indexelési Logika és Kezdőállapot Kezelés
- **Kategória:** Architektúra / Kezdőállapot felépítés
- **Fájl és sorok:** `core/engine.py:206-250`
- **Igazolt tények:** A `generate_steps()` hívása után a `self.step_idx` értéke `0`. Az `Engine.next_step()` hívásakor az index `1`-re nő (`self.step_idx += 1`), és a 1-es indexű lépést adja vissza.
- **Működési kontextus és UI elemzés:** A GUI `MainWindow.sync_from_engine()` és `reset()` metódusai a `generate_steps()` után a `self.engine.steps[0]` lépést jelenítik meg mint **kezdőállapotot** (0. lépés - pl. a rendezetlen tömb beállítása). Az "Előre" gomb megnyomásakor a `next_step()` a 1-es indexű transzformációt adja vissza.
- **Összegzés és Súlyosság (Informational):** A 0. lépés nem veszik el, hanem a kezdőállapotot képviseli az UI-ban. Ez az architektúra szándékos tervezési döntése.

#### `[ENG-02]` Informational / User Warning — Munkamenet Betöltési Logika (`load_state`)
- **Kategória:** Állapotkezelés / UI jelzés
- **Fájl és sorok:** `core/engine.py:280-300`, `ui/state_manager_dialog.py:105-112`
- **Igazolt tények:** A `load_state()` metódus betölti a mentett tömböt, és ha a mentésben lévő `plugin_id` eltér a jelenlegitől, beállítja a `state.plugin_mismatch = True` flag-et. A `StateManagerDialog.on_load` metódus ezt a flag-et ellenőrzi, és kifejezett figyelmeztető üzenetet mutat a felhasználónak: *"Figyelem: A mentett plugin eltér a jelenlegi plugintól!"*.
- **Súlyosság (Informational):** A rendszer nem folytatja csendben a működést, hanem értesíti a felhasználót. Ennek felülbírálása vagy az automatikus plugin-váltás bevezetése terméktervezési döntés.

#### `[PLG-01]` Informational / Coverage Gap — Algoritmus Pluginok Reprodukciós Mérései
- **Kategória:** Tesztlefedettség / Kísérleti bizonyíték
- **Fájl és sorok:** `plugins/quick/plugin.py`, `plugins/merge/plugin.py`, `plugins/fourier/plugin.py`
- **Igazolt tények és reprodukciós mérések:**
  A kijelölt pluginok közvetlen futtatásával kapott tényleges kísérleti eredmények:
  - **QuickSort (`plugins/quick/plugin.py`):**
    - Üres bemenet `[]`: 2 lépés (kezdő és befejező lépés, nem dobott kivételt).
    - Egyelemes bemenet `[5]`: 2 lépés (kezdő és befejező lépés, nem dobott kivételt).
    - Érvényes numerikus `[5, 3]`: 5 lépés.
    - Nem-numerikus `['a', 'b']`: 5 lépés (a Python karaktereit összehasonlítva lefutott).
  - **MergeSort (`plugins/merge/plugin.py`):**
    - Üres bemenet `[]`: 2 lépés.
    - Egyelemes bemenet `[5]`: 2 lépés.
    - Érvényes numerikus `[5, 3]`: 7 lépés.
    - Nem-numerikus `['a', 'b']`: 7 lépés.
  - **DFT (`plugins/fourier/plugin.py` - `DFTPlugin`):**
    - Bármely bemenet (`[]`, `[5]`, `[5, 3]`, `['a', 'b']`): a plugin saját alapértelmezett sine jelét generálja (10 lépés), nem függ a bemeneti tömbtől.
  - **FFT (`plugins/fourier/plugin.py` - `FFTPlugin`):**
    - Bármely bemenet (`[]`, `[5]`, `[5, 3]`, `['a', 'b']`): a plugin saját alapértelmezett jeltípusát generálja (9 lépés).
- **Súlyosság (Informational / Coverage Gap):** A vizsgálat igazolta, hogy a pluginok nem dobnak kivételt üres vagy nem-numerikus adatokra. Ajánlott további automata szélsőérték-tesztek írása a tesztlefedettség növelésére.

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
| **CORS Konfiguráció** | Vesszővel elválasztott origin lécek összefűzése (W3C hiba). | **Low** |
| **Sandbox & Izoláció** | Python szálalapú "timeout" nem állítja le a háttérszálat; nem érvényesített memórialimit. | **Medium / Conditional Risk** |
| **Rate Limiting** | Memóriabeli csúsztatott ablak működik. | Alacsony |

---

## 7. Tesztelési És Ellenőrzési Lefedettségi Hiányok

1. **GUI Vizualizációs Tesztelés:** A PySide6 hiánya miatt a tesztkörnyezetben a Qt felületi komponensek nem tölthetők be.
2. **Plugin Algoritmikus Egységtesztek:** A 43 meglévő egységteszt az alapvető keretrendszert és 3-4 kiválasztott plugint tesztel. A többi pluginra automata egységtesztek írása javasolt.

---

## 8. Prioritásos Remediációs Ütemterv (Roadmap)

### P0 — Azonnali Stabilitási / Kritikus Teendők
*Megjegyzés: A jelenlegi kódbázisban közvetlen távoli kihasználhatóságú P0 kritikus biztonsági rés nem azonosítható (mivel a REST API alapértelmezetten tiltott és kizárólag localhoston hallgat).*

### P1 — Fontos Működési És Architekturális Helyreállítások
1. **`[SEC-03]` Sandbox Átalakítása Folyamat-Alapúra:** A szálalapú timeout cseréje `multiprocessing.Process` vagy `subprocess` futtatásra a REST API `/api/v2/run` endpointjában a garantált leállíthatóság és a memórialimit (`sandbox_max_memory_mb`) érvényesítése érdekében.
2. **`[SEC-01]` API Kulcs Hash-elési Opció:** SHA-256 hash alapon történő mentés megfontolása lemezes JSON fájlba íráskor.
3. **`[SEC-02]` CORS Válaszlécek Javítása:** Pontos Origin-illesztés implementálása.
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
1. A REST API sandbox szál-szivárgásának megszüntetése és a memórialimit érvényesítése folyamat-izolációval (P1).
2. Az API kulcsok hash-elt tárolási opciója és a CORS válaszlécek javítása (P1).
3. A licencfájlok egységesítése a maintainerek által (P1).

A repozitórium nem igényel teljes újraírást, a megjelölt P1 pontok javításával a szoftver stabil és biztonságos állapotba hozható.
