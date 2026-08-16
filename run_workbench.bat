@echo off
setlocal EnableExtensions EnableDelayedExpansion
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"
if /I "%~1"=="/kill" (
  set "KILL_WEB_PORT=%~2"
  if not defined KILL_WEB_PORT set "KILL_WEB_PORT=5173"
  set "KILL_API_PORT=%~3"
  if not defined KILL_API_PORT set "KILL_API_PORT=8000"
  if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0workbench\scripts\stop_workbench.py" --web-port "!KILL_WEB_PORT!" --api-port "!KILL_API_PORT!"
  ) else (
    python "%~dp0workbench\scripts\stop_workbench.py" --web-port "!KILL_WEB_PORT!" --api-port "!KILL_API_PORT!"
  )
  exit /b !ERRORLEVEL!
)
call "%~dp0workbench\run_demo.bat" %*
