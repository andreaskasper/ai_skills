# QR Code Monkey API Reference

Parameter reference for the qrcode-monkey.com API (`GET https://api.qrcode-monkey.com/qr/custom?data=…&config=<JSON>&size=…&file=…`). Style names verified 10/2026. An unknown body, eye or ball name returns no error but an unscannable image, so stick to the names below.

Contents:
- Data encoding
- Style parameters: body styles, eye frames, eye balls
- Color parameters
- Rotation and flip options
- Output options
- Logo
- Color best practices
- Common presets

## Data Encoding

The `data` parameter can contain:
- **URLs**: `https://example.com`
- **Plain text**: Any text string
- **Email**: `mailto:name@example.com`
- **Phone**: `tel:+1234567890`
- **SMS**: `sms:+1234567890`
- **WiFi**: `WIFI:T:WPA;S:NetworkName;P:Password;;`
- **vCard**: Contact information in vCard format

## Style Parameters

### Body Styles (`body`)
- `square` - Classic square dots (default)
- `mosaic` - Mosaic pattern
- `dot` - Round dots
- `circle` - Circular pattern
- `circle-zebra` - Zebra-striped circles
- `circle-zebra-vertical` - Vertical zebra stripes
- `circular` - Circular wave pattern
- `edge-cut` - Cut edge squares
- `edge-cut-smooth` - Smooth cut edges
- `leaf` - Leaf-shaped pattern
- `pointed` - Pointed squares
- `pointed-edge-cut` - Pointed with cut edges
- `pointed-in` - Inward pointed
- `pointed-in-smooth` - Smooth inward pointed
- `pointed-smooth` - Smooth pointed
- `round` - Rounded squares
- `rounded-in` - Inward rounded
- `rounded-in-smooth` - Smooth inward rounded
- `rounded-pointed` - Rounded and pointed
- `star` - Star pattern
- `diamond` - Diamond pattern

### Eye Frames (`eye`)
- `frame0` - Simple square frame (default)
- `frame1` - Rounded square frame
- `frame2` - Extra rounded frame
- `frame3` - Circle frame
- `frame4` - Square with rounded inner corners
- `frame5` - Rounded with dot corners
- `frame6` - Circle with squared corners
- `frame7` - Leaf frame
- `frame8` - Pointed frame
- `frame9` - (valid, unnamed variant)
- `frame10` - Diamond frame
- `frame11` - Circular frame variant
- `frame12` - Star frame
- `frame13` - Flower frame
- `frame14` - Shield frame
- `frame15` - (valid, unnamed variant)
- `frame16` - Custom artistic frame

### Eye Balls (`eyeBall`)
- `ball0` - Square ball (default)
- `ball1` - Rounded square ball
- `ball2` - Extra rounded ball
- `ball3` - Circle ball
- `ball4` - (valid, unnamed variant)
- `ball5` - Diamond ball
- `ball6` - Rounded diamond
- `ball7` - Leaf ball
- `ball8` - Star ball
- `ball9` - (valid, unnamed variant)
- `ball10` - Flower ball
- `ball11` - Shield ball
- `ball12` - Heart ball
- `ball13` - Square with rounded corners
- `ball14` - Circular variant
- `ball15` - Artistic ball
- `ball16` - Custom ball variant 1
- `ball17` - Custom ball variant 2
- `ball18` - Custom ball variant 3
- `ball19` - Custom ball variant 4

## Color Parameters

### Basic Colors
- `bgColor` - Background color (hex, default: `#FFFFFF`)
- `bodyColor` - Main QR code body color (hex, default: `#000000`)

### Eye Colors
- `eye1Color` - Upper left eye color (hex, defaults to bodyColor)
- `eye2Color` - Upper right eye color (hex, defaults to bodyColor)
- `eye3Color` - Lower left eye color (hex, defaults to bodyColor)

### Eye Ball Colors
- `eyeBall1Color` - Upper left eye ball color (hex, defaults to bodyColor)
- `eyeBall2Color` - Upper right eye ball color (hex, defaults to bodyColor)
- `eyeBall3Color` - Lower left eye ball color (hex, defaults to bodyColor)

### Gradient Options
- `gradientColor1` - First gradient color (hex, optional)
- `gradientColor2` - Second gradient color (hex, optional)
- `gradientType` - Gradient type: `linear` or `radial`
- `gradientOnEyes` - Apply gradient to entire QR code (boolean, default: false)

## Rotation and Flip Options

### Eye Frame Rotation (`erf1`, `erf2`, `erf3`)
Arrays that can contain:
- `"fv"` - Flip vertically
- `"fh"` - Flip horizontally
- Example: `["fv", "fh"]` - Flip both ways

### Eye Ball Rotation (`brf1`, `brf2`, `brf3`)
Same options as eye frame rotation.

## Output Options

- `size` - QR code size in pixels (1-3480; API default 300, script default 500); the returned image is about 16 % larger because of the quiet zone
- `file` - Output format: `png`, `svg`, `jpg`, `pdf`, `eps`
  - Note: `pdf` and `eps` don't support gradients

## Logo Options

The API can embed a logo (uploaded image referenced in the config, POST request). `scripts/generate_qrcode.py` does **not** implement this; for a logo, add it to the finished image yourself (e.g. with Pillow, centred, at most about 20 % of the width, with error correction level H) and test that the code still scans.

## Color Best Practices

1. **Contrast**: Background should be lighter than foreground for scannability
2. **Brightness difference**: Aim for at least 100 points difference
3. **Avoid gradients on eyes** unless using high contrast colors
4. **Test scannability**: Always test QR codes with multiple devices
5. **Safe defaults**: Black on white (`#000000` on `#FFFFFF`) always works

## Common Presets

### Professional (Blue)
```
bodyColor: #0277bd
bgColor: #FFFFFF
eye: frame1
eyeBall: ball2
```

### Modern (Gradient)
```
gradientColor1: #667eea
gradientColor2: #764ba2
gradientType: linear
bgColor: #FFFFFF
body: round
```

### Minimalist
```
bodyColor: #000000
bgColor: #FFFFFF
body: dot
eye: frame0
eyeBall: ball0
```
