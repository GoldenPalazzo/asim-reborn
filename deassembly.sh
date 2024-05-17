#!/usr/bin/sh
#
docker run -ti -v $PWD:/srv/ --rm 68k-env:latest m68k-linux-gnu-objdump -b binary -m m68k:68000 -D $1
