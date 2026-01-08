# MurmurTone v1.0 Launch Checklist

## Code Changes (Complete)

- [x] Rename `voice_typer.py` → `murmurtone.py`
- [x] Rename `voice_typer.spec` → `murmurtone.spec`
- [x] Update all user-facing strings (tray icon, window titles)
- [x] Change AppData path to `%APPDATA%\MurmurTone\`
- [x] Update build scripts for MurmurTone.exe output
- [x] Create README with new branding
- [x] Create brand positioning document
- [x] Create landing page template

## Manual Tasks (TODO)

- [ ] **Register murmurtone.com domain**
- [ ] **Push commits to GitHub** (2 commits pending)
  ```bash
  git push origin master
  ```
- [ ] **Rename GitHub repo** → `murmurtone`
  - Go to Settings → General → Repository name
  - GitHub auto-redirects old URLs
- [ ] **Deploy landing page to Vercel**
  - Upload `landing-page.html`
  - Connect murmurtone.com domain
- [ ] **Run build**
  ```bash
  build.bat
  ```
- [ ] **Test the built executable** (`dist\MurmurTone\MurmurTone.exe`)
- [ ] **Create GitHub Release**
  - Tag as `v1.0.0`
  - Upload MurmurTone.exe
  - Write release notes

## Domain Status

- **murmurtone.com**: Available (verified via WHOIS)
- **Trademark**: No conflicts found in USPTO search

## Files Ready for Launch

| File | Purpose |
|------|---------|
| `landing-page.html` | Landing page for murmurtone.com |
| `BRAND_POSITIONING.md` | Brand strategy and messaging |
| `murmurtone.spec` | PyInstaller config for MurmurTone.exe |
| `build.bat` | Build script to create executable |

## Commits Pending Push

```
6a753de Complete MurmurTone rebrand
eef72a7 Rebrand to MurmurTone
```
