"""Tests for PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    EstimatorInferenceExecutionRuntimeConfig,
    INSTRUMENT_EXECUTION_BLOCKED,
    execute_estimator_inference,
)
from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    lookup_governed_executor,
)
from panel_exp.validation.method_suitability_runtime_001 import (
    MethodSuitabilityConfig,
    evaluate_method_suitability,
)
from panel_exp.validation.production_catalog_blocklist_001 import (
    BLOCKER_INFERENCE_NOT_IMPLEMENTED,
    BLOCKER_RESEARCH_ONLY,
    BLOCKER_UNVALIDATED,
    PRODUCTION_CATALOG_BLOCKED,
    PRODUCTION_CATALOG_DIAGNOSTIC_ONLY,
    PRODUCTION_CATALOG_NOT_EVALUATED,
    PRODUCTION_CATALOG_RESEARCH_ONLY,
    PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW,
    ProductionCatalogBlocklistConfig,
    evaluate_production_catalog_status,
    evaluate_production_catalog_status_batch,
    explain_production_blockers,
    get_default_production_catalog_policy,
    is_production_blocked,
    run_validation,
)
from panel_exp.validation.readout_plan_runtime_001 import (
    ReadoutPlanRuntimeConfig,
    build_readout_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001_summary.json"

_AUTH_FALSE_KEYS = (
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
    "estimator_execution_implemented",
    "inference_execution_implemented",
    "effect_estimate_computed",
    "diagnostic_check_executed",
    "sensitivity_check_executed",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "mmm_runtime_calls_implemented",
    "mmm_calibration_authorized",
    "llm_decisioning_authorized",
)


def _production_request(**extra: object) -> dict:
    base = {
        "instrument_id": "UNKNOWN",
        "method_family": "UNKNOWN",
        "estimator_family": "UNKNOWN",
        "inference_family": "UNKNOWN",
        "production_context": "production",
        "requested_role": "PRODUCTION_CANDIDATE",
    }
    base.update(extra)
    return base


def test_public_api_exists() -> None:
    assert callable(evaluate_production_catalog_status)
    assert callable(is_production_blocked)
    assert callable(explain_production_blockers)
    assert callable(get_default_production_catalog_policy)
    policy = get_default_production_catalog_policy()
    assert policy.enforce_production_catalog_blocklist is True


def test_research_only_method_blocked_for_production_but_research_allowed() -> None:
    report = evaluate_production_catalog_status(
        _production_request(estimator_family="TROP_FAMILY", method_family="TROP_FAMILY")
    )
    assert report.production_catalog_status == PRODUCTION_CATALOG_RESEARCH_ONLY
    assert report.is_production_blocked is True
    assert report.is_research_allowed is True
    assert BLOCKER_RESEARCH_ONLY in report.blockers


def test_unvalidated_method_production_blocked() -> None:
    report = evaluate_production_catalog_status(
        _production_request(estimator_family="UNVALIDATED_FAMILY", maturity_status="UNVALIDATED")
    )
    assert report.is_production_blocked is True
    assert BLOCKER_UNVALIDATED in report.blockers or report.production_catalog_status == PRODUCTION_CATALOG_NOT_EVALUATED


def test_expert_review_restricted_not_production_safe() -> None:
    report = evaluate_production_catalog_status(
        _production_request(estimator_family="DID_FAMILY", method_family="DID_FAMILY")
    )
    assert report.is_restricted_expert_review is True
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW


def test_did_bootstrap_production_claim_blocked() -> None:
    report = evaluate_production_catalog_status(
        _production_request(
            instrument_id="DID_BOOTSTRAP",
            estimator_family="DID_FAMILY",
            inference_family="BOOTSTRAP",
            claim_type="INCREMENTAL_LIFT_CLAIM",
        )
    )
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_BLOCKED
    assert BLOCKER_INFERENCE_NOT_IMPLEMENTED in report.blockers


def test_did_point_estimate_governed_role_not_production_claim() -> None:
    report = evaluate_production_catalog_status(
        {
            "instrument_id": "DID_BOOTSTRAP",
            "estimator_family": "DID_FAMILY",
            "inference_family": "BOOTSTRAP",
            "production_context": "research",
            "requested_role": "GOVERNED_POINT_ESTIMATE",
            "claim_type": "INCREMENTAL_LIFT_CLAIM",
        }
    )
    assert report.is_research_allowed is True
    assert report.is_production_blocked is True


def test_tbr_ridge_kfold_production_blocked() -> None:
    assert is_production_blocked(_production_request(instrument_id="TBR_RIDGE_KFOLD"))


def test_tbr_ridge_conformal_production_blocked() -> None:
    assert is_production_blocked(
        _production_request(estimator_family="TBR_RIDGE_FAMILY", inference_family="Conformal")
    )


def test_tbr_ridge_jackknife_production_blocked() -> None:
    for inference in ("UnitJackKnife", "JACKKNIFE", "JKP"):
        assert is_production_blocked(
            _production_request(estimator_family="TBR_RIDGE_FAMILY", inference_family=inference)
        )


def test_tbr_aggregate_unit_panel_mismatch_blocked() -> None:
    assert is_production_blocked(
        _production_request(estimator_family="TBR_FAMILY", method_family="TBR_FAMILY")
    )


def test_augsynth_conformal_blocked_by_default() -> None:
    report = evaluate_production_catalog_status(
        _production_request(estimator_family="AUGSYNTH_FAMILY", inference_family="Conformal")
    )
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_DIAGNOSTIC_ONLY


def test_augsynth_conformal_allowed_when_configured() -> None:
    cfg = ProductionCatalogBlocklistConfig(allow_augsynth_conformal_production=True)
    report = evaluate_production_catalog_status(
        _production_request(estimator_family="AUGSYNTH_FAMILY", inference_family="Conformal"),
        config=cfg,
    )
    assert report.production_catalog_status != PRODUCTION_CATALOG_DIAGNOSTIC_ONLY


@pytest.mark.parametrize(
    "estimator_family",
    ["TROP_FAMILY", "MTGP_FAMILY", "BAYESIAN_TBR_FAMILY"],
)
def test_research_only_estimator_families_blocked(estimator_family: str) -> None:
    assert is_production_blocked(_production_request(estimator_family=estimator_family))


def test_unknown_method_not_evaluated_or_blocked_in_production() -> None:
    report = evaluate_production_catalog_status(_production_request())
    assert report.is_production_blocked is True
    assert report.production_catalog_status in (
        PRODUCTION_CATALOG_NOT_EVALUATED,
        PRODUCTION_CATALOG_BLOCKED,
        PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW,
    )


def test_non_production_dry_run_not_blocked_when_allow_research_only_dry_run() -> None:
    report = evaluate_production_catalog_status(
        {
            "instrument_id": "DID_BOOTSTRAP",
            "estimator_family": "DID_FAMILY",
            "inference_family": "BOOTSTRAP",
            "production_context": "research",
            "requested_role": "DRY_RUN",
        },
        config=ProductionCatalogBlocklistConfig(allow_research_only_dry_run=True),
    )
    assert report.is_research_allowed is True


def test_method_suitability_attaches_production_catalog_status() -> None:
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
            "governed_methods": ["DID_FAMILY"],
        },
        "candidate_method_family_review_targets": ["DID_FAMILY"],
    }
    report = evaluate_method_suitability(packet, MethodSuitabilityConfig())
    row = report.instrument_suitability_matrix[0]
    assert "production_catalog_status" in row
    assert "production_blockers" in row
    assert "is_production_blocked" in row


def test_did_point_estimate_restricted_for_production_claims() -> None:
    report = evaluate_production_catalog_status({
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "production_context": "production",
        "claim_type": "INCREMENTAL_LIFT_CLAIM",
    })
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW


def test_did_point_estimate_allowed_for_review_context() -> None:
    report = evaluate_production_catalog_status({
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "production_context": "review",
        "requested_role": "POINT_ESTIMATE_REVIEW",
    })
    assert report.is_research_allowed is True
    assert report.is_production_blocked is False


def test_readout_plan_excludes_production_blocked_from_primary() -> None:
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
        }],
    }
    report = build_readout_plan(req, ReadoutPlanRuntimeConfig())
    assert "DID_BOOTSTRAP" not in report.readout_plan_packet["planned_primary_candidates"]
    assert "DID_BOOTSTRAP" in (
        report.readout_plan_packet["blocked_instruments"]
        + report.readout_plan_packet["research_only_instruments"]
    )


def test_executor_adapters_expose_production_catalog_metadata() -> None:
    lookup = lookup_governed_executor("DID_2X2_POINT_ESTIMATE")
    assert lookup.production_catalog_blocked is True
    assert lookup.production_claim_blocked is True
    assert lookup.production_catalog_status is not None


def test_execution_runtime_blocks_production_context_when_catalog_blocked() -> None:
    req = {
        "design_id": "d1",
        "readout_plan_status": "READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT",
        "production_context": "production",
        "claim_type": "INCREMENTAL_LIFT_CLAIM",
        "assignment_artifact": {"artifact_id": "a1"},
        "assignment_artifact_id": "a1",
        "reproducibility_manifest": {"manifest_id": "m1"},
        "execution_data_contract": {
            "required_columns": ["geo_id", "week", "sales"],
            "available_columns": ["geo_id", "week", "sales"],
        },
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "bootstrap"},
        "planned_primary_candidates": [{
            "instrument_id": "DID_BOOTSTRAP",
            "execution_role": "PRIMARY_EXECUTION_CANDIDATE",
            "estimator_family": "DID_FAMILY",
            "inference_family": "BOOTSTRAP",
            "assignment_artifact_id": "a1",
            "estimand_type": "STANDARD_INCREMENTALITY",
            "metric_name": "sales",
            "uncertainty_semantics": "bootstrap",
        }],
    }
    report = execute_estimator_inference(
        req,
        EstimatorInferenceExecutionRuntimeConfig(allow_execution_without_governed_executor=True),
    )
    inst = report.instrument_execution_results[0]
    assert inst.instrument_execution_status == INSTRUMENT_EXECUTION_BLOCKED
    assert any("production catalog" in r for r in inst.blocking_reasons)


def test_multiple_requests_evaluated_without_ranking() -> None:
    batch = evaluate_production_catalog_status_batch([
        _production_request(instrument_id="TBR_RIDGE_KFOLD"),
        _production_request(instrument_id="DID_BOOTSTRAP"),
    ])
    assert len(batch) == 2
    assert all(r.is_production_blocked for r in batch)


def test_all_authorization_flags_false() -> None:
    report = evaluate_production_catalog_status(_production_request(instrument_id="DID_BOOTSTRAP"))
    for key in _AUTH_FALSE_KEYS:
        assert report.claim_boundary_report[key] is False


def test_summary_json_validation() -> None:
    run_validation(write_summary=True)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001"
    assert data["final_verdict"] == "production_catalog_blocklist_enforced_no_claim_or_production_authorization"
    for key in _AUTH_FALSE_KEYS:
        assert data[key] is False
