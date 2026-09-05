@echo off
REM Regenerate the Markdown API reference under docs\api\ for all first-party packages.
REM Usage:  scripts\build_api_docs.bat   (from anywhere)
setlocal
set "REPO=%~dp0.."
pushd "%REPO%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
"%PY%" scripts\build_api_docs.py
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
