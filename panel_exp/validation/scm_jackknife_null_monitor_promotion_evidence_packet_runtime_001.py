"""SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001 — evidence packet assembly runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
_SCOPE = "evidence_packet_runtime_no_promotion_no_claim_authorization"
_VERDICT = (
    "scm_jackknife_null_monitor_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"
)
_RECOMMENDED_NEXT = "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json"
)

CANONICAL_INSTRUMENT_IDENTITY = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
CATALOG_ALIAS = "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review"

_REQUIRED_CATEGORIES = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "jackknife_stability",
    "directional_error",
    "donor_pool_diagnostics",
    "pre_period_fit_diagnostics",
    "sensitivity",
    "readout_compatibility",
)

_OPTIONAL_CATEGORIES = frozenset({"production_compatibility"})

_KNOWN_CATEGORIES = frozenset(_REQUIRED_CATEGORIES) | _OPTIONAL_CATEGORIES

_CATEGORY_MISSING_BLOCKER = {
    "instrument_identity": "BLOCKED_MISSING_INSTRUMENT_IDENTITY",
    "claim_boundary": "BLOCKED_MISSING_CLAIM_BOUNDARY",
    "metric_estimand_alignment": "BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT",
    "null_control_false_positive": "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE",
    "jackknife_stability": "BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE",
    "directional_error": "BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE",
    "donor_pool_diagnostics": "BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS",
    "pre_period_fit_diagnostics": "BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS",
    "sensitivity": "BLOCKED_MISSING_SENSITIVITY_EVIDENCE",
    "readout_compatibility": "BLOCKED_MISSING_READOUT_COMPATIBILITY",
}

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

_METHOD_VALIDITY_CATEGORIES = frozenset(
    {
        "instrument_identity",
        "claim_boundary",
        "metric_estimand_alignment",
        "null_control_false_positive",
        "jackknife_stability",
        "directional_error",
        "donor_pool_diagnostics",
        "pre_period_fit_diagnostics",
        "sensitivity",
    }
)

_ALLOWED_REQUESTED_SURFACES = frozenset(
    {
        "null_monitor",
        "diagnostic_null_monitor",
        "restricted_review_null_monitor",
    }
)

_PRODUCTION_SURFACES = frozenset(
    {
        "production",
        "prod",
        "prod_compatibility",
        "production_readout",
        "production_review",
        "production_compatibility",
    }
)

_CATALOG_SURFACES = frozenset({"catalog", "catalog_unblock"})

_CAUSAL_CLAIM_SURFACES = frozenset(
    {
        "causal_lift",
        "business_lift",
        "ci",
        "confidence_interval_claim",
        "p_value",
        "p_value_claim",
        "significance",
        "statistical_significance_claim",
        "roi",
        "roas",
        "roi_roas_claim",
        "decision_recommendation",
    }
)

_ALLOWED_SURFACES = (
    "null_monitor",
    "diagnostic_null_monitor",
    "restricted_review_null_monitor",
)

_PROHIBITED_SURFACES = (
    "causal_lift",
    "business_lift",
    "confidence_interval_claim",
    "p_value_claim",
    "statistical_significance_claim",
    "statistical_power_claim",
    "roi_roas_claim",
    "decision_recommendation",
    "production_readout",
    "catalog_unblock",
    "method_promotion",
    "instrument_promotion",
    "production_compatibility_authorization",
    "trust_report_bypass",
    "claim_authorization_runtime_bypass",
)


class SCMJackknifeNullMonitorPacketReadinessStatus(str, Enum):
    PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT = "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT"
    PACKET_PARTIAL_DIAGNOSTIC_ONLY = "PACKET_PARTIAL_DIAGNOSTIC_ONLY"
    PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE = "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE"
    PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING = "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING"
    PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH = "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH"
    PACKET_BLOCKED_UNSUPPORTED_SURFACE = "PACKET_BLOCKED_UNSUPPORTED_SURFACE"
    PACKET_BLOCKED_CROSS_INFERENCE_FAMILY = "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY"
    PACKET_BLOCKED_CROSS_GEOMETRY = "PACKET_BLOCKED_CROSS_GEOMETRY"
    PACKET_BLOCKED_CROSS_ESTIMAND = "PACKET_BLOCKED_CROSS_ESTIMAND"
    PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION = "PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION"
    PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED = (
        "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED"
    )
    PACKET_NOT_REQUESTED = "PACKET_NOT_REQUESTED"


class SCMJackknifeNullMonitorPromotionReviewEligibilityStatus(str, Enum):
    ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT = "ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT"
    NOT_ELIGIBLE_MISSING_EVIDENCE = "NOT_ELIGIBLE_MISSING_EVIDENCE"
    NOT_ELIGIBLE_IDENTITY_MISMATCH = "NOT_ELIGIBLE_IDENTITY_MISMATCH"
    NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING = "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING"
    NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION = "NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION"
    NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW = "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW"
    NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK = "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK"
    NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW = "NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW"


@dataclass(frozen=True)
class SCMJackknifeNullMonitorEvidenceReference:
    evidence_id: str
    evidence_category: str
    artifact_ref: str
    instrument_identity: str | None = None
    catalog_alias: str | None = None
    evidence_surface: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMJackknifeNullMonitorPromotionEvidencePacketInput:
    packet_id: str
    instrument_identity: str = CANONICAL_INSTRUMENT_IDENTITY
    catalog_alias: str | None = None
    evidence_refs: list[SCMJackknifeNullMonitorEvidenceReference] = field(default_factory=list)
    requested_surface: str | None = "null_monitor"
    lineage: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    created_from_artifacts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SCMJackknifeNullMonitorPromotionEvidencePacket:
    packet_id: str
    instrument_identity: str
    catalog_alias: str | None
    estimator_family: str
    inference_family: str
    geometry: str
    estimand: str
    surface: str
    interval_semantics: str
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    evidence_by_category: dict[str, tuple[dict[str, Any], ...]]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    packet_readiness_status: SCMJackknifeNullMonitorPacketReadinessStatus
    promotion_review_eligibility_status: SCMJackknifeNullMonitorPromotionReviewEligibilityStatus
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["packet_readiness_status"] = self.packet_readiness_status.value
        payload["promotion_review_eligibility_status"] = (
            self.promotion_review_eligibility_status.value
        )
        return payload


def _ref_to_dict(ref: SCMJackknifeNullMonitorEvidenceReference) -> dict[str, Any]:
    return asdict(ref)


def _is_tbrridge_ref(ref: SCMJackknifeNullMonitorEvidenceReference) -> bool:
    metadata = ref.metadata or {}
    source_family = str(metadata.get("source_family", "")).lower()
    if source_family == "tbrridge":
        return True
    artifact_ref = str(ref.artifact_ref).lower()
    return "tbrridge" in artifact_ref


def _is_lane_b_ref(ref: SCMJackknifeNullMonitorEvidenceReference) -> bool:
    cat = str(ref.evidence_category).strip()
    if cat in _LANE_B_CATEGORIES:
        return True
    metadata = ref.metadata or {}
    source_lane = str(metadata.get("source_lane", "")).lower()
    if source_lane in {"lane_b", "lane-b"}:
        return True
    artifact_ref = str(ref.artifact_ref).lower()
    return artifact_ref.startswith("geox_") or "/geox_" in artifact_ref


def _ref_valid_for_category(ref: SCMJackknifeNullMonitorEvidenceReference) -> bool:
    cat = str(ref.evidence_category).strip()
    if cat not in _KNOWN_CATEGORIES and cat not in _LANE_B_CATEGORIES:
        return False
    if not str(ref.artifact_ref).strip():
        return False
    if _is_tbrridge_ref(ref):
        return False
    if _is_lane_b_ref(ref) and cat in _METHOD_VALIDITY_CATEGORIES:
        return False
    if cat == "readout_compatibility" and _is_lane_b_ref(ref):
        return False
    return True


def _resolve_catalog_alias(
    inp: SCMJackknifeNullMonitorPromotionEvidencePacketInput,
    refs: list[SCMJackknifeNullMonitorEvidenceReference],
) -> str | None:
    if inp.catalog_alias == CATALOG_ALIAS:
        return CATALOG_ALIAS
    for ref in refs:
        if ref.catalog_alias == CATALOG_ALIAS:
            return CATALOG_ALIAS
        if ref.instrument_identity == CATALOG_ALIAS:
            return CATALOG_ALIAS
    return inp.catalog_alias


def _normalize_surface(surface: str | None) -> str | None:
    if surface is None:
        return None
    return str(surface).strip().lower()


def _surface_block(
    surface: str | None,
) -> tuple[
    SCMJackknifeNullMonitorPacketReadinessStatus,
    SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    str,
] | None:
    if surface is None:
        return None
    if surface in _ALLOWED_REQUESTED_SURFACES:
        return None
    if surface in _PRODUCTION_SURFACES:
        return (
            SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED,
            SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW,
            "BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED",
        )
    if surface in _CATALOG_SURFACES:
        return (
            SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK,
            "BLOCKED_CATALOG_UNBLOCK_REQUESTED",
        )
    if surface in _CAUSAL_CLAIM_SURFACES:
        return (
            SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION,
            SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW,
            "BLOCKED_CAUSAL_CLAIM_REQUESTED",
        )
    return (
        SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION,
        "BLOCKED_UNSUPPORTED_SURFACE",
    )


def _group_evidence(
    refs: list[SCMJackknifeNullMonitorEvidenceReference],
    *,
    warnings: list[str],
    blockers: list[str],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        cat = str(ref.evidence_category).strip()
        if _is_tbrridge_ref(ref):
            blockers.append(f"TBRIDGE_EVIDENCE_CANNOT_SATISFY_SCM:{cat}")
            warnings.append(f"TBRIDGE_EVIDENCE_CANNOT_SATISFY_SCM:{ref.evidence_id}")
            continue
        if _is_lane_b_ref(ref):
            if cat in _METHOD_VALIDITY_CATEGORIES:
                blockers.append(f"LANE_B_EVIDENCE_NOT_METHOD_VALIDITY:{cat}")
                warnings.append(f"LANE_B_EVIDENCE_CANNOT_SUBSTITUTE_METHOD_VALIDITY:{cat}")
            continue
        if cat in _LANE_B_CATEGORIES:
            blockers.append(f"LANE_B_EVIDENCE_NOT_METHOD_VALIDITY:{cat}")
            warnings.append(f"LANE_B_EVIDENCE_CANNOT_SUBSTITUTE_METHOD_VALIDITY:{cat}")
            continue
        if not _ref_valid_for_category(ref):
            if cat in _KNOWN_CATEGORIES and not str(ref.artifact_ref).strip():
                continue
            continue
        grouped.setdefault(cat, []).append(_ref_to_dict(ref))
    return grouped


def assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
    inp: SCMJackknifeNullMonitorPromotionEvidencePacketInput,
) -> SCMJackknifeNullMonitorPromotionEvidencePacket:
    """Assemble a governed SCM Jackknife null-monitor promotion evidence packet."""
    warnings = list(inp.warnings)
    blockers: list[str] = []
    requested_surface = _normalize_surface(inp.requested_surface)
    catalog_alias = _resolve_catalog_alias(inp, inp.evidence_refs)

    if not inp.evidence_refs and requested_surface is None:
        return _make_packet(
            inp,
            catalog_alias=catalog_alias,
            evidence_by_category={},
            missing_evidence=tuple(_REQUIRED_CATEGORIES),
            blockers=(),
            warnings=warnings,
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_NOT_REQUESTED,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )

    identity = str(inp.instrument_identity).strip()
    if identity and identity != CANONICAL_INSTRUMENT_IDENTITY:
        return _make_packet(
            inp,
            catalog_alias=catalog_alias,
            evidence_by_category=_group_all_refs(inp.evidence_refs),
            missing_evidence=("instrument_identity",),
            blockers=("BLOCKED_INSTRUMENT_IDENTITY_MISMATCH",),
            warnings=warnings,
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
        )

    for ref in inp.evidence_refs:
        ref_identity = ref.instrument_identity
        if ref_identity and str(ref_identity).strip() not in {"", CANONICAL_INSTRUMENT_IDENTITY}:
            if str(ref_identity).strip() == CATALOG_ALIAS:
                catalog_alias = CATALOG_ALIAS
                continue
            return _make_packet(
                inp,
                catalog_alias=catalog_alias,
                evidence_by_category=_group_all_refs(inp.evidence_refs),
                missing_evidence=("instrument_identity",),
                blockers=("BLOCKED_INSTRUMENT_IDENTITY_MISMATCH",),
                warnings=warnings,
                readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH,
                eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
            )

    surface_block = _surface_block(requested_surface)
    if surface_block is not None:
        readiness, eligibility, blocker = surface_block
        return _make_packet(
            inp,
            catalog_alias=catalog_alias,
            evidence_by_category=_group_all_refs(inp.evidence_refs),
            missing_evidence=tuple(_REQUIRED_CATEGORIES),
            blockers=(blocker,),
            warnings=warnings,
            readiness=readiness,
            eligibility=eligibility,
        )

    grouped = _group_evidence(inp.evidence_refs, warnings=warnings, blockers=blockers)
    missing: list[str] = []
    for cat in _REQUIRED_CATEGORIES:
        if cat not in grouped:
            missing.append(cat)
            blockers.append(_CATEGORY_MISSING_BLOCKER[cat])

    if "claim_boundary" in missing:
        return _make_packet(
            inp,
            catalog_alias=catalog_alias,
            evidence_by_category={k: tuple(v) for k, v in grouped.items()},
            missing_evidence=tuple(missing),
            blockers=tuple(sorted(set(blockers))),
            warnings=warnings,
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING,
        )

    if missing:
        readiness = SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
        if grouped and len(grouped) < len(_REQUIRED_CATEGORIES):
            readiness = SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY
        return _make_packet(
            inp,
            catalog_alias=catalog_alias,
            evidence_by_category={k: tuple(v) for k, v in grouped.items()},
            missing_evidence=tuple(missing),
            blockers=tuple(sorted(set(blockers))),
            warnings=warnings,
            readiness=readiness,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )

    return _make_packet(
        inp,
        catalog_alias=catalog_alias,
        evidence_by_category={k: tuple(v) for k, v in grouped.items()},
        missing_evidence=(),
        blockers=(),
        warnings=warnings,
        readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT,
        eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT,
        identity=CANONICAL_INSTRUMENT_IDENTITY,
    )


def _group_all_refs(
    refs: list[SCMJackknifeNullMonitorEvidenceReference],
) -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        cat = str(ref.evidence_category).strip()
        grouped.setdefault(cat, []).append(_ref_to_dict(ref))
    return {k: tuple(v) for k, v in grouped.items()}


def _make_packet(
    inp: SCMJackknifeNullMonitorPromotionEvidencePacketInput,
    *,
    catalog_alias: str | None,
    evidence_by_category: dict[str, tuple[dict[str, Any], ...]] | dict[str, list[dict[str, Any]]],
    missing_evidence: tuple[str, ...],
    blockers: tuple[str, ...],
    warnings: list[str],
    readiness: SCMJackknifeNullMonitorPacketReadinessStatus,
    eligibility: SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    identity: str | None = None,
) -> SCMJackknifeNullMonitorPromotionEvidencePacket:
    normalized = {
        k: tuple(v) if isinstance(v, list) else v for k, v in evidence_by_category.items()
    }
    out_identity = identity or inp.instrument_identity
    if readiness in {
        SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT,
    }:
        out_identity = CANONICAL_INSTRUMENT_IDENTITY
    return SCMJackknifeNullMonitorPromotionEvidencePacket(
        packet_id=inp.packet_id,
        instrument_identity=out_identity,
        catalog_alias=catalog_alias,
        estimator_family="scm",
        inference_family="jackknife",
        geometry="single_cell",
        estimand="delta_mu",
        surface="null_monitor",
        interval_semantics="not_applicable_for_null_monitor",
        allowed_surfaces=_ALLOWED_SURFACES,
        prohibited_surfaces=_PROHIBITED_SURFACES,
        evidence_by_category=normalized,
        missing_evidence=missing_evidence,
        blockers=blockers,
        warnings=tuple(sorted(set(warnings))),
        packet_readiness_status=readiness,
        promotion_review_eligibility_status=eligibility,
        lineage=dict(inp.lineage),
        created_from_artifacts=tuple(inp.created_from_artifacts),
    )


def _sample_references() -> list[SCMJackknifeNullMonitorEvidenceReference]:
    return [
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="instrument_identity_001",
            evidence_category="instrument_identity",
            artifact_ref="docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="claim_boundary_001",
            evidence_category="claim_boundary",
            artifact_ref="docs/track_d/CLAIM_AUTHORIZATION_RUNTIME_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="metric_estimand_alignment_001",
            evidence_category="metric_estimand_alignment",
            artifact_ref="docs/track_d/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="null_control_false_positive_001",
            evidence_category="null_control_false_positive",
            artifact_ref="docs/track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="jackknife_stability_001",
            evidence_category="jackknife_stability",
            artifact_ref="docs/track_d/SCM_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="directional_error_001",
            evidence_category="directional_error",
            artifact_ref="docs/track_d/SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="donor_pool_diagnostics_001",
            evidence_category="donor_pool_diagnostics",
            artifact_ref="docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="pre_period_fit_diagnostics_001",
            evidence_category="pre_period_fit_diagnostics",
            artifact_ref="docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="sensitivity_001",
            evidence_category="sensitivity",
            artifact_ref="docs/track_d/SCM_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001.md",
        ),
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="readout_compatibility_001",
            evidence_category="readout_compatibility",
            artifact_ref="panel_exp/validation/trusted_readout_report_runtime_001.py",
        ),
    ]


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="validation_sample",
            catalog_alias=CATALOG_ALIAS,
            evidence_refs=_sample_references(),
            lineage={"runtime": _ARTIFACT_ID},
        )
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT
    )
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_jackknife_null_monitor_promotion_evidence_packet_runtime",
        "lane": "Lane A - Method instrument promotion framework application",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "catalog_alias": CATALOG_ALIAS,
        "depends_on": [
            "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001",
            "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001",
            "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "evidence_packet_runtime_implemented": True,
        "exact_instrument_identity_enforced": True,
        "catalog_alias_reconciled_without_substitution": True,
        "required_evidence_categories_validated": True,
        "scm_specific_categories_validated": True,
        "packet_readiness_statuses_emitted": True,
        "promotion_review_eligibility_emitted": True,
        "missing_evidence_preserved": True,
        "blockers_preserved": True,
        "warnings_lineage_preserved": True,
        "evidence_substitution_rules_enforced": True,
        "evidence_quality_boundary_preserved": True,
        "runtime_implemented": True,
        "scm_promoted": False,
        "scm_jackknife_promoted": False,
        "method_promoted": False,
        "instrument_promoted": False,
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
        description="SCM Jackknife null-monitor promotion evidence packet assembly validation"
    )
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
