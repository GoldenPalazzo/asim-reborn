#!/usr/bin/sh
#
docker run -ti -v $PWD:/srv/ --rm 68k-env:latest \
    vasmm68k_mot -Faout -no-opt -o "${1%.*}.bin" $1
