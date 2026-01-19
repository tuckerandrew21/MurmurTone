# MurmurTone Release Process

This document describes how to build and release new versions of MurmurTone.

## Prerequisites

- **Python 3.12 or 3.13** (not 3.14+)
- **PyInstaller** (`pip install pyinstaller`)
- **Inno Setup** (https://jrsoftware.org/isdl.php) - add to PATH
- **Cloudflare R2 access** for hosting the installer

## Build the Installer

1. Open a terminal in the repository root
2. Run the build script:
   ```batch
   build.bat
   ```

The script will:
- Verify Python version (3.12 or 3.13 required)
- Prepare the bundled `tiny.en` model if not present
- Build the EXE with PyInstaller
- Create the Windows installer with Inno Setup (if available)

### Output Files

- **Standalone build:** `dist\MurmurTone\`
- **Installer:** `installer_output\MurmurTone-{version}-Setup.exe`

## Upload to Cloudflare R2

The installer is hosted on Cloudflare R2 at `downloads.murmurtone.com`.

### Using Cloudflare Dashboard

1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **R2** > **murmurtone-downloads** bucket
3. Upload `installer_output/MurmurTone-{version}-Setup.exe`
4. Verify the file is accessible at `https://downloads.murmurtone.com/MurmurTone-{version}-Setup.exe`

### Using Wrangler CLI (Optional)

```bash
# Install wrangler if not present
npm install -g wrangler

# Authenticate
wrangler login

# Upload the installer
wrangler r2 object put murmurtone-downloads/MurmurTone-{version}-Setup.exe \
  --file=installer_output/MurmurTone-{version}-Setup.exe
```

## Version Updates

When releasing a new version, update the version number in these files:

| File | Location | Example |
|------|----------|---------|
| `pyproject.toml` | Line 3 | `version = "1.0.0"` |
| `installer.iss` | Line 16 | `#define MyAppVersion "1.0.0"` |
| `install.html` | Line 137 | Download URL and version display |

### Checklist for Version Bump

1. Update version in `pyproject.toml`:
   ```toml
   version = "X.Y.Z"
   ```

2. Update version in `installer.iss`:
   ```iss
   #define MyAppVersion "X.Y.Z"
   ```

3. Update download URL in `install.html`:
   ```html
   <a href="https://downloads.murmurtone.com/MurmurTone-X.Y.Z-Setup.exe" ...>
   ```

4. Update version display in `install.html`:
   ```html
   <p><strong>Version X.Y.Z</strong> ...
   ```

## Full Release Workflow

1. **Update version numbers** in all files listed above
2. **Run `build.bat`** to create the installer
3. **Test the installer** on a clean Windows machine
4. **Upload to R2** using dashboard or wrangler
5. **Verify download** works from `https://downloads.murmurtone.com/...`
6. **Commit changes** to the website
7. **Deploy website** to make new download link live

## Troubleshooting

### Build requires Python 3.12 or 3.13
The build script checks Python version. Use `py -3.12` launcher or install Python 3.12.

### Inno Setup not found
Install from https://jrsoftware.org/isdl.php and add to PATH, or run manually:
```batch
iscc installer.iss
```

### Model not found
The build script will automatically run `prepare_model.py` to download the tiny.en model.
