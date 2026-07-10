"""Governance tests for METHOD_PROMOTION_GENERIC_RUNTIME_001."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_MODULE = _REPO / "panel_exp/validation/method_promotion_generic_runtime_001.py"
_DOC = _REPO / "docs/track_d/METHOD_PROMOTION_GENERIC_RUNTIME_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_VERDICT = "generic_method_promotion_adapter_runtime_implemented_no_promotion_no_claim_authorization"
_NEXT_RUNTIME = "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001"
_LANE_A_NEXT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001"

_ALLOWED_TRUE_FLAGS = (
    "runtime_implemented",
    "generic_runtime_implemented",
    "generic_dataclasses_implemented",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "instrument_promoted",
    "tbrridge_promoted",
    "scm_promoted",
    "augsynth_promoted",
    "did_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "confidence_interval_claim_authorized",
    "p_value_claim_authorized",
    "significance_claim_authorized",
    "statistical_power_claim_authorized",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "roi_roas_claim_authorized",
    "decision_recommendation_authorized",
    "production_readout_authorized",
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "raw_evidence_quality_scored",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
    "augsynth_did_support_implemented",
)

_REQUIRED_TRUE_FLAGS = (
    "generic_runtime_implemented",
    "adapter_runtime_only",
    "supported_profiles_limited_to_completed_applications",
    "tbrridge_profile_supported",
    "scm_null_monitor_profile_supported",
    "packet_summary_adapter_implemented",
    "decision_summary_adapter_implemented",
    "governance_summary_builder_implemented",
    "instrument_specific_runtimes_source_of_truth",
    "status_mapping_implemented",
    "boundary_preservation_implemented",
    "prohibited_action_non_weakening_implemented",
    "alias_substitution_blocked",
    "unmapped_status_blocked",
    "missing_boundary_status_blocked",
    "missing_evidence_preserved",
    "blockers_preserved",
    "warnings_lineage_preserved",
    "mip_facing_summary_boundary_preserved",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_module_exists() -> None:
    assert _RUNTIME_MODULE.exists()


def test_import_api_works() -> None:
    mod = importlib.import_module("panel_exp.validation.method_promotion_generic_runtime_001")
    assert hasattr(mod, "MethodPromotionEvidencePacketSummary")
    assert hasattr(mod, "MethodPromotionReviewDecisionSummary")
    assert hasattr(mod, "MethodPromotionGovernanceSummary")
    assert hasattr(mod, "MethodPromotionInstrumentAdapterProfile")
    assert hasattr(mod, "MethodPromotionGenericAdapterStatus")
    assert hasattr(mod, "adapt_method_promotion_packet_to_generic_summary")
    assert hasattr(mod, "adapt_method_promotion_decision_to_generic_summary")
    assert hasattr(mod, "build_method_promotion_governance_summary")


def test_doc_exists() -> None:
    assert _DOC.exists()
    text = _DOC.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_GENERIC_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_generic_runtime"


def test_generic_runtime_implemented() -> None:
    assert _load_summary()["generic_runtime_implemented"] is True
    assert "adapt_method_promotion_packet_to_generic_summary" in _DOC.read_text(encoding="utf-8")


def test_adapter_runtime_only() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "adapter" in text.lower()
    assert _load_summary()["adapter_runtime_only"] is True


def test_supported_profiles_limited_to_completed_applications() -> None:
    data = _load_summary()
    assert data["supported_profiles_limited_to_completed_applications"] is True
    text = _DOC.read_text(encoding="utf-8")
    assert "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review" in text
    assert "geo.scm.jackknife.single_cell.delta_mu.null_monitor" in text


def test_tbrridge_and_scm_profiles_supported() -> None:
    data = _load_summary()
    assert data["tbrridge_profile_supported"] is True
    assert data["scm_null_monitor_profile_supported"] is True


def test_packet_decision_governance_adapters_implemented() -> None:
    data = _load_summary()
    assert data["packet_summary_adapter_implemented"] is True
    assert data["decision_summary_adapter_implemented"] is True
    assert data["governance_summary_builder_implemented"] is True


def test_source_of_truth_rule_documented_and_enforced() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "source of truth" in text.lower()
    assert _load_summary()["instrument_specific_runtimes_source_of_truth"] is True


def test_status_mapping_implemented() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_REVIEW_INPUT" in text
    assert _load_summary()["status_mapping_implemented"] is True


def test_boundary_preservation_implemented() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "claim_authorization_status" in text
    assert _load_summary()["boundary_preservation_implemented"] is True


def test_prohibited_action_non_weakening_implemented() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "prohibited" in text.lower()
    assert _load_summary()["prohibited_action_non_weakening_implemented"] is True


def test_alias_substitution_blocked() -> None:
    assert _load_summary()["alias_substitution_blocked"] is True
    assert "alias" in _DOC.read_text(encoding="utf-8").lower()


def test_unmapped_status_blocked() -> None:
    assert _load_summary()["unmapped_status_blocked"] is True


def test_missing_boundary_status_blocked() -> None:
    assert _load_summary()["missing_boundary_status_blocked"] is True


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag
    for flag in _ALLOWED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_RUNTIME


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-GENERIC-RUNTIME-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
