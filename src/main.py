#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import sys

from PySide6.QtWidgets import QApplication

import compiler, ide, m68k

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
        sys.exit(app.exec())
        #app = ASIMWindow(main_cpu)
        #app.mainloop()

def main():
    app = QApplication(sys.argv)
    main_window = ide.IDE(sys.argv[1] if len(sys.argv) > 1 else None)
    comp = compiler.Compiler()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
