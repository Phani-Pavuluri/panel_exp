"""
Link catalog maturity ratings to measured validation evidence (additive only).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.method_metadata import (
    EstimatorMetadata,
    EstimatorMaturity,
    EstimatorMaturityEvidence,
)
from panel_exp.validation.calibration_report import CalibrationReport

_MaturityInput = Union[EstimatorMetadata, Mapping[str, Any], None]


def _safe_float(value: Any, default: float = float("nan")) -> float:
    if value is None:
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def _payload_from_output(item: Any) -> Dict[str, Any]:
    if isinstance(item, Mapping):
        return dict(item)
    if hasattr(item, "to_dict"):
        return dict(item.to_dict())
    return {}


def _payload_estimator(payload: Mapping[str, Any]) -> str:
    return str(
        payload.get("estimator")
        or payload.get("estimator_name")
        or ""
    ).strip()


def _scenario_name(payload: Mapping[str, Any]) -> str:
    return str(payload.get("scenario") or payload.get("scenario_name") or "").strip()


def _resolve_maturity_metadata(
    estimator_name: str,
    maturity_metadata: _MaturityInput,
) -> Tuple[EstimatorMaturity, bool]:
    if isinstance(maturity_metadata, EstimatorMetadata):
        return maturity_metadata.maturity, maturity_metadata.synthetic_validation
    if isinstance(maturity_metadata, Mapping):
        raw = maturity_metadata.get("maturity") or maturity_metadata.get(
            "estimator_maturity"
        )
        if isinstance(raw, EstimatorMaturity):
            maturity = raw
        elif raw is not None:
            try:
                maturity = EstimatorMaturity(str(raw))
            except ValueError:
                maturity = EstimatorMaturity.UNVALIDATED
        else:
            maturity = EstimatorMaturity.UNVALIDATED
        synth = bool(
            maturity_metadata.get("synthetic_validation")
            or maturity_metadata.get("estimator_synthetic_validation")
        )
        return maturity, synth
    try:
        from panel_exp.method_registry import get_method_registry

        meta = get_method_registry().metadata(estimator_name)
        return meta.maturity, meta.synthetic_validation
    except KeyError:
        return EstimatorMaturity.UNVALIDATED, False


def _filter_recovery_outputs(
    estimator_name: str,
    recovery_outputs: Optional[Sequence[Any]],
) -> List[Dict[str, Any]]:
    if not recovery_outputs:
        return []
    matched: List[Dict[str, Any]] = []
    for item in recovery_outputs:
        payload = _payload_from_output(item)
        est = _payload_estimator(payload)
        if est and est != estimator_name:
            continue
        matched.append(payload)
    return matched


def _mean_finite(values: Sequence[float]) -> float:
    finite = [v for v in values if v == v]
    return float(sum(finite) / len(finite)) if finite else float("nan")


def _aggregate_recovery_metrics(
    payloads: Sequence[Mapping[str, Any]],
) -> Tuple[float, float, float, float]:
    if not payloads:
        return (float("nan"),) * 4
    return (
        _mean_finite(
            [_safe_float(p.get("false_positive_rate")) for p in payloads]
        ),
        _mean_finite([_safe_float(p.get("coverage")) for p in payloads]),
        _mean_finite([_safe_float(p.get("power")) for p in payloads]),
        _mean_finite(
            [_safe_float(p.get("recovery_success_rate")) for p in payloads]
        ),
    )


def _format_metric(value: float) -> str:
    return f"{value:.2f}" if value == value else "n/a"


def _build_evidence_summary(
    *,
    estimator_name: str,
    maturity: EstimatorMaturity,
    scenarios_run: Sequence[str],
    calibration_available: bool,
    false_positive_rate: float,
    coverage_under_null: float,
    power: float,
    recovery_success_rate: float,
) -> str:
    n_scenarios = len(scenarios_run)
    if not calibration_available and n_scenarios == 0:
        return (
            f"No calibration report or recovery outputs attached for {estimator_name!r}; "
            f"maturity rating remains {maturity.value} by catalog policy."
        )
    parts: List[str] = []
    if n_scenarios:
        parts.append(
            f"Estimator has recovery outputs across {n_scenarios} scenario(s)"
        )
    if calibration_available:
        parts.append("calibration report attached")
    if n_scenarios or calibration_available:
        parts.append(
            "FPR="
            f"{_format_metric(false_positive_rate)}, "
            f"coverage={_format_metric(coverage_under_null)}, "
            f"power={_format_metric(power)}, "
            f"recovery_success={_format_metric(recovery_success_rate)}"
        )
    summary = "; ".join(parts) + "."
    return (
        summary
        + f" Catalog maturity ({maturity.value}) is unchanged by this evidence."
    )


def build_maturity_evidence(
    estimator_name: str,
    maturity_metadata: _MaturityInput = None,
    *,
    calibration_report: Optional[CalibrationReport] = None,
    recovery_outputs: Optional[Sequence[Any]] = None,
) -> EstimatorMaturityEvidence:
    """
    Build additive maturity evidence from catalog metadata and optional validation outputs.

    Does not mutate ``maturity_metadata``, ``calibration_report``, or ``recovery_outputs``.
    Does not change catalog maturity ratings.
    """
    maturity, catalog_synthetic = _resolve_maturity_metadata(
        estimator_name, maturity_metadata
    )
    matched = _filter_recovery_outputs(estimator_name, recovery_outputs)
    scenarios_run = tuple(
        sorted({_scenario_name(p) for p in matched if _scenario_name(p)})
    )

    fpr = float("nan")
    coverage = float("nan")
    power = float("nan")
    recovery_success = float("nan")
    warnings: List[str] = []

    if calibration_report is not None:
        fpr = _safe_float(calibration_report.false_positive_rate)
        coverage = _safe_float(calibration_report.coverage_under_null)
        power = _safe_float(calibration_report.power)
        recovery_success = _safe_float(calibration_report.recovery_success_rate)
        warnings.extend(list(calibration_report.warnings))

    if matched:
        rfpr, rcov, rpow, rrec = _aggregate_recovery_metrics(matched)
        if fpr != fpr and rfpr == rfpr:
            fpr = rfpr
        if coverage != coverage and rcov == rcov:
            coverage = rcov
        if power != power and rpow == rpow:
            power = rpow
        if recovery_success != recovery_success and rrec == rrec:
            recovery_success = rrec

    synthetic_validation_available = catalog_synthetic or bool(matched)
    calibration_available = calibration_report is not None

    evidence_summary = _build_evidence_summary(
        estimator_name=estimator_name,
        maturity=maturity,
        scenarios_run=scenarios_run,
        calibration_available=calibration_available,
        false_positive_rate=fpr,
        coverage_under_null=coverage,
        power=power,
        recovery_success_rate=recovery_success,
    )

    return EstimatorMaturityEvidence(
        estimator_name=estimator_name,
        maturity=maturity,
        synthetic_validation_available=synthetic_validation_available,
        scenarios_run=scenarios_run,
        calibration_available=calibration_available,
        false_positive_rate=fpr,
        coverage_under_null=coverage,
        power=power,
        recovery_success_rate=recovery_success,
        warnings=tuple(warnings),
        evidence_summary=evidence_summary,
    )


def attach_maturity_evidence(
    results_or_artifacts: Dict[str, Any],
    maturity_evidence: EstimatorMaturityEvidence,
) -> Dict[str, Any]:
    """Attach ``maturity_evidence`` dict under ``results_or_artifacts['maturity_evidence']``."""
    results_or_artifacts["maturity_evidence"] = maturity_evidence.to_dict()
    return results_or_artifacts


__all__ = [
    "attach_maturity_evidence",
    "build_maturity_evidence",
]
