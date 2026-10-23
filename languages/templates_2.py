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
        "bubble_sort": """def buborek_rendezes(a):
    # Buborék rendezés - O(n²) - nagyok buborékolnak fel
    n = len(a)
    for i in range(n):
        cserelt = False
        for j in range(0, n-i-1):
            if a[j] > a[j+1]:  # Ha rossz sorrend
                a[j], a[j+1] = a[j+1], a[j]
                cserelt = True
        if not cserelt:  # Ha nem volt csere, kész
            break
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
        "bubble_sort": """void bubbleSort(int a[], int n) {
    for (int i = 0; i < n-1; i++) {
        bool swapped = false;
        for (int j = 0; j < n-i-1; j++) {
            if (a[j] > a[j+1]) {
                swap(a[j], a[j+1]);
                swapped = true;
            }
        }
        if (!swapped) break; // Már rendezett
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
        "bubble_sort": """void bubbleSort(int a[], int n) {
    int i, j, tmp;
    for (i = 0; i < n-1; i++) {
        int swapped = 0;
        for (j = 0; j < n-i-1; j++) {
            if (a[j] > a[j+1]) {
                tmp = a[j]; a[j] = a[j+1]; a[j+1] = tmp;
                swapped = 1;
            }
        }
        if (!swapped) break;
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
        "bubble_sort": """' Buborék rendezés BASIC-ben
FOR I = 0 TO N-2
    SWAPPED = 0
    FOR J = 0 TO N-I-2
        IF A(J) > A(J+1) THEN
            SWAP A(J), A(J+1)
            SWAPPED = 1
        END IF
    NEXT J
    IF SWAPPED = 0 THEN EXIT FOR
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
        "bubble_sort": """class BubbleSort {
    void sort(int a[]) {
        int n = a.length;
        for (int i=0; i<n-1; i++) {
            boolean swapped = false;
            for (int j=0; j<n-i-1; j++) {
                if (a[j] > a[j+1]) {
                    int tmp = a[j];
                    a[j] = a[j+1];
                    a[j+1] = tmp;
                    swapped = true;
                }
            }
            if (!swapped) break;
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
        "bubble_sort": """procedure BubbleSort(var a: array of Integer);
var i, j, tmp: Integer;
    swapped: Boolean;
begin
  for i:=0 to High(a)-1 do begin
    swapped := False;
    for j:=0 to High(a)-i-1 do begin
      if a[j] > a[j+1] then begin
        tmp := a[j]; a[j] := a[j+1]; a[j+1] := tmp;
        swapped := True;
      end;
    end;
    if not swapped then Break;
  end;
end;""",
    }
}

def get_code(lang: str, algo: str) -> str:
    return CODE_TEMPLATES.get(lang, {}).get(algo, "// Hamarosan...")

def get_line_count(lang: str, algo: str) -> int:
    code = get_code(lang, algo)
    return len(code.splitlines())
