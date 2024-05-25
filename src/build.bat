setlocal EnableDelayedExpansion

REM Set directories based on the script's location
set "script_path=%~dp0"
for %%i in ("%script_path%..") do set "prj_dir=%%~fi"
set "bin_dir=%prj_dir%\bin"
set "res_dir=%prj_dir%\res"
set "lib_dir=%prj_dir%\lib"
set "src_dir=%prj_dir%\src"
set "dist_dir=%prj_dir%\dist"

REM Remove the existing dist directory
if exist "%dist_dir%" (
    rmdir /s /q "%dist_dir%"
)

REM Function to convert absolute path to relative path
REM Batch doesn't support functions directly, but we can achieve similar functionality with a subroutine
call :abs_to_rel "%bin_dir%" bin_dir_rel
call :abs_to_rel "%res_dir%" res_dir_rel

REM Run pyinstaller
pyinstaller --clean --onedir --name "AsimReborn" ^
    --add-binary="%bin_dir_rel%\vasmm68k_mot_win:bin" ^
    --add-data="%res_dir_rel%\*:res" ^
    "%src_dir%\main.py"

REM Cleanup
if exist "build" (
    rmdir /s /q "build"
)
del /q "*.spec"
move /y "%prj_dir%\dist" "%prj_dir%\dist"

exit /b

:abs_to_rel
    setlocal
    set "target=%~1"
    for %%i in ("%CD%") do set "current_dir=%%~fi"
    set "relative_path=%target:*%current_dir%\=%"
    endlocal & set "%2=%relative_path%"
    goto :EOF
