#!/bin/bash
# Build script for Nuitka

cd ..

# Install requirements
pip install -r requirements.txt

# Build the application
python3 -m nuitka \
    --onefile \
    --enable-plugin=pyside6 \
    --assume-yes-for-downloads \
    --remove-output \
    --output-filename=sasm-linux \
    --output-dir=building_scripts/builds/nuitka-linux \
    sasm.pyw

cd building_scripts/builds/nuitka-linux
