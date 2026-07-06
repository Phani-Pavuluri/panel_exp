"""Tests for METHOD_PROMOTION_CANDIDATE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_CANDIDATE_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_REQUIRED_CANDIDATES = (
    "SCM_UnitJackKnife",
    "SCM + Placebo",
    "DID_BOOTSTRAP",
    "per-cell marginal",
    "AugSynth",
    "TBRRidge",
    "BRB",
    "Kfold",
    "pooled",
    "multi-cell",
)

_RANK_TAXONOMY = (
    "RANK_0_BLOCKED_DO_NOT_ADVANCE",
    "RANK_1_DEFER_UNTIL_METHOD_EVIDENCE",
    "RANK_2_EVIDENCE_BUILDING_CANDIDATE",
    "RANK_3_RESTRICTED_REVIEW_CANDIDATE",
    "RANK_4_PRODUCTION_COMPATIBILITY_REVIEW_CANDIDATE",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "method_unblocked",
    "production_catalog_unblocked",
    "production_authorization_granted",
    "production_readout_authorized",
    "estimator_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_CANDIDATE_AUDIT_001" in text
    assert "method_promotion_candidates_ranked_no_method_promotion_or_catalog_change" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_CANDIDATE_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_candidate_ranking_taxonomy_present() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for rank in _RANK_TAXONOMY:
        assert rank in text


def test_required_candidate_families_mentioned() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for candidate in _REQUIRED_CANDIDATES:
        assert candidate in text or candidate.replace("_", " ") in text


def test_production_compatibility_runtime_deferred() -> None:
    data = _load_summary()
    assert data["production_compatibility_runtime_deferred"] is True
    assert data["deferred_artifact"] == "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001" in text
    assert "deferred" in text.lower() or "defer" in text.lower()


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert data["final_verdict"] == "method_promotion_candidates_ranked_no_method_promotion_or_catalog_change"
    assert data["scope"] == data["final_verdict"]


def test_forbidden_promotion_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_capability_flags_true() -> None:
    data = _load_summary()
    assert data["candidate_inventory_completed"] is True
    assert data["candidate_rankings_defined"] is True
    assert data["candidate_blockers_documented"] is True
    assert data["next_smallest_artifacts_recommended"] is True


def test_recommended_next_artifact_present() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001"
    assert data["alternative_next_artifact"] == "PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001"


def test_no_rank_4_candidates_conservative() -> None:
    data = _load_summary()
    assert data["rank_4_production_compatibility_review"] == 0


def test_governance_registry_references_audit() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-METHOD-PROMOTION-CANDIDATE-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "METHOD-PROMOTION-CANDIDATE-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-PROMOTION-CANDIDATE-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "METHOD_PROMOTION_CANDIDATE_AUDIT_001"


def test_governance_defers_compatibility_runtime_as_next_immediate() -> None:
    reg = _load_registry()
    compat_lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PRODUCTION-COMPATIBILITY-PROMOTION-REVIEW-CONTRACT-001"
    )
    assert compat_lane["next_artifact"] != "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
    assert compat_lane["next_artifact"] == "SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001"
    audit_inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-PROMOTION-CANDIDATE-AUDIT-001"
    )
    assert audit_inv["evidence"]["production_compatibility_runtime_deferred"] is True
