#!/bin/bash

ARG="$1"

if [[ $ARG == "test" ]]; then
    git clone "https://owenstranathan:$GITHUB_TOKEN@github.com/appfigures/play-sdks.git"
    make build -C play-sdks
fi