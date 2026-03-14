@echo off
setlocal
set "ROOT=%~dp0"
set "JULIA_DIR=%ROOT%resources\julia"

echo [SETUP] Verifying Julia Environment for Packaging...
echo Target Directory: %JULIA_DIR%

if exist "%JULIA_DIR%\bin\julia.exe" (
    echo [OK] Julia found.
    echo.
) else (
    echo [MISSING] Julia Portable is NOT installed!
    echo.
    echo Please follow these steps:
    echo 1. Download Julia Portable (zip) from https://julialang.org/downloads/
    echo    (Recommended: Julia 1.10 or later)
    echo 2. Create folder "%ROOT%resources" if not exists.
    echo 3. Extract the zip into "%JULIA_DIR%"
    echo    Ensure path is: %JULIA_DIR%\bin\julia.exe
    echo.
    echo After extracting, run this script again or proceed to build.
    echo.
    pause
    exit /b 1
)

echo [OPTIONAL] Pre-warming Julia depot...
echo If you want to pre-install PySR dependencies, run:
echo conda run -n pytorch python -c "import pysr; pysr.install()"
echo (Make sure JULIA_BINARIES is set or Julia is in PATH for this step)
echo.
pause
