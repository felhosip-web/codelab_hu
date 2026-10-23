# -*- coding: utf-8 -*-
"""
Bonyolultsági szint jelző - egyszerűtől a bonyolultig
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class ComplexityLevel(Enum):
    BEGINNER = 1      # 🟢 Kezdő - 5-10 sor, egy ciklus, vizuálisan azonnal érthető
    EASY = 2          # 🟡 Könnyű - 10-20 sor, egy-két ciklus, alap adatszerkezet
    MEDIUM = 3        # 🟠 Közepes - 20-40 sor, rekurzió vagy több ciklus
    HARD = 4          # 🔴 Nehéz - 40-80 sor, komplex logika, több adatszerkezet
    EXPERT = 5        # ⚫ Expert - 80+ sor, haladó matek, optimalizáció, mindenhol használják

@dataclass
class ComplexityInfo:
    level: ComplexityLevel
    emoji: str
    name: str
    description: str
    lines: str
    concepts: List[str]
    time_to_understand: str
    color: str

class ComplexityManager:
    def __init__(self):
        self.levels: Dict[ComplexityLevel, ComplexityInfo] = {
            ComplexityLevel.BEGINNER: ComplexityInfo(
                level=ComplexityLevel.BEGINNER,
                emoji="🟢",
                name="Kezdő",
                description="5-10 sor, egy ciklus, azonnal érthető",
                lines="5-10",
                concepts=["változó", "ciklus", "if"],
                time_to_understand="2-5 perc",
                color="#00b894"
            ),
            ComplexityLevel.EASY: ComplexityInfo(
                level=ComplexityLevel.EASY,
                emoji="🟡",
                name="Könnyű",
                description="10-20 sor, egy-két ciklus, alap adatszerkezet",
                lines="10-20",
                concepts=["tömb", "függvény", "ciklus"],
                time_to_understand="5-10 perc",
                color="#fdcb6e"
            ),
            ComplexityLevel.MEDIUM: ComplexityInfo(
                level=ComplexityLevel.MEDIUM,
                emoji="🟠",
                name="Közepes",
                description="20-40 sor, rekurzió vagy több ciklus",
                lines="20-40",
                concepts=["rekurzió", "2D tömb", "pointer"],
                time_to_understand="10-20 perc",
                color="#e17055"
            ),
            ComplexityLevel.HARD: ComplexityInfo(
                level=ComplexityLevel.HARD,
                emoji="🔴",
                name="Nehéz",
                description="40-80 sor, komplex logika",
                lines="40-80",
                concepts=["gráf", "fa", "dinamikus programozás"],
                time_to_understand="20-40 perc",
                color="#d63031"
            ),
            ComplexityLevel.EXPERT: ComplexityInfo(
                level=ComplexityLevel.EXPERT,
                emoji="⚫",
                name="Expert",
                description="80+ sor, haladó matek, mindenhol használják",
                lines="80+",
                concepts=["FFT", "Enigma", "CRC", "optimalizáció"],
                time_to_understand="40+ perc",
                color="#2d3436"
            ),
        }
    
    def get_info(self, level: ComplexityLevel) -> ComplexityInfo:
        return self.levels[level]
    
    def get_by_plugin_type(self, plugin_type: str) -> ComplexityLevel:
        mapping = {
            "simple": ComplexityLevel.BEGINNER,
            "math": ComplexityLevel.BEGINNER,
            "recursion": ComplexityLevel.EASY,
            "array": ComplexityLevel.EASY,
            "fifo_lifo": ComplexityLevel.EASY,
            "sort": ComplexityLevel.MEDIUM,
            "search": ComplexityLevel.EASY,
            "string": ComplexityLevel.MEDIUM,
            "graph": ComplexityLevel.HARD,
            "tree": ComplexityLevel.HARD,
            "hash": ComplexityLevel.MEDIUM,
            "encoding": ComplexityLevel.HARD,
            "crc": ComplexityLevel.EXPERT,
            "fourier": ComplexityLevel.EXPERT,
        }
        return mapping.get(plugin_type, ComplexityLevel.MEDIUM)
    
    def classify_plugin(self, plugin_id: str) -> ComplexityLevel:
        # Egyszerű szabályok plugin id alapján
        beginner = ["factorial", "fibonacci_iter", "gcd", "prime_check", "palindrome", "array_basics"]
        easy = ["fibonacci_rec", "sieve", "hanoi", "binary", "anagram", "stack", "queue", "linear_search", "array_2d", "pointer", "deque", "bubble", "insertion"]
        medium = ["quick", "merge", "kmp", "binary_search", "array_in_array", "circular_queue", "dft"]
        hard = ["bfs", "dfs", "dijkstra", "bst", "avl", "huffman", "enigma"]
        expert = ["fft", "crc", "reed_solomon", "a_star"]
        
        if plugin_id in beginner:
            return ComplexityLevel.BEGINNER
        elif plugin_id in easy:
            return ComplexityLevel.EASY
        elif plugin_id in medium:
            return ComplexityLevel.MEDIUM
        elif plugin_id in hard:
            return ComplexityLevel.HARD
        elif plugin_id in expert:
            return ComplexityLevel.EXPERT
        else:
            return ComplexityLevel.MEDIUM
