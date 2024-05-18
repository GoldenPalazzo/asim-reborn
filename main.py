#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import logging
import os
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Any, Optional, Tuple, Union # "tuple" works from 3.9 onwards

import bare68k as b68k
from bare68k.consts import M68K_CPU_TYPE_68000, MEM_FC_SUPER_MASK 

cpucfg = b68k.CPUConfig(M68K_CPU_TYPE_68000)
memcfg = b68k.MemoryConfig()
memcfg.add_ram_range(0, 2)
runcfg = b68k.RunConfig()
runtime = b68k.Runtime(cpucfg, memcfg, runcfg)

fname: str = ""
base = 0x8000
stack = 0x9000

logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
def open_file_selector():
    global fname
    print("Open file selector")
    fname = filedialog.askopenfilename()
    print(fname)

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

def run_68k():
    mem = runtime.get_mem()
    cpu = runtime.get_cpu()
    c=0
    b68k.api.tools.setup_breakpoints(99999)
    found_new_base = False
    new_base = base
    with open(fname, 'r') as f:
        for line in f.readlines():
            parsed_line = parse_srec_line(line)
            print(parsed_line)
            if parsed_line == None:
                continue
            address = int.from_bytes(parsed_line[1], "big")
            if len(parsed_line) == 3:
                bytecode: bytes = parsed_line[2]
                c = 0
                for dec_byte in bytecode:
                    print(f"writing {dec_byte:02X} at {base+c:02X}")
                    mem.w8(address+c, dec_byte)
                    b68k.api.tools.set_breakpoint(
                            b68k.api.tools.get_next_free_breakpoint(),
                            address+c, MEM_FC_SUPER_MASK, None)
                    c+=1
            else:
                found_new_base = True
                new_base = address
                print(f"found start at {new_base:02X}")
            #c+=1
            #byte = f.read(1)

    print(f"Loaded {c} bytes and starting at {new_base:02X} (stack {stack:02X})\n")
    runtime.reset(new_base, stack)

    
    while True:
        try:
            current_line = b68k.api.disasm.disassemble(cpu.r_pc())
            print(f"{cpu.r_pc():02X}: {current_line[2]}")
            runtime.run()
            print(cpu.get_regs())
            input()
        except KeyboardInterrupt:
            break
    runtime.shutdown()
    pass

def main():
    global fname
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        run_68k()
        return
    root = tk.Tk()
    root.title("ASIM Reborn")
    root.geometry("800x600")
    a = tk.Label(root, text="Hello, World!")
    a.grid()
    btn = tk.Button(root, text="Open file selector", command=open_file_selector)
    btn.grid(column=0, row=1)
    run_btn = tk.Button(root, text="Run Bare68k", command=run_68k)
    run_btn.grid(column=1, row=1)
    root.mainloop()

if __name__ == "__main__":
    main()
