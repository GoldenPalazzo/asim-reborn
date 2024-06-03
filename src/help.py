#!/usr/bin/env python

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton

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

class About(QWidget):
    def __init__(self):
        super().__init__()
        frame = QVBoxLayout()
        self.setWindowTitle("About")
        image = QLabel()
        pmap = QPixmap(str(path_resolver.resolve_path("res/logo_256x256.png")))
        image.setPixmap(pmap)
        about = QLabel("<h1>ASIM Reborn - Simple multiplatform 68k IDE<br />"
                       "Version: 0.1</h1>\n"
                       "Made with blood by <a href=\"https://francescopalazzo.net\">@GoldenPalazzo</a>", self)
        about.setOpenExternalLinks(True)
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.close)
        image.setAlignment(Qt.AlignCenter)
        about.setAlignment(Qt.AlignCenter)
        frame.addWidget(image)
        frame.addWidget(about)
        frame.addWidget(quit_btn)
        frame.setAlignment(Qt.AlignCenter)
        self.setLayout(frame)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    help = About()
    help.show()
    sys.exit(app.exec())
