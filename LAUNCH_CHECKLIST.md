# MurmurTone v1.0 Launch Checklist

## ✅ Track 1: Monetization & Licensing (COMPLETE)

- [x] Create `license.py` module with trial tracking and LemonSqueezy integration
- [x] Add license/trial fields to `config.py`
- [x] Update Settings GUI with License tab
- [x] Implement trial expiration check on app startup
- [x] Create upgrade dialog for expired trials
- [x] Write comprehensive test suite for license system (23 tests)
- [x] All 289 tests passing

**Deliverables:**
- `license.py` - Trial and LemonSqueezy license validation
- `tests/test_license.py` - Comprehensive test coverage
- License tab in Settings GUI with activation UI
- Blocking upgrade dialog on trial expiration

## ✅ Track 3: Build & Packaging (COMPLETE)

- [x] Create `prepare_model.py` script to bundle tiny.en model
- [x] Create `installer.iss` (Inno Setup installer config)
- [x] Update `build.bat` with 3-step automated build process
- [x] Document code signing process in `CODE_SIGNING.md`
- [x] Create comprehensive `BUILD_GUIDE.md`
- [x] PyInstaller spec already configured to bundle model

**Deliverables:**
- `prepare_model.py` - Downloads and prepares tiny.en for bundling (~150MB)
- `installer.iss` - Professional Windows installer with shortcuts, uninstaller
- `build.bat` - One-command build (model + EXE + installer)
- `CODE_SIGNING.md` - Complete guide to EV certificate acquisition and signing
- `BUILD_GUIDE.md` - Comprehensive build documentation

**Build Command:**
```bash
build.bat  # Prepares model, builds EXE, creates installer
```

## ✅ Track 4: Website & Documentation (COMPLETE)

- [x] Update `landing-page.html` with $49/year pricing and trial messaging
- [x] Create `install.html` download page with system requirements
- [x] Completely rewrite `README.md` with launch information
- [x] Add pricing section to README
- [x] Add troubleshooting section to README
- [x] Document all Phase 3 features

**Deliverables:**
- `landing-page.html` - Updated with Early Access pricing, trial CTA
- `install.html` - Complete download page with installation instructions
- `README.md` - 370-line comprehensive documentation

## ✅ Track 2: Integration Testing (AUTOMATED COMPLETE)

**Environment**: Python 3.12.10 installed and configured

### ✅ Automated Testing (COMPLETE)

**Unit Tests**: 289/289 passing (1.13s)

- AI cleanup module (26), Clipboard utilities (11), Configuration (28), Custom commands (14)
- File transcription (14), License system (25), Post-processing (23), Settings GUI (17)
- Translation mode (15), Voice commands (42), Custom vocabulary (9), Other modules (105)

**Integration Tests**: 11/11 passing (`test_track2_live.py`)

1. ✅ License System - Trial status, countdown, expiration detection
2. ✅ Trial Expiration Scenario - Expired trial (15 days ago)
3. ✅ Settings Persistence - Config save/load, all 47 settings
4. ✅ Custom Vocabulary - Configuration storage
5. ✅ Voice Command Logic - All 5 commands verified
6. ✅ AI Cleanup System - Ollama detection, prompt generation
7. ✅ Translation Configuration - Settings validation
8. ✅ Audio File Support - Format support, WAV generation
9. ✅ Configuration Defaults - All settings defined
10. ✅ Hotkey Parsing - String representation
11. ✅ Startup Configuration - Windows integration

**Verified**:

- ✅ App launch with Python 3.12
- ✅ Model loading (small.en with CUDA/float16)
- ✅ License trial countdown (14 days from first launch)
- ✅ Settings persistence in AppData\Roaming\MurmurTone
- ✅ System tray integration
- ✅ All feature flags functional

**Documentation**: Full report in [TRACK2_TESTING.md](TRACK2_TESTING.md)

### ⏳ Manual Testing Required (PENDING)

These features require microphone input and user interaction:

**Core Features**:

- [ ] Push-to-talk recording (Scroll Lock key)
- [ ] Auto-stop recording (silence detection)
- [ ] Voice command: "scratch that"
- [ ] Voice command: "capitalize that"
- [ ] Voice command: "uppercase that"
- [ ] Voice command: "lowercase that"
- [ ] Voice command: "delete last word"

**Advanced Features**:

- [ ] Custom vocabulary with technical terms
- [ ] Audio file transcription (MP3/WAV/M4A)
- [ ] Translation mode (Spanish→English, auto-detect)
- [ ] AI cleanup with Ollama (requires Ollama installation)
- [ ] License activation flow UI
- [ ] Trial expiration dialog

**Build Testing** (after `build.bat`):

- [ ] Install on clean Windows 10 VM
- [ ] Install on clean Windows 11 VM
- [ ] Verify SmartScreen behavior
- [ ] Test all core features in production build

**Priority**: High - Manual testing recommended before public launch

## ⚙️ Phase 8: Post-Launch UX Improvements (IN PROGRESS)

### Settings Window Launch
- [x] Install customtkinter dependency in venv
- [x] Fix settings_gui.py import errors
- [x] Add enhanced error logging for subprocess launches
- [x] Update restart.bat to launch app + GUI + log file
- [x] Create restart-debug.bat for troubleshooting

### Tray Icon Improvements
- [x] Create white logo PNG for icon overlays
- [x] Simplify double-click handler (remove manual timing)
- [ ] Fix icon appearance in system tray (circular with transparency)
- [ ] Fix icon appearance in settings window

**Status**: Settings GUI launches successfully. Icon design needs refinement.

**Next**: Investigate icon rendering to match V1 brand design (circular teal/red with transparent background).

## 🚀 Track 5: Launch Preparation (PENDING)

### Code Signing ($249/year - Optional but Recommended)
- [ ] Order EV code signing certificate from Sectigo ($249/year)
- [ ] Complete business validation (2-5 days)
- [ ] Receive USB token (2-3 days shipping)
- [ ] Sign installer before public release

**Benefit:** Eliminates SmartScreen warnings (prevents 20-30% abandonment)
**Timeline:** 10-14 days from order to signed build
**See:** [CODE_SIGNING.md](CODE_SIGNING.md) for complete guide

### LemonSqueezy Setup
- [ ] Create LemonSqueezy account at [lemonsqueezy.com](https://lemonsqueezy.com)
- [ ] Create product: "MurmurTone Pro" - $49/year subscription
- [ ] Configure webhooks for license validation
- [ ] Test purchase flow with test mode
- [ ] Update `license.py` with production API keys
- [ ] Set early access end date (launch date + 6 months)

### Domain & Hosting
- [ ] **Register murmurtone.com domain** (Namecheap, Cloudflare, etc.)
- [ ] **Deploy landing page** (Vercel, Cloudflare Pages, or Netlify)
  - Upload `landing-page.html` as index.html
  - Upload `install.html`
  - Connect domain
- [ ] **Set up email** forwarding (support@murmurtone.com)

### GitHub Repository
- [ ] **Push all commits to GitHub**
  ```bash
  git add .
  git commit -m "feat: add license system, installer, and updated docs"
  git push origin master
  ```
- [ ] **Rename repository** to `murmurtone`
  - Settings → General → Repository name
  - Update all URLs in documentation
- [ ] **Create v1.0.0 Release**
  - Tag: `v1.0.0`
  - Upload signed installer: `MurmurTone-1.0.0-Setup.exe`
  - Release notes (see below)

### Build & Test
- [ ] **Run build.bat** to create installer
  ```bash
  build.bat
  ```
- [ ] **Test installer** on clean Windows 10 VM
- [ ] **Test installer** on clean Windows 11 VM
- [ ] **Verify no crashes** during installation
- [ ] **Test app startup** and first-run experience
- [ ] **Verify trial countdown** displays correctly in Settings

### Marketing Materials (Optional)
- [ ] Create demo video showing push-to-talk workflow
- [ ] Take screenshots for landing page
- [ ] Write blog post announcing launch
- [ ] Prepare Product Hunt listing
- [ ] Prepare Reddit post (/r/software, /r/privacy, /r/productivity)

---

## Domain Status

- **murmurtone.com**: Available (verified via WHOIS)
- **Trademark**: No conflicts found in USPTO search
- **Email**: Set up support@murmurtone.com forwarding after domain purchase

---

## Pricing Strategy (Finalized)

### Trial
- **Duration:** 14 days
- **Features:** All features unlocked
- **Credit Card:** Not required
- **After Trial:** Prompt to purchase Pro license

### Pro License
- **Price:** $49/year
- **Early Access:** "Lock in this rate forever" messaging
- **Timing:** Price may increase after 6 months for new customers
- **Competitor Pricing:** Most charge $96-180/year (we're 52% cheaper)

### Messaging
- "Try free for 14 days. No credit card required."
- "Early Access: $49/year — Lock in this rate forever"
- "Most competitors: $96-180/year. MurmurTone: $49/year (52% less)"

---

## Files Ready for Launch

### Core Application
| File | Purpose | Status |
|------|---------|--------|
| `murmurtone.py` | Main application | ✅ Complete |
| `license.py` | Trial & license validation | ✅ Complete |
| `config.py` | Configuration + license fields | ✅ Complete |
| `settings_gui.py` | Settings window + License tab | ✅ Complete |

### Build System
| File | Purpose | Status |
|------|---------|--------|
| `prepare_model.py` | Bundle tiny.en model | ✅ Complete |
| `build.bat` | Automated build script | ✅ Complete |
| `murmurtone.spec` | PyInstaller config | ✅ Complete |
| `installer.iss` | Inno Setup config | ✅ Complete |

### Documentation
| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Main documentation | ✅ Complete |
| `BUILD_GUIDE.md` | Build instructions | ✅ Complete |
| `CODE_SIGNING.md` | Signing guide | ✅ Complete |
| `BRAND_POSITIONING.md` | Brand strategy | ✅ Complete |
| `COMPETITIVE_ANALYSIS.md` | Market analysis | ✅ Complete |

### Website
| File | Purpose | Status |
|------|---------|--------|
| `landing-page.html` | Homepage | ✅ Complete |
| `install.html` | Download page | ✅ Complete |

---

## Release Notes Template (v1.0.0)

```markdown
# MurmurTone v1.0.0

**Your voice, locally.** The first release of MurmurTone, a 100% offline voice-to-text tool for Windows.

## 🎉 Try Free for 14 Days

Download and try all features free for 14 days. No credit card required.

**After trial:** Continue with Pro license for $49/year (Early Access pricing)

## ✨ Features

### Core Features
- ⚡ **Instant Transcription** - Press hotkey, speak, release
- 🔒 **100% Offline** - Your voice never leaves your machine
- 🎛️ **Multiple Models** - Choose between speed (tiny) and accuracy (medium)
- 🚀 **GPU Acceleration** - Optional CUDA support
- 🔇 **Noise Gate** - Filter background noise

### Advanced Features
- 🤖 **AI Text Cleanup** - Local Ollama integration for grammar/formality
- 🌐 **Translation Mode** - Speak any language, output English
- 🎵 **Audio File Transcription** - Transcribe MP3, WAV, M4A files
- 📚 **Custom Vocabulary** - Add technical terms for better recognition
- ✍️ **Voice Commands** - "period", "new line", "scratch that", etc.
- 🔠 **Case Manipulation** - "capitalize/uppercase/lowercase that"
- ⌫ **Delete Last Word** - Granular corrections

## 📦 Installation

1. Download `MurmurTone-1.0.0-Setup.exe`
2. Run installer (see note about SmartScreen below)
3. Launch from Start Menu or system tray
4. Configure hotkey in Settings
5. Start transcribing!

**Note:** Windows SmartScreen may show a warning (normal for new apps). We're working on code signing to eliminate this.

## 📋 System Requirements

- Windows 10 (19041+) or Windows 11
- 4 GB RAM (8 GB recommended)
- 500 MB disk space
- Microphone (USB or built-in)
- Optional: NVIDIA GPU for faster transcription

## 🐛 Known Issues

- SmartScreen warning during installation (will be resolved with code signing)
- First startup downloads model (~150MB) if not bundled
- GPU detection may require CUDA 12.x drivers

## 📝 Full Changelog

See [README.md](https://github.com/tuckerandrew21/murmurtone) for complete feature list and documentation.

## 🙏 Acknowledgments

Powered by OpenAI Whisper via faster-whisper. Built with Claude Code.
```

---

## Pre-Launch Quick Reference

### Build Command
```bash
build.bat
```

### Test Checklist
- [ ] Install on clean Windows 10 VM
- [ ] Install on clean Windows 11 VM
- [ ] Test first-run experience (model download or bundled)
- [ ] Test push-to-talk transcription
- [ ] Test trial countdown in Settings → License
- [ ] Test Settings GUI scrollability
- [ ] Test audio file transcription
- [ ] Test AI cleanup (if Ollama installed)
- [ ] Test translation mode
- [ ] Verify no crashes or errors in logs

### Launch Day Checklist
1. Order EV certificate (if doing code signing - 10-14 days)
2. Register murmurtone.com domain
3. Deploy landing page + install page
4. Set up LemonSqueezy product + webhooks
5. Build and sign installer (if certificate ready)
6. Create GitHub Release v1.0.0
7. Update all URLs in documentation to production
8. Test purchase flow end-to-end
9. Monitor error logs and user feedback

---

## Estimated Timeline

### With Code Signing (Recommended)
- **Now:** Order EV certificate from Sectigo ($249/year)
- **Day 2-5:** Complete business validation
- **Day 5-8:** Receive USB token via mail
- **Day 8:** Build and sign installer
- **Day 9:** Deploy website, create release
- **Day 10+:** Launch publicly, monitor feedback

**Total:** ~10-14 days from start to launch

### Without Code Signing (Faster but Higher Abandonment)
- **Now:** Register domain, deploy website
- **Day 1:** Set up LemonSqueezy
- **Day 2:** Build unsigned installer, create release
- **Day 3+:** Launch publicly

**Total:** ~3 days, but expect 20-30% user abandonment due to SmartScreen warnings

---

## Support After Launch

### Monitoring
- Check `%APPDATA%\MurmurTone\murmurtone.log` for errors
- Monitor GitHub Issues
- Monitor support email (support@murmurtone.com)
- Track LemonSqueezy conversions

### Common Issues to Watch For
- SmartScreen abandonment (if not signed)
- Model download failures (network issues)
- GPU detection issues (missing CUDA drivers)
- License activation failures (network/firewall)
- Microphone permission issues (Windows privacy settings)

---

**Current Status:** Tracks 1, 3, 4 complete. Ready for Track 2 (integration testing) and Track 5 (launch preparation).

**Next Steps:**
1. Run integration tests (Track 2)
2. Order code signing certificate (10-14 day lead time)
3. Register domain and deploy website
4. Set up LemonSqueezy product
5. Build and test installer
6. Create GitHub release when ready to launch
