@echo off
REM Start OrderHub servers (Windows batch script)
echo Starting OrderHub servers...
cd /d "%~dp0"
python start_servers.py
pause

