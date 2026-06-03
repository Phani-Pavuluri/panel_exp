"""
F-INF-001 — Interval semantics and inference wrapper contract (Track F).

Classifies inference interval outputs so callable wrappers cannot be treated as
governed uncertainty unless band semantics pass validation. Does not mutate
interval bounds (no abs(), no silent swap of lower/upper).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Mapping, Optional, Sequence, Tuple

import numpy as np

from panel_exp.inference_result import IntervalType

# Issue codes (stable for tests / evidence).
NEGATIVE_HALF_WIDTH = "negative_half_width"
INVERTED_BOUNDS = "inverted_lower_upper_bounds"
NULL_INTERVAL_EXCLUSION_FPR = "null_interval_exclusion_fpr"
MISSING_INTERVAL_TYPE = "missing_interval_type"
MISSING_INTERVAL_UNITS = "missing_interval_units"
MISSING_ESTIMAND_BINDING = "missing_estimand_binding"
MISSING_GEOMETRY_BINDING = "missing_geometry_binding"
BLOCKED_INTERFACE = "blocked_interface"
NON_FINITE_BOUNDS = "non_finite_bounds"
NOT_CALLABLE = "not_callable"
POINT_ONLY = "point_only"

DEFAULT_NULL_FPR_CONCERNING = 0.35
DEFAULT_NULL_FPR_ACCEPTABLE = 0.15


class IntervalSemanticsClassification(str, Enum):
    """Governed readout tier for interval-like inference outputs."""

    GOVERNED_UNCERTAINTY = "governed_uncertainty"
    DIAGNOSTIC_INTERVAL_ONLY = "diagnostic_interval_only"
    CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS = "callable_unverified_interval_semantics"
    BLOCKED_INVALID_INTERVAL = "blocked_invalid_interval"
    BLOCKED_INTERFACE = "blocked_interface"


StructuralIssueCodes = frozenset(
    {
        NEGATIVE_HALF_WIDTH,
        INVERTED_BOUNDS,
        NON_FINITE_BOUNDS,
    }
)


@dataclass(frozen=True)
class IntervalReadout:
    """Minimal readout payload for interval semantics classification."""

    estimator_name: str
    inference_mode: Optional[str]
    geometry_mode: Optional[str]
    callable: bool = True
    blocked_interface_reason: Optional[str] = None
    path_interval_type: Optional[str] = None
    interval_units: Optional[str] = None
    target_estimand: Optional[str] = None
    y: Optional[np.ndarray] = None
    y_hat: Optional[np.ndarray] = None
    y_lower: Optional[np.ndarray] = None
    y_upper: Optional[np.ndarray] = None
    test_length: Optional[int] = None
    null_interval_exclusion_rate: Optional[float] = None
    point_only: bool = False


@dataclass(frozen=True)
class IntervalSemanticsIssue:
    code: str
    message: str


@dataclass(frozen=True)
class IntervalSemanticsVerdict:
    classification: IntervalSemanticsClassification
    issues: Tuple[IntervalSemanticsIssue, ...] = ()
    is_governed_uncertainty: bool = False
    is_callable: bool = False
    is_diagnostic_only: bool = False
    mean_interval_halfwidth: float = float("nan")
    null_interval_exclusion_rate: Optional[float] = None
    path_interval_type: Optional[str] = None
    policy_note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification.value,
            "issues": [{"code": i.code, "message": i.message} for i in self.issues],
            "is_governed_uncertainty": self.is_governed_uncertainty,
            "is_callable": self.is_callable,
            "is_diagnostic_only": self.is_diagnostic_only,
            "mean_interval_halfwidth": self.mean_interval_halfwidth,
            "null_interval_exclusion_rate": self.null_interval_exclusion_rate,
            "path_interval_type": self.path_interval_type,
            "policy_note": self.policy_note,
        }


# Explicit export allowlist for governed uncertainty (AUDIT-010: empty for MMM/lift).
GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST: frozenset[Tuple[str, str, str]] = frozenset()

# Policy: semantically valid intervals that remain diagnostic-only (never governed export).
DIAGNOSTIC_INTERVAL_POLICY: frozenset[Tuple[str, str]] = frozenset(
    {
        ("TBRRidge", "Kfold"),
        ("TBRRidge", "BlockResidualBootstrap"),
        ("TBRRidge", "TimeSeriesKfold"),  # even if fixed structurally — restricted
        ("AugSynthCVXPY", "UnitJackKnife"),
        ("AugSynthCVXPY", "Kfold"),
        ("AugSynthCVXPY", "Conformal"),
        ("TBR", "Kfold"),
        ("TBR", "JKP"),
        ("SyntheticControl", "UnitJackKnife"),
        ("SyntheticControl", "Placebo"),
    }
)

# Track F P2 OC dispositions (expected classification targets for regression tests).
TRACK_F_KNOWN_INTERVAL_DISPOSITIONS: dict[Tuple[str, str, str], IntervalSemanticsClassification] = {
    ("TBRRidge", "TimeSeriesKfold", "single_cell"): (
        IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS
    ),
    ("AugSynthCVXPY", "Conformal", "single_cell"): (
        IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS
    ),
    ("TBR", "JKP", "aggregate_two_series"): (
        IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS
    ),
    ("TBRRidge", "UnitJackKnife", "single_cell"): IntervalSemanticsClassification.BLOCKED_INTERFACE,
    ("TBRRidge", "Conformal", "single_cell"): IntervalSemanticsClassification.BLOCKED_INTERFACE,
    ("TBRRidge", "JKP", "single_cell"): IntervalSemanticsClassification.BLOCKED_INTERFACE,
    ("TBRRidge", "Kfold", "single_cell"): IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
    ("TBRRidge", "BlockResidualBootstrap", "single_cell"): (
        IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
    ),
    ("AugSynthCVXPY", "UnitJackKnife", "single_cell"): (
        IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
    ),
    ("AugSynthCVXPY", "Kfold", "single_cell"): IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
}


def _collapse_series(arr: Optional[np.ndarray]) -> np.ndarray:
    if arr is None:
        return np.asarray([], dtype=float)
    x = np.asarray(arr, dtype=float)
    if x.ndim == 2:
        x = np.nanmean(x, axis=1)
    return x.reshape(-1)


def post_window_band_metrics(
    readout: IntervalReadout,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Return post-window y, y_hat, lo, hi and mean half-width (signed, not abs)."""
    y = _collapse_series(readout.y)
    y_hat = _collapse_series(readout.y_hat)
    y_lo = _collapse_series(readout.y_lower)
    y_hi = _collapse_series(readout.y_upper)

    if readout.test_length is not None and readout.test_length > 0:
        sl = slice(-readout.test_length, None)
        y, y_hat, y_lo, y_hi = y[sl], y_hat[sl], y_lo[sl], y_hi[sl]

    if y_lo.size and y_hi.size:
        hw = float(np.nanmean((y_hi - y_lo) / 2.0))
    else:
        hw = float("nan")
    return y, y_hat, y_lo, y_hi, hw


def detect_negative_halfwidth(mean_halfwidth: float) -> Optional[IntervalSemanticsIssue]:
    if not np.isfinite(mean_halfwidth):
        return None
    if mean_halfwidth < 0:
        return IntervalSemanticsIssue(
            NEGATIVE_HALF_WIDTH,
            f"Mean interval half-width is negative ({mean_halfwidth:.4g}); band sign invalid.",
        )
    return None


def detect_inverted_bounds(y_lower: np.ndarray, y_upper: np.ndarray) -> Optional[IntervalSemanticsIssue]:
    if y_lower.size == 0 or y_upper.size == 0:
        return None
    n = min(y_lower.size, y_upper.size)
    lo = y_lower[-n:]
    hi = y_upper[-n:]
    mask = np.isfinite(lo) & np.isfinite(hi)
    if not np.any(mask):
        return IntervalSemanticsIssue(NON_FINITE_BOUNDS, "Interval bounds are non-finite.")
    if np.any(lo[mask] > hi[mask]):
        return IntervalSemanticsIssue(
            INVERTED_BOUNDS,
            "Lower bound exceeds upper bound on at least one post-window point.",
        )
    return None


def detect_non_finite_bounds(y_lower: np.ndarray, y_upper: np.ndarray) -> Optional[IntervalSemanticsIssue]:
    if y_lower.size == 0 and y_upper.size == 0:
        return None
    if not (np.any(np.isfinite(y_lower)) or np.any(np.isfinite(y_upper))):
        return IntervalSemanticsIssue(NON_FINITE_BOUNDS, "Interval bounds are non-finite.")
    return None


def detect_null_interval_exclusion_fpr(
    rate: Optional[float],
    *,
    concerning: float = DEFAULT_NULL_FPR_CONCERNING,
) -> Optional[IntervalSemanticsIssue]:
    if rate is None or not np.isfinite(rate):
        return None
    if rate >= concerning:
        return IntervalSemanticsIssue(
            NULL_INTERVAL_EXCLUSION_FPR,
            f"Null interval-exclusion rate {rate:.3f} >= concern threshold {concerning:.2f}.",
        )
    return None


def detect_missing_interval_type(path_interval_type: Optional[str]) -> Optional[IntervalSemanticsIssue]:
    if path_interval_type is None or str(path_interval_type).strip() == "":
        return IntervalSemanticsIssue(MISSING_INTERVAL_TYPE, "path_interval_type is missing.")
    if str(path_interval_type) in (IntervalType.UNAVAILABLE.value, "unavailable"):
        return IntervalSemanticsIssue(MISSING_INTERVAL_TYPE, "path_interval_type is unavailable.")
    return None


def detect_missing_interval_units(interval_units: Optional[str]) -> Optional[IntervalSemanticsIssue]:
    if interval_units is None or str(interval_units).strip() == "":
        return IntervalSemanticsIssue(MISSING_INTERVAL_UNITS, "interval_units binding is missing.")
    return None


def detect_missing_estimand_binding(target_estimand: Optional[str]) -> Optional[IntervalSemanticsIssue]:
    if target_estimand is None or str(target_estimand).strip() in ("", "unknown"):
        return IntervalSemanticsIssue(
            MISSING_ESTIMAND_BINDING,
            "target_estimand binding is missing or unknown.",
        )
    return None


def detect_missing_geometry_binding(geometry_mode: Optional[str]) -> Optional[IntervalSemanticsIssue]:
    if geometry_mode is None or str(geometry_mode).strip() == "":
        return IntervalSemanticsIssue(MISSING_GEOMETRY_BINDING, "geometry_mode binding is missing.")
    return None


def _combo_key(readout: IntervalReadout) -> Tuple[str, str, str]:
    return (
        readout.estimator_name,
        str(readout.inference_mode or ""),
        str(readout.geometry_mode or ""),
    )


def _policy_allows_governed_export(readout: IntervalReadout) -> bool:
    est, inf, geo = _combo_key(readout)
    return (est, inf, geo) in GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST


def _policy_diagnostic_only(readout: IntervalReadout) -> bool:
    return (readout.estimator_name, str(readout.inference_mode or "")) in DIAGNOSTIC_INTERVAL_POLICY


def classify_interval_semantics(
    readout: IntervalReadout,
    *,
    null_fpr_concerning: float = DEFAULT_NULL_FPR_CONCERNING,
    require_metadata_bindings: bool = True,
) -> IntervalSemanticsVerdict:
    """
    Classify interval semantics without mutating bounds.

    Callable inference with invalid bands must not become ``governed_uncertainty``.
    """
    issues: list[IntervalSemanticsIssue] = []

    if readout.blocked_interface_reason:
        issues.append(
            IntervalSemanticsIssue(BLOCKED_INTERFACE, readout.blocked_interface_reason)
        )
        return IntervalSemanticsVerdict(
            classification=IntervalSemanticsClassification.BLOCKED_INTERFACE,
            issues=tuple(issues),
            is_governed_uncertainty=False,
            is_callable=False,
            is_diagnostic_only=False,
            path_interval_type=readout.path_interval_type,
            policy_note="Interface blocked before interval readout.",
        )

    if not readout.callable:
        issues.append(IntervalSemanticsIssue(NOT_CALLABLE, "Inference wrapper did not complete."))
        return IntervalSemanticsVerdict(
            classification=IntervalSemanticsClassification.BLOCKED_INTERFACE,
            issues=tuple(issues),
            is_governed_uncertainty=False,
            is_callable=False,
            is_diagnostic_only=False,
            path_interval_type=readout.path_interval_type,
        )

    if readout.point_only:
        return IntervalSemanticsVerdict(
            classification=IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
            issues=(IntervalSemanticsIssue(POINT_ONLY, "Point estimate only; no interval band."),),
            is_governed_uncertainty=False,
            is_callable=True,
            is_diagnostic_only=True,
            path_interval_type=readout.path_interval_type,
            policy_note="Point-only readout is never governed uncertainty.",
        )

    y, y_hat, y_lo, y_hi, mean_hw = post_window_band_metrics(readout)

    if y_lo.size == 0 or y_hi.size == 0:
        issues.append(IntervalSemanticsIssue(MISSING_INTERVAL_TYPE, "Interval bounds absent on readout."))

    for detector in (
        lambda: detect_non_finite_bounds(y_lo, y_hi),
        lambda: detect_inverted_bounds(y_lo, y_hi),
        lambda: detect_negative_halfwidth(mean_hw),
    ):
        hit = detector()
        if hit:
            issues.append(hit)

    if require_metadata_bindings:
        for detector in (
            lambda: detect_missing_interval_type(readout.path_interval_type),
            lambda: detect_missing_interval_units(readout.interval_units),
            lambda: detect_missing_estimand_binding(readout.target_estimand),
            lambda: detect_missing_geometry_binding(readout.geometry_mode),
        ):
            hit = detector()
            if hit:
                issues.append(hit)

    fpr_issue = detect_null_interval_exclusion_fpr(
        readout.null_interval_exclusion_rate,
        concerning=null_fpr_concerning,
    )
    if fpr_issue:
        issues.append(fpr_issue)

    structural = any(i.code in StructuralIssueCodes for i in issues)
    behavioral = any(
        i.code in (NULL_INTERVAL_EXCLUSION_FPR, MISSING_INTERVAL_TYPE, MISSING_INTERVAL_UNITS,
                   MISSING_ESTIMAND_BINDING, MISSING_GEOMETRY_BINDING)
        for i in issues
    )

    if structural:
        classification = IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL
        policy_note = "Structurally invalid interval band; do not treat as uncertainty."
    elif behavioral:
        classification = IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS
        policy_note = "Callable but interval semantics unverified on metadata or null battery."
    elif _policy_allows_governed_export(readout):
        classification = IntervalSemanticsClassification.GOVERNED_UNCERTAINTY
        policy_note = "Passes semantics checks and is on governed export allowlist."
    elif _policy_diagnostic_only(readout) or issues:
        classification = IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
        policy_note = "Restricted diagnostic interval; not governed uncertainty export."
    else:
        classification = IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
        policy_note = "Default safe tier: diagnostic only unless explicitly allowlisted."

    is_governed = classification == IntervalSemanticsClassification.GOVERNED_UNCERTAINTY
    is_diagnostic = classification in (
        IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
        IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS,
        IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL,
    )

    return IntervalSemanticsVerdict(
        classification=classification,
        issues=tuple(issues),
        is_governed_uncertainty=is_governed,
        is_callable=True,
        is_diagnostic_only=is_diagnostic or not is_governed,
        mean_interval_halfwidth=mean_hw,
        null_interval_exclusion_rate=readout.null_interval_exclusion_rate,
        path_interval_type=readout.path_interval_type,
        policy_note=policy_note,
    )


def assert_not_governed_uncertainty(
    verdict: IntervalSemanticsVerdict,
    *,
    context: str = "",
) -> None:
    """Raise when a readout is incorrectly labeled or classified as governed uncertainty."""
    if verdict.is_governed_uncertainty:
        prefix = f"{context}: " if context else ""
        raise ValueError(
            f"{prefix}interval readout classified as governed_uncertainty but policy forbids it "
            f"(classification={verdict.classification.value})."
        )
    if verdict.classification == IntervalSemanticsClassification.GOVERNED_UNCERTAINTY:
        prefix = f"{context}: " if context else ""
        raise ValueError(f"{prefix}governed_uncertainty classification is not permitted.")


def expected_track_f_classification(
    estimator_name: str,
    inference_mode: str,
    geometry_mode: str,
) -> Optional[IntervalSemanticsClassification]:
    """Lookup P2-documented disposition for regression alignment."""
    return TRACK_F_KNOWN_INTERVAL_DISPOSITIONS.get(
        (estimator_name, inference_mode, geometry_mode)
    )


def classify_track_f_combo(
    readout: IntervalReadout,
    *,
    null_fpr_concerning: float = DEFAULT_NULL_FPR_CONCERNING,
    require_metadata_bindings: bool = False,
) -> IntervalSemanticsVerdict:
    """
    Classify a Track F combo readout and assert it cannot become governed uncertainty
    unless semantics pass and allowlist permits.
    """
    verdict = classify_interval_semantics(
        readout,
        null_fpr_concerning=null_fpr_concerning,
        require_metadata_bindings=require_metadata_bindings,
    )
    assert_not_governed_uncertainty(verdict, context=_combo_key(readout).__repr__())
    return verdict


__all__ = [
    "BLOCKED_INTERFACE",
    "DEFAULT_NULL_FPR_ACCEPTABLE",
    "DEFAULT_NULL_FPR_CONCERNING",
    "DIAGNOSTIC_INTERVAL_POLICY",
    "GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST",
    "INVERTED_BOUNDS",
    "MISSING_ESTIMAND_BINDING",
    "MISSING_GEOMETRY_BINDING",
    "MISSING_INTERVAL_TYPE",
    "MISSING_INTERVAL_UNITS",
    "NEGATIVE_HALF_WIDTH",
    "NULL_INTERVAL_EXCLUSION_FPR",
    "TRACK_F_KNOWN_INTERVAL_DISPOSITIONS",
    "IntervalReadout",
    "IntervalSemanticsClassification",
    "IntervalSemanticsIssue",
    "IntervalSemanticsVerdict",
    "assert_not_governed_uncertainty",
    "classify_interval_semantics",
    "classify_track_f_combo",
    "detect_inverted_bounds",
    "detect_missing_estimand_binding",
    "detect_missing_geometry_binding",
    "detect_missing_interval_type",
    "detect_missing_interval_units",
    "detect_negative_halfwidth",
    "detect_null_interval_exclusion_fpr",
    "expected_track_f_classification",
    "post_window_band_metrics",
]
