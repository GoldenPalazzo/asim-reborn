#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

class Palette:
    def __init__(self,
                 background: int,
                 text: int,
                 character: int,
                 directive: int,
                 opcode: int,
                 registers: int,
                 comments: int,
                 highlight: int):
        self.background = (background)
        self.text= (text)
        self.character = (character)
        self.directive = (directive)
        self.opcode = (opcode)
        self.registers = (registers)
        self.comments = (comments)
        self.highlight = (highlight)

monokai = Palette(0x272822,
                  0xf8f8f2,
                  0xe6db74,
                  0xf92672,
                  0x66d9ef,
                  0xa6e22e,
                  0x6d6b6d,
                  0x3e3d32)
