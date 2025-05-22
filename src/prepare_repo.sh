#!/bin/sh
set -uex
prj_dir=$(dirname $(dirname $(readlink -f "$0")))
bin_dir=$prj_dir/bin
res_dir=$prj_dir/res
# Making directories
mkdir -p $bin_dir $res_dir $lib_dir
# Downloading resources
curl -Lo "$res_dir/DroidSansMono.ttf" \
    "https://www.fontsquirrel.com/fonts/download/droid-sans-mono"
curl -Lo "$res_dir/MonoLisa-Regular.ttf" \
    "https://github.com/koprab/monalisa-font/raw/master/MonoLisa-Regular.ttf"
#curl -Lo "$lib_dir/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl" \
#    "https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl"
