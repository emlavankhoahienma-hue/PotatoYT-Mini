@echo off
title PotatoYT-Mini Launcher
chcp 65001 >nul
cls

echo ========================================================
echo    🥔 PotatoYT-Mini - Trinh Duyet YouTube Sieu Nhe
echo          Toi uu cho May Yeu, Choi Game & Da Nhiem
echo ========================================================
echo.

:: 1. Kiem tra Python
set "PYTHON_EXE="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    ) else (
        echo [!] Khong tim thay Python. Vui long cai dat Python 3.10 tro len.
        echo [!] Tai tai: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: 2. Kiem tra thu vien phu thuoc
echo [*] Dang kiem tra thu vien (pywebview)...
"%PYTHON_EXE%" -c "import webview" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Dang tu dong cai dat thu vien pywebview...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [!] Cai dat thu vien that bai. Vui long kiem tra ket noi mang.
        pause
        exit /b 1
    )
)

:: 3. Khoi chay ung dung
echo [*] Dang khoi dong PotatoYT-Mini...
start "" "%PYTHON_EXE%" src\main.py

exit /b 0
