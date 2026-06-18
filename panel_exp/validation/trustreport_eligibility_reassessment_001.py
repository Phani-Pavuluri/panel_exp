"""TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — DCM-001 reassessment after SCM-JK harness correction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from panel_exp.validation.trustreport_eligibility_001 import (
    PROVISIONAL_THRESHOLDS,
    STATUS_ELIGIBLE_CANDIDATE,
    STATUS_ELIGIBLE_WITH_RESTRICTIONS,
    STATUS_INELIGIBLE,
    STATUS_INSUFFICIENT_EVIDENCE,
    TrustReportEligibilityResult,
    TrustReportEmpiricalEvidence,
)

REASSESSMENT_VERSION = "1.0.0"
GATE_LABEL = "provisional_for_trustreport_reassessment_only"
CANONICAL_EFFECT_SCALE = "level_effect"
DCM_001_ROW = "DCM-001"

RC_CORRECTED_EVIDENCE = "TR-REASSESS-CORRECTED-EVIDENCE-USED"
RC_HISTORICAL_SUPERSEDED = "TR-REASSESS-HISTORICAL-EVIDENCE-SUPERSEDED"
RC_LEVEL_SCALE = "TR-REASSESS-LEVEL-SCALE-CONSISTENT"
RC_TYPE_I_CAVEAT = "TR-REASSESS-TYPE-I-CAVEAT"
RC_NOISY_WORLD_CAVEAT = "TR-REASSESS-NOISY-WORLD-CAVEAT"
RC_PREFIT_GATE = "TR-REASSESS-PREFIT-GATE-REQUIRED"
RC_DONOR_GATE = "TR-REASSESS-DONOR-SUPPORT-GATE-REQUIRED"
RC_TREATED_UNIT_ONLY = "TR-REASSESS-TREATED-UNIT-ONLY"
RC_POPULATION_BLOCKED = "TR-REASSESS-POPULATION-CLAIM-BLOCKED"
RC_SUPPORT_GATED = "TR-REASSESS-SUPPORT-GATED"
RC_ELIGIBLE_RESTRICTIONS = "TR-REASSESS-ELIGIBLE-WITH-RESTRICTIONS"
RC_INSUFFICIENT = "TR-REASSESS-INSUFFICIENT-EVIDENCE"
RC_INELIGIBLE = "TR-REASSESS-INELIGIBLE"
RC_AUTH_BLOCKED = "TR-REASSESS-AUTHORIZATION-STILL-BLOCKED"
RC_GEOMETRY_FAIL = "TR-REASSESS-GEOMETRY-INVALID"
RC_SCALE_AMBIGUOUS = "TR-REASSESS-SCALE-AMBIGUOUS"

NULL_WORLDS = (
    "clean_null",
    "weak_signal_null",
    "donor_stress",
    "outside_hull_or_poor_prefit",
    "post_shock_null",
)
POSITIVE_WORLDS = ("clean_positive_lift", "noisy_positive_lift")


@dataclass(frozen=True)
class TrustReportEligibilityReassessmentResult:
    prior_status: str
    reassessed_status: str
    eligible_for_promotion: bool
    trust_report_authorized: bool
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    dcm_row_id: str
    estimator_id: str
    inference_id: str
    corrected_evidence_source: str
    effect_scale: str
    null_coverage: float | None
    positive_coverage: float | None
    negative_coverage: float | None
    type_i_error: float | None
    failure_rate: float | None
    worst_world_coverage: float | None
    support_gate_status: str
    prefit_gate_status: str
    donor_gate_status: str
    semantic_class: str
    authorization_status: str
    reassessment_version: str = REASSESSMENT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _append_unique(codes: list[str], code: str) -> None:
    if code and code not in codes:
        codes.append(code)


def extract_corrected_dcm001_evidence(
    archive: Mapping[str, Any],
    *,
    historical_archive: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build DCM-001 metrics from corrected canonical SCM-JK archive only."""
    if historical_archive is not None:
        # Guard: never blend historical percent-scale metrics into canonical extraction.
        del historical_archive

    summary = archive.get("summary") or {}
    aggregate = archive.get("aggregate_metrics") or {}
    harness = archive.get("harness_correction") or {}

    if not harness.get("supersedes_canonical_rebuild_interpretation"):
        raise ValueError("archive missing harness correction supersession metadata")

    null_cov_vals = [
        _float_or_none(aggregate[w].get("coverage_level"))
        for w in NULL_WORLDS
        if w in aggregate and aggregate[w].get("coverage_level") is not None
    ]
    pos_cov_vals = [
        _float_or_none(aggregate[w].get("coverage_level"))
        for w in POSITIVE_WORLDS
        if w in aggregate and aggregate[w].get("coverage_level") is not None
    ]
    type_i_vals = [
        _float_or_none(aggregate[w].get("null_false_positive_rate"))
        for w in NULL_WORLDS
        if w in aggregate and aggregate[w].get("null_false_positive_rate") is not None
    ]

    clean_pos = aggregate.get("clean_positive_lift") or {}
    noisy_pos = aggregate.get("noisy_positive_lift") or {}
    donor_stress = aggregate.get("donor_stress") or {}

    worst_pos_cov = min(pos_cov_vals) if pos_cov_vals else None

    total = summary.get("total_runs") or 1
    failures = summary.get("total_failures") or 0

    return {
        "artifact_id": archive.get("artifact_id"),
        "evidence_source": "corrected_canonical_archive",
        "effect_scale": harness.get("canonical_effect_scale", CANONICAL_EFFECT_SCALE),
        "geometry": archive.get("geometry"),
        "null_coverage_level": _float_or_none(summary.get("null_coverage_level"))
        or (float(sum(null_cov_vals) / len(null_cov_vals)) if null_cov_vals else None),
        "positive_coverage_level": _float_or_none(summary.get("positive_coverage_level"))
        or (float(sum(pos_cov_vals) / len(pos_cov_vals)) if pos_cov_vals else None),
        "positive_coverage_fractional_percent": _float_or_none(
            summary.get("positive_coverage_fractional_percent")
        ),
        "negative_coverage_level": None,
        "type_i_error": _float_or_none(summary.get("empirical_type_i_error"))
        or (float(sum(type_i_vals) / len(type_i_vals)) if type_i_vals else None),
        "failure_rate": failures / total if total else None,
        "bias_level": _float_or_none(clean_pos.get("mean_bias_level")),
        "rmse_level": _float_or_none(clean_pos.get("rmse")),
        "interval_width": _float_or_none(clean_pos.get("mean_interval_width")),
        "clean_positive_coverage": _float_or_none(clean_pos.get("coverage_level")),
        "noisy_positive_coverage": _float_or_none(noisy_pos.get("coverage_level")),
        "worst_positive_coverage": worst_pos_cov,
        "donor_count_mean": _float_or_none(clean_pos.get("donor_count_mean")),
        "n_treated_mean": _float_or_none(clean_pos.get("n_treated_mean")),
        "n_control_mean": _float_or_none(clean_pos.get("n_control_mean")),
        "prefit_rmse_clean": _float_or_none(clean_pos.get("prefit_rmse_mean")),
        "prefit_rmse_poor_null": _float_or_none(
            (aggregate.get("outside_hull_or_poor_prefit") or {}).get("prefit_rmse_mean")
        ),
        "donor_stress_donor_count": _float_or_none(donor_stress.get("donor_count_mean")),
        "feasible_runs": summary.get("total_runs", 0) - failures,
        "total_runs": summary.get("total_runs"),
    }


def _evaluate_support_gates(metrics: Mapping[str, Any]) -> dict[str, str]:
    """Provisional support gates — characterization only."""
    donor_count = metrics.get("donor_count_mean")
    donor_stress_count = metrics.get("donor_stress_donor_count")
    min_donor = 4.0

    if donor_count is not None and donor_count < min_donor:
        donor_status = "warning_required"
    elif donor_stress_count is not None and donor_stress_count < min_donor:
        donor_status = "warning_required"
    else:
        donor_status = "pass"

    prefit_clean = metrics.get("prefit_rmse_clean")
    prefit_poor = metrics.get("prefit_rmse_poor_null")
    if prefit_poor is not None and prefit_clean is not None and prefit_poor < prefit_clean * 0.5:
        prefit_status = "warning_required"
    else:
        prefit_status = "pass"

    if donor_status == "warning_required" or prefit_status == "warning_required":
        support_status = "support_gated"
    else:
        support_status = "pass"

    return {
        "support_gate_status": support_status,
        "prefit_gate_status": prefit_status,
        "donor_gate_status": donor_status,
        "gate_label": GATE_LABEL,
    }


def reassess_trustreport_eligibility(
    *,
    prior_eligibility_result: TrustReportEligibilityResult
    | Mapping[str, Any]
    | None,
    corrected_empirical_evidence: Mapping[str, Any],
    readout_evidence: Any = None,
) -> TrustReportEligibilityReassessmentResult:
    """Reassess DCM-001 eligibility using corrected SCM-JK evidence only."""
    del readout_evidence

    if isinstance(prior_eligibility_result, TrustReportEligibilityResult):
        prior_status = prior_eligibility_result.status
    elif prior_eligibility_result:
        prior_status = str(prior_eligibility_result.get("eligibility_status") or prior_eligibility_result.get("status") or STATUS_INSUFFICIENT_EVIDENCE)
    else:
        prior_status = STATUS_INSUFFICIENT_EVIDENCE

    metrics = dict(corrected_empirical_evidence)
    codes: list[str] = []
    warnings: list[str] = []

    _append_unique(codes, RC_CORRECTED_EVIDENCE)
    _append_unique(codes, RC_HISTORICAL_SUPERSEDED)
    _append_unique(codes, RC_AUTH_BLOCKED)

    effect_scale = str(metrics.get("effect_scale") or "")
    if effect_scale != CANONICAL_EFFECT_SCALE:
        _append_unique(codes, RC_SCALE_AMBIGUOUS)
        return _build_reassessment(
            prior_status=prior_status,
            reassessed_status=STATUS_INSUFFICIENT_EVIDENCE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            gates=_evaluate_support_gates(metrics),
            semantic_class="ambiguous_scale",
        )

    _append_unique(codes, RC_LEVEL_SCALE)
    _append_unique(codes, RC_TREATED_UNIT_ONLY)
    _append_unique(codes, RC_POPULATION_BLOCKED)

    n_control = metrics.get("n_control_mean")
    n_treated = metrics.get("n_treated_mean")
    if n_control is not None and n_control < 4:
        _append_unique(codes, RC_GEOMETRY_FAIL)
        return _build_reassessment(
            prior_status=prior_status,
            reassessed_status=STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            gates=_evaluate_support_gates(metrics),
            semantic_class="invalid_geometry",
        )

    if n_treated is not None and n_treated < 1:
        _append_unique(codes, RC_GEOMETRY_FAIL)
        return _build_reassessment(
            prior_status=prior_status,
            reassessed_status=STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            gates=_evaluate_support_gates(metrics),
            semantic_class="invalid_geometry",
        )

    gates = _evaluate_support_gates(metrics)
    if gates["prefit_gate_status"] == "warning_required":
        _append_unique(codes, RC_PREFIT_GATE)
    if gates["donor_gate_status"] == "warning_required":
        _append_unique(codes, RC_DONOR_GATE)
    if gates["support_gate_status"] == "support_gated":
        _append_unique(codes, RC_SUPPORT_GATED)

    null_cov = _float_or_none(metrics.get("null_coverage_level"))
    pos_cov = _float_or_none(metrics.get("positive_coverage_level"))
    type_i = _float_or_none(metrics.get("type_i_error"))
    noisy_cov = _float_or_none(metrics.get("noisy_positive_coverage"))
    frac_pos = _float_or_none(metrics.get("positive_coverage_fractional_percent"))

    if frac_pos is not None and frac_pos < 0.2 and pos_cov is not None and pos_cov >= 0.5:
        warnings.append(
            "Historical fractional-percent positive coverage is superseded; "
            "reassessment uses level-scale coverage only."
        )

    material_caveat = False

    pos_min = PROVISIONAL_THRESHOLDS["coverage_positive_min"]
    if pos_cov is None:
        _append_unique(codes, RC_INSUFFICIENT)
        return _build_reassessment(
            prior_status=prior_status,
            reassessed_status=STATUS_INSUFFICIENT_EVIDENCE,
            codes=codes,
            warnings=warnings,
            metrics=metrics,
            gates=gates,
            semantic_class="missing_positive_coverage",
        )

    if pos_cov < pos_min:
        _append_unique(codes, RC_INSUFFICIENT)
        material_caveat = True
    elif pos_cov < 0.85:
        material_caveat = True

    if type_i is not None and type_i > PROVISIONAL_THRESHOLDS["type_i_error_clean_null_max"]:
        _append_unique(codes, RC_TYPE_I_CAVEAT)
        warnings.append(
            f"Empirical type-I error {type_i:.3f} exceeds provisional maximum "
            f"{PROVISIONAL_THRESHOLDS['type_i_error_clean_null_max']:.2f}."
        )
        material_caveat = True

    if noisy_cov is not None and noisy_cov < 0.85:
        _append_unique(codes, RC_NOISY_WORLD_CAVEAT)
        warnings.append(
            f"Noisy positive-world level coverage {noisy_cov:.3f} below 0.85; "
            "support-gated use recommended."
        )
        material_caveat = True

    if null_cov is not None:
        nominal = PROVISIONAL_THRESHOLDS["coverage_nominal"]
        if abs(null_cov - nominal) > PROVISIONAL_THRESHOLDS["coverage_deviation_max"]:
            warnings.append(f"Null-world level coverage {null_cov:.3f} deviates from nominal.")

    failure_rate = _float_or_none(metrics.get("failure_rate"))
    if failure_rate is not None and failure_rate > PROVISIONAL_THRESHOLDS["failure_rate_max"]:
        _append_unique(codes, RC_INSUFFICIENT)
        material_caveat = True

    if RC_GEOMETRY_FAIL in codes or RC_SCALE_AMBIGUOUS in codes:
        status = STATUS_INELIGIBLE
        _append_unique(codes, RC_INELIGIBLE)
    elif RC_INSUFFICIENT in codes and (pos_cov is None or pos_cov < pos_min):
        status = STATUS_INSUFFICIENT_EVIDENCE
    elif material_caveat or gates["support_gate_status"] == "support_gated":
        status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
        _append_unique(codes, RC_ELIGIBLE_RESTRICTIONS)
        warnings.append(
            "Restricted causal-interval candidacy: treated-unit level-scale effect only; "
            "support-gated; no population ATE; no TrustReport authorization."
        )
    else:
        status = STATUS_ELIGIBLE_CANDIDATE
        warnings.append(
            "Provisional promotion candidacy on corrected evidence; TrustReport authorization "
            "still blocked."
        )

    semantic_class = "restricted_causal_interval_level_scale"
    if status == STATUS_ELIGIBLE_CANDIDATE:
        semantic_class = "promotion_candidate_restricted_causal_interval"
    elif status == STATUS_INSUFFICIENT_EVIDENCE:
        semantic_class = "insufficient_evidence"
    elif status == STATUS_INELIGIBLE:
        semantic_class = "ineligible"

    return _build_reassessment(
        prior_status=prior_status,
        reassessed_status=status,
        codes=codes,
        warnings=warnings,
        metrics=metrics,
        gates=gates,
        semantic_class=semantic_class,
        eligible_for_promotion=status == STATUS_ELIGIBLE_CANDIDATE,
    )


def _build_reassessment(
    *,
    prior_status: str,
    reassessed_status: str,
    codes: list[str],
    warnings: list[str],
    metrics: Mapping[str, Any],
    gates: Mapping[str, str],
    semantic_class: str,
    eligible_for_promotion: bool = False,
) -> TrustReportEligibilityReassessmentResult:
    return TrustReportEligibilityReassessmentResult(
        prior_status=prior_status,
        reassessed_status=reassessed_status,
        eligible_for_promotion=eligible_for_promotion,
        trust_report_authorized=False,
        reason_codes=tuple(codes),
        warnings=tuple(warnings),
        dcm_row_id=DCM_001_ROW,
        estimator_id="scm",
        inference_id="unit_jackknife",
        corrected_evidence_source=str(
            metrics.get("artifact_id") or "D5-STAT-SCM-JK-001"
        ),
        effect_scale=str(metrics.get("effect_scale") or CANONICAL_EFFECT_SCALE),
        null_coverage=_float_or_none(metrics.get("null_coverage_level")),
        positive_coverage=_float_or_none(metrics.get("positive_coverage_level")),
        negative_coverage=_float_or_none(metrics.get("negative_coverage_level")),
        type_i_error=_float_or_none(metrics.get("type_i_error")),
        failure_rate=_float_or_none(metrics.get("failure_rate")),
        worst_world_coverage=_float_or_none(metrics.get("worst_positive_coverage")),
        support_gate_status=str(gates.get("support_gate_status", "unknown")),
        prefit_gate_status=str(gates.get("prefit_gate_status", "unknown")),
        donor_gate_status=str(gates.get("donor_gate_status", "unknown")),
        semantic_class=semantic_class,
        authorization_status="blocked",
    )


def corrected_empirical_evidence_for_evaluator(
    metrics: Mapping[str, Any],
) -> TrustReportEmpiricalEvidence:
    """Map corrected DCM-001 metrics to TrustReportEmpiricalEvidence (level scale)."""
    clean_level = _float_or_none(metrics.get("mean_true_effect_level"))
    return TrustReportEmpiricalEvidence(
        artifact_id=str(metrics.get("artifact_id") or "D5-STAT-SCM-JK-001"),
        evidence_source="corrected_canonical_archive",
        coverage=_float_or_none(metrics.get("null_coverage_level")),
        coverage_null=_float_or_none(metrics.get("null_coverage_level")),
        coverage_positive=_float_or_none(metrics.get("positive_coverage_level")),
        type_i_error=_float_or_none(metrics.get("type_i_error")),
        bias=_float_or_none(metrics.get("bias_level")),
        rmse=_float_or_none(metrics.get("rmse_level")),
        interval_width=_float_or_none(metrics.get("interval_width")),
        failure_rate=_float_or_none(metrics.get("failure_rate")),
        worst_world_status="noisy_positive_lift"
        if (_float_or_none(metrics.get("noisy_positive_coverage")) or 1.0) < 0.85
        else "outside_hull_or_poor_prefit",
        provenance_complete=True,
        freshness_status="valid",
        effect_scale=clean_level,
        dcm_row_id=DCM_001_ROW,
        trust_role_allowed_in_source=False,
    )
