---
name: qrcode-generator
description: Generate customizable QR codes (URLs, text, vCards, WiFi credentials, etc.) with colors, gradients, custom shapes and brand colors extracted from a website, via the free qrcode-monkey.com API, or locally for sensitive content. Output as PNG, SVG, JPG, PDF or EPS. Use whenever someone wants to create or style a QR code. Triggers include "create a QR code", "make a QR code", "generate QR", "QR code for", "WiFi QR code", "QR-Code erstellen", "mach mir einen QR-Code", "QR-Code für", "WLAN-QR-Code", "QR-Code in unseren Farben".
---

# QR Code Generator

Styled QR codes come from the qrcode-monkey.com API through `scripts/generate_qrcode.py`. Sensitive content is generated locally with `segno`, because the API receives the encoded data as a URL parameter.

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: the API returns an image without data modules or an error for a style listed here, a style name the user asks for is missing from the list, a code that does not scan, extracted brand colors that are unusable.

## 1. Decide: API or local

| Content | Where |
|---|---|
| URLs, public text, event links | API (styled) |
| WiFi passwords, vCards, phone numbers, e-mail addresses of real people, anything confidential | **local** (section 3), unless the user explicitly accepts sending it to qrcode-monkey |
| API unreachable or rate-limited | local |

Custom body and eye shapes exist only in the API; locally you get colors, size and format.

## 2. Styled code via the API

```bash
python3 scripts/generate_qrcode.py "https://example.com" qrcode.png \
  --body-color "#0277bd" --bg-color "#FFFFFF"
```

| Option | Default | Values |
|---|---|---|
| `--size` | 500 | pixels, max 3480; the API adds a quiet zone (500 → 580 px image) |
| `--body-color`, `--bg-color` | `#000000`, `#FFFFFF` | hex |
| `--body` | `square` | 21 styles, e.g. `round`, `dot`, `rounded-in`, `diamond`; full list in `references/api-params.md` |
| `--eye` / `--eye-ball` | `frame0` / `ball0` | `frame0`–`frame16` / `ball0`–`ball19` |
| `--gradient-color1/2`, `--gradient-type`, `--gradient-on-eyes` | off, `linear` | gradient instead of body color |
| `--file-type` | `png` | `png`, `svg`, `jpg`, `pdf`, `eps` (no gradients in PDF/EPS) |

The script rejects unknown style names, because the API silently returns an unscannable image (eyes only) for them.

Styled example:
```bash
python3 scripts/generate_qrcode.py "https://example.com/event" qrcode.png \
  --body round --eye frame2 --eye-ball ball3 \
  --gradient-color1 "#667eea" --gradient-color2 "#764ba2" --size 800
```

**Brand colors.** `python3 scripts/extract_colors.py "https://example.com" --json` returns `primary`, `secondary`, `accent` and `all_colors` from the site's CSS. "Primary" is just the most frequent color and may be light (e.g. `#eeeeee`); use the darkest suitable brand color as body color on a white or very light background.

**Defaults when the user specifies nothing:** black on white, `square`, 500 px, PNG. For print, SVG or PDF.

**Contrast:** foreground clearly darker than background (roughly: background brightness > 200, foreground < 100 on a 0–255 scale). Never invert (light code on dark background) unless the user insists and tests it.

## 3. Sensitive content: local with segno

```bash
pip install segno          # pure Python, no other dependencies; add --break-system-packages on managed Pythons
```

```python
import segno
from segno import helpers

# WiFi: escapes ; , : \ " in SSID and password correctly
helpers.make_wifi(ssid="MyNetwork", password="YOUR_WIFI_PASSWORD", security="WPA") \
    .save("wifi.png", scale=10, border=4, dark="#0277bd", light="white")

# vCard
helpers.make_vcard(name="Doe;Jane", displayname="Jane Doe",
                   phone="+49123456789", email="jane@example.com").save("contact.svg", scale=10)

# any text
segno.make("Some text", error="m").save("text.pdf", scale=10)
```

`save()` picks the format from the extension (`png`, `svg`, `pdf`, `eps`). If you build a WiFi string by hand (`WIFI:T:WPA;S:<ssid>;P:<password>;;`), escape `; , : \ "` with a backslash, or the code connects to nothing.

## 4. Deliver

1. Save the file where the user can open it (in Claude apps: `/mnt/user-data/outputs/`, then present it).
2. Say what is encoded (for WiFi/vCards without repeating the password in clear text) and which styling was applied.
3. Ask the user to test it with a phone camera before printing.

Further API details (eye colors per corner, flip options, presets): `references/api-params.md`. Don't send large batches to the API in one go; it blocks IPs that request too much.
