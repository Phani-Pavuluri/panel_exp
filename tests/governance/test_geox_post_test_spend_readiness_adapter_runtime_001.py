"""Governance tests for GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001_summary.json"
)
_RUNTIME = _REPO / "panel_exp/validation/post_test_spend_readiness_adapter_runtime_001.py"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_FORBIDDEN_TRUE_FLAGS = (
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
    "estimator_implemented",
    "inference_implemented",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_REQUIRED_TRUE_FLAGS = (
    "post_test_spend_readiness_adapter_completed",
    "post_test_window_filter_implemented",
    "spend_assignment_join_implemented",
    "actual_treatment_spend_implemented",
    "counterfactual_or_bau_spend_supported",
    "spend_delta_readiness_implemented",
    "readiness_blockers_implemented",
    "warnings_implemented",
    "existing_spend_primitives_reused_or_referenced",
    "planning_required_spend_delta_not_reused_as_observed_spend_delta",
    "trusted_readout_consumable_output_defined",
    "runtime_implemented",
)

_VERDICT = "post_test_spend_readiness_adapter_runtime_completed_no_claim_authorization_or_roi_calculator"


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text
    assert _VERDICT in text


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()
    text = _RUNTIME.read_text(encoding="utf-8")
    assert "build_post_test_spend_evidence" in text
    assert "build_trusted_readout_spend_handoff" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "geox_post_test_spend_readiness_adapter_runtime"


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
    assert data["recommended_next_artifact"] == "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001"


def test_return_to_lane_a_after() -> None:
    data = _load_summary()
    assert data["return_to_lane_a_after"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"


def test_lane_b_closure_documented_in_roadmap() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001" in text


def test_mip_audit_registry_updated() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "GEOX-POST-TEST-SPEND-READINESS-ADAPTER-RUNTIME-001" in text


def test_method_soundness_updated() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in text


def test_open_investigations_lane_b_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_b = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-B-FINAL-TRUSTED-READOUT-SPEND-ROI-READINESS"
    )
    assert lane_b["next_artifact"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
