@echo off
call win_build_with_nuitka.bat & cd ../.. & REM "Nuitka Windows Build"
call win_build_with_pyinstaller.bat & cd ../.. & REM "PyInstaller Windows Build"
call wsl bash -c ./lnx_build_with_nuitka.sh & REM "Nuitka Linux Build"
call wsl bash -c ./lnx_build_with_pyinstaller.sh & REM "PyInstaller Linux Build"