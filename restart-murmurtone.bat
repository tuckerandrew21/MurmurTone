@echo off
cd /d "c:\Users\tucke\Repositories\MurmurTone"

echo Killing existing MurmurTone processes...
powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.Path -and (Get-WmiObject Win32_Process -Filter \"ProcessId=$($_.Id)\").CommandLine -match 'murmurtone|settings_webview' } | Stop-Process -Force -ErrorAction SilentlyContinue"

timeout /t 2 /nobreak >nul

echo Starting MurmurTone...
start "" "C:\Users\tucke\AppData\Local\Programs\Python\Python312\pythonw.exe" murmurtone.py

timeout /t 2 /nobreak >nul

echo Opening Settings...
start "" "C:\Users\tucke\AppData\Local\Programs\Python\Python312\python.exe" settings_webview.py

echo Done.
