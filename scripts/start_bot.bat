@echo off
rem Navigate to project root directory
cd /d "%~dp0.."

rem Use virtual environment if available, otherwise fall back to system python
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m bot.main
) else (
    python -m bot.main
)
