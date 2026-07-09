"""Governance tests for TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_FORBIDDEN_TRUE_FLAGS = (
    "claim_authorization_granted",
    "method_promoted",
    "instrument_promoted",
    "method_unblocked",
    "estimator_family_promoted",
    "global_tbrridge_promotion_authorized",
    "catalog_unblocked",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "decision_ready_authorized",
    "uncertainty_authorized",
    "uncertainty_candidate_approved",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "statistical_power_authorized",
    "causal_lift_authorized",
    "business_lift_authorized",
    "roi_authorized",
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

_REQUIRED_TRUE_FLAGS = (
    "tbrridge_claim_authorization_boundary_audit_completed",
    "exact_instrument_identity_documented",
    "claim_taxonomy_defined",
    "allowed_claim_surfaces_defined",
    "prohibited_claim_surfaces_defined",
    "diagnostic_decision_boundary_defined",
    "future_claim_gates_defined",
    "runtime_packet_integration_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001" in text
    assert (
        "tbrridge_kfold_claim_authorization_boundary_audited_no_claim_authorization_or_promotion"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001"
    assert data["status"] == "completed"
    assert data["base_commit"] == "2e378f8"


def test_exact_instrument_identity_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review" in text
    data = _load_summary()
    assert data["exact_instrument_identity_documented"] is True


def test_claim_taxonomy_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Claim taxonomy" in text
    assert "diagnostic_status_claim" in text
    assert "ROI_claim" in text
    data = _load_summary()
    assert data["claim_taxonomy_defined"] is True


def test_allowed_claim_surfaces_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Allowed claim surfaces" in text
    assert "DIAGNOSTIC_STATUS_SUMMARY" in text
    assert "FUTURE_EVIDENCE_PACKET_INPUT_DESCRIPTION" in text
    data = _load_summary()
    assert data["allowed_claim_surfaces_defined"] is True


def test_prohibited_claim_surfaces_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Prohibited claim surfaces" in text
    assert "CONFIDENCE_INTERVAL_CLAIM" in text
    assert "PRODUCTION_READOUT" in text
    assert "UNCERTAINTY_APPROVAL_NOTICE" in text
    data = _load_summary()
    assert data["prohibited_claim_surfaces_defined"] is True


def test_diagnostic_decision_boundary_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Boundary between diagnostic/review language and decision language" in text
    assert "Boundary between diagnostic intervals and statistical intervals" in text
    data = _load_summary()
    assert data["diagnostic_decision_boundary_defined"] is True


def test_future_claim_gates_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Required future gates for stronger claims" in text
    assert "claim authorization contract/runtime" in text
    assert "method-promotion review pass for exact instrument identity" in text
    data = _load_summary()
    assert data["future_claim_gates_defined"] is True


def test_runtime_packet_integration_references_claim_boundary_report() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Runtime packet integration plan" in text
    assert "claim_authorization_boundary_report" in text
    assert "generate_tbrridge_method_promotion_review()" in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert (
        data["recommended_next_artifact"]
        == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
    )
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001" in text


def test_required_flags_true() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_final_verdict_matches_scope() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_kfold_claim_authorization_boundary_audited_no_claim_authorization_or_promotion"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-CLAIM-AUTHORIZATION-BOUNDARY-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-CLAIM-AUTHORIZATION-BOUNDARY-AUDIT-001" in lane_ids
