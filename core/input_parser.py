# -*- coding: utf-8 -*-
"""
Input Parser - Kézi tömb és paraméter bemenetek értelmezése
"""
import re
from typing import List, Optional, Tuple, Dict


PRESETS: Dict[str, List[int]] = {
    "Majdnem rendezett": [1, 2, 3, 5, 4, 6, 7, 8, 9, 10],
    "Fordított": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    "Sok ismétlés": [5, 2, 5, 8, 2, 5, 8, 2, 5, 2],
    "Kevesebb elem (5)": [5, 3, 8, 1, 9],
    "Több elem (15)": [12, 5, 18, 1, 9, 15, 3, 7, 20, 2, 11, 6, 14, 4, 8],
}


def parse_array_input(raw: str, max_items: int = 50) -> Tuple[Optional[List[int]], Optional[str]]:
    """
    Értelmezi a felhasználó által megadott sztringet tömbbé.
    Támogatott formátumok:
    - "5, 3, 8, 1, 9"
    - "[5, 3, 8, 1, 9]"
    - "5 3 8 1 9"
    - "5; 3; 8; 1; 9"

    Visszatérési érték: (array_or_none, error_message_or_none)
    """
    if raw is None or not str(raw).strip():
        return None, "A bemeneti mező nem lehet üres!"

    cleaned = str(raw).strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1].strip()

    if not cleaned:
        return None, "A tömb nem tartalmaz elemeket!"

    tokens = [t for t in re.split(r'[,;\s]+', cleaned) if t]

    if not tokens:
        return None, "Nem találhatók elemek a bemenetben!"

    if len(tokens) > max_items:
        return None, f"Túl sok elem! A maximálisan megengedett elemszám: {max_items}."

    result = []
    for t in tokens:
        try:
            val = int(t)
            result.append(val)
        except ValueError:
            return None, f"Érvénytelen szám: '{t}'. Csak egész számok adhatók meg!"

    return result, None
