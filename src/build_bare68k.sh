#!/usr/bin/sh

prj_dir=$(dirname $(dirname $(readlink -f "$0")))
bin_dir=$prj_dir/bin
res_dir=$prj_dir/res
lib_dir=$prj_dir/lib
cd $lib_dir/bare68k
pip3 install -r requirements-dev.txt
pip3 install setuptools
python3 setup.py build_ext -i
python3 setup.py sdist
python3 setup.py bdist_wheel
mv dist/*.whl $lib_dir
cd $prj_dir
rm -rf $lib_dir/bare68k

