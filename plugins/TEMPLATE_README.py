# -*- coding: utf-8 -*-
"""
Példa - hogyan csinálj új plugin-t?
Másold le ezt a mappát és nevezd át pl. quick-re, és írd át a kódot.

Ez a teljes sablon mutatja, hogy milyen egyszerű újat csinálni.
"""
# A plugin így nézne ki:

TEMPLATE = """
from core.plugin_system import AlgorithmPluginBase
from core.step import VisualizationStep

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
        # yield VisualizationStep(...)
        pass
    
    def get_code(self, lang):
        return self.codes.get(lang, "")
"""
