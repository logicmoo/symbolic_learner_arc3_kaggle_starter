@echo off
setlocal EnableExtensions
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"

set "OMNIROUTE_PORT=%~1"
if not defined OMNIROUTE_PORT set "OMNIROUTE_PORT=20128"
set "OMNIROUTE_CMD=%APPDATA%\npm\omniroute.cmd"

rem OmniRoute loads the repository .env before spawning its dashboard. Pin
rem both generic dashboard variables so a repository PORT value (the
rem Workbench API normally uses 8000) cannot create a second listener there.
set "PORT=%OMNIROUTE_PORT%"
set "DASHBOARD_PORT=%OMNIROUTE_PORT%"

title OmniRoute %OMNIROUTE_PORT%
cd /d "%~dp0..\.."

if not exist "%OMNIROUTE_CMD%" (
  echo Installing the official OmniRoute npm package...
  call npm.cmd install -g omniroute
  if errorlevel 1 exit /b 1
)

echo.
echo ============================================================
echo  OmniRoute local gateway
echo ============================================================
echo  Dashboard:             http://127.0.0.1:%OMNIROUTE_PORT%/
echo  OpenAI-compatible API: http://127.0.0.1:%OMNIROUTE_PORT%/v1
echo  Default workbench model: auto/best-free
echo.
echo  First-run endpoint-key setup is handled by the workbench.
echo  Set OMNIROUTE_ADMIN_PASSWORD if the dashboard password is no
echo  longer OmniRoute's initial CHANGEME value.
echo ============================================================
echo.

call "%OMNIROUTE_CMD%" serve --port %OMNIROUTE_PORT% --no-open --no-tray --log

echo.
echo OmniRoute stopped. Rerun this script to restart it.
echo.
