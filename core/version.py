
from dataclasses import dataclass

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

MAIN_VERSION = Version(3, 4, 0)
MAIN_CODENAME = "Program Szerkezet"
API_VERSION = Version(1, 0, 0)
class
class Version:
    major: int
    minor: int
    patch: int
    suffix: str = ""  # pl "-beta", "-rc1"
    
    def __str__(self):
        base = f"{self.major}.{self.minor}.{self.patch}"
        return base + self.suffix if self.suffix else base
    
    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    @classmethod
    def parse(cls, s: str):
        # "1.2.3" vagy "1.2.3-beta"
        suffix = ""
        if "-" in s:
            s, suffix = s.split("-", 1)
            suffix = "-" + suffix
        parts = s.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts)>2 else 0, suffix)

# === FŐ PROGRAM VERZIÓ ===
MAIN_VERSION = Version(1, 0, 0)  # 1.0.0 - első stabil plugin rendszerű kiadás
MAIN_CODENAME = "Buborék-bázis"

# === PLUGIN API VERZIÓ ===
# Ezt növeljük ha a PluginBase interfész változik (breaking change -> major)
PLUGIN_API_VERSION = Version(1, 0, 0)
PLUGIN_API_HISTORY = {
    "1.0.0": "Alap plugin rendszer: get_steps(), get_code(), id, name, icon, codes, time/space"
}

def check_plugin_compatibility(plugin_api_required: str) -> Tuple[bool, str]:
    """Ellenőrzi hogy a plugin kompatibilis-e a jelenlegi API-val"""
    try:
        required = Version.parse(plugin_api_required)
        current = PLUGIN_API_VERSION
        # Major verziónak egyeznie kell, minor-nak >= kell lennie
        if required.major != current.major:
            return False, f"API major mismatch: plugin {required.major}.x kell, de {current.major}.x van"
        if required > current:
            return False, f"Plugin újabb API-t igényel: {required} > {current}"
        return True, "Kompatibilis"
    except Exception as e:
        return False, f"Verzió parse hiba: {e}"

def get_version_string():
    return f"{MAIN_VERSION} ({MAIN_CODENAME}) | Plugin API {PLUGIN_API_VERSION}"
