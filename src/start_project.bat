@echo off
setlocal

set "ROOT=%~dp0"
set "ENV_NAME=%~1"
if "%ENV_NAME%"=="" set "ENV_NAME=pytorch"
set "MODE=%~2"
if "%MODE%"=="" set "MODE=web"
set "DO_INSTALL=%~3"
set "REQ_NO_TORCH=%TEMP%\requirements_no_torch.txt"

echo ROOT: %ROOT%
echo CONDA_ENV: %ENV_NAME%
echo MODE: %MODE%
echo INSTALL: %DO_INSTALL%

set "BACKEND_DIR="
if exist "%ROOT%backend\app.py" set "BACKEND_DIR=%ROOT%backend"
if "%BACKEND_DIR%"=="" (
  for /d %%D in ("%ROOT%*") do (
    if exist "%%D\app.py" set "BACKEND_DIR=%%~fD"
  )
)

set "FRONTEND_DIR="
if exist "%ROOT%frontend\package.json" if exist "%ROOT%frontend\src" set "FRONTEND_DIR=%ROOT%frontend"
if "%FRONTEND_DIR%"=="" (
  for /d %%D in ("%ROOT%*") do (
    if exist "%%D\package.json" if exist "%%D\src" set "FRONTEND_DIR=%%~fD"
  )
)

if "%BACKEND_DIR%"=="" (
  echo Backend directory not found under: %ROOT%
  if "%~1"=="" pause
  exit /b 1
)
if "%FRONTEND_DIR%"=="" (
  echo Frontend directory not found under: %ROOT%
  if "%~1"=="" pause
  exit /b 1
)
echo BACKEND_DIR: %BACKEND_DIR%
echo FRONTEND_DIR: %FRONTEND_DIR%

where conda >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Conda not found. Run: conda init powershell
  if "%~1"=="" pause
  exit /b 1
)

echo Checking conda env: %ENV_NAME% ...
conda info --envs 2>nul | findstr /b /c:"%ENV_NAME% " >nul 2>nul
if errorlevel 1 (
  echo.
  echo ============================================================
  echo [ERROR] Conda environment "%ENV_NAME%" not found!
  echo.
  echo Available environments:
  conda env list
  echo.
  echo Please fix the ENV_NAME in run_project.bat or create the environment.
  echo Example: conda create -n %ENV_NAME% python=3.10
  echo ============================================================
  if "%~1"=="" pause
  exit /b 1
)
echo Conda env "%ENV_NAME%" OK.

if /i "%DO_INSTALL%"=="install" (
  if not exist "%FRONTEND_DIR%\package.json" (
    echo package.json not found in: %FRONTEND_DIR%
    if "%~1"=="" pause
    exit /b 1
  )
  echo Installing backend dependencies - skip torch...
  pushd "%BACKEND_DIR%"
  if exist "requirements.txt" (
    findstr /v /r /i "^torch$" "^torch\\[" "^torch[<>=!~]" "^torchvision$" "^torchvision\\[" "^torchvision[<>=!~]" "^torchaudio$" "^torchaudio\\[" "^torchaudio[<>=!~]" "requirements.txt" > "%REQ_NO_TORCH%"
    call conda activate %ENV_NAME% && python -m pip install -r "%REQ_NO_TORCH%"
    del "%REQ_NO_TORCH%"
  ) else (
    echo requirements.txt not found. Skipping backend install.
  )
  popd
  echo Installing frontend dependencies...
  pushd "%FRONTEND_DIR%"
  call npm install
  popd
)

echo Starting backend...
start "backend" cmd /k "cd /d ""%BACKEND_DIR%"" && conda activate %ENV_NAME% && python app.py"

if /i "%MODE%"=="share" (
  echo.
  echo ============================================================
  echo  [SHARE MODE] Starting Cloudflare Tunnel...
  echo  Backend serves frontend from frontend/dist/
  echo  Waiting for backend to start...
  echo ============================================================
  timeout /t 6 /nobreak >nul
  set "CF_LOG=%TEMP%\cloudflared.log"
  start "cloudflared" cmd /c ""%ProgramFiles(x86)%\cloudflared\cloudflared.exe" tunnel --url http://localhost:5000 2>"%TEMP%\cloudflared.log""
  echo.
  echo Waiting for Cloudflare Tunnel...
  conda activate %ENV_NAME% && python "%ROOT%fetch_tunnel_url.py"
) else if /i "%MODE%"=="electron" (
  echo Starting frontend and Electron...
  start "frontend-dev" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev -- --host 127.0.0.1 --port 5173"
  start "frontend-electron" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run electron"
) else (
  echo Starting frontend...
  start "frontend-dev" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev -- --host 127.0.0.1 --port 5173"
)

echo Launch requested. Check the new windows.
if "%~1"=="" pause
