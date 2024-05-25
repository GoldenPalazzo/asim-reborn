#!/usr/bin/env python3

import pathlib
import platform
import os.path
import subprocess
import sys

import path_resolver


arguments = ("-Fsrec","-s37","-exec=main","-no-opt")

class Compiler:
    def __init__(self):
        pass
        #subprocess.run(["just", "build"])
    def compile(self, fpath) -> str:
        command_array = [str(path_resolver.compiler_path),
                              *arguments,
                              "-o",
                              f"{os.path.splitext(fpath)[0]}.h68",
                              fpath]
        print(f"Running {command_array}")
        p = subprocess.Popen(command_array, stdout=subprocess.PIPE)
        if p.wait() != 0:
            raise Exception("Compilation failed")
        return p.stdout.read().decode("utf-8")
