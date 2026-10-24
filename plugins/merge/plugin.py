# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

class MergeSortPlugin(AlgorithmPluginBase):
    id = "merge_sort"
    name = "Egyesítő rendezés"
    description = "Oszd ketté, rendezd, egyesítsd - stabil"
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    icon = "🔀"
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
        "Python": """def egyesito_rendezes(a):
    if len(a) > 1:
        mid = len(a)//2
        bal = a[:mid]
        jobb = a[mid:]
        egyesito_rendezes(bal)
        egyesito_rendezes(jobb)
        i = j = k = 0
        while i < len(bal) and j < len(jobb):
            if bal[i] < jobb[j]:
                a[k] = bal[i]; i+=1
            else:
                a[k] = jobb[j]; j+=1
            k+=1
        while i < len(bal):
            a[k]=bal[i]; i+=1; k+=1
        while j < len(jobb):
            a[k]=jobb[j]; j+=1; k+=1
    return a""",
        "C++": """void merge(int a[], int l, int m, int r) {
    int n1 = m-l+1, n2 = r-m;
    int L[n1], R[n2];
    for(int i=0;i<n1;i++) L[i]=a[l+i];
    for(int j=0;j<n2;j++) R[j]=a[m+1+j];
    int i=0,j=0,k=l;
    while(i<n1 && j<n2) {
        if(L[i]<=R[j]) a[k++]=L[i++];
        else a[k++]=R[j++];
    }
    while(i<n1) a[k++]=L[i++];
    while(j<n2) a[k++]=R[j++];
}
void mergeSort(int a[], int l, int r) {
    if(l<r) {
        int m = l+(r-l)/2;
        mergeSort(a,l,m);
        mergeSort(a,m+1,r);
        merge(a,l,m,r);
    }
}""",
        "C": """void merge(int a[], int l, int m, int r) {
    int n1=m-l+1, n2=r-m, i,j,k;
    int L[n1], R[n2];
    for(i=0;i<n1;i++) L[i]=a[l+i];
    for(j=0;j<n2;j++) R[j]=a[m+1+j];
    i=0; j=0; k=l;
    while(i<n1 && j<n2) {
        if(L[i]<=R[j]) a[k++]=L[i++];
        else a[k++]=R[j++];
    }
    while(i<n1) a[k++]=L[i++];
    while(j<n2) a[k++]=R[j++];
}
void mergeSort(int a[], int l, int r) {
    if(l<r){int m=l+(r-l)/2; mergeSort(a,l,m); mergeSort(a,m+1,r); merge(a,l,m,r);}
}""",
        "BASIC": """SUB Merge(a(), l, m, r)
    n1=m-l+1: n2=r-m
    DIM L(n1), R(n2)
    FOR i=0 TO n1-1: L(i)=a(l+i): NEXT
    FOR j=0 TO n2-1: R(j)=a(m+1+j): NEXT
    i=0: j=0: k=l
    WHILE i<n1 AND j<n2
        IF L(i)<=R(j) THEN a(k)=L(i): i=i+1 ELSE a(k)=R(j): j=j+1
        k=k+1
    WEND
    WHILE i<n1: a(k)=L(i): i=i+1: k=k+1: WEND
    WHILE j<n2: a(k)=R(j): j=j+1: k=k+1: WEND
END SUB
SUB MergeSort(a(), l, r)
    IF l<r THEN m=l+(r-l)/2: MergeSort a(),l,m: MergeSort a(),m+1,r: Merge a(),l,m,r
END SUB""",
        "Java": """void merge(int a[], int l, int m, int r) {
    int n1=m-l+1, n2=r-m;
    int L[]=new int[n1], R[]=new int[n2];
    for(int i=0;i<n1;i++) L[i]=a[l+i];
    for(int j=0;j<n2;j++) R[j]=a[m+1+j];
    int i=0,j=0,k=l;
    while(i<n1 && j<n2) {
        if(L[i]<=R[j]) a[k++]=L[i++];
        else a[k++]=R[j++];
    }
    while(i<n1) a[k++]=L[i++];
    while(j<n2) a[k++]=R[j++];
}
void sort(int a[], int l, int r) {
    if(l<r){int m=l+(r-l)/2; sort(a,l,m); sort(a,m+1,r); merge(a,l,m,r);}
}""",
        "Pascal": """procedure Merge(var a: array of Integer; l,m,r: Integer);
var n1,n2,i,j,k: Integer; L,R: array of Integer;
begin
  n1:=m-l+1; n2:=r-m; SetLength(L,n1); SetLength(R,n2);
  for i:=0 to n1-1 do L[i]:=a[l+i];
  for j:=0 to n2-1 do R[j]:=a[m+1+j];
  i:=0; j:=0; k:=l;
  while (i<n1) and (j<n2) do begin
    if L[i]<=R[j] then begin a[k]:=L[i]; Inc(i); end else begin a[k]:=R[j]; Inc(j); end;
    Inc(k);
  end;
  while i<n1 do begin a[k]:=L[i]; Inc(i); Inc(k); end;
  while j<n2 do begin a[k]:=R[j]; Inc(j); Inc(k); end;
end;
procedure MergeSort(var a: array of Integer; l,r: Integer);
var m: Integer;
begin
  if l<r then begin m:=l+(r-l) div 2; MergeSort(a,l,m); MergeSort(a,m+1,r); Merge(a,l,m,r); end;
end;"""
    }
    
    def get_steps(self, arr):
        a = arr.copy()
        comparisons = 0
        merges = 0
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=-1, code_line=1,
            explanation="🔀 Egyesítő kezdés: oszd ketté rekurzívan",
            metrics={"comparisons": 0, "shifts": 0, "pass_num": 0},
            extra={"recursion": [(0, len(a)-1)]}
        )
        
        def merge_sort_recursive(a, l, r, depth):
            nonlocal comparisons, merges
            if l >= r:
                return
            
            m = l + (r - l)//2
            
            yield VisualizationStep(
                array=a, key=None, sorted_end=-1, highlight=list(range(l, r+1)), code_line=3,
                explanation=f"Osztás: [{l},{r}] -> [{l},{m}] és [{m+1},{r}] (depth {depth})",
                metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                extra={"low": l, "high": r, "mid": m, "recursion": [(l,m), (m+1,r)]}
            )
            
            yield from merge_sort_recursive(a, l, m, depth+1)
            yield from merge_sort_recursive(a, m+1, r, depth+1)
            
            yield VisualizationStep(
                array=a, key=None, sorted_end=-1, highlight=list(range(l, r+1)), code_line=8,
                explanation=f"Egyesítés: [{l},{m}] + [{m+1},{r}]",
                metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                extra={"low": l, "high": r, "mid": m}
            )
            
            n1 = m - l + 1
            n2 = r - m
            L = a[l:m+1]
            R = a[m+1:r+1]
            i = j = 0
            k = l
            
            while i < n1 and j < n2:
                comparisons += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=-1, highlight=[l+i, m+1+j], code_line=10,
                    explanation=f"Összehasonlít: {L[i]} vs {R[j]}",
                    metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                    extra={"low": l, "high": r, "mid": m, "i": i, "j": j}
                )
                if L[i] <= R[j]:
                    a[k] = L[i]
                    i += 1
                    code_line_write = 11
                else:
                    a[k] = R[j]
                    j += 1
                    code_line_write = 13
                merges += 1
                k += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=-1, highlight=[k-1], code_line=code_line_write,
                    explanation=f"Beír: a[{k-1}]={a[k-1]}",
                    metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                    extra={"low": l, "high": r}
                )
            
            while i < n1:
                a[k] = L[i]
                i += 1
                k += 1
                merges += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=-1, highlight=[k-1], code_line=16,
                    explanation=f"Maradék balból: a[{k-1}]={a[k-1]}",
                    metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                    extra={"low": l, "high": r}
                )
            while j < n2:
                a[k] = R[j]
                j += 1
                k += 1
                merges += 1
                yield VisualizationStep(
                    array=a, key=None, sorted_end=-1, highlight=[k-1], code_line=18,
                    explanation=f"Maradék jobból: a[{k-1}]={a[k-1]}",
                    metrics={"comparisons": comparisons, "shifts": merges, "pass_num": depth},
                    extra={"low": l, "high": r}
                )
        
        yield from merge_sort_recursive(a, 0, len(a)-1, 0)
        
        yield VisualizationStep(
            array=a, key=None, sorted_end=len(a)-1, code_line=19,
            explanation="✅ Kész! Egyesítve és rendezve",
            metrics={"comparisons": comparisons, "shifts": merges, "pass_num": 0},
            extra={"recursion": []}
        )
    
    def get_code(self, language: str) -> str:
        return self.codes.get(language, self.codes["Python"])
