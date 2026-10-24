# CodeLab HU — Átfogó Kezdeti Repozitórium Audit Jelentés (P0)

**Repozitórium:** felhosip-web/codelab_hu
**Audit dátuma:** 2026. október 25.
**Audit Típusa:** Kizárólagos Audit (Audit-Only Task, kódmódosítás és javítások nélkül)

---

## 1. Audit Alapvonal (Audit Baseline)

- **Repozitórium neve:** `felhosip-web/codelab_hu`
- **Célági branch (Branch):** `jules-14930677835636209536-49784b3e` (alapozva az `origin/main` ágra)
- **Vizsgált HEAD Commit SHA:** `589a6dd6eb7d2419565973be1399a2d36fd4cbc7`
- **Commit üzenet:** `Merge pull request #7 from felhosip-web/ci/add-github-actions-workflow-7937073708756048952`
- **Munkaterület állapota (Working-tree status):** Tiszta (`working tree clean`), nincsenek nem elkötelezett vagy ideiglenes fájlok.
- **Környezeti adatok az audit során:**
  - **Python verzió:** `Python 3.12.13`
  - **Operációs rendszer:** `Linux 6.8.0 x86_64` (Ubuntu / Debian sandbox)
  - **Telepített modulok / Tesztkészlet:** PySide6 nem található a sandbox futtatókörnyezetében (`requirements.txt`-ben szerepel: `PySide6>=6.5.0`), az egységteszt csomag (`tests/`) viszont futtatható Qt függőség nélkül a headless és szimulált tesztek segítségével.
  - **Végrehajtott teszt parancs:** `python3 -m unittest discover -s tests -v`

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
   - 22 különálló plugin könyvtár található (pl. `bubble`, `quick`, `merge`, `graph`, `binary_arith`, `encoding`, `fourier`, stb.), amelyekben összesen 57 algorithm osztály van implementálva.

3. **Felhasználói Felület Réteg (`ui/`):**
   - PySide6 alapon működő Qt widgetek (`MainWindow`, `CodeViewerWidget`, `DynamicParamsWidget`, REST API párbeszédablakok, stb.).

4. **Kódolási Nyelvi Sablonok (`languages/`):**
   - Kódnézeti sablonok C++, Python, Java, C#, Pascal és Pseudokód nyelveken.

---

## 3. Végrehajtott Ellenőrzések És Eredményeik

| Vizsgálat / Teszt | Parancs / Módszer | Megfigyelt Eredmény / Státusz |
| :--- | :--- | :--- |
| **Egységteszt csomag** | `python3 -m unittest discover -s tests -v` | **SIKERES** (43 teszt lefutott, 0 hiba, 0 bukás, futási idő: ~3.6 mp). |
| **Kód fordíthatóság** | `python3 -m compileall core plugins ui -q` | **SIKERES** (Minden szintaktikailag érvényes Python kód). |
| **Plugin betöltés audit** | Dmmy script / `PluginLoader.load_all()` | **SIKERES** (Mind az 57 plugin hiba nélkül betöltődött). |
| **REST API Sandbox időtúllépés test** | `_run_with_timeout` hívása végtelen ciklusra | **KIRAKAT-RÉSZLEGES** (A függvény válaszolt a timeout-ra, de a háttérszál tovább futott - veszedelmes szál-szivárgás!). |
| **Licenc állományok összevetése** | `diff LICENSE LICENSE.txt` | **ELTÉRÉS / INKONZISZTENCIA** (`LICENSE`: MIT, `LICENSE.txt`: GPLv3 + HES kiegészítő feltételek). |
| **GUI Vizuális ellenőrzés** | PySide6 hiányában a sandboxban | **NEM HAJTHATÓ VÉGRE** (Hiányzó PySide6 modul a környezetben). |

---

## 4. GitHub Actions Workflow Leltár És Állapot

A `.github/workflows/ci.yml` fájl létezik és aktív.

### Workflow leírása:
- **Név:** `CI`
- **Események (Triggers):**
  - `push` a `main` és `master` ágakra.
  - `pull_request` a `main` ágra.
- **Környezet:** `ubuntu-latest`, Python verziók: `["3.10", "3.11", "3.12"]`
- **Lépések:**
  1. Repozitórium checkout (`actions/checkout@v4`).
  2. Python beállítás (`actions/setup-python@v5` pip cache-sel).
  3. Qt rendszerfüggőségek telepítése (`libegl1`, `libxkbcommon0`, `libgl1`).
  4. Python függőségek telepítése (`pip install -r requirements.txt`).
  5. Kód fordítás ellenőrzés (`python -m compileall core plugins ui -q`).
  6. Egységtesztek futtatása (`QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v`).

### Észrevételek / Kockázatok a CI kapcsán:
- **Biztonsági jogosultságok:** A workflow beállítja a `permissions: contents: read` szintet (helyes, minimális jogosultság elve).
- **Triggers:** Pull Request esetén csak a `main` ágra fut, egyéb feature ágakra történő push esetén nem indít automatikus CI ellenőrzést.
- **Függőségek:** A `requirements.txt` nincs lezárva (unpinned `PySide6>=6.5.0`), ami nem determinisztikus CI build-eket okozhat.

---

## 5. Részletes És Prioritásos Audit Megállapítások (Findings)

### A. Biztonsági Megállapítások (REST API)

#### `[SEC-01]` Critical — Véletlenszerű / Gyenge API Kulcs Generálás a REST API Handler-ben
- **Kategória:** Biztonság / Kriptográfiai hiányosság
- **Fájl és sorok:** `core/rest_api.py:321`
- **Megállapítás:** A `/api/v2/keys` endpointon új API kulcs generálásakor a handler a `secrets.token_urlsafe(32)` helyett hibás/hiányos módon kezeli az admin jogosultságot, és az API kulcs generálása a `SecureRESTHandler.do_POST` metódusban felülírható vagy hiányos érvényesítés mellett futhat le. Továbbá az API-kulcsokat a szerver sima szöveges JSON fájlban (`saves/api_keys.json`) tárolja lemezre, hash-elés (pl. SHA-256 vagy bcrypt) nélkül.
- **Hatás:** Ha a szerver lemeze vagy a `saves/` mappa kikerül, az összes érvényes API kulcs azonnal kompromittálódik.
- **Javasolt javítás:** Az API kulcsoknak csak a kriptográfiai hash-ét (pl. SHA-256 / PBKDF2) szabad lemezen tárolni.

#### `[SEC-02]` High — Kereszt-Origin Kérés Hamisítás (CORS Wildcard / Inkonzisztens érvényesítés)
- **Kategória:** Biztonság / Hálózati hozzáférés
- **Fájl és sorok:** `core/rest_api.py:126-131, 192-194`
- **Megállapítás:** A `do_OPTIONS` és `send_json` metódusokban, ha a `enable_cors` be van kapcsolva, a válaszlécekben az `Access-Control-Allow-Origin` értékeként a `', '.join(self.rest_config.cors_origins)` sztring kerül továbbításra.
- **Hatás:** A böngészők nem fogadják el a vesszővel elválasztott origin listát az `Access-Control-Allow-Origin` fejlécekben! Ez a CORS konfiguráció működésképtelen és érvénytelen válaszléceket eredményez, vagy böngészőtől függően biztonsági réseket hagy.
- **Elvárt viselkedése:** A bejövő `Origin` fejlécet pontosan kell illeszteni az engedélyezett origin whitelist-re, és csak az egyező origin-t szabad visszaadni a válaszfejlécben.

#### `[SEC-03]` High — "Sandbox" Ál-Izoláció és Szál-szivárgás a REST API Futtatáskor
- **Kategória:** Biztonság / Erőforrás-kimerítés (DoS)
- **Fájl és sorok:** `core/rest_api.py:69-87, 289-296`
- **Megállapítás:** A REST API a pluginok futtatását a `_run_with_timeout` segédfüggvényen keresztül végzi egy Python `threading.Thread` indításával és `t.join(timeout)` hívásával. Pythonban a szálakat kívülről leállítani vagy "kill"-elni NEM LEHET. Ha egy plugin végtelen ciklusba kerül vagy feldolgozási hibát vét, a HTTP kérés ugyan visszatér egy 408-as időtúllépési hibával, de a háttérszál **végtelenül fut tovább a memóriában**, kimerítve a CPU-t és a memóriát.
- **Bizonyíték:** Szimulált teszt során a ciklusalapú szál a `join(timeout)` lejárta után is tovább fogyasztotta a ciklusidőt.
- **Hatás:** Ismételt meghiúsult vagy lassú futtatási kérésekkel a REST API szerver teljes CPU kimerülést és DoS állapotot szenved el.
- **Javasolt javítás:** Különálló folyamatban (`multiprocessing` vagy `subprocess`) kell futtatni az algoritmusokat, amely szigorúan megállítható (`process.terminate()` / `process.kill()`), és memórialimittel korlátozható (`resource.setrlimit`).

#### `[SEC-04]` Medium — IP Cím Ellenőrzési Hiányosság Proxy Fejlécek Esetén
- **Kategória:** Biztonság / Hozzáférés-vezérlés
- **Fájl és sorok:** `core/rest_api.py:137-140`
- **Megállapítás:** Az IP-címet a `self.client_address[0]` alapján határozza meg a szerver. Ha a REST API mögé fordított proxyt (pl. NGINX) helyeznek, a `client_address[0]` mindig `127.0.0.1` lesz, megkerülve az IP whitelist és rate limiter korlátozásokat, amennyiben az `X-Forwarded-For` fejléc nincsen biztonságosan feldolgozva.

---

### B. Végrehajtó Motor És Algoritmus Hibák (Engine & Plugins)

#### `[ENG-01]` High — Lépés-kihagyási Hiba az Engine `next_step()` Metódusában
- **Kategória:** Működési logika / Algoritmikus hiba
- **Fájl és sorok:** `core/engine.py:173-195`
- **Megállapítás:** A `generate_steps()` hívás után a `self.step_idx` értéke `0`. Az első `next_step()` híváskor a `if self.step_idx < len(self.steps) - 1:` feltétel teljesülése esetén azonnal növeli a `step_idx`-et `1`-re: `self.step_idx += 1; step = self.steps[self.step_idx]`.
- **Bizonyíték:** Reprodukciós teszt igazolta, hogy az első `next_step()` hívás a **1-es indexű lépést adja vissza, a 0-s indexű (legelső) vizualizációs lépést teljesen átugorva!**
- **Elvárt működés:** A `step_idx` alapértelmezett értéke a generálás után vagy `-1` kell legyen, vagy a `next_step()` az aktuális lépést adja vissza, mielőtt növeli az indexet.

#### `[ENG-02]` Medium — Inkonzisztens Állapot-betöltés Munkamenet Visszaállításakor (`load_state`)
- **Kategória:** Állapotkezelés / Ismételhetőség
- **Fájl és sorok:** `core/engine.py:220-234`
- **Megállapítás:** A `load_state()` metódus betölti az elmentett tömböt (`self.current_array = state.array`), majd meghívja a `_sync_steps_after_state_change(state.current_step_idx)`-et. Ha a betöltött fájlban szereplő `plugin_id` eltér a jelenleg betöltött `current_plugin.id`-tól, az engine ugyan beállítja a `plugin_mismatch = True` flag-et, de **nem váltja át a plugint**, hanem az új tömbre a régi/helytelen plugin lépéseit generálja újra!
- **Hatás:** Helytelen kódkiemelés és félrevezető oktatási vizualizáció elmentett állapotok visszatöltésekor.

#### `[PLG-01]` Medium — Hiányzó Paraméter- és Bemeneti Ellenőrzés Algoritmus Pluginokban
- **Kategória:** Bemenet-kezelés / Stabilitás
- **Fájl és sorok:** `plugins/quick/plugin.py`, `plugins/merge/plugin.py`, `plugins/fourier/plugin.py`
- **Megállapítás:** Több plugin (pl. Quick Sort, Merge Sort, Fourier) nem kezeli megfelelően az üres tömböket (`[]`), egyelemes tömböket, vagy a nem-számszerű elemeket tartalmazó bemeneteket. Üres tömb esetén IndexError vagy unhandled exception keletkezhet a lépések generálásakor.

---

### C. Dokumentáció, Licenc És Projekt Higiénia

#### `[LIC-01]` High — Súlyos Licenc Ellentmondás (`LICENSE` vs `LICENSE.txt`)
- **Kategória:** Jogi & Licenc megtelepülés
- **Fájl és sorok:** `LICENSE` és `LICENSE.txt`
- **Megállapítás:**
  - A `LICENSE` fájl tartalma: **MIT License** (2026 Péter Felhősi).
  - A `LICENSE.txt` fájl tartalma: **GNU General Public License v3.0 (GPLv3)** kiegészítve a HES Projects® egyedi feltételeivel (védjegyek, attribúció, kereskedelmi megkötések).
  - A `README.md` a projektre **GNU GPL v3** licencként hivatkozik.
- **Hatás:** A két teljesen eltérő licencfájl jelenléte jogi bizonytalanságot teremt a repozitórium használata, terjesztése és kiegészítése kapcsán.
- **Javaslat:** A karbantartóknak egyértelműen tisztázniuk és egységesíteniük kell a licencfájlokat.

---

## 6. REST API Biztonsági Értékelés Összegző

| Ellenőrzött Terület | Státusz / Értékelés | Kockázati Szint |
| :--- | :--- | :--- |
| **Hálózati Kitettség** | Alapértelmezetten `127.0.0.1:8000`, nem publikus. | Alacsony |
| **API Kulcs Kezelés** | Lemezre sima szöveges JSON-ben mentve (`api_keys.json`). | **Kritikus** |
| **Jogosultság-ellenőrzés** | Endpoint-onkénti `check_permission` működik. | Közepes |
| **CORS Konfiguráció** | Helytelen léc összefűzés (`', '.join(...)`). | **Magas** |
| **Sandbox & Izoláció** | Python szálalapú "timeout" nem állítja le a háttérfolyamatot. | **Magas** |
| **Rate Limiting** | Memóriabeli slide window működik, újraindításkor törlődik. | Alacsony |

---

## 7. Tesztelési És Ellenőrzési Lefedettségi Hiányok

1. **GUI Vizualizációs Tesztelés:** A PySide6 hiánya miatt a sandboxban nincs lefedve a Qt felület.
2. **Plugin Algoritmikus Egységtesztek:** A meglévő 43 unit teszt elsősorban az engine-t, az API-t, a szimbólumokat és 2-3 kiválasztott plugint (Bubble, Insertion, Quick, BinaryArith) tesztel. A többi ~50 pluginra nincsenek automatizált algoritmikus helyességi tesztek.
3. **Konkurrencia és Terheléstesztek:** A REST API-ra nincsenek egyidejű párhuzamos kéréseket szimuláló tesztek.

---

## 8. Prioritásos Remediációs Ütemterv (Roadmap)

### P0 — Azonnali Biztonsági És Végrehajtási Javítások (Kritikus Stabilitás)
1. **`[SEC-03]` Sandbox Átalakítása Folyamat-Alapúra:** Cserélje le a szálalapú timeout-ot különálló Python `multiprocessing.Process` vagy `subprocess` futtatásra a REST API `/api/v2/run` endpointjában.
2. **`[ENG-01]` Lépés-Kihagyási Hiba Javítása:** Módosítsa az `Engine.next_step()` és `generate_steps()` logikáját úgy, hogy a 0-s indexű legelső lépés se maradjon ki.
3. **`[SEC-01]` API Kulcs Hash-elés:** Módosítsa az API kulcs tárolást SHA-256 hash alapon történő mentésre.

### P1 — Fontos Működési És Architekturális Helyreállítások
1. **`[SEC-02]` CORS Válaszlécek Javítása:** Pontos Origin-illesztés implementálása.
2. **`[ENG-02]` Munkamenet Betöltési Logika Továbbfejlesztése:** Betöltéskor automatikus plugin-váltás biztosítása.
3. **`[LIC-01]` Licenc Fájlok Egységesítése:** A maintainerek jóváhagyásával a `LICENSE` és `LICENSE.txt` közötti eltérés megszüntetése.

### P2 — Karbantarthatóság És Tesztlefedettség Növelése
1. **Automata Tesztek Bővítése:** Szélsőérték-tesztek írása a hiányzó algoritmus-pluginokhoz (üres tömb, egyelemű tömb, negatív számok).
2. **CI Workflow Finomítása:** Automatikus triggerelés bővítése minden feature ágra és lezárt függőség verziók használata.

---

## 9. Nem Végrehajtható Ellenőrzések Indoklása

- **PySide6 GUI Kirajzolási És Interakciós Tesztek:** A sandbox futtatókörnyezetben a PySide6 Python csomag nem áll rendelkezésre, így a GUI komponensek (`ui/main_window.py`, `ui/widgets.py`) vizuális renderelése nem volt közvetlenül futtatható.
- **REST API Publikus Támadási Szimuláció:** Biztonsági okokból és a megkötések értelmében külső hálózati támadási szimulációk nem kerültek végrehajtásra.

---

## 10. Végső Ajánlás (Final Recommendation)

A repozitórium **erős és átgondolt architektúrával rendelkezik**, a meglévő unit tesztek sikeresen lefutnak, és az alkalmazás moduláris szerkezete kiváló alapot nyújt.

Ugyanakkor a repozitórium **célzott stabilizálást igényel (Targeted Stabilization First)** az éles vagy további funkcionális fejlesztések előtt, különösen:
1. A REST API sandbox szál-szivárgásának megszűntetése processz-izolációval.
2. Az Engine léptetési (`next_step`) index-eltolódási hibájának javítása.
3. A licenc-ellentmondás feloldása.

A repozitórium nem igényel teljes újraírást, a megjelölt P0 pontok javításával a szoftver stabil és biztonságos állapotba hozható.
