#!/usr/bin/env python3

import sys
from typing import Optional, Union, Callable, List
import PySide6

from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget
from PySide6.QtGui import QFont, QTextCursor, QAction, QTextOption
from PySide6.QtCore import Qt

import m68k

class Runner(QWidget):


    def __init__(self):
        super().__init__()
        self.main_cpu = m68k.m68k()
        self.dregs: List[QLabel] = [QLabel(f"0x{0:08X}") for _ in range(8)]
        self.aregs: List[QLabel] = [QLabel(f"0x{0:08X}") for _ in range(8)]
        self.sreg = QLabel(f"{0:016b}")
        self.pc = QLabel(f"{0:08X}")
        self.current_instruction = QLabel("")

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Debugger')
        frame = QVBoxLayout()
        frame.addWidget(QLabel("Debugger"))
        frame.addWidget(self.current_instruction, alignment=Qt.AlignCenter)
        memlayout = QHBoxLayout()
        reglayout = QGridLayout()
        for i in range(8):
            reglayout.addWidget(QLabel(f"D{i}"), i, 0)
            reglayout.addWidget(QLabel(f"A{i}"), i, 2)
            reglayout.addWidget(self.dregs[i], i, 1)
            reglayout.addWidget(self.aregs[i], i, 3)
        memlayout.addLayout(reglayout)
        # memory view
        self.memview = QTextEdit()
        self.memview.setReadOnly(True)
        self.memview.setFont(QFont("Courier", 10))
        self.memview.setLineWrapMode(QTextEdit.NoWrap)
        self.memview.setLineWrapColumnOrWidth(0)
        self.memview.setWordWrapMode(QTextOption.NoWrap)
        self.memview.setTabStopDistance(40)
        self.memview.setTabChangesFocus(True)
        self.memview.setAcceptRichText(False)
        self.memview.setPlaceholderText("Memory")
        memlayout.addWidget(self.memview)
        frame.addLayout(memlayout)
        lastregs = QHBoxLayout()
        lastregs.addWidget(QLabel("SR"))
        lastregs.addWidget(self.sreg)
        lastregs.addWidget(QLabel("PC"))
        lastregs.addWidget(self.pc)
        frame.addLayout(lastregs)
        buttons = QHBoxLayout()
        step_btn = QPushButton('Step', self)
        step_btn.clicked.connect(self.step)
        poweroff_btn = QPushButton('Poweroff', self)
        poweroff_btn.clicked.connect(self.poweroff)
        buttons.addWidget(step_btn)
        buttons.addWidget(poweroff_btn)
        frame.addLayout(buttons)
        self.update_ui()
        self.setLayout(frame)
    
    def load_file(self, fname: str):
        self.main_cpu.load_file(fname)
        self.update_ui()

    def update_ui(self):
        regs = self.main_cpu.get_regs()
        pc = self.main_cpu.cpu.r_pc()
        self.current_instruction.setText(self.main_cpu.get_current_line())
        for i in range(8):
            self.dregs[i].setText(f"0x{regs[f'd{i}']:08X}")
            self.aregs[i].setText(f"0x{regs[f'a{i}']:08X}")
        self.sreg.setText(f"{self.main_cpu.cpu.r_sr():016b}")
        self.pc.setText(f"{pc:08X}")
        self.memview.clear()
        radius = 0x80
        mem = self.main_cpu.get_mem(max(pc-radius//2,0), radius)
        step = 4
        for i in range(0, len(mem), step):
            self.memview.append(f"0x{i+pc-radius//2:08X} {mem[i:i+step].hex()}")
        self.memview.moveCursor(QTextCursor.Start)



    def step(self):
        self.main_cpu.step()
        self.update_ui()

    def poweroff(self):
        self.main_cpu.poweroff()
        self.status.config(text="Poweroff")
        self.after(2000, self.destroy)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    runner = Runner()
    runner.show()
    app.exec_()
