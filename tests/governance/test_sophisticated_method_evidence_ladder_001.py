"""Tests for SOPHISTICATED_METHOD_EVIDENCE_LADDER_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_LADDER = _REPO / "docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_LADDER_STAGES = (
    "STAGE_0_BLOCKED_OR_UNCHARACTERIZED",
    "STAGE_1_RESEARCH_SANDBOX",
    "STAGE_2_DIAGNOSTIC_ONLY",
    "STAGE_3_POINT_ESTIMATE_ONLY",
    "STAGE_4_UNCERTAINTY_CANDIDATE",
    "STAGE_5_RESTRICTED_REVIEW_CANDIDATE",
    "STAGE_6_PRODUCTION_COMPATIBILITY_CANDIDATE",
)

_METHOD_SECTIONS = (
    "DID_BOOTSTRAP",
    "TBRRidge",
    "TBR aggregate",
    "multi-cell pooled",
    "AugSynth JK",
    "SCM multi-treated",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "method_unblocked",
    "production_catalog_unblocked",
    "production_authorization_granted",
    "production_readout_authorized",
    "trusted_business_recommendation_authorized",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "mmm_runtime_calls_implemented",
    "mmm_calibration_authorized",
    "llm_decisioning_authorized",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_ladder_doc_exists() -> None:
    assert _LADDER.exists()
    text = _LADDER.read_text(encoding="utf-8")
    assert "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001" in text
    assert "sophisticated_methods_evidence_ladder_defined_no_method_promotion" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_stage_taxonomy_present() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    for stage in _LADDER_STAGES:
        assert stage in text


def test_did_bootstrap_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "DID_BOOTSTRAP" in text
    assert "parallel trends" in text.lower() or "parallel-trends" in text.lower()
    assert "bootstrap" in text.lower()


def test_tbrridge_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "TBRRidge" in text
    assert "BRB" in text
    assert "KFold" in text or "Kfold" in text


def test_tbr_aggregate_pooled_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "TBR aggregate" in text or "aggregate / pooled" in text
    assert "heterogeneity" in text.lower()


def test_multicell_pooled_global_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "multi-cell" in text.lower() or "multicell" in text.lower()
    assert "multiplicity" in text.lower()


def test_augsynth_jk_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "AugSynth" in text
    assert "jackknife" in text.lower() or "JK" in text


def test_scm_multitreated_section_exists() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    assert "SCM multi-treated" in text or "multi-treated production" in text


def test_false_confidence_risks_documented() -> None:
    data = _load_summary()
    assert data["false_confidence_risks_documented"] is True
    text = _LADDER.read_text(encoding="utf-8")
    assert "false-confidence" in text.lower() or "False-confidence" in text


def test_production_compatibility_runtime_deferred() -> None:
    data = _load_summary()
    assert data["production_compatibility_runtime_deferred"] is True
    assert data["deferred_artifact"] == "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
    text = _LADDER.read_text(encoding="utf-8")
    assert "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001" in text


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert data["final_verdict"] == "sophisticated_methods_evidence_ladder_defined_no_method_promotion"
    assert data["scope"] == data["final_verdict"]


def test_forbidden_promotion_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_capability_flags_true() -> None:
    data = _load_summary()
    assert data["ladder_stages_defined"] is True
    assert data["sophisticated_method_inventory_completed"] is True
    assert data["next_smallest_artifacts_recommended"] is True


def test_recommended_next_artifact_present() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001"
    assert data["alternative_next_artifact"] == "PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001"


def test_method_sections_mentioned_in_doc() -> None:
    text = _LADDER.read_text(encoding="utf-8")
    for section in _METHOD_SECTIONS:
        assert section in text or section.replace(" ", " / ") in text


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-SOPHISTICATED-METHOD-EVIDENCE-LADDER-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "SOPHISTICATED-METHOD-EVIDENCE-LADDER-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-SOPHISTICATED-METHOD-EVIDENCE-LADDER-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001"
