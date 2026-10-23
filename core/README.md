# Core Motor 2.0 - Fejlesztések

## Új modulok

### engine.py
Központi motor:
- `StateManager`: mentés, visszatöltés, undo/redo, history (max 50), auto-save 30 sec
- `PerformanceMonitor`: mérés, avg/min/max
- `Engine`: összeköti plugin + állapot + teljesítmény

### AppState
```python
@dataclass
class AppState:
    version, plugin_id, plugin_version, array, step_idx, params, timestamp, description, stats
```

Mentés: `saves/<plugin>_<timestamp>.json`
Betöltés: `StateManager.load_from_file()`
Lista: `list_saves()` időrendben

### Undo/Redo
- `push_history(state)`: új állapot, levágja a jövőt ha középen vagy
- `undo()`: vissza
- `redo()`: előre
- `can_undo()`, `can_redo()`

### Session export/import
- `export_session()`: összes history egy fájlba
- `import_session(path)`: visszatöltés

### Performance
- `perf_monitor.start("generate_steps")`
- `perf_monitor.end("generate_steps")`
- `get_stats(name)`: count, total, avg, min, max, last

## UI integráció

### MainWindow
- `self.engine = Engine(api_manager, breakpoint_manager)`
- Plugin váltáskor / resetkor: `engine.set_plugin(plugin, array)` majd `engine.generate_steps(array)`
- Léptetés: `engine.next_step()` és `engine.prev_step()`
- Undo / Redo / Betöltés: `engine.undo()`, `engine.redo()`, `engine.load_state(path)` automatikusan újragenerálja a lépéseket és szinkronizálja a `step_idx`-et.
- `list_saves()`: automatikusan kiszűri a konfigurációs és nem AppState formátumú JSON fájlokat (`api_config`, `rest_config`, `breakpoints`, stb.).
- Gombok / Menü: 💾 Mentés, 📂 Állapotkezelő, ↩️ Undo, ↪️ Redo (Állapot menü és bal oldali vezérlőpult).

### StateManagerDialog
- Lista: összes mentés időrendben
- Mentés most, Visszatöltés, Undo, Redo, Export
- Info: history count, index, perf stats

## Jövőbeli fejlesztések
- [ ] Auto-save beállítás
- [ ] Cloud sync
- [ ] Diff két állapot között
- [ ] Time-travel debugging
- [ ] Plugin hot-reload
