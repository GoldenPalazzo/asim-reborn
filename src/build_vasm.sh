#!/bin/sh

prj_dir=$(dirname $(dirname $(readlink -f "$0")))
bin_dir=$prj_dir/bin
src_dir=$prj_dir/src

mkdir -p $bin_dir

curl -Lo $src_dir/vasm.tar.gz http://sun.hasenbraten.de/vasm/release/vasm.tar.gz
tar -xzf $src_dir/vasm.tar.gz -C $src_dir
cd $src_dir/vasm
make CPU=m68k SYNTAX=mot
mv vasmm68k_mot $bin_dir/vasmm68k_mot_unix
rm -rf $src_dir/vasm $src_dir/vasm.tar.gz
