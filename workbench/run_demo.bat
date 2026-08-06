@echo off
set ROOT=%~dp0
if not exist "%ROOT%.venv" python -m venv "%ROOT%.venv"
call "%ROOT%.venv\Scripts\activate.bat"
pip install -r "%ROOT%server\requirements.txt"
cd /d "%ROOT%frontend"
call npm install
start "MeTTa API" cmd /k "cd /d %ROOT%server && %ROOT%.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000"
start "MeTTa UI" cmd /k "cd /d %ROOT%frontend && npm run dev -- --host 0.0.0.0"
