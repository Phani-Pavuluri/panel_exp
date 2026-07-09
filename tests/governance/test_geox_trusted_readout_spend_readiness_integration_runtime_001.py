"""Governance tests for GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = (
    _REPO / "docs/track_d/GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001.md"
)
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001_summary.json"
)
_RUNTIME = (
    _REPO
    / "panel_exp/validation/trusted_readout_spend_readiness_integration_runtime_001.py"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_FORBIDDEN_TRUE_FLAGS = (
    "spend_delta_recomputed",
    "cost_per_incremental_kpi_computed",
    "roi_roas_computed",
    "roi_calculator_runtime_created",
    "spend_ingestion_system_created",
    "final_results_module_created",
    "claim_authorization_duplicated",
    "roi_claim_authorized",
    "roas_claim_authorized",
    "business_lift_claim_authorized",
    "decision_recommendation_authorized",
    "production_readout_authorized",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "mip_orchestration_implemented",
    "dataset_loading_implemented",
)

_REQUIRED_TRUE_FLAGS = (
    "trusted_readout_spend_readiness_integration_completed",
    "post_test_spend_handoff_consumed",
    "trusted_readout_extension_fields_added",
    "spend_readiness_summary_integrated",
    "post_test_spend_evidence_integrated",
    "blocked_efficiency_metrics_integrated",
    "spend_lineage_integrated",
    "spend_warnings_integrated",
    "roi_claim_authorization_delegated",
    "mip_expected_output_fields_supported",
    "kpi_readout_not_blocked_by_missing_spend",
    "runtime_implemented",
)

_VERDICT = "trusted_readout_spend_readiness_integrated_no_roi_calculator_or_claim_authorization"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001" in text
    assert _VERDICT in text


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()
    text = _RUNTIME.read_text(encoding="utf-8")
    assert "integrate_spend_readiness_into_trusted_readout" in text
    assert "generate_trusted_readout_report_with_spend_readiness" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "geox_trusted_readout_spend_readiness_integration_runtime"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001"


def test_return_to_lane_a_after() -> None:
    data = _load_summary()
    assert data["return_to_lane_a_after"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"


def test_roadmap_updated() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001" in text
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001" in text


def test_mip_audit_registry_updated() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "GEOX-TRUSTED-READOUT-SPEND-READINESS-INTEGRATION-RUNTIME-001" in text


def test_method_soundness_updated() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001" in text


def test_open_investigations_lane_b_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_b = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-B-FINAL-TRUSTED-READOUT-SPEND-ROI-READINESS"
    )
    assert lane_b["next_artifact"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
