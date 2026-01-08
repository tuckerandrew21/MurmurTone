@echo off
REM Build script for MurmurTone
REM Requires Python 3.11 installed at the standard location

SET PYTHON_311=C:\Users\tucke\AppData\Local\Programs\Python\Python311\python.exe
SET VENV_DIR=build_venv

echo === MurmurTone Build Script ===
echo.

REM Check if venv exists
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment...
    "%PYTHON_311%" -m venv "%VENV_DIR%"

    echo Installing dependencies...
    "%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt pyinstaller
)

REM Check if model is bundled
if not exist "models\tiny.en\model.bin" (
    echo.
    echo WARNING: Bundled model not found at models\tiny.en\
    echo The app will need to download the model on first run.
    echo.
    echo To bundle the model, run:
    echo   %VENV_DIR%\Scripts\python.exe -c "from faster_whisper import WhisperModel; WhisperModel('tiny.en')"
    echo   mkdir models\tiny.en
    echo   copy %%USERPROFILE%%\.cache\huggingface\hub\models--Systran--faster-whisper-tiny.en\snapshots\*\* models\tiny.en\
    echo.
)

echo Building with PyInstaller...
"%VENV_DIR%\Scripts\pyinstaller.exe" murmurtone.spec --noconfirm

echo.
echo === Build Complete ===
echo Output: dist\MurmurTone\
echo.
pause
