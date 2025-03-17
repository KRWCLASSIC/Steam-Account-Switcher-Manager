@echo off
REM Build script for Nuitka

cd ..

REM Install requirements
pip install -r requirements.txt

REM Build the application
python -m nuitka ^
    --onefile ^
    --enable-plugin=pyside6 ^
    --assume-yes-for-downloads ^
    --windows-console-mode=disable ^
    --remove-output ^
    --output-dir=building_scripts/nuitka ^
    --windows-company-name="KRW CLASSIC" ^
    --windows-product-name="SASM" ^
    --windows-product-version="1.2" ^
    sasm.pyw

cd building_scripts/nuitka