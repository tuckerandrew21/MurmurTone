# MurmurTone

**Your voice, locally.** A private, lightweight voice-to-text tool for Windows that respects your privacy by running entirely offline.

Press your hotkey to record, release to transcribe, and your words appear instantly—no cloud, no tracking, no delays.

Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for fast, accurate, local speech recognition.

---

## 🎉 Try MurmurTone Free for 14 Days

**[Download for Windows →](https://murmurtone.com/install)**

- ✅ No credit card required
- ✅ Full access to all features
- ✅ 100% offline processing
- ✅ After trial: $49/year (Early Access pricing — lock in forever)

---

## Features

### Core Features
- **🔒 100% Offline** - Your voice never leaves your machine
- **⚡ Instant Transcription** - Press hotkey, speak, release — words appear instantly
- **🎛️ System Tray App** - Runs quietly in the background
- **⌨️ Customizable Hotkey** - Set any key combination you want
- **🎤 Multiple Models** - Choose between speed (tiny) and accuracy (medium)
- **🚀 GPU Acceleration** - Optional CUDA support for faster transcription
- **🔇 Noise Gate** - Filter out background noise automatically
- **🔊 Audio Feedback** - Distinct sounds for recording, processing, success, and error states
- **🌍 Auto-Language Detection** - English or auto-detect 18+ languages
- **⚙️ Settings GUI** - Easy configuration, no code editing required

### Advanced Features (Phase 3+)
- **🤖 AI Text Cleanup** - Local Ollama integration for grammar correction and formality adjustment
- **🌐 Translation Mode** - Speak any language, output English
- **🎵 Audio File Transcription** - Transcribe MP3, WAV, M4A files
- **📚 Custom Vocabulary** - Add technical terms, names, acronyms for better recognition
- **✍️ Voice Commands** - Built-in commands: "period", "new line", "scratch that", etc.
- **🔠 Case Manipulation** - "capitalize that", "uppercase that", "lowercase that"
- **⌫ Delete Last Word** - "delete last word" for granular corrections
- **📝 Custom Dictionary** - Create text replacements and shortcuts
- **🎨 Preview Window** - Optional floating preview of transcription

---

## Installation

### For End Users (Recommended)

1. **Download the installer:** [MurmurTone-Setup.exe](https://murmurtone.com/install)
2. **Run the installer** - Follow the on-screen instructions
3. **Launch MurmurTone** - Find the icon in your system tray (bottom-right)
4. **Configure your hotkey** - Right-click tray icon → Settings
5. **Start transcribing!** - Press your hotkey and speak

**System Requirements:**
- Windows 10 (19041+) or Windows 11
- 4 GB RAM (8 GB recommended)
- 500 MB disk space
- Microphone (USB or built-in)
- Optional: NVIDIA GPU for faster transcription

### For Developers

#### Setup from Source

```bash
git clone https://github.com/tuckerandrew21/murmurtone.git
cd murmurtone
pip install -r requirements.txt
python murmurtone.py
```

#### GPU Acceleration (Optional)

```bash
pip install -r requirements-gpu.txt
```

**Requirements:**
- NVIDIA GPU with CUDA support
- CUDA 12.x compatible drivers

#### Running Tests

```bash
pytest tests/ -v
```

All **289 tests** should pass.

#### Building from Source

```bash
# Automated build (downloads model, builds EXE, creates installer)
build.bat

# Manual steps
python prepare_model.py      # Download and bundle tiny.en model
pyinstaller murmurtone.spec   # Build EXE
iscc installer.iss            # Create installer (requires Inno Setup)
```

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed build instructions.

---

## Usage

### Basic Transcription

1. **Launch MurmurTone** - Look for the icon in system tray
2. **Press hotkey** (default: **Ctrl+Shift+Space**) to start recording
3. **Speak clearly** into your microphone
4. **Release hotkey** to stop recording and transcribe
5. **Text appears** automatically in your active window

### Voice Commands

While recording, say these commands:

| Command | Result |
|---------|--------|
| "period" | . |
| "comma" | , |
| "question mark" | ? |
| "exclamation mark" | ! |
| "new line" | ↵ |
| "new paragraph" | ↵↵ |
| "scratch that" | Delete last transcription |
| "delete last word" | Delete one word |
| "capitalize that" | Capitalize last word |
| "uppercase that" | UPPERCASE last word |
| "lowercase that" | lowercase last word |

### AI Text Cleanup (Ollama)

1. **Install Ollama** from [ollama.com](https://ollama.com)
2. **Download a model**: `ollama pull llama3.2:3b`
3. **Enable in Settings** → AI Text Cleanup
4. **Choose mode**: Grammar only, Formality only, or Both
5. **Set formality level**: Casual, Professional, or Formal

Transcriptions will be automatically cleaned up using local AI (no cloud!).

### Translation Mode

1. **Open Settings** → Translation Mode
2. **Enable translation** and select source language (or auto-detect)
3. **Speak in any language**, output English
4. Works with 18+ languages

### Audio File Transcription

1. **Right-click tray icon** → Transcribe Audio File
2. **Select MP3, WAV, or M4A file**
3. **Transcription saves to text file** (opens automatically)

---

## Configuration

Right-click the tray icon and select **Settings** to configure:

### General Settings
| Setting | Options | Description |
|---------|---------|-------------|
| Model Size | tiny.en, base.en, small.en, medium.en | Larger = more accurate but slower |
| Processing Mode | Auto, CPU, GPU-Balanced, GPU-Quality | Device and compute type |
| Language | en, auto, es, fr, de, etc. | English only or auto-detect |
| Hotkey | Any combination | Click "Set Hotkey" and press your keys |

### Audio Settings
| Setting | Options | Description |
|---------|---------|-------------|
| Input Device | System default or specific device | Choose microphone |
| Noise Gate | On/Off, -60 to -20 dB | Filter out background noise |
| Audio Feedback | Processing, Success, Error, Command | Individual sound toggles |

### Advanced Features
| Setting | Description |
|---------|-------------|
| Custom Vocabulary | Add technical terms, names, acronyms |
| Custom Dictionary | Text replacements (e.g., "btw" → "by the way") |
| Custom Commands | Voice-activated shortcuts |
| AI Cleanup | Grammar correction and formality adjustment (Ollama) |
| Translation | Speak any language, output English |

Settings are saved automatically and persist between sessions.

---

## Model Comparison

| Model | Speed | Accuracy | RAM Usage | Best For |
|-------|-------|----------|-----------|----------|
| tiny.en | Fastest | Good | ~1 GB | Quick notes, chat |
| base.en | Fast | Better | ~1.5 GB | General use |
| small.en | Medium | Great | ~2.5 GB | Documentation |
| medium.en | Slower | Best | ~5 GB | Professional transcription |

**Recommendation:** Start with `base.en` for best balance of speed and accuracy.

---

## Pricing

### 14-Day Free Trial
- ✅ **All features unlocked**
- ✅ **No credit card required**
- ✅ **No limitations**

### Pro License: $49/year
- ✅ **Early Access Pricing** - Lock in this rate forever
- ✅ **Unlimited transcription**
- ✅ **All features included**
- ✅ **100% offline**
- ✅ **Priority support**

**After trial:** You'll be prompted to purchase a Pro license. Most competitors charge $96-180/year.

---

## Troubleshooting

### App doesn't start
- Check system tray (bottom-right) - icon may be hidden
- Run from Start Menu: MurmurTone
- Check logs: `%APPDATA%\MurmurTone\murmurtone.log`

### Transcription not working
- Verify microphone is working (test in Settings)
- Check noise gate threshold (try disabling temporarily)
- Ensure model has downloaded (first run takes 2-5 minutes)

### GPU not detected
- Install CUDA 12.x drivers from NVIDIA
- Restart application after installing drivers
- Check Settings → Processing Mode → GPU options should be enabled

### SmartScreen warning during installation
- This is normal for new applications
- Click "More info" → "Run anyway"
- We are working on code signing to eliminate this warning

### More help
- [Open an issue](https://github.com/tuckerandrew21/murmurtone/issues)
- [Email support](mailto:support@murmurtone.com)

---

## Development

### Project Structure

```
murmurtone/
├── murmurtone.py          # Main application
├── config.py              # Configuration management
├── license.py             # Trial and license validation
├── text_processor.py      # Voice commands, filler removal
├── ai_cleanup.py          # Ollama AI cleanup integration
├── settings_gui.py        # Settings window
├── preview_window.py      # Transcription preview overlay
├── clipboard_utils.py     # Clipboard operations (Windows)
├── stats.py               # Usage statistics
├── logger.py              # Logging setup
├── tests/                 # Test suite (289 tests)
├── murmurtone.spec        # PyInstaller build config
├── installer.iss          # Inno Setup installer config
├── build.bat              # Automated build script
├── prepare_model.py       # Model bundling script
└── requirements.txt       # Python dependencies
```

### Running from Source

```bash
# Standard run
python murmurtone.py

# Open settings on startup
python murmurtone.py --settings

# Development mode (more logging)
python murmurtone.py
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_license.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Building

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for comprehensive build instructions.

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## Dependencies

### Core Dependencies
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Local Whisper speech recognition
- [ctranslate2](https://github.com/OpenNMT/CTranslate2) - Fast inference engine
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard listening and simulation
- [pystray](https://github.com/moses-palmer/pystray) - System tray icon
- [sounddevice](https://python-sounddevice.readthedocs.io/) - Audio recording
- numpy - Audio processing
- Pillow - Icon handling
- requests - License validation

### Optional Dependencies
- torch + CUDA - GPU acceleration
- Ollama - Local AI text cleanup

See `requirements.txt` for complete list with pinned versions.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

Third-party licenses: [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)

---

## Acknowledgments

- Powered by [OpenAI Whisper](https://github.com/openai/whisper) via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Built with [Claude Code](https://claude.com/claude-code) AI coding assistant
- Inspired by SuperWhisper, Wispr Flow, and VoiceInk

---

## Links

- **Website:** [murmurtone.com](https://murmurtone.com)
- **Download:** [murmurtone.com/install](https://murmurtone.com/install)
- **GitHub:** [github.com/tuckerandrew21/murmurtone](https://github.com/tuckerandrew21/murmurtone)
- **Issues:** [github.com/tuckerandrew21/murmurtone/issues](https://github.com/tuckerandrew21/murmurtone/issues)
- **Email:** [support@murmurtone.com](mailto:support@murmurtone.com)

---

**MurmurTone** - Your voice, locally. 🎤
