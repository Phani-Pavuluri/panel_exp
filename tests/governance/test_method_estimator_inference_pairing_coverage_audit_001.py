"""Governance tests for METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_ESTIMATOR_FAMILIES = ("TBRRidge", "SCM", "AugSynth", "DID", "TBR")

_INFERENCE_FAMILIES = (
    "KFold",
    "Placebo",
    "Jackknife",
    "Bootstrap",
    "BRB",
    "Conformal",
    "point-only",
)

_MINIMUM_PAIRINGS = (
    "TBRRidge × KFold",
    "TBRRidge × Placebo",
    "TBRRidge × BRB",
    "SCM × Jackknife",
    "SCM × Placebo",
    "AugSynth × point-only",
    "AugSynth × Jackknife",
    "DID × Bootstrap",
)

_REASON_CODES = (
    "IMPLEMENTED",
    "CATALOGED",
    "GOVERNED",
    "RESTRICTED_REVIEW",
    "DIAGNOSTIC_ONLY",
    "RESEARCH_SANDBOX",
    "BLOCKED_BY_ASSUMPTION",
    "BLOCKED_BY_GEOMETRY",
    "NOT_NATURAL_FOR_ESTIMATOR",
    "REDUNDANT_WITH_EXISTING_INSTRUMENT",
    "NOT_IMPLEMENTED",
    "NOT_DOCUMENTED",
    "NOT_PRIORITIZED",
    "REQUIRES_SEPARATE_VALIDATION",
    "FUTURE_CANDIDATE",
    "DEPRECATED",
    "NOT_IN_SCOPE",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "method_unblocked",
    "estimator_family_promoted",
    "global_tbrridge_promotion_authorized",
    "instrument_promoted",
    "pairing_promoted",
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
    "estimator_inference_pairing_coverage_audit_completed",
    "estimator_families_reviewed",
    "inference_families_reviewed",
    "pairing_coverage_matrix_defined",
    "missing_pairing_reason_codes_defined",
    "evidence_inheritance_implications_defined",
    "future_pairing_cataloging_required",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001" in text
    assert (
        "estimator_inference_pairing_coverage_audited_no_method_promotion_or_inference_implementation"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001"
    assert data["status"] == "completed"
    assert data["base_commit"] == "be15f48"


def test_estimator_families_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Estimator families reviewed" in text
    for family in _ESTIMATOR_FAMILIES:
        assert family in text
    data = _load_summary()
    assert data["estimator_families_reviewed"] is True


def test_inference_families_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Inference families reviewed" in text
    for family in _INFERENCE_FAMILIES:
        assert family in text
    data = _load_summary()
    assert data["inference_families_reviewed"] is True


def test_pairing_coverage_matrix_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Estimator × inference coverage matrix" in text
    for pairing in _MINIMUM_PAIRINGS:
        assert pairing in text
    data = _load_summary()
    assert data["pairing_coverage_matrix_defined"] is True


def test_missing_pairing_reason_codes_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Pairing status reason codes" in text
    assert "Missing pairings and why" in text
    assert "No accidental exclusion" in text
    for code in _REASON_CODES:
        assert code in text
    data = _load_summary()
    assert data["missing_pairing_reason_codes_defined"] is True


def test_evidence_inheritance_implications_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence inheritance implications" in text
    assert "KFold leakage" in text
    assert "Placebo tail calibration" in text
    assert "cannot validate" in text.lower()
    data = _load_summary()
    assert data["evidence_inheritance_implications_defined"] is True


def test_future_pairing_cataloging_required() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "must enter through cataloging and classification before validation" in text.lower()
    data = _load_summary()
    assert data["future_pairing_cataloging_required"] is True


def test_no_global_estimator_family_promotion() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Promote instruments, not estimator families" in text
    assert "No global estimator-family promotion" in text
    data = _load_summary()
    assert data["estimator_family_promoted"] is False
    assert data["global_tbrridge_promotion_authorized"] is False


def test_relationship_to_classification_policy_and_triage() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Relationship to instrument classification policy" in text
    assert "Relationship to catalog triage audit" in text
    assert "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001" in text
    assert "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001" in text


def test_not_geometry_taxonomy_audit() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Why this is not a geometry taxonomy audit" in text
    assert "METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001" in text


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
        == "estimator_inference_pairing_coverage_audited_no_method_promotion_or_inference_implementation"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-METHOD-ESTIMATOR-INFERENCE-PAIRING-COVERAGE-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "METHOD-ESTIMATOR-INFERENCE-PAIRING-COVERAGE-AUDIT-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-METHOD-ESTIMATOR-INFERENCE-PAIRING-COVERAGE-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001"
