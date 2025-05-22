#!/bin/sh
set -uex
PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:/usr/local/opt/coreutils/libexec/gnubin:$PATH"
prj_dir=$(dirname $(dirname $(readlink -f "$0")))
bin_dir=$prj_dir/bin
res_dir=$prj_dir/res
lib_dir=$prj_dir/lib
src_dir=$prj_dir/src
dist_dir=$prj_dir/dist

ext=""
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    ext=".exe"
fi
vasm_bin="$(abs_to_rel $bin_dir)/vasmm68k_mot$ext"

rm -rf $dist_dir

abs_to_rel() {
    realpath --relative-to="$PWD" "$1"
}

pyinstaller --clean --onedir --name "AsimReborn" \
    --add-binary="$vasm_bin:bin" \
    --add-data="$(abs_to_rel $res_dir)/*:res" \
    --windowed \
    --target-arch=$(uname -m) \
    --icon="$(abs_to_rel $res_dir)/logo_256x256.ico" \
    $src_dir/main.py


rm -rf build *.spec
if [ ! -d "$prj_dir/dist" ]; then
    mv -n dist $prj_dir/dist
fi

chmod +x $prj_dir/dist/AsimReborn/AsimReborn
chmod +x $prj_dir/dist/AsimReborn/_internal/bin/vasmm68k_mot
