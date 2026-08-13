@echo off
setlocal EnableExtensions
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"

set "ROOT=%~dp0..\.."
set "FREEROUTER_DIR=%ROOT%\vendor\freerouter"
set "FREEROUTER_CONFIG=%ROOT%\workbench\config\freerouter.config.json"

rem FreeRouter's server uses CLAWROUTER_PORT as its highest-priority port
rem override. Pin it here so a value inherited from setkeys or another router
rem cannot move this service onto ClawRouter's port 3456.
set "CLAWROUTER_PORT=18800"

title FreeRouter 18800
cd /d "%ROOT%"

if not exist "%FREEROUTER_DIR%\package.json" (
  if not exist "%ROOT%\vendor" mkdir "%ROOT%\vendor"
  echo Cloning the official FreeRouter source...
  git clone --depth 1 https://github.com/openfreerouter/freerouter.git "%FREEROUTER_DIR%"
  if errorlevel 1 exit /b 1
)

if not exist "%FREEROUTER_DIR%\node_modules" (
  echo Installing FreeRouter dependencies...
  pushd "%FREEROUTER_DIR%"
  call npm.cmd install
  if errorlevel 1 (popd & exit /b 1)
  popd
)

if not exist "%FREEROUTER_DIR%\dist\server.js" (
  echo Building FreeRouter...
  pushd "%FREEROUTER_DIR%"
  call npx.cmd tsc
  if errorlevel 1 (popd & exit /b 1)
  popd
)

if not defined OPENROUTER_API_KEY (
  echo ERROR: OPENROUTER_API_KEY is required for the free OpenRouter route.
  echo Define it in C:\snet\setkeys.bat and restart this launcher.
  exit /b 1
)

echo.
echo ============================================================
echo  FreeRouter local gateway
echo ============================================================
echo  OpenAI-compatible API: http://127.0.0.1:18800/v1
echo  Upstream route:         openrouter/openrouter/free
echo  Configuration:          %FREEROUTER_CONFIG%
echo ============================================================
echo.

cd /d "%FREEROUTER_DIR%"
node dist\server.js

echo.
echo FreeRouter stopped. Rerun this script to restart it.
echo.
