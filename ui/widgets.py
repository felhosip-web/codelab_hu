# -*- coding: utf-8 -*-
"""
Egyedi widgetek - Array Viewer, Code Viewer (Native QPlainTextEdit), Stats
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout,
    QPlainTextEdit, QTextEdit
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QTextCursor, QTextFormat
from core.config import UI_TEXTS
from core.workspace_config import WorkspaceConfig
from ui.code_highlighter import CodeHighlighter


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config or WorkspaceConfig()
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        self.highlighter = CodeHighlighter(
            self.document(), theme=self.config.theme, enabled=self.config.syntax_highlight
        )
        self.apply_config(self.config)

    def apply_config(self, config: WorkspaceConfig):
        self.config = config
        font = QFont(config.font_family, config.font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        if config.theme == "dark":
            self.setStyleSheet("background: #1e1e1e; color: #d4d4d4; border: none;")
        else:
            self.setStyleSheet("background: #ffffff; color: #000000; border: none;")

        self.highlighter.set_theme(config.theme)
        self.highlighter.set_enabled(config.syntax_highlight)
        self.line_number_area.setVisible(config.show_line_numbers)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        if not self.config.show_line_numbers:
            return 0
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            digits += 1
            max_num //= 10
        space = 8 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, new_block_count):
        width = self.line_number_area_width()
        self.setViewportMargins(width, 0, 0, 0)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), width, cr.height()))

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        if not self.config.show_line_numbers:
            return
        painter = QPainter(self.line_number_area)
        bg = QColor("#2d2d2d") if self.config.theme == "dark" else QColor("#f0f0f0")
        fg = QColor("#858585") if self.config.theme == "dark" else QColor("#888888")
        painter.fillRect(event.rect(), bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(fg)
                painter.setFont(self.font())
                painter.drawText(
                    0, top, self.line_number_area.width() - 4, self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class ArrayViewerWidget(QFrame):
    def __init__(self, initial_array):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #fef9e7; border: 2px solid #2e86de; border-radius: 8px;")
        layout = QVBoxLayout(self)

        self.title_label = QLabel(f"🟩 {UI_TEXTS['array_viewer']}")
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
        while self.array_layout.count():
            child = self.array_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels.clear()

        if array is None:
            array = []
        if highlights is None:
            highlights = []

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

        if array:
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
    def __init__(self, workspace_config=None):
        super().__init__()
        self.config = workspace_config or WorkspaceConfig()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.title_label = QLabel("📄 Code Viewer")
        self.title_label.setStyleSheet("background: #2e86de; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(self.title_label)

        self.code_editor = CodeEditor(config=self.config)
        self.code_editor.setReadOnly(True)
        layout.addWidget(self.code_editor)

        self.status_bar = QLabel(f"{UI_TEXTS['pass']} 0 | {UI_TEXTS['comparisons']} 0 | {UI_TEXTS['shifts']} 0")
        self.status_bar.setStyleSheet("background: #f1f2f6; padding: 4px; font-size: 11px;")
        layout.addWidget(self.status_bar)

        self.current_code = ""
        self.current_lang = "C++"

    def apply_workspace_config(self, config: WorkspaceConfig):
        self.config = config
        self.apply_theme_style()
        self.code_editor.apply_config(config)

    def apply_theme_style(self):
        if self.config.theme == "dark":
            self.setStyleSheet("background: #1e1e1e; border: 2px solid #007acc; border-radius: 8px;")
        else:
            self.setStyleSheet("background: white; border: 2px solid #2e86de; border-radius: 8px;")

    def set_code(self, code: str, lang: str):
        self.current_code = code
        self.current_lang = lang
        self.code_editor.setPlainText(code)
        self.code_editor.setExtraSelections([])

    def highlight_line(self, line_num: int):
        extra_selections = []
        doc = self.code_editor.document()
        if 1 <= line_num <= doc.blockCount():
            block = doc.findBlockByLineNumber(line_num - 1)
            if block.isValid():
                cursor = QTextCursor(block)
                selection = QTextEdit.ExtraSelection()
                line_color = QColor(self.config.current_line_color) if self.config.current_line_color else (
                    QColor("#0984e3") if self.config.theme == "dark" else QColor("#2e86de")
                )
                selection.format.setBackground(line_color)
                selection.format.setForeground(QColor("white"))
                selection.format.setFontWeight(QFont.Bold)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)

                if self.config.auto_scroll_to_line:
                    self.code_editor.setTextCursor(cursor)
                    self.code_editor.centerCursor()

        self.code_editor.setExtraSelections(extra_selections)

    def set_title(self, title_text: str):
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


class StringViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #e17055; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("📝 String Matching - csúszóablak, LPS tábla")
        title.setStyleSheet("background: #e17055; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 4px; border-radius: 4px; font-size: 11px; font-family: monospace;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.text_container = QWidget()
        self.text_layout = QHBoxLayout(self.text_container)
        self.text_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("Szöveg:"))
        layout.addWidget(self.text_container)

        self.pattern_container = QWidget()
        self.pattern_layout = QHBoxLayout(self.pattern_container)
        self.pattern_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("Minta:"))
        layout.addWidget(self.pattern_container)

        self.lps_label = QLabel("")
        self.lps_label.setStyleSheet("background: #fdcb6e; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 12px;")
        self.lps_label.setWordWrap(True)
        layout.addWidget(self.lps_label)

        self.hash_label = QLabel("")
        self.hash_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.hash_label.setWordWrap(True)
        layout.addWidget(self.hash_label)

    def update_state(self, step):
        for container, layout in [(self.text_container, self.text_layout), (self.pattern_container, self.pattern_layout)]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        text = step.text
        pattern = step.pattern
        text_pos = step.text_pos
        pattern_pos = step.pattern_pos

        for idx, ch in enumerate(text):
            lbl = QLabel(ch)
            lbl.setMinimumSize(28, 32)
            lbl.setAlignment(Qt.AlignCenter)
            style = "border: 1px solid #b2bec3; border-radius: 4px; font-weight: bold; font-family: monospace;"
            if idx in step.highlight_text:
                if step.extra.get("phase") == "találat":
                    style += " background: #00b894; color: white; border: 2px solid #00a085;"
                elif step.extra.get("jump"):
                    style += " background: #fdcb6e; border: 2px solid #e17055;"
                else:
                    style += " background: #74b9ff; color: white; border: 2px solid #0984e3;"
            elif idx >= text_pos and idx < text_pos + len(pattern) and step.extra.get("phase") in ["hash", "rolling", "nem egyezik"]:
                style += " background: #dfe6e9;"
            else:
                style += " background: white;"
            lbl.setStyleSheet(style)
            self.text_layout.addWidget(lbl)

        spacer = QLabel("")
        spacer.setMinimumWidth(text_pos * 30)
        self.pattern_layout.addWidget(spacer)

        for idx, ch in enumerate(pattern):
            lbl = QLabel(ch)
            lbl.setMinimumSize(28, 32)
            lbl.setAlignment(Qt.AlignCenter)
            style = "border: 1px solid #636e72; border-radius: 4px; font-weight: bold; font-family: monospace;"
            if idx in step.highlight_pattern:
                if step.extra.get("phase") == "találat":
                    style += " background: #00b894; color: white; border: 2px solid #00a085;"
                else:
                    style += " background: #fdcb6e; border: 2px solid #e17055;"
            else:
                style += " background: #ffeaa7;"
            lbl.setStyleSheet(style)
            self.pattern_layout.addWidget(lbl)
        self.pattern_layout.addStretch()

        lps = step.lps or step.extra.get("lps") or []
        if lps:
            lps_text = "LPS: ["
            for i, v in enumerate(lps):
                if i == pattern_pos:
                    lps_text += f"<b style='background: #e74c3c; color: white;'>{v}</b>, "
                else:
                    lps_text += f"{v}, "
            lps_text = lps_text.rstrip(", ") + "]"
            lps_text += f" | Pattern: {pattern}"
            self.lps_label.setText(lps_text)
            self.lps_label.show()
        else:
            self.lps_label.hide()

        p_hash = step.hash_pattern if step.hash_pattern is not None else step.extra.get("p_hash")
        t_hash = step.hash_text if step.hash_text is not None else step.extra.get("t_hash")
        if p_hash is not None:
            hash_info = f"Hash pattern={p_hash} | Hash text ablak={t_hash} | "
            if p_hash == t_hash:
                hash_info += "✅ HASH EGYEZIK -> ellenőrizzük karaktereket"
            else:
                hash_info += "❌ hash nem egyezik -> ugrás"
            hash_info += f" | Ablak: '{step.extra.get('window','')}' | Találatok: {step.extra.get('found', [])}"
            self.hash_label.setText(hash_info)
            self.hash_label.show()
        else:
            self.hash_label.hide()

        info = f"{step.explanation} | i={step.extra.get('i','-')} j={step.extra.get('j','-')} | {step.extra.get('phase','')}"
        self.info_label.setText(info)


class ArrayConceptsViewerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background: #ffffff; border: 2px solid #6c5ce7; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("Tombok, pointerek, tombben tomb - memoria, index, cim")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.array_container = QWidget()
        self.array_layout = QHBoxLayout(self.array_container)
        self.array_layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel("1D Tomb:"))
        layout.addWidget(self.array_container)

        self.matrix_container = QWidget()
        self.matrix_layout = QVBoxLayout(self.matrix_container)
        layout.addWidget(QLabel("2D Matrix:"))
        layout.addWidget(self.matrix_container)

        self.pointer_label = QLabel("")
        self.pointer_label.setStyleSheet("background: #ffeaa7; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.pointer_label.setWordWrap(True)
        layout.addWidget(self.pointer_label)

        self.jagged_container = QWidget()
        self.jagged_layout = QVBoxLayout(self.jagged_container)
        layout.addWidget(QLabel("Tombben tomb (Jagged):"))
        layout.addWidget(self.jagged_container)

        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

    def update_state(self, step):
        for container, layout in [(self.array_container, self.array_layout), (self.matrix_container, self.matrix_layout), (self.jagged_container, self.jagged_layout)]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        array = getattr(step, 'array', []) or step.extra.get('array', []) or []
        array_2d = getattr(step, 'array_2d', None) or step.extra.get('matrix', None)
        jagged = getattr(step, 'jagged', None) or step.extra.get('jagged', None)
        memory = getattr(step, 'memory', {}) or step.extra.get('memory', {})
        pointers = getattr(step, 'pointers', {}) or step.extra.get('pointers', {})

        if array:
            for idx, val in enumerate(array):
                frame = QFrame()
                frame.setStyleSheet("border: 1px solid #b2bec3; border-radius: 4px; background: white;")
                fl = QVBoxLayout(frame)
                fl.setContentsMargins(2,2,2,2)
                idx_lbl = QLabel(f"[{idx}]")
                idx_lbl.setStyleSheet("font-size: 8px; color: #636e72;")
                idx_lbl.setAlignment(Qt.AlignCenter)
                fl.addWidget(idx_lbl)
                val_lbl = QLabel(str(val))
                val_lbl.setAlignment(Qt.AlignCenter)
                style = "font-weight: bold; font-family: monospace; padding: 4px; font-size: 12px;"
                if idx == step.current_index:
                    style += " background: #74b9ff; color: white; border: 2px solid #0984e3; border-radius: 4px;"
                else:
                    style += " background: #dfe6e9; border-radius: 4px;"
                val_lbl.setStyleSheet(style)
                fl.addWidget(val_lbl)
                addr_lbl = QLabel(f"{1000+idx*4}")
                addr_lbl.setStyleSheet("font-size: 7px; color: #636e72;")
                addr_lbl.setAlignment(Qt.AlignCenter)
                fl.addWidget(addr_lbl)
                self.array_layout.addWidget(frame)
            self.array_layout.addStretch()
            self.array_container.show()
        else:
            self.array_container.hide()

        if array_2d:
            for i, row in enumerate(array_2d):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setAlignment(Qt.AlignLeft)
                row_layout.addWidget(QLabel(f"Sor {i}:"))
                for j, val in enumerate(row):
                    lbl = QLabel(str(val))
                    lbl.setMinimumSize(40, 30)
                    lbl.setAlignment(Qt.AlignCenter)
                    style = "border: 1px solid #6c5ce7; border-radius: 4px; font-family: monospace; background: #dfe6e9;"
                    if step.current_index == i*len(row)+j:
                        style += " background: #a29bfe; color: white; border: 2px solid #6c5ce7;"
                    lbl.setStyleSheet(style)
                    row_layout.addWidget(lbl)
                self.matrix_layout.addWidget(row_widget)
            self.matrix_container.show()
        else:
            self.matrix_container.hide()

        if memory or pointers:
            mem_text = "Memoria: "
            for addr in sorted(memory.keys())[:10]:
                mem_text += f"[{addr}]={memory[addr]} "
            if len(memory)>10:
                mem_text += f"... ({len(memory)} cim)"
            mem_text += "\nPointerek: "
            for name, addr in pointers.items():
                val = memory.get(addr, "?")
                mem_text += f"{name}={addr} -> *{name}={val} | "
            self.pointer_label.setText(mem_text)
            self.pointer_label.show()
        else:
            self.pointer_label.hide()

        if jagged:
            for i, row in enumerate(jagged):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setAlignment(Qt.AlignLeft)
                row_layout.addWidget(QLabel(f"{i}:"))
                for j, val in enumerate(row):
                    lbl = QLabel(str(val))
                    lbl.setMinimumSize(36, 28)
                    lbl.setAlignment(Qt.AlignCenter)
                    style = "border: 1px solid #e17055; border-radius: 4px; background: #fab1a0; font-family: monospace;"
                    if step.current_index==i and step.extra.get('j', -1)==j:
                        style += " background: #e17055; color: white;"
                    lbl.setStyleSheet(style)
                    row_layout.addWidget(lbl)
                row_layout.addWidget(QLabel(f"  (hossz {len(row)})"))
                self.jagged_layout.addWidget(row_widget)
            self.jagged_container.show()
        else:
            self.jagged_container.hide()

        self.info_label.setText(step.explanation)
        self.detail_label.setText(f"{step.extra}")
