@echo off
chcp 65001 > nul
setlocal

:: ============================================================
:: AI Trading Agent - Final Test Menu
:: ============================================================

:: 현재 BAT 파일이 위치한 프로젝트 루트로 이동
cd /d "%~dp0"

:MENU
cls

echo.
echo ============================================================
echo                  AI Trading Agent
echo ============================================================
echo.
echo   1. 프로그램을 시작하시겠습니까?
echo   2. 입/출금 정보를 입력하시겠습니까?
echo   3. 기존 데이터를 초기화 하시겠습니까?
echo   4. 프로그램 종료
echo.
echo ============================================================
echo.

set "CHOICE="
set /p "CHOICE=선택하세요 [1-4]: "

if "%CHOICE%"=="1" goto RUN_TRADING
if "%CHOICE%"=="2" goto CASH_MANAGER
if "%CHOICE%"=="3" goto RESET_DB
if "%CHOICE%"=="4" goto EXIT

echo.
echo [ERROR] 잘못된 선택입니다.
echo [INFO] 1, 2, 3, 4 중 하나를 선택해주세요.
pause
goto MENU


:: ============================================================
:: 1. Trading Program
:: ============================================================
:RUN_TRADING

cls
echo.
echo ============================================================
echo                  Trading Program
echo ============================================================
echo.
echo [INFO] run_trading.bat을 실행합니다.
echo.

if not exist "%~dp0run_trading.bat" (
    echo [ERROR] run_trading.bat 파일을 찾을 수 없습니다.
    echo.
    pause
    goto MENU
)

call "%~dp0run_trading.bat"

echo.
echo ============================================================
echo [INFO] Trading Program이 종료되었습니다.
echo [INFO] 메인 메뉴로 돌아갑니다.
echo ============================================================
echo.
pause
goto MENU


:: ============================================================
:: 2. Cash Manager
:: ============================================================
:CASH_MANAGER

cls
echo.
echo ============================================================
echo                  Cash Manager
echo ============================================================
echo.
echo [INFO] cash_manager.bat을 실행합니다.
echo.

if not exist "%~dp0cash_manager.bat" (
    echo [ERROR] cash_manager.bat 파일을 찾을 수 없습니다.
    echo.
    pause
    goto MENU
)

call "%~dp0cash_manager.bat"

echo.
echo ============================================================
echo [INFO] 입/출금 관리가 종료되었습니다.
echo [INFO] 메인 메뉴로 돌아갑니다.
echo ============================================================
echo.
pause
goto MENU


:: ============================================================
:: 3. Reset Database
:: ============================================================
:RESET_DB

cls
echo.
echo ============================================================
echo                  Database Reset
echo ============================================================
echo.
echo [WARNING] 기존 가상투자 데이터가 모두 삭제됩니다.
echo.
echo [WARNING] trading.db의 기존 거래/포트폴리오/
echo           AI 분석 및 관련 기록이 초기화됩니다.
echo.

if not exist "%~dp0reset_db.bat" (
    echo [ERROR] reset_db.bat 파일을 찾을 수 없습니다.
    echo.
    pause
    goto MENU
)

set "CONFIRM="
set /p "CONFIRM=정말 초기화하시겠습니까? [Y/N]: "

if /I "%CONFIRM%"=="Y" goto RESET_DB_EXECUTE

echo.
echo [INFO] 데이터 초기화를 취소했습니다.
echo.
pause
goto MENU


:RESET_DB_EXECUTE

echo.
echo [INFO] reset_db.bat을 실행합니다.
echo.

call "%~dp0reset_db.bat"

echo.
echo ============================================================
echo [INFO] DB 초기화 작업이 종료되었습니다.
echo [INFO] 메인 메뉴로 돌아갑니다.
echo ============================================================
echo.
pause
goto MENU


:: ============================================================
:: 4. Exit
:: ============================================================
:EXIT

cls
echo.
echo ============================================================
echo              AI Trading Agent 종료
echo ============================================================
echo.
echo 프로그램을 종료합니다.
echo.
echo ============================================================
echo.

endlocal
exit /b 0