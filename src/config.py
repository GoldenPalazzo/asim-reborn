#!/usr/bin/env python

# ASIM Reborn - Simple multiplatform 68k IDE
# Copyright (C) 2024 Francesco Palazzo

import tomllib, os
import platformdirs

class Config:
    def __init__(self):
        app_name = "asim-reborn"
        defaults = {
                "editor": {
                    "font": "Monospace",
                }
        }
        self.config = {}
        if not os.path.exists(platformdirs.user_config_dir(app_name)):
            os.makedirs(platformdirs.user_config_dir(app_name))
        self.config_file = os.path.join(platformdirs.user_config_dir(app_name), "config.toml")
        if os.path.exists(self.config_file):
            with open(self.config_file, "rb") as f:
                self.config = tomllib.load(f)
        else:
            self.config = defaults
