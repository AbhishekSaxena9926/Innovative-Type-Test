"""Reference functional simulator for the 8-bit Mini Processor project.

Architecture:
- 8-bit accumulator (ACC), instruction register (IR), output register (OUT)
- 4-bit program counter (PC) and 4-bit memory address operand
- 16 x 8-bit instruction ROM and 16 x 8-bit data RAM
- 8-bit instruction: opcode[7:4] | operand[3:0]

This is an instruction-level functional model, not gate-level or FPGA timing simulation.
"""
from dataclasses import dataclass, field
from typing import List, Optional

OPCODES = {
    0x0: "NOP", 0x1: "LDI", 0x2: "LDA", 0x3: "STA",
    0x4: "ADD", 0x5: "SUB", 0x6: "AND", 0x7: "OR",
    0x8: "XOR", 0x9: "JMP", 0xA: "JZ", 0xB: "JNZ",
    0xC: "INC", 0xD: "DEC", 0xE: "OUT", 0xF: "HLT",
}


def encode(mnemonic: str, operand: int = 0) -> int:
    """Encode one 8-bit instruction from a mnemonic and 4-bit operand."""
    rev = {name: code for code, name in OPCODES.items()}
    name = mnemonic.upper()
    if name not in rev:
        raise ValueError(f"Unknown instruction: {mnemonic}")
    if not 0 <= operand <= 0xF:
        raise ValueError("Operand must be in the range 0..15")
    return (rev[name] << 4) | operand


@dataclass
class MiniProcessor:
    program: List[int] = field(default_factory=lambda: [0] * 16)
    data: List[int] = field(default_factory=lambda: [0] * 16)
    pc: int = 0
    acc: int = 0
    ir: int = 0
    out: int = 0
    z: int = 1
    c: int = 0  # Carry for ADD/INC; borrow for SUB/DEC
    halted: bool = False
    steps: int = 0
    trace: List[dict] = field(default_factory=list)

    def load_program(self, instructions: List[int]) -> None:
        if len(instructions) > 16:
            raise ValueError("Program exceeds 16 instruction locations")
        self.program = [0] * 16
        for i, inst in enumerate(instructions):
            if not 0 <= inst <= 0xFF:
                raise ValueError("Instructions must be 8-bit values")
            self.program[i] = inst
        self.pc = 0
        self.halted = False
        self.steps = 0
        self.trace.clear()

    def _set_z(self) -> None:
        self.z = int(self.acc == 0)

    def step(self) -> Optional[dict]:
        if self.halted:
            return None
        pc_before = self.pc
        self.ir = self.program[self.pc]
        self.pc = (self.pc + 1) & 0xF
        opcode = (self.ir >> 4) & 0xF
        operand = self.ir & 0xF
        mnemonic = OPCODES[opcode]
        acc_before = self.acc
        note = ""

        if opcode == 0x0:  # NOP
            note = "No operation"
        elif opcode == 0x1:  # LDI
            self.acc = operand
            self._set_z()
            note = f"ACC <- 0x{operand:02X}"
        elif opcode == 0x2:  # LDA
            self.acc = self.data[operand] & 0xFF
            self._set_z()
            note = f"ACC <- RAM[{operand}]"
        elif opcode == 0x3:  # STA
            self.data[operand] = self.acc & 0xFF
            note = f"RAM[{operand}] <- ACC"
        elif opcode == 0x4:  # ADD
            total = self.acc + self.data[operand]
            self.c = int(total > 0xFF)
            self.acc = total & 0xFF
            self._set_z()
            note = f"ACC <- ACC + RAM[{operand}]"
        elif opcode == 0x5:  # SUB
            value = self.data[operand]
            self.c = int(self.acc < value)  # borrow flag
            self.acc = (self.acc - value) & 0xFF
            self._set_z()
            note = f"ACC <- ACC - RAM[{operand}]"
        elif opcode == 0x6:  # AND
            self.acc &= self.data[operand]
            self._set_z()
            note = f"ACC <- ACC AND RAM[{operand}]"
        elif opcode == 0x7:  # OR
            self.acc |= self.data[operand]
            self._set_z()
            note = f"ACC <- ACC OR RAM[{operand}]"
        elif opcode == 0x8:  # XOR
            self.acc ^= self.data[operand]
            self._set_z()
            note = f"ACC <- ACC XOR RAM[{operand}]"
        elif opcode == 0x9:  # JMP
            self.pc = operand
            note = f"PC <- {operand}"
        elif opcode == 0xA:  # JZ
            if self.z:
                self.pc = operand
                note = f"Z=1; branch to {operand}"
            else:
                note = "Z=0; branch not taken"
        elif opcode == 0xB:  # JNZ
            if not self.z:
                self.pc = operand
                note = f"Z=0; branch to {operand}"
            else:
                note = "Z=1; branch not taken"
        elif opcode == 0xC:  # INC
            total = self.acc + 1
            self.c = int(total > 0xFF)
            self.acc = total & 0xFF
            self._set_z()
            note = "ACC <- ACC + 1"
        elif opcode == 0xD:  # DEC
            self.c = int(self.acc == 0)  # borrow on decrement from zero
            self.acc = (self.acc - 1) & 0xFF
            self._set_z()
            note = "ACC <- ACC - 1"
        elif opcode == 0xE:  # OUT
            self.out = self.acc
            note = "OUT <- ACC"
        elif opcode == 0xF:  # HLT
            self.halted = True
            note = "Processor halted"

        self.steps += 1
        row = {
            "step": self.steps,
            "pc": pc_before,
            "ir": self.ir,
            "mnemonic": mnemonic,
            "operand": operand,
            "description": note,
            "acc_before": acc_before,
            "acc": self.acc,
            "m0": self.data[0],
            "m1": self.data[1],
            "out": self.out,
            "z": self.z,
            "c": self.c,
            "halted": self.halted,
        }
        self.trace.append(row)
        return row

    def run(self, max_steps: int = 64) -> List[dict]:
        while not self.halted and self.steps < max_steps:
            self.step()
        if not self.halted:
            raise RuntimeError("Execution limit reached; program may contain an infinite loop")
        return self.trace


def demo_program():
    cpu = MiniProcessor()
    cpu.load_program([
        encode("LDI", 5),   # ACC = 5
        encode("STA", 0),   # RAM[0] = 5
        encode("LDI", 3),   # ACC = 3
        encode("ADD", 0),   # ACC = 3 + 5 = 8
        encode("STA", 1),   # RAM[1] = 8
        encode("LDA", 1),   # ACC = 8
        encode("SUB", 0),   # ACC = 8 - 5 = 3
        encode("OUT"),      # OUT = 3
        encode("HLT"),      # stop
    ])
    return cpu, cpu.run()


def run_self_tests():
    results = []
    # Addition: 5 + 3 = 8
    cpu = MiniProcessor(data=[5, 3] + [0] * 14)
    cpu.load_program([encode("LDA", 0), encode("ADD", 1), encode("OUT"), encode("HLT")])
    cpu.run()
    results.append(("ADD 5 + 3", cpu.out == 8, f"OUT=0x{cpu.out:02X}"))

    # Carry: 250 + 10 = 4 with carry set
    cpu = MiniProcessor(data=[250, 10] + [0] * 14)
    cpu.load_program([encode("LDA", 0), encode("ADD", 1), encode("OUT"), encode("HLT")])
    cpu.run()
    results.append(("ADD carry", cpu.out == 4 and cpu.c == 1, f"OUT=0x{cpu.out:02X}, C={cpu.c}"))

    # Subtraction: 8 - 5 = 3
    cpu = MiniProcessor(data=[8, 5] + [0] * 14)
    cpu.load_program([encode("LDA", 0), encode("SUB", 1), encode("OUT"), encode("HLT")])
    cpu.run()
    results.append(("SUB 8 - 5", cpu.out == 3 and cpu.c == 0, f"OUT=0x{cpu.out:02X}, borrow={cpu.c}"))

    # Logic: 0xAA AND 0x0F = 0x0A
    cpu = MiniProcessor(data=[0xAA, 0x0F] + [0] * 14)
    cpu.load_program([encode("LDA", 0), encode("AND", 1), encode("OUT"), encode("HLT")])
    cpu.run()
    results.append(("AND operation", cpu.out == 0x0A, f"OUT=0x{cpu.out:02X}"))

    # Conditional branch: zero result causes jump to OUT instruction
    cpu = MiniProcessor()
    cpu.load_program([encode("LDI", 0), encode("JZ", 3), encode("LDI", 5), encode("OUT"), encode("HLT")])
    cpu.run()
    results.append(("JZ branch", cpu.out == 0, f"OUT=0x{cpu.out:02X}"))

    # HLT: no instruction after halt is executed
    cpu = MiniProcessor()
    cpu.load_program([encode("LDI", 7), encode("HLT"), encode("LDI", 2)])
    cpu.run()
    results.append(("HLT stops execution", cpu.acc == 7 and cpu.steps == 2, f"steps={cpu.steps}, ACC=0x{cpu.acc:02X}"))

    return results


if __name__ == "__main__":
    cpu, trace = demo_program()
    print("DEMONSTRATION PROGRAM TRACE")
    print("Step PC IR  Instruction  ACC  M[0] M[1] OUT  Z C")
    for r in trace:
        print(f"{r['step']:>4} {r['pc']:02X} {r['ir']:02X}  {r['mnemonic']:<4} {r['operand']:X}       "
              f"{r['acc']:02X}   {r['m0']:02X}   {r['m1']:02X}   {r['out']:02X}   {r['z']} {r['c']}")
    print(f"\nFinal output: {cpu.out} (0x{cpu.out:02X})")
    print("\nSELF-TESTS")
    all_ok = True
    for name, passed, detail in run_self_tests():
        print(f"{'PASS' if passed else 'FAIL'} | {name} | {detail}")
        all_ok &= passed
    print(f"\nResult: {'ALL TESTS PASSED' if all_ok else 'TEST FAILURE'}")
    raise SystemExit(0 if all_ok else 1)
