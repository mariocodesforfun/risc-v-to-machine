from enum import Enum
import sys

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


def parse_assembly(assembly_file):
    result = []
    with open(assembly_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        if line.endswith(':'):
            result.append({"type": "label", "name": line[:-1]})
        else:
            parts = line.split()
            operands = []
            for arg in parts[1:]:
                if arg.endswith(','):
                    arg = arg[:-1]
                operands.append(arg)
            result.append({
                "type": "instruction",
                "mnemonic": parts[0],
                "operands": operands,
            })
    return result


def parse_register(reg_str):
    if reg_str.startswith('x'):
        return int(reg_str[1:])
    raise ValueError(f"bad register: {reg_str}")


def parse_immediate(imm_str, labels):
    if '(' in imm_str:
        parts = imm_str.split('(')
        return int(parts[0])
    
    if imm_str in labels:
        return labels[imm_str]
    
    try:
        return int(imm_str)
    except ValueError:
        raise ValueError(f"bad immediate: {imm_str}")


def int_to_binary(value, bits, signed=False):
    if signed:
        if value < 0:
            value = (1 << bits) + value
        return format(value, f'0{bits}b')[-bits:]
    else:
        if value < 0:
            raise ValueError(f"negative value: {value}")
        return format(value, f'0{bits}b')[-bits:]


def generate_machine_code_from_instruction(instruction, labels):
    mnemonic = instruction["mnemonic"]
    operands = instruction["operands"]
    pc = instruction.get("pc", 0)
    
    if mnemonic not in INSTRUCTIONS:
        raise ValueError(f"Unknown instruction: {mnemonic}")
    
    inst_info = INSTRUCTIONS[mnemonic]
    inst_type = inst_info["type"]
    opcode = inst_info["opcode"]
    
    breakdown = {
        "mnemonic": mnemonic,
        "operands": operands,
        "pc": pc,
        "opcode": opcode,
        "type": inst_type.name,
    }
    
    if inst_type == InstructionType.R:
        rd = parse_register(operands[0])
        rs1 = parse_register(operands[1])
        rs2 = parse_register(operands[2])
        funct3 = inst_info["funct3"]
        funct7 = inst_info.get("funct7", "0000000")
        binary = funct7 + int_to_binary(rs2, 5) + int_to_binary(rs1, 5) + funct3 + int_to_binary(rd, 5) + opcode
        
        breakdown.update({
            "funct7": funct7,
            "rs2": rs2,
            "rs1": rs1,
            "funct3": funct3,
            "rd": rd,
        })
        
    elif inst_type == InstructionType.I:
        rd = parse_register(operands[0])
        
        if '(' in operands[1]:
            imm_str = operands[1]
            imm = parse_immediate(imm_str, labels)
            rs1 = parse_register(operands[1].split('(')[1].rstrip(')'))
        else:
            rs1 = parse_register(operands[1])
            imm = parse_immediate(operands[2], labels)
        
        funct3 = inst_info.get("funct3", "000")
        
        if mnemonic in ['slli', 'srli', 'srai']:
            funct7 = inst_info.get("funct7", "0000000")
            imm_low = imm & 0x1F
            imm_high = (imm >> 5) & 0x7F
            binary = int_to_binary(imm_high, 7) + int_to_binary(imm_low, 5) + int_to_binary(rs1, 5) + funct3 + int_to_binary(rd, 5) + opcode
            breakdown.update({
                "funct7": int_to_binary(imm_high, 7),
                "imm_low": imm_low,
                "rs1": rs1,
                "funct3": funct3,
                "rd": rd,
            })
        else:
            imm_12bit = imm & 0xFFF
            imm_binary = int_to_binary(imm_12bit, 12, signed=True)
            binary = imm_binary + int_to_binary(rs1, 5) + funct3 + int_to_binary(rd, 5) + opcode
            breakdown.update({
                "imm": imm,
                "imm_binary": imm_binary,
                "rs1": rs1,
                "funct3": funct3,
                "rd": rd,
            })
        
    elif inst_type == InstructionType.S:
        rs2 = parse_register(operands[0])
        imm_str = operands[1]
        imm = parse_immediate(imm_str, labels)
        rs1 = parse_register(imm_str.split('(')[1].rstrip(')'))
        funct3 = inst_info["funct3"]
        imm_high = (imm >> 5) & 0x7F
        imm_low = imm & 0x1F
        binary = int_to_binary(imm_high, 7) + int_to_binary(rs2, 5) + int_to_binary(rs1, 5) + funct3 + int_to_binary(imm_low, 5) + opcode
        
        breakdown.update({
            "imm": imm,
            "imm_high": imm_high,
            "imm_low": imm_low,
            "rs2": rs2,
            "rs1": rs1,
            "funct3": funct3,
        })
        
    elif inst_type == InstructionType.B:
        rs1 = parse_register(operands[0])
        rs2 = parse_register(operands[1])
        label = operands[2]
        target_pc = labels[label]
        offset = target_pc - pc
        funct3 = inst_info["funct3"]
        imm_12 = (offset >> 12) & 0x1
        imm_10_5 = (offset >> 5) & 0x3F
        imm_4_1 = (offset >> 1) & 0xF
        imm_11 = (offset >> 11) & 0x1
        
        binary = (int_to_binary(imm_12, 1) + int_to_binary(imm_10_5, 6) + 
                 int_to_binary(rs2, 5) + int_to_binary(rs1, 5) + funct3 + 
                 int_to_binary(imm_4_1, 4) + int_to_binary(imm_11, 1) + opcode)
        
        breakdown.update({
            "offset": offset,
            "target_pc": target_pc,
            "imm_12": imm_12,
            "imm_10_5": imm_10_5,
            "imm_4_1": imm_4_1,
            "imm_11": imm_11,
            "rs2": rs2,
            "rs1": rs1,
            "funct3": funct3,
        })
        
    elif inst_type == InstructionType.U:
        rd = parse_register(operands[0])
        imm = parse_immediate(operands[1], labels)
        imm_high = (imm >> 12) & 0xFFFFF
        binary = int_to_binary(imm_high, 20) + int_to_binary(rd, 5) + opcode
        
        breakdown.update({
            "imm": imm,
            "imm_31_12": imm_high,
            "rd": rd,
        })
        
    elif inst_type == InstructionType.J:
        rd = parse_register(operands[0])
        label = operands[1]
        target_pc = labels[label]
        offset = target_pc - pc
        imm_20 = (offset >> 20) & 0x1
        imm_10_1 = (offset >> 1) & 0x3FF
        imm_11 = (offset >> 11) & 0x1
        imm_19_12 = (offset >> 12) & 0xFF
        
        binary = (int_to_binary(imm_20, 1) + int_to_binary(imm_10_1, 10) + 
                 int_to_binary(imm_11, 1) + int_to_binary(imm_19_12, 8) + 
                 int_to_binary(rd, 5) + opcode)
        
        breakdown.update({
            "offset": offset,
            "target_pc": target_pc,
            "imm_20": imm_20,
            "imm_10_1": imm_10_1,
            "imm_11": imm_11,
            "imm_19_12": imm_19_12,
            "rd": rd,
        })
    
    else:
        raise ValueError(f"Unsupported instruction type: {inst_type}")
    
    machine_code_int = int(binary, 2)
    breakdown["binary"] = binary
    breakdown["hex"] = format(machine_code_int, '08x')
    breakdown["decimal"] = machine_code_int
    
    return machine_code_int, breakdown


def generate_machine_code(input_file="input.s"):
    parsed_assembly, labels, PC = address_assignment(input_file)
    machine_code = []
    
    for item in parsed_assembly:
        if item["type"] == "instruction":
            mc_int, breakdown = generate_machine_code_from_instruction(item, labels)
            machine_code.append((mc_int, breakdown))
    
    return machine_code


def address_assignment(input_file="input.s"):
    PC = 0
    parsed_assembly = parse_assembly(input_file)
    labels = {}
    for item in parsed_assembly:
        if item["type"] == "label":
            label_name = item["name"]
            labels[label_name] = PC
        else:
            item["pc"] = PC
            PC += 4
    return parsed_assembly, labels, PC

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    OPCODE = '\033[94m'
    FUNCT3 = '\033[92m'
    FUNCT7 = '\033[93m'
    RD = '\033[91m'
    RS1 = '\033[95m'
    RS2 = '\033[96m'
    IMM = '\033[97m'
    PC = '\033[37m'
    MNEMONIC = '\033[1m'
    OPERANDS = '\033[36m'


def colorize_binary(binary, breakdown, inst_type):
    if inst_type == InstructionType.R:
        funct7 = binary[0:7]
        rs2 = binary[7:12]
        rs1 = binary[12:17]
        funct3 = binary[17:20]
        rd = binary[20:25]
        opcode = binary[25:32]
        return (f"{Colors.FUNCT7}{funct7}{Colors.RESET} "
                f"{Colors.RS2}{rs2}{Colors.RESET} "
                f"{Colors.RS1}{rs1}{Colors.RESET} "
                f"{Colors.FUNCT3}{funct3}{Colors.RESET} "
                f"{Colors.RD}{rd}{Colors.RESET} "
                f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    elif inst_type == InstructionType.I:
        if breakdown["mnemonic"] in ['slli', 'srli', 'srai']:
            imm_high = binary[0:7]
            imm_low = binary[7:12]
            rs1 = binary[12:17]
            funct3 = binary[17:20]
            rd = binary[20:25]
            opcode = binary[25:32]
            return (f"{Colors.IMM}{imm_high}{Colors.RESET} "
                    f"{Colors.IMM}{imm_low}{Colors.RESET} "
                    f"{Colors.RS1}{rs1}{Colors.RESET} "
                    f"{Colors.FUNCT3}{funct3}{Colors.RESET} "
                    f"{Colors.RD}{rd}{Colors.RESET} "
                    f"{Colors.OPCODE}{opcode}{Colors.RESET}")
        else:
            imm = binary[0:12]
            rs1 = binary[12:17]
            funct3 = binary[17:20]
            rd = binary[20:25]
            opcode = binary[25:32]
            return (f"{Colors.IMM}{imm}{Colors.RESET} "
                    f"{Colors.RS1}{rs1}{Colors.RESET} "
                    f"{Colors.FUNCT3}{funct3}{Colors.RESET} "
                    f"{Colors.RD}{rd}{Colors.RESET} "
                    f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    elif inst_type == InstructionType.S:
        imm_high = binary[0:7]
        rs2 = binary[7:12]
        rs1 = binary[12:17]
        funct3 = binary[17:20]
        imm_low = binary[20:25]
        opcode = binary[25:32]
        return (f"{Colors.IMM}{imm_high}{Colors.RESET} "
                f"{Colors.RS2}{rs2}{Colors.RESET} "
                f"{Colors.RS1}{rs1}{Colors.RESET} "
                f"{Colors.FUNCT3}{funct3}{Colors.RESET} "
                f"{Colors.IMM}{imm_low}{Colors.RESET} "
                f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    elif inst_type == InstructionType.B:
        imm_12 = binary[0:1]
        imm_10_5 = binary[1:7]
        rs2 = binary[7:12]
        rs1 = binary[12:17]
        funct3 = binary[17:20]
        imm_4_1 = binary[20:24]
        imm_11 = binary[24:25]
        opcode = binary[25:32]
        return (f"{Colors.IMM}{imm_12}{imm_10_5}{Colors.RESET} "
                f"{Colors.RS2}{rs2}{Colors.RESET} "
                f"{Colors.RS1}{rs1}{Colors.RESET} "
                f"{Colors.FUNCT3}{funct3}{Colors.RESET} "
                f"{Colors.IMM}{imm_4_1}{imm_11}{Colors.RESET} "
                f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    elif inst_type == InstructionType.U:
        imm = binary[0:20]
        rd = binary[20:25]
        opcode = binary[25:32]
        return (f"{Colors.IMM}{imm}{Colors.RESET} "
                f"{Colors.RD}{rd}{Colors.RESET} "
                f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    elif inst_type == InstructionType.J:
        imm_20 = binary[0:1]
        imm_10_1 = binary[1:11]
        imm_11 = binary[11:12]
        imm_19_12 = binary[12:20]
        rd = binary[20:25]
        opcode = binary[25:32]
        return (f"{Colors.IMM}{imm_20}{imm_10_1}{imm_11}{imm_19_12}{Colors.RESET} "
                f"{Colors.RD}{rd}{Colors.RESET} "
                f"{Colors.OPCODE}{opcode}{Colors.RESET}")
    
    return binary


def print_table(machine_codes):
    print(f"\n{'='*130}")
    print(f"{'PC':<8} {'Instruction':<25} {'Operands':<20} {'Type':<6} {'Binary':<50} {'Hex':<10}")
    print(f"{'='*130}")
    
    for mc_int, breakdown in machine_codes:
        pc = breakdown["pc"]
        mnemonic = breakdown["mnemonic"]
        operands_str = ", ".join(breakdown["operands"])
        binary = breakdown["binary"]
        hex_val = breakdown["hex"]
        inst_type = InstructionType[breakdown["type"]]
        type_str = breakdown["type"]
        
        colored_binary = colorize_binary(binary, breakdown, inst_type)
        binary_display_width = len(binary) + 10
        colored_binary_padded = colored_binary + " " * max(0, 50 - binary_display_width)
        
        print(f"{Colors.PC}{pc:08x}{Colors.RESET}  "
              f"{Colors.MNEMONIC}{mnemonic:<25}{Colors.RESET} "
              f"{Colors.OPERANDS}{operands_str:<20}{Colors.RESET} "
              f"{type_str:<6} "
              f"{colored_binary_padded} "
              f"{hex_val}")
    
    print(f"{'='*120}")
    print(f"\n{Colors.BOLD}Color Legend:{Colors.RESET}")
    print(f"  {Colors.OPCODE}Blue{Colors.RESET} = Opcode")
    print(f"  {Colors.FUNCT3}Green{Colors.RESET} = Funct3")
    print(f"  {Colors.FUNCT7}Yellow{Colors.RESET} = Funct7")
    print(f"  {Colors.RD}Red{Colors.RESET} = Destination Register (rd)")
    print(f"  {Colors.RS1}Magenta{Colors.RESET} = Source Register 1 (rs1)")
    print(f"  {Colors.RS2}Cyan{Colors.RESET} = Source Register 2 (rs2)")
    print(f"  {Colors.IMM}Bright White{Colors.RESET} = Immediate Value")


if __name__ == "__main__":
    try:
        input_file = sys.argv[1] if len(sys.argv) > 1 else "input.s"
        machine_codes = generate_machine_code(input_file)
        print_table(machine_codes)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
