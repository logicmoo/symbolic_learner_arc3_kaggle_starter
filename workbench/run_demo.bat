@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"

title MeTTaSymbolicLearnerWorkbench Launcher
echo.
echo  MeTTaSymbolicLearnerWorkbench - local development
echo  -----------------------------------------------
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

echo Starting the local event backend...
start "MeTTa Workbench API" /D "%ROOT%server" "%ComSpec%" /k ""%ROOT%.venv\Scripts\python.exe" -m uvicorn app:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for the backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(45); do { try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 400 } while ((Get-Date) -lt $limit); exit 1"
if errorlevel 1 (
  echo WARNING: The API did not answer yet. Check the MeTTa Workbench API window.
)

echo Starting the live-editing web interface...
start "MeTTa Workbench Web" /D "%ROOT%frontend" "%ComSpec%" /k npm run dev

echo Waiting for the website...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$limit=(Get-Date).AddSeconds(45); do { try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173 -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 400 } while ((Get-Date) -lt $limit); exit 1"
if errorlevel 1 (
  echo WARNING: The web interface did not answer yet. Check the MeTTa Workbench Web window.
) else (
  start "" "http://127.0.0.1:5173/"
)

echo.
echo The workbench is running locally at http://127.0.0.1:5173/
echo Edit files under workbench\frontend\src or workbench\server;
echo the appropriate process reloads automatically.
echo Close the two server windows when you are finished.
echo.
pause
exit /b 0

:failed
echo.
echo Setup failed. Review the error above, then run this file again.
pause
exit /b 1
