@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install pyinstaller==6.16.0 || goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name TB311FU-LineageOS-Installer installer.py || goto :error
echo.
echo Fertig: dist\TB311FU-LineageOS-Installer.exe
pause
exit /b 0
:error
echo Build fehlgeschlagen.
pause
exit /b 1
