@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" sandbox_start.py
) else (
  python sandbox_start.py
)
pause
