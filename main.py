#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import logging
import os
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Any, Optional, Dict, Tuple, Union # "tuple" works from 3.9 onwards

import bare68k as b68k
from bare68k.consts import M68K_CPU_TYPE_68000, MEM_FC_SUPER_MASK 

cpucfg = b68k.CPUConfig(M68K_CPU_TYPE_68000)
memcfg = b68k.MemoryConfig()
memcfg.add_ram_range(0, 2)
runcfg = b68k.RunConfig()
runtime = b68k.Runtime(cpucfg, memcfg, runcfg)

base = 0x8000
stack = 0x9000

ftypes = [
    ('SREC files', '*.srec *.SREC *.h68 *.H68'),
    ('All files', '*'), 
]

logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

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
        self.c = 0
        self.new_base = base

    def load_file(self, fname: str):
        b68k.api.tools.setup_breakpoints(99999)
        self.found_new_base = False
        self.new_base = base
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
                        print(f"writing {dec_byte:02X} at {base+self.c:02X}")
                        self.mem.w8(address+self.c, dec_byte)
                        b68k.api.tools.set_breakpoint(
                                b68k.api.tools.get_next_free_breakpoint(),
                                address+self.c, MEM_FC_SUPER_MASK, None)
                        self.c+=1
                else:
                    self.found_new_base = True
                    self.new_base = address
                    print(f"found start at {self.new_base:02X}")
                #c+=1
                #byte = f.read(1)

        print(f"Loaded {self.c} bytes and starting at {self.new_base:02X} (stack {stack:02X})\n")
        runtime.reset(self.new_base, stack)


    def get_current_line(self) -> str:
        current_line = b68k.api.disasm.disassemble(self.cpu.r_pc())
        return f"0x{self.cpu.r_pc():08X}: {current_line[2]}"

    def step(self):
        print(self.get_current_line())
        runtime.run()
        print(self.cpu.get_regs())


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
        }
            
    def poweroff(self):
        runtime.shutdown()

class ASIMWindow(tk.Tk):
    def __init__(self, cpu):
        super().__init__()
        self.main_cpu = cpu
        self.fname = ""
        self.title("ASIM Reborn")
        self.geometry("800x600")
        self.a = tk.Label(self, text="Hello, World!")
        self.a.grid()
        self.btn = tk.Button(self, text="Open file selector", command=self.open_file_selector)
        self.btn.grid(column=0, row=1)
        self.run_btn = tk.Button(self, text="Run Bare68k", command=self.spawn_68k)
        self.run_btn.grid(column=1, row=1)

        self.dregs = []
        self.aregs = []
        self.status: tk.Label = tk.Label()

        self.mainloop()

    def open_file_selector(self):
        print("Open file selector")
        self.fname = filedialog.askopenfilename(filetypes=ftypes)
        print(self.fname)

    def spawn_68k(self):
        new_window = tk.Toplevel()
        new_window.title("ASIM Reborn")
        new_window.geometry("800x600")
        new_window.grid()
        # registers
        dreg_frame = tk.Frame(new_window)
        areg_frame = tk.Frame(new_window)
        dreg_frame.grid(column=0, row=1)
        areg_frame.grid(column=1, row=1)
        for i in range(8):
            dreg_frame.grid_rowconfigure(i, weight=1)
            dreg_frame.grid_columnconfigure(i, weight=1)
            areg_frame.grid_rowconfigure(i, weight=1)
            areg_frame.grid_columnconfigure(i, weight=1)
            tk.Label(dreg_frame, text=f"D{i}").grid(column=0, row=i)
            d = tk.Label(dreg_frame, text="0x00000000")
            d.grid(column=1, row=i)
            self.dregs.append(d)
            a = tk.Label(areg_frame, text="0x00000000")
            a.grid(column=1, row=i)
            tk.Label(areg_frame, text=f"A{i}").grid(column=0, row=i)
            self.aregs.append(a)
        # status
        status_frame = tk.Frame(new_window)
        status_frame.grid(column=0, row=0)
        self.status = tk.Label(status_frame, text="Loading")
        self.status.grid()
        self.main_cpu.load_file(self.fname)
        self.after(2000, self.update_ui)
        # buttons
        btn_frame = tk.Frame(new_window)
        btn_frame.grid(column=0, row=2)
        step_btn = tk.Button(btn_frame, text="Step", command=self.step)
        step_btn.grid(column=0, row=0)
        run_btn = tk.Button(btn_frame, text="Run")#, command=self.run)
        run_btn.grid(column=1, row=0)
        poweroff_btn = tk.Button(btn_frame, text="Poweroff", command=self.poweroff)
        poweroff_btn.grid(column=2, row=0)

    def update_ui(self):
        regs = self.main_cpu.get_regs()
        self.status.config(text=self.main_cpu.get_current_line())
        for i in range(8):
            self.dregs[i].config(text=f"0x{regs[f'd{i}']:08X}")
            self.aregs[i].config(text=f"0x{regs[f'a{i}']:08X}")

    def step(self):
        self.main_cpu.step()
        self.update_ui()

    def poweroff(self):
        self.main_cpu.poweroff()
        self.status.config(text="Poweroff")
        self.after(2000, self.destroy)

def main():
    global fname
    main_cpu = m68k()
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        main_cpu.load_file(fname)
        while True:
            try:
                main_cpu.step()
                input()
            except KeyboardInterrupt:
                main_cpu.poweroff()
                break
    else:
        app = ASIMWindow(main_cpu)
        app.mainloop()
if __name__ == "__main__":
    main()
