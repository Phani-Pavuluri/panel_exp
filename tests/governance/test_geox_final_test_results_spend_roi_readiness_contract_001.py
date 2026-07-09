"""Governance tests for GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "spend_ingestion_system_created",
    "final_results_module_created",
    "roi_calculator_runtime_created",
    "claim_authorization_duplicated",
    "roi_claim_authorized",
    "roas_claim_authorized",
    "business_lift_claim_authorized",
    "decision_recommendation_authorized",
    "production_readout_authorized",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "inference_implemented",
    "estimator_implemented",
    "simulations_implemented",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_REQUIRED_TRUE_FLAGS = (
    "spend_roi_readiness_contract_completed",
    "existing_readout_stack_reused",
    "no_new_final_results_module",
    "no_new_spend_ingestion_system",
    "post_test_spend_evidence_defined",
    "spend_delta_readiness_defined",
    "roi_roas_readiness_defined",
    "trusted_readout_extension_points_defined",
    "claim_authorization_delegated",
    "mip_orchestration_requirements_defined",
    "runtime_followup_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001" in text
    assert "spend_roi_readiness_contract_defined_no_runtime_or_claim_authorization" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "geox_final_test_results_spend_roi_readiness_contract"


def test_existing_readout_stack_reused() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TRUSTED_READOUT_REPORT" in text
    assert "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001" in text
    assert "estimator_readout_adapter_001.py" in text
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    data = _load_summary()
    assert data["existing_readout_stack_reused"] is True


def test_no_new_final_results_module() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "no new final-results module" in text.lower() or "No new final-results module" in text
    data = _load_summary()
    assert data["no_new_final_results_module"] is True


def test_no_new_spend_ingestion_system() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "no new spend ingestion" in text.lower() or "No new spend ingestion" in text
    data = _load_summary()
    assert data["no_new_spend_ingestion_system"] is True


def test_post_test_spend_evidence_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "PostTestSpendEvidence" in text
    assert "actual_treatment_spend" in text
    assert "spend_delta" in text
    data = _load_summary()
    assert data["post_test_spend_evidence_defined"] is True


def test_spend_delta_readiness_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "BLOCKED_MISSING_SPEND_DELTA" in text
    assert "spend_delta_definition" in text
    data = _load_summary()
    assert data["spend_delta_readiness_defined"] is True


def test_roi_roas_readiness_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "ROAS" in text
    assert "profit_ROI" in text or "profit ROI" in text
    assert "cost_per_incremental_kpi" in text
    data = _load_summary()
    assert data["roi_roas_readiness_defined"] is True


def test_trusted_readout_extension_points_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "spend_readiness_summary" in text
    assert "post_test_spend_evidence" in text
    assert "efficiency_metric_readiness" in text
    data = _load_summary()
    assert data["trusted_readout_extension_points_defined"] is True


def test_claim_authorization_delegated() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert "Does not** authorize `ROI_CLAIM`" in text
    data = _load_summary()
    assert data["claim_authorization_delegated"] is True


def test_mip_orchestration_requirements_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MIP orchestration requirements" in text
    assert "KPI dataset required" in text or "KPI dataset" in text
    data = _load_summary()
    assert data["mip_orchestration_requirements_defined"] is True


def test_runtime_followup_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text
    assert "_weekly_spend_totals()" in text
    data = _load_summary()
    assert data["runtime_followup_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001"
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text


def test_return_to_lane_a_after() -> None:
    data = _load_summary()
    assert (
        data["return_to_lane_a_after"]
        == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
    )
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001" in text


def test_required_flags_true() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_final_verdict_matches_scope() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "spend_roi_readiness_contract_defined_no_runtime_or_claim_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-GEOX-FINAL-TEST-RESULTS-SPEND-ROI-READINESS-CONTRACT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "GEOX-FINAL-TEST-RESULTS-SPEND-AND-ROI-READINESS-CONTRACT-001" in lane_ids
    assert "LANE-B-FINAL-TRUSTED-READOUT-SPEND-ROI-READINESS" in lane_ids


def test_roadmap_references_lane_b() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "Lane B" in text
    assert "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001" in text
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "GEOX-FINAL-TEST-RESULTS-SPEND-AND-ROI-READINESS-CONTRACT-001" in text
