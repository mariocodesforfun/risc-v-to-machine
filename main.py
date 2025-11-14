from enum import Enum

class InstructionType(Enum):
    R = 1
    I = 2
    S = 3
    B = 4
    U = 5
    J = 6

# risc-v instructions
INSTRUCTIONS: dict[str, dict] = {
    # -----------------------
    # R-TYPE (opcode 0110011)
    # -----------------------
    'add':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "000", "funct7": "0000000"},
    'sub':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "000", "funct7": "0100000"},
    'sll':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "001", "funct7": "0000000"},
    'slt':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "010", "funct7": "0000000"},
    'sltu':  {"type": InstructionType.R, "opcode": "0110011", "funct3": "011", "funct7": "0000000"},
    'xor':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "100", "funct7": "0000000"},
    'srl':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "101", "funct7": "0000000"},
    'sra':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "101", "funct7": "0100000"},
    'or':    {"type": InstructionType.R, "opcode": "0110011", "funct3": "110", "funct7": "0000000"},
    'and':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "111", "funct7": "0000000"},

    # RV32M (Multiply/Divide)
    'mul':   {"type": InstructionType.R, "opcode": "0110011", "funct3": "000", "funct7": "0000001"},

    # -----------------------
    # I-TYPE ALU (opcode 0010011)
    # -----------------------
    'addi':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "000"},
    'slti':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "010"},
    'sltiu': {"type": InstructionType.I, "opcode": "0010011", "funct3": "011"},
    'xori':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "100"},
    'ori':   {"type": InstructionType.I, "opcode": "0010011", "funct3": "110"},
    'andi':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "111"},

    # Shift immediates — funct7 matters
    'slli':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "001", "funct7": "0000000"},
    'srli':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "101", "funct7": "0000000"},
    'srai':  {"type": InstructionType.I, "opcode": "0010011", "funct3": "101", "funct7": "0100000"},

    # -----------------------
    # LOADS — I-TYPE (opcode 0000011)
    # -----------------------
    'lb':   {"type": InstructionType.I, "opcode": "0000011", "funct3": "000"},
    'lh':   {"type": InstructionType.I, "opcode": "0000011", "funct3": "001"},
    'lw':   {"type": InstructionType.I, "opcode": "0000011", "funct3": "010"},
    'lbu':  {"type": InstructionType.I, "opcode": "0000011", "funct3": "100"},
    'lhu':  {"type": InstructionType.I, "opcode": "0000011", "funct3": "101"},

    # -----------------------
    # STORES — S-TYPE (opcode 0100011)
    # -----------------------
    'sb':   {"type": InstructionType.S, "opcode": "0100011", "funct3": "000"},
    'sh':   {"type": InstructionType.S, "opcode": "0100011", "funct3": "001"},
    'sw':   {"type": InstructionType.S, "opcode": "0100011", "funct3": "010"},

    # -----------------------
    # BRANCH — B-TYPE (opcode 1100011)
    # -----------------------
    'beq':  {"type": InstructionType.B, "opcode": "1100011", "funct3": "000"},
    'bne':  {"type": InstructionType.B, "opcode": "1100011", "funct3": "001"},
    'blt':  {"type": InstructionType.B, "opcode": "1100011", "funct3": "100"},
    'bge':  {"type": InstructionType.B, "opcode": "1100011", "funct3": "101"},
    'bltu': {"type": InstructionType.B, "opcode": "1100011", "funct3": "110"},
    'bgeu': {"type": InstructionType.B, "opcode": "1100011", "funct3": "111"},

    # -----------------------
    # J-TYPE (opcode 1101111)
    # -----------------------
    'jal':  {"type": InstructionType.J, "opcode": "1101111"},

    # -----------------------
    # JALR — I-TYPE (opcode 1100111)
    # -----------------------
    'jalr': {"type": InstructionType.I, "opcode": "1100111", "funct3": "000"},

    # -----------------------
    # U-TYPE (opcode 0110111, 0010111)
    # -----------------------
    'lui':   {"type": InstructionType.U, "opcode": "0110111"},
    'auipc': {"type": InstructionType.U, "opcode": "0010111"},
}


def parse_assembly(assembly_file: str) -> list[dict]: 
    result: list[dict] = []
    with open(assembly_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        if line == '':
            continue
        if line.endswith(':'):
            label = line[:-1]
            result.append({
                "type": "label",
                "name": label,
            })
        else:
            instruction = line.split()
            clean_operands = []
            for arg in instruction[1:]:
                if arg.endswith(','):
                    # remove the comma
                    arg = arg[:-1]
                clean_operands.append(arg)
            result.append({
                "type": "instruction",
                "mnemonic": instruction[0],
                "operands": clean_operands,
            })
    return result


def generate_machine_code() -> list[int]:
    parsed_assembly, labels, PC = address_assignment()
    machine_code: list[int] = []



def address_assignment():
    PC: int = 0
    parsed_assembly = parse_assembly("input.s")
    # for labels -> PC
    # for instructions -> PC + 4
    labels: dict[str, int] = {}
    for item in parsed_assembly:
        if item["type"] == "label":
            label_name = item["name"]
            labels[label_name] = PC
        else:
            item["pc"] = PC
            PC += 4
    return parsed_assembly, labels, PC

def generate_machine_code_from_instruction(instruction: dict) -> int:
    # R -> rd, rs1, rs2 -> order: funct7, rs2, rs1, funct3, rd, opcode
    # I -> rd, rs1, imm -> order: imm[11:0], rs1, funct3, rd, opcode
    # S -> rs1, rs2, imm -> order: imm[11:0], rs2, rs1, funct3, opcode
    # B -> rs1, rs2, imm -> order: imm[11:0], rs2, rs1, funct3, opcode
    # U -> imm -> order: imm[31:12] rd opcode 
    # J -> rd, imm -> order: imm[20 | 10:1 | 11 | 19:12], rd, opcode

    return 0


if __name__ == "__main__":
    parsed_assembly, labels, PC = address_assignment()
