"""Governance tests for ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "instrument_promoted",
    "estimator_family_promoted",
    "catalog_unblocked",
    "production_catalog_unblocked",
    "production_authorization_granted",
    "production_readout_authorized",
    "uncertainty_authorized",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "inference_implemented",
    "estimator_implemented",
    "simulations_implemented",
    "llm_decisioning_authorized",
)

_VERDICT_FLAGS = (
    "roadmap_scope_aligned",
    "roadmap_milestones_followable",
    "estimator_family_promotion_blocked",
    "exact_instrument_scope_required",
    "tbrridge_kfold_lane_current",
    "pairing_reason_codes_required",
    "pairing_value_prioritization_reflected",
    "no_new_pursue_now_pairing",
    "augsynth_jk_save_for_later",
    "production_compatibility_deferred",
    "geometry_taxonomy_optional_followup",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001" in text
    assert (
        "roadmap_instrument_scope_and_milestones_aligned_no_method_promotion_or_catalog_unblock"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001"
    assert data["status"] == "completed"
    assert data["base_commit"] == "1fab4ad"


def test_roadmap_scope_aligned() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Roadmap scope verdict" in text
    assert "roadmap_scope_aligned`: true" in text.replace("**", "")
    data = _load_summary()
    assert data["roadmap_scope_aligned"] is True


def test_roadmap_milestones_followable() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Milestone followability verdict" in text
    assert "roadmap_milestones_followable`: true" in text.replace("**", "")
    data = _load_summary()
    assert data["roadmap_milestones_followable"] is True


def test_estimator_family_promotion_blocked() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Promote instruments, not estimator families" in text
    data = _load_summary()
    assert data["estimator_family_promotion_blocked"] is True


def test_exact_instrument_scope_required() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "exact instrument identity" in text.lower()
    data = _load_summary()
    assert data["exact_instrument_scope_required"] is True


def test_tbrridge_kfold_lane_current() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review" in text
    data = _load_summary()
    assert data["tbrridge_kfold_lane_current"] is True


def test_pairing_reason_codes_required() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "reason codes" in text.lower()
    data = _load_summary()
    assert data["pairing_reason_codes_required"] is True


def test_pairing_value_prioritization_reflected() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001" in text
    assert "AugSynth × KFold/Conformal" in text or "AugSynth KFold" in text
    data = _load_summary()
    assert data["pairing_value_prioritization_reflected"] is True


def test_no_new_pursue_now_pairing() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "no new PURSUE_NOW" in text.lower() or "No new PURSUE_NOW" in text
    data = _load_summary()
    assert data["no_new_pursue_now_pairing"] is True


def test_augsynth_jk_save_for_later() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001" in text
    assert "save-for-later" in text.lower()
    data = _load_summary()
    assert data["augsynth_jk_save_for_later"] is True


def test_production_compatibility_deferred() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001" in text
    assert "deferred" in text.lower()
    data = _load_summary()
    assert data["production_compatibility_deferred"] is True


def test_geometry_taxonomy_optional_followup() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001" in text
    data = _load_summary()
    assert data["geometry_taxonomy_optional_followup"] is True
    roadmap = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001" in roadmap


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001"
    assert data["next_artifact_confirmed"] == "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_verdict_flags_true() -> None:
    data = _load_summary()
    for flag in _VERDICT_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "roadmap_instrument_scope_and_milestones_aligned_no_method_promotion_or_catalog_unblock"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-ROADMAP-INSTRUMENT-SCOPE-ALIGNMENT-CHECK-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "ROADMAP-INSTRUMENT-SCOPE-ALIGNMENT-CHECK-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-ROADMAP-INSTRUMENT-SCOPE-ALIGNMENT-CHECK-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001"
