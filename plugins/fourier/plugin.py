# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.fourier import Fourier
import math

class FourierStep(VisualizationStep):
    def __init__(self, signal=None, spectrum=None, magnitude=None, phase=None, frequencies=None,
                 current_k=None, current_n=None, signal_type="",
                 code_line=0, explanation="", comparisons=0, extra=None):
        sig = signal or []
        e_dict = extra.copy() if extra else {}
        e_dict.update({
            "signal": sig, "spectrum": spectrum or [], "magnitude": magnitude or [],
            "phase": phase or [], "frequencies": frequencies or [],
            "current_k": current_k, "current_n": current_n, "signal_type": signal_type
        })
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=sig,
            extra=e_dict
        )

class DFTPlugin(AlgorithmPluginBase):
    id = "dft"
    name = "DFT - Diszkrét Fourier"
    description = "Idő -> frekvencia, O(n^2), alap képlet"
    time_complexity = "O(n^2)"
    space_complexity = "O(n)"
    icon = "🌊"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core - HES Projects® by FePe®"
    plugin_type = "fourier"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("N", "Minták száma", "int", 8, 4, 16))
        self.params.add(Param("signal_type", "Jel típus", "choice", "sine", choices=["sine", "cosine", "square", "two_sine", "impulse", "random"]))
        self.params.add(Param("freq", "Frekvencia", "int", 1, 1, 3))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# DFT - Diszkrét Fourier-transzformáció
# Időtartomány -> frekvenciatartomány
# X[k] = sum_{n=0}^{N-1} x[n] * e^{-j2πkn/N}

import cmath

def dft(signal):
    N = len(signal)
    spectrum = []
    for k in range(N):  # Minden frekvencia
        sum_val = 0j
        for n in range(N):  # Minden minta
            angle = -2j * cmath.pi * k * n / N
            sum_val += signal[n] * cmath.exp(angle)
        spectrum.append(sum_val)
    return spectrum

# Példa: 8 minta sine hullám 1Hz
signal = [sin(2π*1*n/8) for n in range(8)]
# DFT -> spektrum: melyik frekvencia mennyire van jelen
# Magnitúdó: |X[k]| - erősség
# Fázis: arg(X[k]) - eltolás

# Használat: hang, kép, MP3, JPEG, MRI, 5G
# Mindenhol ahol időből frekvenciába kell!
""",
        "C++": "// DFT C++\n#include <complex>\n#include <vector>\nusing namespace std;\nvector<complex<double>> dft(const vector<double>& x){\n int N=x.size(); vector<complex<double>> X(N);\n for(int k=0;k<N;k++){ complex<double> sum=0;\n  for(int n=0;n<N;n++){ double angle=-2*M_PI*k*n/N;\n   sum+=x[n]*complex<double>(cos(angle), sin(angle)); }\n  X[k]=sum; } return X; }\n// O(n^2)\n// Magnitúdó: abs(X[k]), Fázis: arg(X[k])",
        "C": "/* DFT C */\n#include <complex.h>\nvoid dft(double* x, complex double* X, int N){\n for(int k=0;k<N;k++){ complex double sum=0;\n  for(int n=0;n<N;n++){ double angle=-2*M_PI*k*n/N;\n   sum+=x[n]*cexp(I*angle); }\n  X[k]=sum; } }\n// Magnitúdó: cabs(X[k])\n// Használat: jelfeldolgozás mindenhol",
        "BASIC": "FUNCTION dft(signal() AS DOUBLE) AS COMPLEX: N=UBOUND(signal): FOR k=0 TO N-1: sum=0: FOR n=0 TO N-1: angle=-2*PI*k*n/N: sum=sum+signal(n)*EXP(COMPLEX(0,angle)): NEXT: X(k)=sum: NEXT: RETURN X: END FUNCTION\n' DFT: ido -> frekvencia",
        "Java": "// DFT Java\nclass DFT{ static Complex[] dft(double[] x){ int N=x.length; Complex[] X=new Complex[N]; for(int k=0;k<N;k++){ Complex sum=new Complex(0,0); for(int n=0;n<N;n++){ double angle=-2*Math.PI*k*n/N; sum=sum.add(new Complex(x[n]*Math.cos(angle), x[n]*Math.sin(angle))); } X[k]=sum; } return X; } }\n// O(n^2)",
        "Pascal": "type Complex = record re,im: Double; end; function dft(x: array of Double): array of Complex; var N,k,n: Integer; angle: Double; sum: Complex; begin N:=Length(x); SetLength(Result,N); for k:=0 to N-1 do begin sum.re:=0; sum.im:=0; for n:=0 to N-1 do begin angle:=-2*Pi*k*n/N; sum.re:=sum.re+x[n]*Cos(angle); sum.im:=sum.im+x[n]*Sin(angle); end; Result[k]:=sum; end; end;"
    }
    
    def get_steps(self, arr):
        N = self.params.get("N")
        signal_type = self.params.get("signal_type")
        freq = self.params.get("freq")
        
        signal = Fourier.generate_signal(signal_type, N, freq, float(N))
        
        yield FourierStep(signal=signal, signal_type=signal_type, code_line=2,
                          explanation=f"🌊 DFT: {signal_type} jel, {N} minta, freq={freq} | Időtartomány",
                          comparisons=0, extra={"phase": "signal", "signal": signal, "type": signal_type, "N": N})
        
        # DFT lépésenként k szerint
        spectrum = []
        for k in range(N):
            sum_val = 0j
            for n in range(N):
                angle = -2j * math.pi * k * n / N
                sum_val += signal[n] * complex(math.cos(angle.imag), math.sin(angle.imag)) if isinstance(angle, complex) else signal[n] * complex(math.cos(-2*math.pi*k*n/N), math.sin(-2*math.pi*k*n/N))
                # Egyszerűsítve
                sum_val = 0j
                for nn in range(N):
                    ang = -2 * math.pi * k * nn / N
                    sum_val += signal[nn] * complex(math.cos(ang), math.sin(ang))
                break
            # Valódi DFT
            real_sum = 0j
            for n in range(N):
                ang = -2 * math.pi * k * n / N
                real_sum += signal[n] * complex(math.cos(ang), math.sin(ang))
            spectrum.append(real_sum)
            
            mag = Fourier.magnitude_spectrum(spectrum)
            phase = Fourier.phase_spectrum(spectrum)
            
            yield FourierStep(signal=signal, spectrum=spectrum, magnitude=mag, phase=phase, current_k=k, signal_type=signal_type, code_line=7,
                              explanation=f"DFT k={k}: X[{k}]={real_sum:.2f} | |X[{k}]|={abs(real_sum):.2f} | Spektrum eddig: {len(spectrum)}/{N}",
                              comparisons=k+1, extra={"phase": "dft_k", "k": k, "Xk": str(real_sum), "magnitude": mag, "spectrum": [str(s) for s in spectrum], "signal": signal, "N": N})
        
        mag = Fourier.magnitude_spectrum(spectrum)
        phase = Fourier.phase_spectrum(spectrum)
        freqs = Fourier.frequency_bins(N, float(N))
        
        # Domináns frekvencia
        max_idx = mag.index(max(mag[1:N//2])) if N>2 else 0
        
        yield FourierStep(signal=signal, spectrum=spectrum, magnitude=mag, phase=phase, frequencies=freqs, signal_type=signal_type, code_line=12,
                          explanation=f"✅ DFT kész: domináns frekvencia k={max_idx} | Magnitúdó max: {max(mag):.2f} | Idő O(n^2)={N*N}",
                          comparisons=N+1, extra={"phase": "done", "signal": signal, "spectrum": [str(s) for s in spectrum], "magnitude": mag, "phase": phase, "freqs": freqs, "dominant": max_idx, "N": N})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class FFTPlugin(AlgorithmPluginBase):
    id = "fft"
    name = "FFT - Gyors Fourier"
    description = "O(n log n), Cooley-Tukey, mindenhol használják"
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    icon = "⚡"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core - HES Projects® by FePe®"
    plugin_type = "fourier"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("N", "Minták (2 hatvány)", "int", 8, 4, 16))
        self.params.add(Param("signal_type", "Jel típus", "choice", "two_sine", choices=["sine", "cosine", "two_sine", "square", "impulse", "random"]))
        self.params.add(Param("freq", "Frekvencia", "int", 1, 1, 4))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# FFT - Fast Fourier Transform O(n log n)
# Cooley-Tukey, rekurzív, páros/páratlan szétválasztás
# Mindenhol használják: MP3, JPEG, 5G, MRI, hangfelismerés

import cmath

def fft(x):
    N = len(x)
    if N <= 1:
        return x
    # Páros/páratlan
    even = fft(x[0::2])
    odd = fft(x[1::2])
    T = [cmath.exp(-2j*cmath.pi*k/N)*odd[k] for k in range(N//2)]
    return [even[k]+T[k] for k in range(N//2)] + [even[k]-T[k] for k in range(N//2)]

# Példa: 8 minta, 2 frekvencia
signal = [sin(2π*1*n/8) + 0.5*sin(2π*3*n/8) for n in range(8)]
spectrum = fft(signal)
# -> spektrumban 2 csúcs: k=1 és k=3

# Sebesség: DFT O(n^2)=64 művelet, FFT O(n log n)=24 művelet 8 mintánál!
# 1024 mintánál: DFT 1M, FFT 10k -> 100x gyorsabb!
""",
        "C++": "// FFT C++ O(n log n)\nvector<complex<double>> fft(const vector<complex<double>>& x){\n int N=x.size(); if(N<=1) return x;\n vector<complex<double>> even(N/2), odd(N/2);\n for(int i=0;i<N/2;i++){ even[i]=x[2*i]; odd[i]=x[2*i+1]; }\n even=fft(even); odd=fft(odd);\n vector<complex<double>> X(N);\n for(int k=0;k<N/2;k++){ complex<double> t=exp(complex<double>(0,-2*M_PI*k/N))*odd[k];\n  X[k]=even[k]+t; X[k+N/2]=even[k]-t; } return X; }\n// Mindenhol: hang, kép, kommunikáció",
        "C": "/* FFT C */\nvoid fft(complex double* x, int N){ if(N<=1) return;\n complex double even[N/2], odd[N/2]; for(int i=0;i<N/2;i++){ even[i]=x[2*i]; odd[i]=x[2*i+1]; }\n fft(even,N/2); fft(odd,N/2);\n for(int k=0;k<N/2;k++){ complex double t=cexp(-2*I*M_PI*k/N)*odd[k];\n  x[k]=even[k]+t; x[k+N/2]=even[k]-t; } }\n// O(n log n) vs DFT O(n^2)",
        "BASIC": "FUNCTION fft(x() AS COMPLEX) AS COMPLEX: N=UBOUND(x)+1: IF N<=1 THEN RETURN x: DIM even(N/2), odd(N/2): FOR i=0 TO N/2-1: even(i)=x(2*i): odd(i)=x(2*i+1): NEXT: even=fft(even): odd=fft(odd): FOR k=0 TO N/2-1: t=EXP(COMPLEX(0,-2*PI*k/N))*odd(k): X(k)=even(k)+t: X(k+N/2)=even(k)-t: NEXT: RETURN X: END FUNCTION\n' Gyors, mindenhol",
        "Java": "// FFT Java\nclass FFT{ static Complex[] fft(Complex[] x){ int N=x.length; if(N<=1) return x; Complex[] even=new Complex[N/2]; Complex[] odd=new Complex[N/2]; for(int i=0;i<N/2;i++){ even[i]=x[2*i]; odd[i]=x[2*i+1]; } even=fft(even); odd=fft(odd); Complex[] X=new Complex[N]; for(int k=0;k<N/2;k++){ Complex t=new Complex(Math.cos(-2*Math.PI*k/N), Math.sin(-2*Math.PI*k/N)).mul(odd[k]); X[k]=even[k].add(t); X[k+N/2]=even[k].sub(t); } return X; } }",
        "Pascal": "function fft(x: array of Complex): array of Complex; var N,k: Integer; even,odd: array of Complex; t: Complex; begin N:=Length(x); if N<=1 then Exit(x); SetLength(even,N div 2); SetLength(odd,N div 2); for k:=0 to N div 2-1 do begin even[k]:=x[2*k]; odd[k]:=x[2*k+1]; end; even:=fft(even); odd:=fft(odd); SetLength(Result,N); for k:=0 to N div 2-1 do begin t.re:=Cos(-2*Pi*k/N)*odd[k].re - Sin(-2*Pi*k/N)*odd[k].im; t.im:=Sin(-2*Pi*k/N)*odd[k].re + Cos(-2*Pi*k/N)*odd[k].im; Result[k].re:=even[k].re+t.re; Result[k].im:=even[k].im+t.im; Result[k+N div 2].re:=even[k].re-t.re; Result[k+N div 2].im:=even[k].im-t.im; end; end;"
    }
    
    def get_steps(self, arr):
        N = self.params.get("N")
        # N legyen 2 hatvány
        # Legközelebbi 2 hatvány
        import math
        pow2 = 1
        while pow2 < N:
            pow2 *= 2
        if pow2 != N:
            N = pow2
            if N>16:
                N=16
        
        signal_type = self.params.get("signal_type")
        freq = self.params.get("freq")
        
        signal = Fourier.generate_signal(signal_type, N, freq, float(N))
        
        yield FourierStep(signal=signal, signal_type=signal_type, code_line=2,
                          explanation=f"⚡ FFT: {signal_type} {N} minta (2 hatvány!) | Idő: időtartomány",
                          comparisons=0, extra={"phase": "signal", "signal": signal, "N": N, "type": signal_type})
        
        # FFT rekurzív lépések szimulálása
        def fft_steps(x, depth=0):
            n = len(x)
            if n <= 1:
                return x
            even = x[0::2]
            odd = x[1::2]
            return (even, odd, depth)
        
        # Szintenként
        level = 0
        current = [signal]
        while len(current[0]) > 1:
            next_level = []
            for segment in current:
                if len(segment) > 1:
                    even = segment[0::2]
                    odd = segment[1::2]
                    next_level.append(even)
                    next_level.append(odd)
                    yield FourierStep(signal=signal, signal_type=signal_type, code_line=8,
                                      explanation=f"FFT szint {level}: {len(segment)} -> páros {even[:3]}... páratlan {odd[:3]}... | Szétválasztás",
                                      comparisons=level+1, extra={"phase": f"split_{level}", "segment": segment, "even": even, "odd": odd, "level": level, "N": N})
                else:
                    next_level.append(segment)
            current = next_level
            level += 1
        
        # Végső FFT
        spectrum = Fourier.fft(signal)
        mag = Fourier.magnitude_spectrum(spectrum)
        phase = Fourier.phase_spectrum(spectrum)
        freqs = Fourier.frequency_bins(N, float(N))
        
        # Összehasonlítás DFT vs FFT
        dft_ops = N*N
        fft_ops = int(N * math.log2(N)) if N>0 else 0
        
        yield FourierStep(signal=signal, spectrum=spectrum, magnitude=mag, phase=phase, frequencies=freqs, signal_type=signal_type, code_line=12,
                          explanation=f"✅ FFT kész: {N} minta | DFT O(n^2)={dft_ops} vs FFT O(n log n)={fft_ops} -> {dft_ops//max(fft_ops,1)}x gyorsabb! | Domináns frekvenciák a magnitúdó csúcsok",
                          comparisons=level+2, extra={"phase": "done", "signal": signal, "spectrum": [str(s) for s in spectrum], "magnitude": mag, "phase": phase, "freqs": freqs, "N": N, "dft_ops": dft_ops, "fft_ops": fft_ops, "speedup": dft_ops//max(fft_ops,1)})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
