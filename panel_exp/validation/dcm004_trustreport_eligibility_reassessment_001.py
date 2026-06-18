"""DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — DID+bootstrap eligibility reassessment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from panel_exp.validation.trustreport_eligibility_001 import (
    PROVISIONAL_THRESHOLDS,
    STATUS_ELIGIBLE_WITH_RESTRICTIONS,
    STATUS_INELIGIBLE,
    STATUS_INSUFFICIENT_EVIDENCE,
)

REASSESSMENT_VERSION = "1.0.0"
GATE_LABEL = "provisional_for_dcm004_reassessment_only"
DCM_004_ROW = "DCM-004"
CANONICAL_EFFECT_SCALE = "cumulative_level"

RC_CORRECTED_EVIDENCE = "TR-DCM004-CORRECTED-PRODUCTION-EVIDENCE-USED"
RC_HARNESS_CORRECTED = "TR-DCM004-HARNESS-CORRECTED"
RC_CUMULATIVE_SCALE = "TR-DCM004-CUMULATIVE-LEVEL-SCALE-CONSISTENT"
RC_POSITIVE_IMPROVED = "TR-DCM004-POSITIVE-COVERAGE-IMPROVED"
RC_NULL_TYPEI_CAVEAT = "TR-DCM004-NULL-TYPEI-CAVEAT"
RC_PARALLEL_TRENDS_GATE = "TR-DCM004-PARALLEL-TRENDS-GATE-REQUIRED"
RC_COMMON_TIMING = "TR-DCM004-COMMON-TIMING-ONLY"
RC_SERIAL_CAVEAT = "TR-DCM004-SERIAL-DEPENDENCE-CAVEAT"
RC_HETEROSKEDASTIC_CAVEAT = "TR-DCM004-HETEROSKEDASTIC-CAVEAT"
RC_STRESS_EXCLUDED = "TR-DCM004-STRESS-WORLD-EXCLUDED"
RC_INSUFFICIENT_NULL = "TR-DCM004-INSUFFICIENT-NULL-CALIBRATION"
RC_ELIGIBLE_RESTRICTIONS = "TR-DCM004-ELIGIBLE-WITH-RESTRICTIONS"
RC_INELIGIBLE = "TR-DCM004-INELIGIBLE"
RC_AUTH_BLOCKED = "TR-DCM004-AUTHORIZATION-STILL-BLOCKED"

SUPPORTED_NULL_CLASSES = frozenset(
    {
        "supported_clean_parallel_common_timing",
        "supported_serial_dependence",
    }
)
UNSUPPORTED_NULL_CLASSES = frozenset(
    {
        "parallel_trends_violation",
        "staggered_timing",
        "stress_or_outlier",
        "weak_support",
    }
)

WORLD_TO_CLASS: dict[str, str] = {
    "clean_parallel_null": "supported_clean_parallel_common_timing",
    "clean_parallel_positive_lift": "supported_clean_parallel_common_timing",
    "weak_signal_null": "supported_serial_dependence",
    "noisy_positive_lift": "supported_heteroskedastic",
    "trend_violation_null": "parallel_trends_violation",
    "trend_violation_positive_lift": "parallel_trends_violation",
    "post_shock_null": "stress_or_outlier",
}

NULL_WORLDS = (
    "clean_parallel_null",
    "weak_signal_null",
    "trend_violation_null",
    "post_shock_null",
)
POSITIVE_WORLDS = (
    "clean_parallel_positive_lift",
    "noisy_positive_lift",
    "trend_violation_positive_lift",
)


@dataclass(frozen=True)
class DCM004TrustReportEligibilityReassessmentResult:
    dcm_row_id: str
    prior_status: str
    reassessed_status: str
    eligible_for_promotion: bool
    trust_report_authorized: bool
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    supported_contract: dict[str, Any]
    evidence_sources: tuple[str, ...]
    null_metrics: dict[str, Any]
    positive_metrics: dict[str, Any]
    negative_metrics: dict[str, Any]
    calibration_by_world_class: dict[str, Any]
    geometry_gate_status: str
    scale_gate_status: str
    parallel_trends_gate_status: str
    timing_gate_status: str
    dependence_gate_status: str
    semantic_class: str
    authorization_status: str
    reassessment_version: str = REASSESSMENT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _append_unique(codes: list[str], code: str) -> None:
    if code and code not in codes:
        codes.append(code)


def _mean(vals: list[float]) -> float | None:
    return float(sum(vals) / len(vals)) if vals else None


def classify_world(world_id: str) -> str:
    return WORLD_TO_CLASS.get(world_id, "unknown")


def extract_post_fix_dcm004_evidence(
    post_fix_archive: Mapping[str, Any],
    *,
    correction_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract DCM-004 metrics from post-production-fix DID canonical replay."""
    summary = post_fix_archive.get("summary") or {}
    aggregate = post_fix_archive.get("aggregate_metrics") or {}
    estimand = post_fix_archive.get("estimand_contract") or {}
    harness = post_fix_archive.get("harness_correction") or {}

    if estimand.get("truth_scale") != CANONICAL_EFFECT_SCALE:
        raise ValueError("post-fix archive missing cumulative_level estimand contract")

    runs = post_fix_archive.get("run_results") or []
    ok_runs = [r for r in runs if r.get("callable_status") == "callable_pass"]

    by_class: dict[str, list[dict[str, Any]]] = {}
    for row in ok_runs:
        cls = classify_world(str(row.get("world_id", "")))
        by_class.setdefault(cls, []).append(row)

    calibration_by_world_class: dict[str, Any] = {}
    for cls, rows in by_class.items():
        null_rows = [r for r in rows if abs(r.get("true_effect") or 0) < 1e-12]
        pos_rows = [r for r in rows if (r.get("true_effect") or 0) > 1e-12]
        neg_rows = [r for r in rows if (r.get("true_effect") or 0) < -1e-12]
        pt_in = [
            bool(r.get("interval_lower") <= r.get("point_estimate") <= r.get("interval_upper"))
            for r in rows
            if None not in (r.get("interval_lower"), r.get("interval_upper"), r.get("point_estimate"))
        ]
        null_cov = [bool(r.get("contains_truth")) for r in null_rows if r.get("contains_truth") is not None]
        type_i = [
            not bool(r.get("contains_zero"))
            for r in null_rows
            if r.get("contains_zero") is not None
        ]
        biases = [_float_or_none(r.get("bias")) for r in rows]
        biases = [b for b in biases if b is not None]
        widths = [_float_or_none(r.get("interval_width")) for r in rows]
        widths = [w for w in widths if w is not None]
        calibration_by_world_class[cls] = {
            "n_runs": len(rows),
            "n_failures": 0,
            "null_coverage": _mean([float(x) for x in null_cov]) if null_cov else None,
            "type_i_error": _mean([float(x) for x in type_i]) if type_i else None,
            "positive_coverage": _mean([float(r["contains_truth"]) for r in pos_rows if r.get("contains_truth") is not None])
            if pos_rows
            else None,
            "mean_interval_width": _mean(widths),
            "point_in_interval_rate": _mean([float(x) for x in pt_in]) if pt_in else None,
            "bias": _mean(biases),
            "rmse": (
                float(sum(b**2 for b in biases) / len(biases)) ** 0.5 if biases else None
            ),
        }

    null_type_i = [
        _float_or_none(aggregate[w].get("null_false_positive_rate"))
        for w in NULL_WORLDS
        if w in aggregate and aggregate[w].get("null_false_positive_rate") is not None
    ]
    null_cov = [
        _float_or_none(aggregate[w].get("null_coverage"))
        for w in NULL_WORLDS
        if w in aggregate and aggregate[w].get("null_coverage") is not None
    ]
    pos_cov = [
        _float_or_none(aggregate[w].get("positive_coverage"))
        for w in POSITIVE_WORLDS
        if w in aggregate and aggregate[w].get("positive_coverage") is not None
    ]

    supported_type_i = [
        _float_or_none(aggregate[w].get("null_false_positive_rate"))
        for w in NULL_WORLDS
        if w in aggregate
        and classify_world(w) in SUPPORTED_NULL_CLASSES
        and aggregate[w].get("null_false_positive_rate") is not None
    ]
    unsupported_type_i = [
        _float_or_none(aggregate[w].get("null_false_positive_rate"))
        for w in NULL_WORLDS
        if w in aggregate
        and classify_world(w) in UNSUPPORTED_NULL_CLASSES
        and aggregate[w].get("null_false_positive_rate") is not None
    ]

    clean_null = aggregate.get("clean_parallel_null") or {}
    clean_pos = aggregate.get("clean_parallel_positive_lift") or {}
    before = (correction_summary or {}).get("before_metrics") or {}
    after = (correction_summary or {}).get("after_metrics") or {}

    supported_null_cov = [
        _float_or_none(aggregate[w].get("null_coverage"))
        for w in NULL_WORLDS
        if w in aggregate
        and classify_world(w) in SUPPORTED_NULL_CLASSES
        and aggregate[w].get("null_coverage") is not None
    ]
    unsupported_null_cov = [
        _float_or_none(aggregate[w].get("null_coverage"))
        for w in NULL_WORLDS
        if w in aggregate
        and classify_world(w) in UNSUPPORTED_NULL_CLASSES
        and aggregate[w].get("null_coverage") is not None
    ]

    n_treated_vals = [b for b in [_float_or_none(r.get("n_treated")) for r in ok_runs] if b is not None]
    n_control_vals = [b for b in [_float_or_none(r.get("n_control")) for r in ok_runs] if b is not None]

    total = summary.get("total_runs") or 1
    failures = summary.get("total_failures") or 0

    return {
        "artifact_id": post_fix_archive.get("artifact_id"),
        "evidence_sources": (
            "D5-STAT-DID-BOOTSTRAP-001 (post-fix replay)",
            "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
            "DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001",
            "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001",
        ),
        "effect_scale": estimand.get("truth_scale", CANONICAL_EFFECT_SCALE),
        "geometry": post_fix_archive.get("geometry"),
        "timing_regime": summary.get("timing_regime"),
        "harness_corrected": bool(harness.get("historical_evidence_retained")),
        "null_coverage_overall": _float_or_none(summary.get("null_coverage")) or _mean(null_cov),
        "positive_coverage_overall": _float_or_none(summary.get("positive_coverage")) or _mean(pos_cov),
        "type_i_error_overall": _float_or_none(summary.get("type_i_error")) or _mean(null_type_i),
        "null_coverage_supported": _mean(supported_null_cov),
        "null_coverage_unsupported": _mean(unsupported_null_cov),
        "type_i_error_supported": _mean(supported_type_i),
        "type_i_error_unsupported": _mean(unsupported_type_i),
        "clean_parallel_null_type_i": _float_or_none(clean_null.get("null_false_positive_rate")),
        "clean_parallel_null_coverage": _float_or_none(clean_null.get("null_coverage")),
        "clean_positive_coverage": _float_or_none(clean_pos.get("positive_coverage")),
        "noisy_positive_coverage": _float_or_none(
            (aggregate.get("noisy_positive_lift") or {}).get("positive_coverage")
        ),
        "post_shock_null_type_i": _float_or_none(
            (aggregate.get("post_shock_null") or {}).get("null_false_positive_rate")
        ),
        "point_in_interval_rate": _float_or_none(after.get("point_in_interval_rate")),
        "before_positive_coverage": _float_or_none(before.get("positive_coverage")),
        "before_type_i_error": _float_or_none(before.get("type_i_error")),
        "failure_rate": failures / total if total else None,
        "bias": _float_or_none(clean_pos.get("mean_bias")),
        "rmse": _float_or_none(clean_pos.get("rmse")),
        "interval_width": _float_or_none(clean_pos.get("mean_interval_width")),
        "n_treated_mean": _mean(n_treated_vals),
        "n_control_mean": _mean(n_control_vals),
        "calibration_by_world_class": calibration_by_world_class,
        "world_classification": {w: classify_world(w) for w in aggregate},
        "total_runs": total,
        "feasible_runs": total - failures,
    }


def _supported_contract() -> dict[str, Any]:
    return {
        "label": GATE_LABEL,
        "timing": {
            "regime": "common_simultaneous_adoption",
            "staggered_pooled_blocked": True,
        },
        "geometry": {
            "unit_panel_single_cell": True,
            "min_treated": 1,
            "min_control": 4,
            "explicit_test_0_control": True,
            "no_overlap": True,
        },
        "estimand": {
            "id": "cumulative_att_level",
            "truth_scale": CANONICAL_EFFECT_SCALE,
            "point_scale": CANONICAL_EFFECT_SCALE,
            "interval_scale": CANONICAL_EFFECT_SCALE,
        },
        "identification": {
            "parallel_trends_required": True,
            "pretrend_diagnostic_required": True,
            "allow_pretrend_violation_characterization_only": False,
        },
        "inference": {
            "method": "centered_deviation_percentile_block_bootstrap",
            "min_bootstrap_replicates": 30,
            "block_resampling": True,
        },
        "excluded_regimes": [
            "parallel_trends_violation",
            "stress_or_outlier",
            "staggered_timing",
        ],
        "semantic": {
            "readout_class": "restricted_causal_interval",
            "estimand": "cumulative_att_level",
            "population_ate_blocked": True,
            "staggered_pooled_blocked": True,
            "null_monitor_relabel_blocked": True,
        },
    }


def reassess_dcm004_trustreport_eligibility(
    *,
    prior_eligibility_result: Mapping[str, Any] | None,
    corrected_empirical_evidence: Mapping[str, Any],
) -> DCM004TrustReportEligibilityReassessmentResult:
    """Reassess DCM-004 only using post-production-fix DID evidence."""
    prior_status = str(
        (prior_eligibility_result or {}).get("eligibility_status")
        or STATUS_INSUFFICIENT_EVIDENCE
    )
    metrics = dict(corrected_empirical_evidence)
    codes: list[str] = []
    warnings: list[str] = []

    _append_unique(codes, RC_CORRECTED_EVIDENCE)
    _append_unique(codes, RC_AUTH_BLOCKED)
    if metrics.get("harness_corrected"):
        _append_unique(codes, RC_HARNESS_CORRECTED)

    contract = _supported_contract()
    evidence_sources = tuple(metrics.get("evidence_sources") or ())

    scale_status = "pass"
    if metrics.get("effect_scale") != CANONICAL_EFFECT_SCALE:
        scale_status = "fail"
        _append_unique(codes, RC_INELIGIBLE)
        return _finalize(
            prior_status=prior_status,
            status=STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            contract=contract,
            evidence_sources=evidence_sources,
            scale_status=scale_status,
            geometry_status="unknown",
            timing_status="unknown",
            pretrend_status="unknown",
            dependence_status="unknown",
            semantic_class="scale_mismatch",
        )

    _append_unique(codes, RC_CUMULATIVE_SCALE)
    _append_unique(codes, RC_COMMON_TIMING)

    geometry_status = "pass"
    n_control = _float_or_none(metrics.get("n_control_mean"))
    n_treated = _float_or_none(metrics.get("n_treated_mean"))
    if n_control is not None and n_control < 4:
        geometry_status = "fail"
    if n_treated is not None and n_treated < 1:
        geometry_status = "fail"
    if geometry_status == "fail":
        _append_unique(codes, RC_INELIGIBLE)
        return _finalize(
            prior_status=prior_status,
            status=STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            contract=contract,
            evidence_sources=evidence_sources,
            scale_status=scale_status,
            geometry_status=geometry_status,
            timing_status="pass",
            pretrend_status="warning_required",
            dependence_status="pass",
            semantic_class="invalid_geometry",
        )

    timing_status = "pass" if metrics.get("timing_regime") == "common_simultaneous_adoption" else "fail"
    if timing_status != "pass":
        _append_unique(codes, RC_INELIGIBLE)

    pretrend_status = "warning_required"
    _append_unique(codes, RC_PARALLEL_TRENDS_GATE)
    warnings.append(
        "Parallel-trends diagnostic required; pretrend-violation worlds are characterization-only."
    )

    dependence_status = "warning_required"
    _append_unique(codes, RC_SERIAL_CAVEAT)
    noisy_cov = _float_or_none(metrics.get("noisy_positive_coverage"))
    if noisy_cov is not None and noisy_cov < 0.85:
        _append_unique(codes, RC_HETEROSKEDASTIC_CAVEAT)
        warnings.append(f"Noisy positive-world coverage {noisy_cov:.3f}; heteroskedastic caveat.")

    post_shock_type_i = _float_or_none(metrics.get("post_shock_null_type_i"))
    if post_shock_type_i is not None and post_shock_type_i > 0.5:
        _append_unique(codes, RC_STRESS_EXCLUDED)
        warnings.append(
            "post_shock_null shows elevated null rejection; stress worlds excluded from supported contract."
        )

    pos_cov = _float_or_none(metrics.get("positive_coverage_overall"))
    clean_pos_cov = _float_or_none(metrics.get("clean_positive_coverage"))
    before_pos = _float_or_none(metrics.get("before_positive_coverage"))
    type_i_supported = _float_or_none(metrics.get("type_i_error_supported"))
    type_i_overall = _float_or_none(metrics.get("type_i_error_overall"))
    type_i_unsupported = _float_or_none(metrics.get("type_i_error_unsupported"))
    clean_null_type_i = _float_or_none(metrics.get("clean_parallel_null_type_i"))

    if before_pos is not None and pos_cov is not None and pos_cov >= 0.5 and before_pos < 0.25:
        _append_unique(codes, RC_POSITIVE_IMPROVED)

    material_caveat = False
    pos_min = PROVISIONAL_THRESHOLDS["coverage_positive_min"]

    if pos_cov is None or clean_pos_cov is None:
        _append_unique(codes, RC_INSUFFICIENT_NULL)
        return _finalize(
            prior_status=prior_status,
            status=STATUS_INSUFFICIENT_EVIDENCE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            contract=contract,
            evidence_sources=evidence_sources,
            scale_status=scale_status,
            geometry_status=geometry_status,
            timing_status=timing_status,
            pretrend_status=pretrend_status,
            dependence_status=dependence_status,
            semantic_class="missing_positive_coverage",
        )

    if pos_cov < pos_min:
        _append_unique(codes, RC_INSUFFICIENT_NULL)
        return _finalize(
            prior_status=prior_status,
            status=STATUS_INSUFFICIENT_EVIDENCE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            contract=contract,
            evidence_sources=evidence_sources,
            scale_status=scale_status,
            geometry_status=geometry_status,
            timing_status=timing_status,
            pretrend_status=pretrend_status,
            dependence_status=dependence_status,
            semantic_class="low_positive_coverage",
        )

    type_i_max = PROVISIONAL_THRESHOLDS["type_i_error_clean_null_max"]
    if type_i_supported is not None and type_i_supported > type_i_max:
        _append_unique(codes, RC_NULL_TYPEI_CAVEAT)
        warnings.append(
            f"Supported-world null type-I {type_i_supported:.3f} exceeds provisional max {type_i_max:.2f}."
        )
        material_caveat = True

    if clean_null_type_i is not None and clean_null_type_i > type_i_max:
        material_caveat = True

    if type_i_overall is not None and type_i_unsupported is not None:
        if type_i_overall > 0.25 and type_i_supported is not None and type_i_supported <= 0.20:
            warnings.append(
                "Aggregate null type-I elevation concentrated in unsupported stress/violation worlds."
            )

    if type_i_supported is not None and type_i_supported > 0.25:
        _append_unique(codes, RC_INSUFFICIENT_NULL)
        return _finalize(
            prior_status=prior_status,
            status=STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            contract=contract,
            evidence_sources=evidence_sources,
            scale_status=scale_status,
            geometry_status=geometry_status,
            timing_status=timing_status,
            pretrend_status=pretrend_status,
            dependence_status=dependence_status,
            semantic_class="supported_null_calibration_failure",
        )

    if material_caveat or dependence_status == "warning_required":
        _append_unique(codes, RC_ELIGIBLE_RESTRICTIONS)
        status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
        warnings.append(
            "Restricted causal-interval candidacy: cumulative level ATT, common timing, "
            "parallel-trends gate, stress worlds excluded."
        )
    elif clean_pos_cov is not None and clean_pos_cov >= 0.85:
        _append_unique(codes, RC_ELIGIBLE_RESTRICTIONS)
        status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
    else:
        _append_unique(codes, RC_INSUFFICIENT_NULL)
        status = STATUS_INSUFFICIENT_EVIDENCE

    return _finalize(
        prior_status=prior_status,
        status=status,
        codes=codes,
        warnings=warnings,
        metrics=metrics,
        contract=contract,
        evidence_sources=evidence_sources,
        scale_status=scale_status,
        geometry_status=geometry_status,
        timing_status=timing_status,
        pretrend_status=pretrend_status,
        dependence_status=dependence_status,
        semantic_class="restricted_causal_interval",
    )


def _finalize(
    *,
    prior_status: str,
    status: str,
    codes: list[str],
    warnings: list[str],
    metrics: Mapping[str, Any],
    contract: dict[str, Any],
    evidence_sources: tuple[str, ...],
    scale_status: str,
    geometry_status: str,
    timing_status: str,
    pretrend_status: str,
    dependence_status: str,
    semantic_class: str,
) -> DCM004TrustReportEligibilityReassessmentResult:
    return DCM004TrustReportEligibilityReassessmentResult(
        dcm_row_id=DCM_004_ROW,
        prior_status=prior_status,
        reassessed_status=status,
        eligible_for_promotion=False,
        trust_report_authorized=False,
        reason_codes=tuple(codes),
        warnings=tuple(warnings),
        supported_contract=contract,
        evidence_sources=evidence_sources,
        null_metrics={
            "overall": {
                "null_coverage": metrics.get("null_coverage_overall"),
                "type_i_error": metrics.get("type_i_error_overall"),
            },
            "supported": {
                "null_coverage": metrics.get("null_coverage_supported"),
                "type_i_error": metrics.get("type_i_error_supported"),
            },
            "unsupported": {
                "null_coverage": metrics.get("null_coverage_unsupported"),
                "type_i_error": metrics.get("type_i_error_unsupported"),
            },
            "clean_parallel_null": {
                "null_coverage": metrics.get("clean_parallel_null_coverage"),
                "type_i_error": metrics.get("clean_parallel_null_type_i"),
            },
        },
        positive_metrics={
            "overall_positive_coverage": metrics.get("positive_coverage_overall"),
            "clean_positive_coverage": metrics.get("clean_positive_coverage"),
            "noisy_positive_coverage": metrics.get("noisy_positive_coverage"),
            "before_positive_coverage": metrics.get("before_positive_coverage"),
            "point_in_interval_rate": metrics.get("point_in_interval_rate"),
        },
        negative_metrics={"negative_coverage": None},
        calibration_by_world_class=dict(metrics.get("calibration_by_world_class") or {}),
        geometry_gate_status=geometry_status,
        scale_gate_status=scale_status,
        parallel_trends_gate_status=pretrend_status,
        timing_gate_status=timing_status,
        dependence_gate_status=dependence_status,
        semantic_class=semantic_class,
        authorization_status="blocked",
    )

