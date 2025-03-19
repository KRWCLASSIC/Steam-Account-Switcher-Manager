#!/bin/bash
# Build script for PyInstaller

cd ..

# Install requirements
pip install -r requirements.txt

# Build the application
"$HOME/.local/bin/pyinstaller" --onefile --name sasm-linux --distpath "building_scripts/builds/pyinstaller-linux" sasm.pyw

# Clean up
rm -rf build
rm -f sasm-linux.spec

cd building_scripts/builds/pyinstaller-linux
