"""Tests for STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from panel_exp.validation.method_suitability_runtime_001 import (
    MethodSuitabilityConfig,
    evaluate_method_suitability,
)
from panel_exp.validation.production_catalog_blocklist_001 import (
    BLOCKER_MISSING_REQUIRED_EVIDENCE,
    BLOCKER_MISSING_THRESHOLDS,
    BLOCKER_STATISTICAL_PROMOTION_THRESHOLD_FAILED,
    evaluate_production_catalog_status,
)
from panel_exp.validation.readout_plan_runtime_001 import (
    ReadoutPlanRuntimeConfig,
    build_readout_plan,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    FAILURE_MISSING_REQUIRED_EVIDENCE,
    FAILURE_THRESHOLD_FAILED_COVERAGE,
    FAILURE_THRESHOLD_FAILED_DIRECTIONAL_FALSE_SIGNAL,
    FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE,
    FAILURE_THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH,
    FAILURE_THRESHOLD_FAILED_TYPE_I_ERROR,
    MATURITY_PRODUCTION_CANDIDATE,
    MATURITY_PRODUCTION_SAFE,
    MATURITY_RESTRICTED_EXPERT_REVIEW,
    STATISTICAL_PROMOTION_BLOCKED,
    STATISTICAL_PROMOTION_FAILED,
    STATISTICAL_PROMOTION_INCONCLUSIVE,
    STATISTICAL_PROMOTION_PASSED,
    STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS,
    StatisticalPromotionThresholdPolicy,
    StatisticalPromotionThresholdReport,
    check_statistical_thresholds,
    evaluate_promotion_thresholds,
    evaluate_statistical_promotion_thresholds,
    explain_threshold_failures,
    get_default_statistical_promotion_policy,
    is_statistically_promotable,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001_summary.json"

_AUTH_FALSE_KEYS = (
    "methods_unblocked",
    "production_catalog_unblocked",
    "production_safe_method_promoted",
    "claim_authorization_runtime_implemented",
    "claim_authorized",
    "claim_authorized_with_restrictions",
    "authorized_claim_text_generated",
    "trusted_readout_handoff_generated",
    "production_readout_authorized",
    "causal_claim_authorized",
    "incremental_lift_claim_authorized",
    "roi_claim_authorized",
    "production_authorization_granted",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "mmm_runtime_calls_implemented",
    "mmm_calibration_authorized",
    "llm_decisioning_authorized",
)


def _candidate_request(**extra: object) -> dict:
    base = {
        "instrument_id": "SCM_UNIT_JACKKNIFE",
        "estimator_family": "SCM",
        "inference_family": "UNIT_JACKKNIFE",
        "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
        "estimand": "STANDARD_INCREMENTALITY",
        "production_context": "production",
    }
    base.update(extra)
    return base


def test_public_api_exists() -> None:
    assert callable(evaluate_statistical_promotion_thresholds)
    assert callable(evaluate_promotion_thresholds)
    assert callable(check_statistical_thresholds)
    assert callable(get_default_statistical_promotion_policy)
    assert callable(explain_threshold_failures)
    assert callable(is_statistically_promotable)
    policy = get_default_statistical_promotion_policy()
    assert policy.coverage_min_production_candidate == 0.90


def test_missing_evidence_blocks_production_candidate() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM",
            "inference_family": "UNIT_JACKKNIFE",
            "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
        }
    )
    assert isinstance(report, StatisticalPromotionThresholdReport)
    assert report.is_statistically_promotable is False
    assert report.promotion_status == STATISTICAL_PROMOTION_INCONCLUSIVE
    assert "coverage" in report.missing_metrics


def test_missing_numeric_threshold_blocks_production_safe() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(
            requested_maturity_state=MATURITY_PRODUCTION_SAFE,
            observed_metrics={"coverage": 0.95, "false_positive_rate": 0.03},
        )
    )
    assert report.is_statistically_promotable is False
    assert "bias_abs" in report.undefined_thresholds or "rmse" in report.undefined_thresholds


def test_coverage_below_threshold_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(observed_metrics={"coverage": 0.70, "false_positive_rate": 0.05, "type_i_error": 0.05})
    )
    assert "coverage" in report.failed_metrics
    assert FAILURE_THRESHOLD_FAILED_COVERAGE in report.blockers
    assert report.is_statistically_promotable is False


def test_coverage_above_threshold_passes_metric_but_not_production_safe() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(observed_metrics={"coverage": 0.92, "false_positive_rate": 0.05, "type_i_error": 0.05})
    )
    assert "coverage" in report.passed_metrics
    safe = evaluate_statistical_promotion_thresholds(
        {
            **_candidate_request(
                requested_maturity_state=MATURITY_PRODUCTION_SAFE,
                observed_metrics={"coverage": 0.92, "false_positive_rate": 0.03, "type_i_error": 0.03},
            )
        }
    )
    assert isinstance(safe, StatisticalPromotionThresholdReport)
    assert safe.is_statistically_promotable is False


def test_type_i_above_max_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(
            observed_metrics={"coverage": 0.95, "type_i_error": 0.20, "false_positive_rate": 0.20}
        )
    )
    assert "type_i_error" in report.failed_metrics
    assert FAILURE_THRESHOLD_FAILED_TYPE_I_ERROR in report.blockers


def test_fpr_above_max_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(
            observed_metrics={"coverage": 0.95, "type_i_error": 0.05, "false_positive_rate": 0.25}
        )
    )
    assert "false_positive_rate" in report.failed_metrics
    assert FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE in report.blockers


def test_directional_false_signal_above_max_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(
            requested_maturity_state=MATURITY_PRODUCTION_SAFE,
            observed_metrics={
                "coverage": 0.95,
                "type_i_error": 0.03,
                "false_positive_rate": 0.03,
                "directional_false_signal_rate": 0.25,
            },
        )
    )
    assert "directional_false_signal_rate" in report.failed_metrics
    assert FAILURE_THRESHOLD_FAILED_DIRECTIONAL_FALSE_SIGNAL in report.blockers


def test_negative_interval_width_rate_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(observed_metrics={"coverage": 0.95, "false_positive_rate": 0.05, "negative_interval_width_rate": 0.01})
    )
    assert "negative_interval_width_rate" in report.failed_metrics
    assert FAILURE_THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH in report.blockers


def test_invalid_interval_rate_fails() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(observed_metrics={"coverage": 0.95, "false_positive_rate": 0.05, "invalid_interval_rate": 0.02})
    )
    assert "invalid_interval_rate" in report.failed_metrics
    assert report.is_statistically_promotable is False


def test_did_bootstrap_production_blocked_by_default() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "DID_BOOTSTRAP",
            "estimator_family": "DID_FAMILY",
            "inference_family": "BOOTSTRAP",
            "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"coverage": 0.95, "false_positive_rate": 0.05},
        }
    )
    assert report.promotion_status == STATISTICAL_PROMOTION_BLOCKED
    assert report.is_statistically_promotable is False


def test_did_2x2_point_estimate_not_production_safe() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "DID_2X2_POINT_ESTIMATE",
            "estimator_family": "DID_FAMILY",
            "inference_family": "POINT_ESTIMATE_ONLY",
            "requested_maturity_state": MATURITY_PRODUCTION_SAFE,
            "estimand": "STANDARD_INCREMENTALITY",
        }
    )
    assert report.is_statistically_promotable is False


def test_tbr_ridge_kfold_fails_with_negative_interval_evidence() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "TBR_RIDGE_KFOLD",
            "estimator_family": "TBR_RIDGE",
            "inference_family": "KFOLD",
            "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"negative_interval_width_rate": 0.05, "coverage": 0.95, "false_positive_rate": 0.05},
        }
    )
    assert report.is_statistically_promotable is False
    assert report.promotion_status in {STATISTICAL_PROMOTION_BLOCKED, STATISTICAL_PROMOTION_FAILED}


def test_tbr_ridge_conformal_blocked_without_calibration() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "TBR_RIDGE_CONFORMAL",
            "estimator_family": "TBR_RIDGE",
            "inference_family": "CONFORMAL",
            "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
            "estimand": "STANDARD_INCREMENTALITY",
        }
    )
    assert report.is_statistically_promotable is False
    assert report.promotion_status in {STATISTICAL_PROMOTION_BLOCKED, STATISTICAL_PROMOTION_INCONCLUSIVE}


@pytest.mark.parametrize("estimator_family", ["TROP", "MTGP", "BAYESIANTBR"])
def test_research_only_methods_remain_research_only(estimator_family: str) -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": f"{estimator_family}_INSTRUMENT",
            "estimator_family": estimator_family,
            "inference_family": "BOOTSTRAP",
            "requested_maturity_state": MATURITY_PRODUCTION_CANDIDATE,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"coverage": 0.95, "false_positive_rate": 0.05},
        }
    )
    assert report.is_statistically_promotable is False


def test_scm_unit_jackknife_restricted_expert_review_with_evidence() -> None:
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM",
            "inference_family": "UNIT_JACKKNIFE",
            "requested_maturity_state": MATURITY_RESTRICTED_EXPERT_REVIEW,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"coverage": 0.85, "false_positive_rate": 0.05},
        }
    )
    assert report.promotion_status in {
        STATISTICAL_PROMOTION_PASSED,
        STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS,
        STATISTICAL_PROMOTION_INCONCLUSIVE,
    }
    safe = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM",
            "inference_family": "UNIT_JACKKNIFE",
            "requested_maturity_state": MATURITY_PRODUCTION_SAFE,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"coverage": 0.95, "false_positive_rate": 0.03, "type_i_error": 0.03},
        }
    )
    assert isinstance(safe, StatisticalPromotionThresholdReport)
    assert safe.is_statistically_promotable is False


def test_config_override_changes_threshold_but_records_policy_version() -> None:
    report = evaluate_statistical_promotion_thresholds(
        _candidate_request(observed_metrics={"coverage": 0.85, "false_positive_rate": 0.05, "type_i_error": 0.05}),
        config={"policy": {"coverage_min_production_candidate": 0.80}},
    )
    assert "coverage" in report.passed_metrics
    assert report.policy_version == get_default_statistical_promotion_policy().policy_version


def test_list_input_returns_multiple_reports_without_ranking() -> None:
    reports = evaluate_statistical_promotion_thresholds(
        [
            _candidate_request(instrument_id="A", observed_metrics={"coverage": 0.95, "false_positive_rate": 0.05, "type_i_error": 0.05}),
            _candidate_request(instrument_id="B", observed_metrics={"coverage": 0.50, "false_positive_rate": 0.05, "type_i_error": 0.05}),
        ]
    )
    assert isinstance(reports, list)
    assert len(reports) == 2
    assert {r.instrument_id for r in reports} == {"A", "B"}


@dataclass
class _ThresholdInput:
    instrument_id: str
    estimator_family: str
    inference_family: str
    requested_maturity_state: str
    estimand: str
    observed_metrics: dict[str, float]


def test_dataclass_like_input_supported() -> None:
    payload = _ThresholdInput(
        instrument_id="SCM_UNIT_JACKKNIFE",
        estimator_family="SCM",
        inference_family="UNIT_JACKKNIFE",
        requested_maturity_state=MATURITY_RESTRICTED_EXPERT_REVIEW,
        estimand="STANDARD_INCREMENTALITY",
        observed_metrics={"coverage": 0.85, "false_positive_rate": 0.05},
    )
    report = evaluate_statistical_promotion_thresholds(payload)
    assert isinstance(report, StatisticalPromotionThresholdReport)


def test_production_catalog_integrates_statistical_threshold_blockers() -> None:
    report = evaluate_production_catalog_status(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM",
            "inference_family": "UNIT_JACKKNIFE",
            "production_context": "production",
            "requested_role": "PRODUCTION_CANDIDATE",
            "claim_type": "INCREMENTAL_LIFT_CLAIM",
        }
    )
    assert report.is_production_blocked is True
    assert (
        BLOCKER_MISSING_THRESHOLDS in report.blockers
        or BLOCKER_MISSING_REQUIRED_EVIDENCE in report.blockers
        or BLOCKER_STATISTICAL_PROMOTION_THRESHOLD_FAILED in report.blockers
    )


def test_method_suitability_attaches_threshold_overlay() -> None:
    packet = {
        "design_id": "d1",
        "design_structure_type": "SINGLE_TREATMENT_CONTROL",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
        },
        "contrast_summaries": [{
            "contrast_id": "T1_vs_C0",
            "contrast_type": "GO_DARK_VS_BAU",
            "estimand_label": "GO_DARK_VS_BAU",
            "bau_control_preserved": True,
        }],
        "estimand_summaries": ["GO_DARK_VS_BAU"],
        "governance_summary": {
            "instrument_catalog_status": "AVAILABLE",
            "governed_methods": ["SCM_FAMILY"],
        },
        "candidate_method_family_review_targets": ["SCM_FAMILY"],
    }
    report = evaluate_method_suitability(packet, MethodSuitabilityConfig())
    row = next(r for r in report.instrument_suitability_matrix if r["instrument_id"] == "SCM_UNIT_JACKKNIFE")
    assert "statistical_promotion_status" in row
    assert "statistical_threshold_failures" in row
    assert "is_statistically_promotion_blocked" in row


def test_readout_plan_excludes_statistically_failed_primary_candidates() -> None:
    req = {
        "design_id": "d1",
        "readout_method_governance_status": "PASS",
        "assignment_artifact": {"artifact_id": "a1"},
        "reproducibility_manifest": {"manifest_id": "m1"},
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "bootstrap"},
        "instrument_suitability_matrix": [{
            "instrument_id": "DID_BOOTSTRAP",
            "estimator_family": "DID_FAMILY",
            "inference_family": "BOOTSTRAP",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
            "governance_status": "GOVERNED",
            "estimand": "STANDARD_INCREMENTALITY",
        }],
    }
    report = build_readout_plan(req, ReadoutPlanRuntimeConfig())
    assert "DID_BOOTSTRAP" not in report.readout_plan_packet["planned_primary_candidates"]


def test_all_claim_production_authorization_flags_false() -> None:
    report = evaluate_statistical_promotion_thresholds(_candidate_request())
    assert isinstance(report, StatisticalPromotionThresholdReport)
    boundary = report.claim_boundary_report
    for key in _AUTH_FALSE_KEYS:
        assert boundary.get(key) is False, key


def test_explain_threshold_failures_and_is_promotable_helpers() -> None:
    payload = _candidate_request(observed_metrics={"coverage": 0.50, "false_positive_rate": 0.05, "type_i_error": 0.05})
    failures = explain_threshold_failures(payload)
    assert FAILURE_THRESHOLD_FAILED_COVERAGE in failures
    assert is_statistically_promotable(payload) is False


def test_summary_json_and_run_validation() -> None:
    summary = run_validation(write_summary=True)
    assert summary["final_verdict"] == (
        "statistical_promotion_thresholds_enforced_no_method_unblock_or_claim_authorization"
    )
    assert _SUMMARY.exists()
    loaded = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _AUTH_FALSE_KEYS:
        assert loaded.get(key) is False, key
