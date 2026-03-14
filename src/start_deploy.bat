@echo off
echo %date% %time% Starting... > D:\projects\software\backend\logs\deploy.log
set PYTHONIOENCODING=utf-8
cd /d D:\projects\software\backend
echo %date% %time% Running Python >> D:\projects\software\backend\logs\deploy.log
D:\Anaconda\envs\software\python.exe app.py >> D:\projects\software\backend\logs\deploy.log 2>&1
echo %date% %time% Python exited with %ERRORLEVEL% >> D:\projects\software\backend\logs\deploy.log
