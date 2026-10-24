# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.enigma import EnigmaMachine, ALPHABET, ROTOR_WIRINGS

class EnigmaStep(VisualizationStep):
    def __init__(self, text="", encoded="", current_char=None, encoded_char=None,
                 rotor_positions=None, path=None, plugboard=None,
                 code_line=0, explanation="", comparisons=0, extra=None):
        e_dict = extra.copy() if extra else {}
        if text and "text" not in e_dict:
            e_dict["text"] = text
        if encoded and "encoded" not in e_dict:
            e_dict["encoded"] = encoded
        if current_char is not None and "current_char" not in e_dict:
            e_dict["current_char"] = current_char
        if encoded_char is not None and "encoded_char" not in e_dict:
            e_dict["encoded_char"] = encoded_char
        if rotor_positions is not None:
            e_dict["rotor_positions"] = rotor_positions
        elif "rotor_positions" not in e_dict:
            e_dict["rotor_positions"] = []
        if path is not None:
            e_dict["path"] = path
        elif "path" not in e_dict:
            e_dict["path"] = []
        if plugboard is not None:
            e_dict["plugboard"] = plugboard
        elif "plugboard" not in e_dict:
            e_dict["plugboard"] = None

        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            extra=e_dict
        )

class EnigmaPlugin(AlgorithmPluginBase):
    id = "enigma"
    name = "Enigma gép"
    description = "II. vh. német rejtjelező: 3 rotor, plugboard, reflector, lépés"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    icon = "⚙️🔐"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "encoding"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("text", "Szöveg", "string", "HELLO WORLD", description="Nagybetűs, A-Z"))
        self.params.add(Param("rotor1", "Rotor 1 (bal)", "choice", "I", choices=["I","II","III","IV","V"], description="Bal rotor"))
        self.params.add(Param("rotor2", "Rotor 2 (közép)", "choice", "II", choices=["I","II","III","IV","V"]))
        self.params.add(Param("rotor3", "Rotor 3 (jobb)", "choice", "III", choices=["I","II","III","IV","V"]))
        self.params.add(Param("pos1", "Pozíció 1", "choice", "A", choices=list(ALPHABET), description="Kezdő pozíció bal"))
        self.params.add(Param("pos2", "Pozíció 2", "choice", "A", choices=list(ALPHABET)))
        self.params.add(Param("pos3", "Pozíció 3", "choice", "A", choices=list(ALPHABET)))
        self.params.add(Param("plugboard", "Plugboard", "string", "AB CD EF", description="Párok: AB CD = A<->B, C<->D"))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Enigma M3 - 3 rotor, reflector B
ALPHABET="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ROTOR_WIRINGS={
    "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
}
REFLECTOR_B="YRUHQSLDPXNGOKMIEBFZCWVJAT"

class Rotor:
    def __init__(self, wiring_name, position=0):
        wiring, notch = ROTOR_WIRINGS[wiring_name]
        self.wiring=wiring
        self.notch=notch
        self.position=position
        self.wiring_list=[ALPHABET.index(c) for c in wiring]
        self.inverse=[0]*26
        for i,w in enumerate(self.wiring_list):
            self.inverse[w]=i
    
    def forward(self, c):
        shifted=(c+self.position)%26
        wired=self.wiring_list[shifted]
        return (wired-self.position)%26
    
    def backward(self, c):
        shifted=(c+self.position)%26
        wired=self.inverse[shifted]
        return (wired-self.position)%26
    
    def should_step_next(self):
        return ALPHABET[self.position]==self.notch
    
    def step(self):
        self.position=(self.position+1)%26

class Enigma:
    def __init__(self, rotor_names, positions, plug_pairs=None):
        self.rotors=[Rotor(rotor_names[i], positions[i]) for i in range(3)]
        self.reflector=[ALPHABET.index(c) for c in REFLECTOR_B]
        self.plugboard=list(range(26))
        if plug_pairs:
            for a,b in plug_pairs:
                ai=ALPHABET.index(a); bi=ALPHABET.index(b)
                self.plugboard[ai]=bi; self.plugboard[bi]=ai
    
    def step_rotors(self):
        # Jobb mindig lép, középső ha jobb notch-on, bal ha középső notch-on (dupla lépés!)
        right_next=self.rotors[2].should_step_next()
        middle_next=self.rotors[1].should_step_next()
        self.rotors[2].step()
        if right_next or middle_next:
            self.rotors[1].step()
        if middle_next:
            self.rotors[0].step()
    
    def encode_char(self, ch):
        if not ch.isalpha(): return ch
        self.step_rotors()
        c=ALPHABET.index(ch.upper())
        c=self.plugboard[c]
        for i in [2,1,0]: c=self.rotors[i].forward(c)
        c=self.reflector[c]
        for i in [0,1,2]: c=self.rotors[i].backward(c)
        c=self.plugboard[c]
        return ALPHABET[c]

# Példa:
# enigma=Enigma(["I","II","III"], [0,0,0], [("A","B")])
# enigma.encode("HELLO") -> "ILBDA"
# Ugyanazzal a beállítással dekódolható (szimmetrikus)!
""",
        "C++": "// Enigma C++ - 3 rotor\nconst string ALPH=\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\";\nmap<string, pair<string,char>> ROTOR={{\"I\",{\"EKMFLGDQVZNTOWYHXUSPAIBRCJ\",'Q'}}, {\"II\",{\"AJDKSIRUXBLHWTMCQGZNPYFVOE\",'E'}}, {\"III\",{\"BDFHJLCPRTXVZNYEIWGAKMUSQO\",'V'}}};\nclass Rotor{string wiring; char notch; int pos; vector<int> w, inv; public: Rotor(string name,int p): pos(p){ wiring=ROTOR[name].first; notch=ROTOR[name].second; w.resize(26); inv.resize(26); for(int i=0;i<26;i++){ w[i]=ALPH.find(wiring[i]); inv[w[i]]=i; }} int forward(int c){ int s=(c+pos)%26; int wired=w[s]; return (wired-pos+26)%26; } int backward(int c){ int s=(c+pos)%26; int wired=inv[s]; return (wired-pos+26)%26; } bool shouldStep(){return ALPH[pos]==notch;} void step(){pos=(pos+1)%26;} };\nclass Enigma{vector<Rotor> rotors; vector<int> reflector, plug; public: Enigma(vector<string> names, vector<int> positions){ for(int i=0;i<3;i++) rotors.emplace_back(names[i], positions[i]); string ref=\"YRUHQSLDPXNGOKMIEBFZCWVJAT\"; for(char c: ref) reflector.push_back(ALPH.find(c)); plug.resize(26); for(int i=0;i<26;i++) plug[i]=i; } void stepRotors(){ bool rNext=rotors[2].shouldStep(), mNext=rotors[1].shouldStep(); rotors[2].step(); if(rNext||mNext) rotors[1].step(); if(mNext) rotors[0].step(); } char encodeChar(char ch){ if(!isalpha(ch)) return ch; stepRotors(); int c=ALPH.find(toupper(ch)); c=plug[c]; for(int i=2;i>=0;i--) c=rotors[i].forward(c); c=reflector[c]; for(int i=0;i<3;i++) c=rotors[i].backward(c); c=plug[c]; return ALPH[c]; } };",
        "C": "/* Enigma C */\n#define ALPH \"ABCDEFGHIJKLMNOPQRSTUVWXYZ\"\nstruct Rotor{char wiring[27]; char notch; int pos; int w[26], inv[26];};\nvoid rotorInit(struct Rotor* r, char* wiring, char notch, int pos){strcpy(r->wiring,wiring); r->notch=notch; r->pos=pos; for(int i=0;i<26;i++){r->w[i]=strchr(ALPH,wiring[i])-ALPH; r->inv[r->w[i]]=i;}}\nint rotorForward(struct Rotor* r, int c){int s=(c+r->pos)%26; int wired=r->w[s]; return (wired-r->pos+26)%26;}\nint rotorBackward(struct Rotor* r, int c){int s=(c+r->pos)%26; int wired=r->inv[s]; return (wired-r->pos+26)%26;}\nvoid enigmaStep(struct Rotor rotors[3]){int rNext=(ALPH[rotors[2].pos]==rotors[2].notch), mNext=(ALPH[rotors[1].pos]==rotors[1].notch); rotors[2].pos=(rotors[2].pos+1)%26; if(rNext||mNext) rotors[1].pos=(rotors[1].pos+1)%26; if(mNext) rotors[0].pos=(rotors[0].pos+1)%26;}",
        "BASIC": "TYPE Rotor: wiring AS STRING: notch AS STRING: pos AS INTEGER: w(25) AS INTEGER: inv(25) AS INTEGER: END TYPE\nSUB RotorInit(r AS Rotor PTR, wiring AS STRING, notch AS STRING, pos AS INTEGER): r->wiring=wiring: r->notch=notch: r->pos=pos: FOR i=0 TO 25: r->w(i)=INSTR(\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\", MID$(wiring,i+1,1))-1: r->inv(r->w(i))=i: NEXT: END SUB\nFUNCTION RotorForward(r AS Rotor PTR, c AS INTEGER) AS INTEGER: s=(c+r->pos) MOD 26: wired=r->w(s): RETURN (wired-r->pos+26) MOD 26: END FUNCTION\nFUNCTION RotorBackward(r AS Rotor PTR, c AS INTEGER) AS INTEGER: s=(c+r->pos) MOD 26: wired=r->inv(s): RETURN (wired-r->pos+26) MOD 26: END FUNCTION\nSUB EnigmaStep(rotors() AS Rotor): rNext=(MID$(\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\",rotors(2).pos+1,1)=rotors(2).notch): mNext=(MID$(\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\",rotors(1).pos+1,1)=rotors(1).notch): rotors(2).pos=(rotors(2).pos+1) MOD 26: IF rNext OR mNext THEN rotors(1).pos=(rotors(1).pos+1) MOD 26: IF mNext THEN rotors(0).pos=(rotors(0).pos+1) MOD 26: END SUB",
        "Java": "class Rotor{String wiring; char notch; int pos; int[] w=new int[26], inv=new int[26]; Rotor(String name,int p){ Map<String, Pair<String,Character>> map=new HashMap<>(); map.put(\"I\", new Pair<>(\"EKMFLGDQVZNTOWYHXUSPAIBRCJ\",'Q')); wiring=map.get(name).getKey(); notch=map.get(name).getValue(); pos=p; for(int i=0;i<26;i++){ w[i]=\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\".indexOf(wiring.charAt(i)); inv[w[i]]=i; }} int forward(int c){ int s=(c+pos)%26; int wired=w[s]; return (wired-pos+26)%26; } int backward(int c){ int s=(c+pos)%26; int wired=inv[s]; return (wired-pos+26)%26; } boolean shouldStep(){return \"ABCDEFGHIJKLMNOPQRSTUVWXYZ\".charAt(pos)==notch;} void step(){pos=(pos+1)%26;}} class Enigma{List<Rotor> rotors=new ArrayList<>(); int[] reflector, plug=new int[26]; Enigma(List<String> names, List<Integer> positions){ for(int i=0;i<3;i++) rotors.add(new Rotor(names.get(i), positions.get(i))); String ref=\"YRUHQSLDPXNGOKMIEBFZCWVJAT\"; reflector=new int[26]; for(int i=0;i<26;i++) reflector[i]=\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\".indexOf(ref.charAt(i)); for(int i=0;i<26;i++) plug[i]=i; } void stepRotors(){ boolean rNext=rotors.get(2).shouldStep(), mNext=rotors.get(1).shouldStep(); rotors.get(2).step(); if(rNext||mNext) rotors.get(1).step(); if(mNext) rotors.get(0).step(); } char encodeChar(char ch){ if(!Character.isLetter(ch)) return ch; stepRotors(); int c=\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\".indexOf(Character.toUpperCase(ch)); c=plug[c]; for(int i=2;i>=0;i--) c=rotors.get(i).forward(c); c=reflector[c]; for(int i=0;i<3;i++) c=rotors.get(i).backward(c); c=plug[c]; return \"ABCDEFGHIJKLMNOPQRSTUVWXYZ\".charAt(c); }}",
        "Pascal": "type Rotor=record wiring: string; notch: Char; pos: Integer; w, inv: array[0..25] of Integer; end; procedure RotorInit(var r: Rotor; wiring: string; notch: Char; pos: Integer); var i: Integer; begin r.wiring:=wiring; r.notch:=notch; r.pos:=pos; for i:=0 to 25 do begin r.w[i]:=Pos(wiring[i+1], 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')-1; r.inv[r.w[i]]:=i; end; end; function RotorForward(var r: Rotor; c: Integer): Integer; var s,wired: Integer; begin s:=(c+r.pos) mod 26; wired:=r.w[s]; Result:=(wired-r.pos+26) mod 26; end; function RotorBackward(var r: Rotor; c: Integer): Integer; var s,wired: Integer; begin s:=(c+r.pos) mod 26; wired:=r.inv[s]; Result:=(wired-r.pos+26) mod 26; end; procedure EnigmaStep(var rotors: array of Rotor); var rNext,mNext: Boolean; begin rNext:=('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[rotors[2].pos+1]=rotors[2].notch); mNext:=('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[rotors[1].pos+1]=rotors[1].notch); rotors[2].pos:=(rotors[2].pos+1) mod 26; if rNext or mNext then rotors[1].pos:=(rotors[1].pos+1) mod 26; if mNext then rotors[0].pos:=(rotors[0].pos+1) mod 26; end;"
    }
    
    def get_steps(self, arr):
        text = self.params.get("text").upper()
        rotor_names = [self.params.get("rotor1"), self.params.get("rotor2"), self.params.get("rotor3")]
        pos_letters = [self.params.get("pos1"), self.params.get("pos2"), self.params.get("pos3")]
        positions = [ALPHABET.index(p) if p in ALPHABET else 0 for p in pos_letters]
        plug_str = self.params.get("plugboard")
        # Plugboard parsing: "AB CD" -> [("A","B"), ("C","D")]
        plug_pairs = []
        for token in plug_str.split():
            if len(token)==2 and token[0].isalpha() and token[1].isalpha():
                plug_pairs.append((token[0].upper(), token[1].upper()))
        
        enigma = EnigmaMachine(rotor_names, positions, [0,0,0], plug_pairs, "B")
        
        yield EnigmaStep(text=text, code_line=1,
                         explanation=f"⚙️🔐 Enigma indul: rotorok {rotor_names} pozíciók {pos_letters} plugboard {plug_pairs}",
                         comparisons=0, extra={"text": text, "rotors": rotor_names, "positions": pos_letters, "plugboard": plug_pairs, "phase": "init"})
        
        # Plugboard vizualizálás
        yield EnigmaStep(text=text, code_line=15,
                         explanation=f"Plugboard: {plug_pairs} - cserék: {' '.join([f'{a}<->{b}' for a,b in plug_pairs]) if plug_pairs else 'nincs'}",
                         comparisons=0, extra={"text": text, "plugboard": plug_pairs, "phase": "plugboard"})
        
        # Rotorok wiring mutatása
        for i, rotor in enumerate(enigma.rotors):
            yield EnigmaStep(text=text, rotor_positions=[r.get_window_letter() for r in enigma.rotors], code_line=5,
                             explanation=f"Rotor {i+1} {rotor.name}: {rotor.wiring[:10]}... notch {rotor.notch} pozíció {rotor.get_window_letter()}",
                             comparisons=0, extra={"text": text, "rotor": rotor.name, "wiring": rotor.wiring, "notch": rotor.notch, "pos": rotor.get_window_letter(), "phase": f"rotor{i+1}"})
        
        encoded = ""
        for idx, ch in enumerate(text):
            if not ch.isalpha():
                encoded+=ch
                yield EnigmaStep(text=text, encoded=encoded, current_char=ch, encoded_char=ch,
                                 rotor_positions=[r.get_window_letter() for r in enigma.rotors],
                                 code_line=30, explanation=f"Nem betű: '{ch}' marad",
                                 comparisons=idx+1, extra={"text": text, "char": ch, "encoded": encoded, "phase": "skip"})
                continue
            
            # Kódolás előtti pozíciók
            old_positions = [r.get_window_letter() for r in enigma.rotors]
            
            enc_char, path = enigma.encode_char(ch)
            encoded+=enc_char
            new_positions = [r.get_window_letter() for r in enigma.rotors]
            
            # Lépésenkénti path vizualizálás
            for step_idx, p in enumerate(path):
                yield EnigmaStep(text=text, encoded=encoded, current_char=ch, encoded_char=enc_char if step_idx==len(path)-1 else None,
                                 rotor_positions=new_positions, path=path[:step_idx+1],
                                 code_line=35+step_idx, explanation=f"{ch} -> ... {p} | Rotorok: {old_positions} -> {new_positions}",
                                 comparisons=idx+1, extra={"text": text, "char": ch, "enc_char": enc_char, "path": path[:step_idx+1], "positions": new_positions, "old_positions": old_positions, "phase": "kódol", "step": step_idx})
            
            yield EnigmaStep(text=text, encoded=encoded, current_char=ch, encoded_char=enc_char,
                             rotor_positions=new_positions, path=path,
                             code_line=45, explanation=f"✅ '{ch}' -> '{enc_char}' | Rotorok most: {new_positions} | Eddig: {encoded}",
                             comparisons=idx+1, extra={"text": text, "char": ch, "enc_char": enc_char, "encoded": encoded, "positions": new_positions, "path": path, "phase": "kész"})
        
        # Dekódolás demonstrálása (szimmetrikus!)
        # Visszaállítjuk az Enigmát eredeti pozícióba és dekódoljuk
        enigma2 = EnigmaMachine(rotor_names, positions, [0,0,0], plug_pairs, "B")
        decoded, _ = enigma2.encode_text(encoded)
        
        yield EnigmaStep(text=text, encoded=encoded, current_char=None, encoded_char=None,
                         rotor_positions=[r.get_window_letter() for r in enigma.rotors],
                         code_line=60, explanation=f"🔓 Enigma szimmetrikus! Dekódolás ugyanazzal a beállítással: '{encoded}' -> '{decoded}'",
                         comparisons=len(text), extra={"text": text, "encoded": encoded, "decoded": decoded, "phase": "dekódol", "symmetric": True})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
