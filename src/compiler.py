#!/usr/bin/env python3

import subprocess

class Compiler:
    def __init__(self):
        pass
        #subprocess.run(["just", "build"])
    def compile(self, fpath):
        print(f"Running compile.sh {fpath}")
        print(subprocess.run(["just", "compile", fpath]))
