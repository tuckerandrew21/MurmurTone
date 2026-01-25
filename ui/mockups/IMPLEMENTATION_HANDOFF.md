# Settings UI Implementation Handoff

## Overview

Mockups are complete for all settings pages. Implement these designs in `ui/index.html` and `ui/app.js`.

## Mockup Files

### Main Pages
| File | Description |
|------|-------------|
| `general.html` | Recording + Output sections |
| `audio.html` | Input Device, Noise Gate, Audio Feedback |
| `recognition.html` | Speech Recognition, Processing Mode, Translation |
| `text.html` | Voice Commands, Filler Word Removal, Word Customization |
| `advanced.html` | AI Text Cleanup (installed state), Maintenance |
| `about.html` | App Info, License (active state), Links |

### State Variants
| File | Description |
|------|-------------|
| `about-trial.html` | Trial license - shows license key input + purchase button |
| `advanced-download.html` | AI model not installed - shows Download button |
| `advanced-downloading.html` | Download in progress - progress bar + cancel |
| `recognition-installed.html` | Whisper model installed - status badge + trash icon |

### Modals
| File | Description |
|------|-------------|
| `modal-edit-list.html` | Edit vocabulary/filler words/shortcuts |
| `modal-confirm.html` | Destructive action confirmation (Reset Settings) |

## Design Pattern

Every setting follows this structure:
```html
<div class="setting-row toggle-row">
    <div class="setting-info">
        <label class="setting-label">Setting Name</label>
        <p class="setting-help">Description text.</p>
    </div>
    <!-- Control on right: toggle, dropdown, button, etc. -->
</div>
```

Child settings use `.child-settings` wrapper for indentation.

## Key CSS Classes

| Class | Purpose |
|-------|---------|
| `.setting-row.toggle-row` | Standard setting row with flexbox |
| `.setting-info` | Wrapper for label + description |
| `.child-settings` | Indented sub-settings |
| `.input-with-button` | Dropdown/input + button combo |
| `.status-badge.success` | Green status indicator |
| `.status-badge.warning` | Yellow status indicator |
| `.btn-icon` | Icon-only button (compact padding) |
| `.setting-row.disabled` | Grayed out, non-interactive |

## State Logic to Implement

### AI Model (Advanced page)
- **Not installed**: Show Download button, disable Cleanup Mode and Formality dropdowns
- **Downloading**: Show progress bar + cancel button, keep dropdowns disabled
- **Installed**: Show "Installed (X GB)" badge + trash icon, enable dropdowns

### Whisper Model (Recognition page)
- **Not installed**: Show Download button next to dropdown
- **Installed**: Show "Installed (X MB)" badge + trash icon

### License (About page)
- **Active**: Show green "Active" badge, hide license key input and purchase button
- **Trial**: Show yellow "Trial (X days remaining)" badge, show license key input + Activate button + Buy Now button
- **Expired**: Show red "Expired" badge, show license key input + Activate button + Buy Now button

### GPU Status (Recognition page)
- **Available**: Green "CUDA Available" badge
- **Unavailable**: Gray "CPU Only" badge
- Refresh button to re-check

## Modals

### Edit List Modal
Used for: Custom Vocabulary, Custom Filler Words, Word Replacements, Text Shortcuts

Structure:
- Header with title + close button
- Body with description, add input + button, scrollable list
- Footer with Cancel + Save buttons (right-aligned)

### Confirm Modal
Used for: Reset Settings, Remove Model

Structure:
- Header with title + close button
- Body with centered warning icon + message text
- Footer with Cancel + destructive action button (right-aligned)

## Files to Modify

1. **`ui/index.html`** - Update HTML structure for each page
2. **`ui/app.js`** - Add state management and event handlers
3. **`ui/styles.css`** - Already updated with new styles (modal-icon, about-text, etc.)

## Implementation Order (Suggested)

1. General page (simplest, good baseline)
2. Audio page (introduces threshold meter interaction)
3. Recognition page (model download states, GPU status)
4. Text page (edit modals for word lists)
5. Advanced page (AI model states, confirm modal for reset)
6. About page (license states)

## Testing

After each page implementation, test visually:

### Launch App
```bash
cd c:/Users/tucke/Repositories/MurmurTone && py -3.12 settings_webview.py
```

### Visual Verification Checklist
For each page, compare against the corresponding mockup file:

1. **Layout**: Label on left, description below, control right-aligned
2. **Spacing**: Consistent gaps between sections and rows
3. **Colors**: Status badges (green/yellow/red), button styles
4. **States**: Toggle child settings enable/disable correctly
5. **Modals**: Open, close, backdrop dimming works

### Functional Tests
- [ ] Navigation between pages works
- [ ] Toggles enable/disable child settings
- [ ] Dropdowns populate and save values
- [ ] Edit buttons open modals
- [ ] Modal close (X button, Cancel, clicking backdrop)
- [ ] Confirm modal shows for destructive actions
- [ ] Status badges reflect actual state (GPU, model installed, license)

### Kill App Between Tests
```bash
taskkill //f //im python.exe
```

## Notes

- Styles are in `ui/styles.css` - most classes already exist
- Modal overlay uses `.visible` class to show/hide
- Progress bar uses `.progress-fill` width for percentage
- All buttons with badges use `<span class="badge">N</span>` inside button
- Python 3.12 required (see `.claude/rules/python-version.md`)
