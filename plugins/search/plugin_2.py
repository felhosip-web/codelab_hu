# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
import random

class SearchStep:
    def __init__(self, array: List[int], target: int, highlight_indices=None, 
                 code_line=0, explanation="", comparisons=0, found_index=None, extra=None):
        self.array = array.copy()
        self.target = target
        self.highlight = highlight_indices or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.found_index = found_index
        self.extra = extra or {}
        # Kompatibilitás a sort rendszerrel
        self.key = target
        self.sorted_end = -1
        self.shifts = 0
        self.pass_num = comparisons

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
        import random
        target_param = self.params.get("target") if hasattr(self, 'params') else None
        if target_param and target_param in a:
            target = target_param
        else:
            target = random.choice(a) if a else 0
        
        yield SearchStep(a, target, highlight_indices=[], code_line=1,
                         explanation=f"🔍 Lineáris keresés: {target} keresése",
                         comparisons=0, found_index=None,
                         extra={"target": target})
        
        for i in range(len(a)):
            yield SearchStep(a, target, highlight_indices=[i], code_line=3,
                             explanation=f"Vizsgál: a[{i}]={a[i]} == {target}?",
                             comparisons=i+1, found_index=None,
                             extra={"target": target, "current": i, "low": 0, "high": len(a)-1})
            
            if a[i] == target:
                yield SearchStep(a, target, highlight_indices=[i], code_line=4,
                                 explanation=f"✅ Megtalálva! Index: {i}",
                                 comparisons=i+1, found_index=i,
                                 extra={"target": target, "found": i})
                return
        
        yield SearchStep(a, target, highlight_indices=[], code_line=6,
                         explanation=f"❌ Nincs találat: {target} nincs a tömbben",
                         comparisons=len(a), found_index=-1,
                         extra={"target": target})
    
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
        import random
        target_param = self.params.get("target") if hasattr(self, 'params') else None
        if target_param and target_param in a:
            target = target_param
        else:
            target = random.choice(a) if a else 0
        
        low, high = 0, len(a)-1
        comparisons = 0
        
        yield SearchStep(a, target, highlight_indices=[], code_line=2,
                         explanation=f"🎯 Bináris keresés: {target} keresése rendezett tömbben",
                         comparisons=0, found_index=None,
                         extra={"target": target, "low": low, "high": high, "recursion": [(low, high)]})
        
        while low <= high:
            mid = (low + high)//2
            comparisons+=1
            
            yield SearchStep(a, target, highlight_indices=[mid], code_line=4,
                             explanation=f"Felezés: low={low}, high={high}, mid={mid} (a[mid]={a[mid]})",
                             comparisons=comparisons, found_index=None,
                             extra={"target": target, "low": low, "high": high, "mid": mid, "recursion": [(low, high)]})
            
            if a[mid] == target:
                yield SearchStep(a, target, highlight_indices=[mid], code_line=6,
                                 explanation=f"✅ Megtalálva! a[{mid}]={target}",
                                 comparisons=comparisons, found_index=mid,
                                 extra={"target": target, "low": low, "high": high, "mid": mid, "found": mid})
                return
            elif a[mid] < target:
                yield SearchStep(a, target, highlight_indices=list(range(mid+1, high+1)), code_line=8,
                                 explanation=f"{a[mid]} < {target}, jobbra megyünk",
                                 comparisons=comparisons, found_index=None,
                                 extra={"target": target, "low": mid+1, "high": high, "mid": mid})
                low = mid + 1
            else:
                yield SearchStep(a, target, highlight_indices=list(range(low, mid)), code_line=10,
                                 explanation=f"{a[mid]} > {target}, balra megyünk",
                                 comparisons=comparisons, found_index=None,
                                 extra={"target": target, "low": low, "high": mid-1, "mid": mid})
                high = mid - 1
        
        yield SearchStep(a, target, highlight_indices=[], code_line=11,
                         explanation=f"❌ Nincs találat: {target}",
                         comparisons=comparisons, found_index=-1,
                         extra={"target": target})
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
