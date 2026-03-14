@echo off
setlocal

set "ROOT=%~dp0"
set "CF_LOG=%TEMP%\cloudflared.log"

:: Run start_project.bat in a subprocess so even if conda/exit kills it,
:: this window stays alive.
cmd /c call "%ROOT%start_project.bat" dl-gpu share

echo.
echo ============================================================
echo   Searching for Cloudflare Tunnel URL ...
echo ============================================================

set "TUNNEL_URL="
if exist "%CF_LOG%" (
    for /f "tokens=*" %%L in ('findstr /r "https://.*trycloudflare\.com" "%CF_LOG%"') do (
        for %%U in (%%L) do (
            echo %%U | findstr /r "https://.*trycloudflare\.com" >nul 2>nul && set "TUNNEL_URL=%%U"
        )
    )
)

echo.
if defined TUNNEL_URL (
    echo ============================================================
    echo.
    echo   YOUR PUBLIC URL:
    echo.
    echo   %TUNNEL_URL%
    echo.
    echo   Send this link to anyone to access your app!
    echo.
    echo ============================================================
) else (
    echo ============================================================
    echo   ERROR: Could not find Cloudflare Tunnel URL.
    echo   Check log: %CF_LOG%
    echo ============================================================
)
echo.
echo Press any key to close this window...
pause >nul
