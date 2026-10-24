# -*- coding: utf-8 -*-
from typing import List
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep


class BinaryAddPlugin(AlgorithmPluginBase):
    id = "binary_add"
    name = "Bináris összeadás (8 bit)"
    description = "Két 8 bites nem-negatív egész szám bináris összeadása LSB-től MSB-ig átvitellel (carry)."
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "➕"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("a", "A érték (0-255)", "int", 13, 0, 255))
        self.params.add(Param("b", "B érték (0-255)", "int", 7, 0, 255))

    def get_params(self):
        return self.params

    def set_param(self, pid, val):
        self.params.set(pid, val)

    codes = {
        "Python": """def binary_add(a: int, b: int) -> int:
    a &= 0xFF
    b &= 0xFF
    result = 0
    carry = 0
    for i in range(8):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        total = bit_a + bit_b + carry
        sum_bit = total % 2
        carry = total // 2
        result |= (sum_bit << i)
    return result
""",
        "C++": """#include <cstdint>

uint8_t binary_add(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t carry = 0;
    for (int i = 0; i < 8; ++i) {
        uint8_t bit_a = (a >> i) & 1;
        uint8_t bit_b = (b >> i) & 1;
        uint8_t total = bit_a + bit_b + carry;
        uint8_t sum_bit = total % 2;
        carry = total / 2;
        result |= (sum_bit << i);
    }
    return result;
}
""",
        "C": """#include <stdint.h>

uint8_t binary_add(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t carry = 0;
    for (int i = 0; i < 8; ++i) {
        uint8_t bit_a = (a >> i) & 1;
        uint8_t bit_b = (b >> i) & 1;
        uint8_t total = bit_a + bit_b + carry;
        uint8_t sum_bit = total % 2;
        carry = total / 2;
        result |= (sum_bit << i);
    }
    return result;
}
""",
        "Java": """public class BinaryArith {
    public static int binaryAdd(int a, int b) {
        a &= 0xFF;
        b &= 0xFF;
        int result = 0;
        int carry = 0;
        for (int i = 0; i < 8; i++) {
            int bitA = (a >> i) & 1;
            int bitB = (b >> i) & 1;
            int total = bitA + bitB + carry;
            int sumBit = total % 2;
            carry = total / 2;
            result |= (sumBit << i);
        }
        return result & 0xFF;
    }
}
""",
    }

    def get_code(self, lang: str) -> str:
        return self.codes.get(lang, self.codes["Python"])

    def get_steps(self, arr=None) -> List[VisualizationStep]:
        if isinstance(arr, (list, tuple)) and len(arr) >= 2:
            a = int(arr[0]) & 0xFF
            b = int(arr[1]) & 0xFF
        else:
            a = int(self.params.get("a")) & 0xFF
            b = int(self.params.get("b")) & 0xFF

        a_bits = f"{a:08b}"
        b_bits = f"{b:08b}"
        result = 0
        carry = 0

        # Step 0: Előkészítés
        yield VisualizationStep(
            explanation=f"Kezdés: a = {a} (0b{a_bits}), b = {b} (0b{b_bits}). 8 bites összeadás LSB-től (jobbról) MSB-ig.",
            code_line=1,
            metrics={"bit": -1, "carry": 0},
            array=[a, b],
            highlight=[],
            extra={
                "a": a,
                "b": b,
                "result": 0,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": "00000000",
                "bit_index": -1,
                "carry": 0,
                "op": "add",
            },
        )

        for i in range(8):
            bit_a = (a >> i) & 1
            bit_b = (b >> i) & 1
            total = bit_a + bit_b + carry
            sum_bit = total % 2
            next_carry = total // 2

            result |= (sum_bit << i)
            res_bits = f"{result & 0xFF:08b}"

            yield VisualizationStep(
                explanation=f"{i}. bit (2^{i}={1<<i}): a={bit_a}, b={bit_b}, bejövő átvitel={carry} -> összeg bit={sum_bit}, új átvitel={next_carry}.",
                code_line=10,
                metrics={"bit": i, "carry": carry},
                array=[a, b, result & 0xFF],
                highlight=[2],
                extra={
                    "a": a,
                    "b": b,
                    "result": result & 0xFF,
                    "a_bits": a_bits,
                    "b_bits": b_bits,
                    "result_bits": res_bits,
                    "bit_index": i,
                    "carry": next_carry,
                    "op": "add",
                },
            )

            carry = next_carry

        final_res = result & 0xFF
        overflow_msg = " (Túlcsordulás! 9. bit átvitel = 1)" if carry else " (Nincs túlcsordulás)."
        yield VisualizationStep(
            explanation=f"Összeadás kész: {a} + {b} = {final_res} (0b{final_res:08b}){overflow_msg}",
            code_line=14,
            metrics={"bit": 8, "carry": carry},
            array=[a, b, final_res],
            highlight=[2],
            extra={
                "a": a,
                "b": b,
                "result": final_res,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": f"{final_res:08b}",
                "bit_index": 7,
                "carry": carry,
                "op": "add",
            },
        )


class BinarySubPlugin(AlgorithmPluginBase):
    id = "binary_sub"
    name = "Bináris kivonás (8 bit)"
    description = "Két 8 bites nem-negatív egész szám bináris kivonása (a - b) kölcsönkérés (borrow) modell alkalmazásával."
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "➖"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("a", "A érték (0-255)", "int", 13, 0, 255))
        self.params.add(Param("b", "B érték (0-255)", "int", 7, 0, 255))

    def get_params(self):
        return self.params

    def set_param(self, pid, val):
        self.params.set(pid, val)

    codes = {
        "Python": """def binary_sub(a: int, b: int) -> int:
    a &= 0xFF
    b &= 0xFF
    result = 0
    borrow = 0
    for i in range(8):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        diff = bit_a - bit_b - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        result |= (diff << i)
    return result & 0xFF
""",
        "C++": """#include <cstdint>

uint8_t binary_sub(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t borrow = 0;
    for (int i = 0; i < 8; ++i) {
        int bit_a = (a >> i) & 1;
        int bit_b = (b >> i) & 1;
        int diff = bit_a - bit_b - borrow;
        if (diff < 0) {
            diff += 2;
            borrow = 1;
        } else {
            borrow = 0;
        }
        result |= (diff << i);
    }
    return result;
}
""",
        "C": """#include <stdint.h>

uint8_t binary_sub(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t borrow = 0;
    for (int i = 0; i < 8; ++i) {
        int bit_a = (a >> i) & 1;
        int bit_b = (b >> i) & 1;
        int diff = bit_a - bit_b - borrow;
        if (diff < 0) {
            diff += 2;
            borrow = 1;
        } else {
            borrow = 0;
        }
        result |= (diff << i);
    }
    return result;
}
""",
        "Java": """public class BinaryArith {
    public static int binarySub(int a, int b) {
        a &= 0xFF;
        b &= 0xFF;
        int result = 0;
        int borrow = 0;
        for (int i = 0; i < 8; i++) {
            int bitA = (a >> i) & 1;
            int bitB = (b >> i) & 1;
            int diff = bitA - bitB - borrow;
            if (diff < 0) {
                diff += 2;
                borrow = 1;
            } else {
                borrow = 0;
            }
            result |= (diff << i);
        }
        return result & 0xFF;
    }
}
""",
    }

    def get_code(self, lang: str) -> str:
        return self.codes.get(lang, self.codes["Python"])

    def get_steps(self, arr=None) -> List[VisualizationStep]:
        if isinstance(arr, (list, tuple)) and len(arr) >= 2:
            a = int(arr[0]) & 0xFF
            b = int(arr[1]) & 0xFF
        else:
            a = int(self.params.get("a")) & 0xFF
            b = int(self.params.get("b")) & 0xFF

        a_bits = f"{a:08b}"
        b_bits = f"{b:08b}"
        result = 0
        borrow = 0

        # Step 0: Előkészítés
        yield VisualizationStep(
            explanation=f"Kezdés: a = {a} (0b{a_bits}), b = {b} (0b{b_bits}). 8 bites kivonás LSB-től (jobbról) MSB-ig.",
            code_line=1,
            metrics={"bit": -1, "borrow": 0},
            array=[a, b],
            highlight=[],
            extra={
                "a": a,
                "b": b,
                "result": 0,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": "00000000",
                "bit_index": -1,
                "borrow": 0,
                "op": "sub",
            },
        )

        for i in range(8):
            bit_a = (a >> i) & 1
            bit_b = (b >> i) & 1
            diff = bit_a - bit_b - borrow
            if diff < 0:
                diff_bit = diff + 2
                next_borrow = 1
            else:
                diff_bit = diff
                next_borrow = 0

            result |= (diff_bit << i)
            res_bits = f"{result & 0xFF:08b}"

            yield VisualizationStep(
                explanation=f"{i}. bit (2^{i}={1<<i}): {bit_a} - {bit_b} - kölcsön({borrow}) = {diff} -> különbség bit={diff_bit}, új kölcsön={next_borrow}.",
                code_line=9,
                metrics={"bit": i, "borrow": borrow},
                array=[a, b, result & 0xFF],
                highlight=[2],
                extra={
                    "a": a,
                    "b": b,
                    "result": result & 0xFF,
                    "a_bits": a_bits,
                    "b_bits": b_bits,
                    "result_bits": res_bits,
                    "bit_index": i,
                    "borrow": next_borrow,
                    "op": "sub",
                },
            )

            borrow = next_borrow

        final_res = result & 0xFF
        borrow_msg = " (Alulcsordulás / negatív eredmény 2-es komplemensben)" if borrow else " (Nincs alulcsordulás)."
        yield VisualizationStep(
            explanation=f"Kivonás kész: {a} - {b} = {final_res} (0b{final_res:08b}){borrow_msg}",
            code_line=16,
            metrics={"bit": 8, "borrow": borrow},
            array=[a, b, final_res],
            highlight=[2],
            extra={
                "a": a,
                "b": b,
                "result": final_res,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": f"{final_res:08b}",
                "bit_index": 7,
                "borrow": borrow,
                "op": "sub",
            },
        )


class BinaryMulPlugin(AlgorithmPluginBase):
    id = "binary_mul"
    name = "Bináris szorzás (8 bit)"
    description = "Két 8 bites egész szám szorzása Léptetés és Hozzáadás (Shift and Add) módszerrel (8x8 bit -> 16 bit)."
    time_complexity = "O(1)"
    space_complexity = "O(1)"
    icon = "✖️"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "array"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("a", "A érték (0-255)", "int", 13, 0, 255))
        self.params.add(Param("b", "B érték (0-255)", "int", 7, 0, 255))

    def get_params(self):
        return self.params

    def set_param(self, pid, val):
        self.params.set(pid, val)

    codes = {
        "Python": """def binary_mul(a: int, b: int) -> int:
    a &= 0xFF
    b &= 0xFF
    result = 0
    for i in range(8):
        bit_b = (b >> i) & 1
        if bit_b == 1:
            partial = a << i
            result += partial
    return result
""",
        "C++": """#include <cstdint>

uint16_t binary_mul(uint8_t a, uint8_t b) {
    uint16_t result = 0;
    for (int i = 0; i < 8; ++i) {
        uint8_t bit_b = (b >> i) & 1;
        if (bit_b == 1) {
            uint16_t partial = (uint16_t)a << i;
            result += partial;
        }
    }
    return result;
}
""",
        "C": """#include <stdint.h>

uint16_t binary_mul(uint8_t a, uint8_t b) {
    uint16_t result = 0;
    for (int i = 0; i < 8; ++i) {
        uint8_t bit_b = (b >> i) & 1;
        if (bit_b == 1) {
            uint16_t partial = (uint16_t)a << i;
            result += partial;
        }
    }
    return result;
}
""",
        "Java": """public class BinaryArith {
    public static int binaryMul(int a, int b) {
        a &= 0xFF;
        b &= 0xFF;
        int result = 0;
        for (int i = 0; i < 8; i++) {
            int bitB = (b >> i) & 1;
            if (bitB == 1) {
                int partial = a << i;
                result += partial;
            }
        }
        return result;
    }
}
""",
    }

    def get_code(self, lang: str) -> str:
        return self.codes.get(lang, self.codes["Python"])

    def get_steps(self, arr=None) -> List[VisualizationStep]:
        if isinstance(arr, (list, tuple)) and len(arr) >= 2:
            a = int(arr[0]) & 0xFF
            b = int(arr[1]) & 0xFF
        else:
            a = int(self.params.get("a")) & 0xFF
            b = int(self.params.get("b")) & 0xFF

        a_bits = f"{a:08b}"
        b_bits = f"{b:08b}"
        result = 0

        # Step 0: Előkészítés
        yield VisualizationStep(
            explanation=f"Kezdés: a = {a} (0b{a_bits}), b = {b} (0b{b_bits}). Shift-and-Add bináris szorzás.",
            code_line=1,
            metrics={"bit": -1, "partial": 0},
            array=[a, b],
            highlight=[],
            extra={
                "a": a,
                "b": b,
                "result": 0,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": "0000000000000000",
                "bit_index": -1,
                "partial": 0,
                "op": "mul",
            },
        )

        for i in range(8):
            bit_b = (b >> i) & 1
            if bit_b == 1:
                partial = a << i
                result += partial
                explanation = f"b {i}. bitje 1 -> hozzáadjuk a eltolt értékét ({a} << {i} = {partial}) a részösszeghez. Új részösszeg: {result}."
            else:
                partial = 0
                explanation = f"b {i}. bitje 0 -> 0-t adunk hozzá. Részösszeg változatlan: {result}."

            res_bits_16 = f"{result:016b}"

            yield VisualizationStep(
                explanation=explanation,
                code_line=8,
                metrics={"bit": i, "partial": partial},
                array=[a, b, result],
                highlight=[2],
                extra={
                    "a": a,
                    "b": b,
                    "result": result,
                    "a_bits": a_bits,
                    "b_bits": b_bits,
                    "result_bits": res_bits_16,
                    "bit_index": i,
                    "partial": partial,
                    "op": "mul",
                },
            )

        high_byte = (result >> 8) & 0xFF
        low_byte = result & 0xFF
        yield VisualizationStep(
            explanation=f"Szorzás kész: {a} * {b} = {result} (16-bit: 0b{result:016b}, felső byte: {high_byte}, alsó byte: {low_byte}).",
            code_line=10,
            metrics={"bit": 8, "result": result},
            array=[a, b, result],
            highlight=[2],
            extra={
                "a": a,
                "b": b,
                "result": result,
                "a_bits": a_bits,
                "b_bits": b_bits,
                "result_bits": f"{result:016b}",
                "bit_index": 7,
                "partial": 0,
                "op": "mul",
            },
        )
