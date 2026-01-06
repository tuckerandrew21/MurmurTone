@echo off
title Voice Typer
cd /d "%~dp0"
"..\whisper-writer\venv311\Scripts\python.exe" voice_typer.py
pause
