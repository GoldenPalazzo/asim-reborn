#!/usr/bin/env python3

import sys
from typing import Optional, Union, Callable, List
import PySide6

from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QPlainTextEdit, QFileDialog, QVBoxLayout, QWidget
from PySide6.QtGui import QFont, QRegularExpressionValidator, QTextCursor, QAction, QTextOption, QValidator
from PySide6.QtCore import QRegularExpression, Qt

import m68k

class Runner(QWidget):


    def __init__(self):
        super().__init__()
        self.main_cpu = m68k.m68k()
        self.dregs: List[QLabel] = [QLabel(f"0x{0:08X}") for _ in range(8)]
        self.aregs: List[QLabel] = [QLabel(f"0x{0:08X}") for _ in range(8)]
        self.sreg = QLabel(f"{0:016b}")
        self.pc = QLabel(f"{0:08X}")
        self.sreg.setFont(QFont("MonoLisa"))
        self.pc.setFont(QFont("MonoLisa"))
        self.current_instruction = QLabel("")
        self.current_instruction.setFont(QFont("MonoLisa", 18))
        self.current_instruction.setAlignment(Qt.AlignCenter)

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        #self.setWindowTitle('Debugger')
        frame = QGridLayout()
        frame.setSpacing(10)
        #frame.addWidget(self.current_instruction, 1, 0, 1, -1)
        reglayout = QGridLayout()
        for i in range(8):
            reglayout.addWidget(QLabel(f"D{i}"), i, 0)
            reglayout.addWidget(QLabel(f"A{i}"), i, 2)
            reglayout.addWidget(self.dregs[i], i, 1)
            reglayout.addWidget(self.aregs[i], i, 3)
            self.dregs[i].setFont(QFont("MonoLisa"))
            self.aregs[i].setFont(QFont("MonoLisa"))

        reglayout.addWidget(QLabel("SR"))
        reglayout.addWidget(self.sreg)
        reglayout.addWidget(QLabel("PC"))
        reglayout.addWidget(self.pc)
        frame.addLayout(reglayout, 3, 0, 1, -1)
        # memory view
        self.memview = QPlainTextEdit()
        self.memview.setReadOnly(True)
        self.memview.setFont(QFont("MonoLisa"))
        self.memview.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.memview.setWordWrapMode(QTextOption.NoWrap)
        self.memview.setTabStopDistance(40)
        self.memview.setTabChangesFocus(True)
        self.memview.setPlaceholderText("Memory")
        frame.addWidget(self.memview, 1, 0, 1, -1)

        self.seekline = QLineEdit()
        self.seekline.setFont(QFont("MonoLisa"))
        self.seekline.setMaxLength(8)
        address_regexp = QRegularExpression("^[0-9a-fA-F]{1,8}$")
        validator = QRegularExpressionValidator(address_regexp, self.seekline)
        self.seekline.setValidator(validator)
        self.seekline.setPlaceholderText("Seek address in hex")
        self.seekline.textChanged.connect(self.update_memview)
        frame.addWidget(self.seekline, 2, 0, 1, -1)

        buttons = QHBoxLayout()
        self.step_btn = QPushButton('Step', self)
        self.step_btn.clicked.connect(self.step)
        self.poweroff_btn = QPushButton('Poweroff', self)
        self.poweroff_btn.clicked.connect(self.poweroff)
        poweroff_action = QAction('Stop', self)
        poweroff_action.triggered.connect(self.poweroff)
        poweroff_action.setShortcut('F8')
        buttons.addWidget(self.step_btn)
        buttons.addWidget(self.poweroff_btn)
        frame.addLayout(buttons, 4, 0, 1, -1)
        #frame.setRowStretch(1, 1)
        self.update_ui()
        self.setLayout(frame)
    
    def load_file(self, fname: str):
        self.main_cpu.load_file(fname)
        self.update_ui()

    def update_ui(self):
        self.update_regs()
        self.update_memview()

    def update_regs(self):
        regs = self.main_cpu.get_regs()
        pc = self.main_cpu.cpu.r_pc()
        self.current_instruction.setText(self.main_cpu.get_current_line())
        for i in range(8):
            self.dregs[i].setText(f"0x{regs[f'd{i}']:08X}")
            self.aregs[i].setText(f"0x{regs[f'a{i}']:08X}")
        self.sreg.setText(f"{self.main_cpu.format_sreg(self.main_cpu.cpu.r_sr())}")
        self.pc.setText(f"0x{pc:08X}")

    def update_memview(self):
        pc = self.main_cpu.cpu.r_pc()
        if self.seekline.text() != "":
            pc = int(self.seekline.text(), 16)
        self.memview.clear()
        radius = 0x80
        start = max(pc-radius//2,0)
        mem = self.main_cpu.get_mem(start, radius)
        step = 4
        for i in range(0, len(mem), step):
            current_addr = i+start
            current_mem = mem[i:i+step].hex()
            self.memview.moveCursor(QTextCursor.End)
            #self.memview.insertPlainText(f"0x{i+start:08X} {mem[i:i+step].hex()}\n")
            self.memview.insertPlainText(f"0x{current_addr:08X} "
                                         f"{' '.join(current_mem[j:j+2] \
                                            for j in range(0, len(current_mem), 2))}")
            if current_addr == self.main_cpu.cpu.r_ax(7):
                self.memview.insertPlainText(" <-- stack pointer")
            self.memview.insertPlainText("\n")
        self.memview.moveCursor(QTextCursor.Start)



    def step(self):
        self.main_cpu.step()
        self.update_ui()

    def poweroff(self):
        self.main_cpu.poweroff()
        self.current_instruction.setText("Powered off")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    runner = Runner()
    runner.show()
    app.exec_()
