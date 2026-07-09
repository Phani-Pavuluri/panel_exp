"""TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001 — evidence packet assembly runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001"
_SCOPE = "evidence_packet_assembly_runtime_no_promotion_no_claim_authorization"
_VERDICT = "tbrridge_promotion_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"
_RECOMMENDED_NEXT = "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001_summary.json"
)

EXACT_INSTRUMENT_IDENTITY = (
    "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
)

_LANE_B_ONLY_CATEGORIES = frozenset(
    {
        "post_test_spend",
        "spend_readiness",
        "spend_delta",
        "efficiency_metric_readiness",
        "roi_readiness",
        "lane_b_spend",
    }
)

_REQUIRED_CATEGORIES = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "directional_error",
    "positive_control_recovery",
    "sensitivity",
    "readout_compatibility",
)

_CATEGORY_MISSING_BLOCKER = {
    "instrument_identity": "BLOCKED_MISSING_INSTRUMENT_IDENTITY",
    "claim_boundary": "BLOCKED_MISSING_CLAIM_BOUNDARY",
    "metric_estimand_alignment": "BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT",
    "null_control_false_positive": "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE",
    "directional_error": "BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE",
    "positive_control_recovery": "BLOCKED_MISSING_POSITIVE_CONTROL_EVIDENCE",
    "sensitivity": "BLOCKED_MISSING_SENSITIVITY_EVIDENCE",
    "readout_compatibility": "BLOCKED_MISSING_READOUT_COMPATIBILITY",
}

_ALLOWED_SURFACES = (
    "DIAGNOSTIC_STATUS_SUMMARY",
    "EVIDENCE_COMPLETENESS_SUMMARY",
    "BLOCKER_SUMMARY",
    "RESTRICTED_REVIEW_READINESS_SUMMARY",
    "METHOD_PROMOTION_REVIEW_INPUT_DESCRIPTION",
    "FUTURE_EVIDENCE_PACKET_INPUT_DESCRIPTION",
)

_PROHIBITED_SURFACES = (
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "STATISTICAL_POWER_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "BUSINESS_LIFT_CLAIM",
    "ROI_CLAIM",
    "DECISION_RECOMMENDATION",
    "PRODUCTION_READOUT",
    "CATALOG_UNBLOCK_NOTICE",
    "METHOD_PROMOTION_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "UNCERTAINTY_APPROVAL_NOTICE",
)

_PRODUCTION_SURFACES = frozenset(
    {
        "production",
        "production_readout",
        "PRODUCTION_READOUT",
        "production_review",
    }
)


class TBRRidgePacketReadinessStatus(str, Enum):
    PACKET_READY_FOR_PROMOTION_REVIEW_INPUT = "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT"
    PACKET_PARTIAL_DIAGNOSTIC_ONLY = "PACKET_PARTIAL_DIAGNOSTIC_ONLY"
    PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE = "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE"
    PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING = "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING"
    PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH = "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH"
    PACKET_BLOCKED_UNSUPPORTED_SURFACE = "PACKET_BLOCKED_UNSUPPORTED_SURFACE"
    PACKET_BLOCKED_CROSS_INFERENCE_FAMILY = "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY"
    PACKET_BLOCKED_CROSS_GEOMETRY = "PACKET_BLOCKED_CROSS_GEOMETRY"
    PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED = (
        "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED"
    )
    PACKET_NOT_REQUESTED = "PACKET_NOT_REQUESTED"


class TBRRidgePromotionReviewEligibilityStatus(str, Enum):
    ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT = "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT"
    NOT_ELIGIBLE_MISSING_EVIDENCE = "NOT_ELIGIBLE_MISSING_EVIDENCE"
    NOT_ELIGIBLE_IDENTITY_MISMATCH = "NOT_ELIGIBLE_IDENTITY_MISMATCH"
    NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING = "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING"
    NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW = "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW"
    NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK = "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK"


@dataclass(frozen=True)
class TBRRidgeEvidenceReference:
    evidence_category: str
    artifact_id: str
    artifact_ref: str
    status: str | None = None
    summary: str | None = None
    lineage: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TBRRidgePromotionEvidencePacketInput:
    packet_id: str
    instrument_identity: str
    evidence_references: tuple[TBRRidgeEvidenceReference, ...]
    requested_surface: str = "restricted_review"
    requested_geometry: str = "single_cell"
    requested_inference_family: str = "kfold"
    requested_estimator_family: str = "tbrridge"
    created_from_artifacts: tuple[str, ...] = ()
    lineage: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class TBRRidgePromotionEvidencePacket:
    packet_id: str
    instrument_identity: str
    estimator_family: str
    inference_family: str
    geometry: str
    estimand: str
    interval_semantics: str
    surface: str
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    claim_authorization_boundary_report_ref: str | None
    evidence_by_category: dict[str, tuple[dict[str, Any], ...]]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    packet_readiness_status: TBRRidgePacketReadinessStatus
    promotion_review_eligibility_status: TBRRidgePromotionReviewEligibilityStatus
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["packet_readiness_status"] = self.packet_readiness_status.value
        payload["promotion_review_eligibility_status"] = (
            self.promotion_review_eligibility_status.value
        )
        return payload


def _parse_identity(identity: str) -> dict[str, str] | None:
    parts = identity.split(".")
    if len(parts) != 7:
        return None
    return {
        "modality": parts[0],
        "estimator_family": parts[1],
        "inference_family": parts[2],
        "geometry": parts[3],
        "estimand": parts[4],
        "interval_semantics": parts[5],
        "surface": parts[6],
    }


def _ref_valid(ref: TBRRidgeEvidenceReference) -> bool:
    if ref.evidence_category in _LANE_B_ONLY_CATEGORIES:
        return False
    if not str(ref.artifact_id).strip():
        return False
    if not str(ref.artifact_ref).strip():
        return False
    return True


def _ref_to_dict(ref: TBRRidgeEvidenceReference) -> dict[str, Any]:
    return asdict(ref)


def _group_evidence(
    refs: tuple[TBRRidgeEvidenceReference, ...],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        cat = str(ref.evidence_category).strip()
        grouped.setdefault(cat, []).append(_ref_to_dict(ref))
    return grouped


def assemble_tbrridge_promotion_evidence_packet(
    inp: TBRRidgePromotionEvidencePacketInput,
) -> TBRRidgePromotionEvidencePacket:
    """Assemble a governed TBRRidge promotion evidence packet from explicit references."""
    warnings = list(inp.warnings)
    blockers: list[str] = []
    missing: list[str] = []

    parsed = _parse_identity(inp.instrument_identity)
    exact_parsed = _parse_identity(EXACT_INSTRUMENT_IDENTITY)

    if inp.instrument_identity != EXACT_INSTRUMENT_IDENTITY or parsed is None:
        return _blocked_packet(
            inp,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
            blockers=("INSTRUMENT_IDENTITY_MISMATCH",),
            missing_evidence=("instrument_identity",),
            evidence_by_category=_group_evidence(inp.evidence_references),
            warnings=warnings,
        )

    surface = str(inp.requested_surface).strip().lower()
    if surface in _PRODUCTION_SURFACES or surface not in {"restricted_review", "restricted-review"}:
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW,
            blockers=("UNSUPPORTED_SURFACE_REQUESTED",),
            evidence_by_category=_group_evidence(inp.evidence_references),
            warnings=warnings,
        )

    if str(inp.requested_inference_family).strip().lower() != "kfold":
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
            blockers=("CROSS_INFERENCE_FAMILY_NOT_ALLOWED",),
            evidence_by_category=_group_evidence(inp.evidence_references),
            warnings=warnings,
        )

    if str(inp.requested_geometry).strip().lower() != "single_cell":
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
            blockers=("CROSS_GEOMETRY_NOT_ALLOWED",),
            evidence_by_category=_group_evidence(inp.evidence_references),
            warnings=warnings,
        )

    if str(inp.requested_estimator_family).strip().lower() != "tbrridge":
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH,
            blockers=("ESTIMATOR_FAMILY_MISMATCH",),
            evidence_by_category=_group_evidence(inp.evidence_references),
            warnings=warnings,
        )

    grouped = _group_evidence(inp.evidence_references)
    valid_by_category: dict[str, list[dict[str, Any]]] = {}

    for cat, refs in grouped.items():
        if cat in _LANE_B_ONLY_CATEGORIES:
            blockers.append(f"LANE_B_EVIDENCE_NOT_METHOD_VALIDITY:{cat}")
            warnings.append(f"LANE_B_EVIDENCE_CANNOT_SUBSTITUTE_METHOD_VALIDITY:{cat}")
            continue
        valid_refs = [r for r in refs if _ref_valid_from_dict(r)]
        if valid_refs:
            valid_by_category[cat] = valid_refs

    for cat in _REQUIRED_CATEGORIES:
        if cat not in valid_by_category:
            missing.append(cat)
            blockers.append(_CATEGORY_MISSING_BLOCKER[cat])

    if "claim_boundary" in missing:
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING,
            blockers=tuple(sorted(set(blockers))),
            missing_evidence=tuple(missing),
            evidence_by_category=valid_by_category,
            warnings=warnings,
        )

    if missing:
        return _blocked_packet(
            inp,
            parsed=parsed,
            readiness=TBRRidgePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE,
            eligibility=TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
            blockers=tuple(sorted(set(blockers))),
            missing_evidence=tuple(missing),
            evidence_by_category=valid_by_category,
            warnings=warnings,
        )

    claim_boundary_ref = valid_by_category["claim_boundary"][0].get("artifact_ref")
    evidence_by_category = {k: tuple(v) for k, v in valid_by_category.items()}

    return TBRRidgePromotionEvidencePacket(
        packet_id=inp.packet_id,
        instrument_identity=EXACT_INSTRUMENT_IDENTITY,
        estimator_family=parsed["estimator_family"],
        inference_family=parsed["inference_family"],
        geometry=parsed["geometry"],
        estimand=parsed["estimand"],
        interval_semantics=parsed["interval_semantics"],
        surface=parsed["surface"],
        allowed_surfaces=_ALLOWED_SURFACES,
        prohibited_surfaces=_PROHIBITED_SURFACES,
        claim_authorization_boundary_report_ref=str(claim_boundary_ref) if claim_boundary_ref else None,
        evidence_by_category=evidence_by_category,
        missing_evidence=(),
        blockers=(),
        warnings=tuple(sorted(set(warnings))),
        packet_readiness_status=TBRRidgePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT,
        promotion_review_eligibility_status=(
            TBRRidgePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT
        ),
        lineage=dict(inp.lineage),
        created_from_artifacts=tuple(inp.created_from_artifacts),
    )


def _ref_valid_from_dict(ref: dict[str, Any]) -> bool:
    cat = str(ref.get("evidence_category", "")).strip()
    if cat in _LANE_B_ONLY_CATEGORIES:
        return False
    if not str(ref.get("artifact_id", "")).strip():
        return False
    if not str(ref.get("artifact_ref", "")).strip():
        return False
    return True


def _blocked_packet(
    inp: TBRRidgePromotionEvidencePacketInput,
    *,
    readiness: TBRRidgePacketReadinessStatus,
    eligibility: TBRRidgePromotionReviewEligibilityStatus,
    blockers: tuple[str, ...],
    evidence_by_category: dict[str, list[dict[str, Any]]] | dict[str, tuple[dict[str, Any], ...]],
    warnings: list[str],
    missing_evidence: tuple[str, ...] = (),
    parsed: dict[str, str] | None = None,
) -> TBRRidgePromotionEvidencePacket:
    parsed = parsed or _parse_identity(inp.instrument_identity) or {
        "estimator_family": inp.requested_estimator_family,
        "inference_family": inp.requested_inference_family,
        "geometry": inp.requested_geometry,
        "estimand": "delta_mu",
        "interval_semantics": "diagnostic_interval",
        "surface": inp.requested_surface,
    }
    normalized = {
        k: tuple(v) if isinstance(v, list) else v for k, v in evidence_by_category.items()
    }
    claim_ref = None
    if "claim_boundary" in normalized and normalized["claim_boundary"]:
        claim_ref = normalized["claim_boundary"][0].get("artifact_ref")
    return TBRRidgePromotionEvidencePacket(
        packet_id=inp.packet_id,
        instrument_identity=inp.instrument_identity,
        estimator_family=parsed.get("estimator_family", "tbrridge"),
        inference_family=parsed.get("inference_family", "kfold"),
        geometry=parsed.get("geometry", "single_cell"),
        estimand=parsed.get("estimand", "delta_mu"),
        interval_semantics=parsed.get("interval_semantics", "diagnostic_interval"),
        surface=parsed.get("surface", "restricted_review"),
        allowed_surfaces=_ALLOWED_SURFACES,
        prohibited_surfaces=_PROHIBITED_SURFACES,
        claim_authorization_boundary_report_ref=str(claim_ref) if claim_ref else None,
        evidence_by_category=normalized,
        missing_evidence=missing_evidence,
        blockers=blockers,
        warnings=tuple(sorted(set(warnings))),
        packet_readiness_status=readiness,
        promotion_review_eligibility_status=eligibility,
        lineage=dict(inp.lineage),
        created_from_artifacts=tuple(inp.created_from_artifacts),
    )


def _sample_references() -> tuple[TBRRidgeEvidenceReference, ...]:
    return (
        TBRRidgeEvidenceReference(
            evidence_category="instrument_identity",
            artifact_id="METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001",
            artifact_ref="docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="claim_boundary",
            artifact_id="TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="metric_estimand_alignment",
            artifact_id="TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="null_control_false_positive",
            artifact_id="TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="directional_error",
            artifact_id="TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="positive_control_recovery",
            artifact_id="TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="sensitivity",
            artifact_id="TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001",
            artifact_ref="docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="readout_compatibility",
            artifact_id="TRUSTED_READOUT_REPORT_RUNTIME_001",
            artifact_ref="panel_exp/validation/trusted_readout_report_runtime_001.py",
        ),
    )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="validation_sample",
            instrument_identity=EXACT_INSTRUMENT_IDENTITY,
            evidence_references=_sample_references(),
            lineage={"runtime": _ARTIFACT_ID},
        )
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
    )
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_promotion_evidence_packet_assembly_runtime",
        "lane": "Lane A - Method instrument promotion",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "instrument_identity": EXACT_INSTRUMENT_IDENTITY,
        "depends_on": [
            "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001",
            "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001",
            "METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001",
            "METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "evidence_packet_runtime_implemented": True,
        "exact_instrument_identity_enforced": True,
        "required_evidence_categories_validated": True,
        "claim_boundary_required": True,
        "missing_evidence_blockers_emitted": True,
        "promotion_review_eligibility_emitted": True,
        "allowed_surfaces_preserved": True,
        "prohibited_surfaces_preserved": True,
        "lane_b_not_substituted_for_method_validity": True,
        "no_evidence_fabrication": True,
        "method_promoted": False,
        "instrument_promoted": False,
        "catalog_unblocked": False,
        "production_compatibility_authorized": False,
        "claim_authorization_changed": False,
        "statistical_claim_authorized": False,
        "confidence_interval_claim_authorized": False,
        "p_value_claim_authorized": False,
        "significance_claim_authorized": False,
        "causal_lift_claim_authorized": False,
        "business_lift_claim_authorized": False,
        "roi_roas_claim_authorized": False,
        "decision_recommendation_authorized": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "new_validation_experiments_run": False,
        "lane_b_runtime_changed": False,
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
    parser = argparse.ArgumentParser(description="TBRRidge promotion evidence packet assembly validation")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
