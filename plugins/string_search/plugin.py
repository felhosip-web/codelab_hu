# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.string_matching import KMPMatcher, RabinKarpMatcher

class StringStep(VisualizationStep):
    def __init__(self, text: str, pattern: str, text_pos=0, pattern_pos=0,
                 lps=None, hash_text=None, hash_pattern=None,
                 highlight_text=None, highlight_pattern=None,
                 code_line=0, explanation="", comparisons=0, extra=None, found_positions=None):
        e_dict = extra.copy() if extra else {}
        e_dict.update({
            "text": text, "pattern": pattern, "text_pos": text_pos, "pattern_pos": pattern_pos,
            "lps": lps or [], "hash_text": hash_text, "hash_pattern": hash_pattern,
            "highlight_text": highlight_text or [], "highlight_pattern": highlight_pattern or [],
            "found_positions": found_positions or []
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=list(text),
            extra=e_dict
        )

class KMPPlugin(AlgorithmPluginBase):
    id = "kmp"
    name = "KMP - Knuth-Morris-Pratt"
    description = "Előre számított LPS táblával átugorja a felesleges összehasonlításokat"
    time_complexity = "O(n+m)"
    space_complexity = "O(m)"
    icon = "📝"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "string"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "ABABDABACDABABCABAB", description="Keresendő"))
        self.params.add(Param("pattern", "Minta", "string", "ABABCABAB", description="Keresett"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def compute_lps(minta):
    # Longest Prefix Suffix - leghosszabb prefix ami suffix is
    m=len(minta)
    lps=[0]*m
    hossz=0
    i=1
    while i<m:
        if minta[i]==minta[hossz]:
            hossz+=1
            lps[i]=hossz
            i+=1
        else:
            if hossz!=0:
                hossz=lps[hossz-1]
            else:
                lps[i]=0
                i+=1
    return lps

def kmp_kereses(szoveg, minta):
    n=len(szoveg)
    m=len(minta)
    lps=compute_lps(minta)
    i=j=0  # i: szöveg, j: minta
    while i<n:
        if minta[j]==szoveg[i]:
            i+=1; j+=1
        if j==m:
            print(f"Találat {i-j} pozícióban")
            j=lps[j-1]  # Ugrás LPS alapján!
        elif i<n and minta[j]!=szoveg[i]:
            if j!=0:
                j=lps[j-1]  # Nem megyünk vissza a szövegben!
            else:
                i+=1
    return lps""",
        "C++": """vector<int> computeLPS(string pat){
    int m=pat.length();
    vector<int> lps(m,0);
    int len=0, i=1;
    while(i<m){
        if(pat[i]==pat[len]){len++; lps[i]=len; i++;}
        else{
            if(len!=0) len=lps[len-1];
            else{ lps[i]=0; i++; }
        }
    }
    return lps;
}
void KMPSearch(string txt, string pat){
    int n=txt.length(), m=pat.length();
    vector<int> lps=computeLPS(pat);
    int i=0,j=0;
    while(i<n){
        if(pat[j]==txt[i]){i++; j++;}
        if(j==m){ cout<<"Találat "<<i-j<<endl; j=lps[j-1]; }
        else if(i<n && pat[j]!=txt[i]){
            if(j!=0) j=lps[j-1];
            else i++;
        }
    }
}""",
        "C": "/* KMP C */\nvoid computeLPS(char* pat, int m, int* lps){int len=0; lps[0]=0; int i=1; while(i<m){if(pat[i]==pat[len]){len++; lps[i]=len; i++;} else{if(len!=0) len=lps[len-1]; else{lps[i]=0; i++;}}}} void KMPSearch(char* txt, char* pat){int n=strlen(txt), m=strlen(pat); int lps[m]; computeLPS(pat,m,lps); int i=0,j=0; while(i<n){if(pat[j]==txt[i]){i++; j++;} if(j==m){printf(\"Talalat %d\\n\",i-j); j=lps[j-1];} else if(i<n && pat[j]!=txt[i]){if(j!=0) j=lps[j-1]; else i++;}}}",
        "BASIC": "SUB ComputeLPS(pat AS STRING, lps() AS INTEGER)\n m=LEN(pat): len=0: lps(0)=0: i=1\n WHILE i<m\n  IF MID$(pat,i+1,1)=MID$(pat,len+1,1) THEN len=len+1: lps(i)=len: i=i+1\n  ELSE IF len<>0 THEN len=lps(len-1) ELSE lps(i)=0: i=i+1\n WEND\nEND SUB\nSUB KMPSearch(txt AS STRING, pat AS STRING)\n n=LEN(txt): m=LEN(pat): DIM lps(m): ComputeLPS(pat,lps)\n i=0: j=0\n WHILE i<n\n  IF MID$(pat,j+1,1)=MID$(txt,i+1,1) THEN i=i+1: j=j+1\n  IF j=m THEN PRINT \"Talalat \";i-j: j=lps(j-1)\n  ELSE IF i<n AND MID$(pat,j+1,1)<>MID$(txt,i+1,1) THEN IF j<>0 THEN j=lps(j-1) ELSE i=i+1\n WEND\nEND SUB",
        "Java": "int[] computeLPS(String pat){int m=pat.length(); int[] lps=new int[m]; int len=0, i=1; lps[0]=0; while(i<m){ if(pat.charAt(i)==pat.charAt(len)){len++; lps[i]=len; i++;} else{if(len!=0) len=lps[len-1]; else{lps[i]=0; i++;}}} return lps;} void KMPSearch(String txt, String pat){int n=txt.length(), m=pat.length(); int[] lps=computeLPS(pat); int i=0,j=0; while(i<n){ if(pat.charAt(j)==txt.charAt(i)){i++; j++;} if(j==m){ System.out.println(\"Talalat \"+(i-j)); j=lps[j-1];} else if(i<n && pat.charAt(j)!=txt.charAt(i)){ if(j!=0) j=lps[j-1]; else i++;}}}",
        "Pascal": "procedure ComputeLPS(pat: string; var lps: array of Integer); var m,len,i: Integer; begin m:=Length(pat); len:=0; lps[0]:=0; i:=1; while i<m do begin if pat[i+1]=pat[len+1] then begin Inc(len); lps[i]:=len; Inc(i); end else begin if len<>0 then len:=lps[len-1] else begin lps[i]:=0; Inc(i); end; end; end; end; procedure KMPSearch(txt, pat: string); var n,m,i,j: Integer; lps: array of Integer; begin n:=Length(txt); m:=Length(pat); SetLength(lps,m); ComputeLPS(pat,lps); i:=0; j:=0; while i<n do begin if pat[j+1]=txt[i+1] then begin Inc(i); Inc(j); end; if j=m then begin WriteLn('Talalat ',i-j); j:=lps[j-1]; end else if (i<n) and (pat[j+1]<>txt[i+1]) then begin if j<>0 then j:=lps[j-1] else Inc(i); end; end; end;"
    }
    
    def get_steps(self, arr):
        text = "ABABDABACDABABCABAB"
        pattern = "ABABCABAB"
        n = len(text)
        m = len(pattern)
        
        # LPS számítás lépésenként
        lps = KMPMatcher.compute_lps(pattern)
        
        yield StringStep(text, pattern, text_pos=0, pattern_pos=0, lps=[], code_line=1,
                         explanation=f"📝 KMP kezdés: szöveg='{text}' ({n}), minta='{pattern}' ({m})",
                         comparisons=0, extra={"phase": "LPS számítás"})
        
        # LPS tábla építés vizualizálva
        temp_lps = [0]*m
        length = 0
        i = 1
        while i < m:
            yield StringStep(text, pattern, text_pos=0, pattern_pos=i, lps=list(temp_lps), code_line=6,
                             explanation=f"LPS[{i}]: '{pattern[i]}' vs '{pattern[length]}' hossz={length}",
                             comparisons=i, extra={"phase": "LPS", "i": i, "length": length, "lps": list(temp_lps)})
            if pattern[i] == pattern[length]:
                length += 1
                temp_lps[i] = length
                yield StringStep(text, pattern, text_pos=0, pattern_pos=i, lps=list(temp_lps), code_line=8,
                                 explanation=f"Egyezik! LPS[{i}]={length}",
                                 comparisons=i, extra={"phase": "LPS", "i": i, "length": length, "lps": list(temp_lps)})
                i += 1
            else:
                if length != 0:
                    length = temp_lps[length-1]
                    yield StringStep(text, pattern, text_pos=0, pattern_pos=i, lps=list(temp_lps), code_line=12,
                                     explanation=f"Nem egyezik, visszaugrás: hossz={length}",
                                     comparisons=i, extra={"phase": "LPS", "i": i, "length": length, "lps": list(temp_lps)})
                else:
                    temp_lps[i] = 0
                    yield StringStep(text, pattern, text_pos=0, pattern_pos=i, lps=list(temp_lps), code_line=14,
                                     explanation=f"LPS[{i}]=0",
                                     comparisons=i, extra={"phase": "LPS", "i": i, "length": length, "lps": list(temp_lps)})
                    i += 1
        
        yield StringStep(text, pattern, text_pos=0, pattern_pos=0, lps=lps, code_line=18,
                         explanation=f"✅ LPS kész: {lps} - leghosszabb prefix ami suffix",
                         comparisons=0, extra={"phase": "keresés", "lps": lps})
        
        # Keresés
        i = j = 0
        comparisons = 0
        found = []
        
        while i < n:
            comparisons+=1
            highlight_t = [i] if i < n else []
            highlight_p = [j] if j < m else []
            
            if j < m and pattern[j] == text[i]:
                yield StringStep(text, pattern, text_pos=i, pattern_pos=j, lps=lps,
                                 highlight_text=highlight_t, highlight_pattern=highlight_p,
                                 code_line=24, explanation=f"Egyezik: text[{i}]='{text[i]}' == pattern[{j}]='{pattern[j]}'",
                                 comparisons=comparisons, extra={"phase": "keresés", "i": i, "j": j, "lps": lps, "found": found})
                i+=1; j+=1
            else:
                if j < m:
                    yield StringStep(text, pattern, text_pos=i, pattern_pos=j, lps=lps,
                                     highlight_text=highlight_t, highlight_pattern=highlight_p,
                                     code_line=28, explanation=f"Nem egyezik: '{text[i] if i<n else ''}' != '{pattern[j]}'",
                                     comparisons=comparisons, extra={"phase": "keresés", "i": i, "j": j, "lps": lps, "found": found})
            
            if j == m:
                found.append(i-j)
                yield StringStep(text, pattern, text_pos=i-j, pattern_pos=0, lps=lps,
                                 highlight_text=list(range(i-j, i)), highlight_pattern=list(range(m)),
                                 code_line=26, explanation=f"✅ TALÁLAT {i-j} pozícióban! LPS alapján ugrás: j={lps[j-1]}",
                                 comparisons=comparisons, extra={"phase": "találat", "i": i, "j": j, "lps": lps, "found": found}, found_positions=list(found))
                j = lps[j-1]
            elif i < n and j < m and pattern[j] != text[i]:
                if j != 0:
                    old_j = j
                    j = lps[j-1]
                    yield StringStep(text, pattern, text_pos=i, pattern_pos=j, lps=lps,
                                     highlight_text=[i], highlight_pattern=[j],
                                     code_line=30, explanation=f"Ugrás! j: {old_j} -> {j} (LPS[{old_j-1}]={j}), szövegben nem megyünk vissza!",
                                     comparisons=comparisons, extra={"phase": "ugrás", "i": i, "j": j, "lps": lps, "found": found, "jump": True})
                else:
                    i+=1
                    yield StringStep(text, pattern, text_pos=i, pattern_pos=j, lps=lps,
                                     highlight_text=[i], highlight_pattern=[j],
                                     code_line=32, explanation=f"j=0, léptetjük a szöveget: i={i}",
                                     comparisons=comparisons, extra={"phase": "léptet", "i": i, "j": j, "lps": lps, "found": found})
        
        yield StringStep(text, pattern, text_pos=n, pattern_pos=0, lps=lps, code_line=34,
                         explanation=f"✅ KMP vége, találatok: {found} | {comparisons} összehasonlítás vs naiv O(n*m)",
                         comparisons=comparisons, extra={"phase": "kész", "found": found, "lps": lps}, found_positions=found)
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class RabinKarpPlugin(AlgorithmPluginBase):
    id = "rabinkarp"
    name = "Rabin-Karp - Hashing"
    description = "Rolling hash, gyors ugrás, hash egyezés után ellenőriz"
    time_complexity = "O(n+m) átlag"
    space_complexity = "O(1)"
    icon = "🔢"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "string"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "ABABDABACDABABCABAB", description="Keresendő"))
        self.params.add(Param("pattern", "Minta", "string", "ABABCABAB", description="Keresett"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def rabin_karp(szoveg, minta, base=256, mod=101):
    n=len(szoveg)
    m=len(minta)
    h=pow(base, m-1, mod)  # base^(m-1) % mod
    # Hash-ek
    p_hash=0
    t_hash=0
    for i in range(m):
        p_hash=(base*p_hash + ord(minta[i])) % mod
        t_hash=(base*t_hash + ord(szoveg[i])) % mod
    
    for i in range(n-m+1):
        # Hash egyezik?
        if p_hash==t_hash:
            # Ellenőrizni kell ténylegesen (ütközés lehet)
            if szoveg[i:i+m]==minta:
                print(f"Találat {i}-ben")
        # Rolling hash - következő ablak
        if i < n-m:
            t_hash=(base*(t_hash - ord(szoveg[i])*h) + ord(szoveg[i+m])) % mod
            if t_hash<0:
                t_hash+=mod
    return p_hash, t_hash""",
        "C++": """void rabinKarp(string txt, string pat, int base=256, int mod=101){
    int n=txt.length(), m=pat.length();
    int h=1; for(int i=0;i<m-1;i++) h=(h*base)%mod;
    int pHash=0, tHash=0;
    for(int i=0;i<m;i++){ pHash=(base*pHash+pat[i])%mod; tHash=(base*tHash+txt[i])%mod; }
    for(int i=0;i<=n-m;i++){
        if(pHash==tHash){
            bool match=true;
            for(int j=0;j<m;j++) if(txt[i+j]!=pat[j]){match=false; break;}
            if(match) cout<<"Talalat "<<i<<endl;
        }
        if(i<n-m){
            tHash=(base*(tHash-txt[i]*h)+txt[i+m])%mod;
            if(tHash<0) tHash+=mod;
        }
    }
}""",
        "C": "/* Rabin-Karp C */\nvoid rabinKarp(char* txt, char* pat, int base, int mod){int n=strlen(txt), m=strlen(pat); int h=1; for(int i=0;i<m-1;i++) h=(h*base)%mod; int pHash=0,tHash=0; for(int i=0;i<m;i++){pHash=(base*pHash+pat[i])%mod; tHash=(base*tHash+txt[i])%mod;} for(int i=0;i<=n-m;i++){if(pHash==tHash){int j; for(j=0;j<m;j++) if(txt[i+j]!=pat[j]) break; if(j==m) printf(\"Talalat %d\\n\",i);} if(i<n-m){tHash=(base*(tHash-txt[i]*h)+txt[i+m])%mod; if(tHash<0) tHash+=mod;}}}",
        "BASIC": "SUB RabinKarp(txt AS STRING, pat AS STRING, base AS INTEGER, mod AS INTEGER)\n n=LEN(txt): m=LEN(pat): h=1: FOR i=0 TO m-2: h=(h*base) MOD mod: NEXT\n pHash=0: tHash=0: FOR i=0 TO m-1: pHash=(base*pHash+ASC(MID$(pat,i+1,1))) MOD mod: tHash=(base*tHash+ASC(MID$(txt,i+1,1))) MOD mod: NEXT\n FOR i=0 TO n-m\n  IF pHash=tHash THEN IF MID$(txt,i+1,m)=pat THEN PRINT \"Talalat \";i\n  IF i<n-m THEN tHash=(base*(tHash-ASC(MID$(txt,i+1,1))*h)+ASC(MID$(txt,i+m+1,1))) MOD mod: IF tHash<0 THEN tHash=tHash+mod\n NEXT\nEND SUB",
        "Java": "void rabinKarp(String txt, String pat, int base, int mod){int n=txt.length(), m=pat.length(); int h=1; for(int i=0;i<m-1;i++) h=(h*base)%mod; int pHash=0,tHash=0; for(int i=0;i<m;i++){pHash=(base*pHash+pat.charAt(i))%mod; tHash=(base*tHash+txt.charAt(i))%mod;} for(int i=0;i<=n-m;i++){if(pHash==tHash){boolean match=true; for(int j=0;j<m;j++) if(txt.charAt(i+j)!=pat.charAt(j)){match=false; break;} if(match) System.out.println(\"Talalat \"+i);} if(i<n-m){tHash=(base*(tHash-txt.charAt(i)*h)+txt.charAt(i+m))%mod; if(tHash<0) tHash+=mod;}}}",
        "Pascal": "procedure RabinKarp(txt, pat: string; base, mod_: Integer); var n,m,h,pHash,tHash,i,j: Integer; match: Boolean; begin n:=Length(txt); m:=Length(pat); h:=1; for i:=0 to m-2 do h:=(h*base) mod mod_; pHash:=0; tHash:=0; for i:=0 to m-1 do begin pHash:=(base*pHash+Ord(pat[i+1])) mod mod_; tHash:=(base*tHash+Ord(txt[i+1])) mod mod_; end; for i:=0 to n-m do begin if pHash=tHash then begin match:=True; for j:=0 to m-1 do if txt[i+j+1]<>pat[j+1] then begin match:=False; Break; end; if match then WriteLn('Talalat ',i); end; if i<n-m then begin tHash:=(base*(tHash-Ord(txt[i+1])*h)+Ord(txt[i+m+1])) mod mod_; if tHash<0 then tHash:=tHash+mod_; end; end; end;"
    }
    
    def get_steps(self, arr):
        text = "ABABDABACDABABCABAB"
        pattern = "ABABCABAB"
        base = 256
        mod = 101
        n = len(text)
        m = len(pattern)
        
        h = pow(base, m-1, mod)
        p_hash = 0
        t_hash = 0
        for i in range(m):
            p_hash = (base*p_hash + ord(pattern[i])) % mod
            t_hash = (base*t_hash + ord(text[i])) % mod
        
        yield StringStep(text, pattern, text_pos=0, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash, code_line=3,
                         explanation=f"🔢 Rabin-Karp: text='{text}' pat='{pattern}' base={base} mod={mod}",
                         comparisons=0, extra={"phase": "hash init", "p_hash": p_hash, "t_hash": t_hash, "h": h})
        
        yield StringStep(text, pattern, text_pos=0, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash, code_line=7,
                         explanation=f"Kezdő hash-ek: pattern={p_hash}, text[0:{m}]='{text[0:m]}'={t_hash}",
                         comparisons=0, extra={"phase": "hash", "p_hash": p_hash, "t_hash": t_hash, "window": text[0:m]})
        
        found = []
        comparisons = 0
        
        for i in range(n-m+1):
            comparisons+=1
            window = text[i:i+m]
            
            if p_hash == t_hash:
                yield StringStep(text, pattern, text_pos=i, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash,
                                 highlight_text=list(range(i, i+m)), highlight_pattern=list(range(m)),
                                 code_line=12, explanation=f"Hash egyezik! {t_hash}=={p_hash} ablak '{window}' vs '{pattern}' - ellenőrizzük",
                                 comparisons=comparisons, extra={"phase": "hash egyezik", "i": i, "p_hash": p_hash, "t_hash": t_hash, "window": window, "found": found})
                
                # Tényleges összehasonlítás
                if window == pattern:
                    found.append(i)
                    yield StringStep(text, pattern, text_pos=i, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash,
                                     highlight_text=list(range(i, i+m)), highlight_pattern=list(range(m)),
                                     code_line=15, explanation=f"✅ VALÓDI találat {i}-ben! '{window}' == '{pattern}'",
                                     comparisons=comparisons, extra={"phase": "találat", "i": i, "found": found, "p_hash": p_hash, "t_hash": t_hash}, found_positions=list(found))
                else:
                    yield StringStep(text, pattern, text_pos=i, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash,
                                     highlight_text=list(range(i, i+m)), highlight_pattern=list(range(m)),
                                     code_line=15, explanation=f"❌ Hamis riasztás! Hash egyezik de '{window}' != '{pattern}' (ütközés)",
                                     comparisons=comparisons, extra={"phase": "hamis", "i": i, "found": found})
            else:
                yield StringStep(text, pattern, text_pos=i, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash,
                                 highlight_text=list(range(i, i+m)), highlight_pattern=[],
                                 code_line=12, explanation=f"Hash nem egyezik: {t_hash}!={p_hash} ablak '{window}' - ugrunk",
                                 comparisons=comparisons, extra={"phase": "nem egyezik", "i": i, "p_hash": p_hash, "t_hash": t_hash, "window": window, "found": found})
            
            # Rolling hash
            if i < n-m:
                old_char = text[i]
                new_char = text[i+m]
                old_hash = t_hash
                t_hash = (base*(t_hash - ord(text[i])*h) + ord(text[i+m])) % mod
                if t_hash < 0:
                    t_hash += mod
                
                yield StringStep(text, pattern, text_pos=i+1, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash,
                                 highlight_text=list(range(i+1, i+1+m)), highlight_pattern=[],
                                 code_line=18, explanation=f"Rolling hash: -'{old_char}'*h +'{new_char}' | {old_hash} -> {t_hash} (ablak '{text[i+1:i+1+m]}')",
                                 comparisons=comparisons, extra={"phase": "rolling", "i": i+1, "p_hash": p_hash, "t_hash": t_hash, "window": text[i+1:i+1+m], "found": found})
        
        yield StringStep(text, pattern, text_pos=n, pattern_pos=0, hash_text=t_hash, hash_pattern=p_hash, code_line=21,
                         explanation=f"✅ Rabin-Karp vége, találatok: {found} | {comparisons} ablak hash-elve",
                         comparisons=comparisons, extra={"phase": "kész", "found": found}, found_positions=found)
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
