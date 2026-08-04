@echo off
setlocal EnableExtensions

rem Always operate from the repository root.
cd /d "%~dp0.."
if errorlevel 1 (
    echo ERROR: Unable to enter the repository root.
    exit /b 1
)

rem Do not let machine-wide Python path variables corrupt the selected base
rem interpreter or the project virtual environment.
set "PYTHONHOME="
set "PYTHONPATH="

echo.
echo === LogicMOO ARC3 Windows setup ===
echo Repository: %CD%
echo.

rem Prefer the Python launcher because it bypasses the Microsoft Store
rem python.exe app-execution alias. Prefer Python 3.12 for reproducibility,
rem then accept a newer Python 3 release, then fall back to a real python.exe.
set "PYTHON_COMMAND="

where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_COMMAND=py -3.12"
)

if not defined PYTHON_COMMAND (
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_COMMAND=py -3"
    )
)

if not defined PYTHON_COMMAND (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_COMMAND=python"
    )
)

if not defined PYTHON_COMMAND (
    echo ERROR: Python 3.12 or newer was not found.
    echo.
    echo Install 64-bit Python from python.org and select "Add python.exe to PATH".
    echo Recommended verification commands:
    echo     py -0p
    echo     py -3 --version
    echo.
    echo If Windows opens the Microsoft Store instead, disable the python.exe
    echo and python3.exe aliases under:
    echo     Settings ^> Apps ^> Advanced app settings ^> App execution aliases
    exit /b 1
)

echo Using: %PYTHON_COMMAND%
call %PYTHON_COMMAND% --version
if errorlevel 1 exit /b 1

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Creating .venv ...
    call %PYTHON_COMMAND% -m venv ".venv"
    if errorlevel 1 (
        echo ERROR: Unable to create .venv.
        exit /b 1
    )
) else (
    echo Reusing existing .venv.
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

"%VENV_PYTHON%" -c "import encodings, sys, sysconfig; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)" >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: The existing .venv is damaged or is not a usable virtual environment.
    echo Recreate it with:
    echo     rmdir /s /q .venv
    echo     scripts\setup_windows.bat
    exit /b 1
)

echo.
echo Updating pip, setuptools, and wheel ...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 exit /b 1

echo.
echo Installing the repository with all optional dependencies ...
"%VENV_PYTHON%" -m pip install -e ".[all]"
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    echo See README_WINDOWS.md for compiler, antivirus, and path troubleshooting.
    exit /b 1
)

rem The protected local Kaggle workflow expects the ARC-AGI-3 Agents framework
rem under vendor\ARC-AGI-3-Agents. Clone it when Git is available.
if not exist "vendor\ARC-AGI-3-Agents\.git" (
    where git >nul 2>nul
    if errorlevel 1 (
        echo.
        echo WARNING: Git was not found, so the optional ARC-AGI-3 Agents
        echo framework was not cloned. Install Git for Windows before using the
        echo protected local Kaggle workflow.
    ) else (
        echo.
        echo Cloning ARC-AGI-3 Agents framework ...
        if not exist "vendor" mkdir "vendor"
        git clone --depth 1 https://github.com/arcprize/ARC-AGI-3-Agents.git "vendor\ARC-AGI-3-Agents"
        if errorlevel 1 exit /b 1
    )
)

if exist "vendor\ARC-AGI-3-Agents" (
    echo.
    echo Slimming optional framework imports ...
    "%VENV_PYTHON%" "scripts\slim_framework.py"
    if errorlevel 1 exit /b 1
)

echo.
echo Verifying imports ...
"%VENV_PYTHON%" -c "import arc_agi, json_repair, numpy, PIL; print('Core Python imports: OK')"
if errorlevel 1 exit /b 1

echo.
echo Setup complete.
echo.
echo Start the terminal debugger with:
echo     scripts\interactive_runner.bat ls20
echo.
echo Start the browser debugger with:
echo     .venv\Scripts\python.exe scripts\run_webui.py --game ls20
echo.
exit /b 0
