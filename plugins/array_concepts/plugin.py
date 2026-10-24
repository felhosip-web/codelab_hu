# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.array_concepts import ArrayConcepts, PointerSim
import random

class ArrayStep(VisualizationStep):
    def __init__(self, array=None, array_2d=None, jagged=None,
                 pointers=None, memory=None,
                 current_index=None, current_value=None,
                 pointer_name=None, target=None,
                 code_line=0, explanation="", comparisons=0, extra=None):
        arr = array or []
        e_dict = extra.copy() if extra else {}
        e_dict.update({
            "array": arr, "array_2d": array_2d, "matrix": array_2d, "jagged": jagged,
            "pointers": pointers or {}, "memory": memory or {},
            "current_index": current_index, "current_value": current_value,
            "pointer_name": pointer_name, "target": target
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=arr,
            highlight=[current_index] if current_index is not None else [],
            key=current_value,
            extra=e_dict
        )

class ArrayBasicsPlugin(AlgorithmPluginBase):
    id = "array_basics"
    name = "Tömb alapok"
    description = "Tömb létrehozás, indexelés, bejárás, memória"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "📦"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("size", "Tömb méret", "int", 8, 3, 12))
        self.params.add(Param("max_val", "Max érték", "int", 20, 5, 50))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Tömb alapok Pythonban
# Létrehozás
tomb = [5, 2, 8, 1, 9]  # 5 elem, index 0..4
# Vagy dinamikusan
tomb = [random.randint(1,20) for _ in range(8)]

# Indexelés - O(1)
elso = tomb[0]      # 5
utolso = tomb[-1]   # 9 vagy tomb[4]
masodik = tomb[1]   # 2

# Bejárás
for i in range(len(tomb)):
    print(f"tomb[{i}] = {tomb[i]}")

# For-each
for ertek in tomb:
    print(ertek)

# Módosítás
tomb[2] = 10  # 8 -> 10

# Hozzáadás (dinamikus)
tomb.append(7)  # Végére

# Memória: folytonos, 4 byte * méret
# Cím: base + index*4
""",
        "C++": "// Tömb C++\nint tomb[5] = {5,2,8,1,9}; // Statikus, stack\nint* dinamikus = new int[8]; // Dinamikus, heap\n// Indexelés O(1)\nint elso = tomb[0];\nint utolso = tomb[4];\n// Bejárás\nfor(int i=0;i<5;i++) cout << \"tomb[\" << i << \"]=\" << tomb[i] << endl;\n// Pointer aritmetika: tomb[i] == *(tomb+i)\n// Módosítás\ntomb[2]=10;\n// Memória: folytonos\n// delete[] dinamikus;",
        "C": "/* Tömb C */\nint tomb[5] = {5,2,8,1,9}; // Stack\nint* dinamikus = malloc(8*sizeof(int)); // Heap\nint elso = tomb[0];\nint utolso = tomb[4];\nfor(int i=0;i<5;i++) printf(\"tomb[%d]=%d\\n\", i, tomb[i]);\ntomb[2]=10;\n// tomb[i] == *(tomb+i)\n// Cím: tomb + i*4\nfree(dinamikus);",
        "BASIC": "DIM tomb(5) AS INTEGER: tomb(0)=5: tomb(1)=2: tomb(2)=8: tomb(3)=1: tomb(4)=9\nelso=tomb(0)\nutolso=tomb(4)\nFOR i=0 TO 4: PRINT \"tomb(\";i;\")=\";tomb(i): NEXT\ntomb(2)=10",
        "Java": "// Tömb Java\nint[] tomb = {5,2,8,1,9};\nint[] dinamikus = new int[8];\nint elso = tomb[0];\nint utolso = tomb[tomb.length-1];\nfor(int i=0;i<tomb.length;i++) System.out.println(\"tomb[\"+i+\"]=\"+tomb[i]);\nfor(int ertek: tomb) System.out.println(ertek);\ntomb[2]=10;\n// Memória: heap, referencia\n// tomb.length",
        "Pascal": "var tomb: array[0..4] of Integer; i: Integer; begin tomb[0]:=5; tomb[1]:=2; tomb[2]:=8; tomb[3]:=1; tomb[4]:=9; elso:=tomb[0]; utolso:=tomb[4]; for i:=0 to 4 do WriteLn('tomb[',i,']=',tomb[i]); tomb[2]:=10; end;"
    }
    
    def get_steps(self, arr):
        size = self.params.get("size")
        max_val = self.params.get("max_val")
        array = ArrayConcepts.create_array(size, max_val)
        
        yield ArrayStep(array=array, code_line=2,
                        explanation=f"📦 Tömb létrehozás: {size} elem, max {max_val}",
                        comparisons=0, extra={"phase": "letrehozas", "size": size, "array": array})
        
        for i in range(len(array)):
            yield ArrayStep(array=array, current_index=i, current_value=array[i], code_line=8,
                            explanation=f"Indexelés O(1): tomb[{i}] = {array[i]} | Cím: base + {i}*4 = {1000+i*4}",
                            comparisons=i+1, extra={"phase": "index", "index": i, "value": array[i], "address": 1000+i*4, "array": array})
        
        # Módosítás
        if len(array)>2:
            old = array[2]
            array[2] = random.randint(1, max_val)
            yield ArrayStep(array=array, current_index=2, current_value=array[2], code_line=20,
                            explanation=f"Módosítás: tomb[2] = {old} -> {array[2]}",
                            comparisons=len(array)+1, extra={"phase": "modositas", "index": 2, "old": old, "new": array[2], "array": array})
        
        yield ArrayStep(array=array, code_line=23,
                        explanation=f"✅ Tömb kész: {array} | Memória: {size*4} byte folytonos",
                        comparisons=len(array)+2, extra={"phase": "kesz", "array": array})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class Array2DPlugin(AlgorithmPluginBase):
    id = "array_2d"
    name = "2D tömb - Mátrix"
    description = "Mátrix, sor/oszlop, 2D indexelés, memória sorfolytonos"
    time_complexity = "O(n*m)"
    space_complexity = "O(n*m)"
    icon = "🔢"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("rows", "Sorok", "int", 3, 2, 5))
        self.params.add(Param("cols", "Oszlopok", "int", 4, 2, 6))
        self.params.add(Param("max_val", "Max érték", "int", 20, 5, 50))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# 2D tömb - Mátrix Pythonban
# Létrehozás
matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
]  # 3 sor, 4 oszlop

# Dinamikus
rows, cols = 3, 4
matrix = [[random.randint(1,20) for _ in range(cols)] for _ in range(rows)]

# Indexelés
elso = matrix[0][0]  # 1
masodik_sor_harmadik = matrix[1][2]  # 7

# Bejárás - soronként
for i in range(rows):
    for j in range(cols):
        print(f"matrix[{i}][{j}] = {matrix[i][j]}")

# Oszloponként
for j in range(cols):
    for i in range(rows):
        print(f"matrix[{i}][{j}] = {matrix[i][j]}")

# Memória: Pythonban lista listában (nem folytonos)
# C-ben: sorfolytonos, cím = base + (i*cols + j)*4
""",
        "C++": "// 2D tömb C++\nint matrix[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}}; // Stack, sorfolytonos\nint** dinamikus = new int*[3]; for(int i=0;i<3;i++) dinamikus[i]=new int[4]; // Heap, nem folytonos\nint elso = matrix[0][0];\nint val = matrix[1][2]; // 7\nfor(int i=0;i<3;i++) for(int j=0;j<4;j++) cout << matrix[i][j] << \" \";\n// Cím: base + (i*cols + j)*4 (sorfolytonos)\n// vector<vector<int>> is lehet",
        "C": "/* 2D tömb C */\nint matrix[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}}; // Sorfolytonos\nint elso = matrix[0][0];\nint val = matrix[1][2];\nfor(int i=0;i<3;i++) for(int j=0;j<4;j++) printf(\"%d \", matrix[i][j]);\n// Cím: base + (i*cols + j)*4\n// Dinamikus: int** m = malloc(rows*sizeof(int*)); for(i) m[i]=malloc(cols*sizeof(int));",
        "BASIC": "DIM matrix(3,4) AS INTEGER: matrix(0,0)=1: matrix(0,1)=2: ' 3 sor 4 oszlop\nFOR i=0 TO 2: FOR j=0 TO 3: PRINT matrix(i,j);: NEXT: PRINT: NEXT",
        "Java": "// 2D tömb Java\nint[][] matrix = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};\nint[][] dinamikus = new int[3][4];\nint elso = matrix[0][0];\nint val = matrix[1][2];\nfor(int i=0;i<matrix.length;i++) for(int j=0;j<matrix[0].length;j++) System.out.print(matrix[i][j]+\" \");\n// Nem feltétlen folytonos, de logikailag sorfolytonos",
        "Pascal": "var matrix: array[0..2,0..3] of Integer; i,j: Integer; begin matrix[0,0]:=1; matrix[1,2]:=7; for i:=0 to 2 do for j:=0 to 3 do Write(matrix[i,j],' '); end;"
    }
    
    def get_steps(self, arr):
        rows = self.params.get("rows")
        cols = self.params.get("cols")
        max_val = self.params.get("max_val")
        matrix = ArrayConcepts.create_2d_array(rows, cols, max_val)
        
        yield ArrayStep(array_2d=matrix, code_line=2,
                        explanation=f"🔢 2D tömb: {rows} sor, {cols} oszlop, {rows*cols} elem",
                        comparisons=0, extra={"phase": "letrehozas", "rows": rows, "cols": cols, "matrix": matrix})
        
        for i in range(rows):
            for j in range(cols):
                yield ArrayStep(array_2d=matrix, current_index=i*cols+j, current_value=matrix[i][j], code_line=12,
                                explanation=f"matrix[{i}][{j}] = {matrix[i][j]} | Cím: base + ({i}*{cols}+{j})*4 = {1000+(i*cols+j)*4}",
                                comparisons=i*cols+j+1, extra={"phase": "index", "i": i, "j": j, "value": matrix[i][j], "address": 1000+(i*cols+j)*4, "matrix": matrix})
        
        yield ArrayStep(array_2d=matrix, code_line=20,
                        explanation=f"✅ Mátrix kész: {rows}x{cols} = {rows*cols} elem, {rows*cols*4} byte sorfolytonos",
                        comparisons=rows*cols+1, extra={"phase": "kesz", "matrix": matrix})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class PointerPlugin(AlgorithmPluginBase):
    id = "pointer"
    name = "Mutatók - Pointerek"
    description = "Címek, értékek, *, &, pointer aritmetika"
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "👉"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("var1", "Változó 1 érték", "int", 10, 1, 100))
        self.params.add(Param("var2", "Változó 2 érték", "int", 20, 1, 100))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Pointer Pythonban nincs explicit, de referencia van
# Szimuláljuk C-szerűen

# Változó
x = 10          # Érték
# Cím Pythonban: id(x) - de nem használjuk közvetlenül

# Lista referencia - pointer szerű
a = [1,2,3]
b = a           # b ugyanarra a listára mutat (pointer)
b[0] = 99       # a is változik! a=[99,2,3]

# C-ben:
# int x = 10;
# int *p = &x;  // p x címére mutat
# *p = 20;      // x = 20 (dereferálás)
# p++;          // következő int címére (p+4)

# Tömb és pointer
# arr[2] == *(arr+2)
""",
        "C++": "// Pointer C++\nint x = 10;\nint* p = &x; // p x címére mutat\ncout << \"x cím: \" << p << \" érték: \" << *p << endl; // 10\n*p = 20; // x = 20\ncout << \"x most: \" << x << endl;\nint arr[3] = {5,10,15};\nint* q = arr; // arr == &arr[0]\ncout << *q << endl; // 5\ncout << *(q+1) << endl; // 10, q+1 = következő int (4 byte)\ncout << q[2] << endl; // 15, q[2] == *(q+2)\n// Pointer aritmetika: p++ 4 byte-tal növel\n// Dinamikus: int* d = new int(30);",
        "C": "/* Pointer C */\nint x = 10;\nint *p = &x; // p x címére mutat\nprintf(\"x cím: %p érték: %d\\n\", p, *p); // 10\n*p = 20; // x = 20\nint arr[3] = {5,10,15};\nint *q = arr; // arr == &arr[0]\nprintf(\"%d\\n\", *q); // 5\nprintf(\"%d\\n\", *(q+1)); // 10\nprintf(\"%d\\n\", q[2]); // 15\n// q++ 4 byte\n// malloc: int *d = malloc(sizeof(int)); *d=30; free(d);",
        "BASIC": "' BASIC-ben nincs pointer, de referencia van\nDIM x AS INTEGER: x=10\n' C-ben: p = &x, *p = 20\n' Tömb: arr(0)=5, pointer szerű indexelés",
        "Java": "// Pointer Java-ban nincs explicit, referencia van\nint x = 10;\n// int* p = &x nincs Java-ban\nint[] arr = {5,10,15};\nint[] q = arr; // q ugyanarra mutat\nq[0]=99; // arr[0] is 99\n// arr[2] == *(arr+2) C-ben\n// Referencia: objektumok mindig pointerek",
        "Pascal": "var x: Integer; p: ^Integer; begin x:=10; New(p); p^:=x; WriteLn(p^); // 10\np^:=20; // x nem változik, p^ igen\nx:=30; // p^ még 20\narr: array[0..2] of Integer; q: ^Integer; begin q:=@arr[0]; WriteLn(q^); // 5\nInc(q); WriteLn(q^); // 10, következő\nend;"
    }
    
    def get_steps(self, arr):
        var1 = self.params.get("var1")
        var2 = self.params.get("var2")
        
        sim = PointerSim()
        
        # Változók létrehozása
        addr_x = sim.malloc("x", var1)
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), current_value=var1, pointer_name="x", code_line=2,
                        explanation=f"int x = {var1}; | Cím: {addr_x} | Érték: {var1} | Memória[{addr_x}] = {var1}",
                        comparisons=1, extra={"phase": "var", "var": "x", "addr": addr_x, "value": var1, "memory": sim.memory.copy(), "pointers": sim.variables.copy()})
        
        addr_y = sim.malloc("y", var2)
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), current_value=var2, pointer_name="y", code_line=3,
                        explanation=f"int y = {var2}; | Cím: {addr_y} | Memória[{addr_y}] = {var2}",
                        comparisons=2, extra={"phase": "var", "var": "y", "addr": addr_y, "value": var2, "memory": sim.memory.copy()})
        
        # Pointer létrehozása
        sim.variables["p"] = addr_x  # p = &x
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), pointer_name="p", target="x", code_line=5,
                        explanation=f"int *p = &x; | p értéke: {addr_x} (x címe) | *p = {sim.memory[addr_x]}",
                        comparisons=3, extra={"phase": "pointer", "pointer": "p", "target": "x", "addr": addr_x, "value": sim.memory[addr_x], "memory": sim.memory.copy()})
        
        # Dereferálás
        sim.memory[addr_x] = var1 + 10  # *p = 20
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), pointer_name="p", target="x", current_value=sim.memory[addr_x], code_line=7,
                        explanation=f"*p = {var1+10}; | x most: {sim.memory[addr_x]} | Memória[{addr_x}] = {sim.memory[addr_x]}",
                        comparisons=4, extra={"phase": "deref", "pointer": "p", "value": sim.memory[addr_x], "memory": sim.memory.copy()})
        
        # Tömb és pointer
        arr = [5, 10, 15]
        for i in range(len(arr)):
            addr = 2000 + i*4
            sim.memory[addr] = arr[i]
        sim.variables["arr"] = 2000
        
        for i in range(len(arr)):
            addr = 2000 + i*4
            yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), current_index=i, current_value=arr[i], pointer_name="arr", code_line=10,
                            explanation=f"arr[{i}] = {arr[i]} | *(arr+{i}) = {arr[i]} | Cím: {addr} = 2000+{i}*4",
                            comparisons=5+i, extra={"phase": "array_pointer", "index": i, "value": arr[i], "addr": addr, "array": arr, "memory": sim.memory.copy()})
        
        # Pointer aritmetika
        q_addr = 2000 + 1*4
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), pointer_name="q", target="arr+1", current_value=arr[1], code_line=12,
                        explanation=f"int *q = arr+1; | q = {q_addr} | *q = {arr[1]} | q++ = {q_addr+4}",
                        comparisons=8, extra={"phase": "arithmetic", "pointer": "q", "addr": q_addr, "value": arr[1], "memory": sim.memory.copy()})
        
        yield ArrayStep(pointers=sim.variables.copy(), memory=sim.memory.copy(), code_line=15,
                        explanation=f"✅ Pointerek: &x cím, *p érték, p++ következő cím",
                        comparisons=9, extra={"phase": "kesz", "memory": sim.memory.copy()})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class ArrayInArrayPlugin(AlgorithmPluginBase):
    id = "array_in_array"
    name = "Tömbben tömb"
    description = "Jagged array, lista listában, nem téglalap"
    time_complexity = "O(n*m)"
    space_complexity = "O(n*m)"
    icon = "🗂️"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("max_val", "Max érték", "int", 20, 5, 50))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Tömbben tömb - Jagged array
# Nem téglalap, minden sor más hosszú

jagged = [
    [1, 2],
    [3, 4, 5, 6],
    [7],
    [8, 9, 10]
]

# Bejárás
for i in range(len(jagged)):
    for j in range(len(jagged[i])):
        print(f"jagged[{i}][{j}] = {jagged[i][j]}")

# Létrehozás dinamikusan
jagged = []
for i in range(3):
    row = [random.randint(1,20) for _ in range(random.randint(2,5))]
    jagged.append(row)

# Memória: lista listában, nem folytonos, minden sor külön lista
# C-ben: int** jagged, minden sor malloc
""",
        "C++": "// Tömbben tömb C++ - Jagged\nvector<vector<int>> jagged = {{1,2},{3,4,5,6},{7},{8,9,10}};\nfor(int i=0;i<jagged.size();i++) for(int j=0;j<jagged[i].size();j++) cout << jagged[i][j] << \" \";\n// Dinamikus\nint rows=3;\nint** jagged2 = new int*[rows];\nint cols[] = {2,4,1};\nfor(int i=0;i<rows;i++) jagged2[i]=new int[cols[i]];\n// Nem folytonos, minden sor külön",
        "C": "/* Tömbben tömb C - Jagged */\nint* jagged[3];\nint row0[]={1,2}; jagged[0]=row0;\nint row1[]={3,4,5,6}; jagged[1]=row1;\nint row2[]={7}; jagged[2]=row2;\nfor(int i=0;i<3;i++) for(int j=0;j<2;j++) printf(\"%d \", jagged[i][j]);\n// Dinamikus: int** j = malloc(3*sizeof(int*)); j[0]=malloc(2*sizeof(int));",
        "BASIC": "DIM jagged(3) AS INTEGER: ' Minden elem lista\n' Pythonban: [[1,2],[3,4,5,6],[7]]",
        "Java": "// Tömbben tömb Java - Jagged\nint[][] jagged = {{1,2},{3,4,5,6},{7},{8,9,10}};\nfor(int i=0;i<jagged.length;i++) for(int j=0;j<jagged[i].length;j++) System.out.print(jagged[i][j]+\" \");\n// Minden sor külön tömb, nem folytonos",
        "Pascal": "var jagged: array of array of Integer; i,j: Integer; begin SetLength(jagged,3); SetLength(jagged[0],2); jagged[0,0]:=1; jagged[0,1]:=2; SetLength(jagged[1],4); // ...\nfor i:=0 to High(jagged) do for j:=0 to High(jagged[i]) do Write(jagged[i,j],' '); end;"
    }
    
    def get_steps(self, arr):
        max_val = self.params.get("max_val")
        jagged = ArrayConcepts.create_jagged_array()
        # Értékeket max_val szerint
        for i in range(len(jagged)):
            for j in range(len(jagged[i])):
                jagged[i][j] = random.randint(1, max_val)
        
        yield ArrayStep(jagged=jagged, code_line=2,
                        explanation=f"🗂️ Tömbben tömb: {len(jagged)} sor, hosszak: {[len(r) for r in jagged]}",
                        comparisons=0, extra={"phase": "letrehozas", "jagged": jagged, "lengths": [len(r) for r in jagged]})
        
        for i in range(len(jagged)):
            for j in range(len(jagged[i])):
                yield ArrayStep(jagged=jagged, current_index=i, current_value=jagged[i][j], code_line=10,
                                explanation=f"jagged[{i}][{j}] = {jagged[i][j]} | Sor {i} hossz {len(jagged[i])}",
                                comparisons=i*3+j+1, extra={"phase": "index", "i": i, "j": j, "value": jagged[i][j], "jagged": jagged})
        
        yield ArrayStep(jagged=jagged, code_line=20,
                        explanation=f"✅ Jagged kész: nem téglalap, minden sor más hosszú, memória nem folytonos",
                        comparisons=10, extra={"phase": "kesz", "jagged": jagged})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
