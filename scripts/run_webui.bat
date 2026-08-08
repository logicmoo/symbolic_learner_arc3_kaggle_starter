@echo off
setlocal
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"

rem Change to the repository root, regardless of where run.bat was launched.
cd /d "%~dp0.."

rem Activate the virtual environment.
call ".\venv\Scripts\activate.bat"

rem Run the interactive runner and pass through any command-line arguments.
python ".\scripts\run_webui.py" %*

set "EXIT_CODE=%ERRORLEVEL%"
endlocal & exit /b %EXIT_CODE%
