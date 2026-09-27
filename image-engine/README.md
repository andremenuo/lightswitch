# Light Switch Image Engine

Goal: create an ON image from an immutable merchant OFF master without changing product or scene geometry.

## Locked pipeline

OFF master -> scene/light detection -> relight engine -> geometry guard -> PASS / RETRY / REJECT.

The relight engine is replaceable. FreeLit is candidate #1 for the first benchmark. Light Switch must not depend on a paid image API.

## Geometry Guard V1

Run:

```
python src/guard_cli.py OFF.jpg ON.jpg --profile lifestyle --report output/report.json
```

Profiles:

- `product`: stricter structural thresholds.
- `lifestyle`: allows major illumination/exposure changes but not spatial movement.

V1 checks same canvas, illumination-normalized edge overlap and ORB feature displacement. Thresholds are intentionally conservative starting values; they are not claimed as proven until calibrated on real benchmark pairs.

A failed candidate must never be published automatically.

## Development order

1. Benchmark FreeLit on real OFF masters with known light masks.
2. Run every candidate through Geometry Guard.
3. Calibrate guard thresholds from accepted/rejected pairs.
4. Automate light-source detection/masking.
5. Add retry logic.
6. Only then connect automatic ecommerce ingestion/publishing.
