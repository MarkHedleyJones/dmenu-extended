#!/usr/bin/env bash

set -eu

python3 -m build --wheel
pip3 install dist/dmenu_extended-*-py3-none-any.whl --upgrade
rm -rf dist src/dmenu_extended.egg-info
