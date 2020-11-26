#!/bin/sh
projdir=$(git rev-parse --show-toplevel)
version=$(grep -E '^__version__' build.py | cut -d\" -f 2)

build_opts="-t hmfont:$version"
docker build $build_opts .

run_opts="-v $projdir/outputs:/outputs"
docker run $run_opts "hmfont:$version"
