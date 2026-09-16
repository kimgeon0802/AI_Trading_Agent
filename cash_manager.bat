@echo off
cd /d "%~dp0"

echo ========================================
echo        AI Trading Agent - Cash Manager
echo ========================================
echo.

python tools\account_tool.py

echo.
pause