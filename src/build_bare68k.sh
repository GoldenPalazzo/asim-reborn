#!/usr/bin/env bash
set -uex

pushd bare68k

# Check if uv is installed
PIP="uv pip"
if ! command -v uv &> /dev/null
then
    echo "uv could not be found, defaulting to pip"
    PIP="pip"
fi

$PIP install setuptools
make init build sdist bdist
popd
