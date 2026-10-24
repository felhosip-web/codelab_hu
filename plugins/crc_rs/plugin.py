# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.crc_rs import CRCCalculator, SimpleRS
import random

class CRCStep(VisualizationStep):
    def __init__(self, data="", generator="", current_data="", crc="", position=-1,
                 code_line=0, explanation="", comparisons=0, extra=None):
        e_dict = extra.copy() if extra else {}
        e_dict.update({
            "data": data, "generator": generator, "current_data": current_data,
            "crc": crc, "position": position
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            extra=e_dict
        )

class CRCPlugin(AlgorithmPluginBase):
    id = "crc"
    name = "CRC - Ciklikus Redundancia"
    description = "Hibafelismerés polinomosztással, Ethernet, ZIP, QR"
    time_complexity = "O(n*m)"
    space_complexity = "O(m)"
    icon = "✅"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "crc"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("data", "Adat bitek", "string", "11010011101100", description="Bináris"))
        self.params.add(Param("generator", "Generátor", "choice", "1011", choices=["1011", "1011 (CRC-3)", "1101", "10011 (CRC-4)", "11000000000000101 (CRC-16)"], description="Polinom"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val):
        # Choice-ból kiszedjük a biteket
        if pid=="generator" and "(" in val:
            val = val.split()[0]
        self.params.set(pid, val)
    
    codes = {
        "Python": """def crc_szamitas(adat_bitek, generator):
    # Adat + 0-k (generátor hossz-1 db)
    adat = adat_bitek + "0"*(len(generator)-1)
    adat_lista = list(adat)
    
    for i in range(len(adat_bitek)):
        if adat_lista[i] == '1':
            # XOR a generátorral
            for j in range(len(generator)):
                if generator[j] == '1':
                    adat_lista[i+j] = '0' if adat_lista[i+j]=='1' else '1'
    
    # Maradék = CRC
    crc = "".join(adat_lista)[-(len(generator)-1):]
    return crc

def crc_ellenorzes(adat_bitek, generator, crc):
    teljes = adat_bitek + crc
    teljes_lista = list(teljes)
    for i in range(len(adat_bitek)):
        if teljes_lista[i] == '1':
            for j in range(len(generator)):
                if generator[j] == '1':
                    teljes_lista[i+j] = '0' if teljes_lista[i+j]=='1' else '1'
    # Ha minden 0, nincs hiba
    return all(b=='0' for b in teljes_lista)

# Példa:
# adat=11010011101100, gen=1011
# adat+000 = 11010011101100000
# Osztás XOR-ral -> maradék 100 = CRC
# Küldött: 11010011101100100
# Vevő ellenőrzi: 0 maradék = OK, nem 0 = hiba
""",
        "C++": "// CRC C++\nstring crcCompute(string data, string gen){ string d=data+string(gen.length()-1,'0'); for(int i=0;i<data.length();i++){ if(d[i]=='1'){ for(int j=0;j<gen.length();j++){ if(gen[j]=='1') d[i+j]=(d[i+j]=='1'?'0':'1'); } } } return d.substr(d.length()-gen.length()+1); } bool crcCheck(string data, string gen, string crc){ string full=data+crc; for(int i=0;i<data.length();i++){ if(full[i]=='1'){ for(int j=0;j<gen.length();j++){ if(gen[j]=='1') full[i+j]=(full[i+j]=='1'?'0':'1'); } } } for(char c: full) if(c!='0') return false; return true; }",
        "C": "/* CRC C */\nvoid crcCompute(char* data, char* gen, char* crc){int n=strlen(data), m=strlen(gen); char d[256]; strcpy(d,data); for(int i=0;i<m-1;i++) strcat(d,\"0\"); for(int i=0;i<n;i++){ if(d[i]=='1'){ for(int j=0;j<m;j++){ if(gen[j]=='1') d[i+j]=(d[i+j]=='1'?'0':'1'); } } } strcpy(crc, d+n);}",
        "BASIC": "FUNCTION CRCCompute(data AS STRING, gen AS STRING) AS STRING: d=data+STRING$(LEN(gen)-1,\"0\"): FOR i=1 TO LEN(data): IF MID$(d,i,1)=\"1\" THEN FOR j=0 TO LEN(gen)-1: IF MID$(gen,j+1,1)=\"1\" THEN MID$(d,i+j,1)=IIF(MID$(d,i+j,1)=\"1\",\"0\",\"1\"): NEXT: NEXT: RETURN MID$(d, LEN(data)+1): END FUNCTION\nFUNCTION CRCCheck(data AS STRING, gen AS STRING, crc AS STRING) AS BOOLEAN: full=data+crc: FOR i=1 TO LEN(data): IF MID$(full,i,1)=\"1\" THEN FOR j=0 TO LEN(gen)-1: IF MID$(gen,j+1,1)=\"1\" THEN MID$(full,i+j,1)=IIF(MID$(full,i+j,1)=\"1\",\"0\",\"1\"): NEXT: NEXT: FOR i=1 TO LEN(full): IF MID$(full,i,1)<>\"0\" THEN RETURN FALSE: NEXT: RETURN TRUE: END FUNCTION",
        "Java": "String crcCompute(String data, String gen){ String d=data+\"0\".repeat(gen.length()-1); StringBuilder sb=new StringBuilder(d); for(int i=0;i<data.length();i++){ if(sb.charAt(i)=='1'){ for(int j=0;j<gen.length();j++){ if(gen.charAt(j)=='1'){ sb.setCharAt(i+j, sb.charAt(i+j)=='1'?'0':'1'); } } } } return sb.substring(sb.length()-gen.length()+1); } boolean crcCheck(String data, String gen, String crc){ String full=data+crc; StringBuilder sb=new StringBuilder(full); for(int i=0;i<data.length();i++){ if(sb.charAt(i)=='1'){ for(int j=0;j<gen.length();j++){ if(gen.charAt(j)=='1'){ sb.setCharAt(i+j, sb.charAt(i+j)=='1'?'0':'1'); } } } } for(int i=0;i<sb.length();i++) if(sb.charAt(i)!='0') return false; return true; }",
        "Pascal": "function CRCCompute(data, gen: string): string; var d: string; i,j: Integer; begin d:=data+StringOfChar('0', Length(gen)-1); for i:=1 to Length(data) do begin if d[i]='1' then begin for j:=0 to Length(gen)-1 do begin if gen[j+1]='1' then begin if d[i+j]='1' then d[i+j]:='0' else d[i+j]:='1'; end; end; end; end; Result:=Copy(d, Length(data)+1, Length(gen)-1); end; function CRCCheck(data, gen, crc: string): Boolean; var full: string; i,j: Integer; begin full:=data+crc; for i:=1 to Length(data) do begin if full[i]='1' then begin for j:=0 to Length(gen)-1 do begin if gen[j+1]='1' then begin if full[i+j]='1' then full[i+j]:='0' else full[i+j]:='1'; end; end; end; end; for i:=1 to Length(full) do if full[i]<>'0' then begin Result:=False; Exit; end; Result:=True; end;"
    }
    
    def get_steps(self, arr):
        data = self.params.get("data")
        gen = self.params.get("generator")
        # Tisztítsuk a gen-t (choice esetén)
        if "(" in gen:
            gen = gen.split()[0]
        gen = "".join([c for c in gen if c in "01"])
        if not gen:
            gen = "1011"
        data = "".join([c for c in data if c in "01"])
        
        yield CRCStep(data=data, generator=gen, current_data=data+"0"*(len(gen)-1), code_line=1,
                      explanation=f"✅ CRC: adat={data} ({len(data)} bit) gen={gen} ({len(gen)} bit)",
                      comparisons=0, extra={"data": data, "gen": gen, "phase": "init"})
        
        steps, crc = CRCCalculator.compute_crc_steps(data, gen)
        
        for idx, (current, pos, expl) in enumerate(steps):
            yield CRCStep(data=data, generator=gen, current_data=current, crc=crc if idx==len(steps)-1 else "", position=pos,
                          code_line=5+idx, explanation=expl,
                          comparisons=idx, extra={"data": data, "gen": gen, "current": current, "pos": pos, "crc": crc, "phase": "osztás", "step": idx})
        
        full = data + crc
        yield CRCStep(data=data, generator=gen, current_data=full, crc=crc, code_line=15,
                      explanation=f"✅ CRC={crc} | Küldött: {full} ({len(full)} bit)",
                      comparisons=len(steps), extra={"data": data, "gen": gen, "crc": crc, "full": full, "phase": "kész"})
        
        # Hibás átvitel szimulálása
        # Fordítsunk meg egy bitet
        error_pos = random.randint(0, len(full)-1)
        corrupted = list(full)
        corrupted[error_pos] = '0' if corrupted[error_pos]=='1' else '1'
        corrupted_str = "".join(corrupted)
        
        yield CRCStep(data=data, generator=gen, current_data=corrupted_str, crc=crc, code_line=18,
                      explanation=f"🔴 Hiba szimulálás: {error_pos}. bit megfordítva: {full} -> {corrupted_str}",
                      comparisons=len(steps)+1, extra={"data": data, "gen": gen, "full": full, "corrupted": corrupted_str, "error_pos": error_pos, "phase": "hiba"})
        
        # Ellenőrzés
        is_ok = CRCCalculator.verify(data, gen, crc)
        is_corrupted_ok = CRCCalculator.verify(corrupted_str[:len(data)], gen, corrupted_str[len(data):]) if len(corrupted_str)>=len(data) else False
        # Egyszerűsített ellenőrzés: a corrupted teljes üzenetet ellenőrizzük
        # CRC ellenőrzés a corrupted full-ra
        full_check = corrupted_str
        for i in range(len(data)):
            if full_check[i]=='1':
                for j in range(len(gen)):
                    if gen[j]=='1':
                        full_check = full_check[:i+j] + ('0' if full_check[i+j]=='1' else '1') + full_check[i+j+1:]
        has_error = any(b=='1' for b in full_check)
        
        yield CRCStep(data=data, generator=gen, current_data=corrupted_str, crc=crc, code_line=20,
                      explanation=f"{'❌ HIBA ÉSZLELVE' if has_error else '✅ Nincs hiba'} | Eredeti OK: {is_ok} | Sérült maradék: {full_check}",
                      comparisons=len(steps)+2, extra={"data": data, "gen": gen, "full": full, "corrupted": corrupted_str, "has_error": has_error, "check": full_check, "phase": "ellenőrzés"})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class RSPlugin(AlgorithmPluginBase):
    id = "reed_solomon"
    name = "Reed-Solomon kód"
    description = "Hibajavító kód, QR, CD, műhold: n=k+2t"
    time_complexity = "O(n*k)"
    space_complexity = "O(n)"
    icon = "🛰️"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "crc"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("data", "Adat", "string", "1,2,3", description="GF(p)-ben, vesszővel, 0<=x<p"))
        self.params.add(Param("n", "Kódszó hossz n", "int", 7, 5, 10, description="n=k+2t"))
        self.params.add(Param("k", "Adat hossz k", "int", 3, 2, 5, description="k < n"))
        self.params.add(Param("p", "Prím mező p", "choice", "7", choices=["7", "11", "13"], description="GF(p)"))
        self.params.add(Param("errors", "Hibák száma", "int", 1, 0, 2, description="Hány hibát szimuláljunk"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Egyszerűsített Reed-Solomon GF(p) felett (prím mező)
# Valódi RS GF(2^8)-ban van, de elv ugyanaz

def rs_kodolas(adat, n, k, p):
    # adat: k hosszú lista GF(p)-ben
    # f(x) = adat[0] + adat[1]*x + ... + adat[k-1]*x^(k-1)
    # kódszó: [f(0), f(1), ..., f(n-1)] mod p
    kodszó=[]
    for x in range(n):
        ertek=0
        for i, coeff in enumerate(adat):
            ertek = (ertek + coeff * pow(x, i, p)) % p
        kodszó.append(ertek)
    return kodszó

def rs_hiba_hozzaadas(kodszó, hiba_poziciok, p):
    sérült=kodszó[:]
    for pos in hiba_poziciok:
        sérült[pos] = (sérült[pos] + 1) % p  # +1 hiba
    return sérült

def rs_dekodolas(vett, n, k, p):
    # Berlekamp-Massey helyett egyszerű: keresünk k pontot ami konzisztens
    # Ha max t = (n-k)//2 hiba van, akkor van ilyen
    from itertools import combinations
    for indices in combinations(range(n), k):
        # Lagrange interpoláció
        y_vals=[vett[i] for i in indices]
        x_vals=list(indices)
        # ... interpolálás ...
        # Vandermonde megoldás mod p
        adat = lagrange_interpolal(y_vals, x_vals, p, k)
        kodolt = rs_kodolas(adat, n, k, p)
        hibak = sum(1 for i in range(n) if kodolt[i]!=vett[i])
        if hibak <= (n-k)//2:
            return adat, kodolt, hibak, indices
    return None

# Példa: n=7, k=3, p=7, adat=[1,2,3]
# f(x)=1+2x+3x^2
# f(0)=1, f(1)=6, f(2)=3, f(3)=6, f(4)=1, f(5)=2, f(6)=2
# kódszó [1,6,3,6,1,2,2] - 4 paritás szimbólum!
# Ha 1 hiba van (n-k=4, t=2, javítható 2 hiba), dekódolható
""",
        "C++": "// Reed-Solomon egyszerűsített GF(p)\nvector<int> rsEncode(vector<int> data, int n, int k, int p){ vector<int> cw(n); for(int x=0;x<n;x++){ int val=0; for(int i=0;i<k;i++){ int pow=1; for(int j=0;j<i;j++) pow=(pow*x)%p; val=(val+data[i]*pow)%p; } cw[x]=val; } return cw; } vector<int> rsAddErrors(vector<int> cw, vector<int> errPos, int p){ vector<int> corrupted=cw; for(int pos: errPos) corrupted[pos]=(corrupted[pos]+1)%p; return corrupted; } // dekódolás Lagrange interpoláció...",
        "C": "/* Reed-Solomon C GF(p) */\nvoid rsEncode(int* data, int k, int n, int p, int* cw){for(int x=0;x<n;x++){int val=0; for(int i=0;i<k;i++){int pow=1; for(int j=0;j<i;j++) pow=(pow*x)%p; val=(val+data[i]*pow)%p;} cw[x]=val;}} void rsAddErrors(int* cw, int n, int* errPos, int errCount, int p){for(int i=0;i<errCount;i++){int pos=errPos[i]; cw[pos]=(cw[pos]+1)%p;}}",
        "BASIC": "SUB RSEncode(data() AS INTEGER, k AS INTEGER, n AS INTEGER, p AS INTEGER, cw() AS INTEGER): FOR x=0 TO n-1: val=0: FOR i=0 TO k-1: pow=1: FOR j=0 TO i-1: pow=(pow*x) MOD p: NEXT: val=(val+data(i)*pow) MOD p: NEXT: cw(x)=val: NEXT: END SUB\nSUB RSAddErrors(cw() AS INTEGER, errPos() AS INTEGER, errCount AS INTEGER, p AS INTEGER): FOR i=0 TO errCount-1: pos=errPos(i): cw(pos)=(cw(pos)+1) MOD p: NEXT: END SUB",
        "Java": "List<Integer> rsEncode(List<Integer> data, int n, int k, int p){ List<Integer> cw=new ArrayList<>(); for(int x=0;x<n;x++){ int val=0; for(int i=0;i<k;i++){ int pow=1; for(int j=0;j<i;j++) pow=(pow*x)%p; val=(val+data.get(i)*pow)%p; } cw.add(val); } return cw; } List<Integer> rsAddErrors(List<Integer> cw, List<Integer> errPos, int p){ List<Integer> corrupted=new ArrayList<>(cw); for(int pos: errPos) corrupted.set(pos, (corrupted.get(pos)+1)%p); return corrupted; }",
        "Pascal": "procedure RSEncode(data: array of Integer; k,n,p: Integer; var cw: array of Integer); var x,val,i,j,pow: Integer; begin for x:=0 to n-1 do begin val:=0; for i:=0 to k-1 do begin pow:=1; for j:=0 to i-1 do pow:=(pow*x) mod p; val:=(val+data[i]*pow) mod p; end; cw[x]:=val; end; end; procedure RSAddErrors(var cw: array of Integer; errPos: array of Integer; errCount,p: Integer); var i,pos: Integer; begin for i:=0 to errCount-1 do begin pos:=errPos[i]; cw[pos]:=(cw[pos]+1) mod p; end; end;"
    }
    
    def get_steps(self, arr):
        data_str = self.params.get("data")
        n = self.params.get("n")
        k = self.params.get("k")
        p = int(self.params.get("p"))
        err_count = self.params.get("errors")
        
        try:
            data = [int(x.strip())%p for x in data_str.split(",") if x.strip()!=""]
        except:
            data = [1,2,3]
        data = data[:k]
        while len(data)<k:
            data.append(0)
        
        if k>=n:
            k=n-1
        t = (n-k)//2
        
        rs = SimpleRS(n=n, k=k, p=p)
        
        yield CRCStep(data=",".join(map(str,data)), code_line=1,
                      explanation=f"🛰️ Reed-Solomon: n={n}, k={k}, p={p}, t={(n-k)//2} hibát javít | adat={data} GF({p})-ben",
                      comparisons=0, extra={"data": data, "n": n, "k": k, "p": p, "t": t, "phase": "init"})
        
        # Polinom
        poly_str = " + ".join([f"{data[i]}*x^{i}" if i>0 else f"{data[i]}" for i in range(k)])
        yield CRCStep(data=",".join(map(str,data)), code_line=5,
                      explanation=f"f(x) = {poly_str} mod {p}",
                      comparisons=0, extra={"data": data, "poly": poly_str, "n": n, "k": k, "p": p, "phase": "polinom"})
        
        # Kódolás
        codeword = rs.encode(data)
        yield CRCStep(data=",".join(map(str,data)), code_line=10,
                      explanation=f"Kódolás: f(0)..f({n-1}) = {codeword} | {k} adat + {n-k} paritás",
                      comparisons=0, extra={"data": data, "codeword": codeword, "n": n, "k": k, "p": p, "phase": "kódol"})
        
        # Részletes értékelés
        for x in range(n):
            val = 0
            calc_steps = []
            for i, coeff in enumerate(data):
                term = coeff * pow(x, i, p) % p
                val = (val + term) % p
                calc_steps.append(f"{coeff}*{x}^{i}={term}")
            yield CRCStep(data=",".join(map(str,data)), code_line=12,
                          explanation=f"f({x}) = {' + '.join(calc_steps)} = {val} mod {p}",
                          comparisons=x+1, extra={"data": data, "x": x, "val": val, "codeword": codeword, "phase": "értékelés"})
        
        # Hibák hozzáadása
        error_positions = random.sample(range(n), min(err_count, n)) if err_count>0 else []
        corrupted = rs.add_errors(codeword, error_positions)
        
        yield CRCStep(data=",".join(map(str,data)), code_line=20,
                      explanation=f"🔴 Hibák szimulálása: {error_positions} pozíciókon +1 | {codeword} -> {corrupted}",
                      comparisons=n, extra={"data": data, "codeword": codeword, "corrupted": corrupted, "errors": error_positions, "n": n, "k": k, "p": p, "phase": "hiba"})
        
        # Dekódolás
        decoded_data, re_encoded, error_num, used_indices = rs.decode(corrupted)
        
        if decoded_data is not None:
            yield CRCStep(data=",".join(map(str,data)), code_line=25,
                          explanation=f"✅ Dekódolva: {used_indices} pontokból interpolálva {decoded_data} | Újrakódolva {re_encoded} | {error_num} hiba javítva",
                          comparisons=n+1, extra={"data": data, "codeword": codeword, "corrupted": corrupted, "decoded": decoded_data, "re_encoded": re_encoded, "errors": error_positions, "used": used_indices, "phase": "javítás"})
            
            yield CRCStep(data=",".join(map(str,data)), code_line=30,
                          explanation=f"✅ Reed-Solomon sikeres! Eredeti {data} == Dekódolt {decoded_data} | {error_num} hiba javítva t={t} kapacitásból",
                          comparisons=n+2, extra={"data": data, "decoded": decoded_data, "codeword": codeword, "corrupted": corrupted, "success": True, "n": n, "k": k, "p": p, "t": t, "phase": "kész"})
        else:
            yield CRCStep(data=",".join(map(str,data)), code_line=25,
                          explanation=f"❌ Dekódolás sikertelen: túl sok hiba ({err_count} > t={t})",
                          comparisons=n+1, extra={"data": data, "codeword": codeword, "corrupted": corrupted, "errors": error_positions, "phase": "hiba", "success": False})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
