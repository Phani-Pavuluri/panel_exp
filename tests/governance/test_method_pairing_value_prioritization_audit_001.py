"""Governance tests for METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_AUGSYNTH_PAIRINGS = (
    "AugSynth × Bootstrap",
    "AugSynth × Placebo",
    "AugSynth × KFold",
)

_PRIORITY_BUCKETS = (
    "PURSUE_NOW",
    "SAVE_FOR_LATER",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_SANDBOX",
    "BLOCK",
    "NEEDS_IMPLEMENTATION_STATUS_CORRECTION",
    "NEEDS_SEPARATE_VALIDATION_PLAN",
)

_VALUE_FRAMEWORK_FIELDS = (
    "implementation_status",
    "unique_causal_value",
    "incremental_value_over_selected_instruments",
    "inference_assumption_risk",
    "validation_cost",
    "recommended_priority",
)

_FORBIDDEN_TRUE_FLAGS = (
    "pairing_promoted",
    "method_promoted",
    "method_unblocked",
    "estimator_family_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "uncertainty_authorized",
    "uncertainty_candidate_approved",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "interval_computed",
    "coverage_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "inference_implemented",
    "estimator_implemented",
    "simulations_implemented",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_POSITIVE_FLAGS = (
    "method_pairing_value_prioritization_audit_completed",
    "left_out_pairings_reviewed",
    "implementation_status_reviewed",
    "pairing_value_framework_defined",
    "prioritization_decisions_defined",
    "save_for_later_queue_defined",
    "roadmap_corrections_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001" in text
    assert (
        "method_pairing_value_prioritization_audited_no_pairing_promotion_or_inference_implementation"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001"
    assert data["status"] == "completed"
    assert data["base_commit"] == "ad2447c"


def test_left_out_pairings_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Pairings reviewed" in text
    assert "left-out" in text.lower() or "left out" in text.lower()
    data = _load_summary()
    assert data["left_out_pairings_reviewed"] is True


def test_implementation_status_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Implementation vs governance distinction" in text
    assert "IMPLEMENTED_BUT_NOT_GOVERNED" in text
    data = _load_summary()
    assert data["implementation_status_reviewed"] is True


def test_pairing_value_framework_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Pairing value scoring framework" in text
    for field in _VALUE_FRAMEWORK_FIELDS:
        assert field in text
    for bucket in _PRIORITY_BUCKETS:
        assert bucket in text
    data = _load_summary()
    assert data["pairing_value_framework_defined"] is True


def test_prioritization_decisions_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Pairing prioritization decisions" in text
    assert "implemented is not enough" in text.lower()
    data = _load_summary()
    assert data["prioritization_decisions_defined"] is True


def test_augsynth_bootstrap_placebo_kfold_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "AugSynth inference pairing review" in text
    for pairing in _AUGSYNTH_PAIRINGS:
        assert pairing in text


def test_save_for_later_queue_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Save-for-later queue" in text
    assert "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001" in text
    data = _load_summary()
    assert data["save_for_later_queue_defined"] is True


def test_roadmap_corrections_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Roadmap corrections required" in text
    assert "Correct coverage audit classifications" in text
    data = _load_summary()
    assert data["roadmap_corrections_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "method_pairing_value_prioritization_audited_no_pairing_promotion_or_inference_implementation"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-METHOD-PAIRING-VALUE-PRIORITIZATION-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "METHOD-PAIRING-VALUE-PRIORITIZATION-AUDIT-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-PAIRING-VALUE-PRIORITIZATION-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001"
