"""DESIGN-GUARDRAIL-RUNTIME-INTEGRATION-001 — runtime design contract guardrails.

Consumes emitted ``design_contract`` and ``contract_validation`` metadata from
tier-1 GeoX design outputs and maps validator state to PASS/WARN/BLOCK guardrail
decisions. Conservative: no downstream promotion, no suitability approval, no
TrustReport/CalibrationSignal/MMM/LLM authorization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from panel_exp.validation.design_contract_builder_001 import (
    contract_validation_summary_from_result,
)
from panel_exp.validation.design_contract_validator_001 import (
    CONTRACT_BLOCKED,
    CONTRACT_INCOMPLETE,
    CONTRACT_UNKNOWN,
    CONTRACT_VALID,
    CONTRACT_VALID_WITH_WARNINGS,
    RC_DOWNSTREAM_AUTH_VIOLATION,
    RC_EMPTY_FORBIDDEN_CLAIMS,
    RC_LEGACY_UNKNOWN,
    RC_MISSING_DESIGN_CONTRACT,
    RC_MISSING_FORBIDDEN_CLAIMS,
    RC_MISSING_GEOMETRY_ID,
    SEVERITY_BLOCK,
    SEVERITY_PASS,
    SEVERITY_UNKNOWN,
    SEVERITY_WARN,
    validate_design_contract,
)

GUARDRAIL_VERSION = "1.0.0"

GUARDRAIL_PASS = "PASS"
GUARDRAIL_WARN = "WARN"
GUARDRAIL_BLOCK = "BLOCK"
GUARDRAIL_UNKNOWN = "UNKNOWN"

# Guardrail reason codes
RC_GUARDRAIL_MISSING_CONTRACT = "D-GUARDRAIL-MISSING-CONTRACT"
RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION = "D-GUARDRAIL-MISSING-CONTRACT-VALIDATION"
RC_GUARDRAIL_CONTRACT_BLOCKED = "D-GUARDRAIL-CONTRACT-BLOCKED"
RC_GUARDRAIL_CONTRACT_INCOMPLETE = "D-GUARDRAIL-CONTRACT-INCOMPLETE"
RC_GUARDRAIL_CONTRACT_UNKNOWN = "D-GUARDRAIL-CONTRACT-UNKNOWN"
RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION = "D-GUARDRAIL-DOWNSTREAM-AUTH-VIOLATION"
RC_GUARDRAIL_CONTRACT_COMPLETE_NOT_ALLOWED = "D-GUARDRAIL-CONTRACT-COMPLETE-NOT-ALLOWED"
RC_GUARDRAIL_OVERCLAIM_TRUSTREPORT = "D-GUARDRAIL-OVERCLAIM-TRUSTREPORT"
RC_GUARDRAIL_OVERCLAIM_CALIBRATION_SIGNAL = "D-GUARDRAIL-OVERCLAIM-CALIBRATION-SIGNAL"
RC_GUARDRAIL_OVERCLAIM_MMM = "D-GUARDRAIL-OVERCLAIM-MMM"
RC_GUARDRAIL_OVERCLAIM_LLM = "D-GUARDRAIL-OVERCLAIM-LLM"
RC_GUARDRAIL_OVERCLAIM_PRODUCTION = "D-GUARDRAIL-OVERCLAIM-PRODUCTION"
RC_GUARDRAIL_REQUIRES_STATISTICAL_VALIDATION = "D-GUARDRAIL-REQUIRES-STATISTICAL-VALIDATION"
RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN = "D-GUARDRAIL-LEGACY-CONTRACT-UNKNOWN"

_ALLOWED_DOWNSTREAM_AUTH = frozenset({"blocked", "not_authorized"})

_OVERCLAIM_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("governance.trust_report_eligible", RC_GUARDRAIL_OVERCLAIM_TRUSTREPORT, "trust_report"),
    ("compatibility.trust_report_eligible", RC_GUARDRAIL_OVERCLAIM_TRUSTREPORT, "trust_report"),
    ("governance.calibration_signal_eligible", RC_GUARDRAIL_OVERCLAIM_CALIBRATION_SIGNAL, "calibration_signal"),
    ("compatibility.calibration_signal_eligible", RC_GUARDRAIL_OVERCLAIM_CALIBRATION_SIGNAL, "calibration_signal"),
    ("governance.mmm_ready", RC_GUARDRAIL_OVERCLAIM_MMM, "mmm"),
    ("compatibility.mmm_eligible", RC_GUARDRAIL_OVERCLAIM_MMM, "mmm"),
    ("governance.llm_authorized", RC_GUARDRAIL_OVERCLAIM_LLM, "llm"),
    ("compatibility.llm_authorized", RC_GUARDRAIL_OVERCLAIM_LLM, "llm"),
    ("governance.production_ready", RC_GUARDRAIL_OVERCLAIM_PRODUCTION, "production"),
    ("governance.causal_readout_authorized", RC_GUARDRAIL_OVERCLAIM_PRODUCTION, "production"),
)


@dataclass
class DesignGuardrailRuntimeResult:
    status: str = GUARDRAIL_BLOCK
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked_roles: list[str] = field(
        default_factory=lambda: [
            "trust_report",
            "calibration_signal",
            "mmm",
            "llm",
            "production",
        ]
    )
    contract_status: str | None = None
    contract_severity: str | None = None
    contract_complete_allowed: bool = False
    downstream_authorization_status: str | None = None
    guardrail_version: str = GUARDRAIL_VERSION
    source: str = "unknown"
    suitability_may_proceed: bool = False
    downstream_may_proceed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _nested_get(data: Mapping[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not _is_mapping(current) or part not in current:
            return None
        current = current[part]
    return current


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _is_contract_validation_summary(payload: Mapping[str, Any]) -> bool:
    return (
        "status" in payload
        and "severity" in payload
        and "contract_complete_allowed" in payload
        and "design_contract" not in payload
        and "schema_name" not in payload
    )


def _is_standalone_contract(payload: Mapping[str, Any]) -> bool:
    return payload.get("schema_name") == "DESIGN-CONTRACT-SCHEMA-001" or (
        payload.get("artifact_type") == "design_output_contract"
        and "design_identity" in payload
    )


def _extract_contract_and_validation(
    payload: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    if "design_contract" in payload:
        contract = payload["design_contract"]
        validation = payload.get("contract_validation")
        if _is_mapping(contract):
            return dict(contract), (
                dict(validation) if _is_mapping(validation) else None
            ), "design_contract"
        return None, None, "legacy_missing_contract"

    design_block = payload.get("design")
    if _is_mapping(design_block) and "design_contract" in design_block:
        contract = design_block["design_contract"]
        validation = design_block.get("contract_validation")
        if _is_mapping(contract):
            return dict(contract), (
                dict(validation) if _is_mapping(validation) else None
            ), "design_contract"
        return None, None, "legacy_missing_contract"

    if _is_standalone_contract(payload):
        return dict(payload), None, "design_contract"

    if _is_contract_validation_summary(payload):
        return None, dict(payload), "contract_validation"

    if any(key in payload for key in ("design_method", "assignment", "evidence_version")):
        return None, None, "legacy_missing_contract"

    return None, None, "legacy_missing_contract"


def _default_blocked_roles() -> list[str]:
    return [
        "trust_report",
        "calibration_signal",
        "mmm",
        "llm",
        "production",
    ]


def _collect_overclaim_violations(
    contract: Mapping[str, Any] | None,
) -> tuple[list[str], list[str]]:
    if contract is None or not _is_mapping(contract):
        return [], []

    reason_codes: list[str] = []
    blocked_roles: list[str] = []

    for path, reason_code, role in _OVERCLAIM_CHECKS:
        value = _nested_get(contract, path)
        if value is True:
            _append_unique(reason_codes, reason_code)
            _append_unique(blocked_roles, role)

    governance = contract.get("governance")
    if _is_mapping(governance):
        auth_status = governance.get("downstream_authorization_status")
        if auth_status is not None and str(auth_status).lower() not in _ALLOWED_DOWNSTREAM_AUTH:
            _append_unique(reason_codes, RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION)
            for role in _default_blocked_roles():
                _append_unique(blocked_roles, role)

        forbidden = governance.get("forbidden_downstream_claims")
        if forbidden is not None and isinstance(forbidden, list) and len(forbidden) == 0:
            _append_unique(reason_codes, RC_GUARDRAIL_CONTRACT_BLOCKED)

    multi_cell = contract.get("multi_cell")
    if _is_mapping(multi_cell):
        geometry = contract.get("geometry")
        geometry_id = (
            str(geometry.get("geometry_id"))
            if _is_mapping(geometry) and geometry.get("geometry_id") is not None
            else None
        )
        if multi_cell.get("is_multi_cell") is True and geometry_id == "pooled_multi_cell":
            _append_unique(reason_codes, RC_GUARDRAIL_CONTRACT_BLOCKED)
            _append_unique(blocked_roles, "production")

    return reason_codes, blocked_roles


def _map_contract_status_to_guardrail_reason(contract_status: str | None) -> str | None:
    if contract_status == CONTRACT_BLOCKED:
        return RC_GUARDRAIL_CONTRACT_BLOCKED
    if contract_status == CONTRACT_INCOMPLETE:
        return RC_GUARDRAIL_CONTRACT_INCOMPLETE
    if contract_status == CONTRACT_UNKNOWN:
        return RC_GUARDRAIL_CONTRACT_UNKNOWN
    return None


def _map_validator_reasons_to_guardrail(validator_reasons: list[str]) -> list[str]:
    mapped: list[str] = []
    for code in validator_reasons:
        if code == RC_DOWNSTREAM_AUTH_VIOLATION:
            _append_unique(mapped, RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION)
        elif code in (RC_EMPTY_FORBIDDEN_CLAIMS, RC_MISSING_FORBIDDEN_CLAIMS):
            _append_unique(mapped, RC_GUARDRAIL_CONTRACT_BLOCKED)
        elif code == RC_MISSING_GEOMETRY_ID:
            _append_unique(mapped, RC_GUARDRAIL_CONTRACT_BLOCKED)
        elif code == RC_LEGACY_UNKNOWN:
            _append_unique(mapped, RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN)
        elif code == RC_MISSING_DESIGN_CONTRACT:
            _append_unique(mapped, RC_GUARDRAIL_MISSING_CONTRACT)
    return mapped


def guardrail_result_from_contract_validation(
    summary: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    source: str = "contract_validation",
    revalidated: bool = False,
) -> DesignGuardrailRuntimeResult:
    """Map a compact ``contract_validation`` summary to a guardrail runtime result."""
    contract_status = str(summary.get("status", CONTRACT_UNKNOWN))
    contract_severity = str(summary.get("severity", SEVERITY_UNKNOWN))
    contract_complete_allowed = bool(summary.get("contract_complete_allowed", False))
    validator_reasons = list(summary.get("reason_codes") or [])
    blocked_roles = list(summary.get("blocked_downstream_roles") or _default_blocked_roles())

    reason_codes: list[str] = []
    warnings: list[str] = list(summary.get("warnings") or [])

    if revalidated:
        _append_unique(reason_codes, RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION)

    status_reason = _map_contract_status_to_guardrail_reason(contract_status)
    if status_reason:
        _append_unique(reason_codes, status_reason)

    for mapped in _map_validator_reasons_to_guardrail(validator_reasons):
        _append_unique(reason_codes, mapped)

    downstream_auth: str | None = None
    if contract is not None and _is_mapping(contract):
        governance = contract.get("governance")
        if _is_mapping(governance):
            downstream_auth = governance.get("downstream_authorization_status")
            if downstream_auth is not None:
                downstream_auth = str(downstream_auth)

    overclaim_reasons, overclaim_roles = _collect_overclaim_violations(contract)
    for code in overclaim_reasons:
        _append_unique(reason_codes, code)
    for role in overclaim_roles:
        _append_unique(blocked_roles, role)

    if contract_severity == SEVERITY_BLOCK or contract_status in (
        CONTRACT_BLOCKED,
        CONTRACT_INCOMPLETE,
        CONTRACT_UNKNOWN,
    ):
        status = GUARDRAIL_BLOCK
    elif contract_status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS):
        if contract_severity == SEVERITY_WARN:
            status = GUARDRAIL_WARN
        else:
            status = GUARDRAIL_WARN
        _append_unique(reason_codes, RC_GUARDRAIL_REQUIRES_STATISTICAL_VALIDATION)
        warnings.append(
            "Contract metadata mechanically valid; statistical validation not executed."
        )
    else:
        status = GUARDRAIL_BLOCK

    if overclaim_reasons:
        status = GUARDRAIL_BLOCK

    if not contract_complete_allowed:
        _append_unique(reason_codes, RC_GUARDRAIL_CONTRACT_COMPLETE_NOT_ALLOWED)

    if downstream_auth is not None and downstream_auth.lower() not in _ALLOWED_DOWNSTREAM_AUTH:
        status = GUARDRAIL_BLOCK
        _append_unique(reason_codes, RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION)

    return DesignGuardrailRuntimeResult(
        status=status,
        reason_codes=reason_codes,
        warnings=warnings,
        blocked_roles=blocked_roles,
        contract_status=contract_status,
        contract_severity=contract_severity,
        contract_complete_allowed=contract_complete_allowed,
        downstream_authorization_status=downstream_auth,
        guardrail_version=GUARDRAIL_VERSION,
        source=source,
        suitability_may_proceed=False,
        downstream_may_proceed=False,
    )


def evaluate_contract_validation_summary(
    summary: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> DesignGuardrailRuntimeResult:
    """Evaluate guardrails from a standalone ``contract_validation`` summary."""
    return guardrail_result_from_contract_validation(
        summary,
        contract=contract,
        source="contract_validation",
    )


def evaluate_design_contract_guardrails(
    evidence_or_contract: Mapping[str, Any],
) -> DesignGuardrailRuntimeResult:
    """Evaluate runtime guardrails from evidence, contract, or golden fixture payload."""
    if not _is_mapping(evidence_or_contract):
        return DesignGuardrailRuntimeResult(
            status=GUARDRAIL_UNKNOWN,
            reason_codes=[RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN],
            source="legacy_missing_contract",
        )

    contract, validation, source = _extract_contract_and_validation(evidence_or_contract)

    if contract is None and validation is None:
        return DesignGuardrailRuntimeResult(
            status=GUARDRAIL_BLOCK,
            reason_codes=[
                RC_GUARDRAIL_MISSING_CONTRACT,
                RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN,
            ],
            source=source,
        )

    if validation is None and contract is not None:
        validation_result = validate_design_contract(contract)
        validation = contract_validation_summary_from_result(validation_result)
        return guardrail_result_from_contract_validation(
            validation,
            contract=contract,
            source=source,
            revalidated=True,
        )

    if validation is None:
        return DesignGuardrailRuntimeResult(
            status=GUARDRAIL_BLOCK,
            reason_codes=[RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION],
            source=source,
        )

    return guardrail_result_from_contract_validation(
        validation,
        contract=contract,
        source=source,
    )
