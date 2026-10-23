# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param

class SortStep:
    def __init__(self, array: List[int], key=None, sorted_end=0, 
                 highlight_indices=None, code_line=0, explanation="", 
                 comparisons=0, shifts=0, pass_num=0, extra=None):
        self.array = array.copy()
        self.key = key
        self.sorted_end = sorted_end
        self.highlight = highlight_indices or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.shifts = shifts
        self.pass_num = pass_num
        self.extra = extra or {}

class SelectionSortPlugin(AlgorithmPluginBase):
    id = "selection_sort"
    name = "Kiválasztó rendezés"
    description = "Keresd meg a minimumot, tedd előre"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    icon = "🎯"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    
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
        "Python": """def kivalaszto_rendezes(a):
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a""",
        "C++": """void selectionSort(int a[], int n) {
    for (int i=0; i<n-1; i++) {
        int min_idx = i;
        for (int j=i+1; j<n; j++) {
            if (a[j] < a[min_idx])
                min_idx = j;
        }
        swap(a[min_idx], a[i]);
    }
}""",
        "C": """void selectionSort(int a[], int n) {
    int i,j,min_idx,tmp;
    for(i=0;i<n-1;i++){
        min_idx=i;
        for(j=i+1;j<n;j++){
            if(a[j]<a[min_idx]) min_idx=j;
        }
        tmp=a[min_idx]; a[min_idx]=a[i]; a[i]=tmp;
    }
}""",
        "BASIC": """FOR I=0 TO N-2
    MIN_IDX=I
    FOR J=I+1 TO N-1
        IF A(J) < A(MIN_IDX) THEN MIN_IDX=J
    NEXT J
    SWAP A(I), A(MIN_IDX)
NEXT I""",
        "Java": """void selectionSort(int a[]) {
    int n=a.length;
    for(int i=0;i<n-1;i++){
        int min_idx=i;
        for(int j=i+1;j<n;j++){
            if(a[j]<a[min_idx]) min_idx=j;
        }
        int tmp=a[min_idx]; a[min_idx]=a[i]; a[i]=tmp;
    }
}""",
        "Pascal": """for i:=0 to High(a)-1 do begin
  min_idx:=i;
  for j:=i+1 to High(a) do
    if a[j] < a[min_idx] then min_idx:=j;
  tmp:=a[min_idx]; a[min_idx]:=a[i]; a[i]:=tmp;
end;"""
    }
    
    def get_steps(self, arr):
        a = arr.copy()
        comparisons = 0
        swaps = 0
        n = len(a)
        
        yield SortStep(a, key=None, sorted_end=-1, code_line=1,
                       explanation="🎯 Kiválasztó kezdés: keresd a minimumot",
                       comparisons=0, shifts=0, pass_num=0)
        
        for i in range(n):
            min_idx = i
            yield SortStep(a, key=None, sorted_end=i-1, highlight_indices=[i], code_line=3,
                           explanation=f"{i+1}. kör: min_idx={i} (a[{i}]={a[i]})",
                           comparisons=comparisons, shifts=swaps, pass_num=i+1,
                           extra={"low": i, "min_idx": min_idx})
            
            for j in range(i+1, n):
                comparisons+=1
                yield SortStep(a, key=None, sorted_end=i-1, highlight_indices=[j, min_idx], code_line=5,
                               explanation=f"Összehasonlít: a[{j}]={a[j]} < a[{min_idx}]={a[min_idx]}?",
                               comparisons=comparisons, shifts=swaps, pass_num=i+1,
                               extra={"low": i, "min_idx": min_idx, "j": j})
                if a[j] < a[min_idx]:
                    min_idx = j
                    yield SortStep(a, key=None, sorted_end=i-1, highlight_indices=[min_idx], code_line=6,
                                   explanation=f"Új minimum: min_idx={min_idx} ({a[min_idx]})",
                                   comparisons=comparisons, shifts=swaps, pass_num=i+1,
                                   extra={"low": i, "min_idx": min_idx, "j": j})
            
            if min_idx != i:
                a[i], a[min_idx] = a[min_idx], a[i]
                swaps+=1
                yield SortStep(a, key=None, sorted_end=i, highlight_indices=[i, min_idx], code_line=7,
                               explanation=f"Csere: a[{i}]↔a[{min_idx}], min a helyére",
                               comparisons=comparisons, shifts=swaps, pass_num=i+1,
                               extra={"low": i, "min_idx": min_idx})
            else:
                yield SortStep(a, key=None, sorted_end=i, highlight_indices=[i], code_line=7,
                               explanation=f"Nincs csere, már a helyén van",
                               comparisons=comparisons, shifts=swaps, pass_num=i+1,
                               extra={"low": i, "min_idx": min_idx})
        
        yield SortStep(a, key=None, sorted_end=n-1, code_line=8,
                       explanation="✅ Kész! Minden minimum a helyére került",
                       comparisons=comparisons, shifts=swaps, pass_num=n)
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
