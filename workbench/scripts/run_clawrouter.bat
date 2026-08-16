@echo off
setlocal EnableExtensions
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"

set "CLAWROUTER_PORT=%~1"
if not defined CLAWROUTER_PORT set "CLAWROUTER_PORT=3456"

title ClawRouter %CLAWROUTER_PORT%
cd /d "%~dp0..\.."

where npx.cmd >nul 2>nul
if errorlevel 1 (
  echo ERROR: npx.cmd was not found. Install Node.js 22 or newer.
  exit /b 1
)

echo.
echo ============================================================
echo  ClawRouter local proxy
echo ============================================================
echo  OpenAI-compatible API: http://127.0.0.1:%CLAWROUTER_PORT%/v1
echo  Health check:          http://127.0.0.1:%CLAWROUTER_PORT%/health
echo  Default workbench model: blockrun/free
echo.
echo  ClawRouter creates its wallet under %%USERPROFILE%%\.openclaw\blockrun.
echo  The free route does not require an API key or wallet balance.
echo ============================================================
echo.

set "WORKBENCH_CONTROL_API=%WORKBENCH_CONTROL_API%"
if not defined WORKBENCH_CONTROL_API set "WORKBENCH_CONTROL_API=http://127.0.0.1:8000"
"%~dp0..\..\.venv\Scripts\python.exe" "%~dp0submit_managed_command.py" --api "%WORKBENCH_CONTROL_API%" --service clawrouter --cwd "%CD%" -- npx.cmd --yes @blockrun/clawrouter --port %CLAWROUTER_PORT%

echo.
echo ClawRouter stopped. Rerun this script to restart it.
echo.
