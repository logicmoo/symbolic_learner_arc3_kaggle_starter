@echo off
setlocal EnableExtensions
set "ROOT=%~dp0.."
set "BIND_IP=%~1"
if not defined BIND_IP set "BIND_IP=127.0.0.1"
set "API_PORT=%~2"
if not defined API_PORT set "API_PORT=8000"
set "PYTHON_EXE=%ROOT%\.venv\Scripts\python.exe"

title MeTTa Workbench API %BIND_IP%:%API_PORT%
cd /d "%ROOT%\server"
doskey restart="%PYTHON_EXE%" -m uvicorn app:app --reload --host %BIND_IP% --port %API_PORT%

echo.
echo ============================================================
echo  MeTTa Workbench API
echo ============================================================
echo  Working directory:
echo    %CD%
echo.
echo  Command being run:
echo    "%PYTHON_EXE%" -m uvicorn app:app --reload --host %BIND_IP% --port %API_PORT%
echo.
echo  If you stop it with Ctrl+C:
echo    type restart
echo  or rerun the full command shown above.
echo  This command window stays open after the server exits.
echo ============================================================
echo.

"%PYTHON_EXE%" -m uvicorn app:app --reload --host %BIND_IP% --port %API_PORT%

echo.
echo ------------------------------------------------------------
echo  API server stopped.
echo  Type: restart
echo  Full restart command:
echo    "%PYTHON_EXE%" -m uvicorn app:app --reload --host %BIND_IP% --port %API_PORT%
echo ------------------------------------------------------------
echo.
