@echo off
setlocal EnableExtensions

rem Change to the repository root regardless of the caller's current directory.
cd /d "%~dp0.."
if errorlevel 1 (
    echo ERROR: Unable to enter the repository root.
    exit /b 1
)

rem Use the project interpreter directly. Activation is unnecessary and this
rem avoids accidentally invoking the Microsoft Store python.exe alias.
set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo ERROR: The project virtual environment does not exist:
    echo     %CD%\.venv
    echo.
    echo Run this first:
    echo     scripts\setup_windows.bat
    echo.
    echo See README_WINDOWS.md for Python, long-path, Git, SWI-Prolog,
    echo PyCharm, UNC-path, and Microsoft Store alias troubleshooting.
    exit /b 1
)

"%VENV_PYTHON%" ".\scripts\interactive_runner.py" %*
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
