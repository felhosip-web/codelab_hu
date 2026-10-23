# -*- coding: utf-8 -*-
"""
Fa és Hash struktúrák motor
"""
from typing import Optional, List, Dict

class TreeNode:
    def __init__(self, value: int):
        self.value = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        self.height = 1
        self.x = 0
        self.y = 0
        self.parent = None

class BST:
    def __init__(self):
        self.root: Optional[TreeNode] = None
        self.nodes_list: List[TreeNode] = []
    
    def insert(self, value: int):
        self.root = self._insert_rec(self.root, value)
    
    def _insert_rec(self, node: Optional[TreeNode], value: int) -> TreeNode:
        if not node:
            new_node = TreeNode(value)
            self.nodes_list.append(new_node)
            return new_node
        if value < node.value:
            node.left = self._insert_rec(node.left, value)
            node.left.parent = node
        elif value > node.value:
            node.right = self._insert_rec(node.right, value)
            node.right.parent = node
        return node
    
    def search_path(self, value: int) -> List[TreeNode]:
        path = []
        cur = self.root
        while cur:
            path.append(cur)
            if cur.value == value:
                break
            elif value < cur.value:
                cur = cur.left
            else:
                cur = cur.right
        return path
    
    def calculate_positions(self):
        """Fa pozíciók kiszámítása rajzoláshoz"""
        def assign_pos(node, depth, x_offset):
            if not node:
                return x_offset
            x_offset = assign_pos(node.left, depth+1, x_offset)
            node.x = x_offset * 70 + 50
            node.y = depth * 70 + 50
            x_offset += 1
            x_offset = assign_pos(node.right, depth+1, x_offset)
            return x_offset
        assign_pos(self.root, 0, 0)

class AVLTree(BST):
    def _height(self, node):
        return node.height if node else 0
    
    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))
    
    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0
    
    def _rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        if T2: T2.parent = y
        x.parent = y.parent
        y.parent = x
        self._update_height(y)
        self._update_height(x)
        return x
    
    def _rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        if T2: T2.parent = x
        y.parent = x.parent
        x.parent = y
        self._update_height(x)
        self._update_height(y)
        return y
    
    def _insert_rec(self, node, value):
        if not node:
            new_node = TreeNode(value)
            self.nodes_list.append(new_node)
            return new_node
        
        if value < node.value:
            node.left = self._insert_rec(node.left, value)
            node.left.parent = node
        elif value > node.value:
            node.right = self._insert_rec(node.right, value)
            node.right.parent = node
        else:
            return node
        
        self._update_height(node)
        balance = self._balance_factor(node)
        
        # LL
        if balance > 1 and value < node.left.value:
            return self._rotate_right(node)
        # RR
        if balance < -1 and value > node.right.value:
            return self._rotate_left(node)
        # LR
        if balance > 1 and value > node.left.value:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # RL
        if balance < -1 and value < node.right.value:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node

class HashTable:
    def __init__(self, size=8):
        self.size = size
        self.buckets: List[List[int]] = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key: int) -> int:
        return key % self.size
    
    def insert(self, key: int):
        idx = self._hash(key)
        if key not in self.buckets[idx]:
            self.buckets[idx].append(key)
            self.count += 1
    
    def search(self, key: int) -> tuple:
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, v in enumerate(bucket):
            if v == key:
                return (idx, i, True)
        return (idx, -1, False)
