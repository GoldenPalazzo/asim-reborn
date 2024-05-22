#!/usr/bin/sh
#
mkdir -p bin
wget http://francescopalazzo.net/downloadable/vasmm68k_mot_linux -O bin/vasmm68k_mot_linux
chmod +x bin/vasmm68k_mot_linux
mkdir -p res
wget https://www.fontsquirrel.com/fonts/download/droid-sans-mono -O res/DroidSansMono.ttf
mkdir -p lib
wget https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl -O lib/bare68k-0.1.2-cp312-cp312-linux_x86_64.whl
