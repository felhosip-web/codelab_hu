# CodeLab HU

![CI](https://github.com/felhosip-web/codelab_hu/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-3.5.0-blue.svg)
![License](https://img.shields.io/badge/license-GNU%20GPL%20v3-green.svg)
![Plugins](https://img.shields.io/badge/plugins-20-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

**CodeLab HU** egy magyar nyelvű, moduláris, interaktív algoritmus-vizualizáló és programstruktúra-oktató alkalmazás. Célja, hogy látványos és lépésről lépésre követhető módon mutassa be az alapvető és haladó informatikai koncepciókat, algoritmusokat, adatstruktúrákat, kódolási eljárásokat és vezérlési szerkezeteket.

---

## 🚀 Gyors indítás

### 1. Klónozás
```bash
git clone https://github.com/felhosip-web/codelab_hu.git
cd codelab_hu
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
- **REST API (v1.0) & API Kezelő (v3.0)**: Biztonságos REST API felület beépített engedélyezési lehetőségekkel, valamint dinamikus API Manager 3.0 feature flag érvényesítéssel és hook csatlakozásokkal.
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

## 🔒 Biztonság és Reverse Proxy Telepítés (Security & Reverse Proxy Deployment)

A CodeLab HU REST API (`core/rest_api.py`) beépített biztonsági funkciókkal (API kulcs hitelesítés, sandbox folyamat-izoláció, IP ellenőrzés és kéréskorlátozás) rendelkezik. Termelési (production) vagy hálózaton keresztüli használat esetén az API-t ajánlott egy reverse proxy (pl. Nginx) mögött futtatni HTTPS védelemmel.

Az alábbiakban olvasható a reverse proxy mögötti működés elemzése, a biztonsági határok és a támogatott telepítési útmutató.

---

### 1. Közvetlen kapcsolat vs. Reverse Proxy működés

A `core/rest_api.py` komponensben a `SecureRESTHandler` az IP-alapú hozzáférés-ellenőrzést és logolást a hálózati socket közvetlen peer címéből (`self.client_address[0]`) nyeri ki.

- **Közvetlen kapcsolat esetén**: A `self.client_address[0]` a hálózaton csatlakozó kliens valódi IP-címét tartalmazza.
- **Reverse Proxy mögött**: A hálózati kapcsolat a proxy és a backend között jön létre, így a `self.client_address[0]` minden bejövő kérésnél a **proxy IP-címét** (alapértelmezetten hurokfelület esetén `127.0.0.1`-et) mutatja, nem a távoli kliensét.

**Ennek hatása a backend biztonsági beállításaira (`RESTConfig` és `APIKey`):**

1. **IP engedélyezési lista (`allowed_ips` és `block_unknown_ips`)**:
   - Ha a `block_unknown_ips = True` beállítás aktív, a proxy IP-címének (pl. `127.0.0.1`) szerepelnie kell az `allowed_ips` listában (az alapértelmezés: `["127.0.0.1"]`).
   - Távoli kliens IP-címek hozzáadása a backend `allowed_ips` listájához hatástalan a proxy mögött, mivel a backend mindig csak a proxy IP-címét látja.
2. **API kulcs IP whitelist (`APIKey.ip_whitelist`)**:
   - Ha egy API kulcshoz be van állítva `ip_whitelist` (pl. `["203.0.113.5"]`), a proxyn keresztül érkező kérések elutasításra kerülnek (`"IP 127.0.0.1 nincs a kulcs whitelistjén"` hibaüzenettel), mert a backend socket címe `127.0.0.1`.
3. **Logolás (`saves/api_access.log`)**:
   - A beépített hozzáférési napló kliens IP-címként a proxy címét (`127.0.0.1`) rögzíti minden proxizott kérésnél.
4. **IP-alapú kéréskorlátozás (`RateLimiter`)**:
   - A globális rate limit (`rate_limit_global_per_min`, alapértelmezetten 100 kérés/perc) a `global:<client_ip>` kulcs alapján gyűjti a kéréseket. Reverse proxy mögött **az összes kliens kérése egyetlen IP-vödörbe (`global:127.0.0.1`) sorolódik**, így egyetlen kliens nagy kérésszáma kimerítheti a keretet az összes többi felhasználó számára is.

---

### 2. Továbbított fejlécek (Forwarded Headers) és megbízhatósági határok

- **Fejlécek figyelmen kívül hagyása**: A jelenlegi `core/rest_api.py` megvalósítás **NEM** dolgozza fel és **NEM** használja az `X-Forwarded-For`, `X-Real-IP` vagy hasonló HTTP fejléceket a kliens azonosítására.
- **Konfiguráció tisztázása**: A proxy oldalon az `X-Forwarded-For` vagy `X-Real-IP` fejlécek beállítása önmagában **nem eredményezi** azt, hogy a backend alkalmazás érvényesítse a szabályokat az eredeti kliens IP-címére.
- **Megbízhatósági határ (Trust Boundary)**: A kliens által küldött HTTP fejlécek önkényes elfogadása sérülékenységhez (IP-spoofing) vezetne. Kódszintű ellenőrzött proxy architektúra (Trusted Proxy ellenőrzés) nélkül a fejlécek nem használhatók biztonsági döntésekhez.
- **Kerülendő megoldások**: **Soha ne adjon hozzá** publikus vagy tetszőleges kliens IP-címeket a backend `allowed_ips` listájához a proxy működés megkerülése érdekében.

---

### 3. Biztonságos Telepítési Útmutató (Safe Deployment Guidance)

Reverse proxy mögötti publikálás esetén kövesse az alábbi biztonsági irányelveket:

1. **Loopback kötés**: Tartsa a backendet a hurokfelületre kötelezve (`RESTConfig.host = "127.0.0.1"`), ha a proxy és az alkalmazás ugyanazon a gépen fut.
2. **Közvetlen elérés tiltása**: Tűzfal vagy hálózati szabályok segítségével biztosítsa, hogy a backend portja (alapértelmezetten `8000`) közvetlenül kívülről ne legyen elérhető.
3. **HTTPS/TLS használata**: A nyilvánosság felé néző reverse proxyn mindig kötelezővé kell tenni a HTTPS (TLS) használatát.
4. **API kulcs hitelesítés**: Hagyja bekapcsolva az API kulcs követelményt (`RESTConfig.require_api_key = True`), és kövesse a legkisebb jogosultság elvét az endpoint engedélyeknél (`enable_read_endpoints`, `enable_write_endpoints`, `enable_execute_endpoints`, `enable_admin_endpoints`).
5. **Kliens IP szűrés és rate limit a proxynál**: Mivel a backend nem tudja megbízhatóan megkülönböztetni az egyes kliens IP-címeket, az IP-alapú korlátozásokat, bant és per-kliens rate limit-et a **reverse proxy rétegben** (pl. Nginx `limit_req_zone`) kell beállítani.
6. **Adminisztrátori figyelmeztetés**: A backend IP-ellenőrzései az összes proxizott kérést egyetlen IP-címnek látják. Az rendszeradminisztrátorok ezt nem téveszthetik össze az egyedi kliensenkénti kényszerítéssel.

---

### 4. Konfigurációs Példa (Nginx Reverse Proxy)

Az alábbiakban egy minimális, biztonságos Nginx példakonfiguráció látható, amely a HTTPS kéréseket a `127.0.0.1:8000` címen futó CodeLab HU backendhez továbbítja:

```nginx
# Per-kliens rate limiting zóna meghatározása az eredeti IP ($binary_remote_addr) alapján
limit_req_zone $binary_remote_addr zone=codelab_api_limit:10m rate=10r/s;

server {
    listen 443 ssl http2;
    server_name codelab.example.com;

    # SSL/TLS tanúsítványok beállítása
    ssl_certificate /etc/letsencrypt/live/codelab.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/codelab.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Kérésméret korlátozása (igazodva a backend max_request_size_kb beállításához)
    client_max_body_size 1m;

    location /api/ {
        # Rate limit érvényesítése a proxynál kliensenként
        limit_req zone=codelab_api_limit burst=20 nodelay;

        # Továbbítás a loopbacken futó CodeLab HU REST API backend felé
        proxy_pass http://127.0.0.1:8000;

        # HTTP fejlécek továbbítása naplózási és audit célból
        # Figyelem: A backend jelenleg nem módosítja az IP-ellenőrzéseit ezen fejlécek alapján!
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Időtúllépési beállítások
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }
}
```

#### Védelmi vezérlők megoszlása (Proxy vs. Backend):

| Biztonsági vezérlő | Felelős réteg | Leírás |
| :--- | :--- | :--- |
| **HTTPS / TLS Titkosítás** | **Reverse Proxy (Nginx)** | Nyilvános kapcsolat védelme. |
| **Eredeti Kliens IP Rate Limit** | **Reverse Proxy (Nginx)** | Per-kliens kéréskorlátozás (`limit_req`). |
| **Kliens IP Szűrés & Ban** | **Reverse Proxy (Nginx)** | Nem kívánt IP-címek blokkolása (`allow`/`deny`). |
| **API Kulcs Hitelesítés** | **CodeLab HU Backend** | `X-API-Key` ellenőrzés SHA-256 hasheléssel. |
| **Endpoint Jogosultságok** | **CodeLab HU Backend** | `read`, `write`, `execute`, `admin` engedélyek ellenőrzése. |
| **Homokozó Izoláció** | **CodeLab HU Backend** | Kód végrehajtás szeparált folyamatban korlátozott memóriával és időkorláttal. |

---

### 5. Korlátozások és Jövőbeli Fejlesztések (Limitations & Future Work)

- **Jelenlegi korlátozás**: A `core/rest_api.py` jelenlegi megvalósítása **nem tartalmaz** megbízható proxy-tudatos (trusted-proxy) kliens IP-kiemelést.
- **Jövőbeli fejlesztés**: Az eredeti kliens IP-címek backend oldali biztonságos azonosítása és ellenőrzése (pl. konfigurálható `trusted_proxies` lista és `X-Forwarded-For` érvényesítés) egy különálló jövőbeli kódfejlesztési feladat keretében valósulhat meg. A jelenlegi kódváltozat nem módosítja a futásidejű viselkedést.

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

- **Szerző**: Péter Felhősi (FePe) / **Hes Projects ® by FePe** (2024-2026)
- **Licenc**: GNU General Public License v3.0 (GNU GPL v3) (lásd: [LICENSE](LICENSE) és [LICENSE.txt](LICENSE.txt)).

*Powered by Hes Projects ® by FePe*
