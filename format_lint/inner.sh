#!/bin/sh
set -e
cd /root
python -m black /target
# python -m utils.format_lint.main
