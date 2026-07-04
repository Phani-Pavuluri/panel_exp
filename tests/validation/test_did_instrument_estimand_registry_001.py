"""Tests for DID_INSTRUMENT_ESTIMAND_UNIFICATION_001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.did_instrument_estimand_registry_001 import (
    DID_2X2_POINT_ESTIMATE,
    DID_BOOTSTRAP_INFERENCE,
    DID_GOVERNED_POINT_ESTIMATE,
    DID_TWFE_LIBRARY_RESEARCH,
    DIDInstrumentRegistryConfig,
    get_did_instrument_contract,
    get_did_instrument_registry,
    is_did_bootstrap_inference_instrument,
    is_did_twfe_research_instrument,
    is_governed_did_point_estimate_instrument,
    resolve_did_instrument_id,
    run_validation,
    validate_did_instrument_for_execution,
)
from panel_exp.validation.estimator_inference_did_executor_003 import execute_did_point_estimate
from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    INSTRUMENT_EXECUTION_BLOCKED,
    INSTRUMENT_EXECUTION_COMPLETED,
    EstimatorInferenceExecutionRuntimeConfig,
    execute_estimator_inference,
)
from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION,
    lookup_governed_executor,
)
from panel_exp.validation.method_suitability_runtime_001 import (
    MethodFamilySuitabilityStatus,
    MethodSuitabilityConfig,
    evaluate_method_suitability,
)
from panel_exp.validation.production_catalog_blocklist_001 import (
    PRODUCTION_CATALOG_BLOCKED,
    PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW,
    evaluate_production_catalog_status,
)
from panel_exp.validation.readout_plan_runtime_001 import (
    ReadoutPlanRuntimeConfig,
    build_readout_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DID_INSTRUMENT_ESTIMAND_UNIFICATION_001_summary.json"

_AUTH_FALSE_KEYS = (
    "twfe_executor_implemented",
    "bootstrap_inference_implemented",
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
    "inference_execution_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "mmm_runtime_calls_implemented",
    "mmm_calibration_authorized",
    "llm_decisioning_authorized",
)


def _panel() -> list[dict]:
    return [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]


def _did_input(**extra: object) -> dict:
    base = {
        "instrument_id": DID_2X2_POINT_ESTIMATE,
        "panel_data": _panel(),
        "unit_id_field": "geo_id",
        "time_field": "week",
        "outcome_field": "sales",
        "treatment_field": "treated",
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
        "assignment_artifact_id": "assignment_001",
        "estimand": "STANDARD_INCREMENTALITY",
        "metric_name": "sales",
    }
    base.update(extra)
    return base


def test_registry_exposes_canonical_instruments() -> None:
    registry = get_did_instrument_registry()
    assert DID_2X2_POINT_ESTIMATE in registry
    assert DID_BOOTSTRAP_INFERENCE in registry
    assert DID_TWFE_LIBRARY_RESEARCH in registry


def test_resolve_canonicalizes_governed_alias() -> None:
    resolution = resolve_did_instrument_id(DID_GOVERNED_POINT_ESTIMATE)
    assert resolution.canonical_instrument_id == DID_2X2_POINT_ESTIMATE
    assert resolution.is_governed_point_estimate is True


def test_resolve_maps_did_bootstrap_to_inference() -> None:
    resolution = resolve_did_instrument_id("DID_BOOTSTRAP")
    assert resolution.canonical_instrument_id == DID_BOOTSTRAP_INFERENCE
    assert resolution.is_bootstrap_inference is True
    assert resolution.is_governed_point_estimate is False


def test_point_estimate_contract_governed_no_uncertainty() -> None:
    contract = get_did_instrument_contract(DID_2X2_POINT_ESTIMATE)
    assert contract.governed_runtime_supported is True
    assert contract.inference_support_status == "INFERENCE_NOT_IMPLEMENTED"
    assert contract.uncertainty_support_status == "UNCERTAINTY_NOT_SUPPORTED"
    assert contract.execution_support_status == "EXECUTION_SUPPORTED"


def test_bootstrap_contract_not_implemented() -> None:
    contract = get_did_instrument_contract("DID_BOOTSTRAP")
    assert contract.canonical_instrument_id == DID_BOOTSTRAP_INFERENCE
    assert contract.governed_runtime_supported is False
    assert contract.execution_support_status == "EXECUTION_NOT_IMPLEMENTED"


def test_twfe_library_research_contract() -> None:
    contract = get_did_instrument_contract(DID_TWFE_LIBRARY_RESEARCH)
    assert contract.research_library_supported is True
    assert contract.governed_runtime_supported is False


def test_executor_accepts_canonical_point_estimate() -> None:
    result = execute_did_point_estimate(
        _did_input(),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is True
    assert result.instrument_id == DID_2X2_POINT_ESTIMATE


def test_executor_rejects_did_bootstrap_by_default() -> None:
    result = execute_did_point_estimate(
        _did_input(instrument_id="DID_BOOTSTRAP"),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False
    assert result.failure_packet is not None
    assert "MISLEADING_INSTRUMENT_ID" in result.failure_packet["blocked_requirements"] or any(
        "bootstrap" in r.lower() for r in result.blocking_reasons
    )


def test_legacy_bootstrap_alias_only_with_transition_config() -> None:
    result = execute_did_point_estimate(
        _did_input(instrument_id="DID_BOOTSTRAP"),
        config={
            "allow_governed_did_point_estimate_execution": True,
            "allow_legacy_did_bootstrap_for_point_estimate": True,
        },
    )
    assert result.did_point_estimate_computed is True


def test_adapter_distinguishes_point_estimate_vs_bootstrap() -> None:
    point = lookup_governed_executor(
        DID_2X2_POINT_ESTIMATE,
        config={"allow_governed_did_point_estimate_execution": True},
    )
    bootstrap = lookup_governed_executor("DID_BOOTSTRAP")
    assert point.availability_status == EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
    assert bootstrap.supports_execution is False
    assert bootstrap.availability_status == EXECUTOR_AVAILABLE_FOR_DRY_RUN


def test_production_catalog_blocks_bootstrap_production_claims() -> None:
    report = evaluate_production_catalog_status({
        "instrument_id": "DID_BOOTSTRAP",
        "production_context": "production",
        "claim_type": "INCREMENTAL_LIFT_CLAIM",
    })
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_BLOCKED


def test_production_catalog_point_estimate_restricted_not_causal() -> None:
    report = evaluate_production_catalog_status({
        "instrument_id": DID_2X2_POINT_ESTIMATE,
        "production_context": "production",
        "claim_type": "INCREMENTAL_LIFT_CLAIM",
    })
    assert report.is_production_blocked is True
    assert report.production_catalog_status == PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW


def test_method_suitability_blocks_did_bootstrap() -> None:
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
        "governance_summary": {"instrument_catalog_status": "AVAILABLE", "governed_methods": ["DID_FAMILY"]},
        "candidate_instrument_review_targets": ["DID_BOOTSTRAP", "DID_2X2_POINT_ESTIMATE"],
    }
    report = evaluate_method_suitability(packet, MethodSuitabilityConfig())
    bootstrap = next(e for e in report.instrument_suitability_reports if e.instrument_id == "DID_BOOTSTRAP")
    point = next(e for e in report.instrument_suitability_reports if e.instrument_id == DID_2X2_POINT_ESTIMATE)
    assert bootstrap.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
    assert point.suitability_status != MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED


def test_readout_plan_uses_canonical_point_instrument() -> None:
    req = {
        "design_id": "d1",
        "readout_method_governance_status": "PASS",
        "assignment_artifact": {"artifact_id": "a1"},
        "reproducibility_manifest": {"manifest_id": "m1"},
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "point_estimate_only"},
        "instrument_suitability_matrix": [{
            "instrument_id": DID_2X2_POINT_ESTIMATE,
            "estimator_family": "DID_FAMILY",
            "inference_family": "POINT_ESTIMATE_ONLY",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
            "governance_status": "GOVERNED",
        }],
    }
    report = build_readout_plan(req, ReadoutPlanRuntimeConfig())
    assert DID_2X2_POINT_ESTIMATE in report.readout_plan_packet["planned_primary_candidates"]


def test_execution_runtime_routes_canonical_point_estimate() -> None:
    from tests.validation.test_estimator_inference_execution_runtime_001 import _base_request

    req = _base_request(panel_data=_panel())
    req["planned_primary_candidates"][0]["instrument_id"] = DID_2X2_POINT_ESTIMATE
    req["planned_primary_candidates"][0]["inference_family"] = "POINT_ESTIMATE_ONLY"
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(req, config=cfg)
    row = next(r for r in report.instrument_execution_results if r.instrument_id == DID_2X2_POINT_ESTIMATE)
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_COMPLETED


def test_execution_runtime_blocks_bootstrap_production_context() -> None:
    from tests.validation.test_estimator_inference_execution_runtime_001 import _base_request

    req = _base_request()
    req["planned_primary_candidates"] = [{
        **req["planned_primary_candidates"][0],
        "instrument_id": "DID_BOOTSTRAP",
        "inference_family": "BOOTSTRAP_INFERENCE_FAMILY",
        "uncertainty_semantics": "bootstrap",
    }]
    req["production_context"] = "production"
    req["claim_type"] = "INCREMENTAL_LIFT_CLAIM"
    report = execute_estimator_inference(req)
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_BOOTSTRAP")
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_BLOCKED


def test_helper_predicates() -> None:
    assert is_governed_did_point_estimate_instrument(DID_GOVERNED_POINT_ESTIMATE)
    assert is_did_bootstrap_inference_instrument("DID_BOOTSTRAP")
    assert is_did_twfe_research_instrument("TWFE")


def test_validation_report_blockers_for_bootstrap() -> None:
    report = validate_did_instrument_for_execution(
        {"instrument_id": "DID_BOOTSTRAP"},
        config=DIDInstrumentRegistryConfig(allow_governed_did_point_estimate_execution=True),
    )
    assert report.execution_allowed is False
    assert report.blockers


def test_all_authorization_flags_false() -> None:
    contract = get_did_instrument_contract(DID_2X2_POINT_ESTIMATE)
    for key in _AUTH_FALSE_KEYS:
        assert contract.claim_boundary[key] is False


def test_summary_json() -> None:
    run_validation(write_summary=True)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001"
    assert data["final_verdict"] == "did_instrument_estimand_unified_no_bootstrap_or_claim_authorization"
    for key in _AUTH_FALSE_KEYS:
        assert data[key] is False
