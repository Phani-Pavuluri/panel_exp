"""Governance tests for AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_VERDICT = "augsynth_jackknife_evidence_packet_contract_defined_no_runtime_no_promotion"
_NEXT_RUNTIME = "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
_LANE_A_NEXT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"

_CORE_CATEGORIES = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "directional_error",
    "positive_control_recovery",
    "sensitivity",
    "readout_compatibility",
)

_AUGSYNTH_CATEGORIES = (
    "donor_pool_diagnostics",
    "pre_period_fit_diagnostics",
    "augmentation_component_diagnostics",
    "synthetic_weight_diagnostics",
    "regularization_or_model_component_diagnostics",
    "jackknife_stability",
    "method_disagreement_or_scm_bridge",
    "support_overlap_or_donor_hull_stress",
)

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "augsynth_runtime_implemented",
    "augsynth_decision_contract_implemented",
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
    "evidence_packet_contract_defined",
    "exact_instrument_identity_defined",
    "alias_substitution_blocked",
    "research_only_substitution_blocked",
    "evidence_reference_contract_defined",
    "packet_input_contract_defined",
    "packet_output_contract_defined",
    "required_evidence_categories_defined",
    "augsynth_specific_evidence_categories_defined",
    "readiness_statuses_defined",
    "eligibility_statuses_defined",
    "allowed_surfaces_defined",
    "unsupported_surfaces_blocked",
    "blockers_defined",
    "warnings_defined",
    "fixed_non_authorization_statuses_defined",
    "generic_framework_compatibility_defined",
    "scm_evidence_substitution_blocked",
    "tbrridge_evidence_substitution_blocked",
    "lane_b_evidence_substitution_blocked",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_jackknife_promotion_evidence_packet_contract"


def test_exact_identity_defined() -> None:
    data = _load_summary()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert data["instrument_identity"] == _INSTRUMENT
    assert _INSTRUMENT in text
    assert "diagnostic_interval" in text
    assert "restricted_review" in text


def test_alias_and_research_only_substitution_blocked() -> None:
    data = _load_summary()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert data["alias_substitution_blocked"] is True
    assert data["research_only_substitution_blocked"] is True
    assert _ALIAS in text
    assert "AUGSYNTH_PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT" in text
    assert "AUGSYNTH_PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT" in text


def test_evidence_reference_input_output_contracts_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AugSynthJackknifeEvidenceReference" in text
    assert "AugSynthJackknifePromotionEvidencePacketInput" in text
    assert "AugSynthJackknifePromotionEvidencePacket" in text
    data = _load_summary()
    assert data["evidence_reference_contract_defined"] is True
    assert data["packet_input_contract_defined"] is True
    assert data["packet_output_contract_defined"] is True


def test_required_evidence_categories_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    for cat in _CORE_CATEGORIES:
        assert cat in text
    assert _load_summary()["required_evidence_categories_defined"] is True


def test_augsynth_specific_categories_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    for cat in _AUGSYNTH_CATEGORIES:
        assert cat in text
    assert _load_summary()["augsynth_specific_evidence_categories_defined"] is True


def test_readiness_and_eligibility_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AugSynthJackknifePacketReadinessStatus" in text
    assert "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT" in text
    assert "AugSynthJackknifePromotionReviewEligibilityStatus" in text
    assert "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT" in text
    data = _load_summary()
    assert data["readiness_statuses_defined"] is True
    assert data["eligibility_statuses_defined"] is True


def test_allowed_and_unsupported_surfaces_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "augsynth_restricted_review" in text
    assert "production_readout" in text
    assert "research_only_as_promotion_substitute" in text
    data = _load_summary()
    assert data["allowed_surfaces_defined"] is True
    assert data["unsupported_surfaces_blocked"] is True


def test_blockers_and_warnings_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AUGSYNTH_PACKET_BLOCKED_SCM_EVIDENCE_SUBSTITUTION" in text
    assert "AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI" in text
    data = _load_summary()
    assert data["blockers_defined"] is True
    assert data["warnings_defined"] is True


def test_fixed_non_authorization_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_THIS_PACKET" in text
    assert "NOT_REGISTERED_BY_THIS_PACKET" in text
    assert _load_summary()["fixed_non_authorization_statuses_defined"] is True


def test_generic_framework_compatibility_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MethodPromotionEvidencePacket" in text
    assert "must **not** be added to" in text
    assert _load_summary()["generic_framework_compatibility_defined"] is True


def test_substitution_blocked() -> None:
    data = _load_summary()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert data["scm_evidence_substitution_blocked"] is True
    assert data["tbrridge_evidence_substitution_blocked"] is True
    assert data["lane_b_evidence_substitution_blocked"] is True
    assert "cannot substitute" in text.lower()


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_RUNTIME
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in _CONTRACT.read_text(
        encoding="utf-8"
    )


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert "AUGSYNTH-JACKKNIFE-PROMOTION-EVIDENCE-PACKET-CONTRACT-001" in _MIP_AUDIT_REGISTRY.read_text(
        encoding="utf-8"
    )


def test_method_soundness_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in _METHOD_SOUNDNESS.read_text(
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
