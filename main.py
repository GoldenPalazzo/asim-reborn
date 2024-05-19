#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import logging
import os
import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Any, Optional, Dict, Tuple, Union # "tuple" works from 3.9 onwards

from PySide2.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog
from PySide2.QtGui import QFont, QTextCursor

import compiler, ide, m68k, run

ftypes = [
    ('SREC files', '*.srec *.SREC *.h68 *.H68'),
    ('All files', '*'), 
]

logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

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
    if len(sys.argv) > 1:
        main_cpu = m68k.m68k()
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
        app = QApplication(sys.argv)
        main_window = ide.IDE()
        comp = compiler.Compiler()
        sys.exit(app.exec_())
        #app = ASIMWindow(main_cpu)
        #app.mainloop()
if __name__ == "__main__":
    main()
