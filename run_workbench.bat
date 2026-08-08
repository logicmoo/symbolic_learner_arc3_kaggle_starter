@echo off
if exist "C:\snet\setkeys.bat" call "C:\snet\setkeys.bat"
call "%~dp0workbench\run_demo.bat" %*
