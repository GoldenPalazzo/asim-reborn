#!/usr/bin/env python

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel

import path_resolver

class Help(QWidget):
    def __init__(self):
        super().__init__()
        frame = QVBoxLayout()
        self.setWindowTitle("Help")
        self.resize(400, 300)
        doc_url = str(path_resolver.resolve_path("res/docs.html"))
        text = open(doc_url).read()
        docs = QLabel(text)
        frame.addWidget(docs)
        self.setLayout(frame)
        self.show()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    help = Help()
    sys.exit(app.exec())
