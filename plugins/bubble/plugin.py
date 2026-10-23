# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param

class SortStep:
    def __init__(self, array: List[int], key=None, sorted_end=0, 
                 highlight_indices=None, code_line=0, explanation="", 
                 comparisons=0, shifts=0, pass_num=0):
        self.array = array.copy()
        self.key = key
        self.sorted_end = sorted_end
        self.highlight = highlight_indices or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.shifts = shifts
        self.pass_num = pass_num

class BubbleSortPlugin(AlgorithmPluginBase):
    id = "bubble_sort"
    name = "Buborék rendezés"
    description = "A nagyok felfelé buborékolnak"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    icon = "🫧"
    
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
        "Python": """def buborek_rendezes(a):
    n = len(a)
    for i in range(n):
        cserelt = False
        for j in range(0, n-i-1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                cserelt = True
        if not cserelt:
            break
    return a""",
        "C++": """void bubbleSort(int a[], int n) {
    for (int i = 0; i < n-1; i++) {
        bool swapped = false;
        for (int j = 0; j < n-i-1; j++) {
            if (a[j] > a[j+1]) {
                swap(a[j], a[j+1]);
                swapped = true;
            }
        }
        if (!swapped) break;
    }
}""",
        "C": """void bubbleSort(int a[], int n) {
    for (int i=0; i<n-1; i++) {
        int swapped=0;
        for (int j=0; j<n-i-1; j++) {
            if (a[j] > a[j+1]) {
                int tmp=a[j]; a[j]=a[j+1]; a[j+1]=tmp;
                swapped=1;
            }
        }
        if (!swapped) break;
    }
}""",
        "BASIC": """FOR I = 0 TO N-2
    SWAPPED = 0
    FOR J = 0 TO N-I-2
        IF A(J) > A(J+1) THEN
            SWAP A(J), A(J+1)
            SWAPPED = 1
        END IF
    NEXT J
    IF SWAPPED=0 THEN EXIT FOR
NEXT I""",
        "Java": """void sort(int a[]) {
    for (int i=0; i<a.length-1; i++) {
        boolean swapped=false;
        for (int j=0; j<a.length-i-1; j++) {
            if (a[j] > a[j+1]) {
                int tmp=a[j]; a[j]=a[j+1]; a[j+1]=tmp;
                swapped=true;
            }
        }
        if (!swapped) break;
    }
}""",
        "Pascal": """for i:=0 to High(a)-1 do begin
  swapped:=False;
  for j:=0 to High(a)-i-1 do
    if a[j] > a[j+1] then begin
      tmp:=a[j]; a[j]:=a[j+1]; a[j+1]:=tmp;
      swapped:=True;
    end;
  if not swapped then Break;
end;"""
    }
    
    def get_steps(self, arr):
        a = arr.copy()
        comparisons = 0
        swaps = 0
        n = len(a)
        yield SortStep(a, key=None, sorted_end=-1, code_line=1,
                       explanation="Buborék kezdés: nagyok felfelé", comparisons=0, shifts=0, pass_num=0)
        for i in range(n):
            swapped=False
            yield SortStep(a, key=None, sorted_end=n-i-1, code_line=2,
                           explanation=f"{i+1}. kör: {n-i-1}-ig vizsgálunk", comparisons=comparisons, shifts=swaps, pass_num=i+1)
            for j in range(0, n-i-1):
                comparisons+=1
                yield SortStep(a, key=None, sorted_end=n-i-1, highlight_indices=[j, j+1], code_line=3,
                               explanation=f"Összehasonlít: {a[j]} és {a[j+1]}", comparisons=comparisons, shifts=swaps, pass_num=i+1)
                if a[j] > a[j+1]:
                    a[j], a[j+1] = a[j+1], a[j]
                    swaps+=1; swapped=True
                    yield SortStep(a, key=None, sorted_end=n-i-1, highlight_indices=[j, j+1], code_line=4,
                                   explanation=f"Csere! {a[j+1]} > {a[j]}", comparisons=comparisons, shifts=swaps, pass_num=i+1)
            yield SortStep(a, key=None, sorted_end=n-i-1, code_line=6,
                           explanation=f"Kör vége, legnagyobb a helyén", comparisons=comparisons, shifts=swaps, pass_num=i+1)
            if not swapped:
                yield SortStep(a, key=None, sorted_end=n-1, code_line=7,
                               explanation="Nincs csere, kész!", comparisons=comparisons, shifts=swaps, pass_num=i+1)
                break
        yield SortStep(a, key=None, sorted_end=n-1, code_line=8,
                       explanation="✅ Kész!", comparisons=comparisons, shifts=swaps, pass_num=n)
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
