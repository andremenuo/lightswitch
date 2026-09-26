import argparse, json
from pathlib import Path
from PIL import Image
from detect import load_mask
from relight import relight
from validate import validate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("mask")
    ap.add_argument("--output", default="output/on.png")
    args = ap.parse_args()

    source = Image.open(args.source).convert("RGB")
    mask = load_mask(args.mask, source.size)
    output = relight(source, mask)
    report = validate(source, output, mask)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if report["pass"]:
        output.save(out, "PNG")
    report_path = out.with_suffix(".json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
