# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep

class StructStep(VisualizationStep):
    def __init__(self, value=None, array=None, structure=None, current_line=None, variables=None, code_line=0, explanation="", comparisons=0, extra=None):
        e_dict = extra.copy() if extra else {}
        e_dict.update({
            "value": value, "structure": structure or "",
            "current_line": current_line, "variables": variables or {}
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=array or [],
            key=value,
            extra=e_dict
        )

class VariablesPlugin(AlgorithmPluginBase):
    id = "variables"
    name = "Változók, típusok"
    description = "int, float, string, bool minden nyelven szerkezet"
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "📦"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "program_structure"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("lang_focus", "Nyelv fókusz", "choice", "Python", choices=["Python", "C++", "C", "BASIC", "Java", "Pascal"]))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Változók, típusok - Python szerkezet
# Dinamikus típus, nem kell deklarálni

# Egész
age = 25              # int
# Tört
price = 19.99         # float
# Szöveg
name = "Péter"        # str
# Logikai
is_ok = True          # bool
# Lista
numbers = [1,2,3]     # list

# Szerkezet: név = érték
# Típus automatikus, változhat: age = "huszonöt"
# Memória: dinamikus, GC
print(f"{name} {age} éves")
""",
        "C++": "// Változók, típusok - C++ szerkezet\n// Statikus típus, deklarálni kell\n\n#include <string>\nint age = 25;              // int 4 byte\nfloat price = 19.99f;      // float 4 byte\ndouble big = 19.99;        // double 8 byte\nstd::string name = \"Péter\"; // string osztály\nbool is_ok = true;         // bool 1 byte\nint numbers[3] = {1,2,3};   // tömb fix méret\n\n// Szerkezet: típus név = érték;\n// Típus nem változhat: age = \"huszonöt\" HIBA!\n// Memória: stack, típus fix\n// cout << name << \" \" << age << \" éves\";\n// auto - C++11: auto x = 25; típus következtetés",
        "C": "/* Változók, típusok - C szerkezet */\n/* Statikus típus, nincs string osztály */\n#include <stdbool.h>\nint age = 25;              /* int 4 byte */\nfloat price = 19.99f;      /* float 4 byte */\ndouble big = 19.99;        /* double 8 byte */\nchar name[] = \"Péter\";     /* char tömb, nincs string! */\nbool is_ok = true;         /* _Bool C99 */\nint numbers[3] = {1,2,3};   /* tömb */\n\n/* Szerkezet: típus név = érték; */\n/* Nincs string, char[] */\n/* printf(\"%s %d éves\", name, age); */\n/* Memória: stack, manuális */",
        "BASIC": "' Változók, típusok - BASIC szerkezet\n' Suffix típus jelölés\n\nage% = 25              ' % = INTEGER 2 byte\nprice! = 19.99         ' ! = SINGLE 4 byte\nbig# = 19.99           ' # = DOUBLE 8 byte\nname$ = \"Péter\"        ' $ = STRING\nis_ok% = -1            ' TRUE = -1, FALSE=0\nDIM numbers%(3) AS INTEGER: numbers%(0)=1: numbers%(1)=2: numbers%(2)=3\n\n' Szerkezet: név + suffix = érték VAGY DIM AS\n' Típus suffix: % ! # $ \n' PRINT name$; age%; \" éves\"\n' Memória: egyszerű, BASIC kezeli",
        "Java": "// Változók, típusok - Java szerkezet\n// Statikus típus, minden objektum\n\nint age = 25;              // int 4 byte\nfloat price = 19.99f;      // float 4 byte\n double big = 19.99;        // double 8 byte\nString name = \"Péter\";     // String osztály, referencia!\nboolean is_ok = true;      // boolean\nint[] numbers = {1,2,3};   // tömb objektum\n\n// Szerkezet: típus név = érték;\n// String nagy S, objektum!\n// System.out.println(name + \" \" + age + \" éves\");\n// Memória: heap referencia, GC\n// var - Java 10: var x = 25; típus következtetés",
        "Pascal": "// Változók, típusok - Pascal szerkezet\n// Statikus, var szekció, := értékadás\n\nvar\n  age: Integer;        // Integer\n  price: Real;         // Real\n  name: string;        // string\n  is_ok: Boolean;      // Boolean\n  numbers: array[0..2] of Integer;\nbegin\n  age := 25;           // := nem =\n  price := 19.99;\n  name := 'Péter';     // ' nem \"\n  is_ok := True;       // True nagy T\n  numbers[0] := 1;\n  // WriteLn(name, ' ', age, ' éves');\nend.\n// Szerkezet: var típus; begin név := érték; end.\n// := értékadás, = összehasonlítás!"
    }
    def get_steps(self, arr):
        lang = self.params.get("lang_focus")
        variables = {"age": 25, "price": 19.99, "name": "Péter", "is_ok": True, "numbers": [1,2,3]}
        yield StructStep(variables=variables, structure="variables", current_line=1, code_line=1, explanation=f"📦 Változók, típusok - {lang} szerkezet | Kezdő 🟢 | Minden nyelven más!", comparisons=0, extra={"phase": "init", "lang": lang, "variables": variables, "structure": "variables"})
        for idx, (k,v) in enumerate(variables.items()):
            yield StructStep(value=v, variables={k:v}, structure="variables", current_line=idx+1, code_line=idx+2, explanation=f"{k} = {v} | Típus: {type(v).__name__} | {lang}-ban: {self.get_lang_decl(k,v,lang)}", comparisons=idx+1, extra={"phase": "var", "key": k, "value": v, "lang": lang, "decl": self.get_lang_decl(k,v,lang)})
        yield StructStep(variables=variables, structure="variables", code_line=10, explanation=f"✅ Változók kész - {lang} szerkezet | Dinamikus (Python/BASIC) vs Statikus (C/C++/Java/Pascal)", comparisons=6, extra={"phase": "done", "variables": variables, "lang": lang})
    def get_lang_decl(self, k,v,lang):
        if lang=="Python": return f"{k} = {repr(v)}"
        elif lang=="C++": return f"int {k} = {v};" if isinstance(v,int) else f'std::string {k} = "{v}";' if isinstance(v,str) else f"auto {k} = {v};"
        elif lang=="C": return f"int {k} = {v};" if isinstance(v,int) else f'char {k}[] = "{v}";'
        elif lang=="BASIC": return f"{k}$ = \"{v}\"" if isinstance(v,str) else f"{k}% = {v}"
        elif lang=="Java": return f"int {k} = {v};" if isinstance(v,int) else f'String {k} = "{v}";'
        elif lang=="Pascal": return f"{k} := {v};" if isinstance(v,int) else f"{k} := '{v}';"
        return f"{k} = {v}"
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class IfElsePlugin(AlgorithmPluginBase):
    id = "if_else"
    name = "Elágazás - if else"
    description = "if, else if, else minden nyelven szerkezet"
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "🔀"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "program_structure"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("score", "Pont", "int", 75, 0, 100))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Elágazás - if else - Python szerkezet
# Behúzás számít! Nincs {} és ()

score = 75

if score >= 90:
    print("Jeles")      # Behúzás 4 szóköz
elif score >= 80:       # elif nem else if!
    print("Jó")
elif score >= 60:
    print("Közepes")
else:
    print("Elégtelen")

# Szerkezet:
# if feltétel:  <- nincs zárójel, van kettőspont!
#     kód       <- behúzás!
# elif feltétel:
#     kód
# else:
#     kód

# Logikai: and, or, not (nem && || !)
# if 60 <= score < 80:  <- láncolt!
""",
        "C++": "// Elágazás - if else - C++ szerkezet\n// {} blokk, () feltétel\n\nint score = 75;\n\nif (score >= 90) {          // () kötelező, {} blokk\n    cout << \"Jeles\";\n} else if (score >= 80) {   // else if külön szavak\n    cout << \"Jó\";\n} else if (score >= 60) {\n    cout << \"Közepes\";\n} else {\n    cout << \"Elégtelen\";\n}\n\n// Szerkezet:\n// if (feltétel) { kód }\n// else if (feltétel) { kód }\n// else { kód }\n// () kötelező, {} ajánlott!\n// Logikai: && || !\n// if (score >= 60 && score < 80)",
        "C": "/* Elágazás - if else - C szerkezet */\n/* {} blokk, () feltétel, mint C++ */\nint score = 75;\nif (score >= 90) {\n    printf(\"Jeles\");\n} else if (score >= 80) {\n    printf(\"Jó\");\n} else if (score >= 60) {\n    printf(\"Közepes\");\n} else {\n    printf(\"Elégtelen\");\n}\n/* Szerkezet: if (felt) { } else if (felt) { } else { } */\n/* () kötelező, {} elhagyható 1 sornál de veszélyes! */\n/* Logikai: && || ! */",
        "BASIC": "' Elágazás - if else - BASIC szerkezet\n' THEN, ELSEIF, ELSE, END IF\n\nscore% = 75\n\nIF score% >= 90 THEN\n    PRINT \"Jeles\"\nELSEIF score% >= 80 THEN\n    PRINT \"Jó\"\nELSEIF score% >= 60 THEN\n    PRINT \"Közepes\"\nELSE\n    PRINT \"Elégtelen\"\nEND IF\n\n' Szerkezet:\n' IF feltétel THEN\n'   kód\n' ELSEIF feltétel THEN\n'   kód\n' ELSE\n'   kód\n' END IF  <- kötelező lezárni!\n' Logikai: AND OR NOT\n' Egysoros: IF score%>=60 THEN PRINT \"átment\" ELSE PRINT \"bukott\"",
        "Java": "// Elágazás - if else - Java szerkezet\n// {} blokk, () feltétel, mint C++\n\nint score = 75;\n\nif (score >= 90) {\n    System.out.println(\"Jeles\");\n} else if (score >= 80) {\n    System.out.println(\"Jó\");\n} else if (score >= 60) {\n    System.out.println(\"Közepes\");\n} else {\n    System.out.println(\"Elégtelen\");\n}\n\n// Szerkezet: if (felt) { } else if (felt) { } else { }\n// () kötelező, {} ajánlott\n// Logikai: && || !\n// String: if (name.equals(\"Péter\")) nem == !",
        "Pascal": "// Elágazás - if else - Pascal szerkezet\n// Nincs {}, begin end, THEN, ELSE, nincs () feltétel körül kötelezően\n\nvar score: Integer;\nbegin\n  score := 75;\n  if score >= 90 then\n    WriteLn('Jeles')\n  else if score >= 80 then\n    WriteLn('Jó')\n  else if score >= 60 then\n    WriteLn('Közepes')\n  else\n    WriteLn('Elégtelen');\nend.\n\n// Szerkezet:\n// if feltétel then kód\n// else if feltétel then kód\n// else kód\n// Nincs () kötelező, THEN kötelező!\n// begin end ha több sor: if felt then begin kód; kód; end\n// Logikai: and or not"
    }
    def get_steps(self, arr):
        score = self.params.get("score")
        yield StructStep(value=score, structure="if_else", code_line=1, explanation=f"🔀 Elágazás: score={score} | Kezdő 🟢 | Minden nyelven más szerkezet!", comparisons=0, extra={"phase": "init", "score": score})
        if score >= 90:
            result = "Jeles"
            branch = "if score>=90"
        elif score >= 80:
            result = "Jó"
            branch = "elif score>=80"
        elif score >= 60:
            result = "Közepes"
            branch = "elif score>=60"
        else:
            result = "Elégtelen"
            branch = "else"
        yield StructStep(value=result, structure="if_else", code_line=3, explanation=f"{branch} -> {result} | score={score} | Elágazás", comparisons=1, extra={"phase": "branch", "score": score, "branch": branch, "result": result})
        yield StructStep(value=result, structure="if_else", code_line=8, explanation=f"✅ {score} -> {result} | Python: behúzás, C++/Java: {{}}, BASIC: END IF, Pascal: THEN", comparisons=2, extra={"phase": "done", "score": score, "result": result})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class ForLoopPlugin(AlgorithmPluginBase):
    id = "for_loop"
    name = "For ciklus"
    description = "for loop minden nyelven szerkezet, 0..n"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    icon = "🔁"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "program_structure"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "n-ig", "int", 5, 3, 8))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# For ciklus - Python szerkezet
# range, behúzás, nincs () {}

# 0..4
for i in range(5):
    print(i)  # 0,1,2,3,4

# 1..5
for i in range(1, 6):
    print(i)  # 1,2,3,4,5

# Lista bejárás
for num in [1,2,3]:
    print(num)

# Szöveg
for ch in "Péter":
    print(ch)

# Szerkezet: for változó in range/lista:
#               kód (behúzás!)
# Nincs () {}, van : és behúzás!
""",
        "C++": "// For ciklus - C++ szerkezet\n// (init; feltétel; lépés) {}\n\n// 0..4\nfor (int i=0; i<5; i++) {   // i++ vagy ++i\n    cout << i; // 0,1,2,3,4\n}\n\n// 1..5\nfor (int i=1; i<=5; i++) {\n    cout << i;\n}\n\n// Lista (C++11 range-based)\nfor (int num : {1,2,3}) {\n    cout << num;\n}\n\n// Szerkezet: for (init; felt; lépés) { kód }\n// () kötelező, {} blokk\n// i definiálható for-ban: for (int i=0; ...)",
        "C": "/* For ciklus - C szerkezet */\n/* (init; felt; lépés) {} */\n/* 0..4 */\nfor (int i=0; i<5; i++) {\n    printf(\"%d \", i); /* 0,1,2,3,4 */\n}\n/* 1..5 */\nfor (int i=1; i<=5; i++) {\n    printf(\"%d \", i);\n}\n/* Lista nincs range-based C-ben! */\nint nums[]={1,2,3};\nfor (int i=0; i<3; i++) {\n    printf(\"%d \", nums[i]);\n}\n/* Szerkezet: for (init; felt; lépés) { kód } */\n/* C99 óta int i for-ban */",
        "BASIC": "' For ciklus - BASIC szerkezet\n' FOR TO STEP NEXT\n\n' 0..4\nFOR i% = 0 TO 4\n    PRINT i%  ' 0,1,2,3,4\nNEXT i%\n\n' 1..5\nFOR i% = 1 TO 5\n    PRINT i%\nNEXT i%\n\n' STEP -2 visszafelé\nFOR i% = 5 TO 1 STEP -1\n    PRINT i%  ' 5,4,3,2,1\nNEXT i%\n\n' Szerkezet: FOR változó = kezdő TO vég STEP lépés\n'            kód\n'            NEXT változó  <- lezárás!\n' STEP elhagyható, default 1",
        "Java": "// For ciklus - Java szerkezet\n// (init; felt; lépés) {}\n\n// 0..4\nfor (int i=0; i<5; i++) {\n    System.out.println(i); // 0,1,2,3,4\n}\n\n// 1..5\nfor (int i=1; i<=5; i++) {\n    System.out.println(i);\n}\n\n// Lista (enhanced for)\nfor (int num : new int[]{1,2,3}) {\n    System.out.println(num);\n}\n\n// Szerkezet: for (init; felt; lépés) { kód }\n// () kötelező, {} blokk\n// Mint C++, C",
        "Pascal": "// For ciklus - Pascal szerkezet\n// TO, DOWNTO, DO, nincs ()\n\n// 0..4\nfor i := 0 to 4 do\n  WriteLn(i); // 0,1,2,3,4\n\n// 1..5\nfor i := 1 to 5 do\n  WriteLn(i);\n\n// Visszafelé 5..1\nfor i := 5 downto 1 do\n  WriteLn(i); // 5,4,3,2,1\n\n// Szerkezet: for változó := kezdő to/downto vég do kód\n// Nincs (), TO vagy DOWNTO, DO kötelező!\n// begin end ha több sor: for ... do begin kód; end;"
    }
    def get_steps(self, arr):
        n = self.params.get("n")
        yield StructStep(value=n, structure="for_loop", code_line=1, explanation=f"🔁 For ciklus: 0..{n-1} | Kezdő 🟢 | Minden nyelven más!", comparisons=0, extra={"phase": "init", "n": n})
        for i in range(n):
            yield StructStep(value=i, array=list(range(i+1)), structure="for_loop", code_line=2, explanation=f"For i={i} | 0..{n-1} | {i+1}/{n} lépés | Python: for i in range({n}): C++/Java: for(int i=0;i<{n};i++)", comparisons=i+1, extra={"phase": "iter", "i": i, "n": n})
        yield StructStep(value=n, structure="for_loop", code_line=4, explanation=f"✅ For kész: 0..{n-1} | {n} iteráció | O(n)", comparisons=n+1, extra={"phase": "done", "n": n})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class WhileLoopPlugin(AlgorithmPluginBase):
    id = "while_loop"
    name = "While ciklus"
    description = "while, feltétel elöl/hátul, minden nyelven"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    icon = "🔄"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "program_structure"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "n-ig", "int", 5, 3, 8))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# While ciklus - Python szerkezet
# Feltétel elöl, behúzás

i = 0
while i < 5:        # Feltétel, kettőspont, behúzás
    print(i)
    i += 1          # i++ nincs Pythonban! i+=1

# Végtelen while True + break
while True:
    if i >= 5:
        break
    print(i)
    i += 1

# Szerkezet: while feltétel:
#              kód (behúzás)
# Nincs () {}, van : és behúzás!
""",
        "C++": "// While ciklus - C++ szerkezet\n// (feltétel) {}\n\nint i=0;\nwhile (i < 5) {     // () kötelező, {} blokk\n    cout << i;\n    i++;            // i++ van!\n}\n\n// Do-while: hátul tesztel, egyszer biztos lefut\nint j=0;\ndo {\n    cout << j;\n    j++;\n} while (j < 5);   // ; kötelező do-while végén!\n\n// Szerkezet: while (felt) { kód }\n// do { kód } while (felt);",
        "C": "/* While ciklus - C szerkezet */\n/* (felt) {} */\nint i=0;\nwhile (i < 5) {\n    printf(\"%d \", i);\n    i++;\n}\n/* Do-while */\nint j=0;\ndo {\n    printf(\"%d \", j);\n    j++;\n} while (j < 5);\n/* Szerkezet: while (felt) { } */\n/* do { } while (felt); */",
        "BASIC": "' While ciklus - BASIC szerkezet\n' WHILE WEND vagy DO LOOP\n\ni% = 0\nWHILE i% < 5         ' Elöl tesztel\n    PRINT i%\n    i% = i% + 1\nWEND                ' WHILE lezárás WEND!\n\n' Do-while elöl tesztel\n\ni% = 0\nDO WHILE i% < 5\n    PRINT i%\n    i% = i% + 1\nLOOP\n\n' Do-while hátul tesztel (egyszer lefut)\n\ni% = 0\nDO\n    PRINT i%\n    i% = i% + 1\nLOOP WHILE i% < 5\n\n' Szerkezet: WHILE feltétel ... WEND\n'          DO WHILE felt ... LOOP\n'          DO ... LOOP WHILE felt",
        "Java": "// While ciklus - Java szerkezet\n// (felt) {}\n\nint i=0;\nwhile (i < 5) {\n    System.out.println(i);\n    i++;\n}\n\n// Do-while\nint j=0;\ndo {\n    System.out.println(j);\n    j++;\n} while (j < 5);\n\n// Szerkezet: while (felt) { }\n// do { } while (felt);",
        "Pascal": "// While ciklus - Pascal szerkezet\n// Feltétel DO, nincs ()\n\nvar i: Integer;\nbegin\n  i := 0;\n  while i < 5 do     // Nincs (), DO kötelező!\n  begin\n    WriteLn(i);\n    Inc(i);          // Inc(i) nem i++\n  end;\n\n  // Repeat-until: hátul tesztel, until feltétel, egyszer lefut\n  i := 0;\n  repeat\n    WriteLn(i);\n    Inc(i);\n  until i >= 5;     // until nem while! Fordított logika!\nend.\n\n// Szerkezet: while felt do kód\n// repeat kód until felt"
    }
    def get_steps(self, arr):
        n = self.params.get("n")
        yield StructStep(value=0, structure="while_loop", code_line=1, explanation=f"🔄 While: i=0, while i<{n} | Kezdő 🟢", comparisons=0, extra={"phase": "init", "n": n, "i": 0})
        i = 0
        comp = 0
        while i < n:
            comp += 1
            yield StructStep(value=i, structure="while_loop", code_line=2, explanation=f"While i={i} < {n} ? Igen -> kód, i++ -> {i+1} | Python: while i<{n}: C++: while(i<{n})", comparisons=comp, extra={"phase": "iter", "i": i, "n": n})
            i += 1
        yield StructStep(value=i, structure="while_loop", code_line=4, explanation=f"While i={i} < {n} ? Nem -> kilép | ✅ {n} iteráció", comparisons=comp+1, extra={"phase": "done", "n": n, "i": i})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class FunctionPlugin(AlgorithmPluginBase):
    id = "function_def"
    name = "Függvények - def"
    description = "Függvény definíció, paraméter, return minden nyelven"
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "🔧"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "program_structure"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("a", "a", "int", 5, 1, 10))
        self.params.add(Param("b", "b", "int", 3, 1, 10))
        self.complexity_level = "easy"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Függvény - Python szerkezet
# def, nincs típus, return, behúzás

def add(a, b):          # def név(param): 
    result = a + b      # behúzás
    return result       # return

# Hívás
x = add(5, 3)  # 8

# Típus hint (opcionális):
def add_typed(a: int, b: int) -> int:
    return a + b

# Alapértelmezett paraméter:
def greet(name="Világ"):
    print(f"Szia {name}")

# Szerkezet: def név(param): 
#              kód
#              return
# Nincs {} (), van : és behúzás!
""",
        "C++": "// Függvény - C++ szerkezet\n// típus név(típus param) { return }\n\nint add(int a, int b) {  // típus név(típus a, típus b)\n    int result = a + b;   // {} blokk\n    return result;        // return típus egyezik!\n}\n\n// Hívás\nint x = add(5, 3); // 8\n\n// Void ha nincs return:\nvoid greet(string name) {\n    cout << \"Szia \" << name;\n}\n\n// Alapértelmezett paraméter:\nint add_default(int a, int b=0) {\n    return a + b;\n}\n\n// Szerkezet: típus név(típus param) { kód return }\n// {} kötelező, típusok mindenhol!",
        "C": "/* Függvény - C szerkezet */\n/* típus név(típus param) { return } */\nint add(int a, int b) {\n    int result = a + b;\n    return result;\n}\n/* Hívás */\n/* int x = add(5, 3); */\n/* Void */\nvoid greet(char* name) {\n    printf(\"Szia %s\", name);\n}\n/* Nincs alapértelmezett paraméter C-ben! */\n/* Nincs túlterhelés C-ben! */\n/* Szerkezet: típus név(típus param) { return } */",
        "BASIC": "' Függvény - BASIC szerkezet\n' FUNCTION, END FUNCTION\n\nFUNCTION add%(a% AS INTEGER, b% AS INTEGER) AS INTEGER\n    result% = a% + b%\n    add% = result%   ' Vagy RETURN result%\nEND FUNCTION\n\n' Hívás\n' x% = add%(5, 3)  ' 8\n\n' SUB ha nincs return:\nSUB greet(name$ AS STRING)\n    PRINT \"Szia \"; name$\nEND SUB\n\n' Szerkezet: FUNCTION név%(param AS TÍPUS) AS TÍPUS\n'            kód\n'            név% = érték  VAGY RETURN\n'            END FUNCTION\n' SUB ... END SUB ha nincs visszatérés",
        "Java": "// Függvény - Java szerkezet (metódus)\n// Minden függvény osztályban van! Nincs szabad függvény\n\nclass MyClass {\n    // Static metódus\n    static int add(int a, int b) {\n        int result = a + b;\n        return result;\n    }\n    \n    // Hívás: MyClass.add(5,3) vagy obj.add(5,3)\n    // int x = MyClass.add(5,3);\n    \n    static void greet(String name) {\n        System.out.println(\"Szia \" + name);\n    }\n    \n    // Nincs alapértelmezett paraméter Java-ban!\n    // Túlterhelés van: add(int) és add(double) külön\n}\n\n// Szerkezet: [static] típus név(típus param) { return }\n// Osztályban kell lennie!",
        "Pascal": "// Függvény - Pascal szerkezet\n// function vagy procedure, var, begin end\n\nfunction add(a, b: Integer): Integer;\nvar\n  result: Integer;\nbegin\n  result := a + b;   // := nem =\n  add := result;     // név := érték, nem return!\nend;\n\n// Hívás: x := add(5, 3);\n\n// Procedure ha nincs return:\nprocedure greet(name: string);\nbegin\n  WriteLn('Szia ', name);\nend;\n\n// Szerkezet: function név(param: típus): típus;\n//            var ... begin név := érték; end;\n//            procedure név(param: típus); begin end;\n// := értékadás, név := return!"
    }
    def get_steps(self, arr):
        a = self.params.get("a")
        b = self.params.get("b")
        yield StructStep(value=None, structure="function", code_line=1, explanation=f"🔧 Függvény: add({a},{b}) | Könnyű 🟡 | Minden nyelven más szerkezet!", comparisons=0, extra={"phase": "init", "a": a, "b": b})
        result = a + b
        yield StructStep(value=result, structure="function", code_line=2, explanation=f"Def add(a={a},b={b}): result={a}+{b}={result} | Python: def add(a,b): C++: int add(int a,int b){{}}", comparisons=1, extra={"phase": "calc", "a": a, "b": b, "result": result})
        yield StructStep(value=result, structure="function", code_line=3, explanation=f"Return {result} | Python: return result, Pascal: add := result, BASIC: add% = result", comparisons=2, extra={"phase": "return", "result": result})
        yield StructStep(value=result, structure="function", code_line=5, explanation=f"✅ add({a},{b})={result} | Hívás: Python add(5,3) C++ add(5,3) Java MyClass.add(5,3) Pascal add(5,3)", comparisons=3, extra={"phase": "done", "a": a, "b": b, "result": result})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
