# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
import math

class SimpleStep:
    def __init__(self, value=None, array=None, extra_data=None, code_line=0, explanation="", comparisons=0, extra=None):
        self.value = value
        self.array = array or []
        self.extra_data = extra_data or {}
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.extra = extra or {}
        self.key = value
        self.sorted_end = -1
        self.highlight = []
        self.shifts = 0
        self.pass_num = comparisons

class FactorialPlugin(AlgorithmPluginBase):
    id = "factorial"
    name = "Faktoriális - n!"
    description = "n! = 1*2*...*n, iteratív és rekurzív"
    time_complexity = "O(n)"
    space_complexity = "O(1) / O(n)"
    icon = "❗"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - HES Projects® by FePe®"
    plugin_type = "simple"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "n érték", "int", 5, 1, 8))
        self.complexity_level = "beginner"
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Faktoriális - n!
# n! = 1*2*3*...*n
# 5! = 120

def factorial_iter(n):
    result = 1
    for i in range(1, n+1):
        result *= i
    return result

def factorial_rec(n):
    if n <= 1:
        return 1
    return n * factorial_rec(n-1)

# Példa: 5! = 1*2*3*4*5 = 120
# Használat: kombinatorika, valószínűség
""",
        "C++": "// Faktoriális C++\nlong long factorial(int n){\n long long res=1;\n for(int i=1;i<=n;i++) res*=i;\n return res; }\n// Rekurzív:\nlong long factorial_rec(int n){\n if(n<=1) return 1;\n return n*factorial_rec(n-1); }\n// 5! = 120",
        "C": "/* Faktoriális C */\nlong long factorial(int n){ long long r=1; for(int i=1;i<=n;i++) r*=i; return r; }\nlong long factorial_rec(int n){ if(n<=1) return 1; return n*factorial_rec(n-1); }\n// 5! = 120",
        "BASIC": "FUNCTION factorial(n AS INTEGER) AS LONG: r=1: FOR i=1 TO n: r=r*i: NEXT: RETURN r: END FUNCTION\n' 5! = 120",
        "Java": "// Faktoriális Java\nlong factorial(int n){ long r=1; for(int i=1;i<=n;i++) r*=i; return r; }\nlong factorial_rec(int n){ if(n<=1) return 1; return n*factorial_rec(n-1); }\n// 5! = 120",
        "Pascal": "function factorial(n: Integer): LongInt; var i: Integer; r: LongInt; begin r:=1; for i:=1 to n do r:=r*i; factorial:=r; end; function factorial_rec(n: Integer): LongInt; begin if n<=1 then factorial_rec:=1 else factorial_rec:=n*factorial_rec(n-1); end; // 5! = 120"
    }
    
    def get_steps(self, arr):
        n = self.params.get("n")
        
        yield SimpleStep(value=1, code_line=2,
                         explanation=f"❗ Faktoriális: {n}! | Kezdő 🟢 | 1*2*...*{n}",
                         comparisons=0, extra={"phase": "init", "n": n, "result": 1})
        
        result = 1
        for i in range(1, n+1):
            result *= i
            yield SimpleStep(value=result, array=list(range(1, i+1)), code_line=4,
                             explanation=f"{i}! = {result} | {i} * {result//i if i>1 else 1} = {result}",
                             comparisons=i, extra={"phase": "iter", "i": i, "result": result, "n": n, "mult": f"{i}!={result}"})
        
        yield SimpleStep(value=result, code_line=6,
                         explanation=f"✅ {n}! = {result} | O(n) idő, O(1) tár | Kombinatorika",
                         comparisons=n+1, extra={"phase": "done", "n": n, "result": result})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class FibonacciPlugin(AlgorithmPluginBase):
    id = "fibonacci_iter"
    name = "Fibonacci - sorozat"
    description = "0,1,1,2,3,5,8,13... iteratív"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "🐚"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - HES Projects® by FePe®"
    plugin_type = "simple"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "n-edik elem", "int", 8, 3, 12))
        self.complexity_level = "beginner"
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Fibonacci - 0,1,1,2,3,5,8,13...
# F(n) = F(n-1) + F(n-2)

def fibonacci(n):
    if n <= 1:
        return n
    fib = [0, 1]
    for i in range(2, n+1):
        fib.append(fib[i-1] + fib[i-2])
    return fib[n]

# Sorozat: 0,1,1,2,3,5,8,13,21,34...
# Aranyarány: F(n)/F(n-1) -> 1.618...
# Természetben: virág szirmok, kagyló, galaxis
""",
        "C++": "// Fibonacci C++\nlong long fibonacci(int n){\n if(n<=1) return n;\n long long a=0,b=1;\n for(int i=2;i<=n;i++){ long long c=a+b; a=b; b=c; }\n return b; }\n// 0,1,1,2,3,5,8...",
        "C": "/* Fibonacci C */\nlong long fibonacci(int n){ if(n<=1) return n; long long a=0,b=1; for(int i=2;i<=n;i++){ long long c=a+b; a=b; b=c; } return b; }\n// 0,1,1,2,3,5,8...",
        "BASIC": "FUNCTION fibonacci(n AS INTEGER) AS LONG: IF n<=1 THEN RETURN n: a=0: b=1: FOR i=2 TO n: c=a+b: a=b: b=c: NEXT: RETURN b: END FUNCTION\n' 0,1,1,2,3,5,8...",
        "Java": "// Fibonacci Java\nlong fibonacci(int n){ if(n<=1) return n; long a=0,b=1; for(int i=2;i<=n;i++){ long c=a+b; a=b; b=c; } return b; }\n// 0,1,1,2,3,5,8...",
        "Pascal": "function fibonacci(n: Integer): LongInt; var a,b,c,i: LongInt; begin if n<=1 then fibonacci:=n else begin a:=0; b:=1; for i:=2 to n do begin c:=a+b; a:=b; b:=c; end; fibonacci:=b; end; end; // 0,1,1,2,3,5,8..."
    }
    
    def get_steps(self, arr):
        n = self.params.get("n")
        
        yield SimpleStep(value=0, array=[0, 1], code_line=2,
                         explanation=f"🐚 Fibonacci: F({n}) | Kezdő 🟢 | 0,1,1,2,3,5,8...",
                         comparisons=0, extra={"phase": "init", "n": n, "fib": [0, 1]})
        
        if n <= 1:
            yield SimpleStep(value=n, code_line=3,
                             explanation=f"F({n}) = {n}",
                             comparisons=1, extra={"phase": "done", "n": n, "result": n})
            return
        
        fib = [0, 1]
        for i in range(2, n+1):
            fib.append(fib[i-1] + fib[i-2])
            yield SimpleStep(value=fib[i], array=fib[:], code_line=6,
                             explanation=f"F({i}) = F({i-1}) + F({i-2}) = {fib[i-1]} + {fib[i-2]} = {fib[i]} | Sorozat: {fib}",
                             comparisons=i, extra={"phase": "iter", "i": i, "fib": fib[:], "result": fib[i]})
        
        yield SimpleStep(value=fib[n], array=fib, code_line=8,
                         explanation=f"✅ F({n}) = {fib[n]} | Aranyarány: {fib[n]/fib[n-1] if fib[n-1]!=0 else 0:.3f} -> 1.618",
                         comparisons=n+1, extra={"phase": "done", "n": n, "result": fib[n], "fib": fib, "golden": fib[n]/fib[n-1] if fib[n-1]!=0 else 0})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class GCDPlugin(AlgorithmPluginBase):
    id = "gcd"
    name = "LNKO - Euklideszi"
    description = "Legnagyobb közös osztó, Euklidesz"
    time_complexity = "O(log min(a,b))"
    space_complexity = "O(1)"
    icon = "🔢"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - HES Projects® by FePe®"
    plugin_type = "simple"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("a", "a", "int", 48, 10, 100))
        self.params.add(Param("b", "b", "int", 18, 10, 100))
        self.complexity_level = "beginner"
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# LNKO - Legnagyobb közös osztó
# Euklideszi algoritmus: gcd(a,b) = gcd(b, a mod b)

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Példa: gcd(48,18)
# 48 % 18 = 12
# 18 % 12 = 6
# 12 % 6 = 0 -> LNKO = 6

# Használat: tört egyszerűsítés, RSA titkosítás
""",
        "C++": "// LNKO C++\nint gcd(int a, int b){ while(b!=0){ int r=a%b; a=b; b=r; } return a; }\n// gcd(48,18)=6\n// Rekurzív: int gcd(int a,int b){ if(b==0) return a; return gcd(b,a%b); }",
        "C": "/* LNKO C */\nint gcd(int a, int b){ while(b!=0){ int r=a%b; a=b; b=r; } return a; }\n// gcd(48,18)=6",
        "BASIC": "FUNCTION gcd(a AS INTEGER, b AS INTEGER) AS INTEGER: WHILE b<>0: r=a MOD b: a=b: b=r: WEND: RETURN a: END FUNCTION\n' gcd(48,18)=6",
        "Java": "// LNKO Java\nint gcd(int a, int b){ while(b!=0){ int r=a%b; a=b; b=r; } return a; }\n// gcd(48,18)=6",
        "Pascal": "function gcd(a,b: Integer): Integer; var r: Integer; begin while b<>0 do begin r:=a mod b; a:=b; b:=r; end; gcd:=a; end; // gcd(48,18)=6"
    }
    
    def get_steps(self, arr):
        a = self.params.get("a")
        b = self.params.get("b")
        
        yield SimpleStep(value=a, array=[a, b], code_line=2,
                         explanation=f"🔢 LNKO: gcd({a},{b}) | Kezdő 🟢 | Euklideszi algoritmus",
                         comparisons=0, extra={"phase": "init", "a": a, "b": b})
        
        steps = []
        orig_a, orig_b = a, b
        comp = 0
        while b != 0:
            r = a % b
            steps.append((a, b, r))
            comp += 1
            yield SimpleStep(value=r, array=[a, b, r], code_line=4,
                             explanation=f"{a} % {b} = {r} | gcd({a},{b}) -> gcd({b},{r})",
                             comparisons=comp, extra={"phase": "mod", "a": a, "b": b, "r": r, "orig_a": orig_a, "orig_b": orig_b})
            a, b = b, r
        
        yield SimpleStep(value=a, code_line=6,
                         explanation=f"✅ LNKO({orig_a},{orig_b}) = {a} | O(log min(a,b))",
                         comparisons=comp+1, extra={"phase": "done", "a": orig_a, "b": orig_b, "result": a, "steps": steps})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class SievePlugin(AlgorithmPluginBase):
    id = "sieve"
    name = "Prímszita - Eratoszthenész"
    description = "Prímek szitálása, vizuálisan szép"
    time_complexity = "O(n log log n)"
    space_complexity = "O(n)"
    icon = "🔍"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - HES Projects® by FePe®"
    plugin_type = "simple"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "n-ig", "int", 30, 10, 50))
        self.complexity_level = "easy"
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Prímszita - Eratoszthenész szitája
# Prímek keresése szitálással

def sieve(n):
    is_prime = [True]*(n+1)
    is_prime[0]=is_prime[1]=False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j]=False
    return [i for i in range(n+1) if is_prime[i]]

# n=30 -> [2,3,5,7,11,13,17,19,23,29]
# Vizuálisan: 2 kihúzza 4,6,8... 3 kihúzza 9,15...
""",
        "C++": "// Prímszita C++\nvector<int> sieve(int n){ vector<bool> prime(n+1,true); prime[0]=prime[1]=false; for(int i=2;i*i<=n;i++) if(prime[i]) for(int j=i*i;j<=n;j+=i) prime[j]=false; vector<int> res; for(int i=2;i<=n;i++) if(prime[i]) res.push_back(i); return res; }\n// 30 -> 2,3,5,7,11,13,17,19,23,29",
        "C": "/* Prímszita C */\nvoid sieve(int n){ bool prime[100]; for(int i=0;i<=n;i++) prime[i]=true; prime[0]=prime[1]=false; for(int i=2;i*i<=n;i++) if(prime[i]) for(int j=i*i;j<=n;j+=i) prime[j]=false; for(int i=2;i<=n;i++) if(prime[i]) printf(\"%d \", i); }",
        "BASIC": "FUNCTION sieve(n AS INTEGER) AS INTEGER: DIM prime(n) AS BOOLEAN: FOR i=0 TO n: prime(i)=TRUE: NEXT: prime(0)=FALSE: prime(1)=FALSE: FOR i=2 TO SQR(n): IF prime(i) THEN FOR j=i*i TO n STEP i: prime(j)=FALSE: NEXT: END IF: NEXT: END FUNCTION\n' 30 -> 2,3,5,7,11...",
        "Java": "// Prímszita Java\nList<Integer> sieve(int n){ boolean[] prime=new boolean[n+1]; Arrays.fill(prime,true); prime[0]=prime[1]=false; for(int i=2;i*i<=n;i++) if(prime[i]) for(int j=i*i;j<=n;j+=i) prime[j]=false; List<Integer> res=new ArrayList<>(); for(int i=2;i<=n;i++) if(prime[i]) res.add(i); return res; }",
        "Pascal": "function sieve(n: Integer): array of Integer; var prime: array of Boolean; i,j: Integer; begin SetLength(prime,n+1); for i:=0 to n do prime[i]:=True; prime[0]:=False; prime[1]:=False; for i:=2 to Trunc(Sqrt(n)) do if prime[i] then begin j:=i*i; while j<=n do begin prime[j]:=False; Inc(j,i); end; end; end;"
    }
    
    def get_steps(self, arr):
        n = self.params.get("n")
        
        is_prime = [True]*(n+1)
        is_prime[0]=is_prime[1]=False
        
        yield SimpleStep(value=n, array=list(range(n+1)), code_line=2,
                         explanation=f"🔍 Prímszita: 0..{n} | Könnyű 🟡 | Szitálás",
                         comparisons=0, extra={"phase": "init", "n": n, "is_prime": is_prime[:], "primes": []})
        
        comp = 0
        for i in range(2, int(n**0.5)+1):
            if is_prime[i]:
                comp += 1
                for j in range(i*i, n+1, i):
                    is_prime[j]=False
                yield SimpleStep(value=i, array=[idx for idx, val in enumerate(is_prime) if val], code_line=5,
                                 explanation=f"Prím {i}: kihúzza {i*i},{i*i+i},... | Prímek eddig: {[idx for idx, val in enumerate(is_prime) if val]}",
                                 comparisons=comp, extra={"phase": "sieve", "i": i, "is_prime": is_prime[:], "primes": [idx for idx, val in enumerate(is_prime) if val]})
        
        primes = [i for i in range(n+1) if is_prime[i]]
        yield SimpleStep(value=len(primes), array=primes, code_line=8,
                         explanation=f"✅ Prímek 0..{n}: {primes} | {len(primes)} db | O(n log log n)",
                         comparisons=comp+1, extra={"phase": "done", "n": n, "primes": primes, "count": len(primes)})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class HanoiPlugin(AlgorithmPluginBase):
    id = "hanoi"
    name = "Hanoi tornyai"
    description = "Rekurzív, vizuálisan klasszikus"
    time_complexity = "O(2^n)"
    space_complexity = "O(n)"
    icon = "🗼"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - HES Projects® by FePe®"
    plugin_type = "simple"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "Korongok", "int", 3, 2, 5))
        self.complexity_level = "easy"
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Hanoi tornyai - rekurzív
# 3 rúd, n korong, nagy nem lehet kicsire

def hanoi(n, source, target, aux):
    if n == 1:
        print(f"{source} -> {target}")
        return
    hanoi(n-1, source, aux, target)
    print(f"{source} -> {target}")
    hanoi(n-1, aux, target, source)

# n=3: 7 lépés, n=4: 15 lépés
# Lépések: 2^n -1
# Vizuálisan gyönyörű rekurzió!
""",
        "C++": "// Hanoi C++\nvoid hanoi(int n, char src, char dst, char aux){\n if(n==1){ cout<<src<<\"->\"<<dst<<endl; return; }\n hanoi(n-1,src,aux,dst);\n cout<<src<<\"->\"<<dst<<endl;\n hanoi(n-1,aux,dst,src); }\n// n=3 -> 7 lépés",
        "C": "/* Hanoi C */\nvoid hanoi(int n, char src, char dst, char aux){ if(n==1){ printf(\"%c->%c\\n\", src,dst); return; } hanoi(n-1,src,aux,dst); printf(\"%c->%c\\n\", src,dst); hanoi(n-1,aux,dst,src); }\n// 2^n -1 lépés",
        "BASIC": "SUB hanoi(n AS INTEGER, src AS STRING, dst AS STRING, aux AS STRING): IF n=1 THEN PRINT src;\"->\";dst: RETURN: hanoi n-1,src,aux,dst: PRINT src;\"->\";dst: hanoi n-1,aux,dst,src: END SUB\n' n=3 -> 7 lépés",
        "Java": "// Hanoi Java\nvoid hanoi(int n, char src, char dst, char aux){ if(n==1){ System.out.println(src+\"->\"+dst); return; } hanoi(n-1,src,aux,dst); System.out.println(src+\"->\"+dst); hanoi(n-1,aux,dst,src); }\n// 2^n -1",
        "Pascal": "procedure hanoi(n: Integer; src,dst,aux: Char); begin if n=1 then WriteLn(src,'->',dst) else begin hanoi(n-1,src,aux,dst); WriteLn(src,'->',dst); hanoi(n-1,aux,dst,src); end; end; // n=3 -> 7 lépés"
    }
    
    def get_steps(self, arr):
        n = self.params.get("n")
        
        yield SimpleStep(value=n, code_line=2,
                         explanation=f"🗼 Hanoi: {n} korong | Könnyű 🟡 | Rekurzív, {2**n-1} lépés",
                         comparisons=0, extra={"phase": "init", "n": n, "moves": []})
        
        moves = []
        def hanoi_rec(n, src, dst, aux, moves_list):
            if n == 1:
                moves_list.append((src, dst))
                return
            hanoi_rec(n-1, src, aux, dst, moves_list)
            moves_list.append((src, dst))
            hanoi_rec(n-1, aux, dst, src, moves_list)
        
        hanoi_rec(n, 'A', 'C', 'B', moves)
        
        for idx, (src, dst) in enumerate(moves):
            yield SimpleStep(value=idx+1, array=[src, dst], code_line=5,
                             explanation=f"Lépés {idx+1}/{len(moves)}: {src} -> {dst} | {2**n-1} lépés összesen",
                             comparisons=idx+1, extra={"phase": "move", "step": idx+1, "src": src, "dst": dst, "total": len(moves), "n": n})
        
        yield SimpleStep(value=len(moves), code_line=8,
                         explanation=f"✅ Hanoi {n} korong: {len(moves)} lépés = 2^{n}-1 | O(2^n)",
                         comparisons=len(moves)+1, extra={"phase": "done", "n": n, "moves": moves, "total": len(moves)})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
