# -*- coding: utf-8 -*-
"""
Algoritmus motor - generátoros lépések, hogy szinkronban legyen a vizualizációval
"""
from typing import List, Dict, Generator

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

def insertion_sort_steps(arr: List[int]) -> Generator[SortStep, None, None]:
    """Insertion sort lépések generátora magyar magyarázatokkal"""
    a = arr.copy()
    comparisons = 0
    shifts = 0
    n = len(a)
    
    yield SortStep(a, key=None, sorted_end=0, code_line=1,
                   explanation="Kezdés: az első elem már rendezettnek számít.",
                   comparisons=0, shifts=0, pass_num=0)
    
    for i in range(1, n):
        key = a[i]
        j = i - 1
        
        yield SortStep(a, key=key, sorted_end=i-1, highlight_indices=[i],
                       code_line=3, explanation=f"Kulcs kiválasztása: key = {key} (i={i})",
                       comparisons=comparisons, shifts=shifts, pass_num=i)
        
        while j >= 0 and a[j] > key:
            comparisons += 1
            a[j+1] = a[j]
            shifts += 1
            yield SortStep(a, key=key, sorted_end=i-1, highlight_indices=[j, j+1],
                           code_line=5, explanation=f"Eltolás: a[{j}]={a[j]} > kulcs({key}), jobbra csúsztat",
                           comparisons=comparisons, shifts=shifts, pass_num=i)
            j -= 1
            if j >=0:
                yield SortStep(a, key=key, sorted_end=i-1, highlight_indices=[j],
                               code_line=4, explanation=f"j csökkentése: j={j}",
                               comparisons=comparisons, shifts=shifts, pass_num=i)
        
        if j < 0:
            yield SortStep(a, key=key, sorted_end=i-1, highlight_indices=[],
                           code_line=4, explanation="j < 0 → megáll, elejére értünk",
                           comparisons=comparisons, shifts=shifts, pass_num=i)
        
        a[j+1] = key
        yield SortStep(a, key=None, sorted_end=i, highlight_indices=[j+1],
                       code_line=8, explanation=f"Beillesztés: a[{j+1}] = kulcs ({key})",
                       comparisons=comparisons, shifts=shifts, pass_num=i)

# Későbbi bővítéshez helyőrzők
def bubble_sort_steps(arr): pass
def quick_sort_steps(arr): pass
