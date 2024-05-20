#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import logging
import os
import subprocess
import sys
from typing import Any, Optional, Dict, Tuple, Union # "tuple" works from 3.9 onwards

from PySide2.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog
from PySide2.QtGui import QFont, QTextCursor

import compiler, ide, m68k, run

ftypes = [
    ('SREC files', '*.srec *.SREC *.h68 *.H68'),
    ('All files', '*'), 
]

#logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

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
