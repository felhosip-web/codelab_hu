# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
import math

class WowStep(VisualizationStep):
    def __init__(self, value=None, array=None, binary=None, nodes=None, pattern=None, extra_data=None, code_line=0, explanation="", comparisons=0, extra=None):
        arr = array or []
        e_dict = extra.copy() if extra else {}
        if extra_data:
            e_dict.update(extra_data)
        e_dict.update({
            "value": value, "binary": binary or "",
            "nodes": nodes or [], "pattern": pattern or []
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=arr,
            key=value,
            extra=e_dict
        )

class BinaryBitsPlugin(AlgorithmPluginBase):
    id = "binary_bits"
    name = "Bitek - bináris varázs"
    description = "Bit villogás, shift, AND OR XOR, wow!"
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "💡"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("num", "Szám", "int", 13, 1, 31))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Bitek - bináris varázs 💡
# 13 = 01101

n = 13
binary = bin(n)[2:]  # 1101
# Bit műveletek:
# n & 1 -> páros?
# n << 1 -> *2
# n >> 1 -> /2
# n ^ n -> 0
# Villogás: 13 = 8+4+1 = 1101

# Wow: bitek ki/be kapcsolása!
""",
        "C++": "// Bitek C++\nint n=13; // 1101\nbool isEven = !(n & 1);\nint doubleN = n << 1; // *2\nint halfN = n >> 1; // /2\nint bits = __builtin_popcount(n); // 3 db 1-es\n// Wow bit villogás",
        "C": "/* Bitek C */\nint n=13; // 1101\nint even = !(n & 1);\nint dbl = n << 1;\nint half = n >> 1;\n// bit count",
        "BASIC": "n=13 ' 1101\nisEven = (n AND 1)=0\n\ndbl = n * 2\n' bit villogás",
        "Java": "// Bitek Java\nint n=13; // 1101\nboolean even = (n & 1)==0;\nint dbl = n << 1;\nint bits = Integer.bitCount(n); // 3\n// Wow",
        "Pascal": "var n: Integer; begin n:=13; // 1101\nif n and 1 =0 then WriteLn('páros');\nn:=n shl 1; // *2\n// bit villogás\nend;"
    }
    def get_steps(self, arr):
        num = self.params.get("num")
        binary = format(num, '05b')
        yield WowStep(value=num, binary=binary, code_line=2, explanation=f"💡 Bitek: {num} = {binary} | 5 bit, wow villogás!", comparisons=0, extra={"phase": "init", "num": num, "binary": binary, "bits": binary})
        # Bit vizsgálat
        for i, bit in enumerate(reversed(binary)):
            idx = len(binary)-1-i
            yield WowStep(value=int(bit), binary=binary, code_line=4, explanation=f"Bit {idx}: {bit} = {2**i} | {num} & {2**i} = {int(bit)*2**i}", comparisons=i+1, extra={"phase": "bit", "idx": idx, "bit": bit, "value": 2**i, "binary": binary})
        # Shift
        left = num << 1
        yield WowStep(value=left, binary=format(left, '05b'), code_line=6, explanation=f"{num} << 1 = {left} = {format(left, '05b')} | *2 wow!", comparisons=6, extra={"phase": "shift_left", "num": num, "result": left, "binary": format(left, '05b')})
        right = num >> 1
        yield WowStep(value=right, binary=format(right, '05b'), code_line=7, explanation=f"{num} >> 1 = {right} = {format(right, '05b')} | /2 wow!", comparisons=7, extra={"phase": "shift_right", "num": num, "result": right, "binary": format(right, '05b')})
        yield WowStep(value=num, binary=binary, code_line=8, explanation=f"✅ {num} = {binary} | {binary.count('1')} db 1-es bit | Páros? {num%2==0}", comparisons=8, extra={"phase": "done", "num": num, "binary": binary, "ones": binary.count('1')})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class PalindromePlugin(AlgorithmPluginBase):
    id = "palindrome"
    name = "Palindrom - tükör"
    description = "racecar visszafelé is racecar, tükör wow!"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    icon = "🪞"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("word", "Szó", "choice", "racecar", choices=["racecar", "level", "madam", "hello", "abccba", "görög"]))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Palindrom - tükör 🪞
# racecar visszafelé is racecar!

def is_palindrome(s):
    left, right = 0, len(s)-1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# racecar -> True, hello -> False
# Wow: két mutató közeledik egymáshoz!
""",
        "C++": "// Palindrom C++\nbool isPalindrome(string s){ int l=0,r=s.size()-1; while(l<r){ if(s[l]!=s[r]) return false; l++; r--; } return true; }\n// racecar True",
        "C": "/* Palindrom C */\nint isPalindrome(char* s){ int l=0,r=strlen(s)-1; while(l<r){ if(s[l]!=s[r]) return 0; l++; r--; } return 1; }\n// racecar",
        "BASIC": "FUNCTION isPalindrome(s AS STRING) AS BOOLEAN: l=1: r=LEN(s): WHILE l<r: IF MID(s,l,1)<>MID(s,r,1) THEN RETURN FALSE: l=l+1: r=r-1: WEND: RETURN TRUE: END FUNCTION\n' racecar True",
        "Java": "// Palindrom Java\nboolean isPalindrome(String s){ int l=0,r=s.length()-1; while(l<r){ if(s.charAt(l)!=s.charAt(r)) return false; l++; r--; } return true; }\n// racecar",
        "Pascal": "function isPalindrome(s: string): Boolean; var l,r: Integer; begin l:=1; r:=Length(s); while l<r do begin if s[l]<>s[r] then Exit(False); Inc(l); Dec(r); end; isPalindrome:=True; end; // racecar"
    }
    def get_steps(self, arr):
        word = self.params.get("word")
        yield WowStep(value=word, array=list(word), code_line=2, explanation=f"🪞 Palindrom: '{word}' | Tükör? | Kezdő 🟢", comparisons=0, extra={"phase": "init", "word": word, "len": len(word)})
        left, right = 0, len(word)-1
        comp = 0
        while left < right:
            comp += 1
            match = word[left] == word[right]
            yield WowStep(value=word, array=list(word), code_line=5, explanation=f"Bal {left}='{word[left]}' vs Jobb {right}='{word[right]}' -> {'egyezik' if match else 'NEM egyezik!'} | Tükör", comparisons=comp, extra={"phase": "check", "left": left, "right": right, "lchar": word[left], "rchar": word[right], "match": match, "word": word})
            if not match:
                break
            left += 1
            right -= 1
        is_pal = word == word[::-1]
        yield WowStep(value=is_pal, array=list(word), code_line=9, explanation=f"{'✅' if is_pal else '❌'} '{word}' {'palindrom' if is_pal else 'NEM palindrom'} | Tükör: {word} vs {word[::-1]}", comparisons=comp+1, extra={"phase": "done", "word": word, "is_palindrome": is_pal, "reverse": word[::-1]})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class PowerPlugin(AlgorithmPluginBase):
    id = "power"
    name = "Hatvány - 2^10 wow!"
    description = "Gyors hatványozás, exponenciális növekedés"
    time_complexity = "O(log n)"
    space_complexity = "O(1)"
    icon = "🚀"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("base", "Alap", "int", 2, 2, 5))
        self.params.add(Param("exp", "Kitevő", "int", 8, 3, 10))
        self.complexity_level = "beginner"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Hatvány - 2^10 = 1024 🚀
# Gyors hatványozás O(log n)

def power(base, exp):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2
    return result

# 2^10 = 1024
# 2^0=1, 2^1=2, 2^2=4, 2^3=8... exponenciális wow!
""",
        "C++": "// Hatvány C++\nlong long power(int base, int exp){ long long res=1; while(exp>0){ if(exp&1) res*=base; base*=base; exp>>=1; } return res; }\n// 2^10=1024",
        "C": "/* Hatvány C */\nlong long power(int b, int e){ long long r=1; while(e>0){ if(e&1) r*=b; b*=b; e>>=1; } return r; }\n// 2^10=1024",
        "BASIC": "FUNCTION power(base AS INTEGER, exp AS INTEGER) AS LONG: r=1: WHILE exp>0: IF exp MOD 2=1 THEN r=r*base: base=base*base: exp=exp\\2: WEND: RETURN r: END FUNCTION\n' 2^10=1024",
        "Java": "// Hatvány Java\nlong power(int base, int exp){ long r=1; while(exp>0){ if((exp&1)==1) r*=base; base*=base; exp>>=1; } return r; }\n// 2^10=1024",
        "Pascal": "function power(base,exp: Integer): LongInt; var r: LongInt; begin r:=1; while exp>0 do begin if exp mod 2=1 then r:=r*base; base:=base*base; exp:=exp div 2; end; power:=r; end; // 2^10=1024"
    }
    def get_steps(self, arr):
        base = self.params.get("base")
        exp = self.params.get("exp")
        yield WowStep(value=1, code_line=2, explanation=f"🚀 Hatvány: {base}^{exp} | Kezdő 🟢 | Exponenciális wow!", comparisons=0, extra={"phase": "init", "base": base, "exp": exp})
        result = 1
        b = base
        e = exp
        step = 0
        powers = []
        while e > 0:
            step += 1
            if e % 2 == 1:
                result *= b
                powers.append(f"{b}")
            yield WowStep(value=result, array=powers[:], code_line=5, explanation=f"Lépés {step}: exp={e} b={b} result={result} | {base}^{exp}={result} (részben)", comparisons=step, extra={"phase": "pow", "exp": e, "base": b, "result": result, "base_orig": base, "exp_orig": exp})
            b *= b
            e //= 2
        yield WowStep(value=result, code_line=9, explanation=f"✅ {base}^{exp} = {result} | O(log n) gyors! | 2^10=1024, 2^20=1M, 2^30=1B wow!", comparisons=step+1, extra={"phase": "done", "base": base, "exp": exp, "result": result})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class CountingSortPlugin(AlgorithmPluginBase):
    id = "counting_sort"
    name = "Számláló rendezés"
    description = "O(n+k), vödrök, vizuálisan wow!"
    time_complexity = "O(n+k)"
    space_complexity = "O(k)"
    icon = "🪣"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("size", "Méret", "int", 10, 5, 15))
        self.params.add(Param("max_val", "Max", "int", 5, 3, 8))
        self.complexity_level = "easy"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Számláló rendezés 🪣 O(n+k)
# Ha kicsi a max érték, brutál gyors!

def counting_sort(arr):
    max_val = max(arr)
    count = [0]*(max_val+1)
    for num in arr:
        count[num] += 1
    sorted_arr = []
    for i in range(len(count)):
        sorted_arr.extend([i]*count[i])
    return sorted_arr

# [2,1,3,2,1] -> count[0,2,2,1] -> [1,1,2,2,3]
# Wow: vödrök, számlálás!
""",
        "C++": "// Számláló rendezés C++\nvoid countingSort(vector<int>& arr){ int maxVal=*max_element(arr.begin(),arr.end()); vector<int> count(maxVal+1,0); for(int n:arr) count[n]++; int idx=0; for(int i=0;i<=maxVal;i++) for(int j=0;j<count[i];j++) arr[idx++]=i; }\n// O(n+k)",
        "C": "/* Számláló rendezés C */\nvoid countingSort(int* arr, int n){ int max=arr[0]; for(int i=1;i<n;i++) if(arr[i]>max) max=arr[i]; int count[max+1]; for(int i=0;i<=max;i++) count[i]=0; for(int i=0;i<n;i++) count[arr[i]]++; int idx=0; for(int i=0;i<=max;i++) for(int j=0;j<count[i];j++) arr[idx++]=i; }",
        "BASIC": "SUB countingSort(arr() AS INTEGER): max=arr(0): FOR i=1 TO UBOUND(arr): IF arr(i)>max THEN max=arr(i): NEXT: DIM count(max) AS INTEGER: FOR i=0 TO UBOUND(arr): count(arr(i))=count(arr(i))+1: NEXT: idx=0: FOR i=0 TO max: FOR j=1 TO count(i): arr(idx)=i: idx=idx+1: NEXT: NEXT: END SUB\n' O(n+k)",
        "Java": "// Számláló rendezés Java\nvoid countingSort(int[] arr){ int max=Arrays.stream(arr).max().getAsInt(); int[] count=new int[max+1]; for(int n:arr) count[n]++; int idx=0; for(int i=0;i<=max;i++) for(int j=0;j<count[i];j++) arr[idx++]=i; }\n// O(n+k)",
        "Pascal": "procedure countingSort(var arr: array of Integer); var max,count: array of Integer; i,j,idx: Integer; begin max:=arr[0]; for i:=1 to High(arr) do if arr[i]>max then max:=arr[i]; SetLength(count,max+1); for i:=0 to High(arr) do Inc(count[arr[i]]); idx:=0; for i:=0 to max do for j:=1 to count[i] do begin arr[idx]:=i; Inc(idx); end; end;"
    }
    def get_steps(self, arr):
        import random
        size = self.params.get("size")
        max_val = self.params.get("max_val")
        array = [random.randint(0, max_val) for _ in range(size)]
        yield WowStep(array=array, code_line=2, explanation=f"🪣 Számláló rendezés: {array} | max={max_val} | Könnyű 🟡", comparisons=0, extra={"phase": "init", "array": array, "max": max_val})
        count = [0]*(max_val+1)
        for num in array:
            count[num] += 1
            yield WowStep(array=array, extra_data={"count": count[:]}, code_line=5, explanation=f"Számlál: {num} -> count[{num}]={count[num]} | Vödrök: {count}", comparisons=count[num], extra={"phase": "count", "num": num, "count": count[:], "array": array})
        sorted_arr = []
        for i in range(len(count)):
            for _ in range(count[i]):
                sorted_arr.append(i)
                yield WowStep(array=sorted_arr, extra_data={"count": count[:]}, code_line=8, explanation=f"Kiír: {i} x{count[i]} -> {sorted_arr}", comparisons=len(sorted_arr), extra={"phase": "write", "i": i, "sorted": sorted_arr[:], "count": count[:]})
        yield WowStep(array=sorted_arr, code_line=10, explanation=f"✅ Rendezve: {sorted_arr} | O(n+k)={size+max_val} wow gyors ha kicsi a max!", comparisons=len(sorted_arr), extra={"phase": "done", "sorted": sorted_arr, "count": count})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class LinkedListPlugin(AlgorithmPluginBase):
    id = "linked_list"
    name = "Láncolt lista"
    description = "Node-ok nyilakkal, pointer lánc wow!"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "🔗"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("size", "Méret", "int", 5, 3, 8))
        self.complexity_level = "easy"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Láncolt lista 🔗
# Node-ok nyilakkal: [10]->[20]->[30]->None

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = new_node

# Wow: nyilak, pointer lánc!
""",
        "C++": "// Láncolt lista C++\nstruct Node{ int data; Node* next; Node(int d): data(d), next(nullptr) {} };\nclass LinkedList{ Node* head; public: LinkedList(): head(nullptr) {} void append(int d){ Node* n=new Node(d); if(!head){ head=n; return; } Node* cur=head; while(cur->next) cur=cur->next; cur->next=n; } };\n// [10]->[20]->[30]->nullptr",
        "C": "/* Láncolt lista C */\nstruct Node{ int data; struct Node* next; };\nvoid append(struct Node** head, int d){ struct Node* n=malloc(sizeof(struct Node)); n->data=d; n->next=NULL; if(!*head){ *head=n; return; } struct Node* cur=*head; while(cur->next) cur=cur->next; cur->next=n; }\n// [10]->[20]->[30]->NULL",
        "BASIC": "TYPE Node: data AS INTEGER: next AS INTEGER: END TYPE\nDIM list(100) AS Node: head=-1\nSUB append(d AS INTEGER): newNode=UBOUND(list)+1: list(newNode).data=d: IF head=-1 THEN head=newNode ELSE cur=head: WHILE list(cur).next<>-1: cur=list(cur).next: WEND: list(cur).next=newNode: END IF: END SUB\n' [10]->[20]->[30]",
        "Java": "// Láncolt lista Java\nclass Node{ int data; Node next; Node(int d){ data=d; } }\nclass LinkedList{ Node head; void append(int d){ Node n=new Node(d); if(head==null){ head=n; return; } Node cur=head; while(cur.next!=null) cur=cur.next; cur.next=n; } }\n// [10]->[20]->[30]->null",
        "Pascal": "type PNode = ^Node; Node = record data: Integer; next: PNode; end; procedure append(var head: PNode; d: Integer); var n,cur: PNode; begin New(n); n^.data:=d; n^.next:=nil; if head=nil then head:=n else begin cur:=head; while cur^.next<>nil do cur:=cur^.next; cur^.next:=n; end; end; // [10]->[20]->[30]->nil"
    }
    def get_steps(self, arr):
        import random
        size = self.params.get("size")
        values = [random.randint(1, 20) for _ in range(size)]
        nodes = []
        for i, val in enumerate(values):
            nodes.append(val)
            yield WowStep(array=nodes[:], nodes=nodes[:], code_line=6, explanation=f"🔗 Append {val} -> {' -> '.join(map(str, nodes))} -> None | Lánc {i+1}/{size}", comparisons=i+1, extra={"phase": "append", "value": val, "nodes": nodes[:], "size": size})
        # Traversal
        for i, val in enumerate(nodes):
            yield WowStep(array=nodes, nodes=nodes, code_line=10, explanation=f"Bejárás {i}: Node {val} -> {nodes[i+1] if i+1<len(nodes) else 'None'} | Nyíl!", comparisons=size+i+1, extra={"phase": "traverse", "idx": i, "value": val, "nodes": nodes})
        yield WowStep(array=nodes, nodes=nodes, code_line=12, explanation=f"✅ Láncolt lista: {' -> '.join(map(str, nodes))} -> None | O(n) wow pointer lánc!", comparisons=size*2, extra={"phase": "done", "nodes": nodes})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class PrimeFactorPlugin(AlgorithmPluginBase):
    id = "prime_factor"
    name = "Prímtényezős felbontás"
    description = "60 = 2*2*3*5 fa wow!"
    time_complexity = "O(sqrt(n))"
    space_complexity = "O(log n)"
    icon = "🌳"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU - Hes Projects ® by FePe"
    plugin_type = "simple"
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("n", "Szám", "int", 60, 12, 100))
        self.complexity_level = "easy"
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    codes = {
        "Python": """# Prímtényezős felbontás 🌳
# 60 = 2*2*3*5

def prime_factors(n):
    factors = []
    d = 2
    while d*d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

# 60 -> [2,2,3,5]
# Fa: 60
#    /  \\
#   2   30
#       / \\
#      2  15
#         / \\
#        3   5
""",
        "C++": "// Prímtényezős C++\nvector<int> primeFactors(int n){ vector<int> f; for(int d=2; d*d<=n; d++){ while(n%d==0){ f.push_back(d); n/=d; } } if(n>1) f.push_back(n); return f; }\n// 60 -> 2,2,3,5",
        "C": "/* Prímtényezős C */\nvoid primeFactors(int n){ for(int d=2; d*d<=n; d++){ while(n%d==0){ printf(\"%d \", d); n/=d; } } if(n>1) printf(\"%d \", n); }\n// 60 -> 2 2 3 5",
        "BASIC": "FUNCTION primeFactors(n AS INTEGER) AS INTEGER: DIM f(100) AS INTEGER: idx=0: d=2: WHILE d*d<=n: WHILE n MOD d=0: f(idx)=d: idx=idx+1: n=n\\d: WEND: d=d+1: WEND: IF n>1 THEN f(idx)=n: END FUNCTION\n' 60 -> 2,2,3,5",
        "Java": "// Prímtényezős Java\nList<Integer> primeFactors(int n){ List<Integer> f=new ArrayList<>(); for(int d=2; d*d<=n; d++){ while(n%d==0){ f.add(d); n/=d; } } if(n>1) f.add(n); return f; }\n// 60 -> 2,2,3,5",
        "Pascal": "function primeFactors(n: Integer): array of Integer; var d: Integer; f: array of Integer; begin SetLength(f,0); d:=2; while d*d<=n do begin while n mod d=0 do begin SetLength(f,Length(f)+1); f[High(f)]:=d; n:=n div d; end; Inc(d); end; if n>1 then begin SetLength(f,Length(f)+1); f[High(f)]:=n; end; primeFactors:=f; end; // 60 -> 2,2,3,5"
    }
    def get_steps(self, arr):
        n = self.params.get("n")
        orig = n
        yield WowStep(value=n, code_line=2, explanation=f"🌳 Prímtényezős: {n} | Könnyű 🟡 | Fa wow!", comparisons=0, extra={"phase": "init", "n": n})
        factors = []
        d = 2
        comp = 0
        while d*d <= n:
            while n % d == 0:
                factors.append(d)
                comp += 1
                yield WowStep(value=d, array=factors[:], code_line=6, explanation=f"{orig} = {'*'.join(map(str, factors))} * {n//d if n//d>1 else ''} | Faktor: {d} | Fa ág!", comparisons=comp, extra={"phase": "factor", "d": d, "factors": factors[:], "n": n, "orig": orig})
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
            yield WowStep(value=n, array=factors[:], code_line=9, explanation=f"Maradék prím: {n} | {orig} = {'*'.join(map(str, factors))}", comparisons=comp+1, extra={"phase": "prime", "factors": factors[:], "orig": orig})
        yield WowStep(value=len(factors), array=factors, code_line=11, explanation=f"✅ {orig} = {' * '.join(map(str, factors))} | {len(factors)} tényező | O(sqrt(n))", comparisons=comp+2, extra={"phase": "done", "orig": orig, "factors": factors})
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
