#!/usr/bin/env python

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

import path_resolver

class Help(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Help")
        self.resize(400, 300)
        frame = QVBoxLayout()
        self.webview = QWebEngineView()
        doc_url = str(path_resolver.resolve_path("res/docs.html"))
        print(doc_url)
        self.webview.load(QUrl.fromLocalFile(doc_url))
        frame.addWidget(self.webview)
        self.setLayout(frame)
        self.show()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    help = Help()
    sys.exit(app.exec())
