#!/usr/bin/env bash

set -ex

if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please run this script from within a virtual environment."
    exit 1
fi

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
