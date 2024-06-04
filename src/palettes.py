#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

class Palette:
    def __init__(self,
                 background: str,
                 text: str,
                 character: str,
                 directive: str,
                 opcode: str,
                 registers: str,
                 comments: str,
                 highlight: str):
        self.background = (background)
        self.text= (text)
        self.character = (character)
        self.directive = (directive)
        self.opcode = (opcode)
        self.registers = (registers)
        self.comments = (comments)
        self.highlight = (highlight)

def dict_to_palette(palette: dict, base: Palette):
    new_palette = Palette(base.background,
                          base.text,
                          base.character,
                          base.directive,
                          base.opcode,
                          base.registers,
                          base.comments,
                          base.highlight)
    new_palette.background = palette.get("background",base.background)
    new_palette.text = palette.get("text",base.text)
    new_palette.character = palette.get("character",base.character)
    new_palette.directive = palette.get("directive",base.directive)
    new_palette.opcode = palette.get("opcode",base.opcode)
    new_palette.registers = palette.get("registers",base.registers)
    new_palette.comments = palette.get("comments",base.comments)
    new_palette.highlight = palette.get("highlight",base.highlight)
    return new_palette

monokai = Palette("#272822",
                  "#f8f8f2",
                  "#e6db74",
                  "#f92672",
                  "#66d9ef",
                  "#a6e22e",
                  "#6d6b6d",
                  "#3e3d32")
