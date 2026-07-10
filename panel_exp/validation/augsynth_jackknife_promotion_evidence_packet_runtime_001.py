"""AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001 — evidence packet assembly runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
_SCOPE = "evidence_packet_runtime_no_promotion_no_claim_authorization"
_VERDICT = (
    "augsynth_jackknife_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"
)
_RECOMMENDED_NEXT = "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json"
)

CANONICAL_INSTRUMENT_IDENTITY = (
    "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
)
ALIAS_RELATED_RESEARCH_IDENTITY = (
    "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
)

_CORE_REQUIRED_CATEGORIES = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "directional_error",
    "positive_control_recovery",
    "sensitivity",
    "readout_compatibility",
)

_AUGSYNTH_REQUIRED_CATEGORIES = (
    "donor_pool_diagnostics",
    "pre_period_fit_diagnostics",
    "augmentation_component_diagnostics",
    "synthetic_weight_diagnostics",
    "regularization_or_model_component_diagnostics",
    "jackknife_stability",
    "method_disagreement_or_scm_bridge",
    "support_overlap_or_donor_hull_stress",
)

_REQUIRED_CATEGORIES = _CORE_REQUIRED_CATEGORIES + _AUGSYNTH_REQUIRED_CATEGORIES

_OPTIONAL_CATEGORIES = (
    "placebo_evidence",
    "conformal_evidence",
    "bootstrap_evidence",
    "production_compatibility",
    "catalog_governance",
    "external_method_review",
)

_KNOWN_CATEGORIES = frozenset(_REQUIRED_CATEGORIES) | frozenset(_OPTIONAL_CATEGORIES)

_CATEGORY_MISSING_BLOCKER = {
    "instrument_identity": "BLOCKED_MISSING_INSTRUMENT_IDENTITY",
    "claim_boundary": "BLOCKED_MISSING_CLAIM_BOUNDARY",
    "metric_estimand_alignment": "BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT",
    "null_control_false_positive": "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE",
    "directional_error": "BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE",
    "positive_control_recovery": "BLOCKED_MISSING_POSITIVE_CONTROL_EVIDENCE",
    "sensitivity": "BLOCKED_MISSING_SENSITIVITY_EVIDENCE",
    "readout_compatibility": "BLOCKED_MISSING_READOUT_COMPATIBILITY",
    "donor_pool_diagnostics": "BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS",
    "pre_period_fit_diagnostics": "BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS",
    "augmentation_component_diagnostics": "BLOCKED_MISSING_AUGMENTATION_COMPONENT_DIAGNOSTICS",
    "synthetic_weight_diagnostics": "BLOCKED_MISSING_SYNTHETIC_WEIGHT_DIAGNOSTICS",
    "regularization_or_model_component_diagnostics": "BLOCKED_MISSING_REGULARIZATION_DIAGNOSTICS",
    "jackknife_stability": "BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE",
    "method_disagreement_or_scm_bridge": "BLOCKED_MISSING_METHOD_DISAGREEMENT_EVIDENCE",
    "support_overlap_or_donor_hull_stress": "BLOCKED_MISSING_SUPPORT_OVERLAP_DIAGNOSTICS",
}

_FORBIDDEN_SOURCE_FAMILIES = frozenset({"tbrridge", "scm", "lane_b", "spend", "roi", "mip"})

_LANE_B_CATEGORIES = frozenset(
    {
        "post_test_spend",
        "spend_readiness",
        "spend_delta",
        "efficiency_metric_readiness",
        "roi_readiness",
        "lane_b_spend",
    }
)

_ALLOWED_REQUESTED_SURFACES = frozenset(
    {
        "restricted_review",
        "diagnostic_restricted_review",
        "augsynth_restricted_review",
    }
)

_PRODUCTION_SURFACES = frozenset(
    {
        "production",
        "production_readout",
        "production_compatibility",
        "prod",
        "prod_compatibility",
        "production_review",
    }
)

_CATALOG_SURFACES = frozenset(
    {
        "catalog",
        "catalog_unblock",
        "catalog_promotion",
    }
)

_CLAIM_MIP_SURFACES = frozenset(
    {
        "claim_authorization",
        "business_recommendation",
        "mip_decision_surface",
    }
)

_ALLOWED_SURFACES = (
    "restricted_review",
    "diagnostic_restricted_review",
    "augsynth_restricted_review",
)

_PROHIBITED_SURFACES = (
    "production",
    "production_readout",
    "production_compatibility",
    "catalog",
    "catalog_unblock",
    "catalog_promotion",
    "claim_authorization",
    "business_recommendation",
    "mip_decision_surface",
    "research_only_as_promotion_substitute",
    "confidence_interval_claim",
    "p_value_claim",
    "statistical_significance_claim",
    "causal_lift_claim",
    "business_lift_claim",
    "roi_roas_claim",
    "decision_recommendation",
    "method_promotion",
    "instrument_promotion",
)

_ALWAYS_WARNINGS = (
    "AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI",
    "AUGSYNTH_WARNING_RESTRICTED_REVIEW_NOT_PROMOTION",
    "AUGSYNTH_WARNING_GENERIC_ADAPTER_PROFILE_NOT_AVAILABLE_YET",
)

_BOUNDARY_STATUSES = {
    "claim_authorization_status": "NOT_AUTHORIZED_BY_THIS_PACKET",
    "catalog_status": "NOT_UNBLOCKED_BY_THIS_PACKET",
    "production_compatibility_status": "NOT_AUTHORIZED_BY_THIS_PACKET",
    "method_promotion_status": "NOT_PROMOTED_BY_THIS_PACKET",
    "instrument_promotion_status": "NOT_PROMOTED_BY_THIS_PACKET",
    "generic_adapter_status": "NOT_REGISTERED_BY_THIS_PACKET",
    "mip_decisioning_status": "NOT_AUTHORIZED_BY_THIS_PACKET",
    "trust_report_bypass_status": "NOT_BYPASSED_BY_THIS_PACKET",
}


class AugSynthJackknifePacketReadinessStatus(str, Enum):
    PACKET_READY_FOR_PROMOTION_REVIEW_INPUT = "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT"
    PACKET_PARTIAL_DIAGNOSTIC_ONLY = "PACKET_PARTIAL_DIAGNOSTIC_ONLY"
    PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE = "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE"
    PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING = "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING"
    PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH = "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH"
    PACKET_BLOCKED_UNSUPPORTED_SURFACE = "PACKET_BLOCKED_UNSUPPORTED_SURFACE"
    PACKET_BLOCKED_CROSS_INFERENCE_FAMILY = "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY"
    PACKET_BLOCKED_CROSS_GEOMETRY = "PACKET_BLOCKED_CROSS_GEOMETRY"
    PACKET_BLOCKED_CROSS_ESTIMAND = "PACKET_BLOCKED_CROSS_ESTIMAND"
    PACKET_BLOCKED_SCOPE_VIOLATION = "PACKET_BLOCKED_SCOPE_VIOLATION"
    PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED = (
        "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED"
    )
    PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT = "PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT"
    PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT = (
        "PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT"
    )
    PACKET_NOT_REQUESTED = "PACKET_NOT_REQUESTED"


class AugSynthJackknifePromotionReviewEligibilityStatus(str, Enum):
    ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT = "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT"
    NOT_ELIGIBLE_MISSING_EVIDENCE = "NOT_ELIGIBLE_MISSING_EVIDENCE"
    NOT_ELIGIBLE_IDENTITY_MISMATCH = "NOT_ELIGIBLE_IDENTITY_MISMATCH"
    NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING = "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING"
    NOT_ELIGIBLE_SCOPE_VIOLATION = "NOT_ELIGIBLE_SCOPE_VIOLATION"
    NOT_ELIGIBLE_ALIAS_SUBSTITUTION = "NOT_ELIGIBLE_ALIAS_SUBSTITUTION"
    NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION = "NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION"
    NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW = "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW"
    NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK = "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK"
    NOT_ELIGIBLE_FOR_CLAIM_REVIEW = "NOT_ELIGIBLE_FOR_CLAIM_REVIEW"


@dataclass(frozen=True)
class AugSynthJackknifeEvidenceReference:
    evidence_id: str
    evidence_category: str
    artifact_ref: str
    instrument_identity: str = CANONICAL_INSTRUMENT_IDENTITY
    evidence_surface: str = "restricted_review"
    source_family: str = "augsynth"
    source_lane: str = ""
    source_artifact_type: str = ""
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AugSynthJackknifePromotionEvidencePacketInput:
    packet_id: str
    instrument_identity: str = CANONICAL_INSTRUMENT_IDENTITY
    requested_surface: str = "restricted_review"
    evidence_references: list[AugSynthJackknifeEvidenceReference] = field(default_factory=list)
    required_evidence_categories: list[str] = field(
        default_factory=lambda: list(_REQUIRED_CATEGORIES)
    )
    optional_evidence_categories: list[str] = field(
        default_factory=lambda: list(_OPTIONAL_CATEGORIES)
    )
    lineage: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    created_from_artifacts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AugSynthJackknifePromotionEvidencePacket:
    packet_id: str
    instrument_identity: str
    alias_related_identity: str
    evidence_by_category: dict[str, tuple[dict[str, Any], ...]]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    packet_readiness_status: AugSynthJackknifePacketReadinessStatus
    promotion_review_eligibility_status: AugSynthJackknifePromotionReviewEligibilityStatus
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    boundary_statuses: dict[str, str]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["packet_readiness_status"] = self.packet_readiness_status.value
        payload["promotion_review_eligibility_status"] = (
            self.promotion_review_eligibility_status.value
        )
        return payload


def _ref_to_dict(ref: AugSynthJackknifeEvidenceReference) -> dict[str, Any]:
    return asdict(ref)


def _normalize_surface(surface: str | None) -> str | None:
    if surface is None:
        return None
    text = str(surface).strip().lower()
    return text or None


def _source_family(ref: AugSynthJackknifeEvidenceReference) -> str:
    family = str(ref.source_family or ref.metadata.get("source_family", "")).strip().lower()
    return family


def _is_substitution_family(family: str) -> str | None:
    if family in {"tbrridge", "tbr"} or "tbrridge" in family:
        return "AUGSYNTH_PACKET_BLOCKED_TBRRIDGE_EVIDENCE_SUBSTITUTION"
    if family == "scm":
        return "AUGSYNTH_PACKET_BLOCKED_SCM_EVIDENCE_SUBSTITUTION"
    if family in {"lane_b", "lane-b", "spend", "roi", "mip"}:
        return "AUGSYNTH_PACKET_BLOCKED_LANE_B_EVIDENCE_SUBSTITUTION"
    return None


def _ref_identity_issue(ref: AugSynthJackknifeEvidenceReference) -> str | None:
    identity = str(ref.instrument_identity).strip()
    if identity == ALIAS_RELATED_RESEARCH_IDENTITY:
        return "AUGSYNTH_PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT"
    if identity and identity != CANONICAL_INSTRUMENT_IDENTITY:
        return "AUGSYNTH_PACKET_BLOCKED_MISSING_CANONICAL_IDENTITY"
    return None


def _ref_valid_for_category(
    ref: AugSynthJackknifeEvidenceReference,
    *,
    blockers: list[str],
    warnings: list[str],
) -> bool:
    cat = str(ref.evidence_category).strip()
    if cat in _LANE_B_CATEGORIES:
        blockers.append("AUGSYNTH_PACKET_BLOCKED_LANE_B_EVIDENCE_SUBSTITUTION")
        warnings.append(f"AUGSYNTH_WARNING_TBRRIDGE_PATTERN_NOT_EVIDENCE:{cat}")
        return False
    if cat not in _KNOWN_CATEGORIES:
        return False
    if not str(ref.artifact_ref).strip():
        return False

    identity_issue = _ref_identity_issue(ref)
    if identity_issue:
        blockers.append(identity_issue)
        return False

    family = _source_family(ref)
    substitution = _is_substitution_family(family)
    if substitution:
        blockers.append(substitution)
        if substitution.endswith("SCM_EVIDENCE_SUBSTITUTION"):
            warnings.append("AUGSYNTH_WARNING_SCM_BRIDGE_NOT_SUBSTITUTION")
        if substitution.endswith("TBRRIDGE_EVIDENCE_SUBSTITUTION"):
            warnings.append("AUGSYNTH_WARNING_TBRRIDGE_PATTERN_NOT_EVIDENCE")
        return False

    artifact_ref = str(ref.artifact_ref).lower()
    if "tbrridge" in artifact_ref:
        blockers.append("AUGSYNTH_PACKET_BLOCKED_TBRRIDGE_EVIDENCE_SUBSTITUTION")
        warnings.append("AUGSYNTH_WARNING_TBRRIDGE_PATTERN_NOT_EVIDENCE")
        return False
    if artifact_ref.startswith("geox_") or "/geox_" in artifact_ref:
        blockers.append("AUGSYNTH_PACKET_BLOCKED_LANE_B_EVIDENCE_SUBSTITUTION")
        return False

    return True


def _group_evidence(
    refs: list[AugSynthJackknifeEvidenceReference],
    *,
    warnings: list[str],
    blockers: list[str],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        if not _ref_valid_for_category(ref, blockers=blockers, warnings=warnings):
            continue
        cat = str(ref.evidence_category).strip()
        grouped.setdefault(cat, []).append(_ref_to_dict(ref))
    return grouped


def _group_all_refs(
    refs: list[AugSynthJackknifeEvidenceReference],
) -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        cat = str(ref.evidence_category).strip()
        grouped.setdefault(cat, []).append(_ref_to_dict(ref))
    return {k: tuple(v) for k, v in grouped.items()}


def _surface_block(
    surface: str | None,
) -> tuple[
    AugSynthJackknifePacketReadinessStatus,
    AugSynthJackknifePromotionReviewEligibilityStatus,
    str,
] | None:
    if surface is None:
        return None
    if surface in _ALLOWED_REQUESTED_SURFACES:
        return None
    if surface == "research_only_as_promotion_substitute":
        return (
            AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT,
            AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION,
            "AUGSYNTH_PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT",
        )
    if surface in _PRODUCTION_SURFACES:
        return (
            AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED,
            AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW,
            "AUGSYNTH_PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED",
        )
    if surface in _CATALOG_SURFACES:
        return (
            AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK,
            "AUGSYNTH_PACKET_BLOCKED_CATALOG_GOVERNANCE_REQUIRED",
        )
    if surface in _CLAIM_MIP_SURFACES:
        return (
            AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CLAIM_REVIEW,
            "AUGSYNTH_PACKET_BLOCKED_CLAIM_AUTHORIZATION_ATTEMPT",
        )
    return (
        AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
        AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_SCOPE_VIOLATION,
        "AUGSYNTH_PACKET_BLOCKED_UNSUPPORTED_SURFACE",
    )


def _make_packet(
    inp: AugSynthJackknifePromotionEvidencePacketInput,
    *,
    evidence_by_category: dict[str, tuple[dict[str, Any], ...]] | dict[str, list[dict[str, Any]]],
    missing_evidence: tuple[str, ...],
    blockers: tuple[str, ...],
    warnings: list[str],
    readiness: AugSynthJackknifePacketReadinessStatus,
    eligibility: AugSynthJackknifePromotionReviewEligibilityStatus,
    identity: str | None = None,
) -> AugSynthJackknifePromotionEvidencePacket:
    normalized = {
        k: tuple(v) if isinstance(v, list) else v for k, v in evidence_by_category.items()
    }
    out_identity = identity or inp.instrument_identity
    if readiness == AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT:
        out_identity = CANONICAL_INSTRUMENT_IDENTITY
    merged_warnings = list(_ALWAYS_WARNINGS) + list(warnings)
    created = tuple(dict.fromkeys(list(inp.created_from_artifacts) + [_ARTIFACT_ID]))
    return AugSynthJackknifePromotionEvidencePacket(
        packet_id=inp.packet_id,
        instrument_identity=out_identity,
        alias_related_identity=ALIAS_RELATED_RESEARCH_IDENTITY,
        evidence_by_category=normalized,
        missing_evidence=missing_evidence,
        blockers=blockers,
        warnings=tuple(dict.fromkeys(merged_warnings)),
        packet_readiness_status=readiness,
        promotion_review_eligibility_status=eligibility,
        allowed_surfaces=_ALLOWED_SURFACES,
        prohibited_surfaces=_PROHIBITED_SURFACES,
        boundary_statuses=dict(_BOUNDARY_STATUSES),
        lineage=dict(inp.lineage),
        created_from_artifacts=created,
    )


def assemble_augsynth_jackknife_promotion_evidence_packet(
    inp: AugSynthJackknifePromotionEvidencePacketInput,
) -> AugSynthJackknifePromotionEvidencePacket:
    """Assemble a governed AugSynth Jackknife restricted-review promotion evidence packet."""
    warnings = list(inp.warnings)
    blockers: list[str] = []
    requested_surface = _normalize_surface(inp.requested_surface)
    required_categories = tuple(inp.required_evidence_categories or _REQUIRED_CATEGORIES)

    if not inp.evidence_references and not requested_surface:
        return _make_packet(
            inp,
            evidence_by_category={},
            missing_evidence=required_categories,
            blockers=(),
            warnings=warnings,
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_NOT_REQUESTED,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )

    identity = str(inp.instrument_identity).strip()
    if identity == ALIAS_RELATED_RESEARCH_IDENTITY:
        return _make_packet(
            inp,
            evidence_by_category=_group_all_refs(inp.evidence_references),
            missing_evidence=("instrument_identity",),
            blockers=("AUGSYNTH_PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT",),
            warnings=warnings,
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION,
        )
    if identity != CANONICAL_INSTRUMENT_IDENTITY:
        return _make_packet(
            inp,
            evidence_by_category=_group_all_refs(inp.evidence_references),
            missing_evidence=("instrument_identity",),
            blockers=("AUGSYNTH_PACKET_BLOCKED_MISSING_CANONICAL_IDENTITY",),
            warnings=warnings,
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
        )

    surface_block = _surface_block(requested_surface)
    if surface_block is not None:
        readiness, eligibility, blocker = surface_block
        return _make_packet(
            inp,
            evidence_by_category=_group_all_refs(inp.evidence_references),
            missing_evidence=required_categories,
            blockers=(blocker,),
            warnings=warnings,
            readiness=readiness,
            eligibility=eligibility,
        )

    grouped = _group_evidence(inp.evidence_references, warnings=warnings, blockers=blockers)
    missing: list[str] = []
    for cat in required_categories:
        if cat not in grouped:
            missing.append(cat)
            blocker_name = _CATEGORY_MISSING_BLOCKER.get(
                cat, "AUGSYNTH_PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE"
            )
            blockers.append(blocker_name)

    if "claim_boundary" in missing:
        return _make_packet(
            inp,
            evidence_by_category={k: tuple(v) for k, v in grouped.items()},
            missing_evidence=tuple(missing),
            blockers=tuple(dict.fromkeys(blockers)),
            warnings=warnings,
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING,
        )

    if missing:
        readiness = AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
        if grouped:
            readiness = AugSynthJackknifePacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY
        return _make_packet(
            inp,
            evidence_by_category={k: tuple(v) for k, v in grouped.items()},
            missing_evidence=tuple(missing),
            blockers=tuple(dict.fromkeys(blockers)),
            warnings=warnings,
            readiness=readiness,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )

    return _make_packet(
        inp,
        evidence_by_category={k: tuple(v) for k, v in grouped.items()},
        missing_evidence=(),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=warnings,
        readiness=AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT,
        eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT,
        identity=CANONICAL_INSTRUMENT_IDENTITY,
    )


def _sample_references() -> list[AugSynthJackknifeEvidenceReference]:
    return [
        AugSynthJackknifeEvidenceReference(
            evidence_id=f"{cat}_001",
            evidence_category=cat,
            artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
        )
        for cat in _REQUIRED_CATEGORIES
    ]


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(
            packet_id="validation_sample",
            evidence_references=_sample_references(),
            lineage={"runtime": _ARTIFACT_ID},
        )
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
    )
    assert packet.boundary_statuses["claim_authorization_status"] == "NOT_AUTHORIZED_BY_THIS_PACKET"
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "augsynth_jackknife_promotion_evidence_packet_runtime",
        "lane": "Lane A - Method instrument promotion framework application",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "alias_related_identity": ALIAS_RELATED_RESEARCH_IDENTITY,
        "depends_on": [
            "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001",
            "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001",
            "METHOD_PROMOTION_GENERIC_RUNTIME_001",
            "METHOD_PROMOTION_GENERIC_CONTRACTS_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "evidence_packet_runtime_implemented": True,
        "exact_instrument_identity_enforced": True,
        "alias_substitution_blocked": True,
        "research_only_substitution_blocked": True,
        "allowed_surface_enforced": True,
        "required_evidence_categories_enforced": True,
        "non_empty_artifact_ref_required": True,
        "scm_evidence_substitution_blocked": True,
        "tbrridge_evidence_substitution_blocked": True,
        "lane_b_evidence_substitution_blocked": True,
        "readiness_precedence_implemented": True,
        "eligibility_mapping_implemented": True,
        "blockers_emitted": True,
        "warnings_emitted": True,
        "fixed_non_authorization_statuses_emitted": True,
        "generic_framework_compatibility_preserved": True,
        "evidence_quality_boundary_preserved": True,
        "runtime_implemented": True,
        "augsynth_runtime_implemented": True,
        "augsynth_decision_contract_implemented": False,
        "generic_runtime_changed": False,
        "generic_adapter_profile_for_augsynth_implemented": False,
        "method_promoted": False,
        "instrument_promoted": False,
        "augsynth_promoted": False,
        "did_promoted": False,
        "catalog_unblocked": False,
        "production_compatibility_authorized": False,
        "claim_authorization_changed": False,
        "statistical_claim_authorized": False,
        "confidence_interval_claim_authorized": False,
        "p_value_claim_authorized": False,
        "significance_claim_authorized": False,
        "statistical_power_claim_authorized": False,
        "causal_lift_claim_authorized": False,
        "business_lift_claim_authorized": False,
        "roi_roas_claim_authorized": False,
        "decision_recommendation_authorized": False,
        "production_readout_authorized": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "new_validation_experiments_run": False,
        "raw_evidence_quality_scored": False,
        "lane_b_runtime_changed": False,
        "mip_decisioning_authorized": False,
        "trust_report_bypassed": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "final_verdict": _VERDICT,
        "validation_sample_readiness_status": packet.packet_readiness_status.value,
        "validation_sample_eligibility_status": packet.promotion_review_eligibility_status.value,
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AugSynth Jackknife promotion evidence packet assembly validation"
    )
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
