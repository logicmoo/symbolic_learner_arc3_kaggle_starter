@echo off
setlocal
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"

cd /d "%~dp0.."
if errorlevel 1 exit /b %errorlevel%

if not exist ".codex-commit-message.txt" (
  echo Missing .codex-commit-message.txt 1>&2
  exit /b 2
)

git diff --cached --quiet --exit-code
if not errorlevel 1 (
  echo Nothing is staged; refusing to create an empty commit. 1>&2
  exit /b 3
)

git diff --cached --check
if errorlevel 1 exit /b %errorlevel%

git commit -F ".codex-commit-message.txt"
exit /b %errorlevel%
