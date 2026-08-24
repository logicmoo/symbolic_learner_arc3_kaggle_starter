@echo off
setlocal EnableExtensions
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"
set "ROOT=%~dp0"
for %%I in ("%ROOT%..") do set "REPO_ROOT=%%~fI"
set "WORKBENCH_PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"

rem Usage:
rem   run_demo.bat [bind_ip] [web_port] [api_port]
rem
rem With no arguments the historical defaults remain:
rem   web  = 127.0.0.1:5173
rem   api  = 127.0.0.1:8000
rem
rem When a non-default web port is supplied and api_port is omitted, the API
rem port is automatically web_port + 1.  A third argument can always override
rem the API port explicitly.

set "BIND_IP=%~1"
if not defined BIND_IP set "BIND_IP=127.0.0.1"

set "WEB_PORT=%~2"
if not defined WEB_PORT set "WEB_PORT=5173"

set "API_PORT=%~3"
if not defined API_PORT (
  if "%WEB_PORT%"=="5173" (
    set "API_PORT=8000"
  ) else (
    set /a API_PORT=WEB_PORT+1 >nul 2>nul
  )
)

call :validate_port "%WEB_PORT%" "web"
if errorlevel 1 exit /b 2
call :validate_port "%API_PORT%" "API"
if errorlevel 1 exit /b 2

set "CONNECT_IP=%BIND_IP%"
if "%CONNECT_IP%"=="0.0.0.0" set "CONNECT_IP=127.0.0.1"

set "WEB_URL=http://%CONNECT_IP%:%WEB_PORT%/"
set "API_URL=http://%CONNECT_IP%:%API_PORT%"
set "API_HEALTH_URL=%API_URL%/api/health"
set "WORKBENCH_CONTROL_API=%API_URL%"
set "CLAWROUTER_PORT=3456"
set "CLAWROUTER_URL=http://127.0.0.1:%CLAWROUTER_PORT%"
set "CLAWROUTER_HEALTH_URL=%CLAWROUTER_URL%/health"
set "OMNIROUTE_PORT=20128"
set "OMNIROUTE_URL=http://127.0.0.1:%OMNIROUTE_PORT%"
set "CHANNEL_RELAY_PORT=46667"
set "CHANNEL_RELAY_URL=http://127.0.0.1:%CHANNEL_RELAY_PORT%"
set "CHANNEL_RELAY_DIR=%REPO_ROOT%\..\mailbox_channel"

title MeTTaSymbolicLearnerWorkbench %BIND_IP%:%WEB_PORT%
echo.
echo  MeTTaSymbolicLearnerWorkbench - local development
echo  -----------------------------------------------
echo  Web: %WEB_URL%
echo  API: %API_URL%
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found on PATH.
  echo Install Python 3.12 or newer, then run this file again.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: npm was not found on PATH.
  echo Install Node.js 22 or newer, then run this file again.
  pause
  exit /b 1
)

if not exist "%WORKBENCH_PYTHON%" (
  echo Creating the repository Python environment...
  python -m venv "%REPO_ROOT%\.venv"
  if errorlevel 1 goto :failed
)

"%WORKBENCH_PYTHON%" -c "import fastapi, pydantic, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Installing Python packages for the first run...
  "%WORKBENCH_PYTHON%" -m pip install --disable-pip-version-check -q -e "%REPO_ROOT%[all]"
  if errorlevel 1 goto :failed
)

if not exist "%ROOT%frontend\node_modules\.bin\vite.cmd" (
  echo Installing web packages for the first run...
  pushd "%ROOT%frontend"
  call npm install
  if errorlevel 1 (
    popd
    goto :failed
  )
  popd
)

echo Starting the local event backend on %BIND_IP%:%API_PORT%...
"%WORKBENCH_PYTHON%" "%ROOT%scripts\start_with_policy.py" --service workbench-api --cwd "%ROOT%." -- "%ComSpec%" /d /c scripts\run_api_server.bat %BIND_IP% %API_PORT%
echo Waiting for the backend before submitting managed commands...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(45); $url='%API_HEALTH_URL%'; do { try { $r=Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 400 } while ((Get-Date) -lt $limit); exit 1"
if errorlevel 1 echo WARNING: The API is unavailable; managed batch files will use legacy mode.

echo Checking Mailbox Channel Relay on 127.0.0.1:%CHANNEL_RELAY_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%CHANNEL_RELAY_URL%/health' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>nul
if errorlevel 1 (
  if exist "%CHANNEL_RELAY_DIR%\mailbox-server.cmd" (
    echo Starting the Mailbox Channel Relay when enabled in System Settings...
    "%WORKBENCH_PYTHON%" "%ROOT%scripts\start_with_policy.py" --service mailbox_server --cwd "%ROOT%." -- "%ComSpec%" /d /c scripts\run_channel_relay.bat "%CHANNEL_RELAY_DIR%"
    if errorlevel 3 (
      echo Mailbox Channel Relay startup is disabled in System Settings.
    ) else (
      echo Waiting for Mailbox Channel Relay...
      "%WORKBENCH_PYTHON%" "%ROOT%scripts\wait_for_managed_service.py" --service mailbox_server --url "%CHANNEL_RELAY_URL%/health" --timeout 90
      if errorlevel 1 echo WARNING: Mailbox Channel Relay did not answer yet.
    )
  ) else (
    echo Mailbox Channel Relay launcher was not found at %CHANNEL_RELAY_DIR%\mailbox-server.cmd.
  )
) else (
  echo Mailbox Channel Relay is already running and will not be claimed by this launcher.
)

echo Checking ClawRouter on 127.0.0.1:%CLAWROUTER_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%CLAWROUTER_HEALTH_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>nul
if errorlevel 1 (
  echo Starting the local ClawRouter proxy on 127.0.0.1:%CLAWROUTER_PORT%...
  "%WORKBENCH_PYTHON%" "%ROOT%scripts\start_with_policy.py" --service clawrouter --cwd "%ROOT%." -- "%ComSpec%" /d /c scripts\run_clawrouter.bat %CLAWROUTER_PORT%
  if errorlevel 3 (
    echo ClawRouter startup is disabled in System Settings.
  ) else (
    echo Waiting for ClawRouter...
    "%WORKBENCH_PYTHON%" "%ROOT%scripts\wait_for_managed_service.py" --service clawrouter --url "%CLAWROUTER_HEALTH_URL%" --timeout 120
    if errorlevel 1 echo WARNING: ClawRouter did not answer yet. Check its configured process window.
  )
) else (
  echo ClawRouter is already running.
)

echo Checking OmniRoute on 127.0.0.1:%OMNIROUTE_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%OMNIROUTE_URL%/' -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>nul
if errorlevel 1 (
  echo Starting the local OmniRoute gateway on 127.0.0.1:%OMNIROUTE_PORT%...
  "%WORKBENCH_PYTHON%" "%ROOT%scripts\start_with_policy.py" --service omniroute --cwd "%ROOT%." -- "%ComSpec%" /d /c scripts\run_omniroute.bat %OMNIROUTE_PORT%
  if errorlevel 3 (
    echo OmniRoute startup is disabled in System Settings.
  ) else (
    echo Waiting for OmniRoute...
    "%WORKBENCH_PYTHON%" "%ROOT%scripts\wait_for_managed_service.py" --service omniroute --url "%OMNIROUTE_URL%/" --timeout 240
    if errorlevel 1 echo WARNING: OmniRoute did not answer yet. Check its configured process window.
  )
) else (
  echo OmniRoute is already running.
)

if exist "%WORKBENCH_PYTHON%" (
  "%WORKBENCH_PYTHON%" "%ROOT%scripts\bootstrap_omniroute.py" "%ROOT%workspaces\shared_library_system"
  if errorlevel 1 echo WARNING: OmniRoute endpoint-key setup failed. Configure it under Settings.
)

echo Starting the live-editing web interface on %BIND_IP%:%WEB_PORT%...
"%WORKBENCH_PYTHON%" "%ROOT%scripts\start_with_policy.py" --service workbench-web --cwd "%ROOT%." -- "%ComSpec%" /d /c scripts\run_vite_server.bat %BIND_IP% %WEB_PORT% %API_URL%

echo Waiting for the website...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(45); do { try { $r=Invoke-WebRequest -UseBasicParsing '%WEB_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 400 } while ((Get-Date) -lt $limit); exit 1"
if errorlevel 1 (
  echo WARNING: The web interface did not answer yet. Check the MeTTa Workbench Vite %WEB_PORT% window.
) else (
  start "" "%WEB_URL%"
)

echo.
echo The workbench is running locally at %WEB_URL%
echo API documentation is at %API_URL%/docs
echo ClawRouter is at %CLAWROUTER_URL%/v1 using blockrun/free by default.
echo OmniRoute is at %OMNIROUTE_URL%/v1 using auto/best-free by default.
echo Mailbox Channel Relay is at %CHANNEL_RELAY_URL% when enabled in System Settings.
echo Edit files under workbench\frontend\src or workbench\server;
echo the appropriate process reloads automatically.
echo Each API/Vite window shows the exact command to rerun after Ctrl+C.
echo Close the API, Vite, ClawRouter, and OmniRoute windows for this instance when you are finished.
echo.
pause
exit /b 0

:validate_port
set "PORT_VALUE=%~1"
set "PORT_LABEL=%~2"
set "BAD_PORT="
for /f "delims=0123456789" %%A in ("%PORT_VALUE%") do set "BAD_PORT=1"
if defined BAD_PORT (
  echo ERROR: Invalid %PORT_LABEL% port "%PORT_VALUE%". Use an integer from 1 through 65535.
  exit /b 1
)
set /a PORT_NUMBER=%PORT_VALUE% >nul 2>nul
if %PORT_NUMBER% LSS 1 (
  echo ERROR: Invalid %PORT_LABEL% port "%PORT_VALUE%". Use an integer from 1 through 65535.
  exit /b 1
)
if %PORT_NUMBER% GTR 65535 (
  echo ERROR: Invalid %PORT_LABEL% port "%PORT_VALUE%". Use an integer from 1 through 65535.
  exit /b 1
)
exit /b 0

:failed
echo.
echo Setup failed. Review the error above, then run this file again.
pause
exit /b 1
