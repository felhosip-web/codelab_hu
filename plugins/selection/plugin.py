# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

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
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=-1, code_line=1,
            explanation="🎯 Kiválasztó kezdés: keresd a minimumot",
            metrics={"comparisons": 0, "swaps": 0, "pass_num": 0}
        )
        
        for i in range(n):
            min_idx = i
            yield VisualizationStep(
                array=a, key=None, sorted_end=i-1, highlight=[i], code_line=4,
                explanation=f"{i+1}. kör: min_idx={i} (a[{i}]={a[i]})",
                metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": i+1},
                extra={"low": i, "min_idx": min_idx}
            )
            
            for j in range(i+1, n):
                comparisons += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=i-1, highlight=[j, min_idx], code_line=6,
                    explanation=f"Összehasonlít: a[{j}]={a[j]} < a[{min_idx}]={a[min_idx]}?",
                    metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": i+1},
                    extra={"low": i, "min_idx": min_idx, "j": j}
                )
                if a[j] < a[min_idx]:
                    min_idx = j
                    yield VisualizationStep(
                        array=a, key=None, sorted_end=i-1, highlight=[min_idx], code_line=7,
                        explanation=f"Új minimum: min_idx={min_idx} ({a[min_idx]})",
                        metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": i+1},
                        extra={"low": i, "min_idx": min_idx, "j": j}
                    )
            
            if min_idx != i:
                a[i], a[min_idx] = a[min_idx], a[i]
                swaps += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=i, highlight=[i, min_idx], code_line=8,
                    explanation=f"Csere: a[{i}]↔a[{min_idx}], min a helyére",
                    metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": i+1},
                    extra={"low": i, "min_idx": min_idx}
                )
            else:
                yield VisualizationStep(
                    array=a, key=None, sorted_end=i, highlight=[i], code_line=8,
                    explanation="Nincs csere, már a helyén van",
                    metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": i+1},
                    extra={"low": i, "min_idx": min_idx}
                )
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=n-1, code_line=9,
            explanation="✅ Kész! Minden minimum a helyére került",
            metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": n}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
