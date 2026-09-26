import argparse, json
from pathlib import Path
from PIL import Image
from detect import propose_mask
from relight import relight
from validate import validate

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", nargs="?", default="input")
    ap.add_argument("--output-dir", default="output")
    ap.add_argument("--mask-dir", default="masks")
    args = ap.parse_args()

    inp, outdir, maskdir = Path(args.input_dir), Path(args.output_dir), Path(args.mask_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    maskdir.mkdir(parents=True, exist_ok=True)
    summary = []

    for path in sorted(p for p in inp.iterdir() if p.suffix.lower() in SUPPORTED):
        src = Image.open(path).convert("RGB")
        mask = propose_mask(src)
        mask_path = maskdir / f"{path.stem}-mask.png"
        mask.save(mask_path)

        on = relight(src, mask)
        report = validate(src, on, mask)
        report["source"] = path.name
        report["mask"] = mask_path.name

        if report["pass"]:
            on.save(outdir / f"{path.stem}-on.png", "PNG")
        (outdir / f"{path.stem}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        summary.append(report)

    passed = sum(1 for r in summary if r["pass"])
    result = {"processed": len(summary), "passed_safety": passed, "results": summary}
    (outdir / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
