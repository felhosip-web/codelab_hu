# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.encoding import HuffmanCoding, RLE, CaesarCipher, Base64Codec, LZWCodec

class EncodingStep:
    def __init__(self, text="", encoded="", decoded="", current_char=None,
                 codes=None, tree=None, freq=None,
                 highlight_text=None, highlight_encoded=None,
                 code_line=0, explanation="", comparisons=0, extra=None):
        self.text = text
        self.encoded = encoded
        self.decoded = decoded
        self.current_char = current_char
        self.codes = codes or {}
        self.tree = tree
        self.freq = freq or {}
        self.highlight_text = highlight_text or []
        self.highlight_encoded = highlight_encoded or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.extra = extra or {}
        # Kompat
        self.array = []
        self.key = None
        self.sorted_end = -1
        self.highlight = []
        self.shifts = 0
        self.pass_num = comparisons
        self.structure = tree

class HuffmanPlugin(AlgorithmPluginBase):
    id = "huffman"
    name = "Huffman kódolás"
    description = "Optimális prefix kód, fa építés gyakoriság alapján"
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    icon = "🌲📦"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "encoding"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "ABRACADABRA", description="Kódolandó"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """from collections import Counter
import heapq

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char=char
        self.freq=freq
        self.left=left
        self.right=right
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_kodolas(szoveg):
    # 1. Gyakoriság számítás
    freq=Counter(szoveg)
    # 2. Kupac építés
    heap=[HuffmanNode(char,f) for char,f in freq.items()]
    heapq.heapify(heap)
    # 3. Fa építés - legkisebb kettőt összevonjuk
    while len(heap)>1:
        left=heapq.heappop(heap)
        right=heapq.heappop(heap)
        merged=HuffmanNode(freq=left.freq+right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    root=heap[0]
    # 4. Kódok generálása DFS-sel
    codes={}
    def gen_codes(node, code):
        if node.char:
            codes[node.char]=code or "0"
        else:
            if node.left: gen_codes(node.left, code+"0")
            if node.right: gen_codes(node.right, code+"1")
    gen_codes(root, "")
    # 5. Kódolás
    encoded="".join(codes[ch] for ch in szoveg)
    return root, codes, encoded

# Dekódolás: fa bejárás bitek alapján
def huffman_dekodolas(encoded, root):
    decoded=""
    node=root
    for bit in encoded:
        node=node.left if bit=="0" else node.right
        if node.char:
            decoded+=node.char
            node=root
    return decoded
""",
        "C++": "// Huffman C++ - priority_queue\nstruct Node{char ch; int freq; Node *left,*right; Node(char c,int f): ch(c),freq(f),left(nullptr),right(nullptr){}}; struct Compare{bool operator()(Node* a, Node* b){return a->freq > b->freq;}}; void buildHuffman(string text){ map<char,int> freq; for(char c: text) freq[c]++; priority_queue<Node*, vector<Node*>, Compare> pq; for(auto &p: freq) pq.push(new Node(p.first,p.second)); while(pq.size()>1){ Node* left=pq.top(); pq.pop(); Node* right=pq.top(); pq.pop(); Node* merged=new Node('\\0', left->freq+right->freq); merged->left=left; merged->right=right; pq.push(merged);} Node* root=pq.top(); // kód generálás... }",
        "C": "/* Huffman C - heap */\nstruct Node{char ch; int freq; struct Node *left,*right;};\nvoid buildHuffman(char* text){int freq[256]={0}; for(int i=0;text[i];i++) freq[(int)text[i]]++; // heap építés, fa összevonás... }",
        "BASIC": "TYPE HuffmanNode: ch AS STRING: freq AS INTEGER: left AS HuffmanNode PTR: right AS HuffmanNode PTR: END TYPE\nSUB BuildHuffman(text AS STRING): DIM freq(255): FOR i=1 TO LEN(text): freq(ASC(MID$(text,i,1)))+=1: NEXT: ' heap + fa építés...\nEND SUB",
        "Java": "class HuffmanNode implements Comparable<HuffmanNode>{char ch; int freq; HuffmanNode left,right; HuffmanNode(char c,int f){ch=c; freq=f;} public int compareTo(HuffmanNode o){return freq-o.freq;}} void buildHuffman(String text){ Map<Character,Integer> freq=new HashMap<>(); for(char c: text.toCharArray()) freq.put(c, freq.getOrDefault(c,0)+1); PriorityQueue<HuffmanNode> pq=new PriorityQueue<>(); for(var e: freq.entrySet()) pq.add(new HuffmanNode(e.getKey(), e.getValue())); while(pq.size()>1){ HuffmanNode left=pq.poll(), right=pq.poll(); HuffmanNode merged=new HuffmanNode('\\0', left.freq+right.freq); merged.left=left; merged.right=right; pq.add(merged);} }",
        "Pascal": "type HuffmanNode=record ch: Char; freq: Integer; left,right: ^HuffmanNode; end; procedure BuildHuffman(text: string); var freq: array[0..255] of Integer; i: Integer; begin for i:=0 to 255 do freq[i]:=0; for i:=1 to Length(text) do Inc(freq[Ord(text[i])]); // heap + fa építés...\nend;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text")
        huffman = HuffmanCoding()
        
        yield EncodingStep(text=text, code_line=1,
                           explanation=f"🌲📦 Huffman: '{text}' kódolása",
                           comparisons=0, extra={"phase": "freq", "text": text})
        
        from collections import Counter
        freq = Counter(text)
        yield EncodingStep(text=text, freq=freq, code_line=10,
                           explanation=f"Gyakoriság: {dict(freq)}",
                           comparisons=0, extra={"phase": "freq", "freq": dict(freq), "text": text})
        
        huffman.build(text)
        huffman.calculate_positions()
        
        yield EncodingStep(text=text, codes=huffman.codes, tree=huffman.root, freq=freq, code_line=18,
                           explanation=f"Fa építve, kódok: {huffman.codes}",
                           comparisons=0, extra={"phase": "fa", "codes": huffman.codes, "freq": dict(freq), "text": text})
        
        # Kódolás lépésenként
        encoded = ""
        for i, ch in enumerate(text):
            code = huffman.codes.get(ch, "")
            encoded+=code
            yield EncodingStep(text=text, encoded=encoded, codes=huffman.codes, tree=huffman.root, freq=freq,
                               current_char=ch, highlight_text=[i], highlight_encoded=list(range(len(encoded)-len(code), len(encoded))),
                               code_line=28, explanation=f"Kódol: '{ch}' -> {code} | eddig: {encoded}",
                               comparisons=i+1, extra={"phase": "kódol", "char": ch, "code": code, "encoded": encoded, "text": text, "codes": huffman.codes})
        
        # Dekódolás
        decoded = huffman.decode(encoded)
        yield EncodingStep(text=text, encoded=encoded, decoded=decoded, codes=huffman.codes, tree=huffman.root, freq=freq,
                           code_line=35, explanation=f"✅ Kódolva: {encoded} ({len(encoded)} bit vs {len(text)*8} bit) | Dekódolva: {decoded}",
                           comparisons=len(text), extra={"phase": "kész", "encoded": encoded, "decoded": decoded, "compression": f"{len(encoded)}/{len(text)*8} = {len(encoded)/(len(text)*8)*100:.1f}%", "text": text, "codes": huffman.codes})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class RLEPlugin(AlgorithmPluginBase):
    id = "rle"
    name = "RLE - Futamhossz kódolás"
    description = "Egyszerű tömörítés: AAAABBB -> 4A3B"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "📏"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "encoding"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "AAAABBBCCDAA", description="Ismétlődő karakterekkel jó"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """def rle_kodolas(szoveg):
    if not szoveg: return ""
    kodolt=[]
    darab=1
    for i in range(1, len(szoveg)):
        if szoveg[i]==szoveg[i-1]:
            darab+=1
        else:
            kodolt.append(f"{darab}{szoveg[i-1]}")
            darab=1
    kodolt.append(f"{darab}{szoveg[-1]}")
    return "".join(kodolt)

def rle_dekodolas(kodolt):
    dekodolt=""
    i=0
    while i < len(kodolt):
        szam_str=""
        while i < len(kodolt) and kodolt[i].isdigit():
            szam_str+=kodolt[i]
            i+=1
        if i < len(kodolt) and szam_str:
            dekodolt+=kodolt[i]*int(szam_str)
            i+=1
    return dekodolt
""",
        "C++": "string rleEncode(string s){ if(s.empty()) return \"\"; string encoded; int count=1; for(int i=1;i<s.length();i++){ if(s[i]==s[i-1]) count++; else{ encoded+=to_string(count)+s[i-1]; count=1; } } encoded+=to_string(count)+s.back(); return encoded; } string rleDecode(string enc){ string decoded; int i=0; while(i<enc.length()){ string num; while(i<enc.length() && isdigit(enc[i])){ num+=enc[i]; i++; } if(i<enc.length() && !num.empty()){ decoded+=string(stoi(num), enc[i]); i++; } } return decoded; }",
        "C": "/* RLE C */\nvoid rleEncode(char* s, char* out){int n=strlen(s), count=1, j=0; for(int i=1;i<n;i++){if(s[i]==s[i-1]) count++; else{ j+=sprintf(out+j,\"%d%c\",count,s[i-1]); count=1;}} sprintf(out+j,\"%d%c\",count,s[n-1]);}",
        "BASIC": "FUNCTION RLEEncode(s AS STRING) AS STRING: IF s=\"\" THEN RETURN \"\": encoded=\"\": count=1: FOR i=2 TO LEN(s): IF MID$(s,i,1)=MID$(s,i-1,1) THEN count+=1 ELSE encoded+=STR$(count)+MID$(s,i-1,1): count=1: NEXT: encoded+=STR$(count)+MID$(s,LEN(s),1): RETURN encoded: END FUNCTION",
        "Java": "String rleEncode(String s){ if(s.isEmpty()) return \"\"; StringBuilder enc=new StringBuilder(); int count=1; for(int i=1;i<s.length();i++){ if(s.charAt(i)==s.charAt(i-1)) count++; else{ enc.append(count).append(s.charAt(i-1)); count=1; } } enc.append(count).append(s.charAt(s.length()-1)); return enc.toString(); }",
        "Pascal": "function RLEEncode(s: string): string; var encoded: string; count,i: Integer; begin if s='' then begin Result:=''; Exit; end; encoded:=''; count:=1; for i:=2 to Length(s) do begin if s[i]=s[i-1] then Inc(count) else begin encoded:=encoded+IntToStr(count)+s[i-1]; count:=1; end; end; encoded:=encoded+IntToStr(count)+s[Length(s)]; Result:=encoded; end;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text")
        
        yield EncodingStep(text=text, code_line=1,
                           explanation=f"📏 RLE: '{text}' kódolása",
                           comparisons=0, extra={"text": text, "phase": "start"})
        
        encoded_parts = []
        count = 1
        for i in range(1, len(text)):
            if text[i] == text[i-1]:
                count+=1
                yield EncodingStep(text=text, encoded="".join(encoded_parts)+f"{count}{text[i]}", current_char=text[i],
                                   highlight_text=list(range(i-count+1, i+1)), code_line=5,
                                   explanation=f"Egyezik: '{text[i]}' darab={count}",
                                   comparisons=i, extra={"text": text, "count": count, "char": text[i], "phase": "számol"})
            else:
                part = f"{count}{text[i-1]}"
                encoded_parts.append(part)
                yield EncodingStep(text=text, encoded="".join(encoded_parts), current_char=text[i-1],
                                   highlight_text=list(range(i-count, i)), highlight_encoded=list(range(len("".join(encoded_parts))-len(part), len("".join(encoded_parts)))),
                                   code_line=8, explanation=f"Kódol: {part} | eddig: {''.join(encoded_parts)}",
                                   comparisons=i, extra={"text": text, "encoded": "".join(encoded_parts), "part": part, "phase": "kódol"})
                count=1
        
        if text:
            part = f"{count}{text[-1]}"
            encoded_parts.append(part)
        
        encoded = "".join(encoded_parts)
        yield EncodingStep(text=text, encoded=encoded, code_line=10,
                           explanation=f"Kódolva: {encoded}",
                           comparisons=len(text), extra={"text": text, "encoded": encoded, "phase": "kódolva"})
        
        decoded = RLE.decode(encoded)
        yield EncodingStep(text=text, encoded=encoded, decoded=decoded, code_line=15,
                           explanation=f"✅ RLE: '{text}' ({len(text)}) -> '{encoded}' ({len(encoded)}) -> '{decoded}' | Tömörítés: {len(encoded)/len(text)*100:.1f}%",
                           comparisons=len(text), extra={"text": text, "encoded": encoded, "decoded": decoded, "phase": "kész"})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class CaesarPlugin(AlgorithmPluginBase):
    id = "caesar"
    name = "Caesar titkosítás"
    description = "Eltolásos titkosítás, klasszikus kódolás"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "🔐"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "encoding"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "HELLO WORLD", description="Titkosítandó"))
        self.params.add(Param("shift", "Eltolás", "int", 3, 1, 25, description="Caesar eltolás"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """def caesar_kodolas(szoveg, eltol=3):
    eredmeny=""
    for ch in szoveg:
        if ch.isalpha():
            base=ord('A') if ch.isupper() else ord('a')
            eredmeny+=chr((ord(ch)-base+eltol)%26+base)
        else:
            eredmeny+=ch
    return eredmeny

def caesar_dekodolas(szoveg, eltol=3):
    return caesar_kodolas(szoveg, -eltol)

# Példa:
# HELLO -> KHOOR (shift 3)
# A -> D, B -> E, ...
# Z -> C (körbe)
""",
        "C++": "string caesarEncode(string s, int shift){ string res; for(char ch: s){ if(isalpha(ch)){ char base=isupper(ch)? 'A':'a'; res+=char((ch-base+shift)%26+base); } else res+=ch; } return res; } string caesarDecode(string s, int shift){ return caesarEncode(s, -shift); }",
        "C": "/* Caesar C */\nvoid caesarEncode(char* s, int shift, char* out){for(int i=0;s[i];i++){char ch=s[i]; if(isalpha(ch)){char base=isupper(ch)? 'A':'a'; out[i]=((ch-base+shift)%26+26)%26+base;} else out[i]=ch;} out[strlen(s)]='\\0';}",
        "BASIC": "FUNCTION CaesarEncode(s AS STRING, shift AS INTEGER) AS STRING: res=\"\": FOR i=1 TO LEN(s): ch=MID$(s,i,1): IF ch>=\"A\" AND ch<=\"Z\" THEN base=ASC(\"A\"): res+=CHR$((ASC(ch)-base+shift) MOD 26+base) ELSE IF ch>=\"a\" AND ch<=\"z\" THEN base=ASC(\"a\"): res+=CHR$((ASC(ch)-base+shift) MOD 26+base) ELSE res+=ch: NEXT: RETURN res: END FUNCTION",
        "Java": "String caesarEncode(String s, int shift){ StringBuilder res=new StringBuilder(); for(char ch: s.toCharArray()){ if(Character.isLetter(ch)){ char base=Character.isUpperCase(ch)? 'A':'a'; res.append((char)((ch-base+shift)%26+base)); } else res.append(ch); } return res.toString(); }",
        "Pascal": "function CaesarEncode(s: string; shift: Integer): string; var res: string; i,base: Integer; ch: Char; begin res:=''; for i:=1 to Length(s) do begin ch:=s[i]; if ch in ['A'..'Z'] then begin base:=Ord('A'); res:=res+Chr((Ord(ch)-base+shift) mod 26+base); end else if ch in ['a'..'z'] then begin base:=Ord('a'); res:=res+Chr((Ord(ch)-base+shift) mod 26+base); end else res:=res+ch; end; Result:=res; end;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text")
        shift = self.params.get("shift")
        
        yield EncodingStep(text=text, code_line=1,
                           explanation=f"🔐 Caesar: '{text}' shift={shift}",
                           comparisons=0, extra={"text": text, "shift": shift, "phase": "start"})
        
        encoded = ""
        for i, ch in enumerate(text):
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                enc_ch = chr((ord(ch)-base+shift)%26+base)
                encoded+=enc_ch
                yield EncodingStep(text=text, encoded=encoded, current_char=ch,
                                   highlight_text=[i], highlight_encoded=[len(encoded)-1],
                                   code_line=5, explanation=f"'{ch}' ({ord(ch)-base}) + {shift} = '{enc_ch}' | {text[:i+1]} -> {encoded}",
                                   comparisons=i+1, extra={"text": text, "shift": shift, "char": ch, "enc_char": enc_ch, "encoded": encoded, "phase": "kódol"})
            else:
                encoded+=ch
                yield EncodingStep(text=text, encoded=encoded, current_char=ch,
                                   highlight_text=[i], code_line=7,
                                   explanation=f"'{ch}' nem betű, marad | {encoded}",
                                   comparisons=i+1, extra={"text": text, "encoded": encoded, "phase": "kódol"})
        
        decoded = CaesarCipher.decode(encoded, shift)
        yield EncodingStep(text=text, encoded=encoded, decoded=decoded, code_line=10,
                           explanation=f"✅ Caesar: '{text}' -> '{encoded}' -> '{decoded}' shift={shift}",
                           comparisons=len(text), extra={"text": text, "encoded": encoded, "decoded": decoded, "shift": shift, "phase": "kész"})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class Base64Plugin(AlgorithmPluginBase):
    id = "base64"
    name = "Base64 kódolás"
    description = "Bináris -> szöveg kódolás, 6 bit -> karakter"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    icon = "🔢🔤"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "encoding"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "Hello!", description="Kódolandó"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """import base64

def base64_kodolas(szoveg):
    # Szöveg -> byteok -> Base64
    byteok=szoveg.encode('utf-8')
    kodolt=base64.b64encode(byteok)
    return kodolt.decode('utf-8')

def base64_dekodolas(kodolt):
    byteok=base64.b64decode(kodolt.encode('utf-8'))
    return byteok.decode('utf-8')

# Példa:
# Hello! -> SGVsbG8h
# 01001000 01100101 01101100 01101100 01101111 00100001
# 010010 000110 010101 101100 011011 000110 111100 100001
# S      G      V      s      b      G      8      h
""",
        "C++": "// Base64 C++\nstring base64Encode(string s){ static const string chars=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\"; string ret; int i=0,j=0; unsigned char a3[3], a4[4]; for(char c: s){ a3[i++]=c; if(i==3){ a4[0]=(a3[0]&0xfc)>>2; a4[1]=((a3[0]&0x03)<<4)+((a3[1]&0xf0)>>4); a4[2]=((a3[1]&0x0f)<<2)+((a3[2]&0xc0)>>6); a4[3]=a3[2]&0x3f; for(int k=0;k<4;k++) ret+=chars[a4[k]]; i=0; } } if(i){ for(j=i;j<3;j++) a3[j]='\\0'; a4[0]=(a3[0]&0xfc)>>2; a4[1]=((a3[0]&0x03)<<4)+((a3[1]&0xf0)>>4); a4[2]=((a3[1]&0x0f)<<2)+((a3[2]&0xc0)>>6); a4[3]=a3[2]&0x3f; for(j=0;j<i+1;j++) ret+=chars[a4[j]]; while(i++<3) ret+='='; } return ret; }",
        "C": "/* Base64 C */\nstatic const char b64[]=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\";\nvoid base64Encode(char* s, char* out){int i=0,j=0; unsigned char a3[3],a4[4]; int len=strlen(s); for(int k=0;k<len;k++){a3[i++]=s[k]; if(i==3){a4[0]=(a3[0]&0xfc)>>2; a4[1]=((a3[0]&0x03)<<4)+((a3[1]&0xf0)>>4); a4[2]=((a3[1]&0x0f)<<2)+((a3[2]&0xc0)>>6); a4[3]=a3[2]&0x3f; for(int l=0;l<4;l++) out[j++]=b64[a4[l]]; i=0;}} if(i){for(j=i;j<3;j++) a3[j]='\\0'; a4[0]=(a3[0]&0xfc)>>2; a4[1]=((a3[0]&0x03)<<4)+((a3[1]&0xf0)>>4); a4[2]=((a3[1]&0x0f)<<2)+((a3[2]&0xc0)>>6); a4[3]=a3[2]&0x3f; for(j=0;j<i+1;j++) out[j]=b64[a4[j]]; while(i++<3) out[j++]='='; out[j]='\\0';}}",
        "BASIC": "FUNCTION Base64Encode(s AS STRING) AS STRING: DIM chars AS STRING: chars=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\": ret=\"\": i=0: DIM a3(2) AS INTEGER: DIM a4(3) AS INTEGER: FOR k=1 TO LEN(s): a3(i)=ASC(MID$(s,k,1)): i+=1: IF i=3 THEN a4(0)=(a3(0) AND &HFC) \\ 4: a4(1)=((a3(0) AND 3) * 16)+((a3(1) AND &HF0) \\ 16): a4(2)=((a3(1) AND &HF) * 4)+((a3(2) AND &HC0) \\ 64): a4(3)=a3(2) AND &H3F: FOR l=0 TO 3: ret+=MID$(chars,a4(l)+1,1): NEXT: i=0: NEXT: ' padding...\nRETURN ret: END FUNCTION",
        "Java": "String base64Encode(String s){ String chars=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\"; StringBuilder ret=new StringBuilder(); int i=0; byte[] a3=new byte[3]; for(byte b: s.getBytes()){ a3[i++]=b; if(i==3){ byte[] a4=new byte[4]; a4[0]=(byte)((a3[0]&0xfc)>>2); a4[1]=(byte)(((a3[0]&0x03)<<4)+((a3[1]&0xf0)>>4)); a4[2]=(byte)(((a3[1]&0x0f)<<2)+((a3[2]&0xc0)>>6)); a4[3]=(byte)(a3[2]&0x3f); for(int k=0;k<4;k++) ret.append(chars.charAt(a4[k])); i=0; } } // padding...\nreturn ret.toString(); }",
        "Pascal": "function Base64Encode(s: string): string; const chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; var ret: string; i,j: Integer; a3: array[0..2] of Byte; a4: array[0..3] of Byte; k: Integer; begin ret:=''; i:=0; for k:=1 to Length(s) do begin a3[i]:=Ord(s[k]); Inc(i); if i=3 then begin a4[0]:=(a3[0] and $fc) shr 2; a4[1]:=((a3[0] and $03) shl 4)+((a3[1] and $f0) shr 4); a4[2]:=((a3[1] and $0f) shl 2)+((a3[2] and $c0) shr 6); a4[3]:=a3[2] and $3f; for j:=0 to 3 do ret:=ret+chars[a4[j]+1]; i:=0; end; end; Result:=ret; end;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text")
        
        yield EncodingStep(text=text, code_line=1,
                           explanation=f"🔢🔤 Base64: '{text}'",
                           comparisons=0, extra={"text": text, "phase": "start"})
        
        # Byte-ok
        bytes_list = list(text.encode('utf-8'))
        binary = " ".join([f"{b:08b}" for b in bytes_list])
        yield EncodingStep(text=text, code_line=3,
                           explanation=f"Byte-ok: {bytes_list} | Bitek: {binary}",
                           comparisons=0, extra={"text": text, "bytes": bytes_list, "binary": binary, "phase": "bytes"})
        
        encoded = Base64Codec.encode(text)
        yield EncodingStep(text=text, encoded=encoded, code_line=4,
                           explanation=f"Base64: 3 byte (24 bit) -> 4 karakter (6 bit*4)",
                           comparisons=0, extra={"text": text, "encoded": encoded, "phase": "kódol"})
        
        # 6 bites csoportok mutatása
        for i in range(0, len(text), 3):
            chunk = text[i:i+3]
            chunk_encoded = Base64Codec.encode(chunk)
            yield EncodingStep(text=text, encoded=chunk_encoded, current_char=chunk,
                               highlight_text=list(range(i, min(i+3, len(text)))),
                               code_line=5, explanation=f"'{chunk}' -> {list(chunk.encode())} -> 6 bit csoportok -> '{chunk_encoded}'",
                               comparisons=i//3+1, extra={"text": text, "chunk": chunk, "encoded_chunk": chunk_encoded, "phase": "chunk"})
        
        decoded = Base64Codec.decode(encoded)
        yield EncodingStep(text=text, encoded=encoded, decoded=decoded, code_line=7,
                           explanation=f"✅ Base64: '{text}' -> '{encoded}' -> '{decoded}' | 33% növekedés",
                           comparisons=1, extra={"text": text, "encoded": encoded, "decoded": decoded, "phase": "kész"})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
