#!/usr/bin/env python3
from PySide2.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog
from PySide2.QtGui import QFont, QTextCursor
import os.path
from typing import Optional, Union, Callable
import sys

import compiler, run

class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.compiler = compiler.Compiler()
        self.runner = run.Runner()

        self.current_file: Optional[str] = None

    def init_ui(self):
        self.text_edit = QTextEdit()
        self.text_edit.setTabStopWidth(40)
        self.text_edit.setFont(QFont('Monospace', 12))
        self.setCentralWidget(self.text_edit)
        self.initMenuBar()

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('IDE')
        self.show()
        
    def initMenuBar(self):
        # File menu
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_file)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)

        fileMenu = self.menuBar().addMenu('File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)
        fileMenu.addAction(exit_action)

        # Run menu
        compile_action = QAction('Compile program', self)
        compile_action.triggered.connect(self.compile_file)
        run_action = QAction('Run program', self)
        run_action.triggered.connect(self.run_file)
        run_menu = self.menuBar().addMenu('Run')
        run_menu.addAction(compile_action)
        run_menu.addAction(run_action)


    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        print(fname)
        if fname:
            with open(fname, 'r') as file:
                self.text_edit.setText(file.read())
            self.current_file = fname

    def save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', '',
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        if fname:
            with open(fname, 'w') as file:
                file.write(self.text_edit.toPlainText())
            self.current_file = fname

    def compile_file(self):
        print("Clicked compile")
        print(f"Compiling {self.current_file}")
        self.compiler.compile(self.current_file)

    def run_file(self):
        if self.current_file != None:
            binary = os.path.splitext(self.current_file)[0] + ".h68"
            self.runner.load_file(binary)
            self.runner.show()

    def close_event(self, event):
        event.accept()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = IDE()
    sys.exit(app.exec_())
