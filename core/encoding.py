# -*- coding: utf-8 -*-
"""
Kódoló-dekódoló motorok - Huffman, RLE, Caesar, Base64, LZW
"""
from collections import Counter, defaultdict
import heapq
import base64

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
        self.code = ""
        self.x = 0
        self.y = 0
    
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoding:
    def __init__(self, text=""):
        self.text = text
        self.root = None
        self.codes = {}
        self.reverse_codes = {}
        if text:
            self.build(text)
    
    def build(self, text):
        self.text = text
        freq = Counter(text)
        heap = [HuffmanNode(char, f) for char, f in freq.items()]
        heapq.heapify(heap)
        
        if len(heap) == 1:
            node = heapq.heappop(heap)
            self.root = HuffmanNode(freq=node.freq, left=node)
            self._generate_codes(self.root, "")
            return
        
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq+right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0] if heap else None
        self._generate_codes(self.root, "")
    
    def _generate_codes(self, node, current_code):
        if not node:
            return
        if node.char is not None:
            node.code = current_code or "0"
            self.codes[node.char] = node.code
            self.reverse_codes[node.code] = node.char
            return
        node.code = current_code
        self._generate_codes(node.left, current_code+"0")
        self._generate_codes(node.right, current_code+"1")
    
    def encode(self):
        return "".join(self.codes.get(ch, "") for ch in self.text)
    
    def decode(self, encoded):
        decoded = ""
        current = ""
        for bit in encoded:
            current += bit
            if current in self.reverse_codes:
                decoded += self.reverse_codes[current]
                current = ""
        return decoded
    
    def calculate_positions(self):
        def assign(node, depth, x_offset):
            if not node:
                return x_offset
            x_offset = assign(node.left, depth+1, x_offset)
            node.x = x_offset * 80 + 40
            node.y = depth * 70 + 40
            x_offset += 1
            x_offset = assign(node.right, depth+1, x_offset)
            return x_offset
        assign(self.root, 0, 0)

class RLE:
    @staticmethod
    def encode(text):
        if not text:
            return ""
        encoded = []
        count = 1
        for i in range(1, len(text)):
            if text[i] == text[i-1]:
                count+=1
            else:
                encoded.append(f"{count}{text[i-1]}")
                count=1
        encoded.append(f"{count}{text[-1]}")
        return "".join(encoded)
    
    @staticmethod
    def decode(encoded):
        decoded = ""
        i = 0
        while i < len(encoded):
            count_str = ""
            while i < len(encoded) and encoded[i].isdigit():
                count_str+=encoded[i]
                i+=1
            if i < len(encoded) and count_str:
                decoded += encoded[i]*int(count_str)
                i+=1
        return decoded

class CaesarCipher:
    @staticmethod
    def encode(text, shift=3):
        result = ""
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result += chr((ord(ch)-base+shift)%26+base)
            else:
                result += ch
        return result
    
    @staticmethod
    def decode(text, shift=3):
        return CaesarCipher.encode(text, -shift)

class Base64Codec:
    @staticmethod
    def encode(text):
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def decode(encoded):
        try:
            return base64.b64decode(encoded.encode()).decode()
        except:
            return ""

class LZWCodec:
    @staticmethod
    def encode(text):
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}
        w = ""
        result = []
        for c in text:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size+=1
                w = c
        if w:
            result.append(dictionary[w])
        return result
    
    @staticmethod
    def decode(codes):
        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}
        w = chr(codes[0]) if codes else ""
        result = w
        for k in codes[1:]:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                entry = ""
            result += entry
            dictionary[dict_size] = w + entry[0]
            dict_size+=1
            w = entry
        return result
