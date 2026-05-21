"""
Non-blocking decision readiness assessment (advisory reporting only).

Does not block runs, change estimator outputs, or alter maturity catalog ratings.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.method_metadata import EstimatorMaturity, EstimatorMaturityEvidence
from panel_exp.validation.calibration_report import (
    MAX_FALSE_POSITIVE_RATE,
    MIN_COVERAGE_UNDER_NULL,
    CalibrationReport,
)

_CalibrationInput = Union[CalibrationReport, Mapping[str, Any], None]
_MaturityInput = Union[EstimatorMaturityEvidence, Mapping[str, Any], None]
_Unknown = "unknown"


class ReadinessStatus(str, Enum):
    """Advisory readiness labels (no automated production approval)."""

    READY_WITH_REVIEW = "ready_with_review"
    NOT_READY_INSUFFICIENT_EVIDENCE = "not_ready_insufficient_evidence"
    NOT_READY_HIGH_FPR = "not_ready_high_fpr"
    NOT_READY_LOW_COVERAGE = "not_ready_low_coverage"
    NOT_READY_NO_INTERVALS = "not_ready_no_intervals"
    NOT_READY_INTERFERENCE_UNKNOWN = "not_ready_interference_unknown"
    NOT_READY_VALIDATION_ERRORS = "not_ready_validation_errors"


_STATUS_LABELS: Dict[ReadinessStatus, str] = {
    ReadinessStatus.READY_WITH_REVIEW: "Ready with expert review",
    ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE: "Not ready — insufficient evidence",
    ReadinessStatus.NOT_READY_HIGH_FPR: "Not ready — high false positive rate",
    ReadinessStatus.NOT_READY_LOW_COVERAGE: "Not ready — low coverage under null",
    ReadinessStatus.NOT_READY_NO_INTERVALS: "Not ready — no uncertainty intervals",
    ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN: "Not ready — interference unknown",
    ReadinessStatus.NOT_READY_VALIDATION_ERRORS: "Not ready — validation errors",
}


_RECOMMENDED_ACTIONS: Dict[ReadinessStatus, Tuple[str, ...]] = {
    ReadinessStatus.READY_WITH_REVIEW: (
        "Proceed only after expert review of design, interference, and inference assumptions.",
        "Confirm calibration and recovery evidence match this dataset and estimator.",
    ),
    ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE: (
        "Use a validated estimator/inference mode or collect additional synthetic validation.",
        "Do not treat outputs as decision-ready without expert sign-off.",
    ),
    ReadinessStatus.NOT_READY_HIGH_FPR: (
        "Review null-calibration evidence; consider more replications or design changes.",
        "Expert review required before any go/no-go decision.",
    ),
    ReadinessStatus.NOT_READY_LOW_COVERAGE: (
        "Review interval calibration under null; widen inference or adjust design.",
        "Expert review required before relying on interval statements.",
    ),
    ReadinessStatus.NOT_READY_NO_INTERVALS: (
        "Attach an inference mode that provides path-level intervals, or document external uncertainty.",
        "Point-estimate-only paths are not decision-ready alone.",
    ),
    ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN: (
        "Declare interference/spillover assumptions in the design spec.",
        "Review geo overlap and spillover diagnostics before causal interpretation.",
    ),
    ReadinessStatus.NOT_READY_VALIDATION_ERRORS: (
        "Resolve blocking validation failures before interpreting results.",
        "Re-run design validation after fixing assignment or constraint issues.",
    ),
}


def _safe_float(value: Any, default: float = float("nan")) -> float:
    if value is None:
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def _as_mapping(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return dict(value.to_dict())
    return {}


def _normalize_maturity(value: Any) -> Optional[EstimatorMaturity]:
    if value is None:
        return None
    if isinstance(value, EstimatorMaturity):
        return value
    text = str(value).strip().lower()
    if not text or text == _Unknown:
        return None
    try:
        return EstimatorMaturity(text)
    except ValueError:
        return None


def _collect_validation_errors(
    validation_summary: Optional[Mapping[str, Any]],
    evidence_errors: Optional[Sequence[Any]],
) -> List[str]:
    errors: List[str] = []
    if evidence_errors:
        for item in evidence_errors:
            text = str(item).strip()
            if text:
                errors.append(text)
    if not validation_summary:
        return errors
    status = str(validation_summary.get("status", "")).upper()
    if status == "FAIL":
        errors.append(f"Design validation status: {status}")
    for key in ("blocking_failures", "errors"):
        block = validation_summary.get(key)
        if isinstance(block, (list, tuple)):
            for item in block:
                text = str(item).strip()
                if text:
                    errors.append(text)
    return errors


def _interference_assumption(
    validation_summary: Optional[Mapping[str, Any]],
    inference_metadata: Dict[str, Any],
) -> str:
    for container in (inference_metadata, validation_summary or {}):
        if not container:
            continue
        for key in ("interference_assumption", "interference"):
            if key in container and container[key] is not None:
                return str(container[key]).strip().lower()
        checks = container.get("checks")
        if isinstance(checks, (list, tuple)):
            for check in checks:
                if not isinstance(check, Mapping):
                    continue
                if check.get("metric") == "interference_assumption":
                    msg = check.get("message")
                    if msg:
                        return str(msg).strip().lower()
    return _Unknown


def _calibration_metrics(
    calibration_report: _CalibrationInput,
    maturity_evidence: _MaturityInput,
) -> Tuple[float, float]:
    fpr = float("nan")
    coverage = float("nan")
    if calibration_report is not None:
        if isinstance(calibration_report, CalibrationReport):
            fpr = _safe_float(calibration_report.false_positive_rate)
            coverage = _safe_float(calibration_report.coverage_under_null)
        else:
            cal = _as_mapping(calibration_report)
            fpr = _safe_float(cal.get("false_positive_rate"))
            coverage = _safe_float(cal.get("coverage_under_null"))
    if maturity_evidence is not None:
        me = (
            maturity_evidence
            if isinstance(maturity_evidence, Mapping)
            else _as_mapping(maturity_evidence)
        )
        if fpr != fpr:
            fpr = _safe_float(me.get("false_positive_rate"))
        if coverage != coverage:
            coverage = _safe_float(me.get("coverage_under_null"))
    return fpr, coverage


def _collect_warnings(
    calibration_report: _CalibrationInput,
    maturity_evidence: _MaturityInput,
    evidence_warnings: Optional[Sequence[Any]],
) -> Tuple[str, ...]:
    warnings: List[str] = []
    if evidence_warnings:
        warnings.extend(str(w).strip() for w in evidence_warnings if str(w).strip())
    if calibration_report is not None:
        if isinstance(calibration_report, CalibrationReport):
            warnings.extend(calibration_report.warnings)
        else:
            raw = _as_mapping(calibration_report).get("warnings") or ()
            warnings.extend(str(w) for w in raw if str(w).strip())
    if maturity_evidence is not None:
        me = (
            maturity_evidence
            if isinstance(maturity_evidence, Mapping)
            else _as_mapping(maturity_evidence)
        )
        raw = me.get("warnings") or ()
        warnings.extend(str(w) for w in raw if str(w).strip())
    return tuple(dict.fromkeys(warnings))


@dataclass(frozen=True)
class ReadinessAssessment:
    """Advisory decision-readiness summary (non-blocking)."""

    status: ReadinessStatus
    reasons: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    recommended_actions: Tuple[str, ...] = ()
    inputs_used: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["status_label"] = _STATUS_LABELS.get(self.status, self.status.value)
        return payload

    def to_markdown(self) -> str:
        lines = [
            "## Decision Readiness",
            "",
            "> **Advisory only.** This assessment does not block execution, "
            "change estimator outputs, or replace expert judgment.",
            "",
            f"- **Status:** {_STATUS_LABELS.get(self.status, self.status.value)} "
            f"(`{self.status.value}`)",
            "",
            "### Reasons",
            "",
        ]
        if self.reasons:
            for reason in self.reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- *No specific blockers recorded; expert review still required.*")
        lines.extend(["", "### Recommended actions", ""])
        if self.recommended_actions:
            for action in self.recommended_actions:
                lines.append(f"- {action}")
        else:
            lines.append("- *No additional actions recorded.*")
        if self.warnings:
            lines.extend(["", "### Related warnings", ""])
            for warning in self.warnings:
                lines.append(f"- {warning}")
        if self.inputs_used:
            lines.extend(["", "### Inputs consulted", ""])
            for key in self.inputs_used:
                lines.append(f"- `{key}`")
        return "\n".join(lines)


def build_readiness_assessment(
    *,
    inference_metadata: Optional[Mapping[str, Any]] = None,
    validation_summary: Optional[Mapping[str, Any]] = None,
    calibration_report: _CalibrationInput = None,
    maturity_evidence: _MaturityInput = None,
    evidence_warnings: Optional[Sequence[Any]] = None,
    evidence_errors: Optional[Sequence[Any]] = None,
    interference_assumption: Optional[str] = None,
) -> ReadinessAssessment:
    """
    Build an advisory readiness assessment from available evidence signals.

    Does not mutate input objects. Precedence (first match wins):

    validation errors > no intervals > insufficient evidence > high FPR >
    low coverage > interference unknown > ready with review.
    """
    meta = _as_mapping(inference_metadata)
    inputs_used: List[str] = []
    if meta:
        inputs_used.append("inference_metadata")
    if validation_summary:
        inputs_used.append("validation_summary")
    if calibration_report is not None:
        inputs_used.append("calibration_report")
    if maturity_evidence is not None:
        inputs_used.append("maturity_evidence")
    if evidence_warnings:
        inputs_used.append("evidence_warnings")
    if evidence_errors:
        inputs_used.append("evidence_errors")
    if interference_assumption is not None:
        inputs_used.append("interference_assumption")

    warnings = _collect_warnings(
        calibration_report, maturity_evidence, evidence_warnings
    )

    validation_errors = _collect_validation_errors(validation_summary, evidence_errors)
    if validation_errors:
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_VALIDATION_ERRORS,
            reasons=tuple(validation_errors),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_VALIDATION_ERRORS
            ],
            inputs_used=tuple(inputs_used),
        )

    intervals_raw = meta.get("intervals_available")
    if intervals_raw is not None and not bool(intervals_raw):
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_NO_INTERVALS,
            reasons=(
                "Path-level uncertainty intervals are not available "
                f"(interval_type={meta.get('path_interval_type') or meta.get('interval_type')!r}).",
            ),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_NO_INTERVALS
            ],
            inputs_used=tuple(inputs_used),
        )

    estimator_maturity = _normalize_maturity(meta.get("estimator_maturity"))
    inference_maturity = _normalize_maturity(meta.get("inference_mode_maturity"))
    insufficient: List[str] = []
    for label, mat in (
        ("estimator", estimator_maturity),
        ("inference mode", inference_maturity),
    ):
        if mat in (
            EstimatorMaturity.RESEARCH_ONLY,
            EstimatorMaturity.UNVALIDATED,
        ):
            insufficient.append(
                f"{label} maturity is {mat.value} (requires expert review or more validation)."
            )
    if insufficient:
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE,
            reasons=tuple(insufficient),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE
            ],
            inputs_used=tuple(inputs_used),
        )

    fpr, coverage = _calibration_metrics(calibration_report, maturity_evidence)
    if fpr == fpr and fpr > MAX_FALSE_POSITIVE_RATE:
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_HIGH_FPR,
            reasons=(
                f"False positive rate {fpr:.3f} exceeds advisory threshold "
                f"{MAX_FALSE_POSITIVE_RATE:.2f}.",
            ),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_HIGH_FPR
            ],
            inputs_used=tuple(inputs_used),
        )

    if coverage == coverage and coverage < MIN_COVERAGE_UNDER_NULL:
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_LOW_COVERAGE,
            reasons=(
                f"Coverage under null {coverage:.3f} is below advisory threshold "
                f"{MIN_COVERAGE_UNDER_NULL:.2f}.",
            ),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_LOW_COVERAGE
            ],
            inputs_used=tuple(inputs_used),
        )

    interference = (
        str(interference_assumption).strip().lower()
        if interference_assumption is not None
        else _interference_assumption(validation_summary, meta)
    )
    if interference in (_Unknown, "unknown", ""):
        return ReadinessAssessment(
            status=ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN,
            reasons=("Interference / spillover assumption is unknown or undeclared.",),
            warnings=warnings,
            recommended_actions=_RECOMMENDED_ACTIONS[
                ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN
            ],
            inputs_used=tuple(inputs_used),
        )

    return ReadinessAssessment(
        status=ReadinessStatus.READY_WITH_REVIEW,
        reasons=(
            "No advisory blockers detected from attached evidence; "
            "expert review is still required before operational decisions.",
        ),
        warnings=warnings,
        recommended_actions=_RECOMMENDED_ACTIONS[ReadinessStatus.READY_WITH_REVIEW],
        inputs_used=tuple(inputs_used),
    )


def attach_readiness_assessment(
    results_or_artifacts: Dict[str, Any],
    assessment: ReadinessAssessment,
) -> Dict[str, Any]:
    """Attach serialized readiness assessment (additive, non-blocking)."""
    results_or_artifacts["readiness_assessment"] = assessment.to_dict()
    return results_or_artifacts


__all__ = [
    "ReadinessAssessment",
    "ReadinessStatus",
    "attach_readiness_assessment",
    "build_readiness_assessment",
]
