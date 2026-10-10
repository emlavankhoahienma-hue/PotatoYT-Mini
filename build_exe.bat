@echo off
title PotatoYT-Mini Builder (PyInstaller)
chcp 65001 >nul
cls

echo ========================================================
echo       🥔 PotatoYT-Mini - Dong Goi File .EXE
echo ========================================================
echo.

:: Tim Python
set "PYTHON_EXE="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        echo [!] Khong tim thay Python!
        pause
        exit /b 1
    )
)

echo [*] Cai dat PyInstaller...
"%PYTHON_EXE%" -m pip install pyinstaller

echo [*] Dang dong goi thanh file .EXE...
"%PYTHON_EXE%" -m PyInstaller --noconsole --onefile ^
    --name "PotatoYT-Mini" ^
    --add-data "src\assets;assets" ^
    --add-data "config.json;." ^
    src\main.py

echo.
if exist "dist\PotatoYT-Mini.exe" (
    echo [✓] Thanh cong! File EXE nam tai: dist\PotatoYT-Mini.exe
) else (
    echo [!] Dong goi that bai. Vui long kiem tra log.
)

pause
