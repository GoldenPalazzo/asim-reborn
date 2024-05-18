set dotenv-load
set export
set positional-arguments

_default:
    @just --list --unsorted

download-docs:
    mkdir -p docs
    cd docs ;\
    curl -JOLf https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf ;\
    curl -JOLf http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf

build:
    docker build -t 68k-env:latest docker-src

compile file:
    jd="$(readlink -f .)" &&\
    fa="$(cd {{quote(invocation_directory())}} && readlink -f "$1")" &&\
    fr="$(realpath --relative-to="$jd" "$fa")" &&\
    docker run -ti -v "$jd":/srv/ --rm 68k-env:latest \
        vasmm68k_mot -Fsrec -s37 -exec=main -no-opt -o "${fr%.*}.h68" "$fr"
