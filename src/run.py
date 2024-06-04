#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import sys
from typing import Optional, Union, Callable, List
import PySide6

from PySide6.QtWidgets import QApplication, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QPlainTextEdit, QFileDialog, QVBoxLayout, QWidget, QScrollArea
from PySide6.QtGui import QFont, QRegularExpressionValidator, QTextCursor, QAction, QTextOption, QValidator
from PySide6.QtCore import QRegularExpression, Qt

import m68k

admitted_modes = [
            "Unsigned byte",
            "Signed byte",
            "Hex byte",
            "Unsigned word",
            "Signed word",
            "Hex word",
            "Unsigned long",
            "Signed long",
            "Hex long",
            "ASCII char",
            "Null termined string"]

class Variable(QWidget):
    def __init__(self, addr: int, name: str = ""):
        super().__init__()
        self.addr = addr
        self.name = name
        addr_label = QLabel(f"{self.name} 0x{addr:08X}")
        self.val_label = QLabel("0")
        self.mode_select = QComboBox()
        self.mode_select.addItems(admitted_modes)
        #self.mode_select.currentIndexChanged.connect(lambda: self.update_val(self.val))
        layout = QHBoxLayout()
        layout.addWidget(addr_label)
        layout.addWidget(self.mode_select)
        layout.addWidget(self.val_label)
        self.del_btn = QPushButton('Delete', self)
        layout.addWidget(self.del_btn)
        self.setLayout(layout)

    def update_val(self, val: str):
        self.val_label.setText(val)

    def get_mode(self) -> str:
        return self.mode_select.currentText().lower()


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
        self.watched_vars: list[Variable]  = []

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
        frame.addLayout(reglayout, 4, 0, 1, -1)
        # memory view
        self.memview = QPlainTextEdit()
        self.memview.setReadOnly(True)
        self.memview.setFont(QFont("MonoLisa"))
        self.memview.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.memview.setWordWrapMode(QTextOption.NoWrap)
        self.memview.setTabStopDistance(40)
        self.memview.setTabChangesFocus(True)
        self.memview.setPlaceholderText("Memory")
        frame.addWidget(self.memview, 1, 0, 1, 1)

#         self.varwatch = QPlainTextEdit()
        # self.varwatch.setReadOnly(True)
        # self.varwatch.setFont(QFont("MonoLisa"))
        # self.varwatch.setLineWrapMode(QPlainTextEdit.NoWrap)
        # self.varwatch.setWordWrapMode(QTextOption.NoWrap)
        # self.varwatch.setTabStopDistance(40)
        # self.varwatch.setTabChangesFocus(True)
#         self.varwatch.setPlaceholderText("Watched variables")
        scrollvars = QScrollArea()
        scrollvars.setWidgetResizable(True)
        dummy_widget = QWidget()
        self.varwatch = QVBoxLayout()
        dummy_widget.setLayout(self.varwatch)
        scrollvars.setWidget(dummy_widget)
        frame.addWidget(scrollvars, 1, 1, 1, 1)

        seeker = QHBoxLayout()
        self.seekline = QLineEdit()
        self.seekline.setFont(QFont("MonoLisa"))
        self.seekline.setMaxLength(8)
        address_regexp = QRegularExpression("^[0-9a-fA-F]{1,8}$")
        seekvalidator = QRegularExpressionValidator(address_regexp, self.seekline)
        self.seekline.setValidator(seekvalidator)
        self.seekline.setPlaceholderText("Seek address in hex")
        self.seekline.textChanged.connect(self.update_memview)
        seeker.addWidget(self.seekline)
        self.seek_sp = QPushButton("Seek SP", self)
        self.seek_sp.clicked.connect(lambda: self.seekline.setText(f"{self.main_cpu.cpu.r_ax(7):08X}"))
        seeker.addWidget(self.seek_sp)
        frame.addLayout(seeker, 2, 0, 1, 1)

        watchvarbtns = QHBoxLayout()
        self.watchvaraddr = QLineEdit()
        self.watchvaraddr.setFont(QFont("MonoLisa"))
        self.watchvaraddr.setMaxLength(8)
        watchvarvalidator = QRegularExpressionValidator(address_regexp, self.watchvaraddr)
        self.watchvaraddr.setValidator(watchvarvalidator)
        self.watchvaraddr.setPlaceholderText("Watch var address")
        add_btn = QPushButton('Add', self)
        clr_btn = QPushButton('Clear', self)
        add_btn.clicked.connect(lambda: self.add_var())
        clr_btn.clicked.connect(self.clr_var)
        watchvarbtns.addWidget(add_btn)
        watchvarbtns.addWidget(clr_btn)
        frame.addWidget(self.watchvaraddr, 2, 1, 1, 1)
        frame.addLayout(watchvarbtns, 3, 1, 1, 1)

        buttons = QHBoxLayout()
        step_btn = QPushButton('Step', self)
        step_btn.clicked.connect(self.step)
        self.poweroff_btn = QPushButton('Stop', self)
        self.poweroff_btn.clicked.connect(self.poweroff)
        poweroff_action = QAction('Stop', self)
        poweroff_action.triggered.connect(self.poweroff)
        poweroff_action.setShortcut('F8')
        buttons.addWidget(step_btn)
        buttons.addWidget(self.poweroff_btn)
        frame.addLayout(buttons, 5, 0, 1, -1)
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
            stack_pointer = self.main_cpu.cpu.r_ax(7)
            if current_addr <= stack_pointer and current_addr+step > stack_pointer:
                self.memview.insertPlainText(" <-- stack pointer")
            self.memview.insertPlainText("\n")
        self.memview.moveCursor(QTextCursor.Start)

        for var in self.watched_vars:
            self.update_var(var)

    def update_var(self, var: Variable) -> bool:
        val = ""
        addr = var.addr
        mode = var.get_mode()
        try:
            if mode.endswith("byte"):
                val = int.from_bytes(
                        self.main_cpu.get_mem(addr, 1),
                        byteorder='big',
                        signed=mode.startswith("s"))
                val = f"{val:02X}" if mode.startswith("h") else str(val)
            elif mode.endswith("char"):
                val = self.main_cpu.get_mem(addr, 1).decode('ascii')
            elif mode.endswith("word"):
                val = int.from_bytes(
                        self.main_cpu.get_mem(addr, 2),
                        byteorder='big',
                        signed=mode.startswith("s"))
                val = f"{val:04X}" if mode.startswith("h") else str(val)
            elif mode.endswith("long"):
                val = int.from_bytes(
                        self.main_cpu.get_mem(addr, 4),
                        byteorder='big',
                        signed=mode.startswith("S"))
                val = f"{val:08X}" if mode.startswith("h") else str(val)
            elif mode.endswith("string"):
                val = b''
                offset = 0
                while True:
                    c = self.main_cpu.get_mem(addr+offset, 1)
                    if c == b'\x00':
                        break
                    val += c
                    offset += 1
                val = val.decode('ascii')
        except ValueError:
            val = "ERROR: Invalid address"

        if val != "":
            var.update_val(val)
            return True
        return False


    def add_var(self, addr: Optional[int] = None, name: str = ""):
        if addr == None:
            addr = int(self.watchvaraddr.text(), 16)
        if name == "":
            name = f"userdef_{len(self.watched_vars)}"
        print(f"Adding var {addr:08X}")
        var = Variable(addr, name)
        self.watched_vars.append(var)
        var.mode_select.currentIndexChanged.connect(lambda: self.update_var(var))
        var.del_btn.clicked.connect(lambda: self.del_var(var))
        self.watchvaraddr.clear()
        self.varwatch.addWidget(var)

    def del_var(self, var: Variable):
        self.watched_vars.remove(var)
        var.deleteLater()
        self.update_memview()

    def clr_var(self):
        for var in self.watched_vars:
            self.varwatch.removeWidget(var)
            var.deleteLater()
        self.watched_vars.clear()
        self.update_memview()

    def step(self):
        self.main_cpu.step()
        self.update_ui()

    def poweroff(self):
        self.main_cpu.poweroff()
        self.current_instruction.setText("Stopped execution")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    runner = Runner()
    runner.show()
    app.exec_()
