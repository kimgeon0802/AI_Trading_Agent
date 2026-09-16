@echo off
echo [INFO] Trading Agent 데이터베이스 초기화를 시작합니다.
if exist "data\trading.db" (
    del "data\trading.db"
    echo [OK] data\trading.db 파일이 삭제되었습니다.
) else (
    echo [INFO] 초기화할 데이터베이스 파일이 존재하지 않습니다.
)
echo [OK] 초기화 작업이 완료되었습니다.
echo [INFO] 다음 Trading Cycle 실행 시 데이터베이스와 초기 자본금(0원)이 자동 생성됩니다.
pause