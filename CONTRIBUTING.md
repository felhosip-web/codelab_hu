# Contributing to CodeLab HU

Köszi hogy segítenél! Magyar oktató app, magyarul.

## Hogyan adj hozzá új algoritmust?

1. Forkold a repót
2. `git checkout -b feature/b-fa-plugin`
3. Csinálj mappát: `mkdir plugins/bfa`
4. Írj `plugin.py`-t:

```python
from core.plugin_system import AlgorithmPluginBase

class BFAPlugin(AlgorithmPluginBase):
    id = "bfa"
    name = "B-fa"
    version = "1.0.0"
    api_version_required = "1.0.0"
    plugin_type = "tree"  # sort, search, graph, tree, hash
    # ...
```

5. Adj hozzá `manifest.json`-t
6. Teszteld: `python3 main.py`
7. Commit: `git commit -m "feat: B-fa plugin v1.0.0"`
8. Push + Pull Request

## Commit üzenetek

- `feat: új plugin` - új funkció
- `fix: javítás` - bugfix
- `docs: dokumentáció`
- `refactor: plugin rendszer` - refaktor
- Használd a SemVer-t: `MAJOR.MINOR.PATCH`

## Verziózás

- Fő program: `core/version.py` → `MAIN_VERSION`
- Plugin API: `PLUGIN_API_VERSION` → breaking change esetén major
- Plugin: saját `version`

## Kérdés?

Nyiss egy Issue-t magyarul vagy angolul.
