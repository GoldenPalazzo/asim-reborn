#!/usr/bin/env python3

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import re
import pathlib
import platform
import os.path
import subprocess
import sys

import path_resolver


class VasmCompiler:
    def __init__(self):
        self.arguments = (
            "-maxerrors=1",
            "-Fsrec",
            "-s37",
            "-exec=main",
            "-no-opt"
        )

    def compile(self, fpath) -> tuple[str,str]:
        command_array = [str(path_resolver.compiler_path),
                              *self.arguments,
                              "-o", f"{os.path.splitext(fpath)[0]}.h68",
                              "-L", f"{os.path.splitext(fpath)[0]}.lst",
                              fpath
        ]
        p = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        #if p.wait() != 0:
        #    raise Exception("Compilation failed")
        return out.decode(), err.decode()

    def get_error_lines(self, error: str) -> list:
        line_re = r"in line (\d+)"
        return list(map(int, re.findall(line_re, error)))
