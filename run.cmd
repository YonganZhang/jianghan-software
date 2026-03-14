@echo off
REM ============================================
REM  jianghan-software - Auto-generated run.cmd
REM  Generated: 2026-03-14
REM  Can be double-clicked for manual debugging
REM ============================================

REM --- Environment Variables ---
set PYTHONIOENCODING=utf-8
set FLASK_ENV=production
set FLASK_DEBUG=0
REM set SECRET_KEY=changeme-in-production

REM --- Conda Python Path ---
set PYTHON_EXE=D:\Anaconda\envs\software\python.exe

REM --- Julia (project-level runtime, optional) ---
if exist "D:\server\jianghan-software\runtime\julia-1.10\bin" (
    set "PATH=D:\server\jianghan-software\runtime\julia-1.10\bin;%PATH%"
)

REM --- Working Directory ---
cd /d "D:\server\jianghan-software\src\backend"

REM --- Launch ---
echo [%date% %time%] Starting jianghan-software...
"%PYTHON_EXE%" app.py
echo [%date% %time%] Process exited with code %ERRORLEVEL%
