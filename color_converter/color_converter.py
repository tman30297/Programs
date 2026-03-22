#!/usr/bin/env python3
"""
Color Converter - Convert between color formats with visual preview
Usage: python color_converter.py [color]
Examples:
  python color_converter.py "#ff5500"
  python color_converter.py "rgb(255, 85, 0)"
  python color_converter.py "hsl(20, 100%, 50%)"
  python color_converter.py "coral"
  python color_converter.py (interactive mode)
"""

import re
import sys
import shutil
import argparse
from typing import Optional, Tuple

# Terminal colors for visual preview
class TerminalColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Basic colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLACK = "\033[40m"
    BG_WHITE = "\033[47m"
    
    @classmethod
    def fg(cls, r: int, g: int, b: int) -> str:
        """Convert RGB to terminal foreground color"""
        # Use 256-color mode
        if r == g == b:
            # Grayscale
            gray = int(r / 255 * 23)
            return f"\033[38;5;{232 + gray}m"
        # Color cube
        r_idx = int(r / 255 * 5)
        g_idx = int(g / 255 * 5)
        b_idx = int(b / 255 * 5)
        color_idx = 16 + r_idx * 36 + g_idx * 6 + b_idx
        return f"\033[38;5;{color_idx}m"
    
    @classmethod
    def bg(cls, r: int, g: int, b: int) -> str:
        """Convert RGB to terminal background color"""
        if r == g == b:
            gray = int(r / 255 * 23)
            return f"\033[48;5;{232 + gray}m"
        r_idx = int(r / 255 * 5)
        g_idx = int(g / 255 * 5)
        b_idx = int(b / 255 * 5)
        color_idx = 16 + r_idx * 36 + g_idx * 6 + b_idx
        return f"\033[48;5;{color_idx}m"


class ColorConverter:
    """Convert between color formats"""
    
    # Common color names
    NAMED_COLORS = {
        'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
        'black': (0, 0, 0), 'white': (255, 255, 255), 'yellow': (255, 255, 0),
        'cyan': (0, 255, 255), 'magenta': (255, 0, 255), 'orange': (255, 165, 0),
        'pink': (255, 192, 203), 'purple': (128, 0, 128), 'brown': (165, 42, 42),
        'gray': (128, 128, 128), 'grey': (128, 128, 128), 'coral': (255, 127, 80),
        'tomato': (255, 99, 71), 'gold': (255, 215, 0), 'silver': (192, 192, 192),
        'navy': (0, 0, 128), 'teal': (0, 128, 128), 'olive': (128, 128, 0),
        'maroon': (128, 0, 0), 'aqua': (0, 255, 255), 'fuchsia': (255, 0, 255),
        'lime': (0, 255, 0), 'aquamarine': (127, 255, 212), 'crimson': (220, 20, 60),
        'indigo': (75, 0, 130), 'violet': (238, 130, 238), 'beige': (245, 245, 220),
        'ivory': (255, 255, 240), 'khaki': (240, 230, 140), 'lavender': (230, 230, 250),
        'salmon': (250, 128, 114), 'turquoise': (64, 224, 208), 'wheat': (245, 222, 179),
    }
    
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'ColorConverter':
        """Parse HEX color string"""
        hex_color = hex_color.strip().lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c*2 for c in hex_color)
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: #{hex_color}")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return cls(r, g, b)
    
    @classmethod
    def from_rgb(cls, rgb_str: str) -> 'ColorConverter':
        """Parse RGB/RGBA color string"""
        match = re.match(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', rgb_str)
        if not match:
            raise ValueError(f"Invalid RGB color: {rgb_str}")
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return cls(r, g, b)
    
    @classmethod
    def from_hsl(cls, hsl_str: str) -> 'ColorConverter':
        """Parse HSL/HSLA color string"""
        match = re.match(r'hsla?\s*\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?', hsl_str)
        if not match:
            raise ValueError(f"Invalid HSL color: {hsl_str}")
        h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return cls._hsl_to_rgb(h, s, l)
    
    @classmethod
    def from_hsv(cls, hsv_str: str) -> 'ColorConverter':
        """Parse HSV/HSB color string"""
        match = re.match(r'hsv\s*\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?', hsv_str)
        if not match:
            raise ValueError(f"Invalid HSV color: {hsv_str}")
        h, s, v = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return cls._hsv_to_rgb(h, s, v)
    
    @classmethod
    def from_name(cls, name: str) -> 'ColorConverter':
        """Parse named color"""
        name_lower = name.lower().strip()
        if name_lower in cls.NAMED_COLORS:
            r, g, b = cls.NAMED_COLORS[name_lower]
            return cls(r, g, b)
        raise ValueError(f"Unknown color name: {name}")
    
    @classmethod
    def parse(cls, color_str: str) -> 'ColorConverter':
        """Auto-detect and parse color format"""
        color_str = color_str.strip()
        
        # HEX
        if color_str.startswith('#') or re.match(r'^[0-9a-fA-F]{3,6}$', color_str):
            return cls.from_hex(color_str)
        
        # RGB/RGBA
        if color_str.lower().startswith('rgb'):
            return cls.from_rgb(color_str)
        
        # HSL/HSLA
        if color_str.lower().startswith('hsl'):
            return cls.from_hsl(color_str)
        
        # HSV/HSB
        if color_str.lower().startswith('hsv'):
            return cls.from_hsv(color_str)
        
        # Named color
        return cls.from_name(color_str)
    
    # Conversion methods
    def to_hex(self) -> str:
        """Convert to HEX"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}".upper()
    
    def to_rgb(self) -> str:
        """Convert to RGB"""
        return f"rgb({self.r}, {self.g}, {self.b})"
    
    def to_rgba(self) -> str:
        """Convert to RGBA"""
        return f"rgba({self.r}, {self.g}, {self.b}, 1)"
    
    def to_hsl(self) -> str:
        """Convert to HSL"""
        h, s, l = self._rgb_to_hsl(self.r, self.g, self.b)
        return f"hsl({h}, {s}%, {l}%)"
    
    def to_hsv(self) -> str:
        """Convert to HSV"""
        h, s, v = self._rgb_to_hsv(self.r, self.g, self.b)
        return f"hsv({h}, {s}%, {v}%)"
    
    def to_int(self) -> int:
        """Convert to integer"""
        return (self.r << 16) + (self.g << 8) + self.b
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Get RGB tuple"""
        return (self.r, self.g, self.b)
    
    @staticmethod
    def _rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
        r, g, b = r/255, g/255, b/255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            return (0, 0, int(l * 100))
        
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        
        if max_c == r:
            h = ((g - b) / d + (6 if g < b else 0)) / 6
        elif max_c == g:
            h = ((b - r) / d + 2) / 6
        else:
            h = ((r - g) / d + 4) / 6
        
        return (int(h*360), int(s*100), int(l*100))
    
    @staticmethod
    def _rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
        r, g, b = r/255, g/255, b/255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        d = max_c - min_c
        
        v = max_c
        s = 0 if max_c == 0 else d / max_c
        
        if max_c == min_c:
            return (0, int(s*100), int(v*100))
        
        if max_c == r:
            h = ((g - b) / d + (6 if g < b else 0)) / 6
        elif max_c == g:
            h = ((b - r) / d + 2) / 6
        else:
            h = ((r - g) / d + 4) / 6
        
        return (int(h*360), int(s*100), int(v*100))
    
    @staticmethod
    def _hsl_to_rgb(h: int, s: int, l: int) -> 'ColorConverter':
        s, l = s/100, l/100
        
        if s == 0:
            val = int(l * 255)
            return ColorConverter(val, val, val)
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        h = h / 360
        
        r = ColorConverter._hue_to_rgb(p, q, h + 1/3)
        g = ColorConverter._hue_to_rgb(p, q, h)
        b = ColorConverter._hue_to_rgb(p, q, h - 1/3)
        
        return ColorConverter(int(r*255), int(g*255), int(b*255))
    
    @staticmethod
    def _hsv_to_rgb(h: int, s: int, v: int) -> 'ColorConverter':
        s, v = s/100, v/100
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return ColorConverter(int((r+m)*255), int((g+m)*255), int((b+m)*255))
    
    @staticmethod
    def _hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    
    def get_contrast_color(self) -> 'ColorConverter':
        """Get high contrast color (black or white)"""
        luminance = (0.299*self.r + 0.587*self.g + 0.114*self.b) / 255
        return ColorConverter(0, 0, 0) if luminance > 0.5 else ColorConverter(255, 255, 255)


def print_color_preview(color: ColorConverter):
    """Print visual color preview in terminal"""
    term_width = shutil.get_terminal_size().columns
    preview_width = min(term_width - 4, 60)
    
    r, g, b = color.to_tuple()
    fg = TerminalColors.fg(*color.get_contrast_color().to_tuple())
    
    print(f"\n  {'━' * preview_width}")
    print(f" {TerminalColors.BG_WHITE}{TerminalColors.fg(r,g,b)}{' ' * preview_width}{TerminalColors.RESET}")
    print(f" {'━' * preview_width}")


def print_color_info(color: ColorConverter):
    """Print all color format conversions"""
    contrast = color.get_contrast_color()
    
    print(f"\n{TerminalColors.BOLD}Color Formats:{TerminalColors.RESET}")
    print(f"  HEX     : {color.to_hex()}")
    print(f"  RGB     : {color.to_rgb()}")
    print(f"  RGBA    : {color.to_rgba()}")
    print(f"  HSL     : {color.to_hsl()}")
    print(f"  HSV     : {color.to_hsv()}")
    print(f"  Integer : {color.to_int()}")
    print(f"  Tuple   : {color.to_tuple()}")
    print(f"  Contrast: #{contrast.to_hex()}")


def interactive_mode():
    """Interactive color picker mode"""
    print(f"{TerminalColors.BOLD}Color Converter - Interactive Mode{TerminalColors.RESET}")
    print("Enter a color (hex, rgb, hsl, hsv, or name). Press Ctrl+C to exit.\n")
    
    while True:
        try:
            color_str = input(f"{TerminalColors.CYAN}Color{TerminalColors.RESET} > ").strip()
            if not color_str:
                continue
            
            color = ColorConverter.parse(color_str)
            print_color_preview(color)
            print_color_info(color)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except ValueError as e:
            print(f"{TerminalColors.RED}Error: {e}{TerminalColors.RESET}")
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description='Color Converter - Convert between color formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  color_converter.py "#ff5500"
  color_converter.py "rgb(255, 85, 0)"
  color_converter.py "hsl(20, 100%, 50%)"
  color_converter.py "coral"
  color_converter.py --palette "#ff0000" "#00ff00" "#0000ff"
  color_converter.py --random
        '''
    )
    parser.add_argument('color', nargs='?', help='Color to convert (hex, rgb, hsl, hsv, or name)')
    parser.add_argument('--palette', nargs='*', help='Show multiple colors side by side')
    parser.add_argument('--random', action='store_true', help='Generate a random color')
    parser.add_argument('--interactive', '-i', action='store_true', help='Enter interactive mode')
    
    args = parser.parse_args()
    
    # Random color
    if args.random:
        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = ColorConverter(r, g, b)
        print_color_preview(color)
        print_color_info(color)
        return
    
    # Palette mode
    if args.palette:
        colors = [ColorConverter.parse(c) for c in args.palette]
        term_width = shutil.get_terminal_size().columns
        block_width = max(5, (term_width - 10) // len(colors))
        
        print()
        for color in colors:
            fg = TerminalColors.fg(*color.get_contrast_color().to_tuple())
            print(f" {TerminalColors.bg(*color.to_tuple())}{' ' * block_width}{TerminalColors.RESET}", end="")
        print()
        
        for color in colors:
            print(f" {color.to_hex():^{block_width}}", end="")
        print("\n")
        return
    
    # Interactive mode
    if args.interactive or not args.color:
        interactive_mode()
        return
    
    # Single color conversion
    try:
        color = ColorConverter.parse(args.color)
        print_color_preview(color)
        print_color_info(color)
    except ValueError as e:
        print(f"{TerminalColors.RED}Error: {e}{TerminalColors.RESET}")
        print("Try: color_converter.py --interactive")
        sys.exit(1)


if __name__ == '__main__':
    main()
