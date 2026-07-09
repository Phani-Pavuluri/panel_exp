"""Governance tests for GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "cost_per_incremental_kpi_computed",
    "roas_computed",
    "profit_roi_computed",
    "roi_calculator_runtime_created",
    "spend_delta_recomputed",
    "spend_ingestion_system_created",
    "final_results_module_created",
    "claim_authorization_duplicated",
    "roi_claim_authorized",
    "roas_claim_authorized",
    "business_recommendation_authorized",
    "decision_recommendation_authorized",
    "production_readout_authorized",
    "mip_orchestration_implemented",
    "estimator_implemented",
    "inference_implemented",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
)

_REQUIRED_TRUE_FLAGS = (
    "efficiency_metric_readiness_mapper_contract_completed",
    "cost_per_readiness_defined",
    "roas_readiness_defined",
    "profit_roi_readiness_defined",
    "numeric_readiness_vs_claim_authorization_defined",
    "trusted_readout_representation_defined",
    "mip_user_interpretation_defined",
    "future_runtime_defined",
    "lane_b_minimum_semantic_chain_completed",
)

_VERDICT = "efficiency_metric_readiness_mapping_contract_defined_no_runtime_or_claim_authorization"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "geox_efficiency_metric_readiness_mapper_contract"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_cost_per_readiness_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "cost_per_incremental_kpi" in text
    assert "BLOCKED_MISSING_SPEND_DELTA_OR_DELTA_MU" in text
    assert _load_summary()["cost_per_readiness_defined"] is True


def test_roas_readiness_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "ROAS" in text
    assert "BLOCKED_MISSING_REVENUE_OR_SPEND" in text
    assert _load_summary()["roas_readiness_defined"] is True


def test_profit_roi_readiness_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "profit_ROI" in text
    assert "BLOCKED_MISSING_PROFIT_OR_SPEND" in text
    assert _load_summary()["profit_roi_readiness_defined"] is True


def test_numeric_readiness_vs_claim_authorization_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Numeric readiness" in text or "numeric readiness" in text
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert "never implies" in text.lower() or "never **implies**" in text
    assert _load_summary()["numeric_readiness_vs_claim_authorization_defined"] is True


def test_trusted_readout_representation_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "efficiency_metric_readiness" in text
    assert "blocked_efficiency_metrics" in text
    assert "diagnostic_efficiency_metrics" in text
    assert _load_summary()["trusted_readout_representation_defined"] is True


def test_mip_user_interpretation_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MIP" in text
    assert "DecisionSurface" in text or "RecommendationContract" in text
    assert _load_summary()["mip_user_interpretation_defined"] is True


def test_future_runtime_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_RUNTIME_001" in text
    assert _load_summary()["future_runtime_defined"] is True


def test_lane_b_minimum_semantic_chain_completed() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "minimum semantic chain" in text.lower()
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text
    assert "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001" in text
    data = _load_summary()
    assert data["lane_b_minimum_semantic_chain_completed"] is True
    assert data["lane_b_status_after_this_artifact"] == "minimum_semantic_chain_completed_return_to_lane_a"


def test_recommended_next_artifact_is_lane_a() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001" in text
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "GEOX-EFFICIENCY-METRIC-READINESS-MAPPER-CONTRACT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001" in text


def test_open_investigations_lane_b_closure() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_b = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-B-FINAL-TRUSTED-READOUT-SPEND-ROI-READINESS"
    )
    assert lane_b["next_artifact"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
