@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo ========================================
echo 修复登录错误 - 添加role字段
echo ========================================
echo.
python fix_login_error.py
