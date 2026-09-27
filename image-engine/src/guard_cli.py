import argparse, json
from pathlib import Path
from guard import validate_geometry

def main():
    ap = argparse.ArgumentParser(description="Light Switch geometry guard")
    ap.add_argument("off")
    ap.add_argument("on")
    ap.add_argument("--profile", choices=["product", "lifestyle"], default="lifestyle")
    ap.add_argument("--report")
    args = ap.parse_args()

    report = validate_geometry(args.off, args.on, args.profile)
    payload = json.dumps(report, indent=2)
    print(payload)

    if args.report:
        p = Path(args.report)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")

    raise SystemExit(0 if report["pass"] else 2)

if __name__ == "__main__":
    main()
