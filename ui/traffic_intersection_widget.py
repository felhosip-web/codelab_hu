# -*- coding: utf-8 -*-
"""
TrafficIntersectionViewerWidget - Dedikált grafikus kereszteződés vizualizáció
CodeLab HU oktatási felületéhez (Phase 2 - Jármű forgalmi kereszteződés).
Négyirányú út, Észak-Dél és Kelet-Nyugat forgalmi sávok, járművek, stopvonalak,
koordinált jelzőlámpák és elsőbbségi infópanel.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPolygonF


class IntersectionCanvasWidget(QWidget):
    """
    Egyedi QPainter vászon a négyirányú útkereszteződés és járművek megjelenítéséhez.
    Tisztán az átadott állapotadatokból rajzol, háttérszálak és önálló időzítők nélkül.
    """
    def __init__(self, parent=None):
        """Inicializálja a vászon widgetet alapértelmezett állapotokkal."""
        super().__init__(parent)
        self.setMinimumSize(400, 360)
        self.lights: Dict[str, Dict[str, bool]] = {
            "ns": {"red": True, "yellow": False, "green": False},
            "ew": {"red": True, "yellow": False, "green": False},
        }
        self.vehicles: Dict[str, List[Dict[str, Any]]] = {
            "north": [], "south": [], "east": [], "west": []
        }
        self.right_of_way = "NONE"

    def set_simulation_state(self, lights: Dict[str, Dict[str, bool]], vehicles: Dict[str, List[Dict[str, Any]]], right_of_way: str):
        """Beállítja az aktuális vizuális állapotot és újrarajzolást kér."""
        self.lights = lights or {}
        self.vehicles = vehicles or {}
        self.right_of_way = right_of_way or "NONE"
        self.update()

    def paintEvent(self, event):
        """Kirajzolja a teljes kereszteződést, lámpákat és járműveket."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        # 1. Háttér (Zöld fű / környezet)
        painter.fillRect(0, 0, w, h, QColor("#1e272e"))

        road_width = min(w, h) * 0.38
        rw2 = road_width / 2.0

        # 2. Utak aszfaltja (Függőleges Észak-Dél és Vízszintes Kelet-Nyugat út)
        road_brush = QBrush(QColor("#2f3640"))
        painter.setPen(Qt.NoPen)
        # É-D út
        painter.fillRect(int(cx - rw2), 0, int(road_width), h, road_brush)
        # K-Ny út
        painter.fillRect(0, int(cy - rw2), w, int(road_width), road_brush)

        # Útszegélyek (Border lines)
        curb_pen = QPen(QColor("#718093"), 2)
        painter.setPen(curb_pen)
        # É-Ny sarok
        painter.drawLine(0, int(cy - rw2), int(cx - rw2), int(cy - rw2))
        painter.drawLine(int(cx - rw2), 0, int(cx - rw2), int(cy - rw2))
        # É-K sarok
        painter.drawLine(int(cx + rw2), 0, int(cx + rw2), int(cy - rw2))
        painter.drawLine(int(cx + rw2), int(cy - rw2), w, int(cy - rw2))
        # D-Ny sarok
        painter.drawLine(0, int(cy + rw2), int(cx - rw2), int(cy + rw2))
        painter.drawLine(int(cx - rw2), int(cy + rw2), int(cx - rw2), h)
        # D-K sarok
        painter.drawLine(int(cx + rw2), int(cy + rw2), w, int(cy + rw2))
        painter.drawLine(int(cx + rw2), int(cy + rw2), int(cx + rw2), h)

        # 3. Stopvonalak (Fehér vastag vonal a behajtás előtt)
        stop_pen = QPen(QColor("#f5f6fa"), 4)
        painter.setPen(stop_pen)
        # Északról érkező sáv (jobb oldali sáv: cx .. cx + rw2)
        painter.drawLine(int(cx), int(cy - rw2), int(cx + rw2), int(cy - rw2))
        # Délről érkező sáv (jobb oldali sáv: cx - rw2 .. cx)
        painter.drawLine(int(cx - rw2), int(cy + rw2), int(cx), int(cy + rw2))
        # Nyugatról érkező sáv (felső/jobb oldali sáv: cy .. cy + rw2)
        painter.drawLine(int(cx - rw2), int(cy), int(cx - rw2), int(cy + rw2))
        # Keletről érkező sáv (bal/jobb oldali sáv: cy - rw2 .. cy)
        painter.drawLine(int(cx + rw2), int(cy - rw2), int(cx + rw2), int(cy))

        # Felező szaggatott vonalak (Sárga)
        lane_pen = QPen(QColor("#fbc531"), 2, Qt.DashLine)
        painter.setPen(lane_pen)
        # Észak
        painter.drawLine(int(cx), 0, int(cx), int(cy - rw2))
        # Dél
        painter.drawLine(int(cx), int(cy + rw2), int(cx), h)
        # Nyugat
        painter.drawLine(0, int(cy), int(cx - rw2), int(cy))
        # Kelet
        painter.drawLine(int(cx + rw2), int(cy), w, int(cy))

        # 4. Kis jelzőlámpák a kereszteződés sarkain
        self._draw_mini_signal(painter, cx + rw2 + 10, cy - rw2 - 40, self.lights.get("ns", {}), "É-D")
        self._draw_mini_signal(painter, cx - rw2 - 45, cy + rw2 + 10, self.lights.get("ns", {}), "É-D")
        self._draw_mini_signal(painter, cx - rw2 - 45, cy - rw2 - 40, self.lights.get("ew", {}), "K-NY")
        self._draw_mini_signal(painter, cx + rw2 + 10, cy + rw2 + 10, self.lights.get("ew", {}), "K-NY")

        # 5. Járművek kirajzolása
        self._draw_vehicles(painter, cx, cy, rw2)

    def _draw_mini_signal(self, painter: QPainter, x: float, y: float, lamps: Dict[str, bool], label: str):
        """Kompakt 3-lámpás jelzőlámpa doboz kirajzolása a sarokra."""
        box_w, box_h = 32, 60
        painter.setPen(QPen(QColor("#111417"), 2))
        painter.setBrush(QBrush(QColor("#181c20")))
        painter.drawRoundedRect(int(x), int(y), box_w, box_h, 4, 4)

        r_active = lamps.get("red", False)
        y_active = lamps.get("yellow", False)
        g_active = lamps.get("green", False)

        lamp_d = 12
        lx = int(x + (box_w - lamp_d) / 2)
        # Piros
        painter.setBrush(QBrush(QColor("#ff3838") if r_active else QColor("#401010")))
        painter.drawEllipse(lx, int(y + 4), lamp_d, lamp_d)
        # Sárga
        painter.setBrush(QBrush(QColor("#ffbe12") if y_active else QColor("#453805")))
        painter.drawEllipse(lx, int(y + 22), lamp_d, lamp_d)
        # Zöld
        painter.setBrush(QBrush(QColor("#2ed573") if g_active else QColor("#083818")))
        painter.drawEllipse(lx, int(y + 40), lamp_d, lamp_d)

    def _draw_vehicles(self, painter: QPainter, cx: float, cy: float, rw2: float):
        """Kirajzolja az összes közeledő, várakozó és áthaladó járművet."""
        # Fit the maximum six-car queue on even the minimum canvas size.
        approach = min(cx, cy) - rw2
        gap = 3.0
        car_len = min(rw2 * 0.65, (approach - 8 - 5 * gap - 1) / 6)
        car_w = min(rw2 * 0.40, car_len * 0.65)

        # Színek irányonként
        colors = {
            "north": QColor("#00a8ff"),  # Kék
            "south": QColor("#9c88ff"),  # Lila
            "east": QColor("#e84118"),   # Pirosas narancs
            "west": QColor("#fbc531"),   # Sárga
        }

        # Északi járművek (Dél felé tartanak a jobb oldali sávban: x = cx + rw2/2)
        ns_lane_x_southbound = cx + rw2 / 2.0
        for v in self.vehicles.get("north", []):
            if v["status"] == "departed":
                continue
            color = colors["north"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vy = (cy - rw2) + prog * (rw2 * 1.0)
            else:
                q = v.get("queue_pos", 0)
                vy = (cy - rw2) - car_len - 8 - q * (car_len + gap)
            self._draw_car_rect(painter, ns_lane_x_southbound - car_w / 2.0, vy, car_w, car_len, color, v["id"])

        # Déli járművek (Észak felé tartanak: x = cx - rw2/2)
        ns_lane_x_northbound = cx - rw2 / 2.0
        for v in self.vehicles.get("south", []):
            if v["status"] == "departed":
                continue
            color = colors["south"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vy = (cy + rw2) - prog * rw2 - (prog - 1) * car_len
            else:
                q = v.get("queue_pos", 0)
                vy = (cy + rw2) + 8 + q * (car_len + gap)
            self._draw_car_rect(painter, ns_lane_x_northbound - car_w / 2.0, vy, car_w, car_len, color, v["id"])

        # Keleti járművek (Nyugat felé tartanak: y = cy - rw2/2)
        ew_lane_y_westbound = cy - rw2 / 2.0
        for v in self.vehicles.get("east", []):
            if v["status"] == "departed":
                continue
            color = colors["east"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vx = (cx + rw2) - prog * rw2 - (prog - 1) * car_len
            else:
                q = v.get("queue_pos", 0)
                vx = (cx + rw2) + 8 + q * (car_len + gap)
            self._draw_car_rect(painter, vx, ew_lane_y_westbound - car_w / 2.0, car_len, car_w, color, v["id"])

        # Nyugati járművek (Kelet felé tartanak: y = cy + rw2/2)
        ew_lane_y_eastbound = cy + rw2 / 2.0
        for v in self.vehicles.get("west", []):
            if v["status"] == "departed":
                continue
            color = colors["west"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vx = (cx - rw2) + prog * (rw2 * 1.0)
            else:
                q = v.get("queue_pos", 0)
                vx = (cx - rw2) - car_len - 8 - q * (car_len + gap)
            self._draw_car_rect(painter, vx, ew_lane_y_eastbound - car_w / 2.0, car_len, car_w, color, v["id"])

    def _draw_car_rect(self, painter: QPainter, x: float, y: float, w: float, h: float, color: QColor, text: str):
        """Kirajzol egy lekerekített téglalap autót azonosító felirattal."""
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(int(x), int(y), int(w), int(h), 5, 5)

        painter.setBrush(QBrush(QColor("#2f3640")))
        painter.setPen(Qt.NoPen)
        cw, ch = max(4, int(w * 0.6)), max(4, int(h * 0.4))
        cx = int(x + (w - cw) / 2)
        cy = int(y + (h - ch) / 2)
        painter.drawRoundedRect(cx, cy, cw, ch, 2, 2)

        painter.setPen(QColor("#ffffff"))
        font = QFont("sans-serif", 8, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(x, y, w, h), Qt.AlignCenter, text)


class TrafficIntersectionViewerWidget(QFrame):
    """
    Dedikált, interaktív négyirányú forgalmi kereszteződés vizualizáció.
    Minden állapotát tisztán a VisualizationStep-ből frissíti (nincs független belső timer).
    """
    def __init__(self, parent=None):
        """Inicializálja a kereszteződés vizualizációs widgetet és paneleket."""
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("""
            TrafficIntersectionViewerWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f3640, stop:1 #1e272e);
                border: 2px solid #718093;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Címsor
        self.title_label = QLabel("🚦 Négyirányú Járműforgalmi Kereszteződés Szimuláció (Phase 2)")
        self.title_label.setStyleSheet(
            "background: #192a56; color: white; padding: 6px; font-weight: bold; border-radius: 6px; font-size: 13px;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # 1. Grafikus Vászon (Intersection canvas)
        self.canvas = IntersectionCanvasWidget(self)
        content_layout.addWidget(self.canvas, stretch=2)

        # 2. Információs Műszerfal Panel
        info_panel = QFrame()
        info_panel.setStyleSheet("""
            QFrame {
                background: #23272a;
                border: 2px solid #353b48;
                border-radius: 10px;
                padding: 8px;
            }
            QLabel {
                color: #f5f6fa;
                font-family: sans-serif;
            }
        """)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(6)
        info_layout.setAlignment(Qt.AlignTop)

        # Elsőbbségi irány jelvény
        row_header = QLabel("ELSŐBBSÉG / SZABAD ÚT:")
        row_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px;")
        info_layout.addWidget(row_header)

        self.right_of_way_badge = QLabel("INICIALIZÁLÁS")
        self.right_of_way_badge.setStyleSheet("""
            background-color: #353b48;
            color: #dcdde1;
            font-weight: bold;
            font-size: 13px;
            padding: 5px 8px;
            border-radius: 6px;
        """)
        self.right_of_way_badge.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.right_of_way_badge)

        # Észak-Dél és Kelet-Nyugat lámpa állapotjelzők
        lights_header = QLabel("JELZŐLÁMPA ÁLLAPOTOK:")
        lights_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(lights_header)

        self.ns_light_status = QLabel("Észak-Dél: PIROS ⛔")
        self.ns_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        info_layout.addWidget(self.ns_light_status)

        self.ew_light_status = QLabel("Kelet-Nyugat: PIROS ⛔")
        self.ew_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        info_layout.addWidget(self.ew_light_status)

        # Várakozó és áthaladt járművek számlálója
        queue_header = QLabel("FORGALMI METRIKÁK:")
        queue_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(queue_header)

        self.queue_info_label = QLabel("Várakozik: É-D: 0 | K-Ny: 0")
        self.queue_info_label.setStyleSheet("color: #f5f6fa; font-size: 11px;")
        info_layout.addWidget(self.queue_info_label)

        self.passed_info_label = QLabel("Áthaladt járművek: 0 db")
        self.passed_info_label.setStyleSheet("color: #2ed573; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.passed_info_label)

        # Hátralévő idő és Ciklus
        time_header = QLabel("HÁTRALÉVŐ FÁZISIDŐ:")
        time_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(time_header)

        self.countdown_label = QLabel("0 mp")
        self.countdown_label.setStyleSheet("""
            background-color: #2f3640;
            color: #00d2d3;
            font-weight: bold;
            font-size: 18px;
            font-family: monospace;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #00a8ff;
        """)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.countdown_label)

        self.cycle_info_label = QLabel("Ciklus: 0 / 0")
        self.cycle_info_label.setStyleSheet("color: #f5f6fa; font-size: 11px; font-weight: bold;")
        info_layout.addWidget(self.cycle_info_label)

        content_layout.addWidget(info_panel, stretch=1)
        main_layout.addLayout(content_layout)

        # Alsó állapotcsík
        self.status_detail = QLabel("Kereszteződés szimuláció készen áll az indításra.")
        self.status_detail.setStyleSheet("""
            background: #182C61;
            color: #EAB543;
            padding: 6px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_detail.setAlignment(Qt.AlignCenter)
        self.status_detail.setWordWrap(True)
        main_layout.addWidget(self.status_detail)

    def update_state(self, step):
        """
        Frissíti a kereszteződés állapotát a kapott VisualizationStep adataiból.
        Tisztán a lépésből olvas, nem használ belső timert.
        """
        extra = getattr(step, 'extra', {}) or {}
        lights = extra.get("lights") or {}
        vehicles = extra.get("vehicles") or {}
        row = extra.get("right_of_way", "NONE")
        row_hu = extra.get("right_of_way_hu", row)

        self.canvas.set_simulation_state(lights, vehicles, row)

        self.right_of_way_badge.setText(str(row_hu).upper())
        if "Észak-Dél" in str(row_hu) or row == "NORTH_SOUTH":
            self.right_of_way_badge.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 12px; padding: 5px 8px; border-radius: 6px;")
        elif "Kelet-Nyugat" in str(row_hu) or row == "EAST_WEST":
            self.right_of_way_badge.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; font-size: 12px; padding: 5px 8px; border-radius: 6px;")
        elif "kiürítés" in str(row_hu).lower() or "piros" in str(row_hu).lower():
            self.right_of_way_badge.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 12px; padding: 5px 8px; border-radius: 6px;")
        else:
            self.right_of_way_badge.setStyleSheet("background-color: #353b48; color: #dcdde1; font-weight: bold; font-size: 12px; padding: 5px 8px; border-radius: 6px;")

        ns_l = lights.get("ns", {})
        ew_l = lights.get("ew", {})

        def get_lamp_str(lamps):
            if lamps.get("green"):
                return "ZÖLD 🟢", "#2ed573"
            elif lamps.get("yellow"):
                return "SÁRGA 🟡", "#fbc531"
            elif lamps.get("red"):
                return "PIROS ⛔", "#ff6b6b"
            return "KIKAPCSOLVA ⚫", "#718093"

        ns_str, ns_col = get_lamp_str(ns_l)
        ew_str, ew_col = get_lamp_str(ew_l)
        self.ns_light_status.setText(f"Észak-Dél: {ns_str}")
        self.ns_light_status.setStyleSheet(f"color: {ns_col}; font-weight: bold; font-size: 12px;")
        self.ew_light_status.setText(f"Kelet-Nyugat: {ew_str}")
        self.ew_light_status.setStyleSheet(f"color: {ew_col}; font-weight: bold; font-size: 12px;")

        arr = getattr(step, 'array', None) or []
        w_ns = arr[0] if len(arr) > 0 else 0
        w_ew = arr[1] if len(arr) > 1 else 0
        passed = arr[2] if len(arr) > 2 else 0
        self.queue_info_label.setText(f"Várakozik: É-D: {w_ns} | K-Ny: {w_ew}")
        self.passed_info_label.setText(f"Áthaladt járművek: {passed} db")

        rem_time = extra.get("remaining_time", 0)
        self.countdown_label.setText(f"{rem_time} mp" if rem_time > 0 else "-")
        cycle = extra.get("cycle", 0)
        total_cycles = extra.get("total_cycles", 0)
        self.cycle_info_label.setText(f"Ciklus: {cycle} / {total_cycles}")

        self.status_detail.setText(getattr(step, 'explanation', ''))
