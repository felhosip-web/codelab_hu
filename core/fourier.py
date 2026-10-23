# -*- coding: utf-8 -*-
"""
Fourier-transzformáció motor - DFT, FFT, spektrum, mindenhol használják
"""
import math
import cmath
from typing import List, Tuple

class Fourier:
    @staticmethod
    def dft(signal: List[float]) -> List[complex]:
        """Discrete Fourier Transform O(n^2)"""
        N = len(signal)
        result = []
        for k in range(N):
            sum_val = 0j
            for n in range(N):
                angle = -2j * cmath.pi * k * n / N
                sum_val += signal[n] * cmath.exp(angle)
            result.append(sum_val)
        return result
    
    @staticmethod
    def idft(spectrum: List[complex]) -> List[complex]:
        """Inverse DFT"""
        N = len(spectrum)
        result = []
        for n in range(N):
            sum_val = 0j
            for k in range(N):
                angle = 2j * cmath.pi * k * n / N
                sum_val += spectrum[k] * cmath.exp(angle)
            result.append(sum_val / N)
        return result
    
    @staticmethod
    def fft(signal: List[float]) -> List[complex]:
        """Fast Fourier Transform O(n log n) - Cooley-Tukey"""
        N = len(signal)
        if N <= 1:
            return [complex(x) for x in signal]
        
        # Páros hossz kell, ha nem, DFT
        if N % 2 != 0:
            return Fourier.dft(signal)
        
        even = Fourier.fft(signal[0::2])
        odd = Fourier.fft(signal[1::2])
        
        T = [cmath.exp(-2j * cmath.pi * k / N) * odd[k] for k in range(N//2)]
        return [even[k] + T[k] for k in range(N//2)] + [even[k] - T[k] for k in range(N//2)]
    
    @staticmethod
    def magnitude_spectrum(spectrum: List[complex]) -> List[float]:
        return [abs(c) for c in spectrum]
    
    @staticmethod
    def phase_spectrum(spectrum: List[complex]) -> List[float]:
        return [cmath.phase(c) for c in spectrum]
    
    @staticmethod
    def frequency_bins(N: int, sample_rate: float = 1.0) -> List[float]:
        return [k * sample_rate / N for k in range(N)]
    
    @staticmethod
    def generate_signal(signal_type: str, N: int = 16, freq: float = 1.0, sample_rate: float = 16.0) -> List[float]:
        """Teszt jelek generálása"""
        import random
        if signal_type == "sine":
            return [math.sin(2*math.pi*freq*i/sample_rate) for i in range(N)]
        elif signal_type == "cosine":
            return [math.cos(2*math.pi*freq*i/sample_rate) for i in range(N)]
        elif signal_type == "square":
            return [1.0 if math.sin(2*math.pi*freq*i/sample_rate) >= 0 else -1.0 for i in range(N)]
        elif signal_type == "sawtooth":
            return [(i % int(sample_rate/freq)) / (sample_rate/freq) * 2 - 1 for i in range(N)]
        elif signal_type == "impulse":
            sig = [0.0]*N
            sig[0] = 1.0
            return sig
        elif signal_type == "random":
            return [random.uniform(-1, 1) for _ in range(N)]
        elif signal_type == "two_sine":
            return [math.sin(2*math.pi*1*i/sample_rate) + 0.5*math.sin(2*math.pi*3*i/sample_rate) for i in range(N)]
        else:
            return [math.sin(2*math.pi*freq*i/sample_rate) for i in range(N)]
