# Light Switch

Minimal e-commerce lighting runtime + image-engine experiments.

## Current focus: Phase 1 — OFF → ON image engine

The original OFF image is the immutable source of truth. The engine must never regenerate product geometry or the full scene.

### Pipeline

1. `detect.py` — produces/loads the permitted light mask.
2. `relight.py` — changes pixels only inside that mask.
3. `validate.py` — rejects output if dimensions change or pixels outside the mask differ.
4. `run.py` — runs the pipeline and writes a validation report.

### Definition of done for Phase 1

- Start with lamps only.
- 10 real OFF images in.
- 10 ON candidates out.
- Same dimensions and geometry.
- Zero changed decoded pixels outside the permitted mask.
- Failed validation = rejected, never published.

This first scaffold intentionally has no paid API dependency. Relighting quality is the next experiment; geometry safety is enforced first.
