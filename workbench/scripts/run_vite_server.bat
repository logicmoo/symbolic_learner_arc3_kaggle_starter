@echo off
rem Intentionally do not SETLOCAL here.  These variables must remain in this
rem child command window after Vite is stopped so `restart` uses the same
rem host, port, and API target.
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"
set "ROOT=%~dp0.."
set "BIND_IP=%~1"
if not defined BIND_IP set "BIND_IP=127.0.0.1"
set "WEB_PORT=%~2"
if not defined WEB_PORT set "WEB_PORT=5173"
set "API_TARGET=%~3"
if not defined API_TARGET set "API_TARGET=http://127.0.0.1:8000"

set "WORKBENCH_WEB_HOST=%BIND_IP%"
set "WORKBENCH_WEB_PORT=%WEB_PORT%"
set "WORKBENCH_API_TARGET=%API_TARGET%"

title MeTTa Workbench Vite %BIND_IP%:%WEB_PORT%
cd /d "%ROOT%\frontend"
doskey restart=npm run dev

echo.
echo ============================================================
echo  MeTTa Workbench Vite Frontend
echo ============================================================
echo  Working directory:
echo    %CD%
echo.
echo  Environment for this instance:
echo    WORKBENCH_WEB_HOST=%WORKBENCH_WEB_HOST%
echo    WORKBENCH_WEB_PORT=%WORKBENCH_WEB_PORT%
echo    WORKBENCH_API_TARGET=%WORKBENCH_API_TARGET%
echo.
echo  Command being run:
echo    npm run dev
echo.
echo  If you stop it with Ctrl+C:
echo    type restart
echo  or rerun: npm run dev
echo  The instance environment above remains set in this window.
echo  This command window stays open after Vite exits.
echo ============================================================
echo.

call npm run dev

echo.
echo ------------------------------------------------------------
echo  Vite frontend stopped.
echo  Type: restart
echo  Full restart command:
echo    npm run dev
echo ------------------------------------------------------------
echo.
