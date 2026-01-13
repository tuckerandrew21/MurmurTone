# Code Signing Guide for MurmurTone

Code signing is **essential** to prevent Windows SmartScreen warnings that can prevent 20-30% of users from installing your app.

---

## Why Code Signing?

When users download and run **unsigned** Windows applications:

1. **Windows SmartScreen** shows scary warnings: "Windows protected your PC"
2. Users must click "More info" → "Run anyway" (many don't)
3. **Windows 11 Smart App Control** may block the app entirely
4. Research shows **20-30% abandonment** due to these warnings

**Code signing eliminates these issues** and signals trust to Windows.

---

## Certificate Types

### Option 1: EV (Extended Validation) Certificate - **RECOMMENDED**
- **Cost:** $249-400/year
- **Validation:** Company verification required (2-5 days)
- **Hardware Token:** Requires USB security key (ships with cert)
- **Instant Reputation:** Bypasses SmartScreen immediately
- **Best for:** Professional launch (our choice)

**Providers:**
- DigiCert (most reputable): $400/year
- Sectigo: $249/year
- SSL.com: $299/year

### Option 2: OV (Organization Validation) Certificate
- **Cost:** $100-200/year
- **Validation:** Basic company verification
- **Reputation Building:** Takes weeks to bypass SmartScreen
- **Best for:** Budget-conscious startups

---

## Purchase Process (EV Certificate - Recommended)

### 1. Choose Provider
We recommend **Sectigo** ($249/year) for best value:
https://sectigo.com/ssl-certificates-tls/code-signing

### 2. Prepare Documentation
You'll need:
- Business name and registration documents
- Physical business address
- DUNS number (get free from Dun & Bradstreet)
- Phone number matching public records
- Valid government-issued ID

### 3. Order Certificate
- Select "EV Code Signing Certificate"
- Complete business validation (2-5 business days)
- Receive USB token by mail (2-3 days shipping)

### 4. Install Certificate
Certificate comes on a **USB hardware token** (like YubiKey).
- Plug in USB token when signing
- Install driver from provider
- Test with: `certutil -scinfo`

**Total timeline:** ~10-14 days from order to first signed build

---

## Signing the Installer

### Prerequisites
1. **EV Certificate USB token** plugged in
2. **Windows SDK** installed (for `signtool.exe`)
   - Download: https://developer.microsoft.com/windows/downloads/windows-sdk/
   - Or install via Visual Studio

### Option A: Automatic Signing (via Inno Setup)

Set environment variables before building:

```batch
set SIGN_TOOL_PATH=C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe
set SIGN_CERT_PATH=C:\path\to\your\certificate.pfx
set SIGN_CERT_PASS=your-certificate-password

REM Build installer (will auto-sign)
iscc installer.iss
```

### Option B: Manual Signing

```batch
REM Sign the installer after building
"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign ^
  /f "C:\path\to\certificate.pfx" ^
  /p "certificate-password" ^
  /t http://timestamp.digicert.com ^
  /fd sha256 ^
  "installer_output\MurmurTone-1.0.0-Setup.exe"
```

### For EV USB Token (No PFX file)

```batch
REM Sign with USB token (no password needed if plugged in)
signtool.exe sign ^
  /n "Your Company Name" ^
  /t http://timestamp.digicert.com ^
  /fd sha256 ^
  "installer_output\MurmurTone-1.0.0-Setup.exe"
```

---

## Verification

After signing, verify the signature:

```batch
REM Check signature
signtool.exe verify /pa "installer_output\MurmurTone-1.0.0-Setup.exe"
```

**Expected output:**
```
Successfully verified: installer_output\MurmurTone-1.0.0-Setup.exe
```

You can also:
1. Right-click the installer → Properties → Digital Signatures tab
2. Should show your company name and certificate details

---

## Cost-Benefit Analysis

### Without Code Signing
- **Cost:** $0
- **SmartScreen warnings:** 100% of new downloads
- **Estimated abandonment:** 20-30%
- **If 1,000 downloads:** ~250 lost conversions

### With EV Code Signing
- **Cost:** $249/year
- **SmartScreen warnings:** 0%
- **Estimated abandonment:** 0-2% (normal install friction)
- **ROI:** Certificate pays for itself after ~10 prevented lost sales

**At $49/year price point:**
- **Break-even:** 6 additional sales from prevented abandonment
- **Expected ROI:** If SmartScreen prevents 10% abandonment → saves ~100 sales/year
- **Revenue impact:** ~$4,900/year vs $249 cost = **19.6x ROI**

---

## Timeline for Launch

### Without Certificate (Launch Now)
- ✅ Can launch immediately
- ⚠️ Users see SmartScreen warnings
- ⚠️ 20-30% abandonment rate
- ⚠️ Unprofessional appearance

### With Certificate (Launch in 2 Weeks)
- ⏰ 2-5 days: Certificate validation
- ⏰ 2-3 days: USB token shipping
- ⏰ 1 day: Setup and test signing
- ✅ Professional, trusted installation
- ✅ 0% SmartScreen warnings
- ✅ Higher conversion rates

**Recommendation:** Order certificate **now** and launch in 2 weeks with signing. The conversion rate improvement will more than compensate for the short delay.

---

## Testing Signed Installer

### Before Public Release
1. **Test on clean Windows 11 VM**
   - Should install without SmartScreen warnings
   - No "Unknown publisher" message

2. **Test Windows Defender SmartScreen**
   - Download from external source (email, cloud)
   - Run installer
   - Should show your company name, not "Unknown"

3. **Verify certificate chain**
   - Right-click installer → Properties → Digital Signatures
   - Certificate should chain to trusted root

---

## Ongoing Maintenance

### Certificate Renewal
- **EV Certificates:** Renew annually ($249/year)
- **Set reminder:** 30 days before expiration
- **Re-validation:** Usually faster than initial validation (1-2 days)

### Key Storage
- **USB Token:** Store securely when not signing
- **Backup:** EV tokens cannot be backed up (hardware-bound)
- **Multiple tokens:** Some providers offer backup tokens (+$50)

### CI/CD Integration
For automated builds:
- **Azure SignTool:** Cloud-based signing (no USB token needed)
- **AWS CloudHSM:** Enterprise HSM integration
- **Simple approach:** Manual signing on secure workstation (our approach for now)

---

## FAQ

**Q: Can I start without code signing?**
A: Yes, but expect significant SmartScreen abandonment. Many users will not proceed past the warning.

**Q: What about self-signed certificates?**
A: Self-signed certs trigger the SAME warnings as unsigned apps. They provide no benefit.

**Q: Can I use a cheaper OV certificate?**
A: OV certificates ($100-200/year) require "reputation building" - weeks of downloads before SmartScreen trusts them. EV certificates work immediately.

**Q: What if I'm a solo developer without a company?**
A: You can get an **Individual Developer Certificate** from Certum ($90/year) but it still shows SmartScreen warnings initially. EV is still recommended.

**Q: How long does the USB token last?**
A: Typically 3-5 years hardware-wise, but certificate must be renewed annually.

**Q: Can I sign on Mac/Linux?**
A: Code signing for Windows apps requires Windows. Use a Windows VM or dedicated signing workstation.

---

## Resources

- **Inno Setup Signing Docs:** https://jrsoftware.org/ishelp/index.php?topic=setup_signtool
- **Microsoft SignTool Docs:** https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool
- **Certificate Providers:**
  - Sectigo: https://sectigo.com/ssl-certificates-tls/code-signing
  - DigiCert: https://www.digicert.com/signing/code-signing-certificates
  - SSL.com: https://www.ssl.com/certificates/code-signing/

---

## Next Steps

1. **Order EV Certificate** from Sectigo ($249/year)
2. **Complete validation** (prepare docs in advance)
3. **Receive USB token** (2-3 days shipping)
4. **Test signing** with dev builds
5. **Sign final installer** before public launch

**Estimated total time:** 10-14 days
**Estimated cost:** $249/year (+ $0 setup)
**Expected ROI:** 20x+ from prevented SmartScreen abandonment
