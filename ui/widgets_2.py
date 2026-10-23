# -*- coding: utf-8 -*-
"""
QT extrákat kihasználó widgetek - Array + Graph Viewer
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit, QGraphicsOpacityEffect, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPen, QBrush, QColor
from core.config import UI_TEXTS

class ArrayViewerWidget(QFrame):
    def __init__(self, initial_array):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #fef9e7; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel(f"🟩 {UI_TEXTS['array_viewer']}")
        title.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.pivot_label = QLabel("")
        self.pivot_label.setStyleSheet("background: #e74c3c; color: white; padding: 4px 8px; border-radius: 10px; font-weight: bold;")
        self.pivot_label.hide()
        header_layout.addWidget(self.pivot_label)
        layout.addLayout(header_layout)
        
        info_row = QHBoxLayout()
        self.key_label = QLabel(f"{UI_TEXTS['key']}: -")
        self.key_label.setStyleSheet("background: #f6b93b; padding: 8px; border-radius: 6px; font-weight: bold; font-size: 16px;")
        self.key_label.setMaximumWidth(80)
        info_row.addWidget(self.key_label)
        self.range_label = QLabel("")
        self.range_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-size: 11px;")
        info_row.addWidget(self.range_label)
        info_row.addStretch()
        layout.addLayout(info_row)
        
        self.array_container = QWidget()
        self.array_layout = QHBoxLayout(self.array_container)
        self.array_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.array_container)
        
        self.recursion_label = QLabel("")
        self.recursion_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        self.recursion_label.setWordWrap(True)
        layout.addWidget(self.recursion_label)
        
        self.labels = []
        self.update_state(initial_array, None, 0, [], extra={})
    
    def update_state(self, array, key, sorted_end, highlights, extra=None):
        extra = extra or {}
        while self.array_layout.count():
            child = self.array_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels.clear()
        
        if key is not None:
            self.key_label.setText(f"{UI_TEXTS['key']}\n{key}")
            self.key_label.show()
        else:
            self.key_label.hide()
        
        pivot_idx = extra.get("pivot")
        if pivot_idx is not None:
            self.pivot_label.setText(f"PIVOT: a[{pivot_idx}]")
            self.pivot_label.show()
        else:
            self.pivot_label.hide()
        
        low = extra.get("low")
        high = extra.get("high")
        if low is not None and high is not None:
            self.range_label.setText(f"[{low}..{high}] i={extra.get('i','-')} j={extra.get('j','-')} mid={extra.get('mid','-')}")
            self.range_label.show()
        else:
            self.range_label.hide()
        
        rec = extra.get("recursion") or extra.get("queue") or extra.get("stack") or extra.get("open")
        if rec:
            txt = f"Sor/Verem: {str(rec)[:80]}"
            self.recursion_label.setText(txt)
            self.recursion_label.show()
        else:
            if extra.get("target") is not None:
                self.recursion_label.setText(f"Cél: {extra.get('target')} | {extra}")
                self.recursion_label.show()
            else:
                self.recursion_label.hide()
        
        for idx, val in enumerate(array):
            lbl = QLabel(str(val))
            lbl.setMinimumSize(48, 48)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(self._style_for(idx, sorted_end, highlights, pivot_idx, extra))
            font = QFont("Sans", 11, QFont.Bold)
            lbl.setFont(font)
            if idx in highlights:
                effect = QGraphicsOpacityEffect(lbl)
                effect.setOpacity(0.9)
                lbl.setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity")
                anim.setDuration(300)
                anim.setStartValue(0.5)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.OutBounce)
                anim.start()
                lbl._anim = anim
                lbl._effect = effect
            self.array_layout.addWidget(lbl)
            self.labels.append(lbl)
        
        legend = QLabel(f"<span style='color:green'>{UI_TEXTS['sorted']}</span> | <span style='color:gray'>{UI_TEXTS['unsorted']}</span> | <span style='color:#e74c3c'>pivot</span> | <span style='color:#f6b93b'>aktív</span>")
        legend.setAlignment(Qt.AlignCenter)
        legend.setStyleSheet("font-size: 10px;")
        self.array_layout.addWidget(legend)
    
    def _style_for(self, idx, sorted_end, highlights, pivot_idx, extra):
        base = "border-radius: 8px; border: 1px solid #333; font-weight: bold;"
        target = extra.get("target")
        found = extra.get("found")
        if found is not None and idx == found:
            return base + " background: #00b894; color: white; border: 3px solid #00a085; font-size: 14px;"
        if pivot_idx is not None and idx == pivot_idx:
            return base + " background: #e74c3c; color: white; border: 3px solid #c0392b; font-size: 14px;"
        if idx in highlights:
            return base + " background: #f6b93b; color: black; border: 2px solid #e67e22;"
        if idx <= sorted_end and sorted_end >=0:
            return base + " background: #6ab04c; color: white;"
        return base + " background: white; color: black;"

class GraphViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #6c5ce7; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        title = QLabel("🗺️ Gráf Nézet - QGraphicsView")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        layout.addWidget(self.view)
        
        self.path_label = QLabel("")
        self.path_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
    
    def update_state(self, step):
        self.scene.clear()
        g = step.graph
        visited = step.visited
        frontier = set(step.frontier) if step.frontier else set()
        current = step.current
        path = set(step.path) if step.path else set()
        path_list = step.path or []
        
        # Élek rajzolása
        for u,v,w in g.edges:
            # Csak egyszer rajzoljuk irányítatlant
            if u > v: 
                continue
            if u in g.nodes and v in g.nodes:
                x1,y1 = g.nodes[u].x, g.nodes[u].y
                x2,y2 = g.nodes[v].x, g.nodes[v].y
                # Ha path része, vastag zöld
                is_path_edge = False
                for i in range(len(path_list)-1):
                    if (path_list[i]==u and path_list[i+1]==v) or (path_list[i]==v and path_list[i+1]==u):
                        is_path_edge = True
                        break
                pen = QPen(QColor("#00b894"), 4) if is_path_edge else QPen(QColor("#b2bec3"), 2)
                if (u==current and v in frontier) or (v==current and u in frontier):
                    pen = QPen(QColor("#fdcb6e"), 3)
                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(pen)
                self.scene.addItem(line)
                # Súly
                mx, my = (x1+x2)/2, (y1+y2)/2
                txt = QGraphicsTextItem(str(int(w)))
                txt.setPos(mx, my)
                txt.setDefaultTextColor(QColor("#636e72"))
                self.scene.addItem(txt)
        
        # Csomópontok
        for nid, node in g.nodes.items():
            color = QColor("#dfe6e9")  # alap
            if nid in path:
                color = QColor("#00b894")  # út
            elif nid == current:
                color = QColor("#e74c3c")  # aktuális
            elif nid in frontier:
                color = QColor("#fdcb6e")  # frontier
            elif nid in visited:
                color = QColor("#74b9ff")  # visited
            
            if nid == step.extra.get("start"):
                color = QColor("#6c5ce7")
            if nid == step.extra.get("target"):
                color = QColor("#e84393")
            
            ellipse = QGraphicsEllipseItem(node.x-18, node.y-18, 36, 36)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(QColor("#2d3436"), 2))
            self.scene.addItem(ellipse)
            
            label = QGraphicsTextItem(str(node.id))
            label.setPos(node.x-8, node.y-10)
            label.setDefaultTextColor(QColor("white") if color != QColor("#dfe6e9") else QColor("black"))
            font = QFont("Sans", 10, QFont.Bold)
            label.setFont(font)
            self.scene.addItem(label)
        
        # Info
        extra = step.extra
        self.info_label.setText(f"Start: {extra.get('start','-')} | Cél: {extra.get('target','-')} | Visited: {len(visited)} | Frontier: {len(frontier)} | {extra}")
        if path_list:
            self.path_label.setText(f"Út: {' -> '.join(map(str, path_list))} | Költség: {step.distances.get(extra.get('target'), '?') if step.distances else '?'}")
            self.path_label.show()
        else:
            self.path_label.hide()
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

class CodeViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: white; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        self.title_label = QLabel("📄 code.cpp - Code Viewer")
        self.title_label.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.title_label)
        self.condition_label = QLabel("j < 0 → stop")
        self.condition_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 10px; font-weight: bold;")
        layout.addWidget(self.condition_label)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Monospace", 10))
        layout.addWidget(self.text_edit)
        self.status_bar = QLabel(f"{UI_TEXTS['pass']} 0 | {UI_TEXTS['comparisons']} 0 | {UI_TEXTS['shifts']} 0")
        self.status_bar.setStyleSheet("background: #f1f2f6; padding: 4px; font-size: 11px;")
        layout.addWidget(self.status_bar)
        self.current_code_lines = []
    def set_code(self, code, lang):
        self.current_code_lines = code.splitlines()
        self.text_edit.setPlainText(code)
    def set_title(self, title_text):
        self.title_label.setText(f"📄 {title_text} - Code Viewer")
    def highlight_line(self, line_num):
        if not self.current_code_lines: return
        html = ""
        for i, line in enumerate(self.current_code_lines, start=1):
            esc = line.replace("<", "&lt;").replace(">", "&gt;")
            if i == line_num:
                html += f"<div style='background: #2e86de; color: white; padding:2px; border-left: 4px solid #f6b93b;'><b>{i:2}: {esc}</b></div>"
            else:
                html += f"<div style='padding:2px;'>{i:2}: {esc}</div>"
        self.text_edit.setHtml(f"<pre style='font-family: monospace; margin:0;'>{html}</pre>")

class StatsBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #dfe6e9; border-radius: 8px; padding: 6px;")
        layout = QHBoxLayout(self)
        self.lbl_time = QLabel(f"{UI_TEXTS['time']}\nO(n²)")
        self.lbl_space = QLabel(f"{UI_TEXTS['space']}\nO(1)")
        self.lbl_size = QLabel(f"{UI_TEXTS['size']}\n10")
        self.lbl_lang = QLabel(f"{UI_TEXTS['language']}\nC++")
        for lbl in [self.lbl_time, self.lbl_space, self.lbl_size, self.lbl_lang]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; background: white; padding: 4px; border-radius: 4px;")
            layout.addWidget(lbl)
    def set_complexity(self, time_c, space_c):
        self.lbl_time.setText(f"{UI_TEXTS['time']}\n{time_c}")
        self.lbl_space.setText(f"{UI_TEXTS['space']}\n{space_c}")
    def update_stats(self, comp, shifts, pass_num):
        self.lbl_size.setText(f"{UI_TEXTS['size']}\n10")


class CRCViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #00b894; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("✅ CRC / 🛰️ Reed-Solomon - hibafelismerés és javítás")
        title.setStyleSheet("background: #00b894; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Bit sor / szimbólum sor
        self.bits_container = QWidget()
        self.bits_layout = QHBoxLayout(self.bits_container)
        self.bits_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.bits_container)
        
        # Polinom / kódszó info
        self.poly_label = QLabel("")
        self.poly_label.setStyleSheet("background: #ffeaa7; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.poly_label.setWordWrap(True)
        layout.addWidget(self.poly_label)
        
        # Eredmény
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
    
    def update_state(self, step):
        while self.bits_layout.count():
            child = self.bits_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        data = step.data or step.extra.get('data','')
        current = step.current_data or step.extra.get('current','')
        gen = step.generator or step.extra.get('gen','')
        pos = step.position
        
        # Bitek / szimbólumok kirajzolása
        display = current or data
        if isinstance(display, list):
            display = "".join(map(str, display))
        
        for idx, ch in enumerate(str(display)[:40]):
            lbl = QLabel(ch)
            lbl.setMinimumSize(28, 32)
            lbl.setAlignment(Qt.AlignCenter)
            style = "border: 1px solid #b2bec3; border-radius: 4px; font-family: monospace; font-weight: bold; background: white;"
            if idx == pos:
                style += " background: #e74c3c; color: white; border: 2px solid #c0392b;"
            elif pos!=-1 and idx>=pos and idx<pos+len(gen) and step.extra.get('phase')=='osztás':
                style += " background: #fdcb6e;"
            elif ch in ['1'] and pos!=-1:
                style += " background: #dfe6e9;"
            lbl.setStyleSheet(style)
            self.bits_layout.addWidget(lbl)
        self.bits_layout.addStretch()
        
        # Polinom / kódszó
        if step.extra.get('phase') in ['polinom', 'értékelés', 'kódol']:
            poly = step.extra.get('poly','')
            codeword = step.extra.get('codeword','')
            self.poly_label.setText(f"f(x)={poly} | Kódszó: {codeword} | n={step.extra.get('n')} k={step.extra.get('k')} p={step.extra.get('p')}")
            self.poly_label.show()
        elif gen:
            self.poly_label.setText(f"Generátor: {gen} | Adat: {data} | Aktuális: {current[:60]}")
            self.poly_label.show()
        else:
            self.poly_label.hide()
        
        # Eredmény
        self.info_label.setText(step.explanation)
        
        result_text = f"CRC: {step.crc or step.extra.get('crc','')} | Full: {step.extra.get('full','')} | Corrupted: {step.extra.get('corrupted','')} | Codeword: {step.extra.get('codeword','')} | Errors: {step.extra.get('errors','')} | {step.extra}"
        self.result_label.setText(result_text)


class FourierViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #6c5ce7; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("Fourier - ido -> frekvencia, mindenhol hasznaljak!")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Ido tartomany
        self.signal_container = QWidget()
        self.signal_layout = QHBoxLayout(self.signal_container)
        self.signal_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("Ido tartomany - jel:"))
        layout.addWidget(self.signal_container)
        
        # Frekvencia spektrum - magnitudó
        self.mag_container = QWidget()
        self.mag_layout = QHBoxLayout(self.mag_container)
        self.mag_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("Frekvencia spektrum - magnitudó |X[k]| (erősség):"))
        layout.addWidget(self.mag_container)
        
        # Fázis
        self.phase_container = QWidget()
        self.phase_layout = QHBoxLayout(self.phase_container)
        layout.addWidget(QLabel("Fázis - arg(X[k]):"))
        layout.addWidget(self.phase_container)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        for container, layout in [(self.signal_container, self.signal_layout), (self.mag_container, self.mag_layout), (self.phase_container, self.phase_layout)]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        signal = getattr(step, 'signal', []) or step.extra.get('signal', [])
        magnitude = getattr(step, 'magnitude', []) or step.extra.get('magnitude', [])
        phase = getattr(step, 'phase', []) or step.extra.get('phase', [])
        spectrum = getattr(step, 'spectrum', []) or step.extra.get('spectrum', [])
        
        # Ido tartomany
        if signal:
            max_sig = max([abs(s) for s in signal]) if signal else 1
            for idx, val in enumerate(signal):
                lbl = QLabel(f"{val:.1f}")
                lbl.setMinimumSize(50, 50)
                lbl.setAlignment(Qt.AlignCenter)
                # Magasság arányos
                height = int(30 + abs(val)/max_sig * 30) if max_sig>0 else 30
                lbl.setMinimumHeight(height)
                style = "border: 1px solid #0984e3; border-radius: 4px; background: #74b9ff; font-family: monospace; font-size: 9px;"
                if idx == step.current_k:
                    style += " background: #0984e3; color: white; border: 3px solid #0652dd;"
                lbl.setStyleSheet(style)
                self.signal_layout.addWidget(lbl)
            self.signal_layout.addStretch()
            self.signal_container.show()
        else:
            self.signal_container.hide()
        
        # Magnitúdó
        if magnitude:
            max_mag = max(magnitude) if magnitude else 1
            for idx, mag in enumerate(magnitude):
                lbl = QLabel(f"{mag:.1f}")
                lbl.setMinimumSize(50, 50)
                lbl.setAlignment(Qt.AlignCenter)
                height = int(20 + mag/max_mag * 40) if max_mag>0 else 20
                lbl.setMinimumHeight(height)
                style = "border: 1px solid #e17055; border-radius: 4px; background: #fab1a0; font-family: monospace; font-size: 9px;"
                if mag == max_mag and max_mag>0.1:
                    style += " background: #e17055; color: white; border: 3px solid #d63031; font-weight: bold;"
                if idx == step.current_k:
                    style += " border: 3px solid #6c5ce7;"
                lbl.setStyleSheet(style)
                self.mag_layout.addWidget(lbl)
            # Domináns frekvencia jelölés
            if magnitude:
                max_idx = magnitude.index(max(magnitude)) if max(magnitude)>0 else -1
                if max_idx>=0:
                    dom_lbl = QLabel(f"Domináns k={max_idx}")
                    dom_lbl.setStyleSheet("color: #e17055; font-weight: bold; font-size: 10px;")
                    self.mag_layout.addWidget(dom_lbl)
            self.mag_layout.addStretch()
            self.mag_container.show()
        else:
            self.mag_container.hide()
        
        # Fázis
        if phase:
            for idx, ph in enumerate(phase):
                lbl = QLabel(f"{ph:.1f}")
                lbl.setMinimumSize(45, 30)
                lbl.setAlignment(Qt.AlignCenter)
                style = "border: 1px solid #00b894; border-radius: 4px; background: #55efc4; font-family: monospace; font-size: 8px;"
                lbl.setStyleSheet(style)
                self.phase_layout.addWidget(lbl)
            self.phase_layout.addStretch()
            self.phase_container.show()
        else:
            self.phase_container.hide()
        
        self.info_label.setText(step.explanation)
        self.detail_label.setText(f"{step.extra.get('phase','')} | N={step.extra.get('N','')} | DFT vs FFT: {step.extra.get('dft_ops','')} vs {step.extra.get('fft_ops','')} -> {step.extra.get('speedup','')}x")

