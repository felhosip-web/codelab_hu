# -*- coding: utf-8 -*-
"""
TrafficLightViewerWidget - Dedikált grafikus jelzőlámpa vizualizáció
CodeLab HU oktatási felületéhez
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen


class LampWidget(QWidget):
    """Egyedi kirajzolt lámpa kör alakú optikával és aktív/inaktív kontraszttal"""
    def __init__(self, color_name: str, active_color: str, inactive_color: str, diameter: int = 56):
        """Inicializálja a lámpa grafikus elemet a megadott színekkel és mérettel."""
        super().__init__()
        self.color_name = color_name
        self.active_color = QColor(active_color)
        self.inactive_color = QColor(inactive_color)
        self.diameter = diameter
        self.is_active = False
        self.setFixedSize(diameter + 16, diameter + 16)

    def set_active(self, active: bool):
        """Beállítja a lámpa aktív/inaktív állapotát és újrarajzolja, ha változott."""
        if self.is_active != active:
            self.is_active = active
            self.update()

    def paintEvent(self, event):
        """Kirajzolja a lámpatestet, lencsét és az optikai fényhatást."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        r = self.diameter / 2.0
        center_x = w / 2.0
        center_y = h / 2.0

        # Külső fekete keret / visor hatás
        painter.setPen(QPen(QColor("#111417"), 3))
        painter.setBrush(QBrush(QColor("#1e272e")))
        painter.drawEllipse(int(center_x - r - 4), int(center_y - r - 4), int(self.diameter + 8), int(self.diameter + 8))

        # Belső optika szín (aktív fény vs sötét kikapcsolt lencse)
        fill_color = self.active_color if self.is_active else self.inactive_color
        border_color = QColor("#ffffff") if self.is_active else QColor("#2d3436")
        painter.setPen(QPen(border_color, 2 if self.is_active else 1))
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(int(center_x - r), int(center_y - r), int(self.diameter), int(self.diameter))

        # Ha aktív, finom fényglória / csillogás
        if self.is_active:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
            painter.drawEllipse(int(center_x - r * 0.4), int(center_y - r * 0.6), int(r * 0.6), int(r * 0.4))


class TrafficLightViewerWidget(QFrame):
    """
    Dedikált, interaktív jelzőlámpa ház 3 lámpával, állapot- és visszaszámláló kijelzővel.
    Minden állapotát tisztán a VisualizationStep-ből frissíti (nincs független belső timer).
    """
    def __init__(self, parent=None):
        """Inicializálja a jelzőlámpa vizualizációs widgetet, a lámpatestet és az információs panelt."""
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("""
            TrafficLightViewerWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f3640, stop:1 #1e272e);
                border: 2px solid #718093;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        # Címsor
        self.title_label = QLabel("🚦 Forgalomirányító Jelzőlámpa Szimuláció (Phase 1)")
        self.title_label.setStyleSheet(
            "background: #273c75; color: white; padding: 6px; font-weight: bold; border-radius: 6px; font-size: 13px;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Középső vízszintes panel: Lámpatest (Housing) és Infó panel
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(25)

        # Lámpatest (Dark metal housing)
        self.housing = QFrame()
        self.housing.setStyleSheet("""
            QFrame {
                background-color: #111417;
                border: 4px solid #2f3640;
                border-radius: 20px;
                padding: 10px;
            }
        """)
        housing_layout = QVBoxLayout(self.housing)
        housing_layout.setAlignment(Qt.AlignCenter)
        housing_layout.setSpacing(8)

        # 3 lámpa (Piros, Sárga, Zöld)
        self.lamp_red = LampWidget(
            color_name="red",
            active_color="#ff3838",
            inactive_color="#401010",
            diameter=54
        )
        self.lamp_yellow = LampWidget(
            color_name="yellow",
            active_color="#ffbe12",
            inactive_color="#453805",
            diameter=54
        )
        self.lamp_green = LampWidget(
            color_name="green",
            active_color="#2ed573",
            inactive_color="#083818",
            diameter=54
        )

        housing_layout.addWidget(self.lamp_red)
        housing_layout.addWidget(self.lamp_yellow)
        housing_layout.addWidget(self.lamp_green)

        content_layout.addWidget(self.housing)

        # Infó & Műszerfal panel
        info_panel = QFrame()
        info_panel.setStyleSheet("""
            QFrame {
                background: #23272a;
                border: 2px solid #353b48;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #f5f6fa;
                font-family: sans-serif;
            }
        """)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(8)
        info_layout.setAlignment(Qt.AlignVCenter)

        # Állapot jelvény
        state_header = QLabel("AKTUÁLIS ÁLLAPOT:")
        state_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(state_header)

        self.state_badge = QLabel("INICIALIZÁLÁS")
        self.state_badge.setStyleSheet("""
            background-color: #353b48;
            color: #dcdde1;
            font-weight: bold;
            font-size: 15px;
            padding: 6px 12px;
            border-radius: 6px;
        """)
        self.state_badge.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.state_badge)

        # Hátralévő idő kijelző
        time_header = QLabel("HÁTRALÉVŐ IDŐ:")
        time_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(time_header)

        self.countdown_label = QLabel("0 mp")
        self.countdown_label.setStyleSheet("""
            background-color: #2f3640;
            color: #00d2d3;
            font-weight: bold;
            font-size: 20px;
            font-family: monospace;
            padding: 6px 14px;
            border-radius: 6px;
            border: 1px solid #00a8ff;
        """)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.countdown_label)

        # Ciklus és fázis információk
        self.cycle_info_label = QLabel("Ciklus: 0 / 0")
        self.cycle_info_label.setStyleSheet("color: #f5f6fa; font-size: 12px; font-weight: bold;")
        info_layout.addWidget(self.cycle_info_label)

        self.next_state_label = QLabel("Következő fázis: -")
        self.next_state_label.setStyleSheet("color: #dcdde1; font-size: 11px;")
        info_layout.addWidget(self.next_state_label)

        content_layout.addWidget(info_panel)
        main_layout.addLayout(content_layout)

        # Alsó részletes leíró állapotcsík
        self.status_detail = QLabel("Készen áll az indításra.")
        self.status_detail.setStyleSheet("""
            background: #182C61;
            color: #EAB543;
            padding: 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_detail.setAlignment(Qt.AlignCenter)
        self.status_detail.setWordWrap(True)
        main_layout.addWidget(self.status_detail)

    def update_state(self, step):
        """
        Frissíti a lámpatest állapotát a kapott VisualizationStep adataiból.
        Tisztán a lépésből olvas, nem használ háttérbeli időzítőt vagy sleepet.
        """
        extra = getattr(step, 'extra', {}) or {}
        lamps = extra.get("lamps", {})
        red_active = bool(lamps.get("red", False))
        yellow_active = bool(lamps.get("yellow", False))
        green_active = bool(lamps.get("green", False))

        self.lamp_red.set_active(red_active)
        self.lamp_yellow.set_active(yellow_active)
        self.lamp_green.set_active(green_active)

        state_hu = extra.get("state_hu", extra.get("state", "KÉSZÜLTSÉG"))
        self.state_badge.setText(str(state_hu).upper())

        # Állapotjelvény stílusa a szignál szerint
        if red_active and yellow_active:
            self.state_badge.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 6px;")
        elif red_active:
            self.state_badge.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 6px;")
        elif green_active:
            self.state_badge.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 6px;")
        elif yellow_active:
            self.state_badge.setStyleSheet("background-color: #f39c12; color: black; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 6px;")
        else:
            self.state_badge.setStyleSheet("background-color: #353b48; color: #dcdde1; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 6px;")

        rem_time = extra.get("remaining_time", 0)
        self.countdown_label.setText(f"{rem_time} mp" if rem_time > 0 else "-")

        cycle = extra.get("cycle", 0)
        total_cycles = extra.get("total_cycles", 0)
        self.cycle_info_label.setText(f"Ciklus: {cycle} / {total_cycles}")

        next_st = extra.get("next_state")
        if next_st:
            self.next_state_label.setText(f"Következő fázis: {next_st}")
        else:
            self.next_state_label.setText("Következő fázis: Ciklus vége")

        self.status_detail.setText(getattr(step, 'explanation', ''))
