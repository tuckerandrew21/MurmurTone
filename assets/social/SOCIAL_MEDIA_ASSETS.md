# Social Media Assets Guide

This document specifies the social media assets needed for MurmurTone's online presence.

## Required Assets

### 1. Profile Picture (400x400px)

**File:** `profile-400x400.png`

**Specifications:**
- Size: 400x400 pixels
- Format: PNG with transparency
- Content: MurmurTone logo icon (shield with waveform)
- Background: White or brand gradient
- Safe area: Keep logo within center 80% (logo may be cropped to circle on some platforms)

**Usage:**
- Twitter/X profile
- LinkedIn profile
- GitHub organization
- Discord server
- Any social platform

---

### 2. Twitter/X Cover (1500x500px)

**File:** `twitter-cover-1500x500.png`

**Specifications:**
- Size: 1500x500 pixels
- Format: PNG or JPG
- Safe area: Keep important content in center 1200x400 (edges may be cropped on mobile)

**Design Elements:**
- Background: Brand gradient (#667eea to #764ba2, 135° angle)
- Logo: Left side or centered
- Tagline: "Your voice, locally."
- Key visual: Sound waveform pattern or privacy lock icon
- Optional: "100% Offline Voice-to-Text" subtitle

**Prompt for AI Generation:**
```
Create a Twitter header banner, 1500x500 pixels, purple-blue gradient background (#667eea to #764ba2 at 135 degrees).

Left side: MurmurTone logo (shield with waveform inside).
Center: Large text "Your voice, locally." in white, clean sans-serif font.
Right side: Subtle sound wave pattern extending across.

Bottom right corner: Small text "Private • Offline • Fast" in white at 50% opacity.

Style: Modern, clean, tech-forward. No people or photos. Minimal design.
```

---

### 3. LinkedIn Cover (1584x396px)

**File:** `linkedin-cover-1584x396.png`

**Specifications:**
- Size: 1584x396 pixels
- Format: PNG or JPG
- Safe area: Keep important content in center 1200x300

**Design Elements:**
- Similar to Twitter cover but more professional tone
- Include: Logo, tagline, and key value proposition
- Consider: "Private Voice-to-Text for Windows" descriptor

**Prompt for AI Generation:**
```
Create a LinkedIn cover banner, 1584x396 pixels, purple-blue gradient background (#667eea to #764ba2 at 135 degrees).

Left side: MurmurTone logo (shield with waveform inside).
Center: Text "MurmurTone" large, with "Private Voice-to-Text for Windows" below in smaller text.
Right side: Abstract waveform visualization.

Tagline at bottom: "Your voice, locally." in white.

Style: Professional, modern, B2B appropriate. Clean minimalist design.
```

---

### 4. Social Sharing Image / OG Image (1200x630px)

**File:** `og-image-1200x630.png`

**Specifications:**
- Size: 1200x630 pixels (Facebook/LinkedIn sharing standard)
- Format: PNG or JPG
- This appears when links are shared on social media

**Design Elements:**
- Logo prominently displayed
- Tagline: "Your voice, locally."
- Key benefits: "100% Offline • Private • Fast"
- Website URL: murmurtone.com
- Background: Brand gradient

**Prompt for AI Generation:**
```
Create a social media sharing image, 1200x630 pixels, purple-blue gradient background (#667eea to #764ba2 at 135 degrees).

Center: Large MurmurTone logo (shield with waveform inside).
Below logo: "MurmurTone" text in bold white.
Below name: "Your voice, locally." tagline in white.

Bottom section: Three icons with labels - Lock icon "Private", Computer icon "Offline", Lightning icon "Fast".

Bottom right corner: "murmurtone.com" in small white text.

Style: Bold, eye-catching, shareable. Modern tech aesthetic.
```

---

### 5. Favicon Set

**Files:** Already created at `/icon.ico`

Additional sizes if needed:
- `favicon-16x16.png`
- `favicon-32x32.png`
- `apple-touch-icon-180x180.png`

---

## Platform-Specific Guidelines

### Twitter/X
- Profile: 400x400px (displays as circle)
- Header: 1500x500px
- Bio: Max 160 characters
- Bio template: "MurmurTone - Private voice-to-text for Windows. 100% offline transcription. No cloud, no tracking. $49/year. Your voice, locally. 🎤"

### LinkedIn
- Profile: 400x400px (displays as circle)
- Cover: 1584x396px
- Bio: Professional tone, mention Windows-only, B2B potential

### GitHub
- Profile: 400x400px
- Repo social preview: 1280x640px (optional)

### Discord
- Server icon: 512x512px
- Server banner: 960x540px (Nitro feature)

---

## Color References

For consistency across all assets:

```
Primary Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Indigo: #667eea
Purple: #764ba2
White: #ffffff
Text on gradient: white with varying opacity (100%, 90%, 70%)
```

---

## Typography

Use system fonts or these web-safe alternatives:
- Headlines: Bold/SemiBold weight
- Body: Regular weight
- Tagline: SemiBold or Medium weight

---

## Usage Notes

1. **Consistency:** All assets should use the same gradient direction (135°) and color values
2. **Logo placement:** Prefer left-aligned or centered
3. **Whitespace:** Generous padding around text elements
4. **Contrast:** Ensure all text is readable on gradient background
5. **No stock photos:** Use abstract shapes, waveforms, icons only

---

## Generation Instructions

To generate these assets:

1. Use AI image generation tools (Gemini, DALL-E, Midjourney)
2. Use the prompts provided above
3. Request exact dimensions
4. If dimensions are off, resize/crop maintaining safe areas
5. Save as PNG for transparency support, JPG for photos
6. Optimize file sizes for web (< 500KB per image)

---

## Existing Assets

The following assets already exist:
- `/icon.png` - Logo icon (1024x1024)
- `/icon.svg` - Logo icon (vector)
- `/icon.ico` - Windows icon (multi-resolution)
- `/assets/logo/murmurtone-logo-icon.png` - Logo copy
- `/assets/logo/murmurtone-logo-icon.ico` - Icon copy
- `/assets/logo/murmurtone-logo-icon.svg` - Vector copy
