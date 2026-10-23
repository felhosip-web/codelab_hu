# -*- coding: utf-8 -*-
"""
Egyedi widgetek - Array Viewer, Code Viewer, Stats
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from core.config import UI_TEXTS

class ArrayViewerWidget(QFrame):
    def __init__(self, initial_array):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #fef9e7; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        title = QLabel(f"🟩 {UI_TEXTS['array_viewer']}")
        title.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.key_label = QLabel(f"{UI_TEXTS['key']}: -")
        self.key_label.setStyleSheet("background: #f6b93b; padding: 8px; border-radius: 6px; font-weight: bold; font-size: 16px;")
        self.key_label.setMaximumWidth(80)
        layout.addWidget(self.key_label)
        
        self.array_container = QWidget()
        self.array_layout = QHBoxLayout(self.array_container)
        self.array_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.array_container)
        
        self.labels = []
        self.update_state(initial_array, None, 0, [])
    
    def update_state(self, array, key, sorted_end, highlights):
        # Töröljük a régi elemeket
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
        
        for idx, val in enumerate(array):
            lbl = QLabel(str(val))
            lbl.setMinimumSize(45, 45)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(self._style_for(idx, sorted_end, highlights))
            font = QFont("Sans", 11, QFont.Bold)
            lbl.setFont(font)
            self.array_layout.addWidget(lbl)
            self.labels.append(lbl)
        
        # sorted / unsorted felirat
        legend = QLabel(f"<span style='color:green'>{UI_TEXTS['sorted']}</span> | <span style='color:gray'>{UI_TEXTS['unsorted']}</span>")
        legend.setAlignment(Qt.AlignCenter)
        self.array_layout.addWidget(legend)
    
    def _style_for(self, idx, sorted_end, highlights):
        base = "border-radius: 6px; border: 1px solid #333; font-weight: bold;"
        if idx in highlights:
            return base + " background: #f6b93b; color: black; border: 2px solid red;"
        if idx <= sorted_end:
            return base + " background: #6ab04c; color: white;"
        return base + " background: white; color: black;"

class CodeViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: white; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        title = QLabel("📄 insertion_sort.cpp - Code Viewer")
        title.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
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
    
    def highlight_line(self, line_num):
        if not self.current_code_lines:
            return
        html = ""
        for i, line in enumerate(self.current_code_lines, start=1):
            esc = line.replace("<", "&lt;").replace(">", "&gt;")
            if i == line_num:
                html += f"<div style='background: #2e86de; color: white;'><b>{i:2}: {esc}</b></div>"
            else:
                html += f"<div>{i:2}: {esc}</div>"
        self.text_edit.setHtml(f"<pre style='font-family: monospace;'>{html}</pre>")

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
            lbl.setStyleSheet("font-weight: bold;")
            layout.addWidget(lbl)
    
    def update_stats(self, comp, shifts, pass_num):
        self.lbl_size.setText(f"{UI_TEXTS['size']}\n10")
        # dinamikusan frissíthető lenne


class TreeViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #00b894; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("🌳 Fa Nézet - QGraphicsView + forgatás animáció")
        title.setStyleSheet("background: #00b894; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.info_label)
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)
        self.path_label = QLabel("")
        self.path_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
    
    def update_state(self, step):
        self.scene.clear()
        tree = step.structure
        if not hasattr(tree, 'root') or not tree.root:
            self.info_label.setText("Üres fa")
            return
        # Fa bejárás rajzoláshoz
        def draw_node(node):
            if not node:
                return
            # Node
            is_highlight = node.value in (step.highlight_nodes or [])
            is_current = node.value == step.current_value
            color = QColor("#00b894") if is_highlight else QColor("#dfe6e9")
            if is_current:
                color = QColor("#e74c3c")
            # AVL esetén magasság kiírás
            label_text = str(node.value)
            if hasattr(node, 'height'):
                label_text += f"\nh={node.height}"
            
            ellipse = QGraphicsEllipseItem(node.x-22, node.y-22, 44, 44)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(QColor("#2d3436"), 2 if not is_current else 3))
            self.scene.addItem(ellipse)
            txt = QGraphicsTextItem(label_text)
            txt.setPos(node.x-12, node.y-12)
            txt.setDefaultTextColor(QColor("white") if is_highlight or is_current else QColor("black"))
            font = QFont("Sans", 9, QFont.Bold)
            txt.setFont(font)
            self.scene.addItem(txt)
            
            # Élek
            if node.left:
                line = QGraphicsLineItem(node.x, node.y+22, node.left.x, node.left.y-22)
                line.setPen(QPen(QColor("#636e72"), 2))
                self.scene.addItem(line)
                draw_node(node.left)
            if node.right:
                line = QGraphicsLineItem(node.x, node.y+22, node.right.x, node.right.y-22)
                line.setPen(QPen(QColor("#636e72"), 2))
                self.scene.addItem(line)
                draw_node(node.right)
        
        draw_node(tree.root)
        extra = step.extra
        self.info_label.setText(f"Aktuális: {step.current_value} | Beszúrva: {extra.get('inserted','-')} | {extra}")
        if extra.get("path"):
            self.path_label.setText(f"Út: {' -> '.join(map(str, extra.get('path')))}")
            self.path_label.show()
        else:
            self.path_label.hide()
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

class HashViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #fdcb6e; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("🗃️ Hash Tábla - vödrök, láncolt lista")
        title.setStyleSheet("background: #fdcb6e; color: #2d3436; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        self.buckets_container = QWidget()
        self.buckets_layout = QVBoxLayout(self.buckets_container)
        layout.addWidget(self.buckets_container)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        # Törlés
        while self.buckets_layout.count():
            child = self.buckets_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                # nested layouts
                while child.layout().count():
                    c2 = child.layout().takeAt(0)
                    if c2.widget():
                        c2.widget().deleteLater()
        
        ht = step.structure
        buckets = step.extra.get("buckets") or [list(b) for b in ht.buckets]
        current = step.current_value
        hash_idx = step.extra.get("hash_idx")
        search = step.extra.get("search")
        
        for idx, bucket in enumerate(buckets):
            row = QHBoxLayout()
            idx_label = QLabel(f"[{idx}]")
            idx_label.setMinimumWidth(40)
            if idx == hash_idx:
                idx_label.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; padding: 4px; border-radius: 4px;")
            else:
                idx_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-weight: bold;")
            row.addWidget(idx_label)
            
            if not bucket:
                empty = QLabel("(üres)")
                empty.setStyleSheet("color: #b2bec3; font-style: italic;")
                row.addWidget(empty)
            else:
                for val in bucket:
                    lbl = QLabel(str(val))
                    lbl.setMinimumSize(40, 32)
                    lbl.setAlignment(Qt.AlignCenter)
                    if val == current or val == search:
                        lbl.setStyleSheet("background: #fdcb6e; border: 2px solid #e17055; border-radius: 6px; font-weight: bold;")
                    else:
                        lbl.setStyleSheet("background: white; border: 1px solid #636e72; border-radius: 6px;")
                    row.addWidget(lbl)
                    if bucket.index(val) < len(bucket)-1:
                        arrow = QLabel("→")
                        arrow.setStyleSheet("font-weight: bold;")
                        row.addWidget(arrow)
            row.addStretch()
            container = QWidget()
            container.setLayout(row)
            self.buckets_layout.addWidget(container)
        
        extra = step.extra
        self.info_label.setText(f"Hash: {current} % {ht.size} = {hash_idx} | Keresés: {search} | {extra}")
        if extra.get("collision"):
            self.detail_label.setText(f"⚠️ Ütközés! Vödör {hash_idx} már foglalt, láncoljuk")
            self.detail_label.show()
        elif extra.get("found") is not None:
            self.detail_label.setText(f"{'✅ Találat' if extra.get('found') else '❌ Nincs'} | Vödör {hash_idx}")
            self.detail_label.show()
        else:
            self.detail_label.hide()


class SimpleVisualViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #00b894; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("Egyszeru de latvanyos - faktorialis, Fibonacci, LNKO, primszita, Hanoi")
        title.setStyleSheet("background: #00b894; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        self.visual_container = QWidget()
        self.visual_layout = QHBoxLayout(self.visual_container)
        self.visual_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.visual_container)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        while self.visual_layout.count():
            child = self.visual_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        array = getattr(step, 'array', []) or step.extra.get('fib', []) or step.extra.get('primes', []) or []
        value = getattr(step, 'value', None)
        extra = step.extra
        
        # Faktoriális, Fibonacci, LNKO, szita, Hanoi vizualizáció
        if extra.get('phase') in ['init', 'iter', 'done', 'mod', 'sieve', 'move']:
            if 'fib' in extra:
                fib = extra['fib']
                for idx, val in enumerate(fib):
                    lbl = QLabel(str(val))
                    lbl.setMinimumSize(50, 50)
                    lbl.setAlignment(Qt.AlignCenter)
                    style = "border: 2px solid #00b894; border-radius: 8px; background: #55efc4; font-family: monospace; font-weight: bold;"
                    if idx == len(fib)-1:
                        style += " background: #00b894; color: white; border: 3px solid #00a085;"
                    lbl.setStyleSheet(style)
                    self.visual_layout.addWidget(lbl)
            elif 'primes' in extra or 'is_prime' in extra:
                # Prímszita: számok, prímek zöldek, kihúzottak szürkék
                is_prime = extra.get('is_prime', [])
                n = extra.get('n', 30)
                if is_prime:
                    for i in range(len(is_prime)):
                        if i<2:
                            continue
                        lbl = QLabel(str(i))
                        lbl.setMinimumSize(40, 40)
                        lbl.setAlignment(Qt.AlignCenter)
                        if is_prime[i]:
                            style = "border: 2px solid #00b894; border-radius: 20px; background: #55efc4; font-weight: bold;"
                        else:
                            style = "border: 1px solid #b2bec3; border-radius: 4px; background: #dfe6e9; color: #636e72;"
                        lbl.setStyleSheet(style)
                        self.visual_layout.addWidget(lbl)
                else:
                    for val in array:
                        lbl = QLabel(str(val))
                        lbl.setMinimumSize(40, 40)
                        lbl.setAlignment(Qt.AlignCenter)
                        lbl.setStyleSheet("border: 2px solid #00b894; border-radius: 20px; background: #55efc4; font-weight: bold;")
                        self.visual_layout.addWidget(lbl)
            elif extra.get('phase') == 'move':
                # Hanoi: forrás -> cél
                src = extra.get('src', '')
                dst = extra.get('dst', '')
                lbl = QLabel(f"{src} -> {dst}")
                lbl.setMinimumSize(80, 40)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("border: 2px solid #e17055; border-radius: 8px; background: #fab1a0; font-weight: bold; font-size: 14px;")
                self.visual_layout.addWidget(lbl)
            else:
                # Általános: érték
                if value is not None:
                    lbl = QLabel(str(value))
                    lbl.setMinimumSize(60, 60)
                    lbl.setAlignment(Qt.AlignCenter)
                    lbl.setStyleSheet("border: 3px solid #6c5ce7; border-radius: 30px; background: #a29bfe; color: white; font-weight: bold; font-size: 16px;")
                    self.visual_layout.addWidget(lbl)
                for val in array[:20]:  # Max 20
                    lbl = QLabel(str(val))
                    lbl.setMinimumSize(45, 35)
                    lbl.setAlignment(Qt.AlignCenter)
                    lbl.setStyleSheet("border: 1px solid #b2bec3; border-radius: 4px; background: #dfe6e9; font-family: monospace;")
                    self.visual_layout.addWidget(lbl)
            
            self.visual_layout.addStretch()
        
        self.info_label.setText(step.explanation)
        self.detail_label.setText(f"{extra}")

