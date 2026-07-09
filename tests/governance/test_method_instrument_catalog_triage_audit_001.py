"""Governance tests for METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_TRIAGE_IDENTITIES = (
    "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review",
    "geo.tbrridge.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only",
    "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review",
    "geo.scm.placebo.single_treated.delta_mu.placebo_tail.diagnostic_only",
    "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only",
    "geo.did.bootstrap.panel_delta.delta_mu.bootstrap_interval.diagnostic_only",
)

_CLASSIFICATION_TIERS = (
    "PROMOTION_CANDIDATE",
    "RESTRICTED_REVIEW",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_SANDBOX",
    "BLOCKED",
    "DEPRECATED",
)

_EVIDENCE_INHERITANCE_MARKERS = (
    "Evidence inheritance matrix",
    "Estimator-level reusable",
    "Inference-specific required",
    "Instrument-specific required",
    "Inherited allowed",
    "Inherited prohibited",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "method_unblocked",
    "estimator_family_promoted",
    "global_tbrridge_promotion_authorized",
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
    "method_instrument_catalog_triage_audit_completed",
    "classification_policy_applied",
    "instrument_triage_matrix_defined",
    "evidence_inheritance_matrix_defined",
    "roadmap_correction_defined",
    "exact_instrument_id_required_for_future_promotion",
    "estimator_family_global_promotion_blocked",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001" in text
    assert (
        "method_instrument_catalog_triaged_no_method_promotion_or_catalog_unblock"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001"
    assert data["status"] == "completed"
    assert data["base_commit"] == "0188b04"


def test_classification_policy_applied() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Classification policy applied" in text
    assert "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001" in text
    data = _load_summary()
    assert data["classification_policy_applied"] is True


def test_instrument_triage_matrix_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Triage classification matrix" in text
    for identity in _TRIAGE_IDENTITIES:
        assert identity in text
    for tier in _CLASSIFICATION_TIERS:
        assert tier in text
    data = _load_summary()
    assert data["instrument_triage_matrix_defined"] is True


def test_evidence_inheritance_matrix_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for marker in _EVIDENCE_INHERITANCE_MARKERS:
        assert marker in text
    assert "No cross-inference-family promotion" in text
    data = _load_summary()
    assert data["evidence_inheritance_matrix_defined"] is True


def test_exact_instrument_id_required_for_future_promotion() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Exact instrument ID required" in text
    assert "exact instrument id" in text.lower()
    data = _load_summary()
    assert data["exact_instrument_id_required_for_future_promotion"] is True


def test_estimator_family_global_promotion_blocked() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "estimator-family promotion" in text.lower()
    assert "global estimator-family promotion" in text.lower()
    data = _load_summary()
    assert data["estimator_family_global_promotion_blocked"] is True


def test_tbrridge_lane_corrected_to_exact_instrument_scope() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRidge lane correction" in text
    assert "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review" in text
    assert "TBRRidge promotion evidence battery" in text or "applies to" in text.lower()


def test_roadmap_correction_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Roadmap changes required" in text
    data = _load_summary()
    assert data["roadmap_correction_defined"] is True


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
        == "method_instrument_catalog_triaged_no_method_promotion_or_catalog_unblock"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-METHOD-INSTRUMENT-CATALOG-TRIAGE-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "METHOD-INSTRUMENT-CATALOG-TRIAGE-AUDIT-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-INSTRUMENT-CATALOG-TRIAGE-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001"
