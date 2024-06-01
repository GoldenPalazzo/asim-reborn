#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import pathlib, platform, sys
if getattr(sys, 'frozen', False):
    base_path = pathlib.Path(sys._MEIPASS) # type: ignore

else:
    base_path = pathlib.Path(__file__).parent.parent

def resolve_path(path: str) -> pathlib.Path:
    return (base_path / path).resolve()

print(base_path)
compiler_path = (base_path /
                 "bin" /
                 ("vasmm68k_mot_"
                  f"{'win.exe' if platform.system() == 'Windows' else 'unix'}")
                 ).resolve()

