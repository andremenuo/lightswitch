from PIL import Image, ImageFilter, ImageEnhance

def relight(source: Image.Image, mask: Image.Image) -> Image.Image:
    """Deterministic zero-cost baseline. Only mask-permitted pixels are replaced."""
    src = source.convert("RGB")
    # Warm, brighter candidate generated from the original pixels—not a regenerated scene.
    warm = ImageEnhance.Brightness(src).enhance(1.35)
    r, g, b = warm.split()
    r = r.point(lambda x: min(255, int(x * 1.08)))
    b = b.point(lambda x: int(x * 0.90))
    candidate = Image.merge("RGB", (r, g, b))
    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=max(1, src.width // 300)))
    # Hard permission boundary: blur may not leak outside the original mask.
    soft_mask = Image.composite(soft_mask, Image.new("L", mask.size, 0), mask)
    return Image.composite(candidate, src, soft_mask)
