# -*- coding: utf-8 -*-
from core.config import LANGUAGES

# Minden nyelvhez egy teljes kód sablon magyar kommentekkel
CODE_TEMPLATES = {
    "Python": {
        "insertion_sort": """def beszurasos_rendezes(a):
    # Beszúró rendezés - O(n²)
    for i in range(1, len(a)):
        kulcs = a[i]  # Aktuális kulcs
        j = i - 1
        while j >= 0 and a[j] > kulcs:
            a[j + 1] = a[j]  # Jobbra tolás
            j -= 1
        a[j + 1] = kulcs  # Beillesztés
    return a""",
    },
    "C++": {
        "insertion_sort": """void insertionSort(int a[], int n) {
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
    },
    "C": {
        "insertion_sort": """void insertionSort(int a[], int n) {
    int i, key, j;
    for (i = 1; i < n; i++) {
        key = a[i];
        j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j+1] = a[j];
            j = j - 1;
        }
        a[j+1] = key;
    }
}""",
    },
    "BASIC": {
        "insertion_sort": """' Beszúró rendezés BASIC-ben
FOR I = 1 TO N-1
    KEY = A(I)
    J = I - 1
    WHILE J >= 0 AND A(J) > KEY
        A(J+1) = A(J)
        J = J - 1
    WEND
    A(J+1) = KEY
NEXT I""",
    },
    "Java": {
        "insertion_sort": """class InsertionSort {
    void sort(int a[]) {
        int n = a.length;
        for (int i=1; i<n; ++i) {
            int key = a[i];
            int j = i-1;
            while (j>=0 && a[j] > key) {
                a[j+1] = a[j];
                j = j-1;
            }
            a[j+1] = key;
        }
    }
}""",
    },
    "Pascal": {
        "insertion_sort": """procedure InsertionSort(var a: array of Integer);
var i, j, key: Integer;
begin
  for i:=1 to High(a) do begin
    key := a[i];
    j := i-1;
    while (j>=0) and (a[j] > key) do begin
      a[j+1] := a[j];
      j := j-1;
    end;
    a[j+1] := key;
  end;
end;""",
    }
}

def get_code(lang: str, algo: str) -> str:
    return CODE_TEMPLATES.get(lang, {}).get(algo, "// Hamarosan...")

def get_line_count(lang: str, algo: str) -> int:
    code = get_code(lang, algo)
    return len(code.splitlines())
