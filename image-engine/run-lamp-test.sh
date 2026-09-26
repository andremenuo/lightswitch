#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python src/batch.py input --manifest lamp-test-manifest.json --output-dir output --mask-dir masks
