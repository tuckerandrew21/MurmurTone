# MurmurTone Logo Design Brief

## Logo Concepts

### Primary Concept: Waveform + Lock (Privacy First)

**Symbolism:**
- Sound waveform = Voice/Speech
- Lock/Shield = Privacy/Security
- Contained within = Local/Offline processing

**Visual Direction:**
- Sound waveform integrated within or surrounded by a shield/lock shape
- The waveform should be recognizable but stylized
- Shield should be subtle, not aggressive (approachable privacy)
- Clean, modern, minimalist aesthetic

**AI Generation Prompts:**

**Option 1 (Nano Banana / DALL-E / Midjourney):**
```
Modern tech logo design, sound waveform contained within shield shape,
purple-blue gradient from #667eea to #764ba2, clean minimalist style,
privacy and voice symbolism, flat design, vector art style, white background
```

**Option 2 (More Specific):**
```
Minimalist logo: audio waveform inside rounded shield icon,
gradient colors purple #764ba2 to indigo #667eea,
modern tech aesthetic, privacy-focused, clean lines, vector graphic
```

**Option 3 (Alternative Composition):**
```
Abstract logo combining microphone and padlock elements,
purple-blue gradient (#667eea, #764ba2), modern minimalist,
represents secure voice technology, flat icon design
```

### Alternative Concept: Microphone Whisper

**Symbolism:**
- Microphone = Voice input
- Soft waves = Murmur (quiet, private)
- Emanating circles = Sound propagation (contained, not cloud-based)

**Visual Direction:**
- Minimalist microphone icon at center
- Soft, subtle sound waves emanating outward
- Friendly, approachable, less "security-focused" than primary
- Use for softer contexts (tutorials, support, community)

**AI Generation Prompts:**

**Option 1:**
```
Minimalist microphone icon with soft sound waves emanating,
purple-blue gradient, friendly approachable style,
simple clean design, vector art, white background
```

**Option 2:**
```
Simple microphone logo with concentric circles representing sound,
gradient from #667eea to #764ba2, modern friendly aesthetic,
flat design, vector graphic
```

## Logo Specifications

### Required Variants

Once you have a selected design, create these variants:

#### 1. Full Logo (Horizontal Layout)
- Icon + "MurmurTone" wordmark
- Wordmark to the right of icon
- Spacing: Icon width × 0.5 between icon and text
- Font: System font stack (use Segoe UI Bold on Windows)
- Size: Icon 64px height, wordmark aligned to icon vertical center

#### 2. Icon Only
- Square format
- For: App icon, favicons, system tray
- Sizes needed: 16×16, 32×32, 64×64, 128×128, 256×256, 512×512, 1024×1024
- Format: PNG with transparency

#### 3. Wordmark Only
- "MurmurTone" text only
- Use same font as full logo
- For: Footer, headers where icon is redundant
- Height: 40px standard

#### 4. Reversed/White Version
- For dark backgrounds
- Change icon and text to white (#ffffff)
- Or use lighter gradient: #8b9cf6 to #9566c0

#### 5. Monochrome Version
- Single color: #667eea (brand primary)
- For print, limited color contexts
- Can also create pure black (#000000) version

### Clear Space

Minimum clear space around logo:
- Distance = Height of "M" in "MurmurTone"
- Apply on all four sides
- Prevents logo from being crowded by other elements

### Minimum Sizes

- Digital: 32px height (full logo), 16px (icon only)
- Print: 0.5 inches height (full logo), 0.25 inches (icon only)

### File Formats Needed

#### For Digital Use:
- **PNG**: All sizes with transparency, 72 DPI
- **SVG**: Scalable vector format
- **ICO**: Windows icon format (multi-resolution: 16, 32, 64, 256)

#### For Print Use:
- **PDF**: Vector format
- **PNG**: 300 DPI high resolution

### Color Specifications

**Primary Gradient:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Individual Colors:**
- Indigo: #667eea (102, 126, 234 RGB)
- Purple: #764ba2 (118, 75, 162 RGB)

**For SVG:**
```xml
<linearGradient id="brand-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
</linearGradient>
```

## Design Guidelines

### What Makes a Good MurmurTone Logo:

✅ **DO:**
- Clean, simple shapes (recognizable at small sizes)
- Modern, tech-forward aesthetic
- Conveys privacy/security without being aggressive
- Scales well from 16px to billboard size
- Works in both color and monochrome
- Distinct from competitors (not generic)
- Memorable shape/silhouette

❌ **AVOID:**
- Overly complex details (won't scale down)
- Clip art or generic stock icons
- Aggressive security imagery (barbed wire, heavy locks)
- Cloud imagery (contradicts offline message)
- Script/decorative fonts (hard to read small)
- More than 3 colors
- Trends that will date quickly (3D, bevels, shadows)

### Typography for Wordmark

**Primary Font Option: System Default**
- Windows: Segoe UI Bold
- Mac: San Francisco Bold
- Web: system-ui, -apple-system, 'Segoe UI', Roboto

**Alternative Font Option: Custom**
If you want more distinctive typography:
- **Inter Bold** (Google Fonts) - modern, clean, geometric
- **Manrope Bold** (Google Fonts) - approachable, slightly rounded
- **Outfit Bold** (Google Fonts) - tech-forward, distinctive

**Wordmark Specifications:**
- Always "MurmurTone" (capital M, capital T, no spaces)
- Letter spacing: -0.03em (slightly tighter than default)
- Never italicize
- Never outline or add effects

## Implementation Steps

### Step 1: Generate Concepts
1. Use AI tool (Nano Banana, DALL-E, Midjourney) with prompts above
2. Generate 5-10 variations of primary concept
3. Generate 3-5 variations of alternative concept
4. Export at high resolution (at least 1024×1024px)

### Step 2: Select Best Design
Evaluate options based on:
- Clarity at small sizes (test at 32px)
- Memorability (unique shape)
- Brand alignment (privacy, simplicity, speed)
- Technical feasibility (can it be vectorized cleanly?)

### Step 3: Refine in Vector Editor
1. Import selected design into Illustrator/Figma/Inkscape
2. Trace/recreate as vector paths (no raster)
3. Apply exact gradient colors (#667eea to #764ba2)
4. Clean up paths (remove unnecessary points)
5. Ensure icon is centered and balanced

### Step 4: Create Wordmark
1. Type "MurmurTone" in selected font
2. Apply letter spacing: -0.03em
3. Apply gradient or solid #667eea color
4. Align vertically with icon center

### Step 5: Export All Variants
Use export settings from "File Formats Needed" section above

### Step 6: Test Logo
- View at multiple sizes (16px to 1024px)
- Test on light and dark backgrounds
- View in grayscale (colorblind test)
- Print at small size (business card size)
- Test in Windows system tray (16×16 with transparency)

## File Naming Convention

```
murmurtone-logo-full.svg
murmurtone-logo-full.png
murmurtone-logo-icon.svg
murmurtone-logo-icon.png
murmurtone-logo-icon-16.png
murmurtone-logo-icon-32.png
murmurtone-logo-icon-64.png
murmurtone-logo-icon-128.png
murmurtone-logo-icon-256.png
murmurtone-logo-icon-512.png
murmurtone-logo-icon-1024.png
murmurtone-logo-wordmark.svg
murmurtone-logo-wordmark.png
murmurtone-logo-reversed.svg
murmurtone-logo-reversed.png
murmurtone-logo-monochrome.svg
murmurtone-logo-monochrome.png
icon.png (replace existing, 1024×1024)
icon.ico (multi-resolution Windows icon)
```

## Example Logo Compositions

### Full Logo Layout (Horizontal)
```
┌──────────────────────────────┐
│  [Icon]  MurmurTone          │
│   64px   ← 32px → 40px text  │
└──────────────────────────────┘
```

### App Icon (Square)
```
┌─────────┐
│         │
│  [Icon] │
│         │
└─────────┘
  64×64px
```

### System Tray Icon (Small)
```
┌───┐
│[I]│  ← Simplified version
└───┘    for 16×16px
```

## References & Inspiration

**Similar Aesthetic (for inspiration, not copying):**
- 1Password logo (friendly security)
- Figma logo (modern tech, simple)
- Linear logo (clean, minimalist)
- Raycast logo (approachable tech tool)

**Privacy/Security Done Right:**
- Signal logo (lock + speech bubble)
- ProtonMail logo (lock integrated subtly)
- Standard Notes logo (shield + document)

## Budget & Timeline

**If outsourcing logo design:**
- Fiverr: $50-200 for custom logo
- 99designs: $299+ for logo contest
- Professional designer: $500-2000

**DIY with AI tools:**
- Nano Banana: Free/subscription
- DALL-E: ~$0.02-0.20 per image
- Midjourney: $10/month subscription
- Time: 2-4 hours including refinement

## Next Steps After Logo Creation

1. Replace `icon.png` with new 1024×1024 logo icon
2. Create `icon.ico` multi-resolution Windows icon
3. Update `landing-page.html` header with new logo
4. Update `install.html` with new logo
5. Add logo files to `assets/logo/` folder
6. Update BRAND_GUIDE.md with final logo specifications
7. Add logo to press kit
8. Update social media profiles with new logo

## Questions?

If uncertain about any design direction:
- Prioritize "privacy + voice" symbolism
- Keep it simple (works at 16px)
- When in doubt, simpler is better
- Test with real users if possible

---

**Remember:** The logo should communicate "private voice typing" at a glance while being modern, approachable, and trustworthy.
