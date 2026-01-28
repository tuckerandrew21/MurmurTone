# Settings Search Guide

The MurmurTone settings GUI now includes a powerful search feature that filters settings across all tabs in real-time.

## How to Use

1. Type in the search box at the top of the settings window
2. Settings matching your query will remain visible
3. Non-matching settings will be hidden
4. The GUI automatically switches to the first tab containing matches
5. Clear the search box to show all settings again

## Searchable Terms by Tab

### Tab 1: General
- **Hotkey**: hotkey, keyboard shortcut, key, scroll lock, pause
- **Paste Mode**: paste mode, clipboard, direct typing, paste, automatic
- **Silence**: silence, timeout, auto stop, duration
- **Preview**: preview, window, overlay, show, position, corner, placement, auto hide, delay, theme, dark, light, font, size
- **Startup**: startup, start with windows, boot, launch

### Tab 2: Audio & Recording
- **Input Device**: input device, microphone, audio input
- **Noise Gate**: noise gate, threshold, filter, background noise, level, meter, test, db
- **Audio Feedback**: audio feedback, sounds, beep, chime, processing, success, error, command, sound
- **Volume**: volume, loudness, sound volume

### Tab 3: Recognition & Model
- **Model**: model, size, tiny, base, small, medium, accuracy
- **Processing**: processing, cpu, gpu, cuda, device, compute
- **GPU Status**: gpu, status, cuda, graphics card, install, gpu support, nvidia
- **Vocabulary**: vocabulary, custom, jargon, names, acronyms

### Tab 4: Text Processing
- **Voice Commands**: voice commands, punctuation, period, comma, new line
- **Scratch That**: scratch that, delete, undo, remove
- **Filler Removal**: filler, um, uh, removal, filter, aggressive, like
- **Dictionary**: dictionary, replace, words, phrases, corrections
- **Commands**: commands, custom, trigger, expand, shortcuts

### Tab 5: Account & Advanced
- **AI Cleanup**: ai, ollama, cleanup, grammar, formality, local, cleanup mode, both
- **History**: history, transcription, recent, log
- **About**: about, version, help, updates

## Examples

- Type **"gpu"** → Shows GPU status, processing mode, and CUDA install options (Tab 3)
- Type **"paste"** → Shows paste mode settings (Tab 1)
- Type **"noise"** → Shows noise gate settings and level meter (Tab 2)
- Type **"filler"** → Shows filler removal settings (Tab 4)
- Type **"preview"** → Shows all preview window settings (Tab 1)
- Type **"ollama"** → Shows AI cleanup settings (Tab 5)

## Technical Details

- Search is case-insensitive
- Partial matches work (e.g., "hot" matches "hotkey")
- Multiple settings can match the same search term
- Search indexes 40+ major settings across all 5 tabs
