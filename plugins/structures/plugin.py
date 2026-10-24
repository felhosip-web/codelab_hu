# -*- coding: utf-8 -*-
from typing import List, Set
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.structures import BST, AVLTree, HashTable
import random

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

class BSTPlugin(AlgorithmPluginBase):
    id = "bst"
    name = "BST - Bináris keresőfa"
    description = "Beszúrás, keresés fa bejárással, O(log n) átlag"
    time_complexity = "O(log n) átlag"
    space_complexity = "O(n)"
    icon = "🌳"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "tree"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("values", "Értékek", "string", "8,3,10,1,6,14,4,7,13", description="Vesszővel"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """class Node:
    def __init__(self, val):
        self.val=val
        self.left=None
        self.right=None

def beszuras(gyoker, ertek):
    if not gyoker:
        return Node(ertek)
    if ertek < gyoker.val:
        gyoker.left = beszuras(gyoker.left, ertek)
    elif ertek > gyoker.val:
        gyoker.right = beszuras(gyoker.right, ertek)
    return gyoker

def kereses(gyoker, ertek):
    while gyoker:
        if ertek == gyoker.val:
            return gyoker
        elif ertek < gyoker.val:
            gyoker = gyoker.left
        else:
            gyoker = gyoker.right
    return None""",
        "C++": """struct Node{int val; Node *left,*right; Node(int v): val(v), left(nullptr), right(nullptr){}};
Node* insert(Node* root, int val){
    if(!root) return new Node(val);
    if(val < root->val) root->left = insert(root->left, val);
    else if(val > root->val) root->right = insert(root->right, val);
    return root;
}
Node* search(Node* root, int val){
    while(root){
        if(val==root->val) return root;
        else if(val<root->val) root=root->left;
        else root=root->right;
    }
    return nullptr;
}""",
        "C": "/* BST C */\nstruct Node{int val; struct Node *left,*right;};\nstruct Node* insert(struct Node* root, int val){ if(!root){struct Node* n=malloc(sizeof(*n)); n->val=val; n->left=n->right=NULL; return n;} if(val<root->val) root->left=insert(root->left,val); else if(val>root->val) root->right=insert(root->right,val); return root;}",
        "BASIC": "TYPE Node: val AS INTEGER: left AS Node PTR: right AS Node PTR: END TYPE\nFUNCTION Insert(root AS Node PTR, val AS INTEGER) AS Node PTR\n IF root=NULL THEN RETURN NEW Node(val)\n IF val<root->val THEN root->left=Insert(root->left,val) ELSE IF val>root->val THEN root->right=Insert(root->right,val)\n RETURN root\nEND FUNCTION",
        "Java": "class Node{int val; Node left,right; Node(int v){val=v;}} Node insert(Node root, int val){ if(root==null) return new Node(val); if(val<root.val) root.left=insert(root.left,val); else if(val>root.val) root.right=insert(root.right,val); return root; } Node search(Node root, int val){ while(root!=null){ if(val==root.val) return root; else if(val<root.val) root=root.left; else root=root.right;} return null;}",
        "Pascal": "type PNode=^Node; Node=record val: Integer; left,right: PNode; end; function Insert(root: PNode; val: Integer): PNode; begin if root=nil then begin New(root); root^.val:=val; root^.left:=nil; root^.right:=nil; end else if val<root^.val then root^.left:=Insert(root^.left,val) else if val>root^.val then root^.right:=Insert(root^.right,val); Result:=root; end;"
    }
    
    def get_steps(self, arr):
        bst = BST()
        values = [8, 3, 10, 1, 6, 14, 4, 7, 13]
        random.shuffle(values)
        comparisons = 0
        
        yield StructureStep(bst, current_value=None, code_line=1,
                            explanation=f"🌳 BST kezdés: {values} beszúrása",
                            comparisons=0, extra={"values": values, "inserted": []})
        
        inserted = []
        for val in values:
            comparisons+=1
            # Keresési út mutatása beszúrás előtt
            path = []
            cur = bst.root
            while cur:
                path.append(cur.value)
                if val < cur.value:
                    cur = cur.left
                elif val > cur.value:
                    cur = cur.right
                else:
                    break
                yield StructureStep(bst, current_value=val, highlight_nodes=path, code_line=6,
                                    explanation=f"Keres: {val} {path[-1] if path else ''} -> {'bal' if val < path[-1] else 'jobb' if path else ''}",
                                    comparisons=comparisons, extra={"values": values, "inserted": inserted, "path": path, "current": val})
            
            bst.insert(val)
            bst.calculate_positions()
            inserted.append(val)
            yield StructureStep(bst, current_value=val, highlight_nodes=[val], code_line=3,
                                explanation=f"Beszúrva: {val} a fa {len(inserted)}. elemeként",
                                comparisons=comparisons, extra={"values": values, "inserted": inserted, "current": val, "path": path})
        
        # Keresés bemutatása
        search_val = random.choice(values)
        yield StructureStep(bst, current_value=search_val, code_line=12,
                            explanation=f"🔍 Keresés: {search_val}",
                            comparisons=comparisons, extra={"search": search_val})
        
        path = bst.search_path(search_val)
        for node in path:
            comparisons+=1
            yield StructureStep(bst, current_value=search_val, highlight_nodes=[n.value for n in path[:path.index(node)+1]], code_line=14,
                                explanation=f"Keres: {search_val} vs {node.value}",
                                comparisons=comparisons, extra={"search": search_val, "path": [n.value for n in path]})
        
        yield StructureStep(bst, current_value=search_val, highlight_nodes=[search_val], code_line=15,
                            explanation=f"✅ Megtalálva: {search_val}",
                            comparisons=comparisons, extra={"search": search_val, "found": True, "path": [n.value for n in path]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class AVLPlugin(AlgorithmPluginBase):
    id = "avl"
    name = "AVL Fa - Kiegyensúlyozott"
    description = "Önkiegyensúlyozó fa, forgatásokkal, mindig O(log n)"
    time_complexity = "O(log n)"
    space_complexity = "O(n)"
    icon = "⚖️"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "tree"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("values", "Értékek", "string", "8,3,10,1,6,14,4,7,13", description="Vesszővel"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """class AVLNode:
    def __init__(self, val):
        self.val=val
        self.left=None
        self.right=None
        self.height=1

def magassag(n): return n.height if n else 0

def forgat_jobbra(y):
    x=y.left; T2=x.right
    x.right=y; y.left=T2
    y.height=1+max(magassag(y.left),magassag(y.right))
    x.height=1+max(magassag(x.left),magassag(x.right))
    return x

def beszuras(node, val):
    if not node: return AVLNode(val)
    if val<node.val: node.left=beszuras(node.left,val)
    elif val>node.val: node.right=beszuras(node.right,val)
    node.height=1+max(magassag(node.left),magassag(node.right))
    balance=magassag(node.left)-magassag(node.right)
    # LL, RR, LR, RL forgatások...
    return node""",
        "C++": """int height(Node* n){return n? n->height:0;}
int balance(Node* n){return n? height(n->left)-height(n->right):0;}
Node* rightRotate(Node* y){Node* x=y->left; Node* T2=x->right; x->right=y; y->left=T2; y->height=1+max(height(y->left),height(y->right)); x->height=1+max(height(x->left),height(x->right)); return x;}
Node* insert(Node* node, int val){ if(!node) return new Node(val); if(val<node->val) node->left=insert(node->left,val); else if(val>node->val) node->right=insert(node->right,val); node->height=1+max(height(node->left),height(node->right)); int bal=balance(node); /* LL, RR, LR, RL */ return node; }""",
        "C": "/* AVL C - forgatások */\nint height(Node* n){return n? n->height:0;} Node* rightRotate(Node* y){Node* x=y->left; Node* T2=x->right; x->right=y; y->left=T2; y->height=1+max(height(y->left),height(y->right)); x->height=1+max(height(x->left),height(x->right)); return x;}",
        "BASIC": "FUNCTION Height(n): IF n=NULL THEN Height=0 ELSE Height=n->height: END FUNCTION\nFUNCTION RightRotate(y): x=y->left: T2=x->right: x->right=y: y->left=T2: y->height=1+MAX(Height(y->left),Height(y->right)): x->height=1+MAX(Height(x->left),Height(x->right)): RightRotate=x: END FUNCTION",
        "Java": "int height(Node n){return n!=null? n.height:0;} Node rightRotate(Node y){Node x=y.left; Node T2=x.right; x.right=y; y.left=T2; y.height=1+Math.max(height(y.left),height(y.right)); x.height=1+Math.max(height(x.left),height(x.right)); return x;} Node insert(Node node, int val){ if(node==null) return new Node(val); if(val<node.val) node.left=insert(node.left,val); else if(val>node.val) node.right=insert(node.right,val); node.height=1+Math.max(height(node.left),height(node.right)); int bal=height(node.left)-height(node.right); /* forgatások */ return node;}",
        "Pascal": "function Height(n: PNode): Integer; begin if n=nil then Result:=0 else Result:=n^.height; end; function RightRotate(y: PNode): PNode; var x: PNode; T2: PNode; begin x:=y^.left; T2:=x^.right; x^.right:=y; y^.left:=T2; y^.height:=1+Max(Height(y^.left),Height(y^.right)); x^.height:=1+Max(Height(x^.left),Height(x^.right)); Result:=x; end;"
    }
    
    def get_steps(self, arr):
        avl = AVLTree()
        values = [10, 20, 30, 40, 50, 25]  # Olyan sor ami forgatást okoz
        comparisons = 0
        
        yield StructureStep(avl, current_value=None, code_line=1,
                            explanation=f"⚖️ AVL kezdés: {values} (forgatások lesznek)",
                            comparisons=0, extra={"values": values, "inserted": []})
        
        inserted = []
        for val in values:
            comparisons+=1
            yield StructureStep(avl, current_value=val, code_line=12,
                                explanation=f"Beszúrás: {val}, egyensúly ellenőrzés",
                                comparisons=comparisons, extra={"values": values, "inserted": inserted, "current": val})
            
            avl.insert(val)
            avl.calculate_positions()
            inserted.append(val)
            
            # Ellenőrizzük volt-e forgatás (magasság változás)
            yield StructureStep(avl, current_value=val, highlight_nodes=[val], code_line=15,
                                explanation=f"AVL beszúrva: {val}, magasság frissítve, forgatás ha kell (balance)",
                                comparisons=comparisons, extra={"values": values, "inserted": inserted, "current": val, "rotation": True})
        
        yield StructureStep(avl, current_value=None, code_line=18,
                            explanation=f"✅ AVL fa kész, mindig kiegyensúlyozott, magasság={avl.root.height if avl.root else 0}",
                            comparisons=comparisons, extra={"values": values, "inserted": inserted})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class HashTablePlugin(AlgorithmPluginBase):
    id = "hashtable"
    name = "Hash Tábla"
    description = "Láncolt listás hash, O(1) átlagos keresés"
    time_complexity = "O(1) átlag"
    space_complexity = "O(n)"
    icon = "🗃️"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "hash"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("hash_size", "Hash méret", "int", 6, 3, 12))
        self.params.add(Param("values", "Értékek", "string", "12,22,32,7,17,27,5,15", description="Vesszővel"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """class HashTabla:
    def __init__(self, meret=8):
        self.meret=meret
        self.vodrok=[[] for _ in range(meret)]
    
    def hash_fv(self, kulcs):
        return kulcs % self.meret
    
    def beszuras(self, kulcs):
        idx=self.hash_fv(kulcs)
        if kulcs not in self.vodrok[idx]:
            self.vodrok[idx].append(kulcs)
    
    def kereses(self, kulcs):
        idx=self.hash_fv(kulcs)
        return kulcs in self.vodrok[idx]""",
        "C++": """class HashTable{
    int size; vector<vector<int>> buckets;
public:
    HashTable(int s=8): size(s), buckets(s){}
    int hashFunc(int key){return key % size;}
    void insert(int key){
        int idx=hashFunc(key);
        if(find(buckets[idx].begin(), buckets[idx].end(), key)==buckets[idx].end())
            buckets[idx].push_back(key);
    }
    bool search(int key){
        int idx=hashFunc(key);
        return find(buckets[idx].begin(), buckets[idx].end(), key)!=buckets[idx].end();
    }
};""",
        "C": "/* Hash C */\n#define SIZE 8\nstruct Node{int key; struct Node* next;}; struct Node* table[SIZE]={0};\nint hashFunc(int key){return key%SIZE;}\nvoid insert(int key){int idx=hashFunc(key); struct Node* n=malloc(sizeof(*n)); n->key=key; n->next=table[idx]; table[idx]=n;}\nint search(int key){int idx=hashFunc(key); struct Node* cur=table[idx]; while(cur){if(cur->key==key) return 1; cur=cur->next;} return 0;}",
        "BASIC": "DIM buckets(SIZE) AS List\nFUNCTION HashFunc(key): HashFunc=key MOD SIZE: END FUNCTION\nSUB Insert(key): idx=HashFunc(key): IF NOT Contains(buckets(idx), key) THEN buckets(idx).Add(key): END SUB\nFUNCTION Search(key): idx=HashFunc(key): Search=Contains(buckets(idx), key): END FUNCTION",
        "Java": "class HashTable{int size; List<List<Integer>> buckets; HashTable(int s){size=s; buckets=new ArrayList<>(s); for(int i=0;i<s;i++) buckets.add(new ArrayList<>());} int hashFunc(int key){return key%size;} void insert(int key){int idx=hashFunc(key); if(!buckets.get(idx).contains(key)) buckets.get(idx).add(key);} boolean search(int key){int idx=hashFunc(key); return buckets.get(idx).contains(key);}}",
        "Pascal": "type HashTable=record size: Integer; buckets: array of array of Integer; end; function HashFunc(key, size: Integer): Integer; begin Result:=key mod size; end; procedure Insert(var ht: HashTable; key: Integer); var idx: Integer; begin idx:=HashFunc(key, ht.size); if not Contains(ht.buckets[idx], key) then Add(ht.buckets[idx], key); end;"
    }
    
    def get_steps(self, arr):
        ht = HashTable(size=6)
        values = [12, 22, 32, 7, 17, 27, 5, 15]
        comparisons = 0
        
        yield StructureStep(ht, current_value=None, code_line=1,
                            explanation=f"🗃️ Hash tábla kezdés: méret={ht.size}, láncolt",
                            comparisons=0, extra={"values": values, "buckets": [list(b) for b in ht.buckets], "size": ht.size})
        
        for val in values:
            comparisons+=1
            idx = ht._hash(val)
            yield StructureStep(ht, current_value=val, code_line=6,
                                explanation=f"Hash: {val} % {ht.size} = {idx} -> vödör {idx}",
                                comparisons=comparisons, extra={"values": values, "current": val, "hash_idx": idx, "buckets": [list(b) for b in ht.buckets]})
            
            is_collision = len(ht.buckets[idx]) > 0
            if is_collision:
                yield StructureStep(ht, current_value=val, code_line=8,
                                    explanation=f"Ütközés! Vödör {idx} már tartalmaz: {ht.buckets[idx]}, láncoljuk",
                                    comparisons=comparisons, extra={"values": values, "current": val, "hash_idx": idx, "buckets": [list(b) for b in ht.buckets], "collision": True})
            
            ht.insert(val)
            yield StructureStep(ht, current_value=val, code_line=9,
                                explanation=f"Beszúrva: {val} -> vödör {idx}: {ht.buckets[idx]}",
                                comparisons=comparisons, extra={"values": values, "current": val, "hash_idx": idx, "buckets": [list(b) for b in ht.buckets]})
        
        # Keresés
        search_val = random.choice(values)
        idx, pos, found = ht.search(search_val)
        yield StructureStep(ht, current_value=search_val, code_line=12,
                            explanation=f"🔍 Keresés: {search_val} hash={idx}",
                            comparisons=comparisons, extra={"search": search_val, "hash_idx": idx, "buckets": [list(b) for b in ht.buckets]})
        
        yield StructureStep(ht, current_value=search_val, code_line=13,
                            explanation=f"✅ Megtalálva: vödör {idx}, pozíció {pos}" if found else f"❌ Nincs benne",
                            comparisons=comparisons+1, extra={"search": search_val, "hash_idx": idx, "found": found, "buckets": [list(b) for b in ht.buckets]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
