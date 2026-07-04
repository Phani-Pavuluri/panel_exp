"""Tests for READOUT_PLAN_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_plan_runtime_001 import (
    InstrumentPlanningCategory,
    ReadoutPlanRuntimeConfig,
    ReadoutPlanStatus,
    ReadoutStackRole,
    build_readout_plan,
    plan_readout_stack,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_PLAN_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_PLAN_RUNTIME_001_REPORT.md"


def _base_request(**extra: object) -> dict:
    req = {
        "design_id": "design_readout_plan_test",
        "readout_method_governance_status": "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
        "assignment_artifact_status": "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
        "assignment_plan": {
            "artifact_id": "assignment_plan_001",
            "assignment_algorithm_category": "DETERMINISTIC_RULE_ASSIGNMENT",
        },
        "assignment_candidate": {"candidate_id": "assignment_candidate_001"},
        "reproducibility_manifest": {"seed_policy": "NOT_APPLICABLE_DETERMINISTIC"},
        "instrument_suitability_matrix": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "estimator_family": "DID_FAMILY",
                "inference_family": "POINT_ESTIMATE_ONLY",
                "governance_status": "GOVERNED",
                "planning_category": "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE",
                "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
                "review_requirements": ["STANDARD_INCREMENTALITY_REVIEW"],
                "required_diagnostics": ["placebo_check"],
                "required_sensitivity_checks": ["donor_pool_sensitivity"],
                "uncertainty_semantics": "causal_interval_candidate_requires_validation",
                "estimand_compatibility_status": "PASS",
                "warnings": [],
                "blocking_reasons": [],
            },
            {
                "instrument_id": "SCM_PLACEBO",
                "estimator_family": "SCM_FAMILY",
                "inference_family": "PLACEBO_INFERENCE_FAMILY",
                "governance_status": "DIAGNOSTIC_ONLY",
                "planning_category": "PLANNING_DIAGNOSTIC_ONLY",
                "suitability_status": "METHOD_FAMILY_DIAGNOSTIC_ONLY",
                "review_requirements": ["METHOD_GOVERNANCE_REVIEW"],
                "required_diagnostics": ["placebo_check"],
                "required_sensitivity_checks": [],
                "uncertainty_semantics": "prediction_interval_only",
                "estimand_compatibility_status": "PASS",
                "warnings": [],
                "blocking_reasons": [],
                "diagnostic_only_reason": "governance diagnostic-only instrument",
            },
        ],
        "estimand_scope": {
            "estimand_type": "STANDARD_INCREMENTALITY",
            "estimand": "STANDARD_INCREMENTALITY",
            "population_scope": "eligible_dma",
            "time_window": "post_period",
            "metric_kpi": "sales",
        },
        "uncertainty_scope": {
            "semantics": "causal_interval_candidate_requires_validation",
            "uncertainty_sources_included": ["resampling"],
        },
        "required_diagnostics": ["placebo_check", "pre_period_fit_diagnostic"],
        "required_sensitivity_checks": ["donor_pool_sensitivity"],
        "claim_eligibility_reports": [{"claim_type": "POINT_ESTIMATE_READOUT_CLAIM", "eligible": True}],
        "claim_scope": {
            "estimand": "STANDARD_INCREMENTALITY",
            "population_scope": "eligible_dma",
            "time_window": "post_period",
            "metric_kpi": "sales",
            "assignment_artifact": "assignment_plan_001",
            "planned_instruments": ["DID_2X2_POINT_ESTIMATE", "SCM_PLACEBO"],
            "uncertainty_semantics": "causal_interval_candidate_requires_validation",
            "diagnostics_prerequisites": ["placebo_check"],
            "sensitivity_prerequisites": ["donor_pool_sensitivity"],
            "reporting_caveats": [],
            "roi_governance_status": "NOT_APPROVED",
        },
        "production_governance_config": {"blocked_roles": ["production", "trust_report"]},
    }
    req.update(extra)
    return req


def test_eligible_did_bootstrap_primary_candidate() -> None:
    report = build_readout_plan(_base_request())
    assert report.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT
    assert any(x.instrument_id == "DID_2X2_POINT_ESTIMATE" for x in report.planned_primary_candidates)


def test_multiple_eligible_primary_candidates_without_winner() -> None:
    req = _base_request()
    req["instrument_suitability_matrix"].append(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM_FAMILY",
            "inference_family": "JACKKNIFE_INFERENCE_FAMILY",
            "planning_category": "PLANNING_ELIGIBLE_WITH_WARNINGS",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS",
            "warnings": ["stress-null elevated false positives"],
        }
    )
    report = build_readout_plan(req)
    assert len(report.planned_primary_candidates) >= 2
    assert not report.claim_boundary_report.method_winner_selected
    assert not report.claim_boundary_report.primary_readout_stack_selected


def test_restricted_tbr_ridge_brb_primary_with_caveats() -> None:
    req = _base_request()
    req["instrument_suitability_matrix"] = [
        {
            "instrument_id": "TBR_RIDGE_BRB",
            "estimator_family": "TBR_RIDGE_FAMILY",
            "inference_family": "BOOTSTRAP_INFERENCE_FAMILY",
            "planning_category": "PLANNING_RESTRICTED_REQUIRES_REVIEW",
            "suitability_status": "METHOD_FAMILY_RESTRICTED",
            "required_diagnostics": ["parallel_trend_diagnostic"],
            "required_sensitivity_checks": ["inference_path_sensitivity"],
        }
    ]
    report = build_readout_plan(req)
    assert any(x.instrument_id == "TBR_RIDGE_BRB" for x in report.planned_primary_candidates)
    assert any("restricted" in c for c in report.reporting_caveats)


def test_scm_placebo_diagnostic_only_slot() -> None:
    req = _base_request()
    req["instrument_suitability_matrix"] = [req["instrument_suitability_matrix"][1]]
    cfg = ReadoutPlanRuntimeConfig(block_when_only_diagnostic_instruments=False)
    report = build_readout_plan(req, cfg)
    assert report.planned_primary_candidates == ()
    assert all(x.stack_role == ReadoutStackRole.DIAGNOSTIC_READOUT_CANDIDATE for x in report.planned_diagnostic_candidates)


def test_blocked_and_not_evaluated_preserved() -> None:
    req = _base_request()
    req["instrument_suitability_matrix"] = [
        {
            "instrument_id": "AB_STANDARD_INFERENCE",
            "planning_category": "PLANNING_BLOCKED",
            "suitability_status": "METHOD_FAMILY_BLOCKED",
            "blocking_reasons": ["requires individual randomized ab"],
        },
        {
            "instrument_id": "UNKNOWN_PATH",
            "planning_category": "PLANNING_NOT_EVALUATED",
            "suitability_status": "METHOD_FAMILY_NOT_EVALUATED",
        },
    ]
    cfg = ReadoutPlanRuntimeConfig(block_when_all_instruments_blocked=False)
    report = build_readout_plan(req, cfg)
    assert any(x.instrument_id == "AB_STANDARD_INFERENCE" for x in report.blocked_instruments)
    assert any(x.instrument_id == "UNKNOWN_PATH" for x in report.not_evaluated_instruments)


def test_blocked_readout_governance_blocks_plan() -> None:
    req = _base_request(readout_method_governance_status="READOUT_GOVERNANCE_BLOCKED_BY_INSTRUMENT_GOVERNANCE")
    report = build_readout_plan(req)
    assert report.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE


def test_missing_assignment_artifact_blocks_plan() -> None:
    req = _base_request()
    req.pop("assignment_plan")
    req.pop("assignment_candidate")
    report = build_readout_plan(req)
    assert report.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT


def test_missing_reproducibility_manifest_blocks_plan() -> None:
    req = _base_request()
    req.pop("reproducibility_manifest")
    report = build_readout_plan(req)
    assert report.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT


def test_all_instruments_blocked_blocks_plan() -> None:
    req = _base_request(
        instrument_suitability_matrix=[
            {"instrument_id": "X1", "planning_category": "PLANNING_BLOCKED", "suitability_status": "METHOD_FAMILY_BLOCKED"},
            {"instrument_id": "X2", "planning_category": "PLANNING_BLOCKED", "suitability_status": "METHOD_FAMILY_BLOCKED"},
        ]
    )
    report = build_readout_plan(req)
    assert report.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS


def test_only_diagnostic_instruments_behavior_configurable() -> None:
    req = _base_request(instrument_suitability_matrix=[_base_request()["instrument_suitability_matrix"][1]])
    blocked = build_readout_plan(req)
    assert blocked.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS
    provisional = build_readout_plan(req, ReadoutPlanRuntimeConfig(block_when_only_diagnostic_instruments=False))
    assert provisional.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL


def test_missing_estimand_scope_blocks_or_provisional() -> None:
    req = _base_request()
    req.pop("estimand_scope")
    blocked = build_readout_plan(req)
    assert blocked.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ESTIMAND
    cfg = ReadoutPlanRuntimeConfig(block_on_missing_estimand_scope=False)
    provisional = build_readout_plan(req, cfg)
    assert provisional.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL


def test_missing_uncertainty_scope_blocks_or_provisional() -> None:
    req = _base_request()
    req.pop("uncertainty_scope")
    blocked = build_readout_plan(req)
    assert blocked.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS
    cfg = ReadoutPlanRuntimeConfig(block_on_missing_uncertainty_scope=False)
    provisional = build_readout_plan(req, cfg)
    assert provisional.readout_plan_status == ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL


def test_diagnostics_and_sensitivity_prerequisites_preserved() -> None:
    report = build_readout_plan(_base_request())
    assert "placebo_check" in report.required_diagnostics
    assert "donor_pool_sensitivity" in report.required_sensitivity_checks
    assert report.claim_boundary_report.execution_prerequisites_generated


def test_srm_balance_prerequisites_added_for_randomized_assignment() -> None:
    req = _base_request(
        assignment_plan={
            "artifact_id": "assignment_plan_001",
            "assignment_algorithm_category": "RANDOMIZED_ASSIGNMENT",
        },
    )
    report = build_readout_plan(req)
    assert "srm_balance_readout_diagnostic" in report.required_diagnostics
    assert "srm_balance_readout_diagnostic_required" in report.execution_prerequisites


def test_missing_diagnostics_and_sensitivity_require_plan() -> None:
    req = _base_request(required_diagnostics=[], required_sensitivity_checks=[])
    report = build_readout_plan(req)
    assert report.readout_plan_status in (
        ReadoutPlanStatus.READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN,
        ReadoutPlanStatus.READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN,
    )
    assert any("diagnostic plan required" in w for w in report.warnings)
    assert any("sensitivity plan required" in w for w in report.warnings)


def test_claim_scope_generated_not_authorized_and_roi_caveat() -> None:
    req = _base_request(
        claim_eligibility_reports=[{"claim_type": "ROI_CLAIM", "eligible": True}],
    )
    report = build_readout_plan(req)
    assert report.claim_scope is not None
    assert not report.claim_boundary_report.causal_claim_authorized
    assert not report.claim_boundary_report.roi_claim_authorized
    assert any("ROI" in c for c in report.reporting_caveats)


def test_dosage_and_budget_reallocation_caveats() -> None:
    dosage_req = _base_request(
        estimand_scope={"estimand_type": "DOSAGE_CONTRAST", "estimand": "DOSAGE_CONTRAST"},
    )
    dosage_report = build_readout_plan(dosage_req)
    assert any("dosage" in c.lower() for c in dosage_report.reporting_caveats)

    budget_req = _base_request(
        estimand_scope={"estimand_type": "BUDGET_REALLOCATION", "estimand": "BUDGET_REALLOCATION"},
    )
    budget_report = build_readout_plan(budget_req)
    assert any("budget reallocation" in c.lower() for c in budget_report.reporting_caveats)


def test_assignment_limitation_caveat_preserved() -> None:
    report = build_readout_plan(_base_request())
    assert any("deterministic explicit-pool assignment limitation" in c for c in report.reporting_caveats)


def test_claim_boundary_execution_flags_false() -> None:
    report = build_readout_plan(_base_request())
    cb = report.claim_boundary_report
    assert cb.readout_plan_runtime_implemented
    assert cb.readout_plan_generated
    assert not cb.primary_readout_stack_selected
    assert not cb.method_winner_selected
    assert not cb.estimator_execution_implemented
    assert not cb.inference_execution_implemented
    assert not cb.effect_estimate_computed
    assert not cb.lift_computed
    assert not cb.roi_computed
    assert not cb.p_value_computed
    assert not cb.confidence_interval_computed
    assert not cb.uncertainty_computed
    assert not cb.diagnostic_check_executed
    assert not cb.sensitivity_check_executed
    assert not cb.production_readout_authorized
    assert not cb.production_authorization_granted
    assert not cb.mmm_runtime_calls_implemented
    assert not cb.llm_decisioning_authorized


def test_alias_and_multiple_requests_no_ranking() -> None:
    r1 = _base_request(design_id="d1")
    r2 = _base_request(design_id="d2")
    report = plan_readout_stack([r1, r2])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None


def test_runtime_accepts_contract_alias_status() -> None:
    req = _base_request(readout_method_governance_status="READOUT_PLAN_READY_FOR_RUNTIME_PLANNING")
    report = build_readout_plan(req)
    assert report.readout_plan_status in (
        ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT,
        ReadoutPlanStatus.READOUT_PLAN_READY_WITH_WARNINGS,
        ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL,
        ReadoutPlanStatus.READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN,
        ReadoutPlanStatus.READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN,
    )


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "readout_plan_runtime_implemented_planning_only_no_estimator_execution_or_claim_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["readout_plan_runtime_implemented"] is True
    assert summary["readout_plan_generated"] is True
    assert summary["primary_readout_stack_selected"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()


def test_production_blocked_instrument_excluded_from_primary_candidates() -> None:
    req = _base_request(
        instrument_suitability_matrix=[{
            "instrument_id": "TBR_RIDGE_KFOLD",
            "estimator_family": "TBR_RIDGE_FAMILY",
            "inference_family": "KFOLD",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
            "governance_status": "GOVERNED",
        }],
    )
    report = build_readout_plan(req)
    assert "TBR_RIDGE_KFOLD" not in report.readout_plan_packet["planned_primary_candidates"]
