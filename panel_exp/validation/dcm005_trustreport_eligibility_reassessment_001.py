"""DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — TBRRidge path reassessment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

REASSESSMENT_VERSION = "1.0.0"
DCM_005_ROW = "DCM-005"
GATE_LABEL = "provisional_for_dcm005_reassessment_only"

INV_BRB = "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"
INV_KFOLD = "INV-TBRRIDGE-KFOLD-NULL-FPR-001"
INV_PLACEBO = "INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001"

REMEDIATION_ARTIFACT_BRB = "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001"

RC_BRB_CENTERING = "TR-DCM005-BRB-CENTERING-CORRECTED"
RC_BRB_VARIANCE = "TR-DCM005-BRB-VARIANCE-CALIBRATION-FAILED"
RC_BRB_TYPEI = "TR-DCM005-BRB-TYPEI-UNACCEPTABLE"
RC_BRB_CAUSAL_BLOCKED = "TR-DCM005-BRB-CAUSAL-INTERVAL-BLOCKED"
RC_KFOLD_CV = "TR-DCM005-KFOLD-CV-STABILITY-NOT-CAUSAL"
RC_KFOLD_SIGN = "TR-DCM005-KFOLD-SIGN-FAILURE"
RC_KFOLD_DIAG = "TR-DCM005-KFOLD-DIAGNOSTIC-ONLY"
RC_PLACEBO_SINGLE = "TR-DCM005-PLACEBO-SINGLE-TREATED-ONLY"
RC_PLACEBO_MIN_CTRL = "TR-DCM005-PLACEBO-MIN-CONTROLS"
RC_PLACEBO_NULL = "TR-DCM005-PLACEBO-NULL-MONITOR-ONLY"
RC_PLACEBO_RELABEL = "TR-DCM005-PLACEBO-CAUSAL-RELABEL-BLOCKED"
RC_PATH_SPECIFIC = "TR-DCM005-PATH-SPECIFIC-DECISIONS"
RC_NO_PROMOTION = "TR-DCM005-NO-PROMOTION"
RC_AUTH_BLOCKED = "TR-DCM005-AUTHORIZATION-STILL-BLOCKED"

REQUIRED_EVIDENCE_ARTIFACTS: dict[str, str] = {
    "brb_characterization": "D5-TRUST-TBRRIDGE-BRB-001",
    "brb_correction": "TBRRIDGE-BRB-INTERVAL-CORRECTION-001",
    "kfold": "D5-TRUST-TBRRIDGE-KFOLD-001",
    "placebo": "D5-TRUST-TBRRIDGE-PLACEBO-001",
}

TYPE_I_MAX_ACCEPTABLE = 0.20
NULL_COVERAGE_MIN = 0.80
VARIANCE_RATIO_MAX = 3.0


@dataclass(frozen=True)
class DCM005PathDecision:
    path_id: str
    estimator_id: str
    inference_id: str
    statistical_status: str
    semantic_class: str
    trustreport_eligibility_status: str
    promotion_candidate: bool
    trust_report_authorized: bool
    supported_roles: tuple[str, ...]
    blocked_roles: tuple[str, ...]
    restrictions: tuple[str, ...]
    reason_codes: tuple[str, ...]
    investigation_id: str
    investigation_disposition: str
    production_role: str = "blocked"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DCM005TrustReportEligibilityReassessmentResult:
    dcm_row_id: str
    prior_status: str
    aggregate_status: str
    eligible_for_promotion: bool
    trust_report_authorized: bool
    path_decisions: tuple[DCM005PathDecision, ...]
    investigation_handoff: dict[str, Any]
    evidence_sources: tuple[str, ...]
    authorization_status: str
    reassessment_version: str = REASSESSMENT_VERSION

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["path_decisions"] = [p.to_dict() for p in self.path_decisions]
        return d


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


def _validate_summary(summary: Mapping[str, Any], expected_id: str) -> None:
    if summary.get("artifact_id") != expected_id:
        raise ValueError(f"artifact_id mismatch: expected {expected_id}, got {summary.get('artifact_id')}")
    auth = summary.get("authorization_summary") or {}
    if auth.get("trust_report_authorized") is True or auth.get("trust_report_ready") is True:
        raise ValueError(f"{expected_id} unexpectedly authorizes TrustReport")


def load_dcm005_evidence(
    *,
    brb_summary: Mapping[str, Any],
    brb_correction_summary: Mapping[str, Any],
    kfold_summary: Mapping[str, Any],
    placebo_summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Load and validate committed DCM-005 path evidence."""
    _validate_summary(brb_summary, REQUIRED_EVIDENCE_ARTIFACTS["brb_characterization"])
    _validate_summary(brb_correction_summary, REQUIRED_EVIDENCE_ARTIFACTS["brb_correction"])
    _validate_summary(kfold_summary, REQUIRED_EVIDENCE_ARTIFACTS["kfold"])
    _validate_summary(placebo_summary, REQUIRED_EVIDENCE_ARTIFACTS["placebo"])

    after = brb_correction_summary.get("after_metrics") or {}
    before_gap = _float_or_none(
        (brb_correction_summary.get("original_defect") or {}).get("bootstrap_center_gap_before")
    )
    center_gap = _float_or_none(after.get("bootstrap_center_minus_point"))

    return {
        "brb": {
            "centering_corrected": center_gap is not None and abs(center_gap) < 1.0,
            "bootstrap_center_gap_before": before_gap,
            "bootstrap_center_gap_after": center_gap,
            "null_coverage": _float_or_none(after.get("null_coverage")),
            "type_i_error": _float_or_none(after.get("type_i_error")),
            "positive_coverage": _float_or_none(after.get("positive_coverage")),
            "negative_coverage": _float_or_none(after.get("negative_coverage")),
            "variance_ratio": _float_or_none(after.get("mean_variance_ratio")),
            "verdict": brb_correction_summary.get("verdict"),
        },
        "kfold": {
            "verdict": kfold_summary.get("verdict"),
            "sign_accuracy_positive": _float_or_none(
                (kfold_summary.get("point_estimate_results") or {}).get("sign_accuracy_positive")
            ),
            "sign_accuracy_overall": _float_or_none(kfold_summary.get("sign_accuracy")),
            "mean_abs_null_point_estimate": _float_or_none(
                (kfold_summary.get("production_defect_assessment") or {}).get(
                    "mean_abs_null_point_estimate"
                )
            ),
            "null_interval_coverage": _float_or_none(
                (kfold_summary.get("production_defect_assessment") or {}).get("null_interval_coverage")
            ),
            "leakage_flagged": (kfold_summary.get("leakage_diagnostics") or {}).get(
                "runs_with_leakage_flag", 0
            )
            > 0,
            "production_decision": (kfold_summary.get("production_defect_assessment") or {}).get(
                "decision"
            ),
            "semantic": kfold_summary.get("semantic_classification") or {},
        },
        "placebo": {
            "verdict": placebo_summary.get("verdict"),
            "type_i_null": _float_or_none(
                (placebo_summary.get("production_defect_assessment") or {}).get("type_i_null")
            ),
            "power_positive": _float_or_none(
                (placebo_summary.get("production_defect_assessment") or {}).get("power_positive")
            ),
            "single_treated_required": True,
            "min_controls": (placebo_summary.get("config") or {}).get("min_controls_production", 5),
            "failure_reasons": (placebo_summary.get("failure_summary") or {}).get("failure_reasons", []),
            "semantic": placebo_summary.get("semantic_classification") or {},
            "production_decision": (placebo_summary.get("production_defect_assessment") or {}).get(
                "decision"
            ),
        },
        "evidence_sources": (
            REQUIRED_EVIDENCE_ARTIFACTS["brb_characterization"],
            REQUIRED_EVIDENCE_ARTIFACTS["brb_correction"],
            REQUIRED_EVIDENCE_ARTIFACTS["kfold"],
            REQUIRED_EVIDENCE_ARTIFACTS["placebo"],
        ),
    }


def _decide_brb_path(evidence: Mapping[str, Any]) -> DCM005PathDecision:
    brb = dict(evidence.get("brb") or {})
    codes: list[str] = []
    restrictions: list[str] = []

    _append_unique(codes, RC_AUTH_BLOCKED)
    if brb.get("centering_corrected"):
        _append_unique(codes, RC_BRB_CENTERING)
        restrictions.append("centering_corrected_post_interval_correction")

    type_i = _float_or_none(brb.get("type_i_error"))
    null_cov = _float_or_none(brb.get("null_coverage"))
    var_ratio = _float_or_none(brb.get("variance_ratio"))

    variance_failed = (
        (type_i is not None and type_i > TYPE_I_MAX_ACCEPTABLE)
        or (null_cov is not None and null_cov < NULL_COVERAGE_MIN)
        or (var_ratio is not None and var_ratio > VARIANCE_RATIO_MAX)
    )

    if variance_failed:
        _append_unique(codes, RC_BRB_VARIANCE)
        _append_unique(codes, RC_BRB_TYPEI)
        _append_unique(codes, RC_BRB_CAUSAL_BLOCKED)

    statistical_status = "DEFERRED_FOR_REMEDIATION" if variance_failed else "INSUFFICIENT_EVIDENCE"
    semantic_class = "restricted_causal_interval_blocked"
    eligibility = "INELIGIBLE_FOR_CAUSAL_INTERVAL"
    disposition = "REMEDIATE"
    production_role = "blocked_pending_remediation"

    restrictions.extend(
        [
            "causal_interval_blocked_until_variance_remediation",
            "null_calibration_unacceptable",
            f"remediation_artifact:{REMEDIATION_ARTIFACT_BRB}",
        ]
    )

    return DCM005PathDecision(
        path_id="DCM-005-BRB",
        estimator_id="tbrridge",
        inference_id="brb",
        statistical_status=statistical_status,
        semantic_class=semantic_class,
        trustreport_eligibility_status=eligibility,
        promotion_candidate=False,
        trust_report_authorized=False,
        supported_roles=(),
        blocked_roles=(
            "trust_report",
            "calibration_signal",
            "production",
            "causal_interval",
        ),
        restrictions=tuple(restrictions),
        reason_codes=tuple(codes),
        investigation_id=INV_BRB,
        investigation_disposition=disposition,
        production_role=production_role,
    )


def _decide_kfold_path(evidence: Mapping[str, Any]) -> DCM005PathDecision:
    kf = dict(evidence.get("kfold") or {})
    codes: list[str] = [RC_AUTH_BLOCKED, RC_KFOLD_CV, RC_KFOLD_DIAG]
    sign_pos = _float_or_none(kf.get("sign_accuracy_positive"))
    if sign_pos is not None and sign_pos < 0.10:
        codes.append(RC_KFOLD_SIGN)

    restrictions = (
        "cross_validation_dispersion_not_causal_att_uncertainty",
        "directional_diagnostic_and_model_selection_only",
        "no_trustreport_promotion",
    )

    return DCM005PathDecision(
        path_id="DCM-005-KFOLD",
        estimator_id="tbrridge",
        inference_id="kfold",
        statistical_status="INELIGIBLE_FOR_CAUSAL_INTERVAL",
        semantic_class="DIAGNOSTIC_ONLY",
        trustreport_eligibility_status="DIAGNOSTIC_ONLY",
        promotion_candidate=False,
        trust_report_authorized=False,
        supported_roles=("directional_diagnostic", "model_selection_diagnostic"),
        blocked_roles=("trust_report", "calibration_signal", "production", "causal_interval"),
        restrictions=restrictions,
        reason_codes=tuple(dict.fromkeys(codes)),
        investigation_id=INV_KFOLD,
        investigation_disposition="DIAGNOSTIC_ONLY",
        production_role="diagnostic_only",
    )


def _decide_placebo_path(evidence: Mapping[str, Any]) -> DCM005PathDecision:
    pl = dict(evidence.get("placebo") or {})
    codes = [RC_AUTH_BLOCKED, RC_PLACEBO_NULL, RC_PLACEBO_RELABEL, RC_PLACEBO_SINGLE, RC_PLACEBO_MIN_CTRL]

    restrictions = (
        "single_treated_unit_only",
        "minimum_five_control_units",
        "exchangeability_caveat_under_serial_dependence",
        "null_monitor_and_falsification_only",
        "no_causal_interval_relabeling",
    )

    return DCM005PathDecision(
        path_id="DCM-005-PLACEBO",
        estimator_id="tbrridge",
        inference_id="placebo",
        statistical_status="NULL_MONITOR_ACCEPTABLE",
        semantic_class="NULL_MONITOR_ONLY",
        trustreport_eligibility_status="NULL_MONITOR_ONLY",
        promotion_candidate=False,
        trust_report_authorized=False,
        supported_roles=("null_monitor", "falsification_diagnostic"),
        blocked_roles=("trust_report", "calibration_signal", "production", "causal_interval"),
        restrictions=restrictions,
        reason_codes=tuple(codes),
        investigation_id=INV_PLACEBO,
        investigation_disposition="NULL_MONITOR_ONLY",
        production_role="null_monitor_restricted",
    )


def _aggregate_status(paths: tuple[DCM005PathDecision, ...]) -> str:
    statuses = {p.trustreport_eligibility_status for p in paths}
    if len(statuses) > 1:
        return "MIXED_WITH_TERMINAL_PATH_DECISIONS"
    if all(s == "DIAGNOSTIC_ONLY" for s in statuses):
        return "DIAGNOSTIC_ONLY"
    if all("INELIGIBLE" in s for s in statuses):
        return "INELIGIBLE_FOR_CAUSAL_INTERVAL"
    return "PATH_SPECIFIC_RESTRICTIONS"


def _build_investigation_handoff(paths: tuple[DCM005PathDecision, ...]) -> dict[str, Any]:
    terminal_ids: list[str] = []
    resolved: list[str] = []
    follow_up: list[str] = []

    for path in paths:
        if path.investigation_id == INV_BRB and path.investigation_disposition == "REMEDIATE":
            follow_up.append(INV_BRB)
        elif path.investigation_disposition in {"DIAGNOSTIC_ONLY", "NULL_MONITOR_ONLY"}:
            terminal_ids.append(path.investigation_id)
            resolved.append(path.investigation_id)

    return {
        "follow_up_issues": follow_up,
        "resolved_issues": resolved,
        "terminal_dispositions": terminal_ids,
        "next_artifact": "D5-TRUST-MULTICELL-PERCELL-INFERENCE-001",
    }


def reassess_dcm005_trustreport_eligibility(
    *,
    prior_eligibility_result: Mapping[str, Any] | None,
    path_evidence: Mapping[str, Any],
    registry_investigations: Mapping[str, Mapping[str, Any]] | None = None,
) -> DCM005TrustReportEligibilityReassessmentResult:
    """Reassess DCM-005 TBRRidge paths using committed trust characterization evidence."""
    prior_status = str(
        (prior_eligibility_result or {}).get("eligibility_status") or "INSUFFICIENT_EVIDENCE"
    )

    required_inv = {INV_BRB, INV_KFOLD, INV_PLACEBO}
    if registry_investigations is not None:
        missing = required_inv - set(registry_investigations)
        if missing:
            raise ValueError(f"registry missing required investigations: {sorted(missing)}")

    brb = _decide_brb_path(path_evidence)
    kfold = _decide_kfold_path(path_evidence)
    placebo = _decide_placebo_path(path_evidence)
    paths = (brb, kfold, placebo)

    if len({p.path_id for p in paths}) != 3:
        raise ValueError("path decisions incomplete")

    aggregate = _aggregate_status(paths)
    handoff = _build_investigation_handoff(paths)

    global_codes = [RC_PATH_SPECIFIC, RC_NO_PROMOTION, RC_AUTH_BLOCKED]

    return DCM005TrustReportEligibilityReassessmentResult(
        dcm_row_id=DCM_005_ROW,
        prior_status=prior_status,
        aggregate_status=aggregate,
        eligible_for_promotion=False,
        trust_report_authorized=False,
        path_decisions=paths,
        investigation_handoff=handoff,
        evidence_sources=tuple(path_evidence.get("evidence_sources") or ()),
        authorization_status="blocked",
        reassessment_version=REASSESSMENT_VERSION,
    )
