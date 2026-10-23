# -*- coding: utf-8 -*-
"""
Enigma gép - M3 modell, 3 rotor, reflector B, plugboard
"""
from typing import List, Dict

# Történelmi rotorok wiring-je
ROTOR_WIRINGS = {
    "I":   ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),  # notch Q
    "II":  ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV":  ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V":   ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
}

REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
REFLECTOR_C = "FVPJIAOYEDRZXWGCTKUQSBNMHL"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Rotor:
    def __init__(self, wiring_name="I", position=0, ring_setting=0):
        wiring, notch = ROTOR_WIRINGS.get(wiring_name, ROTOR_WIRINGS["I"])
        self.name = wiring_name
        self.wiring = wiring
        self.notch = notch
        self.position = position  # 0-25
        self.ring_setting = ring_setting
        self.wiring_list = [ALPHABET.index(c) for c in wiring]
        self.inverse_wiring = [0]*26
        for i, w in enumerate(self.wiring_list):
            self.inverse_wiring[w] = i
    
    def forward(self, c: int) -> int:
        # Bemegy jobbról balra
        shifted = (c + self.position - self.ring_setting) % 26
        wired = self.wiring_list[shifted]
        return (wired - self.position + self.ring_setting) % 26
    
    def backward(self, c: int) -> int:
        shifted = (c + self.position - self.ring_setting) % 26
        wired = self.inverse_wiring[shifted]
        return (wired - self.position + self.ring_setting) % 26
    
    def should_step_next(self):
        return ALPHABET[self.position] == self.notch
    
    def step(self):
        self.position = (self.position + 1) % 26
    
    def get_window_letter(self):
        return ALPHABET[self.position]

class EnigmaMachine:
    def __init__(self, rotor_names=None, positions=None, ring_settings=None, plugboard_pairs=None, reflector="B"):
        rotor_names = rotor_names or ["I", "II", "III"]
        positions = positions or [0,0,0]
        ring_settings = ring_settings or [0,0,0]
        
        self.rotors = []
        for i in range(3):
            name = rotor_names[i] if i < len(rotor_names) else "I"
            pos = positions[i] if i < len(positions) else 0
            ring = ring_settings[i] if i < len(ring_settings) else 0
            self.rotors.append(Rotor(name, pos, ring))
        
        self.reflector = REFLECTOR_B if reflector=="B" else REFLECTOR_C
        self.reflector_list = [ALPHABET.index(c) for c in self.reflector]
        
        # Plugboard
        self.plugboard = list(range(26))
        if plugboard_pairs:
            for pair in plugboard_pairs:
                if len(pair)==2:
                    a = ALPHABET.index(pair[0].upper())
                    b = ALPHABET.index(pair[1].upper())
                    self.plugboard[a] = b
                    self.plugboard[b] = a
    
    def _step_rotors(self):
        # Jobb rotor mindig lép
        # Középső lép ha jobb notch-on van, vagy bal notch miatt dupla lépés
        # Double stepping: ha középső notch-on van, bal is lép
        
        # Check notches before stepping
        right_should_step_middle = self.rotors[2].should_step_next()
        middle_should_step_left = self.rotors[1].should_step_next()
        
        # Right always steps
        self.rotors[2].step()
        
        if right_should_step_middle or middle_should_step_left:
            self.rotors[1].step()
        
        if middle_should_step_left:
            self.rotors[0].step()
    
    def encode_char(self, ch: str, with_step=True) -> tuple:
        # Returns (encoded_char, path)
        if not ch.isalpha():
            return (ch, [])
        
        if with_step:
            self._step_rotors()
        
        c = ALPHABET.index(ch.upper())
        path = [f"Input {ch}({c})"]
        
        # Plugboard in
        c = self.plugboard[c]
        path.append(f"Plugboard in -> {ALPHABET[c]}({c})")
        
        # Rotorok jobbról balra (2->1->0)
        for i in [2,1,0]:
            c_old = c
            c = self.rotors[i].forward(c)
            path.append(f"Rotor {self.rotors[i].name} [{self.rotors[i].get_window_letter()}] {ALPHABET[c_old]}->{ALPHABET[c]}")
        
        # Reflector
        c_old = c
        c = self.reflector_list[c]
        path.append(f"Reflector B {ALPHABET[c_old]}->{ALPHABET[c]}")
        
        # Rotorok balról jobbra (0->1->2)
        for i in [0,1,2]:
            c_old = c
            c = self.rotors[i].backward(c)
            path.append(f"Rotor {self.rotors[i].name} vissza {ALPHABET[c_old]}->{ALPHABET[c]}")
        
        # Plugboard out
        c_old = c
        c = self.plugboard[c]
        path.append(f"Plugboard out {ALPHABET[c_old]}->{ALPHABET[c]}")
        
        encoded_char = ALPHABET[c]
        return (encoded_char, path)
    
    def encode_text(self, text: str):
        result = ""
        paths = []
        for ch in text:
            enc, path = self.encode_char(ch)
            result+=enc
            paths.append((ch, enc, path, [r.get_window_letter() for r in self.rotors]))
        return result, paths
    
    def get_rotor_positions(self):
        return "".join([r.get_window_letter() for r in self.rotors])
