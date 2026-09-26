from pathlib import Path
from PIL import Image

def load_mask(mask_path: str, size: tuple[int, int]) -> Image.Image:
    """Load an explicit grayscale permission mask. White pixels may change."""
    p = Path(mask_path)
    if not p.exists():
        raise FileNotFoundError(
            f"Missing mask: {p}. Phase 1 deliberately requires an explicit mask "
            "before automatic detection is introduced."
        )
    mask = Image.open(p).convert("L")
    if mask.size != size:
        raise ValueError(f"Mask {mask.size} must match source {size}")
    return mask
