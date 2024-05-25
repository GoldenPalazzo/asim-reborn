#!/usr/bin/env python3
from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow, QMessageBox, QTextEdit, QFileDialog
from PySide6.QtGui import QFont, QFontDatabase, QSyntaxHighlighter, QTextCharFormat, QTextCursor, QKeySequence, QKeyEvent, QAction, QColor, QTextDocument
from PySide6.QtCore import QFileInfo, Qt, QEvent
import os.path
from typing import Optional, Union, Callable
import re
import sys

import compiler, run, opcodes, palettes, path_resolver

class M68KHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument):
        super().__init__(parent)
        self.init_formats(palettes.monokai)
    def init_formats(self, palette: palettes.Palette):
        opcode_format = QTextCharFormat()
        opcode_format.setForeground(QColor(palette.opcode))
        opcode_format.setFontWeight(QFont.Bold)
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor(palette.directive))
        directive_format.setFontWeight(QFont.Bold)
        registers_format = QTextCharFormat()
        registers_format.setForeground(QColor(palette.registers))
        registers_format.setFontWeight(QFont.Bold)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(palette.comments))
        comment_format.setFontItalic(True)
        comment_format.setFontWeight(QFont.Light)
        character_format = QTextCharFormat()
        character_format.setForeground(QColor(palette.character))
        opcode_re= re.compile(
                opcodes.regex_generator(opcodes.opcodes),
                re.IGNORECASE)
        directive_re = re.compile(
                opcodes.regex_generator(opcodes.directives),
                re.IGNORECASE)
        registers_re = re.compile(
                opcodes.regex_generator(opcodes.registers),
                re.IGNORECASE)
        comment_re = re.compile(r';.*')
        character_re = re.compile(r"'.'")
        string_re = re.compile(r'"[^"]*"')
        self.expr_form_couples = [(opcode_re, opcode_format),
                                   (directive_re, directive_format),
                                   (registers_re, registers_format),
                                   (comment_re, comment_format),
                                   (character_re, character_format),
                                   (string_re, character_format)]


    def highlightBlock(self, text):
        for expression, format in self.expr_form_couples:
            for match in re.finditer(expression, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)
        
class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.tab_size = 4
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            spaces = self.tab_size - self.textCursor().columnNumber() % self.tab_size
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.KeyboardModifiers(e.nativeModifiers()),
                              " "*spaces)
        super().keyPressEvent(e)
        #print(self.textCursor().columnNumber())


class IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compiler = compiler.Compiler()
        self.runner = run.Runner()
        self.current_file: Optional[str] = None
 
        self.init_ui()
        self.highlighter = M68KHighlighter(self.text_edit.document())

    def init_ui(self):
        self.text_edit = CustomTextEdit()
        self.text_edit.tab_size = 8
        font_path = str(path_resolver.resolve_path("res/MonoLisa-Regular.ttf"))
        default_font = "MonoLisa"
        found_font = QFontDatabase.addApplicationFont(font_path)
        if found_font == -1:
            print("MonoLisa font not found, fallbacking Monospace")
            default_font = "Monospace"
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(lambda: self.update_window_title(True))

        self.setGeometry(100, 100, 800, 600)
        self.update_window_title(False)
        self.text_edit.setStyleSheet("QTextEdit { "
                                     f"font-family: '{default_font}'; "
                                     "font-size: 16pt; "
                                     f"background-color: #{palettes.monokai.background:X}; "
                                     f"color: #{palettes.monokai.text:X}; "
                           " }")
 
        # Compilation dock
        self.dock = QDockWidget("Compiler log", self)
        self.dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.compiler_widget = QTextEdit()
        self.compiler_widget.setReadOnly(True)
        self.compiler_widget.setText("Compiler ready.")
        self.dock.setWidget(self.compiler_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

        self.initMenuBar()
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
        # Window menu
        window_menu = self.menuBar().addMenu('Window')
        window_menu.addAction(self.dock.toggleViewAction())


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
        msg = self.compiler.compile(self.current_file)
        self.compiler_widget.setText(msg)

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
    sys.exit(app.exec())
