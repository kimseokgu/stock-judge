@echo off
cd /d "%~dp0backend"

echo.
echo ===================================
echo   주식 매매 판단기 시작 중...
echo ===================================

:: 로컬 IP 출력 (핸드폰 접속용)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
  set IP=%%a
  goto :found
)
:found
set IP=%IP: =%

echo.
echo [PC]     http://localhost:8000
echo [핸드폰] http://%IP%:8000
echo.
echo * 핸드폰과 PC가 같은 와이파이에 연결되어 있어야 합니다.
echo * 이 창을 닫으면 서버가 종료됩니다.
echo ===================================
echo.

start "" http://localhost:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000
