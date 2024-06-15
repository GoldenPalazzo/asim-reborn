#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import time
from typing import Optional

from PySide6.QtCore import QRunnable, QThreadPool, Qt, QSize, QTimer, QObject, Signal
from PySide6.QtGui import QImage, qRgb, QPixmap, QPainter, QResizeEvent, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy

import m68k


DEFAULT_ADDRESS     = 0x020000
SECOND_FRAME_OFFSET = 0x010000
PALETTE_OFFSET      = 0x020000
STATUS_OFFSET       = 0x020400

ACK_MASK            = 0b10000000
FILL_SCREEN_MASK    = 0b01000000

class ImageComposer(QRunnable):
    def __init__(self, image: QImage, canvas:QLabel, cpu: m68k.m68k, addr, width, height, refr_rate:int = 1):
        super().__init__()
        self._abort = False
        self.image = image
        self.canvas = canvas
        self.scr_width = width
        self.scr_height = height

        self.cpu = cpu
        self.addr = addr
        self.refr_rate = refr_rate

    def abort(self):
        self._abort = True

    def run(self):
        while not self._abort:
            self.update_image()
            time.sleep(1/self.refr_rate)

    def update_image(self):
        """Reads from self.addr WxH argb bytes and updates the image"""
        if not self.cpu.get_power_status():
            self.fill_screen(QColor(255, 255, 255))
        else:
            fill_flag = self.get_sr()["fill"]
            if fill_flag:
                color = self.get_color(self.cpu.get_mem(self.addr, 1)[0])
                self.fill_screen(color)
            else:
                t = time.time()
                self.read_framebuffer()
                print(f"Read framebuffer in {time.time() - t} seconds")
        self.canvas.setPixmap(QPixmap.fromImage(self.image))

    def get_color(self, palette_index: int) -> QColor:
        """Returns the color at the palette index"""
        color = self.cpu.get_mem(self.addr + PALETTE_OFFSET + palette_index * 3, 3)
        return QColor(color[0], color[1], color[2])

    def check_ack(self):
        """Checks if the ack bit is set and updates the image"""
        print("Checking ack...")
        if self.get_sr()["ack"]:
            self.update_image()
        #if self.frameswap:
        #    self.cpu.set_irq(self.irq)

    def get_sr(self) -> dict:
        """Returns the status register"""
        sr = int(self.cpu.get_mem(self.addr+STATUS_OFFSET, 1).hex(), 16)
        return {"ack": sr & ACK_MASK,
                "fill": sr & FILL_SCREEN_MASK}

    def fill_screen(self, color: QColor):
        """Fills the screen with a color"""
        fb:memoryview = self.image.bits()
        for y in range(self.scr_height):
            for x in range(self.scr_width):
                fb[(x + y * self.scr_width) * 3] = color.red()
                fb[(x + y * self.scr_width) * 3 + 1] = color.green()
                fb[(x + y * self.scr_width) * 3 + 2] = color.blue()

    def read_framebuffer(self):
        """Each pixel is 1 byte in argb format"""
        fb:memoryview = self.image.bits()
        for y in range(self.scr_height):
            t = time.time()
            for x in range(self.scr_width):
                color = self.get_color(self.cpu.get_mem(self.addr + x + y * self.scr_width, 1)[0])
                fb[(x + y * self.scr_width) * 3] = color.red()
                fb[(x + y * self.scr_width) * 3 + 1] = color.green()
                fb[(x + y * self.scr_width) * 3 + 2] = color.blue()
            if y == 0:
                print(f"Read row {y} in {time.time() - t} seconds")

class Screen(QWidget):
    def __init__(self, cpu: m68k.m68k, addr: int = DEFAULT_ADDRESS, frameswap: bool = False,
                 width: int = 256, height: int = 256, refr_rate: int = 1, parent = None):
        """Emulated screen with WxH pixels and a 16-bit color depth
        memory: addr + sr + w * h - 1
        pixel: 0baarrggbb where a is typically set to 1
        sr: 0bssrrggbb where s is ab (ack, black screen)"""

        super().__init__(parent)
        frame = QVBoxLayout()
        self.cpu = cpu
        self.addr = addr
        self.frameswap = frameswap
        self.irq = 1
        self.scr_width: int = width
        self.scr_height: int = height
        self.refr_rate = refr_rate
        self.resize(self.scr_width, self.scr_height)
        self.image = QImage(self.scr_width, self.scr_height, QImage.Format_RGB888)
        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setWindowTitle("Screen")
        self.power = False
        self.power_btn = QPushButton(f"Power {'off' if self.power else 'on'}")
        self.power_btn.clicked.connect(self.toggle_power)
        self.power_label = QLabel("Screen is turned off")
        self.power_label.setAlignment(Qt.AlignCenter)
        self.power_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        frame.addWidget(self.canvas)
        frame.addWidget(self.power_label)
        frame.addWidget(self.power_btn)
        self.setLayout(frame)

        self.fill_screen(QColor(255, 255, 255))
        self.show()

    def fill_screen(self, color: QColor):
        """Fills the screen with a color"""
        fb:memoryview = self.image.bits()
        for y in range(self.scr_height):
            for x in range(self.scr_width):
                fb[(x + y * self.scr_width) * 3] = color.red()
                fb[(x + y * self.scr_width) * 3 + 1] = color.green()
                fb[(x + y * self.scr_width) * 3 + 2] = color.blue()

    def read_framebuffer(self):
        """Each pixel is 1 byte in argb format"""
        fb:memoryview = self.image.bits()
        for y in range(self.scr_height):
            t = time.time()
            for x in range(self.scr_width):
                color = self.get_color(self.cpu.get_mem(self.addr + x + y * self.scr_width, 1)[0])
                fb[(x + y * self.scr_width) * 3] = color.red()
                fb[(x + y * self.scr_width) * 3 + 1] = color.green()
                fb[(x + y * self.scr_width) * 3 + 2] = color.blue()
            if y == 0:
                print(f"Read row {y} in {time.time() - t} seconds")

    def get_color(self, palette_index: int) -> QColor:
        """Returns the color at the palette index"""
        color = self.cpu.get_mem(self.addr + PALETTE_OFFSET + palette_index * 3, 3)
        return QColor(color[0], color[1], color[2])

    def update_image(self):
        """Reads from self.addr WxH argb bytes and updates the image"""
        if not self.cpu.get_power_status():
            self.fill_screen(QColor(255, 255, 255))
            self.power_label.setHidden(False)
            self.power_label.setText("CPU and mem are off")
        else:
            fill_flag = self.get_sr()["fill"]
            if fill_flag:
                color = self.get_color(self.cpu.get_mem(self.addr, 1)[0])
                self.fill_screen(color)
            else:
                t = time.time()
                self.read_framebuffer()
                print(f"Read framebuffer in {time.time() - t} seconds")
        self.canvas.setPixmap(QPixmap.fromImage(self.image))

    def check_ack(self):
        """Checks if the ack bit is set and updates the image"""
        print("Checking ack...")
        if self.get_sr()["ack"]:
            self.update_image()
        if self.frameswap:
            self.cpu.set_irq(self.irq)

    def get_sr(self) -> dict:
        """Returns the status register"""
        sr = int(self.cpu.get_mem(self.addr+STATUS_OFFSET, 1).hex(), 16)
        return {"ack": sr & ACK_MASK,
                "fill": sr & FILL_SCREEN_MASK}

    def toggle_power(self):
        """Toggles the power of the screen"""
        self.power = not self.power
        self.power_btn.setText(f"{'Shutdown' if self.power else 'Power on'}")
        self.power_label.setText("Screen is turned off")
        self.power_label.setHidden(self.power or self.cpu.get_power_status())
        if self.power:
            self.drawthread = ImageComposer(self.image, self.canvas, self.cpu, self.addr, self.scr_width, self.scr_height, self.refr_rate)
            QThreadPool.globalInstance().start(self.drawthread)
        else:
            self.drawthread.abort()
            self.fill_screen(QColor(255, 255, 255))

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    screen = Screen(None)
    sys.exit(app.exec_())
