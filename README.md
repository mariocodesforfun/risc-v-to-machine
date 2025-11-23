# RISC-V Assembler

Converts RISC-V assembly to machine code with colored binary output.

## Usage

```bash
python3 main.py [input_file]  # defaults file that gets read is input.s
```

Run it by either editting to input.s file or by creating your own <file_name.s> file and then running main.py

## Supported Instructions

**R-type:** add, sub, sll, slt, sltu, xor, srl, sra, or, and, mul  
**I-type:** addi, slti, sltiu, xori, ori, andi, slli, srli, srai, lb, lh, lw, lbu, lhu, jalr  
**S-type:** sb, sh, sw  
**B-type:** beq, bne, blt, bge, bltu, bgeu  
**U-type:** lui, auipc  
**J-type:** jal

## Example

```assembly
start:
    addi x1, x0, 5
    addi x2, x0, 10
    add  x3, x1, x2
```

Output shows PC, instruction, operands, type, colored binary fields, and hex.

Binary colors: Blue=opcode, Green=funct3, Yellow=funct7, Red=rd, Magenta=rs1, Cyan=rs2, White=immediate

Supports labels for branches/jumps. Comments start with `#`.

