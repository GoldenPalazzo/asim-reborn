set prj_dir=%~dp0
set bin_dir=%prj_dir%bin
set res_dir=%prj_dir%res
set lib_dir=%prj_dir%lib
if not exist "%bin_dir%" mkdir "%bin_dir%"
if not exist "%res_dir%" mkdir "%res_dir%"
if not exist "%lib_dir%" mkdir "%lib_dir%"
curl -L -o %bin_dir%\vasmm68k_mot_win.exe http://francescopalazzo.net/downloadable/vasmm68k_mot_win.exe 
curl -L -o %res_dir%\DroidSansMono.ttf https://www.fontsquirrel.com/fonts/download/droid-sans-mono
curl -L -o %res_dir%\MonoLisa-Regular.ttf https://github.com/koprab/monalisa-font/raw/master/MonoLisa-Regular.ttf
curl -L -o %lib_dir%\bare68k-0.1.2-cp312-cp312-win_amd64.whl https://github.com/GoldenPalazzo/bare68k-python3.12/releases/download/v0.1.2-3.12/bare68k-0.1.2-cp312-cp312-win_amd64.whl
attrib +r %bin_dir%\vasmm68k_mot_win.exe
set PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
