# -*- coding: utf-8 -*-
"""
String Matching motor - KMP és Rabin-Karp
"""
from typing import List, Dict

class KMPMatcher:
    @staticmethod
    def compute_lps(pattern: str) -> List[int]:
        """Longest Prefix Suffix táblázat"""
        m = len(pattern)
        lps = [0]*m
        length = 0
        i = 1
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length-1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

class RabinKarpMatcher:
    @staticmethod
    def hash_func(s: str, base=256, mod=101):
        h = 0
        for ch in s:
            h = (h*base + ord(ch)) % mod
        return h
