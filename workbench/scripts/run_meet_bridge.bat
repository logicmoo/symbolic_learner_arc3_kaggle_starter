@echo off
rem Google Meet STT bridge — always-on servant meeting + mailbox two-way.
rem Managed by the workbench Processes page (meet_caption_bridge.managed_service.json).
cd /d "%~dp0..\.."
".venv\Scripts\python.exe" scripts\meet_caption_bridge.py %*
