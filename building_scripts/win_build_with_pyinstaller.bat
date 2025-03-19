@echo off
REM Build script for PyInstaller

cd ..

REM Install requirements
pip install -r requirements.txt

REM Build the application
pyinstaller --onefile --name sasm --distpath "building_scripts/builds/pyinstaller-win" sasm.pyw

REM Clean up
rmdir /s /q build >nul 2>&1
del SASM.spec >nul 2>&1

cd building_scripts/builds/pyinstaller-win