REM Description: Download all the necessary files to build the project
REM Author: Francesco Palazzo
mkdir bin
mkdir res
mkdir lib
curl http://francescopalazzo.net/downloadable/vasmm68k_mot_win.exe -o bin\vasmm68k_mot_win.exe
curl https://www.fontsquirrel.com/fonts/download/droid-sans-mono -o res\DroidSansMono.ttf
curl https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-win_amd64.whl -o lib\bare68k.whl
dir bin
dir res
dir lib
