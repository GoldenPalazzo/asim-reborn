from PySide6.QtGui import QColor

class Palette:
    def __init__(self,
                 background: int,
                 text: int,
                 character: int,
                 directive: int,
                 opcode: int,
                 registers: int,):
        self.background = (background)
        self.text= (text)
        self.character = (character)
        self.directive = (directive)
        self.opcode = (opcode)
        self.registers = (registers)

monokai = Palette(0x2e2e2e, 
                  0xd6d6d6,
                  0xe5b567,
                  0xb05279,
                  0x6c99bb,
                  0xb4d273)
