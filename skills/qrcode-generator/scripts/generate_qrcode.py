#!/usr/bin/env python3
"""
Generate QR codes using the qrcode-monkey.com API.

This script creates customizable QR codes with various styling options.
"""

import urllib.parse
import urllib.request
import json
import sys
import argparse
from typing import Optional


def generate_qrcode(
    data: str,
    output_path: str,
    size: int = 300,
    bg_color: str = "#FFFFFF",
    body_color: str = "#000000",
    body: str = "square",
    eye: str = "frame0",
    eye_ball: str = "ball0",
    eye1_color: Optional[str] = None,
    eye2_color: Optional[str] = None,
    eye3_color: Optional[str] = None,
    eyeball1_color: Optional[str] = None,
    eyeball2_color: Optional[str] = None,
    eyeball3_color: Optional[str] = None,
    gradient_color1: Optional[str] = None,
    gradient_color2: Optional[str] = None,
    gradient_type: str = "linear",
    gradient_on_eyes: bool = False,
    logo_path: Optional[str] = None,
    file_type: str = "png"
) -> str:
    """
    Generate a QR code and save it to a file.
    
    Args:
        data: The data to encode in the QR code (URL, text, vCard, etc.)
        output_path: Path where the QR code image will be saved
        size: Size of the QR code in pixels (max 3480)
        bg_color: Background color as hex (e.g., "#FFFFFF")
        body_color: QR code body color as hex (e.g., "#000000")
        body: Body style (square, mosaic, dot, circle, etc.)
        eye: Eye frame style (frame0-frame16)
        eye_ball: Eye ball style (ball0-ball19)
        eye1_color: Color of upper left eye (defaults to body_color)
        eye2_color: Color of upper right eye (defaults to body_color)
        eye3_color: Color of lower left eye (defaults to body_color)
        eyeball1_color: Color of upper left eye ball (defaults to body_color)
        eyeball2_color: Color of upper right eye ball (defaults to body_color)
        eyeball3_color: Color of lower left eye ball (defaults to body_color)
        gradient_color1: First gradient color (optional)
        gradient_color2: Second gradient color (optional)
        gradient_type: Gradient type ("linear" or "radial")
        gradient_on_eyes: Apply gradient to entire QR code including eyes
        logo_path: Path to logo image to embed in QR code (optional)
        file_type: Output format (png, svg, jpg, pdf, eps)
    
    Returns:
        Path to the saved QR code file
    """
    # Use body_color as default for eye colors if not specified
    eye1_color = eye1_color or body_color
    eye2_color = eye2_color or body_color
    eye3_color = eye3_color or body_color
    eyeball1_color = eyeball1_color or body_color
    eyeball2_color = eyeball2_color or body_color
    eyeball3_color = eyeball3_color or body_color
    
    # Build config object
    config = {
        "bgColor": bg_color,
        "body": body,
        "eye": eye,
        "eyeBall": eye_ball,
        "gradientOnEyes": str(gradient_on_eyes).lower(),
        "brf1": [],
        "brf2": [],
        "brf3": [],
        "erf1": [],
        "erf2": [],
        "erf3": [],
        "bodyColor": body_color,
        "eye1Color": eye1_color,
        "eye2Color": eye2_color,
        "eye3Color": eye3_color,
        "eyeBall1Color": eyeball1_color,
        "eyeBall2Color": eyeball2_color,
        "eyeBall3Color": eyeball3_color,
    }
    
    # Add gradient colors if specified
    if gradient_color1:
        config["gradientColor1"] = gradient_color1
    if gradient_color2:
        config["gradientColor2"] = gradient_color2
    if gradient_color1 or gradient_color2:
        config["gradientType"] = gradient_type
    
    # Build URL
    base_url = "https://api.qrcode-monkey.com/qr/custom"
    params = {
        "data": data,
        "config": json.dumps(config),
        "size": str(size),
        "download": "false",
        "file": file_type
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    # Download the QR code
    try:
        with urllib.request.urlopen(url) as response:
            qr_data = response.read()
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(qr_data)
        
        print(f"QR code saved to: {output_path}")
        return output_path
    
    except urllib.error.URLError as e:
        print(f"Error generating QR code: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate customizable QR codes using qrcode-monkey.com API"
    )
    parser.add_argument("data", help="Data to encode (URL, text, etc.)")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--size", type=int, default=300, help="QR code size in pixels (default: 300, max: 3480)")
    parser.add_argument("--bg-color", default="#FFFFFF", help="Background color (default: #FFFFFF)")
    parser.add_argument("--body-color", default="#000000", help="Body color (default: #000000)")
    parser.add_argument("--body", default="square", help="Body style (default: square)")
    parser.add_argument("--eye", default="frame0", help="Eye style (default: frame0)")
    parser.add_argument("--eye-ball", default="ball0", help="Eye ball style (default: ball0)")
    parser.add_argument("--gradient-color1", help="First gradient color")
    parser.add_argument("--gradient-color2", help="Second gradient color")
    parser.add_argument("--gradient-type", default="linear", choices=["linear", "radial"], help="Gradient type")
    parser.add_argument("--gradient-on-eyes", action="store_true", help="Apply gradient to entire QR code")
    parser.add_argument("--file-type", default="png", choices=["png", "svg", "jpg", "pdf", "eps"], help="Output format (default: png)")
    
    args = parser.parse_args()
    
    generate_qrcode(
        data=args.data,
        output_path=args.output,
        size=args.size,
        bg_color=args.bg_color,
        body_color=args.body_color,
        body=args.body,
        eye=args.eye,
        eye_ball=args.eye_ball,
        gradient_color1=args.gradient_color1,
        gradient_color2=args.gradient_color2,
        gradient_type=args.gradient_type,
        gradient_on_eyes=args.gradient_on_eyes,
        file_type=args.file_type
    )


if __name__ == "__main__":
    main()
