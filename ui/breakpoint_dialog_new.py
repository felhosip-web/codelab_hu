# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QInputDialog, QCheckBox,
    QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt

class BreakpointDialog(QDialog):
    def __init__(self, breakpoint_manager, current_plugin_id=None, parent=None):
        super().__init__(parent)
        self.bp_manager = breakpoint_manager
        self.current_plugin_id = current_plugin_id
        self.setWindowTitle("Breakpointok - fejlett logika")
        self.setMinimumSize(800, 500)
        layout = QVBoxLayout(self)
        title = QLabel("Breakpointok - felteteles, hit count, logpoint")
        title.setStyleSheet("background: #e74c3c; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(title)
        info = QLabel("Feltetel: i==5, comparisons>100, hit%10==0 | Hit feltetel: hit==5 | Logpoint: nem all meg, csak logol")
        info.setStyleSheet("background: #dfe6e9; padding: 6px; border-radius: 4px; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.list_widget)
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("background: #2d2d3d; color: #f1f2f6; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px;")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        btn_layout = QHBoxLayout()
        self.btn_toggle = QPushButton("Ki/Be")
        self.btn_toggle.clicked.connect(self.on_toggle)
        btn_layout.addWidget(self.btn_toggle)
        self.btn_edit = QPushButton("Szerkesztes")
        self.btn_edit.clicked.connect(self.on_edit)
        btn_layout.addWidget(self.btn_edit)
        self.btn_add = QPushButton("Uj")
        self.btn_add.clicked.connect(self.on_add)
        btn_layout.addWidget(self.btn_add)
        self.btn_remove = QPushButton("Torles")
        self.btn_remove.clicked.connect(self.on_remove)
        btn_layout.addWidget(self.btn_remove)
        self.btn_clear = QPushButton("Osszes torlese")
        self.btn_clear.clicked.connect(self.on_clear)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.refresh_list()
    def refresh_list(self):
        self.list_widget.clear()
        plugin_ids = [self.current_plugin_id] if self.current_plugin_id else list(self.bp_manager.breakpoints.keys())
        for pid in plugin_ids:
            if not pid: continue
            for bp in self.bp_manager.get_breakpoints(pid):
                status = "OK" if bp.enabled else "OFF"
                pre = "PRE" if bp.predefined else "USR"
                log = "LOG" if bp.is_logpoint else "BRK"
                cond = f"cond={bp.condition}" if bp.condition else ""
                hit_cond = f"hit_cond={bp.hit_condition}" if bp.hit_condition else ""
                log_msg = f"log={bp.log_message[:20]}" if bp.log_message else ""
                item = QListWidgetItem(f"{status} {log} {pre} {pid} | Sor {bp.line} | hit={bp.hit_count} | {cond} {hit_cond} {log_msg} | {bp.description}")
                item.setData(Qt.UserRole, (pid, bp.line))
                self.list_widget.addItem(item)
    def on_selection_changed(self, current, previous):
        if not current:
            self.detail_label.setText("")
            return
        pid, line = current.data(Qt.UserRole)
        for bp in self.bp_manager.get_breakpoints(pid):
            if bp.line == line:
                self.detail_label.setText(f"Plugin: {bp.plugin_id} | Sor: {bp.line} | Enabled: {bp.enabled} | Feltetel: {bp.condition} | Hit feltetel: {bp.hit_condition} | Hit count: {bp.hit_count} | Logpoint: {bp.is_logpoint} | Log: {bp.log_message} | Leiras: {bp.description}")
                break
    def on_toggle(self):
        item = self.list_widget.currentItem()
        if not item: return
        pid, line = item.data(Qt.UserRole)
        self.bp_manager.toggle_breakpoint(pid, line)
        self.refresh_list()
    def on_edit(self):
        item = self.list_widget.currentItem()
        if not item: return
        pid, line = item.data(Qt.UserRole)
        bp = None
        for b in self.bp_manager.get_breakpoints(pid):
            if b.line == line:
                bp = b
                break
        if not bp: return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Breakpoint szerkesztes - {pid}:{line}")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        condition_edit = QLineEdit(bp.condition)
        condition_edit.setPlaceholderText("pl. i==5, comparisons>100")
        form.addRow("Feltetel:", condition_edit)
        hit_condition_edit = QLineEdit(bp.hit_condition)
        hit_condition_edit.setPlaceholderText("pl. hit==5, hit%10==0")
        form.addRow("Hit feltetel:", hit_condition_edit)
        log_message_edit = QLineEdit(bp.log_message)
        log_message_edit.setPlaceholderText("pl. i={i} j={j} hit={hit}")
        form.addRow("Log uzenet:", log_message_edit)
        is_logpoint_check = QCheckBox("Logpoint")
        is_logpoint_check.setChecked(bp.is_logpoint)
        form.addRow(is_logpoint_check)
        description_edit = QLineEdit(bp.description)
        form.addRow("Leiras:", description_edit)
        enabled_check = QCheckBox("Engedelyezve")
        enabled_check.setChecked(bp.enabled)
        form.addRow(enabled_check)
        layout.addLayout(form)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Megse")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        if dialog.exec():
            bp.condition = condition_edit.text()
            bp.hit_condition = hit_condition_edit.text()
            bp.log_message = log_message_edit.text()
            bp.is_logpoint = is_logpoint_check.isChecked()
            bp.description = description_edit.text()
            bp.enabled = enabled_check.isChecked()
            self.bp_manager.save()
            self.refresh_list()
    def on_add(self):
        if not self.current_plugin_id: return
        line, ok = QInputDialog.getInt(self, "Breakpoint", "Sor szama:", 1, 1, 100)
        if ok:
            self.bp_manager.add_breakpoint(self.current_plugin_id, line)
            self.refresh_list()
    def on_remove(self):
        item = self.list_widget.currentItem()
        if not item: return
        pid, line = item.data(Qt.UserRole)
        self.bp_manager.remove_breakpoint(pid, line)
        self.refresh_list()
    def on_clear(self):
        if self.current_plugin_id:
            self.bp_manager.clear_all(self.current_plugin_id)
        else:
            self.bp_manager.clear_all()
        self.refresh_list()
