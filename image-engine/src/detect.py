from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

def load_mask(mask_path: str, size: tuple[int, int]) -> Image.Image:
    p = Path(mask_path)
    if not p.exists():
        raise FileNotFoundError(f"Missing mask: {p}")
    mask = Image.open(p).convert("L")
    if mask.size != size:
        raise ValueError(f"Mask {mask.size} must match source {size}")
    return mask

def propose_mask(source: Image.Image) -> Image.Image:
    """Zero-cost conservative proposal for lamp images.

    Finds bright, low-saturation regions that are plausible shades/bulbs.
    This is intentionally conservative: uncertain images should be rejected
    rather than changing unrelated product pixels.
    """
    rgb = source.convert("RGB")
    hsv = rgb.convert("HSV")
    _, sat, val = hsv.split()

    bright = val.point(lambda p: 255 if p >= 150 else 0)
    low_sat = sat.point(lambda p: 255 if p <= 115 else 0)
    mask = ImageChops.multiply(bright, low_sat)

    # Remove tiny JPEG noise, then slightly close holes inside plausible emitters.
    mask = mask.filter(ImageFilter.MedianFilter(size=5))
    mask = mask.filter(ImageFilter.MaxFilter(size=9))
    mask = mask.filter(ImageFilter.MinFilter(size=7))
    return mask

# Imported here to keep Pillow-only dependency.
from PIL import ImageChops
