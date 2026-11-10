# -*- coding: utf-8 -*-
"""
TrafficPedestrianIntersectionViewerWidget - Dedikált grafikus kereszteződés és
gyalogosforgalom vizualizáció a CodeLab HU oktatási felületéhez (Phase 3).
Négyirányú út, Észak-Dél és Kelet-Nyugat sávok, járművek, stopvonalak,
4 gyalogos zebra átkelő, 2-állású gyalogos jelzőlámpák, interaktív hívógombok,
kérelemjelzők, várakozó és átkelő gyalogosok, valamint valós idejű oktatási műszerfal.
"""
from typing import Dict, Any, List, Optional, Callable
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QGridLayout
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QCursor


class PedestrianIntersectionCanvasWidget(QWidget):
    """
    Egyedi QPainter vászon a négyirányú útkereszteződés, járművek, gyalogosátkelők,
    gyalogoslámpák és gyalogosok megjelenítéséhez.
    Interaktív: a vásznon elhelyezett hívógombokra kattintva is kérelem regisztrálható!
    """
    crossing_requested = Signal(str)

    def __init__(self, parent=None):
        """Inicializálja a vászon widgetet alapértelmezett állapotokkal."""
        super().__init__(parent)
        self.setMinimumSize(420, 380)
        self.setMouseTracking(True)
        self.vehicle_lights: Dict[str, Dict[str, bool]] = {
            "ns": {"red": True, "yellow": False, "green": False},
            "ew": {"red": True, "yellow": False, "green": False},
        }
        self.pedestrian_lights: Dict[str, Dict[str, bool]] = {
            c: {"red": True, "green": False} for c in ["north", "south", "east", "west"]
        }
        self.pedestrian_requests: Dict[str, bool] = {
            c: False for c in ["north", "south", "east", "west"]
        }
        self.vehicles: Dict[str, List[Dict[str, Any]]] = {
            "north": [], "south": [], "east": [], "west": []
        }
        self.pedestrians: Dict[str, List[Dict[str, Any]]] = {
            "north": [], "south": [], "east": [], "west": []
        }
        self.right_of_way = "NONE"
        self._button_rects: Dict[str, QRectF] = {}

    def set_simulation_state(
        self,
        vehicle_lights: Dict[str, Dict[str, bool]],
        pedestrian_lights: Dict[str, Dict[str, bool]],
        pedestrian_requests: Dict[str, bool],
        vehicles: Dict[str, List[Dict[str, Any]]],
        pedestrians: Dict[str, List[Dict[str, Any]]],
        right_of_way: str
    ):
        """Beállítja az aktuális szimulációs állapotot és frissíti a vásznat."""
        self.vehicle_lights = vehicle_lights or {}
        self.pedestrian_lights = pedestrian_lights or {}
        self.pedestrian_requests = pedestrian_requests or {}
        self.vehicles = vehicles or {}
        self.pedestrians = pedestrians or {}
        self.right_of_way = right_of_way or "NONE"
        self.update()

    def mousePressEvent(self, event):
        """Kattintás kezelése a vásznon: ha a hívógombok valamelyikére kattintanak, kérést bocsát ki."""
        pos = event.position() if hasattr(event, "position") else event.pos()
        for crossing, rect in self._button_rects.items():
            if rect.contains(pos):
                self.crossing_requested.emit(crossing)
                break
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Egérmozgás: ha a hívógombok felett van az egérmutató, mutató kéz kurzor jelenik meg."""
        pos = event.position() if hasattr(event, "position") else event.pos()
        over_button = any(rect.contains(pos) for rect in self._button_rects.values())
        if over_button:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        """Kirajzolja a teljes kereszteződést, zebrákat, lámpákat, járműveket és gyalogosokat."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        # 1. Háttér / fű
        painter.fillRect(0, 0, w, h, QColor("#1e272e"))

        road_width = min(w, h) * 0.38
        rw2 = road_width / 2.0

        # 2. Aszfalt utak
        road_brush = QBrush(QColor("#2f3640"))
        painter.setPen(Qt.NoPen)
        painter.fillRect(int(cx - rw2), 0, int(road_width), h, road_brush)
        painter.fillRect(0, int(cy - rw2), w, int(road_width), road_brush)

        # Útszegélyek
        curb_pen = QPen(QColor("#718093"), 2)
        painter.setPen(curb_pen)
        painter.drawLine(0, int(cy - rw2), int(cx - rw2), int(cy - rw2))
        painter.drawLine(int(cx - rw2), 0, int(cx - rw2), int(cy - rw2))
        painter.drawLine(int(cx + rw2), 0, int(cx + rw2), int(cy - rw2))
        painter.drawLine(int(cx + rw2), int(cy - rw2), w, int(cy - rw2))
        painter.drawLine(0, int(cy + rw2), int(cx - rw2), int(cy + rw2))
        painter.drawLine(int(cx - rw2), int(cy + rw2), int(cx - rw2), h)
        painter.drawLine(int(cx + rw2), int(cy + rw2), w, int(cy + rw2))
        painter.drawLine(int(cx + rw2), int(cy + rw2), int(cx + rw2), h)

        # 3. Gyalogosátkelőhelyek (Zebra sávok)
        self._draw_crosswalks(painter, cx, cy, rw2)

        # 4. Stopvonalak
        stop_pen = QPen(QColor("#f5f6fa"), 3)
        painter.setPen(stop_pen)
        stop_offset = 24.0
        painter.drawLine(int(cx), int(cy - rw2 - stop_offset), int(cx + rw2), int(cy - rw2 - stop_offset))
        painter.drawLine(int(cx - rw2), int(cy + rw2 + stop_offset), int(cx), int(cy + rw2 + stop_offset))
        painter.drawLine(int(cx - rw2 - stop_offset), int(cy), int(cx - rw2 - stop_offset), int(cy + rw2))
        painter.drawLine(int(cx + rw2 + stop_offset), int(cy - rw2), int(cx + rw2 + stop_offset), int(cy))

        # Felező szaggatott vonalak
        lane_pen = QPen(QColor("#fbc531"), 2, Qt.DashLine)
        painter.setPen(lane_pen)
        painter.drawLine(int(cx), 0, int(cx), int(cy - rw2 - stop_offset))
        painter.drawLine(int(cx), int(cy + rw2 + stop_offset), int(cx), h)
        painter.drawLine(0, int(cy), int(cx - rw2 - stop_offset), int(cy))
        painter.drawLine(int(cx + rw2 + stop_offset), int(cy), w, int(cy))

        # 5. Jármű jelzőlámpák a sarkokon
        ns_lamps = self.vehicle_lights.get("ns", {})
        ew_lamps = self.vehicle_lights.get("ew", {})
        self._draw_vehicle_signal(painter, cx + rw2 + 10, cy - rw2 - 40, ns_lamps, "É-D")
        self._draw_vehicle_signal(painter, cx - rw2 - 42, cy + rw2 + 10, ns_lamps, "É-D")
        self._draw_vehicle_signal(painter, cx - rw2 - 42, cy - rw2 - 40, ew_lamps, "K-NY")
        self._draw_vehicle_signal(painter, cx + rw2 + 10, cy + rw2 + 10, ew_lamps, "K-NY")

        # 6. Gyalogos jelzőlámpák és interaktív hívógombok mind a 4 átkelőnél
        self._draw_pedestrian_signal_and_button(painter, "north", cx - rw2 - 20, cy - rw2 - 14)
        self._draw_pedestrian_signal_and_button(painter, "south", cx + rw2 + 5, cy + rw2 + 6)
        self._draw_pedestrian_signal_and_button(painter, "west", cx - rw2 - 14, cy - rw2 - 20)
        self._draw_pedestrian_signal_and_button(painter, "east", cx + rw2 + 6, cy + rw2 + 5)

        # 7. Járművek kirajzolása
        self._draw_vehicles(painter, cx, cy, rw2, stop_offset)

        # 8. Gyalogosok kirajzolása
        self._draw_pedestrians(painter, cx, cy, rw2)

    def _draw_crosswalks(self, painter: QPainter, cx: float, cy: float, rw2: float):
        """Kirajzolja a 4 zebra átkelőt fehér csíkokkal."""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#f5f6fa")))

        bar_thickness = 4.0
        bar_len = 16.0
        num_bars = 6
        step_x = (rw2 * 2.0) / (num_bars + 1)
        for i in range(1, num_bars + 1):
            bx = cx - rw2 + i * step_x - bar_thickness / 2.0
            painter.fillRect(int(bx), int(cy - rw2 - bar_len - 2), int(bar_thickness), int(bar_len), QBrush(QColor("#f5f6fa")))
            painter.fillRect(int(bx), int(cy + rw2 + 2), int(bar_thickness), int(bar_len), QBrush(QColor("#f5f6fa")))

        num_v_bars = 6
        step_y = (rw2 * 2.0) / (num_v_bars + 1)
        for i in range(1, num_v_bars + 1):
            by = cy - rw2 + i * step_y - bar_thickness / 2.0
            painter.fillRect(int(cx - rw2 - bar_len - 2), int(by), int(bar_len), int(bar_thickness), QBrush(QColor("#f5f6fa")))
            painter.fillRect(int(cx + rw2 + 2), int(by), int(bar_len), int(bar_thickness), QBrush(QColor("#f5f6fa")))

    def _draw_vehicle_signal(self, painter: QPainter, x: float, y: float, lamps: Dict[str, bool], label: str):
        """3-lámpás jármű jelzőlámpa doboz."""
        box_w, box_h = 30, 56
        painter.setPen(QPen(QColor("#111417"), 1.5))
        painter.setBrush(QBrush(QColor("#181c20")))
        painter.drawRoundedRect(int(x), int(y), box_w, box_h, 4, 4)

        r_active = lamps.get("red", False)
        y_active = lamps.get("yellow", False)
        g_active = lamps.get("green", False)

        lamp_d = 10
        lx = int(x + (box_w - lamp_d) / 2)
        painter.setBrush(QBrush(QColor("#ff3838") if r_active else QColor("#401010")))
        painter.drawEllipse(lx, int(y + 4), lamp_d, lamp_d)
        painter.setBrush(QBrush(QColor("#ffbe12") if y_active else QColor("#453805")))
        painter.drawEllipse(lx, int(y + 20), lamp_d, lamp_d)
        painter.setBrush(QBrush(QColor("#2ed573") if g_active else QColor("#083818")))
        painter.drawEllipse(lx, int(y + 36), lamp_d, lamp_d)

    def _draw_pedestrian_signal_and_button(self, painter: QPainter, crossing: str, x: float, y: float):
        """2-lámpás gyalogos lámpa és kattintható hívógomb kérelemjelzővel."""
        p_lamp = self.pedestrian_lights.get(crossing, {})
        is_requested = self.pedestrian_requests.get(crossing, False)

        box_w, box_h = 16, 28
        painter.setPen(QPen(QColor("#111417"), 1))
        painter.setBrush(QBrush(QColor("#181c20")))
        painter.drawRoundedRect(int(x), int(y), box_w, box_h, 3, 3)

        d = 7
        lx = int(x + (box_w - d) / 2)
        p_red = p_lamp.get("red", True)
        painter.setBrush(QBrush(QColor("#ff3838") if p_red else QColor("#3a1010")))
        painter.drawEllipse(lx, int(y + 3), d, d)

        p_green = p_lamp.get("green", False)
        painter.setBrush(QBrush(QColor("#2ed573") if p_green else QColor("#083015")))
        painter.drawEllipse(lx, int(y + 14), d, d)

        # Hívógomb kérelemjelző lámpa (sárga kerek gomb)
        btn_d = 8
        btn_x = int(x + (box_w - btn_d) / 2)
        btn_y = int(y + box_h + 3)

        # Regisztráljuk a kattintható területet nagyobb margóval
        self._button_rects[crossing] = QRectF(btn_x - 4, btn_y - 4, btn_d + 8, btn_d + 8)

        painter.setPen(QPen(QColor("#ffffff") if is_requested else QColor("#57606f"), 1.2))
        painter.setBrush(QBrush(QColor("#fbc531") if is_requested else QColor("#2f3640")))
        painter.drawEllipse(btn_x, btn_y, btn_d, btn_d)

    def _draw_vehicles(self, painter: QPainter, cx: float, cy: float, rw2: float, stop_offset: float):
        """Kirajzolja a járműveket."""
        approach = min(cx, cy) - rw2 - stop_offset
        gap = 3.0
        car_len = min(rw2 * 0.65, max(12.0, (approach - 8 - 5 * gap - 1) / 6.0))
        car_w = min(rw2 * 0.40, car_len * 0.65)

        colors = {
            "north": QColor("#00a8ff"),
            "south": QColor("#9c88ff"),
            "east": QColor("#e84118"),
            "west": QColor("#fbc531"),
        }

        # Északi járművek
        ns_lane_x_sb = cx + rw2 / 2.0
        for v in self.vehicles.get("north", []):
            if v["status"] == "departed":
                continue
            color = colors["north"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vy = (cy - rw2) + prog * (rw2 * 1.0)
            else:
                q = v.get("queue_pos", 0)
                vy = (cy - rw2 - stop_offset) - car_len - 4 - q * (car_len + gap)
            self._draw_car_rect(painter, ns_lane_x_sb - car_w / 2.0, vy, car_w, car_len, color, v["id"])

        # Déli járművek
        ns_lane_x_nb = cx - rw2 / 2.0
        for v in self.vehicles.get("south", []):
            if v["status"] == "departed":
                continue
            color = colors["south"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vy = (cy + rw2) - prog * rw2 - (prog - 1) * car_len
            else:
                q = v.get("queue_pos", 0)
                vy = (cy + rw2 + stop_offset) + 4 + q * (car_len + gap)
            self._draw_car_rect(painter, ns_lane_x_nb - car_w / 2.0, vy, car_w, car_len, color, v["id"])

        # Keleti járművek
        ew_lane_y_wb = cy - rw2 / 2.0
        for v in self.vehicles.get("east", []):
            if v["status"] == "departed":
                continue
            color = colors["east"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vx = (cx + rw2) - prog * rw2 - (prog - 1) * car_len
            else:
                q = v.get("queue_pos", 0)
                vx = (cx + rw2 + stop_offset) + 4 + q * (car_len + gap)
            self._draw_car_rect(painter, vx, ew_lane_y_wb - car_w / 2.0, car_len, car_w, color, v["id"])

        # Nyugati járművek
        ew_lane_y_eb = cy + rw2 / 2.0
        for v in self.vehicles.get("west", []):
            if v["status"] == "departed":
                continue
            color = colors["west"]
            if v["status"] == "crossing":
                prog = v.get("crossing_progress", 1)
                vx = (cx - rw2) + prog * (rw2 * 1.0)
            else:
                q = v.get("queue_pos", 0)
                vx = (cx - rw2 - stop_offset) - car_len - 4 - q * (car_len + gap)
            self._draw_car_rect(painter, vx, ew_lane_y_eb - car_w / 2.0, car_len, car_w, color, v["id"])

    def _draw_car_rect(self, painter: QPainter, x: float, y: float, w: float, h: float, color: QColor, text: str):
        """Kirajzol egy autót azonosító felirattal."""
        painter.setPen(QPen(QColor("#ffffff"), 1.2))
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(int(x), int(y), int(w), int(h), 4, 4)

        painter.setBrush(QBrush(QColor("#2f3640")))
        painter.setPen(Qt.NoPen)
        cw, ch = max(3, int(w * 0.6)), max(3, int(h * 0.4))
        cx = int(x + (w - cw) / 2)
        cy = int(y + (h - ch) / 2)
        painter.drawRoundedRect(cx, cy, cw, ch, 2, 2)

        painter.setPen(QColor("#ffffff"))
        font = QFont("sans-serif", 7, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(x, y, w, h), Qt.AlignCenter, text)

    def _draw_pedestrians(self, painter: QPainter, cx: float, cy: float, rw2: float):
        """Kirajzolja a várakozó és átkelő gyalogosokat kis körökként."""
        ped_r = 5.0
        ped_color = QColor("#00d2d3")

        # Északi átkelő
        y_north = cy - rw2 - 10
        for p in self.pedestrians.get("north", []):
            if p["status"] == "departed":
                continue
            if p["status"] == "crossing":
                prog = p.get("crossing_progress", 1)
                px = (cx - rw2) + prog * (rw2 * 2.0 / 3.0)
            else:
                q = p.get("queue_pos", 0)
                px = (cx - rw2) - 10 - q * 12
            self._draw_ped_dot(painter, px, y_north, ped_r, ped_color, p["id"])

        # Déli átkelő
        y_south = cy + rw2 + 10
        for p in self.pedestrians.get("south", []):
            if p["status"] == "departed":
                continue
            if p["status"] == "crossing":
                prog = p.get("crossing_progress", 1)
                px = (cx + rw2) - prog * (rw2 * 2.0 / 3.0)
            else:
                q = p.get("queue_pos", 0)
                px = (cx + rw2) + 10 + q * 12
            self._draw_ped_dot(painter, px, y_south, ped_r, ped_color, p["id"])

        # Nyugati átkelő
        x_west = cx - rw2 - 10
        for p in self.pedestrians.get("west", []):
            if p["status"] == "departed":
                continue
            if p["status"] == "crossing":
                prog = p.get("crossing_progress", 1)
                py = (cy + rw2) - prog * (rw2 * 2.0 / 3.0)
            else:
                q = p.get("queue_pos", 0)
                py = (cy + rw2) + 10 + q * 12
            self._draw_ped_dot(painter, x_west, py, ped_r, ped_color, p["id"])

        # Keleti átkelő
        x_east = cx + rw2 + 10
        for p in self.pedestrians.get("east", []):
            if p["status"] == "departed":
                continue
            if p["status"] == "crossing":
                prog = p.get("crossing_progress", 1)
                py = (cy - rw2) + prog * (rw2 * 2.0 / 3.0)
            else:
                q = p.get("queue_pos", 0)
                py = (cy - rw2) - 10 - q * 12
            self._draw_ped_dot(painter, x_east, py, ped_r, ped_color, p["id"])

    def _draw_ped_dot(self, painter: QPainter, x: float, y: float, r: float, color: QColor, text: str):
        """Kirajzol egy gyalogost."""
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(x - r), int(y - r), int(r * 2), int(r * 2))


class TrafficPedestrianIntersectionViewerWidget(QFrame):
    """
    Dedikált, interaktív vizualizációs widget a kereszteződés és gyalogosforgalom
    megjelenítéséhez (Phase 3).
    Valós idejű gombkezelést és kommunikációs csatornát biztosít az aktív szimulációhoz.
    """
    request_made = Signal(str)

    def __init__(self, parent=None):
        """Inicializálja a widgetet és felületi komponenseit."""
        super().__init__(parent)
        self.plugin = None
        self.engine = None
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("""
            TrafficPedestrianIntersectionViewerWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f3640, stop:1 #1e272e);
                border: 2px solid #718093;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Címsor
        self.title_label = QLabel("🚶🚦 Négyirányú Kereszteződés és Gyalogos Szimuláció (Phase 3)")
        self.title_label.setStyleSheet(
            "background: #192a56; color: white; padding: 6px; font-weight: bold; border-radius: 6px; font-size: 13px;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # 1. Rajzvászon
        self.canvas = PedestrianIntersectionCanvasWidget(self)
        self.canvas.crossing_requested.connect(self.request_pedestrian)
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

        # Elsőbbség / Fázis
        row_header = QLabel("ELSŐBBSÉG / AKTÍV FORGALOM:")
        row_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px;")
        info_layout.addWidget(row_header)

        self.right_of_way_badge = QLabel("INICIALIZÁLÁS")
        self.right_of_way_badge.setStyleSheet("""
            background-color: #353b48;
            color: #dcdde1;
            font-weight: bold;
            font-size: 12px;
            padding: 5px 8px;
            border-radius: 6px;
        """)
        self.right_of_way_badge.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.right_of_way_badge)

        # Jármű jelzőlámpák állapota
        v_header = QLabel("JÁRMŰ JELZŐLÁMPÁK:")
        v_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(v_header)

        self.ns_light_status = QLabel("Észak-Dél jármű: PIROS ⛔")
        self.ns_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.ns_light_status)

        self.ew_light_status = QLabel("Kelet-Nyugat jármű: PIROS ⛔")
        self.ew_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.ew_light_status)

        # Gyalogos jelzőlámpák és igények állapota
        p_header = QLabel("GYALOGOS JELZŐK ÉS IGÉNYEK:")
        p_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(p_header)

        self.ped_light_status = QLabel("Gyalogos átkelők: PIROS ⛔")
        self.ped_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.ped_light_status)

        self.ped_requests_label = QLabel("Hívógombok: Nincs kérelem")
        self.ped_requests_label.setStyleSheet("color: #fbc531; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.ped_requests_label)

        # Interaktív Gyalogos Hívógombok (valós idejű gombok a felületen)
        buttons_header = QLabel("GYALOGOS HÍVÓGOMBOK:")
        buttons_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(buttons_header)

        btn_grid = QGridLayout()
        btn_grid.setSpacing(4)

        btn_style = """
            QPushButton {
                background-color: #2f3640;
                color: #f5f6fa;
                border: 1px solid #718093;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e1b12c;
                color: #1e272e;
            }
            QPushButton:pressed {
                background-color: #fbc531;
                color: #1e272e;
            }
        """

        self.btn_north = QPushButton("Észak 🔔")
        self.btn_north.setStyleSheet(btn_style)
        self.btn_north.clicked.connect(lambda: self.request_pedestrian("north"))
        btn_grid.addWidget(self.btn_north, 0, 0)

        self.btn_south = QPushButton("Dél 🔔")
        self.btn_south.setStyleSheet(btn_style)
        self.btn_south.clicked.connect(lambda: self.request_pedestrian("south"))
        btn_grid.addWidget(self.btn_south, 0, 1)

        self.btn_west = QPushButton("Nyugat 🔔")
        self.btn_west.setStyleSheet(btn_style)
        self.btn_west.clicked.connect(lambda: self.request_pedestrian("west"))
        btn_grid.addWidget(self.btn_west, 1, 0)

        self.btn_east = QPushButton("Kelet 🔔")
        self.btn_east.setStyleSheet(btn_style)
        self.btn_east.clicked.connect(lambda: self.request_pedestrian("east"))
        btn_grid.addWidget(self.btn_east, 1, 1)

        info_layout.addLayout(btn_grid)

        # Forgalmi metrikák
        m_header = QLabel("FORGALMI METRIKÁK:")
        m_header.setStyleSheet("color: #718093; font-weight: bold; font-size: 10px; margin-top: 4px;")
        info_layout.addWidget(m_header)

        self.metrics_label = QLabel("Várakozik: Jármű: 0 | Gyalogos: 0")
        self.metrics_label.setStyleSheet("color: #f5f6fa; font-size: 11px;")
        info_layout.addWidget(self.metrics_label)

        self.passed_label = QLabel("Áthaladt: 0 db")
        self.passed_label.setStyleSheet("color: #2ed573; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.passed_label)

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

        # Alsó részletes állapotmagyarázat
        self.status_detail = QLabel("Kereszteződés és gyalogos szimuláció készen áll az indításra.")
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

    def set_plugin(self, plugin):
        """Beállítja a társított plugint a valós idejű kommunikációhoz."""
        self.plugin = plugin

    def set_engine(self, engine):
        """Beállítja a társított motort a valós idejű lépésfrissítéshez."""
        self.engine = engine

    def request_pedestrian(self, crossing: str):
        """
        Kezeli az interaktív gombnyomást a vászonról vagy az információs panelről.
        A kérést közvetlenül az aktív szimulációhoz továbbítja.
        """
        crossing = str(crossing).strip().lower()
        self.request_made.emit(crossing)
        handled = False
        if self.plugin and hasattr(self.plugin, 'register_pedestrian_request'):
            handled = self.plugin.register_pedestrian_request(crossing, engine=self.engine)
        elif self.engine and hasattr(self.engine, 'register_pedestrian_request'):
            handled = self.engine.register_pedestrian_request(crossing)

        # Frissítsük a vizuális hívógomb visszajelzést a kérelemről
        cur_reqs = dict(self.canvas.pedestrian_requests)
        cur_reqs[crossing] = True
        self.canvas.pedestrian_requests = cur_reqs
        self.canvas.update()

        req_list = [c.upper() for c, req in cur_reqs.items() if req]
        self.ped_requests_label.setText(f"Hívógombok: {', '.join(req_list) if req_list else 'Nincs kérelem'}")

    def update_state(self, step):
        """Frissíti a felületi elemeket az átadott VisualizationStep alapján."""
        extra = getattr(step, 'extra', {}) or {}
        v_lights = extra.get("vehicle_lights") or {}
        p_lights = extra.get("pedestrian_lights") or {}
        p_reqs = extra.get("pedestrian_requests") or {}
        vehicles = extra.get("vehicles") or {}
        pedestrians = extra.get("pedestrians") or {}
        row = extra.get("right_of_way", "NONE")
        row_hu = extra.get("right_of_way_hu", row)

        self.canvas.set_simulation_state(v_lights, p_lights, p_reqs, vehicles, pedestrians, row)

        self.right_of_way_badge.setText(str(row_hu).upper())
        if "Észak-Dél" in str(row_hu) or row == "NORTH_SOUTH":
            self.right_of_way_badge.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 11px; padding: 5px 8px; border-radius: 6px;")
        elif "Kelet-Nyugat" in str(row_hu) or row == "EAST_WEST":
            self.right_of_way_badge.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; font-size: 11px; padding: 5px 8px; border-radius: 6px;")
        elif "Gyalogos" in str(row_hu) or row == "PEDESTRIANS":
            self.right_of_way_badge.setStyleSheet("background-color: #16a085; color: white; font-weight: bold; font-size: 11px; padding: 5px 8px; border-radius: 6px;")
        elif "kiürítés" in str(row_hu).lower() or "piros" in str(row_hu).lower():
            self.right_of_way_badge.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 11px; padding: 5px 8px; border-radius: 6px;")
        else:
            self.right_of_way_badge.setStyleSheet("background-color: #353b48; color: #dcdde1; font-weight: bold; font-size: 11px; padding: 5px 8px; border-radius: 6px;")

        def get_lamp_str(lamps):
            if lamps.get("green"):
                return "ZÖLD 🟢", "#2ed573"
            elif lamps.get("yellow"):
                return "SÁRGA 🟡", "#fbc531"
            elif lamps.get("red"):
                return "PIROS ⛔", "#ff6b6b"
            return "KIKAPCSOLVA ⚫", "#718093"

        ns_str, ns_col = get_lamp_str(v_lights.get("ns", {}))
        ew_str, ew_col = get_lamp_str(v_lights.get("ew", {}))
        self.ns_light_status.setText(f"Észak-Dél jármű: {ns_str}")
        self.ns_light_status.setStyleSheet(f"color: {ns_col}; font-weight: bold; font-size: 11px;")
        self.ew_light_status.setText(f"Kelet-Nyugat jármű: {ew_str}")
        self.ew_light_status.setStyleSheet(f"color: {ew_col}; font-weight: bold; font-size: 11px;")

        active_peds = [c.upper() for c, l in p_lights.items() if l.get("green")]
        if active_peds:
            self.ped_light_status.setText(f"Gyalogos: ZÖLD 🟢 ({', '.join(active_peds)})")
            self.ped_light_status.setStyleSheet("color: #2ed573; font-weight: bold; font-size: 11px;")
        else:
            self.ped_light_status.setText("Gyalogos átkelők: PIROS ⛔")
            self.ped_light_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 11px;")

        req_list = [c.upper() for c, req in p_reqs.items() if req]
        self.ped_requests_label.setText(f"Hívógombok: {', '.join(req_list) if req_list else 'Nincs kérelem'}")

        arr = getattr(step, 'array', None) or []
        w_v = arr[0] if len(arr) > 0 else 0
        w_p = arr[1] if len(arr) > 1 else 0
        passed = arr[2] if len(arr) > 2 else 0
        self.metrics_label.setText(f"Várakozik: Jármű: {w_v} | Gyalogos: {w_p}")
        self.passed_label.setText(f"Áthaladt összesen: {passed} db")

        rem_time = extra.get("remaining_time", 0)
        self.countdown_label.setText(f"{rem_time} mp" if rem_time > 0 else "-")
        cycle = extra.get("cycle", 0)
        total_cycles = extra.get("total_cycles", 0)
        self.cycle_info_label.setText(f"Ciklus: {cycle} / {total_cycles}")

        self.status_detail.setText(getattr(step, 'explanation', ''))
