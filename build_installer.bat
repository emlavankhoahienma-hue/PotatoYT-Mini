@echo off
title PotatoYT-Mini Installer Builder
chcp 65001 >nul
cls

echo ========================================================
echo       🥔 PotatoYT-Mini - Dong Goi Bo Cai Dat Setup
echo ========================================================
echo.

:: 1. Rebuild executable
echo [*] Dang bien dich PotatoYT-Mini.exe...
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /target:winexe /win32icon:potato.ico /out:PotatoYT-Mini.exe src\Launcher.cs

:: 2. Find Inno Setup compiler
set "ISCC_EXE="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo [!] Khong tim thay Inno Setup compiler (ISCC.exe).
    echo [!] Vui long cai dat Inno Setup 6: winget install JRSoftware.InnoSetup
    pause
    exit /b 1
)

:: 3. Compile Installer
echo [*] Dang dong goi bo cai dat PotatoYT-Mini-Setup.exe...
"%ISCC_EXE%" installer.iss

echo.
if exist "dist\PotatoYT-Mini-Setup.exe" (
    echo [OK] Thanh cong! Bo cai dat nam tai: dist\PotatoYT-Mini-Setup.exe
) else (
    echo [!] Dong goi that bai.
)

pause
