@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:GEMINI_API_KEY = (Get-Content '.env' | Where-Object { $_ -match '^GEMINI_CLI_API_KEY=' }) -replace '^GEMINI_CLI_API_KEY=', ''; gemini"

endlocal