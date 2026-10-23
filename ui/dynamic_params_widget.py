# -*- coding: utf-8 -*-
"""
Dinamikus paraméterek UI widget - futás közben állítható
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QSpinBox, QLineEdit, QComboBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from core.dynamic_params import Param, DynamicParams

class DynamicParamsWidget(QFrame):
    param_changed = Signal(str, object)  # param_id, value
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f1f2f6; border: 2px solid #6c5ce7; border-radius: 8px;")
        self.layout = QVBoxLayout(self)
        
        title = QLabel("🎛️ Dinamikus Paraméterek - futás közben állítható")
        title.setStyleSheet("background: #6c5ce7; color: white; padding: 4px; font-weight: bold; border-radius: 4px;")
        self.layout.addWidget(title)
        
        self.params_container = QVBoxLayout()
        self.layout.addLayout(self.params_container)
        
        self.current_params = None
        self.widgets = {}
        
        # Alkalmaz gomb
        self.apply_btn = QPushButton("✓ Alkalmaz és újragenerál")
        self.apply_btn.setStyleSheet("background: #00b894; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        self.apply_btn.clicked.connect(self.on_apply)
        self.layout.addWidget(self.apply_btn)
        
        self.layout.addStretch()
    
    def set_params(self, dynamic_params: DynamicParams):
        # Törlés
        while self.params_container.count():
            child = self.params_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    c2 = child.layout().takeAt(0)
                    if c2.widget():
                        c2.widget().deleteLater()
        
        self.widgets.clear()
        self.current_params = dynamic_params
        
        if not dynamic_params:
            lbl = QLabel("Ennek a pluginnak nincs állítható paramétere")
            lbl.setStyleSheet("color: #636e72; font-style: italic;")
            self.params_container.addWidget(lbl)
            return
        
        for param in dynamic_params.list_params():
            row = QHBoxLayout()
            lbl = QLabel(f"{param.name}:")
            lbl.setMinimumWidth(100)
            lbl.setToolTip(param.description)
            row.addWidget(lbl)
            
            if param.type == "int":
                spin = QSpinBox()
                spin.setRange(param.min_val or 0, param.max_val or 100)
                spin.setValue(dynamic_params.get(param.id))
                spin.valueChanged.connect(lambda v, pid=param.id: self.on_param_change(pid, v))
                row.addWidget(spin)
                self.widgets[param.id] = spin
            elif param.type == "float":
                spin = QSpinBox()  # Egyszerűsítve int-ként
                spin.setRange(int(param.min_val or 0), int(param.max_val or 100))
                spin.setValue(int(dynamic_params.get(param.id)))
                spin.valueChanged.connect(lambda v, pid=param.id: self.on_param_change(pid, v))
                row.addWidget(spin)
                self.widgets[param.id] = spin
            elif param.type == "string":
                edit = QLineEdit()
                edit.setText(str(dynamic_params.get(param.id)))
                edit.textChanged.connect(lambda t, pid=param.id: self.on_param_change(pid, t))
                row.addWidget(edit)
                self.widgets[param.id] = edit
            elif param.type == "choice":
                combo = QComboBox()
                combo.addItems(param.choices or [])
                combo.setCurrentText(str(dynamic_params.get(param.id)))
                combo.currentTextChanged.connect(lambda t, pid=param.id: self.on_param_change(pid, t))
                row.addWidget(combo)
                self.widgets[param.id] = combo
            elif param.type == "bool":
                chk = QCheckBox()
                chk.setChecked(bool(dynamic_params.get(param.id)))
                chk.stateChanged.connect(lambda s, pid=param.id: self.on_param_change(pid, bool(s)))
                row.addWidget(chk)
                self.widgets[param.id] = chk
            
            # Leírás
            desc = QLabel(param.description)
            desc.setStyleSheet("font-size: 9px; color: #636e72;")
            row.addWidget(desc)
            row.addStretch()
            
            container = QFrame()
            container.setLayout(row)
            container.setStyleSheet("background: white; border-radius: 4px; padding: 2px;")
            self.params_container.addWidget(container)
    
    def on_param_change(self, param_id, value):
        if self.current_params:
            self.current_params.set(param_id, value)
        self.param_changed.emit(param_id, value)
    
    def on_apply(self):
        # Minden paramétert kibocsát
        if self.current_params:
            for pid in self.current_params.params:
                self.param_changed.emit(pid, self.current_params.get(pid))
    
    def get_values(self):
        if self.current_params:
            return self.current_params.to_dict()
        return {}
