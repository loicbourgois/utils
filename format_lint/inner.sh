#!/bin/sh
set -e
ignore="E203,C901,W291,E226,E741,W0611,E501,E722,E402,E722,E711,W605,W503,F401,W0401"
pylint --version
black --version
flake8 --version
pylama --version
python -m black /target
pylama -i $ignore /target
pylint --jobs=0 \
    --rcfile /target/pylintrc \
    /target
# flake8 --ignore=$ignore /target
