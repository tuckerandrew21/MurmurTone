"""
Simple Voice Typer - Press Ctrl+Shift+Space to record, release to transcribe and type.
"""
import sys
import threading
import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard
from pynput.keyboard import Controller

# Configuration
MODEL_SIZE = "tiny.en"  # Options: tiny.en, base.en, small.en, medium.en
SAMPLE_RATE = 16000

print("Loading Whisper model (this may take a minute)...", flush=True)
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print("Model loaded!", flush=True)
print("Press Ctrl+Shift+Space to start recording.", flush=True)
print("Release to stop and transcribe.", flush=True)
print("Press Ctrl+C to quit.", flush=True)

keyboard_controller = Controller()
current_keys = set()
is_recording = False
audio_data = []
stream = None

def audio_callback(indata, frames, time_info, status):
    global audio_data, is_recording
    if is_recording:
        audio_data.append(indata.copy())

def start_recording():
    global is_recording, audio_data, stream
    if is_recording:
        return
    print("\n>> Recording...", flush=True)
    is_recording = True
    audio_data = []
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.float32, callback=audio_callback)
    stream.start()

def stop_recording():
    global is_recording, stream, audio_data
    if not is_recording:
        return
    is_recording = False
    if stream:
        stream.stop()
        stream.close()
        stream = None

    if not audio_data:
        print("No audio.", flush=True)
        return

    print(">> Transcribing...", flush=True)
    audio = np.concatenate(audio_data, axis=0).flatten()

    segments, _ = model.transcribe(audio, language="en")
    text = "".join(segment.text for segment in segments).strip()

    if text:
        print(f">> Typing: {text}", flush=True)
        time.sleep(0.1)
        keyboard_controller.type(text + " ")
    else:
        print(">> No speech detected.", flush=True)

    print("\nReady. Press Ctrl+Shift+Space.", flush=True)

def on_press(key):
    global current_keys
    current_keys.add(key)
    if keyboard.Key.ctrl_l in current_keys and keyboard.Key.shift in current_keys and keyboard.Key.space in current_keys:
        if not is_recording:
            start_recording()

def on_release(key):
    global current_keys
    current_keys.discard(key)
    if is_recording:
        threading.Thread(target=stop_recording).start()

# Main loop
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\nExiting.", flush=True)
