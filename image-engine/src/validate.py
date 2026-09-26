from PIL import Image, ImageChops

def validate(source: Image.Image, output: Image.Image, mask: Image.Image) -> dict:
    src = source.convert("RGB")
    out = output.convert("RGB")
    if src.size != out.size:
        return {"pass": False, "reason": "dimension_mismatch"}

    diff = ImageChops.difference(src, out)
    outside = Image.composite(diff, Image.new("RGB", src.size, 0), mask.point(lambda p: 255 - p))
    bbox = outside.getbbox()
    changed_outside = bbox is not None
    changed_anywhere = diff.getbbox() is not None

    return {
        "pass": (not changed_outside) and changed_anywhere,
        "same_dimensions": True,
        "changed_outside_mask": changed_outside,
        "light_change_detected": changed_anywhere,
    }
