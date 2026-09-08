@echo off
setlocal
cd /d "%~dp0"

:: Run the python script which handles environment loading and validation
python scripts/run_trading_cycle.py

pause
