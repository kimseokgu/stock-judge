@echo off
cd /d "%~dp0backend"
start "server" /min cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "ngrok" /min cmd /c "ngrok http --domain=sleek-yesterday-staff.ngrok-free.dev 8000"
timeout /t 2 /nobreak >nul
start "" http://localhost:8000
exit
