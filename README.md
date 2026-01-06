# Voice Typer

Simple voice-to-text tool using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Press a hotkey to record, release to transcribe and type into any application.

## Usage

1. Run `start.bat` (or `python voice_typer.py`)
2. Press **Ctrl+Shift+Space** to start recording
3. Release any key to stop and transcribe
4. Text is automatically typed into the active window

## Requirements

- Python 3.11 (recommended)
- Windows (uses pynput for keyboard simulation)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `voice_typer.py` to change:
- `MODEL_SIZE` - Options: `tiny.en`, `base.en`, `small.en`, `medium.en` (larger = more accurate but slower)
- `SAMPLE_RATE` - Audio sample rate (default: 16000)

## Dependencies

- faster-whisper - Local Whisper speech recognition
- pynput - Keyboard listening and typing simulation
- sounddevice - Audio recording
- numpy - Audio processing
