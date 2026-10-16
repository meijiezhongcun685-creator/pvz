@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
  echo.
  echo [ERROR] If you see an error above, take a screenshot and send it to me.
  pause
)
