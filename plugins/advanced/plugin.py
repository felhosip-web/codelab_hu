# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.structures import BST
import random

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.x = 0
        self.y = 0

class BTree:
    def __init__(self, t=2):
        self.t = t
        self.root = BTreeNode(t, True)
        self.root.keys = []
    
    def search(self, k, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and k == node.keys[i]:
            return (node, i)
        if node.leaf:
            return None
        return self.search(k, node.children[i])
    
    def insert(self, k):
        r = self.root
        if len(r.keys) == 2*self.t-1:
            s = BTreeNode(self.t, False)
            s.children.append(r)
            self._split_child(s, 0)
            self.root = s
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)
    
    def _split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BTreeNode(t, y.leaf)
        z.keys = y.keys[t:]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        x.children.insert(i+1, z)
        x.keys.insert(i, y.keys[t-1])
        y.keys = y.keys[:t-1]
    
    def _insert_nonfull(self, x, k):
        i = len(x.keys)-1
        if x.leaf:
            x.keys.append(0)
            while i >=0 and k < x.keys[i]:
                x.keys[i+1] = x.keys[i]
                i-=1
            x.keys[i+1] = k
        else:
            while i>=0 and k < x.keys[i]:
                i-=1
            i+=1
            if len(x.children[i].keys) == 2*self.t-1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i+=1
            self._insert_nonfull(x.children[i], k)
    
    def calculate_positions(self):
        def assign(node, depth, x_offset):
            if not node:
                return x_offset
            # Gyerekek először
            for child in node.children:
                x_offset = assign(child, depth+1, x_offset)
            node.x = x_offset * 120 + 60
            node.y = depth * 90 + 40
            x_offset += 1
            return x_offset
        assign(self.root, 0, 0)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.x = 0
        self.y = 0
        self.char = ""

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.words = []
    
    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
                node.children[ch].char = ch
            node = node.children[ch]
        node.is_end = True
        if word not in self.words:
            self.words.append(word)
    
    def search(self, word):
        node = self.root
        path = [node]
        for ch in word:
            if ch not in node.children:
                return (False, path)
            node = node.children[ch]
            path.append(node)
        return (node.is_end, path)
    
    def calculate_positions(self):
        def assign(node, depth, x_offset):
            node.x = x_offset * 60 + 30
            node.y = depth * 70 + 30
            x_offset += 1
            for child in node.children.values():
                x_offset = assign(child, depth+1, x_offset)
            return x_offset
        assign(self.root, 0, 0)

from core.step import VisualizationStep

class StructureStep(VisualizationStep):
    def __init__(self, structure, current_value=None, highlight_nodes=None, 
                 code_line=0, explanation="", comparisons=0, extra=None, path=None):
        e_dict = extra.copy() if extra else {}
        if structure is not None and "structure" not in e_dict:
            e_dict["structure"] = structure
        if current_value is not None and "current_value" not in e_dict:
            e_dict["current_value"] = current_value
        if highlight_nodes is not None:
            e_dict["highlight_nodes"] = highlight_nodes
        elif "highlight_nodes" not in e_dict:
            e_dict["highlight_nodes"] = []
        if path is not None:
            e_dict["path"] = path
        elif "path" not in e_dict:
            e_dict["path"] = []

        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            key=current_value,
            extra=e_dict
        )

class BTreePlugin(AlgorithmPluginBase):
    id = "btree"
    name = "B-fa (2-3-4 fa)"
    description = "Több kulcs egy csomóban, adatbázisokban használják"
    time_complexity = "O(log n)"
    space_complexity = "O(n)"
    icon = "🌲"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "btree"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("t", "Fokszám (t)", "int", 2, 2, 4, description="Min kulcs = t-1, max = 2t-1"))
        self.params.add(Param("values", "Értékek", "string", "10,20,5,6,12,30,7,17", description="Vesszővel"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, param_id, value):
        self.params.set(param_id, value)
    
    def generate_input(self, params_dict=None):
        vals_str = self.params.get("values")
        try:
            vals = [int(x.strip()) for x in vals_str.split(",") if x.strip()]
        except:
            vals = [10,20,5,6,12,30,7,17]
        return vals
    
    codes = {
        "Python": """class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t=t
        self.keys=[]
        self.children=[]
        self.leaf=leaf

class BTree:
    def __init__(self, t):
        self.t=t
        self.root=BTreeNode(t, True)
    
    def insert(self, k):
        r=self.root
        if len(r.keys)==2*self.t-1:
            s=BTreeNode(self.t, False)
            s.children.append(r)
            self.split_child(s,0)
            self.root=s
            self.insert_nonfull(s,k)
        else:
            self.insert_nonfull(r,k)
    
    def split_child(self, x, i):
        t=self.t
        y=x.children[i]
        z=BTreeNode(t, y.leaf)
        z.keys=y.keys[t:]
        if not y.leaf:
            z.children=y.children[t:]
            y.children=y.children[:t]
        x.children.insert(i+1, z)
        x.keys.insert(i, y.keys[t-1])
        y.keys=y.keys[:t-1]
""",
        "C++": "// B-fa C++ - t fokszám, 2t-1 max kulcs\nclass BTreeNode{public: int t; vector<int> keys; vector<BTreeNode*> children; bool leaf; BTreeNode(int _t, bool _leaf): t(_t), leaf(_leaf){} void splitChild(int i, BTreeNode* y){ BTreeNode* z=new BTreeNode(y->t, y->leaf); z->keys.assign(y->keys.begin()+t, y->keys.end()); if(!y->leaf) z->children.assign(y->children.begin()+t, y->children.end()); y->keys.resize(t-1); children.insert(children.begin()+i+1, z); keys.insert(keys.begin()+i, y->keys[t-1]); }};",
        "C": "/* B-fa C */\n#define T 2\nstruct BTreeNode{int keys[2*T-1]; struct BTreeNode* children[2*T]; int n; int leaf;};\nvoid splitChild(struct BTreeNode* x, int i){struct BTreeNode* y=x->children[i]; struct BTreeNode* z=malloc(sizeof(*z)); z->leaf=y->leaf; z->n=T-1; for(int j=0;j<T-1;j++) z->keys[j]=y->keys[j+T]; if(!y->leaf) for(int j=0;j<T;j++) z->children[j]=y->children[j+T]; y->n=T-1; for(int j=x->n;j>=i+1;j--) x->children[j+1]=x->children[j]; x->children[i+1]=z; for(int j=x->n-1;j>=i;j--) x->keys[j+1]=x->keys[j]; x->keys[i]=y->keys[T-1]; x->n+=1;}",
        "BASIC": "TYPE BTreeNode: t AS INTEGER: keys() AS INTEGER: children() AS BTreeNode PTR: n AS INTEGER: leaf AS BOOLEAN: END TYPE\nSUB SplitChild(x AS BTreeNode PTR, i AS INTEGER): y=x->children(i): z=NEW BTreeNode(y->t, y->leaf): z->n=T-1: FOR j=0 TO T-2: z->keys(j)=y->keys(j+T): NEXT: IF NOT y->leaf THEN FOR j=0 TO T-1: z->children(j)=y->children(j+T): NEXT: y->n=T-1: FOR j=x->n TO i+1 STEP -1: x->children(j+1)=x->children(j): NEXT: x->children(i+1)=z: FOR j=x->n-1 TO i STEP -1: x->keys(j+1)=x->keys(j): NEXT: x->keys(i)=y->keys(T-1): x->n=x->n+1: END SUB",
        "Java": "class BTreeNode{int t; List<Integer> keys; List<BTreeNode> children; boolean leaf; BTreeNode(int _t, boolean _leaf){t=_t; leaf=_leaf; keys=new ArrayList<>(); children=new ArrayList<>();} void splitChild(int i, BTreeNode y){BTreeNode z=new BTreeNode(y.t, y.leaf); z.keys.addAll(y.keys.subList(t, y.keys.size())); if(!y.leaf) z.children.addAll(y.children.subList(t, y.children.size())); y.keys.subList(t-1, y.keys.size()).clear(); children.add(i+1, z); keys.add(i, y.keys.get(t-1));}}",
        "Pascal": "type BTreeNode=record t: Integer; keys: array of Integer; children: array of BTreeNode; n: Integer; leaf: Boolean; end; procedure SplitChild(var x: BTreeNode; i: Integer); var y,z: BTreeNode; j: Integer; begin y:=x.children[i]; z.t:=y.t; z.leaf:=y.leaf; z.n:=T-1; for j:=0 to T-2 do z.keys[j]:=y.keys[j+T]; if not y.leaf then for j:=0 to T-1 do z.children[j]:=y.children[j+T]; y.n:=T-1; for j:=x.n downto i+1 do x.children[j+1]:=x.children[j]; x.children[i+1]:=z; for j:=x.n-1 downto i do x.keys[j+1]:=x.keys[j]; x.keys[i]:=y.keys[T-1]; Inc(x.n); end;"
    }
    
    def get_steps(self, arr):
        t = self.params.get("t")
        values_str = self.params.get("values")
        try:
            values = [int(x.strip()) for x in values_str.split(",") if x.strip()]
        except:
            values = [10,20,5,6,12,30,7,17]
        
        btree = BTree(t=t)
        comparisons = 0
        
        yield StructureStep(btree, current_value=None, code_line=1,
                            explanation=f"🌲 B-fa t={t}: max kulcs={2*t-1}, min={t-1}",
                            comparisons=0, extra={"t": t, "values": values, "inserted": []})
        
        inserted = []
        for val in values:
            comparisons+=1
            yield StructureStep(btree, current_value=val, code_line=10,
                                explanation=f"B-fa beszúrás: {val}, ha tele van a csomó, split",
                                comparisons=comparisons, extra={"t": t, "values": values, "inserted": inserted, "current": val})
            btree.insert(val)
            btree.calculate_positions()
            inserted.append(val)
            yield StructureStep(btree, current_value=val, highlight_nodes=[val], code_line=12,
                                explanation=f"Beszúrva: {val}, fa most {len(inserted)} elem",
                                comparisons=comparisons, extra={"t": t, "values": values, "inserted": inserted, "current": val})
        
        yield StructureStep(btree, current_value=None, code_line=15,
                            explanation=f"✅ B-fa kész, t={t}, gyökér kulcsok: {btree.root.keys}",
                            comparisons=comparisons, extra={"t": t, "values": values, "inserted": inserted})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class TriePlugin(AlgorithmPluginBase):
    id = "trie"
    name = "Trie - Szótár fa"
    description = "Prefix fa, szavak gyors keresése, automatikus kiegészítés"
    time_complexity = "O(m) m=szó hossz"
    space_complexity = "O(ALFABÉT*m*N)"
    icon = "📚"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "trie"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("words", "Szavak", "string", "alma,almás,almafa,körte,barack", description="Vesszővel"))
        self.params.add(Param("search_word", "Keresett szó", "string", "almafa", description="Keresés"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """class TrieNode:
    def __init__(self):
        self.children={}
        self.is_end=False

class Trie:
    def __init__(self):
        self.root=TrieNode()
    
    def insert(self, word):
        node=self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch]=TrieNode()
            node=node.children[ch]
        node.is_end=True
    
    def search(self, word):
        node=self.root
        for ch in word:
            if ch not in node.children:
                return False
            node=node.children[ch]
        return node.is_end
    
    def starts_with(self, prefix):
        # Automatikus kiegészítéshez
        node=self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node=node.children[ch]
        # Összes szó a részfából
        return self._collect(node, prefix)
""",
        "C++": "struct TrieNode{ map<char,TrieNode*> children; bool isEnd; TrieNode(): isEnd(false){} }; class Trie{ TrieNode* root; public: Trie(){root=new TrieNode();} void insert(string word){ TrieNode* node=root; for(char ch: word){ if(!node->children[ch]) node->children[ch]=new TrieNode(); node=node->children[ch]; } node->isEnd=true; } bool search(string word){ TrieNode* node=root; for(char ch: word){ if(!node->children[ch]) return false; node=node->children[ch]; } return node->isEnd; } };",
        "C": "/* Trie C */\n#define ALPH 26\nstruct TrieNode{ struct TrieNode* children[ALPH]; int isEnd;};\nstruct TrieNode* createNode(){struct TrieNode* n=malloc(sizeof(*n)); for(int i=0;i<ALPH;i++) n->children[i]=NULL; n->isEnd=0; return n;}\nvoid insert(struct TrieNode* root, char* word){struct TrieNode* node=root; for(int i=0; word[i]; i++){int idx=word[i]-'a'; if(!node->children[idx]) node->children[idx]=createNode(); node=node->children[idx];} node->isEnd=1;}",
        "BASIC": "TYPE TrieNode: children(25) AS TrieNode PTR: isEnd AS BOOLEAN: END TYPE\nFUNCTION CreateNode() AS TrieNode PTR: n=NEW TrieNode: FOR i=0 TO 25: n->children(i)=NULL: NEXT: n->isEnd=FALSE: RETURN n: END FUNCTION\nSUB Insert(root AS TrieNode PTR, word AS STRING): node=root: FOR i=1 TO LEN(word): idx=ASC(MID$(word,i,1))-ASC(\"a\"): IF node->children(idx)=NULL THEN node->children(idx)=CreateNode(): node=node->children(idx): NEXT: node->isEnd=TRUE: END SUB",
        "Java": "class TrieNode{ Map<Character,TrieNode> children=new HashMap<>(); boolean isEnd; } class Trie{ TrieNode root=new TrieNode(); void insert(String word){ TrieNode node=root; for(char ch: word.toCharArray()){ node.children.putIfAbsent(ch, new TrieNode()); node=node.children.get(ch); } node.isEnd=true; } boolean search(String word){ TrieNode node=root; for(char ch: word.toCharArray()){ if(!node.children.containsKey(ch)) return false; node=node.children.get(ch); } return node.isEnd; } }",
        "Pascal": "type PTrieNode=^TrieNode; TrieNode=record children: array[0..25] of PTrieNode; isEnd: Boolean; end; function CreateNode: PTrieNode; var n: PTrieNode; i: Integer; begin New(n); for i:=0 to 25 do n^.children[i]:=nil; n^.isEnd:=False; Result:=n; end; procedure Insert(root: PTrieNode; word: string); var node: PTrieNode; i,idx: Integer; begin node:=root; for i:=1 to Length(word) do begin idx:=Ord(word[i])-Ord('a'); if node^.children[idx]=nil then node^.children[idx]:=CreateNode; node:=node^.children[idx]; end; node^.isEnd:=True; end;"
    }
    
    def get_steps(self, arr):
        words_str = self.params.get("words")
        search_word = self.params.get("search_word")
        words = [w.strip() for w in words_str.split(",") if w.strip()]
        
        trie = Trie()
        comparisons = 0
        
        yield StructureStep(trie, current_value=None, code_line=1,
                            explanation=f"📚 Trie kezdés: {words}",
                            comparisons=0, extra={"words": words, "inserted": [], "search": search_word})
        
        inserted = []
        for word in words:
            comparisons+=1
            yield StructureStep(trie, current_value=word, code_line=9,
                                explanation=f"Trie beszúrás: '{word}' karakterenként",
                                comparisons=comparisons, extra={"words": words, "inserted": inserted, "current": word})
            trie.insert(word)
            trie.calculate_positions()
            inserted.append(word)
            yield StructureStep(trie, current_value=word, highlight_nodes=[word], code_line=12,
                                explanation=f"Beszúrva: '{word}'",
                                comparisons=comparisons, extra={"words": words, "inserted": inserted, "current": word})
        
        # Keresés
        yield StructureStep(trie, current_value=search_word, code_line=16,
                            explanation=f"🔍 Keresés: '{search_word}'",
                            comparisons=comparisons, extra={"words": words, "inserted": inserted, "search": search_word})
        
        found, path = trie.search(search_word)
        for i, node in enumerate(path):
            comparisons+=1
            yield StructureStep(trie, current_value=search_word, highlight_nodes=[node.char] if hasattr(node, 'char') else [], code_line=18,
                                explanation=f"Keres: '{search_word[:i]}' -> char '{node.char if hasattr(node,'char') else ''}'",
                                comparisons=comparisons, extra={"words": words, "search": search_word, "path": [n.char for n in path if hasattr(n,'char')], "current_char": node.char if hasattr(node,'char') else ''})
        
        yield StructureStep(trie, current_value=search_word, code_line=21,
                            explanation=f"{'✅ Megtalálva' if found else '❌ Nincs benne'}: '{search_word}'",
                            comparisons=comparisons, extra={"words": words, "search": search_word, "found": found, "path": [n.char for n in path if hasattr(n,'char')]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class BoyerMoorePlugin(AlgorithmPluginBase):
    id = "boyermoore"
    name = "Boyer-Moore"
    description = "Leggyorsabb gyakorlatban, jobbról balra, rossz karakter heurisztika"
    time_complexity = "O(n/m) legjobb, O(n*m) legrosszabb"
    space_complexity = "O(m + szigma)"
    icon = "🏃"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "string"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "ABAAABABAAABABAA", description="Hosszú szöveg"))
        self.params.add(Param("pattern", "Minta", "string", "ABABAA", description="Keresett"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """def bad_char_heuristic(minta):
    # Rossz karakter tábla: utolsó előfordulás
    bad_char={}
    for i in range(len(minta)):
        bad_char[minta[i]]=i
    return bad_char

def boyer_moore(szoveg, minta):
    n=len(szoveg)
    m=len(minta)
    bad_char=bad_char_heuristic(minta)
    s=0  # eltolás
    while s <= n-m:
        j=m-1
        # Jobbról balra hasonlít
        while j>=0 and minta[j]==szoveg[s+j]:
            j-=1
        if j<0:
            print(f"Találat {s}-ben")
            # Ugrás: ha van még szöveg, a következő karakter alapján
            s += m - bad_char.get(szoveg[s+m], -1) if s+m<n else 1
        else:
            # Rossz karakter szabály: ugrás
            s += max(1, j - bad_char.get(szoveg[s+j], -1))
    return bad_char
""",
        "C++": "map<char,int> badCharHeuristic(string pat){ map<char,int> bad; for(int i=0;i<pat.length();i++) bad[pat[i]]=i; return bad; } void boyerMoore(string txt, string pat){ int n=txt.length(), m=pat.length(); auto bad=badCharHeuristic(pat); int s=0; while(s<=n-m){ int j=m-1; while(j>=0 && pat[j]==txt[s+j]) j--; if(j<0){ cout<<\"Talalat \"<<s<<endl; s+= (s+m<n) ? m-bad[txt[s+m]] : 1; } else{ s+= max(1, j-bad[txt[s+j]]); } } }",
        "C": "/* Boyer-Moore C - rossz karakter */\nvoid badCharHeuristic(char* pat, int m, int bad[256]){for(int i=0;i<256;i++) bad[i]=-1; for(int i=0;i<m;i++) bad[(int)pat[i]]=i;} void boyerMoore(char* txt, char* pat){int n=strlen(txt), m=strlen(pat); int bad[256]; badCharHeuristic(pat,m,bad); int s=0; while(s<=n-m){int j=m-1; while(j>=0 && pat[j]==txt[s+j]) j--; if(j<0){printf(\"Talalat %d\\n\",s); s+= (s+m<n) ? m-bad[(int)txt[s+m]] : 1;} else{ int bc=j-bad[(int)txt[s+j]]; s+= bc>1? bc:1;}}}",
        "BASIC": "SUB BadCharHeuristic(pat AS STRING, bad() AS INTEGER): FOR i=0 TO 255: bad(i)=-1: NEXT: FOR i=0 TO LEN(pat)-1: bad(ASC(MID$(pat,i+1,1)))=i: NEXT: END SUB\nSUB BoyerMoore(txt AS STRING, pat AS STRING): n=LEN(txt): m=LEN(pat): DIM bad(255): BadCharHeuristic(pat,bad): s=0: WHILE s<=n-m: j=m-1: WHILE j>=0 AND MID$(pat,j+1,1)=MID$(txt,s+j+1,1): j=j-1: WEND: IF j<0 THEN PRINT \"Talalat \";s: s=s+IIF(s+m<n, m-bad(ASC(MID$(txt,s+m+1,1))), 1) ELSE s=s+MAX(1, j-bad(ASC(MID$(txt,s+j+1,1)))): WEND: END SUB",
        "Java": "Map<Character,Integer> badCharHeuristic(String pat){ Map<Character,Integer> bad=new HashMap<>(); for(int i=0;i<pat.length();i++) bad.put(pat.charAt(i), i); return bad; } void boyerMoore(String txt, String pat){ int n=txt.length(), m=pat.length(); Map<Character,Integer> bad=badCharHeuristic(pat); int s=0; while(s<=n-m){ int j=m-1; while(j>=0 && pat.charAt(j)==txt.charAt(s+j)) j--; if(j<0){ System.out.println(\"Talalat \"+s); s+= (s+m<n) ? m-bad.getOrDefault(txt.charAt(s+m), -1) : 1; } else{ s+= Math.max(1, j-bad.getOrDefault(txt.charAt(s+j), -1)); } } }",
        "Pascal": "procedure BadCharHeuristic(pat: string; var bad: array of Integer); var i: Integer; begin for i:=0 to 255 do bad[i]:=-1; for i:=0 to Length(pat)-1 do bad[Ord(pat[i+1])]:=i; end; procedure BoyerMoore(txt, pat: string); var n,m,s,j,bc: Integer; bad: array[0..255] of Integer; begin n:=Length(txt); m:=Length(pat); BadCharHeuristic(pat,bad); s:=0; while s<=n-m do begin j:=m-1; while (j>=0) and (pat[j+1]=txt[s+j+1]) do Dec(j); if j<0 then begin WriteLn('Talalat ',s); if s+m<n then s:=s+m-bad[Ord(txt[s+m+1])] else Inc(s); end else begin bc:=j-bad[Ord(txt[s+j+1])]; if bc>1 then s:=s+bc else Inc(s); end; end; end;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text")
        pattern = self.params.get("pattern")
        n = len(text)
        m = len(pattern)
        
        # Bad char tábla
        bad_char = {}
        for i in range(m):
            bad_char[pattern[i]] = i
        
        yield StructureStep(None, current_value=None, code_line=1,
                            explanation=f"🏃 Boyer-Moore: text='{text}' pat='{pattern}'",
                            comparisons=0, extra={"text": text, "pattern": pattern, "bad_char": dict(bad_char), "phase": "init"})
        
        yield StructureStep(None, current_value=None, code_line=3,
                            explanation=f"Rossz karakter tábla: {bad_char}",
                            comparisons=0, extra={"text": text, "pattern": pattern, "bad_char": dict(bad_char), "phase": "bad_char"})
        
        s = 0
        comparisons = 0
        found = []
        
        while s <= n-m:
            j = m-1
            comparisons+=1
            
            # Jobbról balra hasonlítás
            while j>=0 and pattern[j]==text[s+j]:
                yield StructureStep(None, current_value=text[s+j], code_line=12,
                                    explanation=f"Egyezik jobbról: pattern[{j}]='{pattern[j]}' == text[{s+j}]",
                                    comparisons=comparisons, extra={"text": text, "pattern": pattern, "s": s, "j": j, "bad_char": dict(bad_char), "found": found})
                j-=1
            
            if j<0:
                found.append(s)
                yield StructureStep(None, current_value=None, code_line=16,
                                    explanation=f"✅ TALÁLAT {s}-ben! Ugrás: m - bad_char[text[s+m]]",
                                    comparisons=comparisons, extra={"text": text, "pattern": pattern, "s": s, "j": j, "found": found, "bad_char": dict(bad_char), "phase": "találat"})
                s += m - bad_char.get(text[s+m], -1) if s+m<n else 1
            else:
                bc = j - bad_char.get(text[s+j], -1)
                jump = bc if bc>1 else 1
                yield StructureStep(None, current_value=text[s+j], code_line=19,
                                    explanation=f"Rossz karakter: text[{s+j}]='{text[s+j]}' pattern[{j}]='{pattern[j]}' -> ugrás {jump} (j - bad_char)",
                                    comparisons=comparisons, extra={"text": text, "pattern": pattern, "s": s, "j": j, "bad_char": dict(bad_char), "found": found, "phase": "ugrás", "jump": jump})
                s += jump
        
        yield StructureStep(None, current_value=None, code_line=21,
                            explanation=f"✅ Boyer-Moore vége, találatok: {found} | {comparisons} eltolás vs KMP/Rabin-Karp",
                            comparisons=comparisons, extra={"text": text, "pattern": pattern, "found": found, "bad_char": dict(bad_char)})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
