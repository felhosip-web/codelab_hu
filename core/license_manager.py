# -*- coding: utf-8 -*-
"""
Licenc kezelés - GNU GPL v3 (Hes Projects ® by FePe)
"""
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json

@dataclass
class LicenseInfo:
    name: str = "Hes Projects ® by FePe - CodeLab HU"
    short_name: str = "CodeLab HU"
    version: str = "3.0.0"
    license_type: str = "GNU GPL v3"
    copyright: str = "Copyright (C) 2024-2026 Péter Felhősi (FePe) / Hes Projects ® by FePe"
    author: str = "Péter Felhősi (FePe)"
    company: str = "Hes Projects ® by FePe"
    trademark: str = "Hes Projects ® by FePe and CodeLab HU branding"
    license_file: str = "LICENSE"
    gpl_url: str = "https://www.gnu.org/licenses/gpl-3.0.txt"
    contact: str = "Hes Projects ® by FePe - GitHub"
    year: str = "2024-2026"
    
    attribution_required: str = "Hes Projects ® by FePe - CodeLab HU - Copyright (C) 2024-2026 Péter Felhősi"
    powered_by: str = "Powered by Hes Projects ® by FePe"

class LicenseManager:
    def __init__(self, license_path="LICENSE"):
        self.license_path = Path(license_path)
        self.info = LicenseInfo()
        self.checked = False
        self.valid = True
    
    def get_license_text(self) -> str:
        if self.license_path.exists():
            return self.license_path.read_text(encoding='utf-8')
        return "LICENSE nem található - Hes Projects ® by FePe GNU GPL v3"
    
    def get_short_license(self) -> str:
        return f"""{self.info.name} v{self.info.version}
{self.info.copyright}
{self.info.license_type}

This program is free software under GNU GPL v3.
Attribution required: {self.info.attribution_required}

Contact: {self.info.contact}
"""
    
    def get_header(self) -> str:
        return f"""# {self.info.name} v{self.info.version}
# {self.info.copyright}
# {self.info.license_type} - {self.info.trademark}
# License: {self.info.license_file} - {self.info.gpl_url}
"""
    
    def check_license(self) -> bool:
        # Egyszerű ellenőrzés: van-e LICENSE.txt
        self.checked = True
        self.valid = self.license_path.exists()
        return self.valid
    
    def export_license_info(self, path="saves/license_info.json"):
        p = Path(path)
        p.parent.mkdir(exist_ok=True)
        data = {
            "info": self.info.__dict__,
            "checked_at": datetime.now().isoformat(),
            "valid": self.valid,
            "license_text_preview": self.get_license_text()[:500]
        }
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return p
    
    def validate_attribution(self, text: str) -> bool:
        # Ellenőrzi hogy szerepel-e az attribution
        required = ["Hes Projects", "FePe", "Péter Felhősi"]
        return any(r in text for r in required)
