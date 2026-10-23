# -*- coding: utf-8 -*-
"""
Vörös-fekete fa + Fa bejárások pluginok - leglátványosabb forgatások
"""
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.structures import BST
import random

class RBNode:
    def __init__(self, value: int):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = "RED"  # RED vagy BLACK
        self.x = 0
        self.y = 0

class RBTree:
    def __init__(self):
        self.root = None
        self.NIL = RBNode(0)
        self.NIL.color = "BLACK"
        self.NIL.left = None
        self.NIL.right = None
    
    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        return y
    
    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        return y
    
    def insert(self, value: int):
        node = RBNode(value)
        node.left = self.NIL
        node.right = self.NIL
        
        y = None
        x = self.root
        
        while x and x != self.NIL:
            y = x
            if node.value < x.value:
                x = x.left
            else:
                x = x.right
        
        node.parent = y
        if not y:
            self.root = node
        elif node.value < y.value:
            y.left = node
        else:
            y.right = node
        
        if not node.parent:
            node.color = "BLACK"
            return
        
        if not node.parent.parent:
            return
        
        self._fix_insert(node)
    
    def _fix_insert(self, k):
        while k.parent and k.parent.color == "RED":
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if u.color == "RED":
                    u.color = "BLACK"
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    self._left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right
                if u.color == "RED":
                    u.color = "BLACK"
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    k.parent.color = "BLACK"
                    k.parent.parent.color = "RED"
                    self._right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = "BLACK"
    
    def calculate_positions(self):
        def assign(node, depth, x_offset):
            if not node or node == self.NIL:
                return x_offset
            x_offset = assign(node.left, depth+1, x_offset)
            node.x = x_offset * 70 + 50
            node.y = depth * 70 + 50
            x_offset += 1
            x_offset = assign(node.right, depth+1, x_offset)
            return x_offset
        assign(self.root, 0, 0)
    
    def inorder(self):
        result = []
        def dfs(node):
            if not node or node == self.NIL:
                return
            dfs(node.left)
            result.append(node)
            dfs(node.right)
        dfs(self.root)
        return result

class StructureStep:
    def __init__(self, structure, current_value=None, highlight_nodes=None, 
                 code_line=0, explanation="", comparisons=0, extra=None, path=None):
        self.structure = structure
        self.current_value = current_value
        self.highlight_nodes = highlight_nodes or []
        self.code_line = code_line
        self.explanation = explanation
        self.comparisons = comparisons
        self.extra = extra or {}
        self.path = path or []
        self.array = []
        self.key = current_value
        self.sorted_end = -1
        self.highlight = []
        self.shifts = 0
        self.pass_num = comparisons

class RedBlackTreePlugin(AlgorithmPluginBase):
    id = "rbtree"
    name = "Vörös-fekete Fa"
    description = "Önkiegyensúlyozó fa színekkel, forgatás + átszínezés"
    time_complexity = "O(log n)"
    space_complexity = "O(n)"
    icon = "🔴⚫"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "tree"
    
    codes = {
        "Python": """class RBNode:
    def __init__(self, val):
        self.val=val
        self.color="RED"
        self.left=self.right=self.parent=None

class RBTree:
    def __init__(self):
        self.NIL=RBNode(0)
        self.NIL.color="BLACK"
        self.root=None
    
    def left_rotate(self, x):
        y=x.right
        x.right=y.left
        if y.left: y.left.parent=x
        y.parent=x.parent
        if not x.parent: self.root=y
        elif x==x.parent.left: x.parent.left=y
        else: x.parent.right=y
        y.left=x
        x.parent=y
    
    def insert(self, val):
        node=RBNode(val)
        node.left=node.right=self.NIL
        y=None
        x=self.root
        while x and x!=self.NIL:
            y=x
            if node.val < x.val: x=x.left
            else: x=x.right
        node.parent=y
        if not y: self.root=node
        elif node.val < y.val: y.left=node
        else: y.right=node
        if not node.parent:
            node.color="BLACK"
            return
        self.fix_insert(node)
    
    def fix_insert(self, k):
        while k.parent and k.parent.color=="RED":
            if k.parent==k.parent.parent.right:
                u=k.parent.parent.left
                if u.color=="RED": # Case 1 - átszínez
                    u.color="BLACK"
                    k.parent.color="BLACK"
                    k.parent.parent.color="RED"
                    k=k.parent.parent
                else:
                    if k==k.parent.left: # Case 2 - forgat
                        k=k.parent
                        self.right_rotate(k)
                    k.parent.color="BLACK"
                    k.parent.parent.color="RED"
                    self.left_rotate(k.parent.parent)
            # ... tükör eset
        self.root.color="BLACK"
""",
        "C++": """enum Color{RED,BLACK};
struct Node{int val; Color color; Node *left,*right,*parent;};
class RBTree{
    Node *root, *NIL;
    void leftRotate(Node* x){
        Node* y=x->right;
        x->right=y->left;
        if(y->left) y->left->parent=x;
        y->parent=x->parent;
        if(!x->parent) root=y;
        else if(x==x->parent->left) x->parent->left=y;
        else x->parent->right=y;
        y->left=x; x->parent=y;
    }
    void fixInsert(Node* k){
        while(k->parent && k->parent->color==RED){
            if(k->parent==k->parent->parent->right){
                Node* u=k->parent->parent->left;
                if(u->color==RED){u->color=BLACK; k->parent->color=BLACK; k->parent->parent->color=RED; k=k->parent->parent;}
                else{if(k==k->parent->left){k=k->parent; rightRotate(k);} k->parent->color=BLACK; k->parent->parent->color=RED; leftRotate(k->parent->parent);}
            }
        }
        root->color=BLACK;
    }
};""",
        "C": "/* RB fa C - színek + forgatás */\n#define RED 0\n#define BLACK 1\nstruct Node{int val; int color; struct Node *left,*right,*parent;};\nvoid leftRotate(Node* x){Node* y=x->right; x->right=y->left; if(y->left) y->left->parent=x; y->parent=x->parent; if(!x->parent) root=y; else if(x==x->parent->left) x->parent->left=y; else x->parent->right=y; y->left=x; x->parent=y;}",
        "BASIC": "TYPE RBNode: val AS INTEGER: color AS STRING: left AS RBNode PTR: right AS RBNode PTR: parent AS RBNode PTR: END TYPE\nSUB LeftRotate(x AS RBNode PTR): y=x->right: x->right=y->left: IF y->left THEN y->left->parent=x: y->parent=x->parent: IF x->parent=NULL THEN root=y ELSE IF x=x->parent->left THEN x->parent->left=y ELSE x->parent->right=y: y->left=x: x->parent=y: END SUB",
        "Java": "enum Color{RED,BLACK} class Node{int val; Color color; Node left,right,parent; Node(int v){val=v; color=Color.RED;}} class RBTree{Node root, NIL; void leftRotate(Node x){Node y=x.right; x.right=y.left; if(y.left!=null) y.left.parent=x; y.parent=x.parent; if(x.parent==null) root=y; else if(x==x.parent.left) x.parent.left=y; else x.parent.right=y; y.left=x; x.parent=y;} void fixInsert(Node k){while(k.parent!=null && k.parent.color==Color.RED){/* ... */} root.color=Color.BLACK;}}",
        "Pascal": "type Color=(RED,BLACK); PNode=^Node; Node=record val: Integer; color: Color; left,right,parent: PNode; end; procedure LeftRotate(x: PNode); var y: PNode; begin y:=x^.right; x^.right:=y^.left; if y^.left<>nil then y^.left^.parent:=x; y^.parent:=x^.parent; if x^.parent=nil then root:=y else if x=x^.parent^.left then x^.parent^.left:=y else x^.parent^.right:=y; y^.left:=x; x^.parent:=y; end;"
    }
    
    def get_steps(self, arr):
        rbt = RBTree()
        values = [10, 20, 30, 15, 25, 5, 1, 35, 40]
        comparisons = 0
        
        yield StructureStep(rbt, current_value=None, code_line=1,
                            explanation=f"🔴⚫ Vörös-fekete fa kezdés: {values}",
                            comparisons=0, extra={"values": values, "inserted": []})
        
        inserted = []
        for val in values:
            comparisons+=1
            yield StructureStep(rbt, current_value=val, code_line=20,
                                explanation=f"Beszúrás: {val} mint PIROS node",
                                comparisons=comparisons, extra={"values": values, "inserted": inserted, "current": val})
            
            rbt.insert(val)
            rbt.calculate_positions()
            inserted.append(val)
            
            yield StructureStep(rbt, current_value=val, highlight_nodes=[val], code_line=40,
                                explanation=f"RB fixup: színek ellenőrzése, forgatás/átszínezés ha kell",
                                comparisons=comparisons, extra={"values": values, "inserted": inserted, "current": val, "rotation": True})
        
        inorder = [n.value for n in rbt.inorder()]
        yield StructureStep(rbt, current_value=None, code_line=50,
                            explanation=f"✅ RB fa kész, inorder: {inorder}, gyökér fekete, pirosnak nincs piros gyereke",
                            comparisons=comparisons, extra={"values": values, "inserted": inserted, "inorder": inorder})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class TraversalPlugin(AlgorithmPluginBase):
    id = "traversal"
    name = "Fa bejárások"
    description = "In-order, Pre-order, Post-order, Szint szerinti animálva"
    time_complexity = "O(n)"
    space_complexity = "O(h)"
    icon = "🚶"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "traversal"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("values", "Értékek", "string", "8,3,10,1,6,14,4,7,13", description="Fa építéshez"))
        self.params.add(Param("traversal_type", "Bejárás típusa", "choice", "mind", choices=["mind", "inorder", "preorder", "postorder", "levelorder"], description="Melyik bejárást mutassa"))
    
    def get_params(self):
        return self.params
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def inorder(node, eredmeny=[]):
    if node:
        inorder(node.left, eredmeny)
        eredmeny.append(node.val)  # Középen
        inorder(node.right, eredmeny)
    return eredmeny

def preorder(node, eredmeny=[]):
    if node:
        eredmeny.append(node.val)  # Elől
        preorder(node.left, eredmeny)
        preorder(node.right, eredmeny)
    return eredmeny

def postorder(node, eredmeny=[]):
    if node:
        postorder(node.left, eredmeny)
        postorder(node.right, eredmeny)
        eredmeny.append(node.val)  # Hátul
    return eredmeny

def levelorder(gyoker):
    from collections import deque
    if not gyoker: return []
    sor=deque([gyoker])
    eredmeny=[]
    while sor:
        node=sor.popleft()
        eredmeny.append(node.val)
        if node.left: sor.append(node.left)
        if node.right: sor.append(node.right)
    return eredmeny""",
        "C++": """void inorder(Node* node, vector<int>& res){
    if(node){ inorder(node->left, res); res.push_back(node->val); inorder(node->right, res); }
}
void preorder(Node* node, vector<int>& res){
    if(node){ res.push_back(node->val); preorder(node->left, res); preorder(node->right, res); }
}
void postorder(Node* node, vector<int>& res){
    if(node){ postorder(node->left, res); postorder(node->right, res); res.push_back(node->val); }
}
void levelorder(Node* root){
    if(!root) return;
    queue<Node*> q; q.push(root);
    while(!q.empty()){ Node* n=q.front(); q.pop(); cout<<n->val<<" "; if(n->left) q.push(n->left); if(n->right) q.push(n->right); }
}""",
        "C": "/* Bejárások C */\nvoid inorder(Node* node){ if(node){ inorder(node->left); printf(\"%d \", node->val); inorder(node->right); } }\nvoid preorder(Node* node){ if(node){ printf(\"%d \", node->val); preorder(node->left); preorder(node->right); } }\nvoid postorder(Node* node){ if(node){ postorder(node->left); postorder(node->right); printf(\"%d \", node->val); } }",
        "BASIC": "SUB InOrder(node)\n IF node<>NULL THEN InOrder(node->left): PRINT node->val: InOrder(node->right)\nEND SUB\nSUB PreOrder(node)\n IF node<>NULL THEN PRINT node->val: PreOrder(node->left): PreOrder(node->right)\nEND SUB\nSUB PostOrder(node)\n IF node<>NULL THEN PostOrder(node->left): PostOrder(node->right): PRINT node->val\nEND SUB",
        "Java": "void inorder(Node node, List<Integer> res){ if(node!=null){ inorder(node.left,res); res.add(node.val); inorder(node.right,res); } } void preorder(Node node, List<Integer> res){ if(node!=null){ res.add(node.val); preorder(node.left,res); preorder(node.right,res); } } void postorder(Node node, List<Integer> res){ if(node!=null){ postorder(node.left,res); postorder(node.right,res); res.add(node.val); } } void levelorder(Node root){ if(root==null) return; Queue<Node> q=new LinkedList<>(); q.add(root); while(!q.isEmpty()){ Node n=q.poll(); System.out.print(n.val+\" \"); if(n.left!=null) q.add(n.left); if(n.right!=null) q.add(n.right); } }",
        "Pascal": "procedure InOrder(node: PNode; var res: array of Integer); begin if node<>nil then begin InOrder(node^.left,res); Add(res,node^.val); InOrder(node^.right,res); end; end; procedure PreOrder(node: PNode; var res: array of Integer); begin if node<>nil then begin Add(res,node^.val); PreOrder(node^.left,res); PreOrder(node^.right,res); end; end; procedure PostOrder(node: PNode; var res: array of Integer); begin if node<>nil then begin PostOrder(node^.left,res); PostOrder(node^.right,res); Add(res,node^.val); end; end;"
    }
    
    def get_steps(self, arr):
        from core.structures import BST
        bst = BST()
        values = [8, 3, 10, 1, 6, 14, 4, 7, 13]
        for v in values:
            bst.insert(v)
        bst.calculate_positions()
        
        comparisons = 0
        
        yield StructureStep(bst, current_value=None, code_line=1,
                            explanation=f"🚶 Fa bejárások: fa {values}",
                            comparisons=0, extra={"values": values, "type": "fa"})
        
        # In-order
        inorder_result = []
        def inorder_gen(node):
            nonlocal comparisons
            if not node:
                return
            yield from inorder_gen(node.left)
            inorder_result.append(node.value)
            comparisons+=1
            yield StructureStep(bst, current_value=node.value, highlight_nodes=list(inorder_result), code_line=2,
                                explanation=f"In-order: bal -> gyökér -> jobb | {node.value} hozzáad",
                                comparisons=comparisons, extra={"traversal": "inorder", "result": list(inorder_result), "current": node.value})
            yield from inorder_gen(node.right)
        
        yield StructureStep(bst, current_value=None, code_line=1,
                            explanation="📖 In-order (rendezett): bal, gyökér, jobb",
                            comparisons=comparisons, extra={"traversal": "inorder", "result": []})
        yield from inorder_gen(bst.root)
        yield StructureStep(bst, current_value=None, code_line=3,
                            explanation=f"✅ In-order kész: {inorder_result} (rendezett!)",
                            comparisons=comparisons, extra={"traversal": "inorder", "result": inorder_result})
        
        # Pre-order
        preorder_result = []
        def preorder_gen(node):
            nonlocal comparisons
            if not node:
                return
            preorder_result.append(node.value)
            comparisons+=1
            yield StructureStep(bst, current_value=node.value, highlight_nodes=list(preorder_result), code_line=9,
                                explanation=f"Pre-order: gyökér -> bal -> jobb | {node.value}",
                                comparisons=comparisons, extra={"traversal": "preorder", "result": list(preorder_result), "current": node.value})
            yield from preorder_gen(node.left)
            yield from preorder_gen(node.right)
        
        yield StructureStep(bst, current_value=None, code_line=8,
                            explanation="📖 Pre-order: gyökér, bal, jobb (másoláshoz jó)",
                            comparisons=comparisons, extra={"traversal": "preorder", "result": []})
        yield from preorder_gen(bst.root)
        yield StructureStep(bst, current_value=None, code_line=10,
                            explanation=f"✅ Pre-order kész: {preorder_result}",
                            comparisons=comparisons, extra={"traversal": "preorder", "result": preorder_result})
        
        # Post-order
        postorder_result = []
        def postorder_gen(node):
            nonlocal comparisons
            if not node:
                return
            yield from postorder_gen(node.left)
            yield from postorder_gen(node.right)
            postorder_result.append(node.value)
            comparisons+=1
            yield StructureStep(bst, current_value=node.value, highlight_nodes=list(postorder_result), code_line=16,
                                explanation=f"Post-order: bal -> jobb -> gyökér | {node.value}",
                                comparisons=comparisons, extra={"traversal": "postorder", "result": list(postorder_result), "current": node.value})
        
        yield StructureStep(bst, current_value=None, code_line=15,
                            explanation="📖 Post-order: bal, jobb, gyökér (törléshez jó)",
                            comparisons=comparisons, extra={"traversal": "postorder", "result": []})
        yield from postorder_gen(bst.root)
        yield StructureStep(bst, current_value=None, code_line=17,
                            explanation=f"✅ Post-order kész: {postorder_result}",
                            comparisons=comparisons, extra={"traversal": "postorder", "result": postorder_result})
        
        # Level-order
        from collections import deque
        level_result = []
        q = deque([bst.root] if bst.root else [])
        yield StructureStep(bst, current_value=None, code_line=20,
                            explanation="📖 Szint szerinti (BFS): szintenként, sorral",
                            comparisons=comparisons, extra={"traversal": "levelorder", "result": []})
        while q:
            node = q.popleft()
            if not node:
                continue
            level_result.append(node.value)
            comparisons+=1
            yield StructureStep(bst, current_value=node.value, highlight_nodes=list(level_result), code_line=27,
                                explanation=f"Level-order: sorból kivesz {node.value}, gyerekeit sorba",
                                comparisons=comparisons, extra={"traversal": "levelorder", "result": list(level_result), "current": node.value, "queue": [n.value for n in q]})
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        
        yield StructureStep(bst, current_value=None, code_line=28,
                            explanation=f"✅ Level-order kész: {level_result} | Minden bejárás bemutatva!",
                            comparisons=comparisons, extra={"traversal": "levelorder", "result": level_result})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
