@echo off
setlocal

set "ENV_NAME=%~1"
if "%ENV_NAME%"=="" set "ENV_NAME=dl-gpu"
set "MODE=%~2"
if "%MODE%"=="" set "MODE=web"

echo.
echo  ========================================
echo   Yongan Project Launcher
echo  ========================================
echo   ENV:  %ENV_NAME%
echo   MODE: %MODE%
echo.
echo   Available modes:
echo     web      - Local dev (frontend + backend)
echo     electron - Desktop app (Electron)
echo     share    - Public access via ngrok
echo  ========================================
echo.

call "%~dp0start_project.bat" %ENV_NAME% %MODE%

echo.
pause
