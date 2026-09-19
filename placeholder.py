#!/usr/bin/env python3
"""
placeholder.py - Generate placeholder images for your website.

Every image gets:
  - a black background with a thin grey cross (so you can see the center at a glance)
  - your own custom name as a big title (e.g. "HERO IMAGE")
  - the dimensions (e.g. "1920 x 1080")
  - the file type (e.g. ".jpg")

Usage:
  python placeholder.py                                  -> interactive mode
  python placeholder.py "Hero Image"                     -> 1920x1080 jpg
  python placeholder.py "Hero Image" -s 1600x900         -> custom size
  python placeholder.py "Hero" "Team:800x600" "Logo:400x400"
                                                         -> several at once, each with its own size
  python placeholder.py "Banner" -f png -o ./img         -> png, custom output folder

Requires: Python 3.8+ and Pillow  (pip install pillow)
The font (Poppins Black, OFL license) is downloaded automatically on first run.
"""

import argparse
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is missing. Install it with:  pip install pillow")

# --------------------------------------------------------------------------- #
# Settings (tuned to match a 1920 x 1080 reference image)
# --------------------------------------------------------------------------- #
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Black.ttf"
FONT_PATH = Path(__file__).resolve().parent / "fonts" / "Poppins-Black.ttf"

REF_W, REF_H = 1920, 1080  # reference size that all measurements are based on
TITLE_SIZE = 144           # title font size at 1920x1080
INFO_SIZE = 72             # font size of "1920 x 1080" and ".jpg"
TRACKING = 0.10            # letter spacing (in em)
TITLE_BASE = -1            # title baseline relative to the center (px at 1920x1080)
SIZE_BASE = 86             # baseline of the dimensions line relative to the center
EXT_BASE = 174             # baseline of the file type line relative to the center
X_SHIFT = -2               # small horizontal correction (px at 1920x1080)
LINE_WIDTH = 1             # thickness of the cross (px at 1920x1080)
MAX_TEXT_WIDTH = 0.92      # text may use at most 92% of the image width

FORMATS = {
    "jpg": ("JPEG", ".jpg"),
    "jpeg": ("JPEG", ".jpg"),
    "png": ("PNG", ".png"),
    "webp": ("WEBP", ".webp"),
}

FALLBACK_FONTS = [
    "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


# --------------------------------------------------------------------------- #
# Font
# --------------------------------------------------------------------------- #
def find_font(custom=None):
    """Return the path of the font to use (downloads Poppins if needed)."""
    if custom:
        return str(custom)
    if FONT_PATH.exists():
        return str(FONT_PATH)
    try:
        print("Downloading Poppins Black (one time only)...")
        FONT_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        return str(FONT_PATH)
    except Exception as exc:  # no internet, blocked, ...
        print(f"Could not download Poppins ({exc}).")
        for candidate in FALLBACK_FONTS:
            if Path(candidate).exists():
                print(f"Falling back to: {candidate}")
                return candidate
        print(
            "No suitable font found. Download Poppins-Black.ttf manually and put it in:\n"
            f"{FONT_PATH}\n"
            "or pass a font with --font path/to/font.ttf"
        )
        sys.exit(1)


# --------------------------------------------------------------------------- #
# Drawing text with letter spacing, centered on the visible ink
# --------------------------------------------------------------------------- #
def layout(text, font, tracking_px):
    """Return the x position of each character (kerning + tracking) and the ink extents."""
    xs, x = [], 0.0
    for i, ch in enumerate(text):
        xs.append(x)
        adv = font.getlength(ch)
        if i + 1 < len(text):  # kerning with the next character
            nxt = text[i + 1]
            adv = font.getlength(ch + nxt) - font.getlength(nxt)
        x += adv + tracking_px
    left = font.getbbox(text[0])[0]
    right = xs[-1] + font.getbbox(text[-1])[2]
    return xs, left, right


def text_width(text, font_path, size):
    font = ImageFont.truetype(font_path, max(1, round(size)))
    _, left, right = layout(text, font, TRACKING * size)
    return right - left


def draw_centered(draw, text, font_path, size, cx, baseline, fill):
    font = ImageFont.truetype(font_path, max(1, round(size)))
    xs, left, right = layout(text, font, TRACKING * size)
    x0 = cx - (left + right) / 2
    for ch, x in zip(text, xs):
        if ch != " ":
            draw.text((x0 + x, baseline), ch, font=font, fill=fill, anchor="ls")


# --------------------------------------------------------------------------- #
# The cross (anti-aliased through supersampling)
# --------------------------------------------------------------------------- #
def draw_cross(img, color, width_px):
    w, h = img.size
    ss = 4 if w * h * 16 <= 80_000_000 else 2  # lower supersampling for huge images
    mask = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(mask)
    lw = max(1, round(width_px * ss))
    d.line([(0, 0), (w * ss, h * ss)], fill=255, width=lw)
    d.line([(0, h * ss), (w * ss, 0)], fill=255, width=lw)
    box = getattr(Image, "Resampling", Image).BOX
    mask = mask.resize((w, h), box)
    img.paste(color, (0, 0), mask)


# --------------------------------------------------------------------------- #
# Building a placeholder
# --------------------------------------------------------------------------- #
def make_placeholder(name, width, height, ext, font_path,
                     bg="#000000", fg="#ffffff", line_color="#808080", cross=True):
    scale = min(width / REF_W, height / REF_H)
    cx, cy = width / 2 + X_SHIFT * scale, height / 2

    img = Image.new("RGB", (width, height), ImageColor.getrgb(bg))
    if cross:
        draw_cross(img, ImageColor.getrgb(line_color), max(1, round(LINE_WIDTH * scale)))
    draw = ImageDraw.Draw(img)
    fg = ImageColor.getrgb(fg)

    title = name.strip().upper() or "PLACEHOLDER"

    # Title: scales with the image size, but shrinks when the name is too long
    title_size = TITLE_SIZE * scale
    tw = text_width(title, font_path, title_size)
    if tw > width * MAX_TEXT_WIDTH:
        title_size *= width * MAX_TEXT_WIDTH / tw

    # Info lines: shrink a bit more if "1920 x 1080" doesn't fit (tiny images)
    info_size = INFO_SIZE * scale
    size_txt = f"{width} x {height}"
    sw = text_width(size_txt, font_path, info_size)
    if sw > width * MAX_TEXT_WIDTH:
        info_size *= width * MAX_TEXT_WIDTH / sw

    draw_centered(draw, title, font_path, title_size, cx, cy + TITLE_BASE * scale, fg)
    draw_centered(draw, size_txt, font_path, info_size, cx, cy + SIZE_BASE * scale, fg)
    draw_centered(draw, ext, font_path, info_size, cx, cy + EXT_BASE * scale, fg)
    return img


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def parse_size(text):
    m = re.fullmatch(r"\s*(\d+)\s*[xX×*]\s*(\d+)\s*", text)
    if not m:
        raise ValueError(f"Invalid size '{text}'. Use e.g. 1920x1080")
    w, h = int(m.group(1)), int(m.group(2))
    if not (16 <= w <= 10000 and 16 <= h <= 10000):
        raise ValueError("Width and height must be between 16 and 10000 px.")
    return w, h


def parse_item(item, default_size):
    """'Name' or 'Name:800x600' -> (name, (w, h))"""
    m = re.fullmatch(r"(.*?)(?::(\d+\s*[xX×*]\s*\d+))?", item.strip())
    name = m.group(1).strip()
    size = parse_size(m.group(2)) if m.group(2) else default_size
    return name, size


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "placeholder"


def save(img, path, fmt_key, quality):
    pil_fmt = FORMATS[fmt_key][0]
    kwargs = {}
    if pil_fmt == "JPEG":
        kwargs = {"quality": quality, "subsampling": 0, "optimize": True}
    elif pil_fmt == "WEBP":
        kwargs = {"quality": quality}
    elif pil_fmt == "PNG":
        kwargs = {"optimize": True}
    img.save(path, pil_fmt, **kwargs)


def create(name, size, args, font_path):
    fmt_key = args.format.lower().lstrip(".")
    ext = FORMATS[fmt_key][1]
    img = make_placeholder(
        name, size[0], size[1], ext, font_path,
        bg=args.bg, fg=args.fg, line_color=args.line_color, cross=not args.no_cross,
    )
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slugify(name)}{ext}"
    save(img, path, fmt_key, args.quality)
    print(f"  ✔ {path}  ({size[0]}x{size[1]})")


def interactive(args, font_path, default_size):
    print("Placeholder maker - leave the name empty to quit.\n")
    while True:
        name = input("Name (e.g. Hero Image): ").strip()
        if not name:
            break
        while True:
            raw = input(f"Size [{default_size[0]}x{default_size[1]}]: ").strip()
            try:
                size = parse_size(raw) if raw else default_size
                break
            except ValueError as exc:
                print(f"  {exc}")
        create(name, size, args, font_path)
        print()


def main():
    p = argparse.ArgumentParser(
        description="Generate placeholder images with a cross marking the center.",
        epilog='Example: python placeholder.py "Hero Image" "Team:800x600" -f png',
    )
    p.add_argument("items", nargs="*", metavar="NAME[:WxH]",
                   help="Placeholder name, optionally with its own size (e.g. Team:800x600)")
    p.add_argument("-s", "--size", default="1920x1080", help="Default size (default: 1920x1080)")
    p.add_argument("-f", "--format", default="jpg", choices=sorted(FORMATS), help="File type (default: jpg)")
    p.add_argument("-o", "--output", default="placeholders", help="Output folder (default: ./placeholders)")
    p.add_argument("--bg", default="#000000", help="Background color (default: #000000)")
    p.add_argument("--fg", default="#ffffff", help="Text color (default: #ffffff)")
    p.add_argument("--line-color", default="#808080", help="Cross color (default: #808080)")
    p.add_argument("--no-cross", action="store_true", help="Don't draw the cross")
    p.add_argument("--quality", type=int, default=92, help="Quality for jpg/webp (default: 92)")
    p.add_argument("--font", help="Use your own font file (.ttf) instead of Poppins Black")
    args = p.parse_args()

    try:
        default_size = parse_size(args.size)
        ImageColor.getrgb(args.bg), ImageColor.getrgb(args.fg), ImageColor.getrgb(args.line_color)
    except ValueError as exc:
        p.error(str(exc))

    font_path = find_font(args.font)

    if not args.items:
        interactive(args, font_path, default_size)
        return

    print("Creating:")
    for item in args.items:
        try:
            name, size = parse_item(item, default_size)
            create(name, size, args, font_path)
        except ValueError as exc:
            print(f"  ✘ {item}: {exc}")


if __name__ == "__main__":
    main()
