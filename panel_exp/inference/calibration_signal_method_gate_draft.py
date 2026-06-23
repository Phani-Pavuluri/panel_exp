"""CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001 — draft CalibrationSignal method gate.

Maps Method Readiness Matrix V2 tiers into future CalibrationSignal eligibility rules.
Draft review map only — no signal creation, export, or downstream authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.inference.method_readiness_matrix_v2 import (
    MethodReadinessMatrixRow,
    MethodReadinessMatrixV2,
    ReadinessTier,
    build_method_readiness_matrix_v2,
)

_ARTIFACT_ID = "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001"
_SOURCE_MATRIX_ARTIFACT_ID = "METHOD_READINESS_MATRIX_V2_001"
_VERDICT = "calibration_signal_method_gate_draft_defined_no_authorization"

DRAFT_GATE_WARNING = (
    "CalibrationSignal method gate draft only — future-review eligible does not mean "
    "signal-ready; no CalibrationSignal creation, export, or downstream authorization."
)

FORBIDDEN_DRAFT_OUTPUTS = (
    "actual_calibration_signal_creation",
    "calibration_signal_export",
    "mmm_ingestion",
    "llm_decisioning",
    "production_decisioning",
    "live_api_execution",
    "scheduler_execution",
    "budget_optimization",
)

DOWNSTREAM_FLAG_KEYS = (
    "calibration_signal_allowed",
    "calibration_signal_authorized",
    "trustreport_authorized",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


class CalibrationSignalGateStatus(str, Enum):
    ELIGIBLE_FOR_FUTURE_REVIEW = "eligible_for_future_review"
    CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE = (
        "conditionally_reviewable_after_additional_evidence"
    )
    NOT_ELIGIBLE_DIAGNOSTIC_ONLY = "not_eligible_diagnostic_only"
    NOT_ELIGIBLE_SENSITIVITY_ONLY = "not_eligible_sensitivity_only"
    NOT_ELIGIBLE_CONTRACT_ONLY = "not_eligible_contract_only"
    NOT_ELIGIBLE_UNRESOLVED_MULTIPLICITY_DEPENDENCE = (
        "not_eligible_unresolved_multiplicity_dependence"
    )
    NOT_ELIGIBLE_RESEARCH_DEFERRED = "not_eligible_research_deferred"
    NOT_ELIGIBLE_BLOCKED = "not_eligible_blocked"


class CalibrationSignalDraftUseBoundary(str, Enum):
    DRAFT_REVIEW_MAP_ONLY = "draft_review_map_only"
    FUTURE_REVIEW_ONLY_NO_SIGNAL_CREATION = "future_review_only_no_signal_creation"
    NOT_REVIEWABLE = "not_reviewable"
    BLOCKED_FROM_CALIBRATION_SIGNAL = "blocked_from_calibration_signal"


class CalibrationSignalRequiredEvidence(str, Enum):
    FINAL_METHOD_VALIDATION = "final_method_validation"
    TRUSTREPORT_AUTHORIZATION = "trustreport_authorization"
    ESTIMAND_COMPATIBILITY = "estimand_compatibility"
    LIFT_SCALE_COMPATIBILITY = "lift_scale_compatibility"
    UNCERTAINTY_CONTRACT = "uncertainty_contract"
    FRESHNESS_POLICY = "freshness_policy"
    CONFLICT_POLICY = "conflict_policy"
    METHOD_VERSION_PROVENANCE = "method_version_provenance"
    DOWNSTREAM_CONSUMPTION_POLICY = "downstream_consumption_policy"
    PRODUCTION_REVIEW_SIGNOFF = "production_review_signoff"


FULL_REVIEW_EVIDENCE = (
    CalibrationSignalRequiredEvidence.FINAL_METHOD_VALIDATION,
    CalibrationSignalRequiredEvidence.TRUSTREPORT_AUTHORIZATION,
    CalibrationSignalRequiredEvidence.ESTIMAND_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.LIFT_SCALE_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.UNCERTAINTY_CONTRACT,
    CalibrationSignalRequiredEvidence.FRESHNESS_POLICY,
    CalibrationSignalRequiredEvidence.CONFLICT_POLICY,
    CalibrationSignalRequiredEvidence.METHOD_VERSION_PROVENANCE,
    CalibrationSignalRequiredEvidence.DOWNSTREAM_CONSUMPTION_POLICY,
    CalibrationSignalRequiredEvidence.PRODUCTION_REVIEW_SIGNOFF,
)

FRAMEWORK_CANDIDATE_EVIDENCE = (
    CalibrationSignalRequiredEvidence.FINAL_METHOD_VALIDATION,
    CalibrationSignalRequiredEvidence.TRUSTREPORT_AUTHORIZATION,
    CalibrationSignalRequiredEvidence.ESTIMAND_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.LIFT_SCALE_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.UNCERTAINTY_CONTRACT,
    CalibrationSignalRequiredEvidence.METHOD_VERSION_PROVENANCE,
    CalibrationSignalRequiredEvidence.PRODUCTION_REVIEW_SIGNOFF,
)

PER_CELL_EVIDENCE = (
    CalibrationSignalRequiredEvidence.ESTIMAND_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.DOWNSTREAM_CONSUMPTION_POLICY,
)

HETEROGENEITY_EVIDENCE = (
    CalibrationSignalRequiredEvidence.FINAL_METHOD_VALIDATION,
    CalibrationSignalRequiredEvidence.ESTIMAND_COMPATIBILITY,
    CalibrationSignalRequiredEvidence.PRODUCTION_REVIEW_SIGNOFF,
)


@dataclass(frozen=True)
class CalibrationSignalGateDraftRow:
    method_id: str
    readiness_tier: str
    method_family: str
    inference_mode: str
    geometry: str
    usage_boundary: str
    gate_status: CalibrationSignalGateStatus
    draft_use_boundary: CalibrationSignalDraftUseBoundary
    required_evidence_before_review: tuple[CalibrationSignalRequiredEvidence, ...]
    categorical_exclusion_reasons: tuple[str, ...]
    allowed_draft_outputs: tuple[str, ...]
    forbidden_outputs: tuple[str, ...]
    source_readiness_evidence: tuple[str, ...]
    calibration_signal_allowed: bool = False
    calibration_signal_authorized: bool = False
    trustreport_authorized: bool = False
    mmm_ingestion_allowed: bool = False
    llm_decisioning_allowed: bool = False
    production_decisioning_allowed: bool = False
    live_api_authorized: bool = False
    scheduler_authorized: bool = False
    budget_optimization_allowed: bool = False


@dataclass(frozen=True)
class CalibrationSignalMethodGateDraft:
    artifact_id: str
    rows: tuple[CalibrationSignalGateDraftRow, ...]
    verdict: str
    source_matrix_artifact_id: str
    gate_status_counts: Mapping[str, int]
    downstream_authorization_flags: Mapping[str, bool]
    warnings: tuple[str, ...]


def _downstream_flags_false() -> dict[str, bool]:
    return {k: False for k in DOWNSTREAM_FLAG_KEYS}


def map_readiness_tier_to_calibration_gate_status(
    readiness_tier: str,
) -> CalibrationSignalGateStatus:
    """Map a Method Readiness Matrix V2 tier to a draft CalibrationSignal gate status."""
    mapping = {
        ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE.value: (
            CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW
        ),
        ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE.value: (
            CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
        ),
        ReadinessTier.PER_CELL_MARGINAL_ONLY.value: (
            CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
        ),
        ReadinessTier.CONTRACT_CANDIDATE.value: (
            CalibrationSignalGateStatus.NOT_ELIGIBLE_CONTRACT_ONLY
        ),
        ReadinessTier.DIAGNOSTIC_ONLY.value: (
            CalibrationSignalGateStatus.NOT_ELIGIBLE_DIAGNOSTIC_ONLY
        ),
        ReadinessTier.SENSITIVITY_ONLY.value: (
            CalibrationSignalGateStatus.NOT_ELIGIBLE_SENSITIVITY_ONLY
        ),
        ReadinessTier.HETEROGENEITY_REVIEW_REQUIRED.value: (
            CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
        ),
        ReadinessTier.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED.value: (
            CalibrationSignalGateStatus.NOT_ELIGIBLE_UNRESOLVED_MULTIPLICITY_DEPENDENCE
        ),
        ReadinessTier.RESEARCH_DEFERRED.value: (
            CalibrationSignalGateStatus.NOT_ELIGIBLE_RESEARCH_DEFERRED
        ),
        ReadinessTier.BLOCKED.value: CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED,
    }
    return mapping.get(readiness_tier, CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED)


def _draft_use_boundary(
    gate_status: CalibrationSignalGateStatus,
) -> CalibrationSignalDraftUseBoundary:
    if gate_status == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW:
        return CalibrationSignalDraftUseBoundary.FUTURE_REVIEW_ONLY_NO_SIGNAL_CREATION
    if gate_status == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE:
        return CalibrationSignalDraftUseBoundary.FUTURE_REVIEW_ONLY_NO_SIGNAL_CREATION
    if gate_status in {
        CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED,
        CalibrationSignalGateStatus.NOT_ELIGIBLE_UNRESOLVED_MULTIPLICITY_DEPENDENCE,
    }:
        return CalibrationSignalDraftUseBoundary.BLOCKED_FROM_CALIBRATION_SIGNAL
    return CalibrationSignalDraftUseBoundary.NOT_REVIEWABLE


def _required_evidence(
    row: MethodReadinessMatrixRow,
    gate_status: CalibrationSignalGateStatus,
) -> tuple[CalibrationSignalRequiredEvidence, ...]:
    tier = row.readiness_tier.value
    if tier == ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE.value:
        return FULL_REVIEW_EVIDENCE
    if tier == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE.value:
        return FRAMEWORK_CANDIDATE_EVIDENCE
    if tier == ReadinessTier.PER_CELL_MARGINAL_ONLY.value:
        return (
            *PER_CELL_EVIDENCE,
            CalibrationSignalRequiredEvidence.FINAL_METHOD_VALIDATION,
            CalibrationSignalRequiredEvidence.PRODUCTION_REVIEW_SIGNOFF,
        )
    if tier == ReadinessTier.HETEROGENEITY_REVIEW_REQUIRED.value:
        return HETEROGENEITY_EVIDENCE
    if gate_status in {
        CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW,
        CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE,
    }:
        return FRAMEWORK_CANDIDATE_EVIDENCE
    return ()


def _exclusion_reasons(
    row: MethodReadinessMatrixRow,
    gate_status: CalibrationSignalGateStatus,
) -> tuple[str, ...]:
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_DIAGNOSTIC_ONLY:
        return ("diagnostic_only_rows_cannot_produce_calibration_signal",)
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_SENSITIVITY_ONLY:
        return ("sensitivity_only_rows_cannot_produce_calibration_signal",)
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_CONTRACT_ONLY:
        return ("contract_only_rows_are_not_inference_authorization",)
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_UNRESOLVED_MULTIPLICITY_DEPENDENCE:
        return (
            "multiplicity_or_shared_control_dependence_unresolved",
            *row.blocked_reasons,
        )
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_RESEARCH_DEFERRED:
        return ("research_deferred_pending_method_evidence",)
    if gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED:
        return row.blocked_reasons or ("blocked_from_governed_causal_evidence",)
    return ()


def _allowed_draft_outputs(gate_status: CalibrationSignalGateStatus) -> tuple[str, ...]:
    if gate_status == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW:
        return ("draft_future_review_eligibility_map",)
    if gate_status == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE:
        return ("draft_conditional_review_map", "required_evidence_checklist")
    return ("draft_exclusion_map",)


def _map_matrix_row(row: MethodReadinessMatrixRow) -> CalibrationSignalGateDraftRow:
    gate_status = map_readiness_tier_to_calibration_gate_status(row.readiness_tier.value)
    required = _required_evidence(row, gate_status)
    exclusions = _exclusion_reasons(row, gate_status)
    source_evidence = tuple(ref.artifact_id for ref in row.evidence_refs)

    per_cell_notes: tuple[str, ...] = ()
    if row.method_id == "multicell_per_cell_marginal_only":
        per_cell_notes = (
            "per_cell_only_calibration_signal_scope_rule",
            "no_global_winner_pooled_claim_enforcement",
            "multiplicity_boundary",
        )

    return CalibrationSignalGateDraftRow(
        method_id=row.method_id,
        readiness_tier=row.readiness_tier.value,
        method_family=row.method_family.value,
        inference_mode=row.inference_mode.value,
        geometry=row.geometry.value,
        usage_boundary=row.usage_boundary.value,
        gate_status=gate_status,
        draft_use_boundary=_draft_use_boundary(gate_status),
        required_evidence_before_review=required,
        categorical_exclusion_reasons=exclusions + per_cell_notes,
        allowed_draft_outputs=_allowed_draft_outputs(gate_status),
        forbidden_outputs=FORBIDDEN_DRAFT_OUTPUTS,
        source_readiness_evidence=source_evidence,
    )


def _gate_status_counts(
    rows: tuple[CalibrationSignalGateDraftRow, ...],
) -> dict[str, int]:
    counts: dict[str, int] = {status.value: 0 for status in CalibrationSignalGateStatus}
    for row in rows:
        counts[row.gate_status.value] += 1
    return counts


def build_calibration_signal_method_gate_draft(
    matrix: object | None = None,
) -> CalibrationSignalMethodGateDraft:
    """Build draft CalibrationSignal method gate from Method Readiness Matrix V2."""
    source = matrix if isinstance(matrix, MethodReadinessMatrixV2) else build_method_readiness_matrix_v2()
    rows = tuple(_map_matrix_row(row) for row in source.rows)
    return CalibrationSignalMethodGateDraft(
        artifact_id=_ARTIFACT_ID,
        rows=rows,
        verdict=_VERDICT,
        source_matrix_artifact_id=_SOURCE_MATRIX_ARTIFACT_ID,
        gate_status_counts=_gate_status_counts(rows),
        downstream_authorization_flags=_downstream_flags_false(),
        warnings=(DRAFT_GATE_WARNING,),
    )


def find_calibration_gate_row(
    draft: CalibrationSignalMethodGateDraft,
    method_id: str,
) -> CalibrationSignalGateDraftRow | None:
    """Return draft gate row by method_id, or None if not found."""
    for row in draft.rows:
        if row.method_id == method_id:
            return row
    return None


def filter_calibration_gate_rows(
    draft: CalibrationSignalMethodGateDraft,
    gate_status: CalibrationSignalGateStatus | None = None,
    method_family: str | None = None,
) -> tuple[CalibrationSignalGateDraftRow, ...]:
    """Filter draft gate rows by status and/or method family."""
    result: list[CalibrationSignalGateDraftRow] = []
    for row in draft.rows:
        if gate_status is not None and row.gate_status != gate_status:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        result.append(row)
    return tuple(result)


def _serialize_row(row: CalibrationSignalGateDraftRow) -> dict[str, Any]:
    return {
        "method_id": row.method_id,
        "readiness_tier": row.readiness_tier,
        "method_family": row.method_family,
        "inference_mode": row.inference_mode,
        "geometry": row.geometry,
        "usage_boundary": row.usage_boundary,
        "gate_status": row.gate_status.value,
        "draft_use_boundary": row.draft_use_boundary.value,
        "required_evidence_before_review": [e.value for e in row.required_evidence_before_review],
        "categorical_exclusion_reasons": list(row.categorical_exclusion_reasons),
        "allowed_draft_outputs": list(row.allowed_draft_outputs),
        "forbidden_outputs": list(row.forbidden_outputs),
        "source_readiness_evidence": list(row.source_readiness_evidence),
        "calibration_signal_allowed": row.calibration_signal_allowed,
        "calibration_signal_authorized": row.calibration_signal_authorized,
        "trustreport_authorized": row.trustreport_authorized,
        "mmm_ingestion_allowed": row.mmm_ingestion_allowed,
        "llm_decisioning_allowed": row.llm_decisioning_allowed,
        "production_decisioning_allowed": row.production_decisioning_allowed,
        "live_api_authorized": row.live_api_authorized,
        "scheduler_authorized": row.scheduler_authorized,
        "budget_optimization_allowed": row.budget_optimization_allowed,
    }


def summarize_calibration_signal_method_gate_draft(
    draft: CalibrationSignalMethodGateDraft,
) -> dict[str, Any]:
    """Serialize draft CalibrationSignal method gate for validation archives."""
    return {
        "artifact_id": draft.artifact_id,
        "verdict": draft.verdict,
        "source_matrix_artifact_id": draft.source_matrix_artifact_id,
        "row_count": len(draft.rows),
        "gate_status_counts": dict(draft.gate_status_counts),
        "downstream_authorization_flags": dict(draft.downstream_authorization_flags),
        "warnings": list(draft.warnings),
        "rows": [_serialize_row(row) for row in draft.rows],
    }


def validate_calibration_signal_method_gate_draft(
    draft: CalibrationSignalMethodGateDraft,
) -> dict[str, Any]:
    """Validate draft gate invariants and return structured validation summary."""
    issues: list[str] = []
    matrix = build_method_readiness_matrix_v2()
    source_ids = {row.method_id for row in matrix.rows}
    draft_ids = [row.method_id for row in draft.rows]
    unique_ids = len(draft_ids) == len(set(draft_ids))
    ids_match = set(draft_ids) == source_ids

    if not unique_ids:
        issues.append("duplicate method_id in draft gate")
    if not ids_match:
        missing = sorted(source_ids - set(draft_ids))
        extra = sorted(set(draft_ids) - source_ids)
        if missing:
            issues.append(f"missing source method_ids: {missing}")
        if extra:
            issues.append(f"extra method_ids not in source matrix: {extra}")
    if len(draft.rows) != len(matrix.rows):
        issues.append(
            f"draft row count {len(draft.rows)} != source matrix row count {len(matrix.rows)}"
        )

    reviewable_statuses = {
        CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW,
        CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE,
    }
    not_eligible_prefix = "not_eligible_"

    for row in draft.rows:
        for key in DOWNSTREAM_FLAG_KEYS:
            if getattr(row, key):
                issues.append(f"{row.method_id}: {key} must be false")

        if "actual_calibration_signal_creation" not in row.forbidden_outputs:
            issues.append(f"{row.method_id}: must forbid actual_calibration_signal_creation")
        if "calibration_signal_export" not in row.forbidden_outputs:
            issues.append(f"{row.method_id}: must forbid calibration_signal_export")

        if row.gate_status in reviewable_statuses:
            if not row.required_evidence_before_review:
                issues.append(f"{row.method_id}: reviewable row missing required evidence")
        elif row.gate_status.value.startswith(not_eligible_prefix):
            if not row.categorical_exclusion_reasons:
                issues.append(f"{row.method_id}: ineligible row missing exclusion reasons")

        if row.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY.value:
            if row.gate_status != CalibrationSignalGateStatus.NOT_ELIGIBLE_DIAGNOSTIC_ONLY:
                issues.append(f"{row.method_id}: diagnostic tier must map to not_eligible_diagnostic_only")

        if row.method_id == "multicell_per_cell_marginal_only":
            if row.gate_status != (
                CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
            ):
                issues.append("multicell_per_cell_marginal_only must be conditionally reviewable")

    for key in DOWNSTREAM_FLAG_KEYS:
        if draft.downstream_authorization_flags.get(key):
            issues.append(f"draft downstream flag {key} must be false")

    return {
        "valid": not issues,
        "row_count": len(draft.rows),
        "source_row_count": len(matrix.rows),
        "method_ids_match_source_matrix": ids_match,
        "unique_method_ids": unique_ids,
        "gate_status_counts": dict(draft.gate_status_counts),
        "issues": issues,
    }


__all__ = [
    "CalibrationSignalDraftUseBoundary",
    "CalibrationSignalGateDraftRow",
    "CalibrationSignalGateStatus",
    "CalibrationSignalMethodGateDraft",
    "CalibrationSignalRequiredEvidence",
    "build_calibration_signal_method_gate_draft",
    "filter_calibration_gate_rows",
    "find_calibration_gate_row",
    "map_readiness_tier_to_calibration_gate_status",
    "summarize_calibration_signal_method_gate_draft",
    "validate_calibration_signal_method_gate_draft",
]
