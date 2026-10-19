@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Start START_SERVER.bat or START_SANDBOX.bat.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.11 or newer and check your connection.
pause
exit /b 1
