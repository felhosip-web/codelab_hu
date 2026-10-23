# -*- coding: utf-8 -*-
"""
Példa - hogyan csinálj új plugin-t?
Másold le ezt a mappát és nevezd át pl. quick-re, és írd át a kódot.

Ez a teljes buborék rendezés plugin 1 fájlban volt, most ez a sablon mutatja
hogy milyen egyszerű újat csinálni.
"""
# A plugins/quick/plugin.py így nézne ki:

TEMPLATE = """
from core.plugin_system import AlgorithmPluginBase

class SortStep:
    def __init__(self, array, key=None, sorted_end=0, highlight_indices=None, 
                 code_line=0, explanation="", comparisons=0, shifts=0, pass_num=0):
        self.array = array.copy()
        self.key = key
        self.sorted_end = sorted_end
        self.highlight = highlight_indices or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.shifts = shifts
        self.pass_num = pass_num

class MyNewSortPlugin(AlgorithmPluginBase):
    id = "my_sort"
    name = "Az én rendezésem"
    description = "Leírás"
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    icon = "⭐"
    
    codes = {
        "Python": "def sort(a): pass",
        "C++": "void sort() {}",
        # ... többi nyelv
    }
    
    def get_steps(self, arr):
        # yield SortStep(...)
        pass
    
    def get_code(self, lang):
        return self.codes.get(lang, "")
"""
