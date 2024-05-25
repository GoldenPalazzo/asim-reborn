#!/usr/bin/sh
#
prj_dir=$(dirname $(dirname $(readlink -f "$0")))
bin_dir=$prj_dir/bin
res_dir=$prj_dir/res
lib_dir=$prj_dir/lib
mkdir -p $bin_dir $res_dir $lib_dir
wget "http://francescopalazzo.net/downloadable/vasmm68k_mot_linux" -O "$bin_dir/vasmm68k_mot_linux"
wget "https://www.fontsquirrel.com/fonts/download/droid-sans-mono" -O "$res_dir/DroidSansMono.ttf"
wget "https://github.com/koprab/monalisa-font/raw/master/MonoLisa-Regular.ttf" -O "$res_dir/MonoLisa-Regular.ttf"
wget "https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl" -O "$lib_dir/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl"
chmod +x "bin/vasmm68k_mot_linux"
