"""Governance tests for METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_POLICY = _REPO / "docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_IDENTITY_FIELDS = (
    "modality",
    "estimator_family",
    "inference_family",
    "geometry",
    "estimand",
    "interval_semantics",
    "metric_scope",
    "treatment_contrast",
    "allowed_surface",
)

_CLASSIFICATION_TIERS = (
    "PROMOTION_CANDIDATE",
    "RESTRICTED_REVIEW",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_SANDBOX",
    "BLOCKED",
    "DEPRECATED",
)

_EXAMPLE_IDENTITIES = (
    "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review",
    "geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only",
    "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review",
    "geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only",
    "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only",
    "geo.did.bootstrap.panel_delta.bootstrap_interval.diagnostic_only",
)

_EVIDENCE_INHERITANCE_RULES = (
    "Evidence from one inference family cannot promote another inference family",
    "Evidence from one geometry cannot authorize another geometry",
    "Evidence from diagnostic surfaces cannot authorize production surfaces",
    "Estimator-family names cannot be promoted globally",
    "Promotion applies only to exact cataloged instrument identities",
    "Unsupported surfaces are blocked by default",
    "All evidence inheritance must be explicit and recorded",
)

_ALLOWED_SURFACES_BY_TIER = (
    "Allowed/prohibited surfaces by tier",
    "RESTRICTED_REVIEW",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_SANDBOX",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "method_unblocked",
    "estimator_family_promoted",
    "global_tbrridge_promotion_authorized",
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
    "method_instrument_classification_policy_defined",
    "governed_instrument_identity_defined",
    "classification_tiers_defined",
    "evidence_inheritance_rules_defined",
    "estimator_family_promotion_prohibited",
    "instrument_level_promotion_required",
    "pairing_specific_validation_required",
    "catalog_triage_audit_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_policy_doc_exists() -> None:
    assert _POLICY.exists()
    text = _POLICY.read_text(encoding="utf-8")
    assert "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001" in text
    assert (
        "method_instrument_classification_policy_defined_no_method_promotion_or_catalog_unblock"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001"
    assert data["status"] == "completed"


def test_governed_instrument_identity_documented() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "Governed instrument identity" in text
    for field in _IDENTITY_FIELDS:
        assert field in text
    for identity in _EXAMPLE_IDENTITIES:
        assert identity in text
    data = _load_summary()
    assert data["governed_instrument_identity_defined"] is True


def test_classification_tiers_documented() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "Classification tiers" in text
    for tier in _CLASSIFICATION_TIERS:
        assert tier in text
    data = _load_summary()
    assert data["classification_tiers_defined"] is True


def test_estimator_family_promotion_prohibited() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "estimator-family promotion is prohibited" in text.lower()
    assert "Promote instruments, not estimator families" in text
    data = _load_summary()
    assert data["estimator_family_promotion_prohibited"] is True


def test_instrument_level_promotion_required() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "Promotion applies only to exact cataloged instrument identities" in text
    data = _load_summary()
    assert data["instrument_level_promotion_required"] is True


def test_evidence_inheritance_rules_documented() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "Evidence inheritance rules" in text
    for rule in _EVIDENCE_INHERITANCE_RULES:
        assert rule in text
    data = _load_summary()
    assert data["evidence_inheritance_rules_defined"] is True


def test_pairing_specific_validation_required() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    assert "Pairing-specific validation requirements" in text
    assert "TBRRidge + KFold" in text
    data = _load_summary()
    assert data["pairing_specific_validation_required"] is True


def test_allowed_prohibited_surfaces_documented() -> None:
    text = _POLICY.read_text(encoding="utf-8")
    for marker in _ALLOWED_SURFACES_BY_TIER:
        assert marker in text


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001"
    text = _POLICY.read_text(encoding="utf-8")
    assert "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001" in text


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
        == "method_instrument_classification_policy_defined_no_method_promotion_or_catalog_unblock"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-METHOD-INSTRUMENT-CLASSIFICATION-POLICY-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "METHOD-INSTRUMENT-CLASSIFICATION-POLICY-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-INSTRUMENT-CLASSIFICATION-POLICY-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001"
