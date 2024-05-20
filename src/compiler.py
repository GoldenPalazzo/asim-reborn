#!/usr/bin/env python3

import pathlib
import platform
import os.path
import subprocess

compiler_path = (pathlib.Path(__file__).parent.parent / "bin" / (f"vasmm68k_mot_{'win.exe' if platform.system() == 'Windows' else 'linux'}")).resolve()
print(compiler_path)

arguments = ("-Fsrec","-s37","-exec=main","-no-opt")

class Compiler:
    def __init__(self):
        pass
        #subprocess.run(["just", "build"])
    def compile(self, fpath):
        command_array = [compiler_path,
                              *arguments,
                              "-o",
                              f"{os.path.splitext(fpath)[0]}.h68",
                              fpath]
        print(f"Running {command_array}")
        subprocess.run(command_array)
