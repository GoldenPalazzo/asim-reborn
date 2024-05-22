#!/usr/bin/env python3
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog
from PySide6.QtGui import QFont, QTextCursor, QKeySequence, QKeyEvent, QAction
from PySide6.QtCore import Qt, QEvent
import os.path
from typing import Optional, Union, Callable
import sys

import compiler, run

class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.tab_size = 4
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.KeyboardModifiers(e.nativeModifiers()),
                              " "*self.tab_size)
        super().keyPressEvent(e)


class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compiler = compiler.Compiler()
        self.runner = run.Runner()
        self.current_file: Optional[str] = None
        self.init_ui()

    def init_ui(self):
        self.text_edit = CustomTextEdit()
        self.text_edit.tab_size = 8
        self.text_edit.setFont(QFont('Courier', 12))
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(lambda: self.update_window_title(True))
        self.initMenuBar()

        self.setGeometry(100, 100, 800, 600)
        self.update_window_title(False)
        self.show()
        
    def initMenuBar(self):
        # File menu
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_file)
        new_action.setShortcut(QKeySequence.New)
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut(QKeySequence.Open)
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut(QKeySequence.Save)
        save_as_new_action = QAction('Save as new', self)
        save_as_new_action.triggered.connect(self.save_as_new)
        save_as_new_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)

        fileMenu = self.menuBar().addMenu('File')
        fileMenu.addAction(new_action)
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)
        fileMenu.addAction(save_as_new_action)
        fileMenu.addAction(exit_action)
        # Run menu
        compile_action = QAction('Compile program', self)
        compile_action.triggered.connect(self.compile_file)
        run_action = QAction('Run program', self)
        run_action.triggered.connect(self.run_file)
        run_action.setShortcut(QKeySequence("F5"))
        run_menu = self.menuBar().addMenu('Run')
        run_menu.addAction(compile_action)
        run_menu.addAction(run_action)

    def new_file(self):
        self.text_edit.clear()
        self.current_file = None
        self.update_window_title(False)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        print(fname)
        if fname:
            with open(fname, 'r') as file:
                self.text_edit.setText(file.read())
            self.current_file = fname
            self.update_window_title(False)

    def save_file(self):
        if not self.current_file:
            self.save_as_new()
            return
        with open(self.current_file, 'w') as file:
            file.write(self.text_edit.toPlainText())
        self.update_window_title(False)

    def save_as_new(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', '',
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        if fname:
            if os.path.splitext(fname)[1] == '':
                fname += '.a68'
            self.current_file = fname
            self.save_file()

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

    def update_window_title(self, modified: bool):
        self.setWindowTitle('IDE - '
                            f'{self.current_file if self.current_file else "untitled"}'
                            f'{"*" if modified else ""}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = IDE()
    sys.exit(app.exec_())
