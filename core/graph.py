# -*- coding: utf-8 -*-
"""
Gráf motor - csomópontok, élek, algoritmusokhoz
"""
from typing import Dict, List, Tuple
import math
import random

class GraphNode:
    def __init__(self, id: int, x: float, y: float, label: str = ""):
        self.id = id
        self.x = x
        self.y = y
        self.label = label or str(id)
        self.neighbors: List[Tuple[int, float]] = []  # (neighbor_id, weight)

class Graph:
    def __init__(self):
        self.nodes: Dict[int, GraphNode] = {}
        self.edges: List[Tuple[int, int, float]] = []  # (from, to, weight)
    
    def add_node(self, id: int, x: float, y: float, label: str = ""):
        self.nodes[id] = GraphNode(id, x, y, label)
    
    def add_edge(self, u: int, v: int, weight: float = 1.0, directed=False):
        if u in self.nodes and v in self.nodes:
            self.nodes[u].neighbors.append((v, weight))
            self.edges.append((u, v, weight))
            if not directed:
                self.nodes[v].neighbors.append((u, weight))
                self.edges.append((v, u, weight))
    
    @classmethod
    def create_sample_maze(cls, size=6):
        """Rács gráf, mint labirintus"""
        g = cls()
        # Node-ok rácsban
        for r in range(size):
            for c in range(size):
                id = r*size + c
                g.add_node(id, c*80+40, r*80+40, f"{id}")
        # Élek jobbra és le
        for r in range(size):
            for c in range(size):
                id = r*size + c
                if c < size-1:
                    # Random súly, néha nincs él (fal)
                    if random.random() > 0.2:
                        g.add_edge(id, id+1, random.randint(1, 9))
                if r < size-1:
                    if random.random() > 0.2:
                        g.add_edge(id, id+size, random.randint(1, 9))
        return g
    
    @classmethod
    def create_random_weighted(cls, n=8):
        g = cls()
        # Körben elhelyezve
        for i in range(n):
            angle = 2*math.pi*i/n
            x = 200 + 150*math.cos(angle)
            y = 200 + 150*math.sin(angle)
            g.add_node(i, x, y, f"{i}")
        # Random élek
        for i in range(n):
            for j in range(i+1, n):
                if random.random() > 0.5:
                    g.add_edge(i, j, random.randint(1, 20))
        return g
    
    @classmethod
    def create_pathfinding_grid(cls, size=8):
        """A* -hoz rács akadályokkal"""
        g = cls()
        obstacles = set(random.sample(range(size*size), size*2))
        for r in range(size):
            for c in range(size):
                id = r*size + c
                if id in obstacles:
                    continue
                g.add_node(id, c*60+30, r*60+30, f"{id}")
        for r in range(size):
            for c in range(size):
                id = r*size + c
                if id not in g.nodes:
                    continue
                for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    nid = nr*size+nc
                    if 0 <= nr < size and 0 <= nc < size and nid in g.nodes:
                        g.add_edge(id, nid, 1)
        return g
