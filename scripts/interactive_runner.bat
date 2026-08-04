@echo off
setlocal EnableExtensions

rem Change to the repository root regardless of the caller's current directory.
cd /d "%~dp0.."
if errorlevel 1 (
    echo ERROR: Unable to enter the repository root.
    exit /b 1
)

rem A project virtual environment must not inherit a machine-wide PYTHONHOME or
rem PYTHONPATH. Either variable can make Python search an unrelated installation
rem and print "Could not find platform independent libraries ^<prefix^>".
set "PYTHONHOME="
set "PYTHONPATH="

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

rem Detect a damaged or non-venv interpreter before attempting package repairs.
"%VENV_PYTHON%" -c "import encodings, sys, sysconfig; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)" >nul 2>nul
if errorlevel 1 (
    echo ERROR: .venv is damaged or is not a usable Python virtual environment.
    echo.
    echo Recreate it with:
    echo     rmdir /s /q .venv
    echo     scripts\setup_windows.bat
    exit /b 1
)

rem A git pull can add a new required dependency to pyproject.toml. Repair the
rem editable base installation automatically instead of crashing on import.
"%VENV_PYTHON%" -c "import json_repair" >nul 2>nul
if errorlevel 1 (
    echo.
    echo Updating core project dependencies in .venv ...
    "%VENV_PYTHON%" -m pip install -e "."
    if errorlevel 1 (
        echo.
        echo ERROR: Unable to update the project dependencies.
        echo Run this exact Command Prompt command:
        echo     .venv\Scripts\python.exe -m pip install -e ".[all]"
        echo.
        echo Command Prompt requires double quotes here; single quotes are
        echo passed literally and make '.^[all^]' an invalid requirement.
        exit /b 1
    )
)

"%VENV_PYTHON%" ".\scripts\interactive_runner.py" %*
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
