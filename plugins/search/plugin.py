# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
import random

class LinearSearchPlugin(AlgorithmPluginBase):
    id = "linear_search"
    name = "Lineáris keresés"
    description = "Végigmegy minden elemen, amíg meg nem találja"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    icon = "🔍"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "search"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("array_size", "Tömb méret", "int", 12, 5, 20))
        self.params.add(Param("max_value", "Max érték", "int", 50, 10, 100))
        self.params.add(Param("target", "Keresett érték", "int", 25, 1, 50, description="Ha nincs, random választ"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    
    def generate_input(self, params_dict=None):
        size = self.params.get("array_size")
        max_v = self.params.get("max_value")
        arr = sorted([random.randint(1, max_v) for _ in range(size)])
        return arr
    

    codes = {
        "Python": """def linearis_kereses(a, cel):
    # Lineáris keresés - O(n)
    for i in range(len(a)):
        if a[i] == cel:  # Megtaláltuk?
            return i  # Index vissza
    return -1  # Nincs benne""",
        "C++": """int linearSearch(int a[], int n, int target) {
    for (int i=0; i<n; i++) {
        if (a[i] == target)
            return i;
    }
    return -1;
}""",
        "C": """int linearSearch(int a[], int n, int target) {
    int i;
    for(i=0;i<n;i++){
        if(a[i]==target) return i;
    }
    return -1;
}""",
        "BASIC": """FUNCTION LinearSearch(a(), target)
    FOR i=0 TO N-1
        IF a(i)=target THEN
            LinearSearch=i: EXIT FUNCTION
        END IF
    NEXT i
    LinearSearch=-1
END FUNCTION""",
        "Java": """int linearSearch(int a[], int target) {
    for(int i=0;i<a.length;i++){
        if(a[i]==target) return i;
    }
    return -1;
}""",
        "Pascal": """function LinearSearch(a: array of Integer; target: Integer): Integer;
var i: Integer;
begin
  for i:=0 to High(a) do
    if a[i]=target then Exit(i);
  Result:=-1;
end;"""
    }
    
    def get_steps(self, arr):
        a = sorted(arr)
        target = random.choice(a) if a else 0
        
        yield VisualizationStep(
            array=a, key=target, sorted_end=-1, highlight=[], code_line=1,
            explanation=f"🔍 Lineáris keresés: {target} keresése",
            metrics={"comparisons": 0, "pass_num": 0},
            extra={"target": target}
        )
        
        for i in range(len(a)):
            yield VisualizationStep(
                array=a, key=target, sorted_end=-1, highlight=[i], code_line=4,
                explanation=f"Vizsgál: a[{i}]={a[i]} == {target}?",
                metrics={"comparisons": i+1, "pass_num": i+1},
                extra={"target": target, "current": i, "low": 0, "high": len(a)-1}
            )
            
            if a[i] == target:
                yield VisualizationStep(
                    array=a, key=target, sorted_end=-1, highlight=[i], code_line=5,
                    explanation=f"✅ Megtalálva! Index: {i}",
                    metrics={"comparisons": i+1, "pass_num": i+1},
                    extra={"target": target, "found": i}
                )
                return
        
        yield VisualizationStep(
            array=a, key=target, sorted_end=-1, highlight=[], code_line=6,
            explanation=f"❌ Nincs találat: {target} nincs a tömbben",
            metrics={"comparisons": len(a), "pass_num": len(a)},
            extra={"target": target}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])

class BinarySearchPlugin(AlgorithmPluginBase):
    id = "binary_search"
    name = "Bináris keresés"
    description = "Felezéses keresés rendezett tömbben - nagyon gyors"
    time_complexity = "O(log n)"
    space_complexity = "O(1)"
    icon = "🎯"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "search"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("array_size", "Tömb méret", "int", 12, 5, 20))
        self.params.add(Param("max_value", "Max érték", "int", 50, 10, 100))
        self.params.add(Param("target", "Keresett érték", "int", 25, 1, 50, description="Ha nincs, random választ"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    
    def generate_input(self, params_dict=None):
        size = self.params.get("array_size")
        max_v = self.params.get("max_value")
        arr = sorted([random.randint(1, max_v) for _ in range(size)])
        return arr
    

    codes = {
        "Python": """def binaris_kereses(a, cel):
    # Bináris keresés - csak rendezett tömbben! O(log n)
    low, high = 0, len(a)-1
    while low <= high:
        mid = (low + high)//2
        if a[mid] == cel:
            return mid
        elif a[mid] < cel:
            low = mid + 1  # Jobb fele
        else:
            high = mid - 1  # Bal fele
    return -1""",
        "C++": """int binarySearch(int a[], int n, int target) {
    int low=0, high=n-1;
    while(low <= high) {
        int mid = (low+high)/2;
        if(a[mid]==target) return mid;
        else if(a[mid] < target) low=mid+1;
        else high=mid-1;
    }
    return -1;
}""",
        "C": """int binarySearch(int a[], int n, int target) {
    int low=0, high=n-1, mid;
    while(low<=high){
        mid=(low+high)/2;
        if(a[mid]==target) return mid;
        else if(a[mid]<target) low=mid+1;
        else high=mid-1;
    }
    return -1;
}""",
        "BASIC": """FUNCTION BinarySearch(a(), target)
    low=0: high=N-1
    WHILE low <= high
        mid=(low+high)/2
        IF a(mid)=target THEN BinarySearch=mid: EXIT FUNCTION
        ELSE IF a(mid) < target THEN low=mid+1 ELSE high=mid-1
    WEND
    BinarySearch=-1
END FUNCTION""",
        "Java": """int binarySearch(int a[], int target) {
    int low=0, high=a.length-1;
    while(low<=high){
        int mid=(low+high)/2;
        if(a[mid]==target) return mid;
        else if(a[mid]<target) low=mid+1;
        else high=mid-1;
    }
    return -1;
}""",
        "Pascal": """function BinarySearch(a: array of Integer; target: Integer): Integer;
var low,high,mid: Integer;
begin
  low:=0; high:=High(a);
  while low<=high do begin
    mid:=(low+high) div 2;
    if a[mid]=target then Exit(mid)
    else if a[mid]<target then low:=mid+1 else high:=mid-1;
  end;
  Result:=-1;
end;"""
    }
    
    def get_steps(self, arr):
        a = sorted(arr)
        target = random.choice(a) if a else 0
        low, high = 0, len(a)-1
        comparisons = 0
        
        yield VisualizationStep(
            array=a, key=target, sorted_end=-1, highlight=[], code_line=3,
            explanation=f"🎯 Bináris keresés: {target} keresése rendezett tömbben",
            metrics={"comparisons": 0, "pass_num": 0},
            extra={"target": target, "low": low, "high": high, "recursion": [(low, high)]}
        )
        
        while low <= high:
            mid = (low + high)//2
            comparisons += 1
            
            yield VisualizationStep(
                array=a, key=target, sorted_end=-1, highlight=[mid], code_line=6,
                explanation=f"Felezés: low={low}, high={high}, mid={mid} (a[mid]={a[mid]})",
                metrics={"comparisons": comparisons, "pass_num": comparisons},
                extra={"target": target, "low": low, "high": high, "mid": mid, "recursion": [(low, high)]}
            )
            
            if a[mid] == target:
                yield VisualizationStep(
                    array=a, key=target, sorted_end=-1, highlight=[mid], code_line=7,
                    explanation=f"✅ Megtalálva! a[{mid}]={target}",
                    metrics={"comparisons": comparisons, "pass_num": comparisons},
                    extra={"target": target, "low": low, "high": high, "mid": mid, "found": mid}
                )
                return
            elif a[mid] < target:
                yield VisualizationStep(
                    array=a, key=target, sorted_end=-1, highlight=list(range(mid+1, high+1)), code_line=9,
                    explanation=f"{a[mid]} < {target}, jobbra megyünk",
                    metrics={"comparisons": comparisons, "pass_num": comparisons},
                    extra={"target": target, "low": mid+1, "high": high, "mid": mid}
                )
                low = mid + 1
            else:
                yield VisualizationStep(
                    array=a, key=target, sorted_end=-1, highlight=list(range(low, mid)), code_line=11,
                    explanation=f"{a[mid]} > {target}, balra megyünk",
                    metrics={"comparisons": comparisons, "pass_num": comparisons},
                    extra={"target": target, "low": low, "high": mid-1, "mid": mid}
                )
                high = mid - 1
        
        yield VisualizationStep(
            array=a, key=target, sorted_end=-1, highlight=[], code_line=12,
            explanation=f"❌ Nincs találat: {target}",
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            extra={"target": target}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
