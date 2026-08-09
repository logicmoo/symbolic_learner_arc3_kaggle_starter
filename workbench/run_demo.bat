@echo off
setlocal EnableExtensions
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"
set "ROOT=%~dp0"

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
set "CLAWROUTER_PORT=3456"
set "CLAWROUTER_URL=http://127.0.0.1:%CLAWROUTER_PORT%"
set "CLAWROUTER_HEALTH_URL=%CLAWROUTER_URL%/health"

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

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo Creating the local Python environment...
  python -m venv "%ROOT%.venv"
  if errorlevel 1 goto :failed
)

"%ROOT%.venv\Scripts\python.exe" -c "import fastapi, pydantic, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Installing Python packages for the first run...
  "%ROOT%.venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%ROOT%server\requirements.txt"
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

echo Checking ClawRouter on 127.0.0.1:%CLAWROUTER_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing '%CLAWROUTER_HEALTH_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>nul
if errorlevel 1 (
  echo Starting the local ClawRouter proxy on 127.0.0.1:%CLAWROUTER_PORT%...
  start "ClawRouter %CLAWROUTER_PORT%" /D "%ROOT%" "%ComSpec%" /k scripts\run_clawrouter.bat %CLAWROUTER_PORT%
  echo Waiting for ClawRouter...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(120); do { try { $r=Invoke-WebRequest -UseBasicParsing '%CLAWROUTER_HEALTH_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $limit); exit 1"
  if errorlevel 1 (
    echo WARNING: ClawRouter did not answer yet. Check the ClawRouter %CLAWROUTER_PORT% window.
  )
) else (
  echo ClawRouter is already running.
)

echo Starting the local event backend on %BIND_IP%:%API_PORT%...
start "MeTTa Workbench API %API_PORT%" /D "%ROOT%" "%ComSpec%" /k scripts\run_api_server.bat %BIND_IP% %API_PORT%

echo Waiting for the backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(45); $url='%API_HEALTH_URL%'; do { try { $r=Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 400 } while ((Get-Date) -lt $limit); exit 1"
if errorlevel 1 (
  echo WARNING: The API did not answer yet. Check the MeTTa Workbench API %API_PORT% window.
)

echo Starting the live-editing web interface on %BIND_IP%:%WEB_PORT%...
start "MeTTa Workbench Vite %WEB_PORT%" /D "%ROOT%" "%ComSpec%" /k scripts\run_vite_server.bat %BIND_IP% %WEB_PORT% %API_URL%

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
echo Edit files under workbench\frontend\src or workbench\server;
echo the appropriate process reloads automatically.
echo Each API/Vite window shows the exact command to rerun after Ctrl+C.
echo Close the API, Vite, and ClawRouter windows for this instance when you are finished.
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
