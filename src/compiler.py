#!/usr/bin/env python3

import pathlib
import platform
import os.path
import subprocess
import sys

if getattr(sys, 'frozen', False):
    base_path = pathlib.Path(sys._MEIPASS) # type: ignore

else:
    base_path = pathlib.Path(__file__).parent.parent
compiler_path = (base_path /
                 "bin" /
                 ("vasmm68k_mot_"
                  f"{'win.exe' if platform.system() == 'Windows' else 'linux'}")
                 ).resolve()
print(compiler_path)

arguments = ("-Fsrec","-s37","-exec=main","-no-opt")

class Compiler:
    def __init__(self):
        pass
        #subprocess.run(["just", "build"])
    def compile(self, fpath):
        command_array = [str(compiler_path),
                              *arguments,
                              "-o",
                              f"{os.path.splitext(fpath)[0]}.h68",
                              fpath]
        print(f"Running {command_array}")
        subprocess.run(command_array)
