from PySide6.QtGui import QColor

class Palette:
    def __init__(self, background: int, foreground: int):
        self.background = QColor(background)
        self.foreground = QColor(foreground)

monokai = Palette(0x2e2e2e, 0xd6d6d6)
