REM Description: Download all the necessary files to build the project
REM Author: Francesco Palazzo
mkdir bin
mkdir res
mkdir lib
curl -L -o bin\vasmm68k_mot_win.exe http://francescopalazzo.net/downloadable/vasmm68k_mot_win.exe 
curl -L -o res\DroidSansMono.ttf https://www.fontsquirrel.com/fonts/download/droid-sans-mono
curl -L -o res\MonoLisa-Regular.ttf https://github.com/koprab/monalisa-font/raw/master/MonoLisa-Regular.ttf
curl -L -o lib\bare68k-0.1.2-cp312-cp312-win_amd64.whl https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-win_amd64.whl
dir bin
dir res
dir lib
set PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
