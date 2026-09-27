import cv2
import numpy as np
from pathlib import Path

PROFILES = {
    "product": {
        "min_edge_overlap": 0.94,
        "max_median_shift_px": 1.0,
        "max_p95_shift_px": 3.0,
        "min_good_matches": 30,
    },
    "lifestyle": {
        "min_edge_overlap": 0.90,
        "max_median_shift_px": 1.5,
        "max_p95_shift_px": 4.0,
        "min_good_matches": 40,
    },
}

def _gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    return img, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def _edges(gray):
    # Normalize local contrast so the comparison is less sensitive to day/evening exposure.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    norm = clahe.apply(gray)
    return cv2.Canny(norm, 60, 160)

def _edge_overlap(a, b):
    kernel = np.ones((3, 3), np.uint8)
    ad = cv2.dilate(a, kernel, iterations=1)
    bd = cv2.dilate(b, kernel, iterations=1)
    am = a > 0
    bm = b > 0
    if am.sum() == 0 or bm.sum() == 0:
        return 0.0
    recall_ab = np.logical_and(am, bd > 0).sum() / am.sum()
    recall_ba = np.logical_and(bm, ad > 0).sum() / bm.sum()
    return float(2 * recall_ab * recall_ba / max(recall_ab + recall_ba, 1e-9))

def _feature_shift(a, b):
    orb = cv2.ORB_create(nfeatures=5000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None:
        return {"good_matches": 0, "median_shift_px": float("inf"), "p95_shift_px": float("inf")}

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs = matcher.knnMatch(da, db, k=2)
    good = [m for m, n in pairs if m.distance < 0.72 * n.distance]
    if not good:
        return {"good_matches": 0, "median_shift_px": float("inf"), "p95_shift_px": float("inf")}

    shifts = np.array([
        np.linalg.norm(np.array(ka[m.queryIdx].pt) - np.array(kb[m.trainIdx].pt))
        for m in good
    ], dtype=np.float32)
    return {
        "good_matches": len(good),
        "median_shift_px": float(np.median(shifts)),
        "p95_shift_px": float(np.percentile(shifts, 95)),
    }

def validate_geometry(off_path, on_path, profile="lifestyle"):
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    limits = PROFILES[profile]

    off_color, off = _gray(off_path)
    on_color, on = _gray(on_path)

    if off_color.shape[:2] != on_color.shape[:2]:
        return {"pass": False, "reason": "dimension_mismatch", "profile": profile}

    edge_score = _edge_overlap(_edges(off), _edges(on))
    features = _feature_shift(off, on)

    checks = {
        "edge_structure": edge_score >= limits["min_edge_overlap"],
        "enough_matches": features["good_matches"] >= limits["min_good_matches"],
        "median_geometry": features["median_shift_px"] <= limits["max_median_shift_px"],
        "p95_geometry": features["p95_shift_px"] <= limits["max_p95_shift_px"],
    }

    return {
        "pass": all(checks.values()),
        "profile": profile,
        "same_dimensions": True,
        "edge_overlap": round(edge_score, 5),
        **features,
        "checks": checks,
        "thresholds": limits,
        "note": "Thresholds are conservative V1 defaults and must be calibrated on real OFF/ON benchmark pairs.",
    }
