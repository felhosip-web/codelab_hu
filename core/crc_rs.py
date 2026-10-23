# -*- coding: utf-8 -*-
"""
CRC és Reed-Solomon motor - hibafelismerés és javítás
"""

class CRCCalculator:
    @staticmethod
    def compute_crc(data_bits: str, generator: str) -> str:
        """CRC számítás polinomosztással"""
        # data + 0...0 (generator hossz-1 db nulla)
        data = data_bits + "0"*(len(generator)-1)
        # Osztás
        for i in range(len(data_bits)):
            if data[i] == '1':
                # XOR a generátorral
                for j in range(len(generator)):
                    data = data[:i+j] + ('0' if data[i+j]==generator[j] else '1') + data[i+j+1:]
        # Maradék az utolsó len(generator)-1 bit
        return data[-(len(generator)-1):]
    
    @staticmethod
    def compute_crc_steps(data_bits: str, generator: str):
        """Lépésenkénti CRC osztás vizuálhoz"""
        steps = []
        data = list(data_bits + "0"*(len(generator)-1))
        data_str = "".join(data)
        steps.append((data_str, -1, "Kezdés: adat + 0-k: " + data_str))
        
        for i in range(len(data_bits)):
            if data[i] == '1':
                old = "".join(data)
                for j in range(len(generator)):
                    if generator[j] == '1':
                        data[i+j] = '0' if data[i+j]=='1' else '1'
                new = "".join(data)
                steps.append((new, i, f"{i}. pozíció 1, XOR {generator}: {old[:i]}[{old[i:i+len(generator)]}]->{new[i:i+len(generator)]}]{old[i+len(generator):]}"))
            else:
                steps.append(("".join(data), i, f"{i}. pozíció 0, nincs XOR"))
        
        crc = "".join(data)[-(len(generator)-1):]
        return steps, crc
    
    @staticmethod
    def verify(data_bits: str, generator: str, crc: str) -> bool:
        full = data_bits + crc
        for i in range(len(data_bits)):
            if full[i] == '1':
                for j in range(len(generator)):
                    if generator[j] == '1':
                        full = full[:i+j] + ('0' if full[i+j]=='1' else '1') + full[i+j+1:]
        return all(b=='0' for b in full)

# Egyszerű Galois Field GF(2^3) vagy GF(2^4) kis példához
# Reed-Solomon egyszerűsített verzió: GF(7) vagy GF(11) prím mezővel, hogy érthető legyen

class SimpleRS:
    """Egyszerűsített Reed-Solomon GF(p) felett, p prím, hogy ne kelljen GF(2^m)"""
    def __init__(self, n=7, k=3, p=7):
        # n = kódszó hossz, k = adat hossz, n-k = paritás
        self.n = n
        self.k = k
        self.p = p  # prím mező
    
    def encode(self, data):
        # data: k hosszú lista GF(p)-ben
        # Egyszerű: polinom értékelés n pontban (Reed-Solomon mint evaluációs kód)
        # f(x) = data[0] + data[1]*x + ... + data[k-1]*x^(k-1)
        # kódszó: [f(0), f(1), ..., f(n-1)] mod p
        codeword = []
        for x in range(self.n):
            val = 0
            for i, coeff in enumerate(data):
                val = (val + coeff * pow(x, i, self.p)) % self.p
            codeword.append(val)
        return codeword
    
    def add_errors(self, codeword, error_positions):
        corrupted = codeword[:]
        for pos in error_positions:
            if 0 <= pos < len(corrupted):
                corrupted[pos] = (corrupted[pos] + 1) % self.p  # 1-et hozzáadunk hibaként
        return corrupted
    
    def decode(self, received):
        # Berlekamp-Massey helyett egyszerű: ha k pont jó, interpolálunk
        # Feltételezzük hogy n-k >= 2*hibaszám
        # Keressük meg mely k pont konzisztens
        # Egyszerűsített: próbáljuk ki minden k kombinációt (kis n esetén)
        from itertools import combinations
        for indices in combinations(range(self.n), self.k):
            # Interpolálás ezekből a pontokból
            # Lagrange interpoláció GF(p)-ben
            data = self._interpolate([received[i] for i in indices], list(indices))
            # Ellenőrizzük hány egyezik
            encoded = self.encode(data)
            errors = sum(1 for i in range(self.n) if encoded[i] != received[i])
            if errors <= (self.n - self.k)//2:
                return data, encoded, errors, indices
        return None, None, None, None
    
    def _interpolate(self, y_vals, x_vals):
        # Lagrange interpoláció 0..k-1 együtthatókhoz GF(p)-ben
        k = len(y_vals)
        coeffs = [0]*k
        
        # Egyszerű megoldás kis k-ra: megoldjuk lineáris rendszerként
        # Vandermonde mátrix
        # Gaussian elimination mod p
        # M * coeffs = y
        # M[i][j] = x_i^j
        
        # Build matrix
        M = [[pow(x_vals[i], j, self.p) for j in range(k)] for i in range(k)]
        y = y_vals[:]
        
        # Gaussian elimination mod p
        for col in range(k):
            # Find pivot
            pivot = None
            for row in range(col, k):
                if M[row][col] % self.p != 0:
                    pivot = row
                    break
            if pivot is None:
                continue
            M[col], M[pivot] = M[pivot], M[col]
            y[col], y[pivot] = y[pivot], y[col]
            
            # Normalize pivot row
            inv = pow(M[col][col], -1, self.p)
            for j in range(col, k):
                M[col][j] = (M[col][j]*inv) % self.p
            y[col] = (y[col]*inv) % self.p
            
            # Eliminate
            for row in range(k):
                if row != col and M[row][col] != 0:
                    factor = M[row][col]
                    for j in range(col, k):
                        M[row][j] = (M[row][j] - factor*M[col][j]) % self.p
                    y[row] = (y[row] - factor*y[col]) % self.p
        
        return y
