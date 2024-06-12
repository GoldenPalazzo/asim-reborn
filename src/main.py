#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

from PySide6.QtWidgets import QApplication

import compiler, ide, m68k, config

ftypes = [
    ('SREC files', '*.srec *.SREC *.h68 *.H68'),
    ('All files', '*'),
]

#logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

def main_old():
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
        sys.exit(app.exec())
        #app = ASIMWindow(main_cpu)
        #app.mainloop()

def main():
    cfg = config.Config().config
    app = QApplication(sys.argv)
    dark_stylesheet = """
        QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QScrollArea {
            background-color: #2E2E2E;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 18px;
        }
        QPushButton {
            background-color: #4A4A4A;
            color: #FFFFFF;
            border: 1px solid #5A5A5A;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #5A5A5A;
        }
    """
    app.setStyleSheet(dark_stylesheet)
    main_window = ide.IDE(sys.argv[1] if len(sys.argv) > 1 else None,
                          config=cfg)
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
