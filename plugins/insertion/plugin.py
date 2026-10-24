# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

class InsertionSortPlugin(AlgorithmPluginBase):
    id = "insertion_sort"
    name = "Beszúró rendezés"
    description = "Vedd fel. Csúsztasd be. A rendezett részbe illeszt."
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    icon = "📌"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("array_size", "Tömb méret", "int", 10, 3, 20, description="Hány elem legyen"))
        self.params.add(Param("max_value", "Max érték", "int", 20, 5, 100, description="Max érték"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, param_id, value):
        self.params.set(param_id, value)
    
    def generate_input(self, params_dict=None):
        import random
        size = self.params.get("array_size")
        max_v = self.params.get("max_value")
        return [random.randint(1, max_v) for _ in range(size)]
    

    codes = {
        "Python": """def beszurasos_rendezes(a):
    for i in range(1, len(a)):
        kulcs = a[i]
        j = i - 1
        while j >= 0 and a[j] > kulcs:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = kulcs
    return a""",
        "C++": """void insertionSort(int a[], int n) {
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;
    }
}""",
        "C": """void insertionSort(int a[], int n) {
    int i, key, j;
    for (i = 1; i < n; i++) {
        key = a[i]; j = i-1;
        while (j >= 0 && a[j] > key) {
            a[j+1] = a[j]; j--;
        }
        a[j+1] = key;
    }
}""",
        "BASIC": """' Beszúró rendezés
FOR I = 1 TO N-1
    KEY = A(I): J = I-1
    WHILE J >=0 AND A(J) > KEY
        A(J+1) = A(J): J = J-1
    WEND
    A(J+1) = KEY
NEXT I""",
        "Java": """void sort(int a[]) {
    for (int i=1; i<a.length; ++i) {
        int key = a[i]; int j = i-1;
        while (j>=0 && a[j] > key) {
            a[j+1] = a[j]; j--;
        }
        a[j+1] = key;
    }
}""",
        "Pascal": """for i:=1 to High(a) do begin
  key:=a[i]; j:=i-1;
  while (j>=0) and (a[j]>key) do begin
    a[j+1]:=a[j]; j:=j-1;
  end;
  a[j+1]:=key;
end;"""
    }
    
    def get_steps(self, arr):
        a = arr.copy()
        comparisons = 0
        shifts = 0
        n = len(a)
        yield VisualizationStep(
            array=a, key=None, sorted_end=0, code_line=1,
            explanation="Kezdés: első elem rendezett",
            metrics={"comparisons": 0, "shifts": 0, "pass_num": 0}
        )
        for i in range(1, n):
            key = a[i]
            j = i - 1
            yield VisualizationStep(
                array=a, key=key, sorted_end=i-1, highlight=[i], code_line=3,
                explanation=f"Kulcs: {key} (i={i})",
                metrics={"comparisons": comparisons, "shifts": shifts, "pass_num": i}
            )
            while j >= 0 and a[j] > key:
                comparisons += 1
                a[j+1] = a[j]
                shifts += 1
                yield VisualizationStep(
                    array=a, key=key, sorted_end=i-1, highlight=[j, j+1], code_line=6,
                    explanation=f"Tolás: a[{j}]={a[j]} > kulcs",
                    metrics={"comparisons": comparisons, "shifts": shifts, "pass_num": i}
                )
                j -= 1
            if j < 0:
                yield VisualizationStep(
                    array=a, key=key, sorted_end=i-1, highlight=[], code_line=5,
                    explanation="j < 0 → megáll",
                    metrics={"comparisons": comparisons, "shifts": shifts, "pass_num": i}
                )
            a[j+1] = key
            yield VisualizationStep(
                array=a, key=None, sorted_end=i, highlight=[j+1], code_line=8,
                explanation=f"Beilleszt: a[{j+1}]={key}",
                metrics={"comparisons": comparisons, "shifts": shifts, "pass_num": i}
            )
        yield VisualizationStep(
            array=a, key=None, sorted_end=n-1, code_line=9,
            explanation="✅ Kész! Minden elem a helyén.",
            metrics={"comparisons": comparisons, "shifts": shifts, "pass_num": n}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
