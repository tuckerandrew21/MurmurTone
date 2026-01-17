# Settings GUI Frontend Audit Report

**Date:** 2026-01-17
**Auditor:** Claude (automated + manual verification)

---

## Executive Summary

The MurmurTone settings GUI passes the audit with good results:

| Area | Status | Notes |
|------|--------|-------|
| Visual Consistency | Pending User Review | Color constants match mockup |
| Stability | PASS | 19/19 tests passing |
| Performance | PASS | 1.55s startup (target <2s) |
| Accessibility | Skipped | Per user request |

---

## 1. Visual Consistency Audit

### Color Constants Verification

All color constants in [theme.py](theme.py) match the mockup CSS exactly:

| Color | theme.py | Mockup CSS | Match |
|-------|----------|------------|-------|
| PRIMARY | #0d9488 | #0d9488 | Yes |
| PRIMARY_DARK | #0f766e | #0f766e | Yes |
| PRIMARY_LIGHT | #14b8a6 | #14b8a6 | Yes |
| SLATE_900 | #0f172a | #0f172a | Yes |
| SLATE_800 | #1e293b | #1e293b | Yes |
| SLATE_700 | #334155 | #334155 | Yes |
| SLATE_600 | #475569 | #475569 | Yes |
| SLATE_500 | #64748b | #64748b | Yes |
| SLATE_400 | #94a3b8 | #94a3b8 | Yes |
| SUCCESS | #10b981 | #10b981 | Yes |
| WARNING | #f59e0b | #f59e0b | Yes |
| ERROR | #ef4444 | #ef4444 | Yes |

### Mockup Screenshots Captured

Reference screenshots saved to `.playwright-mcp/`:
- mockup-general-page.png
- mockup-audio-page.png
- mockup-recognition-page.png
- mockup-text-page.png
- mockup-advanced-page.png
- mockup-about-page.png

**Action Required:** User should visually compare running app to these mockups and report deviations.

---

## 2. Stability Test Results

**Test File:** [tests/test_settings_gui_stability.py](tests/test_settings_gui_stability.py)

### Test Summary: 19/19 PASSED

```
tests/test_settings_gui_stability.py::TestConfigFileHandling::test_load_missing_config_file PASSED
tests/test_settings_gui_stability.py::TestConfigFileHandling::test_load_corrupted_config_file PASSED
tests/test_settings_gui_stability.py::TestConfigFileHandling::test_load_empty_config_file PASSED
tests/test_settings_gui_stability.py::TestConfigFileHandling::test_load_config_with_extra_keys PASSED
tests/test_settings_gui_stability.py::TestAudioDeviceHandling::test_no_audio_devices_available PASSED
tests/test_settings_gui_stability.py::TestAudioDeviceHandling::test_sounddevice_import_fails PASSED
tests/test_settings_gui_stability.py::TestInputValidation::test_silence_duration_clamping PASSED
tests/test_settings_gui_stability.py::TestInputValidation::test_noise_threshold_range PASSED
tests/test_settings_gui_stability.py::TestInputValidation::test_auto_hide_delay_accepts_zero PASSED
tests/test_settings_gui_stability.py::TestInputValidation::test_unicode_in_vocabulary PASSED
tests/test_settings_gui_stability.py::TestInputValidation::test_large_vocabulary_list PASSED
tests/test_settings_gui_stability.py::TestGPUDetection::test_cuda_status_without_gpu PASSED
tests/test_settings_gui_stability.py::TestGPUDetection::test_check_cuda_returns_bool PASSED
tests/test_settings_gui_stability.py::TestThemeConsistency::test_theme_imports_without_error PASSED
tests/test_settings_gui_stability.py::TestThemeConsistency::test_theme_color_format PASSED
tests/test_settings_gui_stability.py::TestThemeConsistency::test_style_helpers_return_dicts PASSED
tests/test_settings_gui_stability.py::TestResourceCleanup::test_autosave_manager_stops_on_destroy PASSED
tests/test_settings_gui_stability.py::TestResourceCleanup::test_audio_stream_cleanup PASSED
tests/test_settings_gui_stability.py::TestConcurrentOperations::test_rapid_config_saves PASSED
```

### Coverage Areas

- **Config File Handling:** Missing, corrupted, empty, and extra keys
- **Audio Device Handling:** No devices, missing sounddevice library
- **Input Validation:** Silence duration, noise threshold, auto-hide delay, unicode, large lists
- **GPU Detection:** Graceful handling when unavailable
- **Theme Consistency:** Valid hex colors, style helper functions

---

## 3. Performance Baseline

### Startup Time

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Module import | 234ms | - | - |
| Window build | 1318ms | - | - |
| **Total** | **1553ms** | <2000ms | PASS |

### Profile Breakdown (pyinstrument)

| Component | Time | % of Total |
|-----------|------|------------|
| About section | 484ms | 25% |
| - faster_whisper import | 266ms | 14% |
| mainloop/render | 410ms | 21% |
| CTk updates | 418ms | 21% |
| General section | 123ms | 6% |
| Audio section | 105ms | 5% |
| CTk init | 85ms | 4% |
| Recognition section | 70ms | 4% |
| Text section | 65ms | 3% |
| Advanced section | 61ms | 3% |
| Sidebar | 46ms | 2% |

### Performance Recommendations

1. **Lazy load faster_whisper** - The About section imports faster_whisper just for version info, adding 266ms. Consider lazy loading or caching the version string.

2. **Defer section creation** - Currently all 6 sections are built at startup. Could build only the visible section initially and lazy-load others on navigation.

---

## 4. Accessibility & DPI

Skipped per user request. Future audit should verify:

- [ ] Tab navigation reaches all controls
- [ ] Focus indicators visible
- [ ] Escape closes dialogs
- [ ] Text contrast meets WCAG AA (4.5:1)
- [ ] Controls scale correctly at 100%, 125%, 150%, 200% DPI

---

## 5. Files Modified/Created

| File | Action |
|------|--------|
| tests/test_settings_gui_stability.py | Created (19 tests) |
| AUDIT_REPORT.md | Created |
| .playwright-mcp/mockup-*.png | Created (6 screenshots) |

---

## 6. Running the Tests

```bash
# Run stability tests
py -3.12 -m pytest tests/test_settings_gui_stability.py -v

# Run all tests
py -3.12 -m pytest tests/ -v

# Profile startup time
py -3.12 -m pyinstrument settings_gui.py
```

---

## 7. Recommendations Summary

1. **Performance:** Consider lazy-loading faster_whisper import in About section
2. **Testing:** Add visual regression tests using screenshot comparison when CI is set up
3. **Accessibility:** Schedule follow-up audit for keyboard navigation and screen reader support
