@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building Windows executable...
pyinstaller build_windows.spec --clean

echo.
echo Build complete!
echo Executable at: dist\InverterTracker.exe
pause
