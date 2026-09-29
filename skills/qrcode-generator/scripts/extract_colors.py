#!/usr/bin/env python3
"""
Extract dominant colors from a website for QR code branding.

This script fetches a website and analyzes its colors to suggest
QR code styling that matches the brand.
"""

import urllib.request
import re
import sys
import argparse
from collections import Counter
from typing import List, Tuple


def extract_hex_colors(html: str) -> List[str]:
    """Extract all hex color codes from HTML/CSS."""
    # Match hex colors in various formats
    pattern = r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b'
    matches = re.findall(pattern, html)
    
    # Normalize 3-digit hex to 6-digit
    normalized = []
    for match in matches:
        if len(match) == 3:
            # Expand #abc to #aabbcc
            normalized.append('#' + ''.join([c*2 for c in match]))
        else:
            normalized.append('#' + match)
    
    return normalized


def color_brightness(hex_color: str) -> float:
    """Calculate perceived brightness of a color (0-255)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    # Use perceived brightness formula
    return (r * 0.299 + g * 0.587 + b * 0.114)


def is_grayscale(hex_color: str) -> bool:
    """Check if a color is grayscale (R=G=B)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return r == g == b


def extract_brand_colors(url: str) -> dict:
    """
    Extract brand colors from a website.
    
    Args:
        url: The website URL to analyze
    
    Returns:
        Dictionary with suggested colors for QR code styling
    """
    try:
        # Fetch the website
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Extract all hex colors
        colors = extract_hex_colors(html)
        
        if not colors:
            return {
                "primary": "#000000",
                "secondary": "#FFFFFF",
                "accent": None,
                "message": "No colors found, using defaults"
            }
        
        # Count color frequency
        color_counts = Counter(colors)
        
        # Filter out pure white and near-white colors (common backgrounds)
        filtered_colors = [
            (color, count) for color, count in color_counts.items()
            if color_brightness(color) < 240
        ]
        
        # Sort by frequency
        sorted_colors = sorted(filtered_colors, key=lambda x: x[1], reverse=True)
        
        # Find primary color (most common non-white color)
        primary_color = sorted_colors[0][0] if sorted_colors else "#000000"
        
        # Find contrasting colors for secondary
        dark_colors = [c for c, _ in sorted_colors if color_brightness(c) < 128]
        light_colors = [c for c, _ in sorted_colors if color_brightness(c) >= 128]
        
        # Choose secondary color with good contrast to primary
        if color_brightness(primary_color) < 128:
            # Primary is dark, use light secondary
            secondary_color = light_colors[0] if light_colors else "#FFFFFF"
        else:
            # Primary is light, use dark secondary
            secondary_color = dark_colors[0] if dark_colors else "#000000"
        
        # Find accent color (second most common, different from primary)
        accent_color = None
        for color, _ in sorted_colors[1:]:
            if color != primary_color and not is_grayscale(color):
                accent_color = color
                break
        
        return {
            "primary": primary_color,
            "secondary": secondary_color,
            "accent": accent_color,
            "all_colors": [c for c, _ in sorted_colors[:10]],
            "message": f"Extracted {len(sorted_colors)} colors from website"
        }
    
    except Exception as e:
        print(f"Error extracting colors from {url}: {e}", file=sys.stderr)
        return {
            "primary": "#000000",
            "secondary": "#FFFFFF",
            "accent": None,
            "message": f"Error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract brand colors from a website"
    )
    parser.add_argument("url", help="Website URL to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = extract_brand_colors(args.url)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(f"Brand Colors from {args.url}:")
        print(f"  Primary:   {result['primary']}")
        print(f"  Secondary: {result['secondary']}")
        if result['accent']:
            print(f"  Accent:    {result['accent']}")
        print(f"\n{result['message']}")
        if 'all_colors' in result and len(result['all_colors']) > 3:
            print(f"\nOther colors found: {', '.join(result['all_colors'][3:])}")


if __name__ == "__main__":
    main()
