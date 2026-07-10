"""Governance tests for AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001_summary.json"
)
_RUNTIME = _REPO / "panel_exp/validation/augsynth_jackknife_review_decision_runtime_001.py"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_VERDICT = (
    "augsynth_jackknife_review_decision_runtime_implemented_no_promotion_no_claim_authorization"
)
_NEXT_AUDIT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001"
_LANE_A_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001"

_ALLOWED_TRUE_FLAGS = ("runtime_implemented", "augsynth_decision_runtime_implemented")

_FORBIDDEN_TRUE_FLAGS = (
    "generic_runtime_changed",
    "generic_adapter_profile_for_augsynth_implemented",
    "method_promoted",
    "instrument_promoted",
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
)

_REQUIRED_TRUE_FLAGS = (
    "review_decision_runtime_implemented",
    "deterministic_decision_mapping_implemented",
    "decision_precedence_implemented",
    "positive_decision_semantics_preserved",
    "alias_research_only_rejects_implemented",
    "allowed_next_actions_emitted",
    "prohibited_actions_emitted",
    "fixed_non_authorization_statuses_emitted",
    "evidence_quality_boundary_preserved",
    "generic_framework_compatibility_preserved",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()


def test_import_api_works() -> None:
    mod = importlib.import_module(
        "panel_exp.validation.augsynth_jackknife_review_decision_runtime_001"
    )
    assert hasattr(mod, "AugSynthJackknifeReviewDecisionInput")
    assert hasattr(mod, "AugSynthJackknifeReviewDecision")
    assert hasattr(mod, "AugSynthJackknifeReviewDecisionStatus")
    assert hasattr(mod, "decide_augsynth_jackknife_review")


def test_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_jackknife_review_decision_runtime"


def test_deterministic_mapping_and_precedence() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "Decision precedence" in text
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    data = _load_summary()
    assert data["deterministic_decision_mapping_implemented"] is True
    assert data["decision_precedence_implemented"] is True


def test_positive_decision_semantics_preserved() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "restricted-review governance input" in text.lower()
    assert _load_summary()["positive_decision_semantics_preserved"] is True


def test_alias_research_only_rejects_implemented() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION" in text
    assert "REJECT_FOR_ALIAS_SUBSTITUTION" in text
    assert _ALIAS in text
    assert _load_summary()["alias_research_only_rejects_implemented"] is True


def test_allowed_prohibited_actions_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "continue_augsynth_restricted_review_diagnostics" in text
    assert "augsynth_promotion" in text
    data = _load_summary()
    assert data["allowed_next_actions_emitted"] is True
    assert data["prohibited_actions_emitted"] is True


def test_fixed_non_authorization_statuses_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_THIS_DECISION" in text
    assert "NOT_REGISTERED_BY_THIS_DECISION" in text
    assert _load_summary()["fixed_non_authorization_statuses_emitted"] is True


def test_evidence_quality_boundary_preserved() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "score evidence quality" in text.lower()
    assert _load_summary()["evidence_quality_boundary_preserved"] is True


def test_generic_framework_compatibility_preserved() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "APPROVE_REVIEW_CONTINUATION" in text
    assert "generic runtime" in text.lower()
    assert _load_summary()["generic_framework_compatibility_preserved"] is True


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
    assert data["recommended_next_artifact"] == _NEXT_AUDIT
    assert _NEXT_AUDIT in _RUNTIME_DOC.read_text(encoding="utf-8")


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert "AUGSYNTH-JACKKNIFE-REVIEW-DECISION-RUNTIME-001" in _MIP_AUDIT_REGISTRY.read_text(
        encoding="utf-8"
    )


def test_method_soundness_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001" in _METHOD_SOUNDNESS.read_text(
        encoding="utf-8"
    )


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
