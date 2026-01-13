# Dropdown Testing Guide

## Automated Verification
All 12 dropdown fields in settings_gui.py have been confirmed to have `state="readonly"` set.

## Manual Testing Checklist

To verify dropdowns are non-editable but still functional:

### General Section
1. **Recording Mode** dropdown (push_to_talk, toggle, auto_stop)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show options
   - Select option: Should work

2. **Language** dropdown (Auto-detect, English, Spanish, etc.)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show language list
   - Select language: Should work

3. **Paste Method** dropdown (clipboard, type)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show options
   - Select option: Should work

4. **Preview Position** dropdown (top_left, top_right, etc.)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show positions
   - Select position: Should work

5. **Preview Theme** dropdown (dark, light)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show themes
   - Select theme: Should work

### Audio Section
6. **Microphone** dropdown (device list)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show available devices
   - Select device: Should work

7. **Sample Rate** dropdown (8000, 16000, etc.)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show rates
   - Select rate: Should work

### Recognition Section
8. **Model Size** dropdown (tiny, base, small, etc.)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show models
   - Select model: Should work

9. **Compute Type** dropdown (int8, float16)
   - Try typing: Should NOT be possible
   - Click dropdown: Should show compute types
   - Select type: Should work

10. **Translation Source Language** dropdown
    - Try typing: Should NOT be possible
    - Click dropdown: Should show language list
    - Select language: Should work

### Advanced Section
11. **Cleanup Mode** dropdown (grammar, professional, casual, creative)
    - Try typing: Should NOT be possible
    - Click dropdown: Should show modes
    - Select mode: Should work

12. **Formality Level** dropdown (casual, neutral, formal)
    - Try typing: Should NOT be possible
    - Click dropdown: Should show levels
    - Select level: Should work

## Testing Command
```bash
# Launch settings GUI
python settings_gui.py

# Run automated verification
python test_dropdown_readonly.py
```

## Expected Behavior
- User CANNOT type arbitrary text into dropdowns
- User CAN click to see dropdown options
- User CAN select from predefined options
- Selection updates the bound StringVar correctly
- No errors or exceptions occur
