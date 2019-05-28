#!/bin/bash
mkdir -p cropro
cp cropro.py cropro
echo "from . import cropro" > cropro/__init__.py
rm cropro.ankiaddon
cd cropro && zip -r ../cropro.ankiaddon *
