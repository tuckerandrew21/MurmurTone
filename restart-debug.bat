@echo off
cd /d "%~dp0"
echo Stopping existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

echo Starting MurmurTone (with console for debugging)...
start "" "%~dp0venv\Scripts\python.exe" murmurtone.py
timeout /t 2 /nobreak >nul

echo Opening settings...
start "" "%~dp0venv\Scripts\python.exe" settings_gui.py

echo Opening log file...
timeout /t 1 /nobreak >nul
start "" notepad.exe "%APPDATA%\MurmurTone\murmurtone.log"

echo.
echo Debug mode: Console windows will show any errors
echo Press any key to exit this window...
pause >nul
