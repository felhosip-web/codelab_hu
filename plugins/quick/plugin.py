# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

class QuickSortPlugin(AlgorithmPluginBase):
    id = "quick_sort"
    name = "Gyors rendezés"
    description = "Oszd meg és uralkodj! Pivot + particionálás"
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    icon = "⚡"
    
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
        "Python": """def gyors_rendezes(a, low=0, high=None):
    if high is None:
        high = len(a)-1
    if low < high:
        # Particionálás - pivot helyére tesz
        pi = particional(a, low, high)
        # Rekurzívan a két fél
        gyors_rendezes(a, low, pi-1)
        gyors_rendezes(a, pi+1, high)

def particional(a, low, high):
    pivot = a[high]  # Utolsó mint pivot
    i = low - 1
    for j in range(low, high):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i+1], a[high] = a[high], a[i+1]
    return i+1""",
        "C++": """int partition(int a[], int low, int high) {
    int pivot = a[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (a[j] <= pivot) {
            i++;
            swap(a[i], a[j]);
        }
    }
    swap(a[i+1], a[high]);
    return i+1;
}

void quickSort(int a[], int low, int high) {
    if (low < high) {
        int pi = partition(a, low, high);
        quickSort(a, low, pi-1);
        quickSort(a, pi+1, high);
    }
}""",
        "C": """int partition(int a[], int low, int high) {
    int pivot = a[high], i = low-1, tmp;
    for (int j=low; j<high; j++) {
        if (a[j] <= pivot) {
            i++;
            tmp=a[i]; a[i]=a[j]; a[j]=tmp;
        }
    }
    tmp=a[i+1]; a[i+1]=a[high]; a[high]=tmp;
    return i+1;
}
void quickSort(int a[], int low, int high) {
    if (low < high) {
        int pi = partition(a, low, high);
        quickSort(a, low, pi-1);
        quickSort(a, pi+1, high);
    }
}""",
        "BASIC": """FUNCTION Partition(a(), low, high)
    pivot = a(high): i = low-1
    FOR j = low TO high-1
        IF a(j) <= pivot THEN
            i = i+1: SWAP a(i), a(j)
        END IF
    NEXT j
    SWAP a(i+1), a(high)
    Partition = i+1
END FUNCTION

SUB QuickSort(a(), low, high)
    IF low < high THEN
        pi = Partition(a(), low, high)
        QuickSort a(), low, pi-1
        QuickSort a(), pi+1, high
    END IF
END SUB""",
        "Java": """int partition(int a[], int low, int high) {
    int pivot = a[high];
    int i = low-1;
    for (int j=low; j<high; j++) {
        if (a[j] <= pivot) {
            i++;
            int tmp=a[i]; a[i]=a[j]; a[j]=tmp;
        }
    }
    int tmp=a[i+1]; a[i+1]=a[high]; a[high]=tmp;
    return i+1;
}
void quickSort(int a[], int low, int high) {
    if (low < high) {
        int pi = partition(a, low, high);
        quickSort(a, low, pi-1);
        quickSort(a, pi+1, high);
    }
}""",
        "Pascal": """function Partition(var a: array of Integer; low, high: Integer): Integer;
var pivot, i, j, tmp: Integer;
begin
  pivot:=a[high]; i:=low-1;
  for j:=low to high-1 do
    if a[j] <= pivot then begin
      Inc(i);
      tmp:=a[i]; a[i]:=a[j]; a[j]:=tmp;
    end;
  tmp:=a[i+1]; a[i+1]:=a[high]; a[high]:=tmp;
  Result:=i+1;
end;

procedure QuickSort(var a: array of Integer; low, high: Integer);
var pi: Integer;
begin
  if low < high then begin
    pi:=Partition(a, low, high);
    QuickSort(a, low, pi-1);
    QuickSort(a, pi+1, high);
  end;
end;"""
    }
    
    def get_steps(self, arr):
        a = arr.copy()
        comparisons = 0
        swaps = 0
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=-1, code_line=1,
            explanation="⚡ Gyors rendezés kezdés: oszd meg és uralkodj!",
            metrics={"comparisons": 0, "swaps": 0, "pass_num": 0},
            extra={"recursion": [(0, len(a)-1)], "pivot": None}
        )
        
        stack = [(0, len(a)-1, 0)]  # (low, high, depth)
        
        while stack:
            low, high, depth = stack.pop()
            
            if low >= high:
                continue
            
            pivot = a[high]
            yield VisualizationStep(
                array=a, key=pivot, sorted_end=-1, highlight=[high], code_line=12,
                explanation=f"Pivot választás: a[{high}]={pivot} (depth {depth})",
                metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": depth},
                extra={"pivot": high, "low": low, "high": high, "recursion": [(l,h) for l,h,_ in stack] + [(low, high)]}
            )
            
            i = low - 1
            for j in range(low, high):
                comparisons += 1
                yield VisualizationStep(
                    array=a, key=pivot, sorted_end=-1, highlight=[j, high], code_line=15,
                    explanation=f"Vizsgál: a[{j}]={a[j]} <= pivot {pivot}? (i={i})",
                    metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": depth},
                    extra={"pivot": high, "low": low, "high": high, "i": i, "j": j, "recursion": [(l,h) for l,h,_ in stack]}
                )
                
                if a[j] <= pivot:
                    i += 1
                    if i != j:
                        a[i], a[j] = a[j], a[i]
                        swaps += 1
                        yield VisualizationStep(
                            array=a, key=pivot, sorted_end=-1, highlight=[i, j], code_line=17,
                            explanation=f"Csere: a[{i}]↔a[{j}], i={i} növelve",
                            metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": depth},
                            extra={"pivot": high, "low": low, "high": high, "i": i, "j": j, "recursion": [(l,h) for l,h,_ in stack]}
                        )
            
            a[i+1], a[high] = a[high], a[i+1]
            swaps += 1
            pi = i+1
            
            yield VisualizationStep(
                array=a, key=None, sorted_end=-1, highlight=[pi], code_line=18,
                explanation=f"✅ Pivot a helyén: index {pi}, érték {a[pi]}. Két részre bontunk.",
                metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": depth},
                extra={"pivot": pi, "low": low, "high": high, "partition": pi, "recursion": [(l,h) for l,h,_ in stack] + [(low, pi-1), (pi+1, high)]}
            )
            
            stack.append((pi+1, high, depth+1))
            stack.append((low, pi-1, depth+1))
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=len(a)-1, highlight=[], code_line=19,
            explanation="✅ Kész! Minden partíció rendezve.",
            metrics={"comparisons": comparisons, "swaps": swaps, "pass_num": 0},
            extra={"recursion": [], "pivot": None}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
