#!/bin/sh
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
UTILS="${SCRIPT_DIR}/.."
ls $UTILS
UTILS=$UTILS \
    database=$database \
    destination=$destination \
    docker-compose \
    --file $UTILS/document_database/docker-compose.yml up --build
