#!/usr/bin/env python3

from typing import Any, Optional, Dict, Tuple, Union # "tuple" works from 3.9 onwards

import bare68k as b68k
from bare68k.consts import M68K_CPU_TYPE_68000, MEM_FC_SUPER_MASK 

cpucfg = b68k.CPUConfig(M68K_CPU_TYPE_68000)
memcfg = b68k.MemoryConfig()
memcfg.add_ram_range(0, 2)
runcfg = b68k.RunConfig()
runtime = b68k.Runtime(cpucfg, memcfg, runcfg)

base = 0x8000
stack = 0x9200


def parse_srec_line(line: str) -> Optional[Union[
        Tuple[int, bytes, bytes], Tuple[int, bytes]]]:
    line = line.strip()
    if line[0] != 'S':
        return None
    record_type = int(line[1])
    bytecount: int = int(line[2:4], 16)
    if record_type in (1,2,3):
        addrsize = record_type + 1
        return (
                bytecount,
                bytes.fromhex(line[4:4+addrsize*2]),
                bytes.fromhex(line[4+addrsize*2:-2])
        )
    elif record_type in (7,8,9):
        return (
                bytecount,
                bytes.fromhex(line[4:-2])
        )
    return None

class m68k:
    def __init__(self):
        self.mem = runtime.get_mem()
        self.cpu = runtime.get_cpu()
        self.new_base = base

    def load_file(self, fname: str):
        b68k.api.tools.setup_breakpoints(1)
        self.found_new_base = False
        self.new_base = base
        c = 0
        with open(fname, 'r') as f:
            for line in f.readlines():
                parsed_line = parse_srec_line(line)
                print(parsed_line)
                if parsed_line == None:
                    continue
                address = int.from_bytes(parsed_line[1], "big")
                if len(parsed_line) == 3:
                    bytecode: bytes = parsed_line[2]
                    self.c = 0
                    for dec_byte in bytecode:
                        print(f"writing {dec_byte:02X} at {base+c:02X}")
                        self.mem.w8(address+c, dec_byte)
                        c+=1
                else:
                    self.found_new_base = True
                    self.new_base = address
                    b68k.api.tools.set_breakpoint(
                                b68k.api.tools.get_next_free_breakpoint(),
                                address, MEM_FC_SUPER_MASK, None)

                    print(f"found start at {self.new_base:02X}")
                #c+=1
                #byte = f.read(1)

        print(f"Loaded {self.c} bytes and starting at {self.new_base:02X} (stack {stack:02X})\n")
        runtime.reset(self.new_base, stack)


    def get_current_line(self) -> str:
        current_line = b68k.api.disasm.disassemble(self.cpu.r_pc())
        return f"0x{self.cpu.r_pc():08X}: {current_line[2]}"

    def step(self):
        self.cpu.execute(1)
        print(self.cpu.get_regs())

    def format_sreg(self, sr: int) -> str:
        mask = 0x8000
        prot = "T?S??210???XNZVC"
        string = ""
        for i in range(16):
            if mask & sr:
                string += prot[i]
            else:
                string += "-"
            mask >>= 1
        return string

    def get_regs(self) -> Dict[str, int]:
        return {
            "d0": self.cpu.r_dx(0),
            "d1": self.cpu.r_dx(1),
            "d2": self.cpu.r_dx(2),
            "d3": self.cpu.r_dx(3),
            "d4": self.cpu.r_dx(4),
            "d5": self.cpu.r_dx(5),
            "d6": self.cpu.r_dx(6),
            "d7": self.cpu.r_dx(7),
            "a0": self.cpu.r_ax(0),
            "a1": self.cpu.r_ax(1),
            "a2": self.cpu.r_ax(2),
            "a3": self.cpu.r_ax(3),
            "a4": self.cpu.r_ax(4),
            "a5": self.cpu.r_ax(5),
            "a6": self.cpu.r_ax(6),
            "a7": self.cpu.r_ax(7),
            "sr": self.cpu.r_sr()
        }

    def get_mem(self, start, bytelen) -> bytes:
        bytearray = b''
        for i in range(bytelen):
            bytearray += self.mem.r8(start+i).to_bytes(1, "big")
        return bytearray
            
    def poweroff(self):
        runtime.shutdown()


