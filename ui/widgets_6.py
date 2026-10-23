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
        self.title_label.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.title_label)
        
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
        
        self.title_label = QLabel("📄 insertion_sort.cpp - Code Viewer")
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

    def set_title(self, title_text):
        self.title_label.setText(f"📄 {title_text} - Code Viewer")

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
    
    def set_complexity(self, time_c, space_c):
        self.lbl_time.setText(f"{UI_TEXTS['time']}\n{time_c}")
        self.lbl_space.setText(f"{UI_TEXTS['space']}\n{space_c}")

    def update_stats(self, comp, shifts, pass_num):
        self.lbl_size.setText(f"{UI_TEXTS['size']}\n10")
        # dinamikusan frissíthető lenne


class BTreeViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #6c5ce7; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("🌲 B-fa - több kulcs egy csomóban, split")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.info_label)
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        self.scene.clear()
        btree = step.structure
        if not btree or not btree.root:
            self.info_label.setText("Üres B-fa")
            return
        
        def draw_node(node):
            # Node doboz több kulccsal
            x = node.x
            y = node.y
            width = len(node.keys)*40 + 20
            rect = self.scene.addRect(x-width/2, y-20, width, 40)
            is_current = step.current_value in node.keys if step.current_value else False
            color = QColor("#fdcb6e") if is_current else QColor("#dfe6e9")
            rect.setBrush(QBrush(color))
            rect.setPen(QPen(QColor("#2d3436"), 2))
            
            for i, key in enumerate(node.keys):
                txt = QGraphicsTextItem(str(key))
                txt.setPos(x-width/2+10+i*40, y-10)
                txt.setDefaultTextColor(QColor("#2d3436"))
                font = QFont("Sans", 9, QFont.Bold)
                txt.setFont(font)
                self.scene.addItem(txt)
                if i < len(node.keys)-1:
                    line = self.scene.addLine(x-width/2+40+i*40, y-20, x-width/2+40+i*40, y+20)
                    line.setPen(QPen(QColor("#b2bec3"), 1))
            
            for child in node.children:
                # Él a szülő közepéből gyerekbe
                line = QGraphicsLineItem(x, y+20, child.x, child.y-20)
                line.setPen(QPen(QColor("#636e72"), 2))
                self.scene.addItem(line)
                draw_node(child)
        
        draw_node(btree.root)
        extra = step.extra
        self.info_label.setText(f"t={extra.get('t','-')} | Aktuális: {step.current_value} | Beszúrva: {extra.get('inserted','-')}")
        self.detail_label.setText(f"Gyökér: {btree.root.keys} | {extra}")
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

class TrieViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #00b894; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("📚 Trie - prefix fa, karakterenként")
        title.setStyleSheet("background: #00b894; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px;")
        layout.addWidget(self.info_label)
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 10px;")
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        self.scene.clear()
        trie = step.structure
        if not trie or not trie.root:
            self.info_label.setText("Üres Trie")
            return
        
        def draw_node(node, is_end=False):
            x = getattr(node, 'x', 0)
            y = getattr(node, 'y', 0)
            char = getattr(node, 'char', 'ROOT')
            is_highlight = char in (step.extra.get('path', []) or [])
            is_current = char == step.extra.get('current_char', '')
            
            color = QColor("#00b894") if is_highlight else QColor("#dfe6e9")
            if is_current:
                color = QColor("#e74c3c")
            if is_end:
                color = QColor("#6c5ce7")
            
            ellipse = QGraphicsEllipseItem(x-18, y-18, 36, 36)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(QColor("#2d3436"), 2))
            self.scene.addItem(ellipse)
            
            txt = QGraphicsTextItem(char if char else '""')
            txt.setPos(x-8, y-10)
            txt.setDefaultTextColor(QColor("white") if is_highlight or is_end or is_current else QColor("black"))
            font = QFont("Sans", 9, QFont.Bold)
            txt.setFont(font)
            self.scene.addItem(txt)
            
            if is_end:
                end_mark = QGraphicsTextItem("END")
                end_mark.setPos(x-12, y+18)
                end_mark.setDefaultTextColor(QColor("#6c5ce7"))
                font2 = QFont("Sans", 7, QFont.Bold)
                end_mark.setFont(font2)
                self.scene.addItem(end_mark)
            
            for child in node.children.values():
                line = QGraphicsLineItem(x, y+18, child.x, child.y-18)
                line.setPen(QPen(QColor("#636e72"), 1))
                self.scene.addItem(line)
                draw_node(child, child.is_end)
        
        draw_node(trie.root, trie.root.is_end)
        extra = step.extra
        self.info_label.setText(f"Keresés: {extra.get('search','-')} | Beszúrva: {extra.get('inserted','-')} | Út: {extra.get('path','-')}")
        self.detail_label.setText(f"{'✅ Találat' if extra.get('found') else '❌ Nincs' if 'found' in extra else ''} | Szavak: {extra.get('words','-')}")
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)


class FIFOLIFOViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #0984e3; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("FIFO / LIFO - Verem, Sor, KorKoros, Deque")
        title.setStyleSheet("background: #0984e3; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Stack vertical
        self.stack_container = QWidget()
        self.stack_layout = QVBoxLayout(self.stack_container)
        self.stack_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("Verem (LIFO) - felul tol, felul vesz:"))
        layout.addWidget(self.stack_container)
        
        # Queue horizontal
        self.queue_container = QWidget()
        self.queue_layout = QHBoxLayout(self.queue_container)
        self.queue_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("Sor (FIFO) - hatul tol, elol vesz:"))
        layout.addWidget(self.queue_container)
        
        # Circular
        self.circular_container = QWidget()
        self.circular_layout = QHBoxLayout(self.circular_container)
        layout.addWidget(QLabel("Korkoros sor - front/rear forog:"))
        layout.addWidget(self.circular_container)
        
        # Deque
        self.deque_container = QWidget()
        self.deque_layout = QHBoxLayout(self.deque_container)
        layout.addWidget(QLabel("Deque - mindket vegen:"))
        layout.addWidget(self.deque_container)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
    
    def update_state(self, step):
        for container, layout in [(self.stack_container, self.stack_layout), (self.queue_container, self.queue_layout), (self.circular_container, self.circular_layout), (self.deque_container, self.deque_layout)]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        stype = getattr(step, 'structure_type', '') or step.extra.get('phase', '')
        structure = getattr(step, 'structure', None) or step.extra.get('stack', []) or step.extra.get('queue', []) or step.extra.get('deque', []) or []
        if not structure and hasattr(step, 'extra'):
            structure = step.extra.get('queue', []) or step.extra.get('stack', []) or step.extra.get('deque', []) or step.extra.get('circular', []) or []
            if not structure and 'queue' in step.extra:
                structure = step.extra['queue']
        
        # Stack
        if step.structure_type == 'stack' or 'stack' in step.extra:
            stack_data = step.extra.get('stack', structure)
            for idx, val in enumerate(reversed(stack_data)):
                lbl = QLabel(str(val))
                lbl.setMinimumSize(80, 30)
                lbl.setAlignment(Qt.AlignCenter)
                is_top = idx==0
                style = "border: 2px solid #e17055; border-radius: 4px; font-family: monospace; font-weight: bold; background: #fab1a0;"
                if is_top:
                    style += " background: #e17055; color: white; border: 3px solid #d63031;"
                lbl.setStyleSheet(style)
                self.stack_layout.addWidget(lbl)
            if stack_data:
                top_lbl = QLabel(f"Top -> {stack_data[-1] if stack_data else 'ures'}")
                top_lbl.setStyleSheet("color: #e17055; font-weight: bold; font-size: 10px;")
                self.stack_layout.addWidget(top_lbl)
            self.stack_container.show()
        else:
            self.stack_container.hide()
        
        # Queue
        if step.structure_type == 'queue' or 'queue' in step.extra:
            queue_data = step.extra.get('queue', structure)
            for idx, val in enumerate(queue_data):
                lbl = QLabel(str(val))
                lbl.setMinimumSize(50, 40)
                lbl.setAlignment(Qt.AlignCenter)
                style = "border: 1px solid #0984e3; border-radius: 4px; background: #74b9ff; font-family: monospace; font-weight: bold;"
                if idx==0:
                    style += " background: #0984e3; color: white; border: 3px solid #0652dd;"
                lbl.setStyleSheet(style)
                self.queue_layout.addWidget(lbl)
            if queue_data:
                front_lbl = QLabel(f"Front={queue_data[0]} Rear={queue_data[-1]}")
                front_lbl.setStyleSheet("color: #0984e3; font-weight: bold; font-size: 10px;")
                self.queue_layout.addWidget(front_lbl)
            self.queue_layout.addStretch()
            self.queue_container.show()
        else:
            self.queue_container.hide()
        
        # Circular
        if step.structure_type == 'circular' or 'circular' in step.extra or step.extra.get('capacity'):
            queue_data = step.extra.get('queue', structure)
            front = step.extra.get('front', step.front)
            rear = step.extra.get('rear', step.rear)
            capacity = step.extra.get('capacity', len(queue_data) if queue_data else 5)
            for idx in range(capacity):
                val = queue_data[idx] if idx < len(queue_data) else None
                lbl = QLabel(str(val) if val is not None else "None")
                lbl.setMinimumSize(50, 40)
                lbl.setAlignment(Qt.AlignCenter)
                style = "border: 1px solid #00b894; border-radius: 8px; font-family: monospace; background: white;"
                if idx==front and front!=-1:
                    style += " background: #00b894; color: white; border: 3px solid #00a085;"
                if idx==rear and rear!=-1:
                    style += " border: 3px solid #e17055;"
                if val is None:
                    style += " background: #dfe6e9; color: #636e72;"
                lbl.setStyleSheet(style)
                self.circular_layout.addWidget(lbl)
            info = QLabel(f"front={front} rear={rear} cap={capacity}")
            info.setStyleSheet("color: #00b894; font-weight: bold; font-size: 10px;")
            self.circular_layout.addWidget(info)
            self.circular_layout.addStretch()
            self.circular_container.show()
        else:
            self.circular_container.hide()
        
        # Deque
        if step.structure_type == 'deque' or 'deque' in step.extra:
            deque_data = step.extra.get('deque', structure)
            for idx, val in enumerate(deque_data):
                lbl = QLabel(str(val))
                lbl.setMinimumSize(50, 40)
                lbl.setAlignment(Qt.AlignCenter)
                style = "border: 1px solid #6c5ce7; border-radius: 4px; background: #a29bfe; font-family: monospace;"
                if idx==0 or idx==len(deque_data)-1:
                    style += " background: #6c5ce7; color: white; border: 2px solid #5f27cd;"
                lbl.setStyleSheet(style)
                self.deque_layout.addWidget(lbl)
            self.deque_layout.addStretch()
            self.deque_container.show()
        else:
            self.deque_container.hide()
        
        self.info_label.setText(step.explanation)
        self.detail_label.setText(f"{step.extra}")

