@echo off
setlocal EnableExtensions
set "RELAY_ROOT=%~1"
if not defined RELAY_ROOT set "RELAY_ROOT=%~dp0..\..\..\mailbox_channel"
set "RELAY_PYTHON=python"
if exist "%RELAY_ROOT%\.venv\Scripts\python.exe" set "RELAY_PYTHON=%RELAY_ROOT%\.venv\Scripts\python.exe"
set "WORKBENCH_CONTROL_API=%WORKBENCH_CONTROL_API%"
if not defined WORKBENCH_CONTROL_API set "WORKBENCH_CONTROL_API=http://127.0.0.1:8000"
set "PYTHONPATH=%RELAY_ROOT%\src;%PYTHONPATH%"
"%~dp0..\..\.venv\Scripts\python.exe" "%~dp0submit_managed_command.py" --api "%WORKBENCH_CONTROL_API%" --service channel-relay --cwd "%RELAY_ROOT%" --env PYTHONPATH -- "%RELAY_PYTHON%" -m mailbox_channels.server
exit /b %ERRORLEVEL%
