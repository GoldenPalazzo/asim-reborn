#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import logging
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Any, Optional

import bare68k as b68k
from bare68k.consts import M68K_CPU_TYPE_68000, MEM_FC_SUPER_MASK 

cpucfg = b68k.CPUConfig(M68K_CPU_TYPE_68000)
memcfg = b68k.MemoryConfig()
memcfg.add_ram_range(0, 2)
#memcfg.add_rom_range(2, 1)
runcfg = b68k.RunConfig()
runtime: Optional[b68k.Runtime] = b68k.Runtime(cpucfg, memcfg, runcfg)

fname: str = ""
base = 0x8000
stack = 0x9000

logging.basicConfig(filename='myapp.log', level=logging.INFO)
def open_file_selector():
    global fname
    print("Open file selector")
    fname = filedialog.askopenfilename()
    print(fname)

def run_68k():
    mem = runtime.get_mem()
    cpu = runtime.get_cpu()
    c=0
    b68k.api.tools.setup_watchpoints(1)
    b68k.api.tools.setup_breakpoints(1)
    with open(fname, 'rb') as f:
        byte = f.read(1)
        while byte != b"":
            print(f"writing {int.from_bytes(byte, 'big'):02X} at {base+c:02X}")
            mem.w8(base+c, int.from_bytes(byte, "big"))
#            b68k.api.tools.set_breakpoint(c+1, base+c, 0, None)
            c+=1
            byte = f.read(1)
        b68k.api.tools.set_breakpoint(0, base+c-1, MEM_FC_SUPER_MASK, None)
        b68k.api.tools.set_watchpoint(0, 0x10000, MEM_FC_SUPER_MASK, None)

    print(f"Loaded {c} bytes")
    runtime.reset(base, stack)

    print(cpu.get_regs(),end ="\n\n")

    runtime.run()

    print(cpu.get_regs())

    runtime.run()
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
