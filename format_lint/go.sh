#!/bin/sh
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
UTILS="${SCRIPT_DIR}/.."
UTILS=$UTILS \
    target=$target \
    docker-compose \
    --file $UTILS/format_lint/docker-compose.yml up --build
