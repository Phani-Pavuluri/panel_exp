"""DESIGN-GUARDRAIL-ENFORCEMENT-001 — authoritative runtime design path enforcement.

Combines contract validation, design guardrails, and combination guardrails into a
single enforcement result. Fail-closed for downstream roles; no bypass API.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from panel_exp.validation.design_combination_guardrail_001 import (
    COMBINATION_STATUS_NOT_EVALUATED,
    DesignCombinationGuardrailResult,
    evaluate_design_combination_guardrails,
)
from panel_exp.validation.design_guardrail_runtime_001 import (
    GUARDRAIL_BLOCK,
    GUARDRAIL_UNKNOWN,
    GUARDRAIL_WARN,
    DesignGuardrailRuntimeResult,
    evaluate_design_contract_guardrails,
)

ENFORCEMENT_VERSION = "1.0.0"

# Contract-layer enforcement reason codes
RC_ENFORCE_MISSING_CONTRACT = "D-ENFORCE-MISSING-CONTRACT"
RC_ENFORCE_CONTRACT_BLOCKED = "D-ENFORCE-CONTRACT-BLOCKED"
RC_ENFORCE_GUARDRAIL_BLOCKED = "D-ENFORCE-GUARDRAIL-BLOCKED"
RC_ENFORCE_DOWNSTREAM_ROLE_BLOCKED = "D-ENFORCE-DOWNSTREAM-ROLE-BLOCKED"
RC_ENFORCE_DOWNSTREAM_AUTH_VIOLATION = "D-ENFORCE-DOWNSTREAM-AUTH-VIOLATION"
RC_ENFORCE_LEGACY_UNKNOWN = "D-ENFORCE-LEGACY-UNKNOWN"
RC_ENFORCE_RESEARCH_ONLY = "D-ENFORCE-RESEARCH-ONLY"

DOWNSTREAM_BLOCKED_ROLES = frozenset(
    {
        "trustreport",
        "trust_report",
        "calibrationsignal",
        "calibration_signal",
        "mmm",
        "llm",
        "production",
        "production_decision",
        "production_recommendation",
        "automated_budget_action",
        "pooled_causal_claim",
    }
)

RESEARCH_ALLOWED_ROLES = frozenset(
    {
        "research",
        "diagnostic",
        "validation",
        "blocked_status_explanation",
    }
)

_DEFAULT_BLOCKED_ROLES = (
    "trust_report",
    "calibration_signal",
    "mmm",
    "llm",
    "production",
    "production_decision",
    "production_recommendation",
    "automated_budget_action",
    "pooled_causal_claim",
)


class DesignGuardrailViolation(RuntimeError):
    """Raised when an enforced execution path is blocked by guardrails."""

    def __init__(
        self,
        message: str,
        *,
        result: "DesignGuardrailEnforcementResult",
    ) -> None:
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class DesignGuardrailEnforcementResult:
    status: str
    severity: str
    allowed: bool
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    blocked_roles: tuple[str, ...]
    design_id: str | None
    estimator_id: str | None
    inference_id: str | None
    geometry_id: str | None
    readout_semantics: str | None
    contract_status: str | None
    design_guardrail_status: str | None
    combination_status: str | None
    combination_id: str | None
    requested_downstream_role: str | None
    downstream_authorization_status: str | None
    enforcement_version: str = ENFORCEMENT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_role(role: str | None) -> str:
    return (role or "").strip().lower().replace("-", "_")


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _severity_from_status(status: str) -> str:
    if status == GUARDRAIL_BLOCK:
        return "BLOCK"
    if status == GUARDRAIL_WARN:
        return "WARN"
    if status == GUARDRAIL_UNKNOWN:
        return "UNKNOWN"
    return status


def _merge_reason_codes(*groups: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for group in groups:
        for code in group:
            if code not in seen:
                seen.append(code)
    return tuple(seen)


def _worst_status(*statuses: str) -> str:
    order = {GUARDRAIL_BLOCK: 3, GUARDRAIL_WARN: 2, GUARDRAIL_UNKNOWN: 1, "PASS": 0}
    worst = GUARDRAIL_UNKNOWN
    worst_rank = -1
    for s in statuses:
        rank = order.get(s, 2)
        if rank > worst_rank:
            worst_rank = rank
            worst = s
    return worst


def _role_allowed(
    *,
    status: str,
    role: str | None,
    combination_status: str | None,
) -> bool:
    normalized = _normalize_role(role)
    if not normalized:
        return False
    if normalized in DOWNSTREAM_BLOCKED_ROLES:
        return False
    if normalized in RESEARCH_ALLOWED_ROLES:
        if status == GUARDRAIL_BLOCK:
            return False
        if combination_status in (
            "blocked_due_to_geometry_mismatch",
            "blocked_for_pooled_claim",
            "blocked_due_to_readout_mismatch",
            "empirically_blocked",
            "adapter_required",
            "bridge_required",
        ):
            return False
        return status in (GUARDRAIL_WARN, "PASS")
    return False


def enforce_design_decision_path(
    *,
    design_contract: Mapping[str, Any] | None = None,
    contract_validation: Mapping[str, Any] | None = None,
    design_guardrail: Mapping[str, Any] | None = None,
    combination_guardrail: Mapping[str, Any] | None = None,
    design_id: str | None = None,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    geometry_id: str | None = None,
    readout_semantics: str | None = None,
    requested_downstream_role: str | None = None,
    readout_claim_type: str | None = None,
    evidence_payload: Mapping[str, Any] | None = None,
) -> DesignGuardrailEnforcementResult:
    """Combine contract, design, and combination guardrails into one enforcement result."""
    contract = design_contract
    validation = contract_validation
    if evidence_payload is not None and _is_mapping(evidence_payload):
        design_block = evidence_payload.get("design")
        if _is_mapping(design_block):
            contract = contract or design_block.get("design_contract")
            validation = validation or design_block.get("contract_validation")
            design_guardrail = design_guardrail or design_block.get("design_guardrail")
            combination_guardrail = combination_guardrail or design_block.get("combination_guardrail")
        contract = contract or evidence_payload.get("design_contract")
        validation = validation or evidence_payload.get("contract_validation")
        design_guardrail = design_guardrail or evidence_payload.get("design_guardrail")
        combination_guardrail = combination_guardrail or evidence_payload.get("combination_guardrail")

    reason_codes: list[str] = []
    warnings: list[str] = []
    blocked_roles = list(_DEFAULT_BLOCKED_ROLES)

    if contract is None:
        reason_codes.append(RC_ENFORCE_MISSING_CONTRACT)
        if requested_downstream_role:
            reason_codes.append(RC_ENFORCE_LEGACY_UNKNOWN)
        status = GUARDRAIL_BLOCK if requested_downstream_role else GUARDRAIL_UNKNOWN
        return DesignGuardrailEnforcementResult(
            status=status,
            severity=_severity_from_status(status),
            allowed=False,
            reason_codes=tuple(reason_codes),
            warnings=tuple(warnings),
            blocked_roles=tuple(blocked_roles),
            design_id=design_id,
            estimator_id=estimator_id,
            inference_id=inference_id,
            geometry_id=geometry_id,
            readout_semantics=readout_semantics,
            contract_status=None,
            design_guardrail_status=None,
            combination_status=COMBINATION_STATUS_NOT_EVALUATED,
            combination_id=None,
            requested_downstream_role=requested_downstream_role,
            downstream_authorization_status=None,
        )

    dg_result: DesignGuardrailRuntimeResult
    if design_guardrail is not None and _is_mapping(design_guardrail):
        dg_result = DesignGuardrailRuntimeResult(**dict(design_guardrail))
    else:
        payload: dict[str, Any] = {"design_contract": dict(contract)}
        if validation is not None:
            payload["contract_validation"] = dict(validation)
        dg_result = evaluate_design_contract_guardrails(payload)

    cg_result: DesignCombinationGuardrailResult
    if combination_guardrail is not None and _is_mapping(combination_guardrail):
        cg_result = DesignCombinationGuardrailResult(**dict(combination_guardrail))
    else:
        cg_result = evaluate_design_combination_guardrails(
            design_contract=contract,
            contract_validation=validation,
            design_guardrail=dg_result.to_dict(),
            design_id=design_id,
            estimator_id=estimator_id,
            inference_id=inference_id,
            geometry_id=geometry_id,
            readout_semantics=readout_semantics,
            requested_downstream_role=requested_downstream_role,
            readout_claim_type=readout_claim_type,
        )

    if dg_result.status == GUARDRAIL_BLOCK:
        reason_codes.append(RC_ENFORCE_GUARDRAIL_BLOCKED)
        if dg_result.contract_status in ("contract_blocked", "contract_incomplete"):
            reason_codes.append(RC_ENFORCE_CONTRACT_BLOCKED)

    for code in dg_result.reason_codes:
        if code not in reason_codes:
            reason_codes.append(code)

    for code in cg_result.reason_codes:
        if code not in reason_codes:
            reason_codes.append(code)

    warnings.extend(dg_result.warnings)
    warnings.extend(cg_result.warnings)

    for role in dg_result.blocked_roles:
        if role not in blocked_roles:
            blocked_roles.append(role)
    for role in cg_result.blocked_roles:
        if role not in blocked_roles:
            blocked_roles.append(role)

    downstream_auth = dg_result.downstream_authorization_status
    if downstream_auth is not None and str(downstream_auth).lower() not in (
        "blocked",
        "not_authorized",
        None,
    ):
        reason_codes.append(RC_ENFORCE_DOWNSTREAM_AUTH_VIOLATION)
        status = GUARDRAIL_BLOCK
    else:
        status = _worst_status(dg_result.status, cg_result.status)

    if requested_downstream_role:
        role_norm = _normalize_role(requested_downstream_role)
        if role_norm in DOWNSTREAM_BLOCKED_ROLES:
            reason_codes.append(RC_ENFORCE_DOWNSTREAM_ROLE_BLOCKED)
            status = GUARDRAIL_BLOCK
        elif status == GUARDRAIL_UNKNOWN:
            reason_codes.append(RC_ENFORCE_LEGACY_UNKNOWN)
            status = GUARDRAIL_BLOCK

    if status == GUARDRAIL_WARN:
        reason_codes.append(RC_ENFORCE_RESEARCH_ONLY)

    allowed = _role_allowed(
        status=status,
        role=requested_downstream_role,
        combination_status=cg_result.combination_status,
    )

    design_id_resolved = cg_result.design_id or design_id
    if design_id_resolved is None and _is_mapping(contract):
        ident = contract.get("design_identity")
        if _is_mapping(ident):
            design_id_resolved = ident.get("design_inventory_id")

    return DesignGuardrailEnforcementResult(
        status=status,
        severity=_severity_from_status(status),
        allowed=allowed,
        reason_codes=_merge_reason_codes(reason_codes),
        warnings=tuple(warnings),
        blocked_roles=tuple(blocked_roles),
        design_id=str(design_id_resolved) if design_id_resolved else None,
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=cg_result.geometry_id or geometry_id,
        readout_semantics=readout_semantics,
        contract_status=dg_result.contract_status,
        design_guardrail_status=dg_result.status,
        combination_status=cg_result.combination_status,
        combination_id=cg_result.combination_id,
        requested_downstream_role=requested_downstream_role,
        downstream_authorization_status=downstream_auth,
    )


def assert_design_path_allowed(
    enforcement_result: DesignGuardrailEnforcementResult | Mapping[str, Any],
    *,
    requested_role: str,
) -> None:
    """Raise ``DesignGuardrailViolation`` when the requested role is not permitted."""
    if _is_mapping(enforcement_result) and not isinstance(enforcement_result, DesignGuardrailEnforcementResult):
        result = DesignGuardrailEnforcementResult(**dict(enforcement_result))
    else:
        result = enforcement_result  # type: ignore[assignment]

    role_norm = _normalize_role(requested_role)
    if role_norm in DOWNSTREAM_BLOCKED_ROLES:
        raise DesignGuardrailViolation(
            f"Downstream role '{requested_role}' is blocked by design guardrail enforcement.",
            result=result,
        )

    if role_norm in RESEARCH_ALLOWED_ROLES:
        if not _role_allowed(
            status=result.status,
            role=requested_role,
            combination_status=result.combination_status,
        ):
            raise DesignGuardrailViolation(
                f"Research role '{requested_role}' is not permitted (status={result.status}).",
                result=result,
            )
        return

    raise DesignGuardrailViolation(
        f"Unknown or unsupported role '{requested_role}' — fail closed.",
        result=result,
    )


def build_producer_guardrail_bundle(
    *,
    design_contract: Mapping[str, Any] | None,
    contract_validation: Mapping[str, Any] | None,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    geometry_id: str | None = None,
    readout_semantics: str | None = None,
) -> dict[str, Any]:
    """Build design_guardrail, combination_guardrail, and guardrail_enforcement for producers."""
    payload: dict[str, Any] = {}
    if design_contract is not None:
        payload["design_contract"] = dict(design_contract)
    if contract_validation is not None:
        payload["contract_validation"] = dict(contract_validation)

    design_guardrail = evaluate_design_contract_guardrails(payload or {"design_contract": {}})
    combination_guardrail = evaluate_design_combination_guardrails(
        design_contract=design_contract,
        contract_validation=contract_validation,
        design_guardrail=design_guardrail.to_dict(),
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=geometry_id,
        readout_semantics=readout_semantics,
    )
    enforcement = enforce_design_decision_path(
        design_contract=design_contract,
        contract_validation=contract_validation,
        design_guardrail=design_guardrail.to_dict(),
        combination_guardrail=combination_guardrail.to_dict(),
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=geometry_id,
        readout_semantics=readout_semantics,
    )
    return {
        "design_guardrail": design_guardrail.to_dict(),
        "combination_guardrail": combination_guardrail.to_dict(),
        "guardrail_enforcement": enforcement.to_dict(),
    }
