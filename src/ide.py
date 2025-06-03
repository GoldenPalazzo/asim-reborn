#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import os
import os.path
from typing import Optional, Union, Callable
import re
import sys

from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow, \
    QMessageBox, QTextEdit, QPlainTextEdit, QFileDialog, QTabWidget, QWidget
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QSyntaxHighlighter, \
    QTextFormat, QTextCharFormat, QTextCursor, QKeySequence, QKeyEvent, \
    QAction, QColor, QTextDocument, QIcon, QDrag
from PySide6.QtCore import QFileInfo, QTimer, Qt, QEvent, QSize, QRect

from compiler import VasmCompiler
import run, opcodes, palettes, path_resolver, help, screen

class LineNumber(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class M68KHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument, palette: palettes.Palette = palettes.monokai):
        super().__init__(parent)
        self.init_formats(palette)
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
        comment_re = re.compile('(?<![\'"])[*;]([^\'"]*)(?![\'"])')
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

class IDETextEdit(QPlainTextEdit):
    def __init__(self,
                 palette: palettes.Palette = palettes.monokai,
                 font: str = "Monospace",
                 font_size: int = 16):
        super().__init__()
        self.ui_palette = palette
        self.tab_size = 8
        self.setFont(QFont(font, font_size))
        self.setStyleSheet("QPlainTextEdit { "
            # f"font-family: '{self.font}'; "
            # f"font-size: {self.font_size}pt; "
            f"background-color: {self.ui_palette.background}; "
            f"color: {self.ui_palette.text}; "
        " }")


        self.setCursorWidth(5)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.lineNumberArea = LineNumber(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            spaces = self.tab_size - self.textCursor().columnNumber() % self.tab_size
            e = QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.KeyboardModifiers(e.nativeModifiers()),
                              " "*spaces)
        super().keyPressEvent(e)
        self.highlightCurrentLine()
        #print(self.textCursor().columnNumber())

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#333333"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(self.ui_palette.text))
                painter.drawText(0, int(top), self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self): # currently only highlights cursor's line
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(self.ui_palette.highlight))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


class IDE(QMainWindow):
    def __init__(self, file: Optional[str] = None, config: dict = {}):
        super().__init__()
        # Config
        editor_config = config.get("editor", {})
        self.font = editor_config.get("font-family", self.setup_monolisa())
        self.font_size = int(editor_config.get("font-size", 16))
        self.ui_palette = palettes.dict_to_palette(editor_config.get("palette", {}),
                                                palettes.monokai)
        icon = QIcon()
        icon.addFile(str((path_resolver.base_path/"res"/"logo_256x256.ico").resolve()),
                     QSize(256, 256))
        icon.addFile(str((path_resolver.base_path/"res"/"logo_24x24.ico").resolve()),
                     QSize(24, 24))
        self.setWindowIcon(icon)
        self.setWindowTitle("ASIM Reborn")
        # Classes
        self.compiler = VasmCompiler()
        self.runner = run.Runner()
        self.documentation = help.Help()
        self.about = help.About()

        #State
        self.current_file: str = ""
        self.current_lst: dict[int, int] = {}

        self.init_ui()
        self.runner_polling = QTimer()
        self.runner_polling.timeout.connect(self.runner.update_ui)
        self.runner_polling.timeout.connect(self.update_highlighted_running_line)

        if file:
            self.current_file = file
            self.load_file(file)

    def setup_monolisa(self) -> str:
        font_path = str((path_resolver.base_path/"res"/"MonoLisa-Regular.ttf").resolve())
        found_font = QFontDatabase.addApplicationFont(font_path)
        if found_font == -1:
            return "Monospace"
        return "MonoLisa"

    def init_ui(self):
        self.text_edit = IDETextEdit(self.ui_palette, self.font, self.font_size)
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.highlighter = M68KHighlighter(self.text_edit.document(), self.ui_palette)

        self.setGeometry(100, 100, 800, 600)
        self.update_window_title(False)

        # Compilation dock
        self.dock = QDockWidget("Compiler log", self)
        self.dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.compiler_widget = QPlainTextEdit()
        self.compiler_widget.setReadOnly(True)
        self.compiler_widget.setPlainText("Compiler ready.")
        self.dock.setWidget(self.compiler_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        self.dock.hide()

        #Execution dock
        self.exec_dock = QDockWidget("Execution", self)
        self.exec_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        # sidetabs.addTab(self.runner, "Runner")
        # sidetabs.addTab(self.documentation, "Documentation")
        # sidetabs.addTab(screen.Screen(self.runner.main_cpu), "Screen")
        # sidetabs.tabBarDoubleClicked.connect(self.detach_tab)
        # self.side_dock.setWidget(sidetabs)
        self.exec_dock.setWidget(self.runner)
        self.addDockWidget(Qt.RightDockWidgetArea, self.exec_dock)

        # Docs dock
        self.docs_dock = QDockWidget("Documentation", self)
        self.docs_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.docs_dock.setWidget(self.documentation)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docs_dock)
        self.docs_dock.hide()

        # Screen dock
        # self.screen_dock = QDockWidget("Screen", self)
        # self.screen_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        # self.screen_dock.setWidget(screen.Screen(self.runner.main_cpu, refr_rate=24))
        # self.addDockWidget(Qt.RightDockWidgetArea, self.screen_dock)

        self.runner.poweroff_btn.clicked.connect(self.stop_highlighting)

        self.tabifyDockWidget(self.exec_dock, self.docs_dock)
        # self.tabifyDockWidget(self.exec_dock, self.screen_dock)

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
        compile_action = QAction('Compile', self)
        compile_action.setShortcut(QKeySequence("F5"))
        compile_action.triggered.connect(self.compile_file)
        run_action = QAction('Run', self)
        run_action.triggered.connect(self.runner.run)
        run_action.setShortcut(QKeySequence("F6"))
        run_debug_action = QAction('Run with debug', self)
        run_debug_action.triggered.connect(self.execute_file)
        run_debug_action.setShortcut(QKeySequence("F7"))
        step_action = QAction('Step', self)
        step_action.triggered.connect(self.runner.step)
        step_action.setShortcut(QKeySequence("F8"))
        stop_action = QAction('Stop', self)
        stop_action.triggered.connect(self.stop)
        stop_action.setShortcut(QKeySequence("F9"))
        run_menu = self.menuBar().addMenu('Run')
        run_menu.addAction(compile_action)
        run_menu.addAction(run_action)
        run_menu.addAction(run_debug_action)
        run_menu.addAction(step_action)
        run_menu.addAction(stop_action)
        # Window menu
        docks_menu = self.menuBar().addMenu('Window')
        docks_menu.addAction(self.dock.toggleViewAction())
        docks_menu.addAction(self.exec_dock.toggleViewAction())
        docks_menu.addAction(self.docs_dock.toggleViewAction())
        # window_menu.addAction(self.screen_dock.toggleViewAction())
        # Help menu
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction(about_action)

    def on_text_changed(self):
        self.update_window_title(True)
        self.stop_highlighting()

    def new_file(self):
        self.text_edit.clear()
        self.current_file = None
        self.update_window_title(False)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', '',
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        #print(fname)
        if fname:
            self.load_file(fname)

    def load_file(self, fname: str):
        with open(fname, 'r') as file:
            self.text_edit.setPlainText(file.read())
        self.current_file = fname
        self.update_window_title(False)

    def save_file(self) -> bool:
        if not self.current_file:
            return self.save_as_new()
        with open(self.current_file, 'w') as file:
            file.write(self.text_edit.toPlainText())
        self.update_window_title(False)
        return True

    def save_as_new(self) -> bool:
        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', '',
                                                  'M68K assembler (*.a68 .A68)'
                                                  ';;All Files (*.*)')
        if fname:
            if os.path.splitext(fname)[1] == '':
                fname += '.a68'
            self.current_file = fname
            return self.save_file()
        return False

    def compile_file(self):
        #print("Clicked compile")
        if self.current_file == "":
            if self.text_edit.document().isEmpty():
                QMessageBox.warning(self, "Error", "No file to compile.")
                return
            else:
                if not self.save_as_new():
                    QMessageBox.warning(self, "Error", "Could not save file")
                    return
        #print(f"Compiling {self.current_file}")
        out, err = self.compiler.compile(self.current_file)
        self.dock.show()
        self.compiler_widget.setPlainText(out + err)
        if err != "":
            errors = self.compiler.get_error_lines(err)
            #print(f"errors in {errors}")
            self.highlight_errors(errors)

    def parse_lst(self, path: str, import_vars: bool = True):
        valid_line_re = re.compile(r'^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{8}$')
        valid_symbol_re = re.compile(r'.*\s+A:[0-9A-Fa-f]{8}')
        with open(path, 'r') as file:
            lines = file.readlines()
            symbols_mode = False
            for i, line in enumerate(lines):
                # pair: address -> line number
                #print(f"Line {i}: {line}")
                if line.startswith("Symbols by name"):
                    symbols_mode = True
                    continue
                s = line.split()
                if symbols_mode:
                    if line == "\n":
                        print("End of symbols")
                        symbols_mode = False
                        break
                    if len(s) < 2:
                        continue
                    if not valid_symbol_re.match(line):
                        continue
                    address = int(s[1][2:], 16)
                    row = i
                    #print(f"Address: {address}, line: {row}")
                    if import_vars:
                        self.runner.add_var(address, s[0])
                    continue
                if len(s) < 3:
                    continue
                if not valid_line_re.match(s[0]):
                    continue
                address = int(s[0][3:], 16)
                row = int(s[2][:-1])
                #print(s[2].lower())
                #print(f"Address: {address}, line: {row}")
                self.current_lst[address] = row

    def execute_file(self):
        #check is .lst file exists
        if self.current_file == None:
            QMessageBox.warning(self, "Error", "No file to run.")
            return
        lst = ""
        for ext in (".lst", ".LIS"):
            lst = os.path.splitext(self.current_file)[0] + ext
            if os.path.exists(lst):
                lst = os.path.splitext(self.current_file)[0] + ext
                import_vars = QMessageBox.question(self, "Import variables",
                                     "Do you want to import variables from the lst file?") \
                                == QMessageBox.Yes
                print(import_vars)
                self.parse_lst(lst, import_vars)
                self.runner_polling.start(500)
                break
        else:
            QMessageBox.warning(self, "Error", "No lst file to run. Line highlighting disabled.")
            self.runner_polling.stop()
        for ext in (".h68", ".H68"):
            bin = os.path.splitext(self.current_file)[0] + ext
            if os.path.exists(bin):
                self.runner.load_file(bin)
                self.exec_dock.show()
                break
        else:
            QMessageBox.warning(self, "Error", "No binary file to run.")
            self.runner_polling.stop()
            return

    def close_event(self, event):
        event.accept()

    def update_window_title(self, modified: bool):
        self.setWindowTitle('IDE - '
                            f'{self.current_file if self.current_file else "untitled"}'
                            f'{"*" if modified else ""}')

    def update_highlighted_running_line(self):
        pc = self.runner.main_cpu.cpu.r_pc()
        #print("Running line: ", self.current_lst.get(pc, -1))
        line = self.current_lst.get(pc, 0)-1
        #print(line)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#64fffd8d"))
        #fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        #cursor = self.text_edit.textCursor()
        cursor = QTextCursor(self.text_edit.document().findBlockByLineNumber(line))
        cursor.select(QTextCursor.LineUnderCursor)
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format = fmt
        self.text_edit.setExtraSelections([selection])
        #cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

    def highlight_errors(self, errors: list[int]):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#ff6464"))
        selections = []
        for line in errors:
            cursor = QTextCursor(self.text_edit.document().findBlockByLineNumber(line-1))
            cursor.select(QTextCursor.LineUnderCursor)
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = fmt
            selections.append(selection)
        self.text_edit.setExtraSelections(selections)

    def stop(self):
        self.stop_highlighting()
        self.runner.poweroff()

    def stop_highlighting(self):
        self.runner_polling.stop()
        self.text_edit.setExtraSelections([])

    def show_about(self):
        self.about.show()

    def show_update_message(self, version: str):
        QMessageBox.information(self, "Update available",
                                f"New version {version} is available."
                                "<a href=\"https://github.com/GoldenPalazzo/asim-reborn/releases\">")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = IDE()
    sys.exit(app.exec())
