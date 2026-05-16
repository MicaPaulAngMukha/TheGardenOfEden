@echo off
echo Building Garden of Eden executable...
echo.

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller GardenOfEden.spec

echo.
echo Build complete! Check the 'dist' folder for GardenOfEden.exe
echo.
pause
