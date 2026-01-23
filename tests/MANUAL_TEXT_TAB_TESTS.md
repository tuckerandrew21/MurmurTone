# Manual Text Tab Testing Checklist

This checklist covers live speech recognition testing that cannot be automated. Total estimated time: **35 minutes**.

## Prerequisites

Before starting, ensure:

- [ ] **Backup config**: `copy %APPDATA%\MurmurTone\config.yaml %APPDATA%\MurmurTone\config_backup.yaml`
- [ ] **Microphone connected** and working (test in Windows Sound settings)
- [ ] **MurmurTone main app running** (`py -3.12 main.py`) - NOT settings GUI
- [ ] **Quiet environment** - minimize background noise
- [ ] **Settings GUI open** to Text tab (`py -3.12 settings_webview.py` → Text tab)
- [ ] **Reset all Text settings to defaults** (disable all features, clear all lists)

---

## Test 1: Voice Commands (5 minutes)

### 1.1 Enable Voice Commands

- [ ] Enable "Voice Commands" toggle in settings
- [ ] Start recording with hotkey (default: Ctrl+Shift+Space)
- [ ] Speak: "This is a test period new line Another line comma end"
- [ ] **Expected output**:
  ```
  This is a test.
  Another line, end
  ```
- [ ] Verify "period" became `.` and "new line" created line break
- [ ] Verify "comma" became `,`

### 1.2 Disable Voice Commands

- [ ] Disable "Voice Commands" toggle in settings
- [ ] Start recording with hotkey
- [ ] Speak: "new line period comma"
- [ ] **Expected output**: `new line period comma` (literal text, no conversion)
- [ ] Verify commands are NOT executed when disabled

---

## Test 2: Scratch That (3 minutes)

### 2.1 Scratch That Enabled

- [ ] Enable "Voice Commands" toggle
- [ ] Enable "Scratch That" toggle
- [ ] Start recording, speak: "This is the first sentence"
- [ ] Verify text appears in your editor/output
- [ ] Start recording again, say: "scratch that"
- [ ] **Expected**: Last transcription ("This is the first sentence") is deleted/removed
- [ ] Start recording, speak: "This is the second sentence"
- [ ] Verify second sentence appears

### 2.2 Scratch That Disabled

- [ ] Disable "Scratch That" toggle (keep "Voice Commands" enabled)
- [ ] Start recording, speak: "This is a test"
- [ ] Start recording again, say: "scratch that"
- [ ] **Expected**: "scratch that" is typed literally (NOT treated as command)
- [ ] Verify undo does NOT happen

---

## Test 3: Filler Removal - Basic Mode (5 minutes)

### 3.1 Basic Filler Removal

- [ ] Enable "Filler Removal" toggle
- [ ] **Disable** "Aggressive Mode" toggle
- [ ] Start recording
- [ ] Speak: "um well I think uh this is basically good you know"
- [ ] **Expected output**: `well I think this is basically good you know`
- [ ] Verify "um" removed
- [ ] Verify "uh" removed
- [ ] Verify "basically" preserved (not removed in basic mode)
- [ ] Verify "you know" preserved (not removed in basic mode)

### 3.2 Filler Removal Disabled

- [ ] Disable "Filler Removal" toggle
- [ ] Start recording
- [ ] Speak: "um this is uh a test"
- [ ] **Expected output**: `um this is uh a test` (fillers preserved)
- [ ] Verify no filler words removed when disabled

---

## Test 4: Filler Removal - Aggressive Mode (3 minutes)

### 4.1 Aggressive Filler Removal

- [ ] Enable "Filler Removal" toggle
- [ ] **Enable** "Aggressive Mode" toggle
- [ ] Start recording
- [ ] Speak: "um well I think uh this is basically good you know"
- [ ] **Expected output**: `well I think this is good`
- [ ] Verify "um" removed
- [ ] Verify "uh" removed
- [ ] Verify "basically" removed (aggressive mode)
- [ ] Verify "you know" removed (aggressive mode)

---

## Test 5: Custom Filler Words (5 minutes)

### 5.1 Add Custom Filler Word

- [ ] Ensure "Filler Removal" is enabled
- [ ] In settings, add "actually" to custom filler list
- [ ] Start recording
- [ ] Speak: "actually this is actually working actually fine"
- [ ] **Expected output**: `this is working fine`
- [ ] Verify all instances of "actually" removed

### 5.2 Remove Custom Filler Word

- [ ] Remove "actually" from custom filler list
- [ ] Start recording
- [ ] Speak: "actually this is actually a test"
- [ ] **Expected output**: `actually this is actually a test` (preserved)
- [ ] Verify "actually" is NOT removed after being removed from list

### 5.3 Multiple Custom Fillers

- [ ] Add "honestly" and "literally" to custom filler list
- [ ] Start recording
- [ ] Speak: "honestly I literally think this is good"
- [ ] **Expected output**: `I think this is good`
- [ ] Verify both custom fillers removed

---

## Test 6: Custom Dictionary (5 minutes)

**NOTE**: If Dictionary editor modal is not implemented in WebView, skip this test and document as known gap.

### 6.1 Simple Replacements

- [ ] Open Dictionary Editor (click "Edit Dictionary" button)
- [ ] Add replacement: `teh` → `the`
- [ ] Add replacement: `youre` → `you're`
- [ ] Save and close
- [ ] Start recording
- [ ] Speak or type: "teh cat and youre dog"
- [ ] **Expected output**: `the cat and you're dog`
- [ ] Verify replacements applied correctly

### 6.2 Case Sensitivity

- [ ] Open Dictionary Editor
- [ ] Add replacement: `API` → `api` (case-sensitive: TRUE)
- [ ] Save and close
- [ ] Start recording, speak: "API"
- [ ] **Expected output**: `api` (if spoken as "API")
- [ ] Verify case-sensitive replacement works

---

## Test 7: Text Shortcuts (5 minutes)

**NOTE**: If Shortcuts editor modal is not implemented in WebView, skip this test and document as known gap.

### 7.1 Single-Line Shortcuts

- [ ] Open Shortcuts Editor (click "Edit Shortcuts" button)
- [ ] Add shortcut: `addr` → `123 Main Street`
- [ ] Save and close
- [ ] Start recording
- [ ] Say or type: "Please send to addr"
- [ ] **Expected**: "addr" expands to "123 Main Street"
- [ ] Full output: `Please send to 123 Main Street`

### 7.2 Multi-Line Shortcuts

- [ ] Open Shortcuts Editor
- [ ] Add shortcut: `sig` → `Best regards,\nJohn Smith`
- [ ] Save and close
- [ ] Start recording
- [ ] Say or type: "sig"
- [ ] **Expected**: Multi-line signature inserted:
  ```
  Best regards,
  John Smith
  ```
- [ ] Verify newline preserved

### 7.3 Disabled Shortcuts

- [ ] Open Shortcuts Editor
- [ ] Disable the `addr` shortcut (enabled: FALSE)
- [ ] Save and close
- [ ] Start recording, say: "addr"
- [ ] **Expected**: `addr` typed literally (NOT expanded)
- [ ] Verify disabled shortcuts are not expanded

---

## Test 8: Edge Cases (5 minutes)

### 8.1 Large Custom Filler List

- [ ] Add 20+ words to custom filler list (e.g., word1, word2, ..., word20)
- [ ] Start recording
- [ ] Speak a sentence containing several of these words
- [ ] **Expected**: All custom filler words removed
- [ ] Verify performance not degraded with large list

### 8.2 Unicode and Special Characters

- [ ] Add custom filler: `café` (with accent)
- [ ] Start recording, speak: "café"
- [ ] **Expected**: "café" removed from output
- [ ] Verify unicode characters handled correctly

- [ ] Open Dictionary Editor (if available)
- [ ] Add replacement: `café` → `coffee shop`
- [ ] Start recording, speak: "café"
- [ ] **Expected**: `coffee shop`
- [ ] Verify unicode in dictionary works

### 8.3 Very Long Shortcut

- [ ] Open Shortcuts Editor (if available)
- [ ] Add shortcut with 200+ character replacement
- [ ] Start recording, trigger the shortcut
- [ ] **Expected**: Full 200+ char text inserted
- [ ] Verify long replacements work

---

## Test 9: Cleanup (2 minutes)

After completing all tests:

- [ ] Disable all test features (Voice Commands, Filler Removal, Scratch That)
- [ ] Remove all custom filler words from list
- [ ] Remove test dictionary entries (if editor available)
- [ ] Remove test shortcuts (if editor available)
- [ ] **Optionally restore backup**: `copy %APPDATA%\MurmurTone\config_backup.yaml %APPDATA%\MurmurTone\config.yaml`
- [ ] Restart MurmurTone main app to load clean config

---

## Results Summary

| Test Category | Pass/Fail | Notes |
|---------------|-----------|-------|
| Voice Commands Enable | ☐ Pass ☐ Fail | |
| Voice Commands Disable | ☐ Pass ☐ Fail | |
| Scratch That Enable | ☐ Pass ☐ Fail | |
| Scratch That Disable | ☐ Pass ☐ Fail | |
| Filler Removal Basic | ☐ Pass ☐ Fail | |
| Filler Removal Aggressive | ☐ Pass ☐ Fail | |
| Custom Filler Words | ☐ Pass ☐ Fail | |
| Dictionary Replacements | ☐ Pass ☐ Fail ☐ N/A (not implemented) | |
| Text Shortcuts Single-line | ☐ Pass ☐ Fail ☐ N/A (not implemented) | |
| Text Shortcuts Multi-line | ☐ Pass ☐ Fail ☐ N/A (not implemented) | |
| Edge Cases | ☐ Pass ☐ Fail | |

**Overall Result**: ☐ All tests passed ☐ Some tests failed ☐ Some features not implemented

**Known Gaps**:
- [ ] Dictionary editor modal not implemented in WebView
- [ ] Vocabulary editor not implemented in WebView
- [ ] Shortcuts editor modal not implemented in WebView

**Bugs Found**: (list any bugs discovered during testing)
1.
2.
3.

---

## Troubleshooting

**Problem**: Voice commands not executing
- **Solution**: Verify "Voice Commands" toggle is ON in settings
- **Solution**: Check that MurmurTone main app is running (not just settings GUI)
- **Solution**: Verify hotkey is working (try re-binding in settings)

**Problem**: Filler removal not working
- **Solution**: Verify "Filler Removal" toggle is ON
- **Solution**: Check that words are spelled correctly in custom filler list
- **Solution**: Ensure aggressive mode is enabled if testing aggressive fillers

**Problem**: Dictionary replacements not applying
- **Solution**: Verify replacements were saved in Dictionary editor
- **Solution**: Check case sensitivity settings
- **Solution**: Restart MurmurTone main app to reload config

**Problem**: Microphone not picking up audio
- **Solution**: Check Windows Sound settings → Input device
- **Solution**: Test microphone in other applications
- **Solution**: Verify correct input device selected in MurmurTone Audio settings

---

**Total Testing Time**: ~35 minutes
**Completion Date**: ___________
**Tester Name**: ___________
