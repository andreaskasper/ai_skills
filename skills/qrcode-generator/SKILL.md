---
name: qrcode-generator
description: Generate customizable QR codes (URLs, text, vCards, WiFi credentials, etc.) with colors, gradients, custom shapes and brand colors extracted from a website, via the free qrcode-monkey.com API with an offline fallback. Output as PNG, SVG, JPG, PDF or EPS. Use whenever someone wants to create or style a QR code. Triggers include "create a QR code", "make a QR code", "generate QR", "QR code for", "QR-Code erstellen", "mach mir einen QR-Code", "QR-Code für", "QR-Code in unseren Farben".
---

# QR Code Generator

Generate high-quality, customizable QR codes using the qrcode-monkey.com API.

## Core Workflow

### 1. Understand the Request

Determine:
- **Content to encode**: URL, text, vCard, WiFi credentials, etc.
- **Styling preferences**: Colors, shapes, gradients
- **Brand matching**: Extract colors from a website if requested
- **Output requirements**: Size and format

### 2. Generate the QR Code

Use `scripts/generate_qrcode.py` for reliable QR code generation:

```bash
python3 scripts/generate_qrcode.py "https://example.com" output.png \
  --size 500 \
  --body-color "#0277bd" \
  --bg-color "#FFFFFF"
```

**Key script parameters**:
- First argument: Data to encode
- Second argument: Output path
- `--size`: Pixels (default 300, max 3480)
- `--body-color`: Main QR code color (hex)
- `--bg-color`: Background color (hex)
- `--body`: Style (square, dot, circle, rounded, etc.)
- `--eye`: Eye frame style (frame0-frame16)
- `--eye-ball`: Eye ball style (ball0-ball19)
- `--gradient-color1/2`: For gradient effects
- `--file-type`: Output format (png, svg, jpg, pdf, eps)

### 3. Extract Brand Colors (Optional)

When users request QR codes matching a website's design, use `scripts/extract_colors.py`:

```bash
python3 scripts/extract_colors.py "https://example.com" --json
```

This returns:
- `primary`: Main brand color
- `secondary`: Contrasting color
- `accent`: Additional brand color (if found)

Apply these colors to the QR code for brand consistency.

## Common Use Cases

### Simple URL QR Code
```bash
python3 scripts/generate_qrcode.py "https://example.com/event/2026" qrcode.png
```

### Brand-Matched QR Code
1. Extract colors: `python3 scripts/extract_colors.py "https://example.com" --json`
2. Generate with colors: Use extracted primary as `--body-color`

### Contact Information (vCard)
Encode vCard format:
```
BEGIN:VCARD
VERSION:3.0
FN:Jane Doe
TEL:+49123456789
EMAIL:jane@example.com
END:VCARD
```

### WiFi Credentials
```bash
python3 scripts/generate_qrcode.py "WIFI:T:WPA;S:NetworkName;P:Password;;" wifi.png
```

### Styled QR Code
```bash
python3 scripts/generate_qrcode.py "Hello World" qrcode.png \
  --body rounded \
  --eye frame2 \
  --eye-ball ball3 \
  --gradient-color1 "#667eea" \
  --gradient-color2 "#764ba2" \
  --gradient-type linear \
  --size 800
```

## Decision Framework

**When user doesn't specify styling**:
- Use black on white (safe default)
- Size: 500px (good balance of quality and file size)
- Format: PNG (universal compatibility)

**When "brand matching" or "website design" mentioned**:
1. Extract colors from the specified website
2. Use primary color as body color
3. Use white or light color as background
4. Apply rounded or modern body style for professional look

**Color safety check**:
- Always ensure sufficient contrast (light background, dark foreground)
- Background brightness should be >200
- Foreground brightness should be <100
- Verify scannability requirements are met

**Format selection**:
- PNG: Default, best for most uses
- SVG: For scalable/print applications
- JPG: For smaller file sizes
- PDF/EPS: Professional printing (no gradient support)

## Advanced Customization

For complex styling needs, consult `references/api-params.md` for:
- Complete body style options (35+ styles)
- Eye frame and ball combinations
- Rotation and flip options
- Gradient configuration details

## Output

Always:
1. Save the QR code where the user can access it (in claude.ai: `/mnt/user-data/outputs/`, then present the file)
2. Show or link the file
3. Mention the encoded data and any styling applied
4. Suggest testing the QR code with a scanner

## Offline fallback

If the API is unreachable, rate-limited or the data is sensitive (e.g. WiFi passwords you'd rather not send to a third-party service), generate locally:

```bash
pip install "qrcode[pil]"          # add --break-system-packages on managed Pythons
python3 -c "import qrcode; qrcode.make('https://example.com').save('qrcode.png')"
```

Colors via `qrcode.QRCode(...).make_image(fill_color='#0277bd', back_color='white')`. Custom body/eye shapes are only available through the API.

## Important Notes

- **Privacy**: the API is a third-party service; the encoded data is sent to it. For credentials or personal data, prefer the offline fallback.

- **Rate limiting**: Don't generate too many QR codes at once (IP may be blocked)
- **Contrast**: Background must be lighter than foreground for scannability
- **Size limits**: Maximum 3480 pixels
- **Gradients**: Not supported in PDF/EPS formats
- **Testing**: Always recommend users test QR codes before production use
