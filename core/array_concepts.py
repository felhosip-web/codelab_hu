# -*- coding: utf-8 -*-
"""
Tömb kezelés motor - alapok, 2D, pointerek, tömbben tömb
"""

class ArrayConcepts:
    @staticmethod
    def create_array(size, max_val=20):
        import random
        return [random.randint(1, max_val) for _ in range(size)]
    
    @staticmethod
    def create_2d_array(rows, cols, max_val=20):
        import random
        return [[random.randint(1, max_val) for _ in range(cols)] for _ in range(rows)]
    
    @staticmethod
    def create_jagged_array():
        import random
        return [
            [random.randint(1, 20) for _ in range(random.randint(2, 5))],
            [random.randint(1, 20) for _ in range(random.randint(3, 6))],
            [random.randint(1, 20) for _ in range(random.randint(1, 4))],
        ]

class PointerSim:
    """Pointer szimuláció - memória címek, értékek, dereferálás"""
    def __init__(self):
        self.memory = {}  # cím -> érték
        self.next_addr = 1000
        self.variables = {}  # név -> cím
    
    def malloc(self, var_name, value):
        addr = self.next_addr
        self.next_addr += 4  # 4 byte
        self.memory[addr] = value
        self.variables[var_name] = addr
        return addr
    
    def get_address(self, var_name):
        return self.variables.get(var_name, None)
    
    def get_value(self, addr_or_var):
        if isinstance(addr_or_var, str):
            addr = self.variables.get(addr_or_var)
            if addr is not None:
                return self.memory.get(addr)
            return None
        else:
            return self.memory.get(addr_or_var)
    
    def set_value(self, var_name, value):
        addr = self.variables.get(var_name)
        if addr is not None:
            self.memory[addr] = value
    
    def pointer_to(self, pointer_name, target_var):
        # pointer_name -> target_var címére mutat
        target_addr = self.variables.get(target_var)
        if target_addr is not None:
            self.variables[pointer_name] = target_addr  # pointer értéke a cím
    
    def dereference(self, pointer_name):
        # *pointer
        addr = self.variables.get(pointer_name)
        if addr is not None:
            return self.memory.get(addr)
        return None
    
    def pointer_arithmetic(self, pointer_name, offset):
        # pointer + offset
        addr = self.variables.get(pointer_name)
        if addr is not None:
            return addr + offset*4
        return None
