"""
Non-blocking decision readiness assessment (advisory reporting only).

Does not block runs, change estimator outputs, or alter maturity catalog ratings.
Policy profiles (exploratory / standard / strict) configure advisory thresholds only.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.method_metadata import EstimatorMaturity, EstimatorMaturityEvidence
from panel_exp.validation.calibration_report import CalibrationReport

_CalibrationInput = Union[CalibrationReport, Mapping[str, Any], None]
_MaturityInput = Union[EstimatorMaturityEvidence, Mapping[str, Any], None]
_ProfileInput = Union["ReadinessProfile", "ReadinessPolicyConfig", None]
_Unknown = "unknown"


class ReadinessProfile(str, Enum):
    """Named readiness policy profiles (advisory thresholds only)."""

    EXPLORATORY = "exploratory"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass(frozen=True)
class ReadinessPolicyConfig:
    """Thresholds and flags for one readiness profile."""

    name: str
    max_false_positive_rate: float
    min_coverage_under_null: float
    min_power: float
    allow_unknown_interference: bool
    allow_research_only: bool
    require_intervals: bool
    minimum_recovery_success_rate: Optional[float] = None

    def thresholds_used_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "max_false_positive_rate": self.max_false_positive_rate,
            "min_coverage_under_null": self.min_coverage_under_null,
            "min_power": self.min_power,
            "allow_unknown_interference": self.allow_unknown_interference,
            "allow_research_only": self.allow_research_only,
            "require_intervals": self.require_intervals,
        }
        if self.minimum_recovery_success_rate is not None:
            payload["minimum_recovery_success_rate"] = (
                self.minimum_recovery_success_rate
            )
        return payload


EXPLORATORY_POLICY = ReadinessPolicyConfig(
    name="exploratory",
    max_false_positive_rate=0.20,
    min_coverage_under_null=0.80,
    min_power=0.60,
    allow_unknown_interference=True,
    allow_research_only=True,
    require_intervals=False,
    minimum_recovery_success_rate=None,
)

STANDARD_POLICY = ReadinessPolicyConfig(
    name="standard",
    max_false_positive_rate=0.10,
    min_coverage_under_null=0.90,
    min_power=0.80,
    allow_unknown_interference=False,
    allow_research_only=False,
    require_intervals=True,
    minimum_recovery_success_rate=None,
)

STRICT_POLICY = ReadinessPolicyConfig(
    name="strict",
    max_false_positive_rate=0.05,
    min_coverage_under_null=0.95,
    min_power=0.90,
    allow_unknown_interference=False,
    allow_research_only=False,
    require_intervals=True,
    minimum_recovery_success_rate=0.95,
)

_PROFILE_TO_CONFIG: Dict[ReadinessProfile, ReadinessPolicyConfig] = {
    ReadinessProfile.EXPLORATORY: EXPLORATORY_POLICY,
    ReadinessProfile.STANDARD: STANDARD_POLICY,
    ReadinessProfile.STRICT: STRICT_POLICY,
}


def resolve_readiness_policy(profile: _ProfileInput = None) -> ReadinessPolicyConfig:
    """Resolve a profile enum or custom config; default is STANDARD."""
    if profile is None:
        return STANDARD_POLICY
    if isinstance(profile, ReadinessPolicyConfig):
        return profile
    return _PROFILE_TO_CONFIG[profile]


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
) -> Tuple[float, float, float, float]:
    """Return (fpr, coverage_under_null, power, recovery_success_rate)."""
    fpr = float("nan")
    coverage = float("nan")
    power = float("nan")
    recovery_success = float("nan")
    if calibration_report is not None:
        if isinstance(calibration_report, CalibrationReport):
            fpr = _safe_float(calibration_report.false_positive_rate)
            coverage = _safe_float(calibration_report.coverage_under_null)
            power = _safe_float(calibration_report.power)
            recovery_success = _safe_float(calibration_report.recovery_success_rate)
        else:
            cal = _as_mapping(calibration_report)
            fpr = _safe_float(cal.get("false_positive_rate"))
            coverage = _safe_float(cal.get("coverage_under_null"))
            power = _safe_float(cal.get("power"))
            recovery_success = _safe_float(cal.get("recovery_success_rate"))
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
        if power != power:
            power = _safe_float(me.get("power"))
        if recovery_success != recovery_success:
            recovery_success = _safe_float(me.get("recovery_success_rate"))
    return fpr, coverage, power, recovery_success


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
    profile_name: str = STANDARD_POLICY.name
    thresholds_used: Tuple[Tuple[str, Any], ...] = ()

    def thresholds_used_dict(self) -> Dict[str, Any]:
        return dict(self.thresholds_used)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["status_label"] = _STATUS_LABELS.get(self.status, self.status.value)
        payload["thresholds_used"] = self.thresholds_used_dict()
        return payload

    def to_markdown(self) -> str:
        lines = [
            "## Decision Readiness",
            "",
            "> **Advisory only.** This assessment does not block execution, "
            "change estimator outputs, or replace expert judgment.",
            "",
            f"- **Profile:** {self.profile_name}",
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
        if self.thresholds_used:
            lines.extend(["", "### Thresholds (profile)", ""])
            for key, value in self.thresholds_used:
                lines.append(f"- **{key}:** {value}")
        if self.inputs_used:
            lines.extend(["", "### Inputs consulted", ""])
            for key in self.inputs_used:
                lines.append(f"- `{key}`")
        return "\n".join(lines)


def _make_assessment(
    config: ReadinessPolicyConfig,
    *,
    status: ReadinessStatus,
    reasons: Sequence[str],
    warnings: Tuple[str, ...],
    inputs_used: Tuple[str, ...],
) -> ReadinessAssessment:
    thresholds = tuple(config.thresholds_used_dict().items())
    return ReadinessAssessment(
        status=status,
        reasons=tuple(reasons),
        warnings=warnings,
        recommended_actions=_RECOMMENDED_ACTIONS[status],
        inputs_used=inputs_used,
        profile_name=config.name,
        thresholds_used=thresholds,
    )


def build_readiness_assessment(
    *,
    inference_metadata: Optional[Mapping[str, Any]] = None,
    validation_summary: Optional[Mapping[str, Any]] = None,
    calibration_report: _CalibrationInput = None,
    maturity_evidence: _MaturityInput = None,
    evidence_warnings: Optional[Sequence[Any]] = None,
    evidence_errors: Optional[Sequence[Any]] = None,
    interference_assumption: Optional[str] = None,
    profile: _ProfileInput = ReadinessProfile.STANDARD,
) -> ReadinessAssessment:
    """
    Build an advisory readiness assessment from available evidence signals.

    Does not mutate input objects. Precedence (first match wins):

    validation errors > no intervals (if required) > insufficient evidence >
    high FPR > low coverage > low power / recovery (profile) > interference unknown >
    ready with review.

    Default profile is STANDARD.
    """
    config = resolve_readiness_policy(profile)
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
    inputs_used.append(f"profile:{config.name}")

    warnings = _collect_warnings(
        calibration_report, maturity_evidence, evidence_warnings
    )
    used = tuple(inputs_used)

    validation_errors = _collect_validation_errors(validation_summary, evidence_errors)
    if validation_errors:
        return _make_assessment(
            config,
            status=ReadinessStatus.NOT_READY_VALIDATION_ERRORS,
            reasons=validation_errors,
            warnings=warnings,
            inputs_used=used,
        )

    if config.require_intervals:
        intervals_raw = meta.get("intervals_available")
        if intervals_raw is not None and not bool(intervals_raw):
            return _make_assessment(
                config,
                status=ReadinessStatus.NOT_READY_NO_INTERVALS,
                reasons=(
                    "Path-level uncertainty intervals are not available "
                    f"(interval_type={meta.get('path_interval_type') or meta.get('interval_type')!r}).",
                ),
                warnings=warnings,
                inputs_used=used,
            )

    if not config.allow_research_only:
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
            return _make_assessment(
                config,
                status=ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE,
                reasons=insufficient,
                warnings=warnings,
                inputs_used=used,
            )

    fpr, coverage, power, recovery_success = _calibration_metrics(
        calibration_report, maturity_evidence
    )
    if fpr == fpr and fpr > config.max_false_positive_rate:
        return _make_assessment(
            config,
            status=ReadinessStatus.NOT_READY_HIGH_FPR,
            reasons=(
                f"False positive rate {fpr:.3f} exceeds profile threshold "
                f"{config.max_false_positive_rate:.2f} ({config.name}).",
            ),
            warnings=warnings,
            inputs_used=used,
        )

    if coverage == coverage and coverage < config.min_coverage_under_null:
        return _make_assessment(
            config,
            status=ReadinessStatus.NOT_READY_LOW_COVERAGE,
            reasons=(
                f"Coverage under null {coverage:.3f} is below profile threshold "
                f"{config.min_coverage_under_null:.2f} ({config.name}).",
            ),
            warnings=warnings,
            inputs_used=used,
        )

    profile_insufficient: List[str] = []
    if power == power and power < config.min_power:
        profile_insufficient.append(
            f"Power {power:.3f} is below profile threshold {config.min_power:.2f}."
        )
    if (
        config.minimum_recovery_success_rate is not None
        and recovery_success == recovery_success
        and recovery_success < config.minimum_recovery_success_rate
    ):
        profile_insufficient.append(
            f"Recovery success rate {recovery_success:.3f} is below profile threshold "
            f"{config.minimum_recovery_success_rate:.2f}."
        )
    if profile_insufficient:
        return _make_assessment(
            config,
            status=ReadinessStatus.NOT_READY_INSUFFICIENT_EVIDENCE,
            reasons=profile_insufficient,
            warnings=warnings,
            inputs_used=used,
        )

    if not config.allow_unknown_interference:
        interference = (
            str(interference_assumption).strip().lower()
            if interference_assumption is not None
            else _interference_assumption(validation_summary, meta)
        )
        if interference in (_Unknown, "unknown", ""):
            return _make_assessment(
                config,
                status=ReadinessStatus.NOT_READY_INTERFERENCE_UNKNOWN,
                reasons=("Interference / spillover assumption is unknown or undeclared.",),
                warnings=warnings,
                inputs_used=used,
            )

    return _make_assessment(
        config,
        status=ReadinessStatus.READY_WITH_REVIEW,
        reasons=(
            "No advisory blockers detected from attached evidence under "
            f"profile {config.name!r}; expert review is still required before "
            "operational decisions.",
        ),
        warnings=warnings,
        inputs_used=used,
    )


def attach_readiness_assessment(
    results_or_artifacts: Dict[str, Any],
    assessment: ReadinessAssessment,
) -> Dict[str, Any]:
    """Attach serialized readiness assessment (additive, non-blocking)."""
    results_or_artifacts["readiness_assessment"] = assessment.to_dict()
    return results_or_artifacts


__all__ = [
    "EXPLORATORY_POLICY",
    "ReadinessAssessment",
    "ReadinessPolicyConfig",
    "ReadinessProfile",
    "ReadinessStatus",
    "STANDARD_POLICY",
    "STRICT_POLICY",
    "attach_readiness_assessment",
    "build_readiness_assessment",
    "resolve_readiness_policy",
]
