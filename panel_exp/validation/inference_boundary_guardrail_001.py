"""INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001 — readout-boundary enforcement."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from panel_exp.validation.design_combination_guardrail_001 import (
    COMBINATION_STATUS_NOT_EVALUATED,
    evaluate_design_combination_guardrails,
)
from panel_exp.validation.design_combination_resolver_001 import (
    RESOLUTION_UNKNOWN,
    resolve_design_combination,
)
from panel_exp.validation.design_guardrail_enforcement_001 import (
    DOWNSTREAM_BLOCKED_ROLES,
    RESEARCH_ALLOWED_ROLES,
    DesignGuardrailEnforcementResult,
    enforce_design_decision_path,
)
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_BLOCK, GUARDRAIL_WARN
from panel_exp.validation.inference_boundary_identity_001 import (
    InferenceBoundaryIdentity,
    identity_from_mapping,
)

BOUNDARY_VERSION = "1.0.0"

RC_BOUNDARY_MISSING_IDENTITY = "I-BOUNDARY-MISSING-IDENTITY"
RC_BOUNDARY_UNKNOWN_ESTIMATOR = "I-BOUNDARY-UNKNOWN-ESTIMATOR"
RC_BOUNDARY_UNKNOWN_INFERENCE = "I-BOUNDARY-UNKNOWN-INFERENCE"
RC_BOUNDARY_UNKNOWN_READOUT_SEMANTICS = "I-BOUNDARY-UNKNOWN-READOUT-SEMANTICS"
RC_BOUNDARY_DCM_UNRESOLVED = "I-BOUNDARY-DCM-UNRESOLVED"
RC_BOUNDARY_GEOMETRY_MISMATCH = "I-BOUNDARY-GEOMETRY-MISMATCH"
RC_BOUNDARY_POINT_ONLY = "I-BOUNDARY-POINT-ONLY"
RC_BOUNDARY_INTERVAL_SEMANTICS_MISMATCH = "I-BOUNDARY-INTERVAL-SEMANTICS-MISMATCH"
RC_BOUNDARY_NULL_MONITOR_NOT_CAUSAL = "I-BOUNDARY-NULL-MONITOR-NOT-CAUSAL"
RC_BOUNDARY_FORECAST_NOT_CAUSAL = "I-BOUNDARY-FORECAST-NOT-CAUSAL"
RC_BOUNDARY_SIGN_NOT_SIGNIFICANCE = "I-BOUNDARY-SIGN-NOT-SIGNIFICANCE"
RC_BOUNDARY_PER_CELL_ONLY = "I-BOUNDARY-PER-CELL-ONLY"
RC_BOUNDARY_POOLED_MULTICELL_BLOCKED = "I-BOUNDARY-POOLED-MULTICELL-BLOCKED"
RC_BOUNDARY_MISSING_CELL_ID = "I-BOUNDARY-MISSING-CELL-ID"
RC_BOUNDARY_SHARED_CONTROL_DEPENDENCE = "I-BOUNDARY-SHARED-CONTROL-DEPENDENCE"
RC_BOUNDARY_ESTIMAND_MISMATCH = "I-BOUNDARY-ESTIMAND-MISMATCH"
RC_BOUNDARY_DOWNSTREAM_ROLE_BLOCKED = "I-BOUNDARY-DOWNSTREAM-ROLE-BLOCKED"
RC_BOUNDARY_RESEARCH_ONLY = "I-BOUNDARY-RESEARCH-ONLY"
RC_BOUNDARY_LEGACY_UNKNOWN = "I-BOUNDARY-LEGACY-UNKNOWN"


class InferenceBoundaryViolation(RuntimeError):
    """Raised when a governed readout request is blocked at the inference boundary."""

    def __init__(
        self,
        message: str,
        *,
        result: "InferenceBoundaryGuardrailResult",
    ) -> None:
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class InferenceBoundaryGuardrailResult:
    status: str
    severity: str
    allowed: bool
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    dcm_row_id: str | None
    combination_status: str
    design_id: str | None
    estimator_id: str | None
    inference_id: str | None
    instrument_id: str | None
    geometry_id: str | None
    readout_semantics: str | None
    interval_type: str | None
    estimand: str | None
    cell_id: str | None
    pooled: bool
    requested_role: str | None
    downstream_authorization_status: str | None
    boundary_version: str = BOUNDARY_VERSION
    enforcement: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _norm_role(role: str | None) -> str:
    return (role or "").strip().lower().replace("-", "_")


def _extract_design_payload(design_evidence: Any) -> dict[str, Any]:
    if _is_mapping(design_evidence):
        if "design" in design_evidence and _is_mapping(design_evidence["design"]):
            return dict(design_evidence["design"])
        return dict(design_evidence)
    if hasattr(design_evidence, "to_dict"):
        return design_evidence.to_dict()
    return {}


def _boundary_readout_claim_type(identity: InferenceBoundaryIdentity) -> str | None:
    rs = identity.readout_semantics or "unknown"
    if rs == "causal_interval":
        return "causal_interval"
    if rs == "significance_test":
        return "significance_test"
    if rs == "null_monitor_interval":
        return "causal_inference"
    if rs in ("pooled_point", "pooled_interval"):
        return "pooled_multicell_causal"
    if rs == "forecast_interval":
        return "causal_interval"
    return None


def _collect_boundary_violations(
    identity: InferenceBoundaryIdentity,
    resolution_dcm: str | None,
    *,
    design_contract: Mapping[str, Any] | None,
) -> list[str]:
    codes: list[str] = []
    if not identity.estimator_id:
        codes.append(RC_BOUNDARY_UNKNOWN_ESTIMATOR)
    if identity.readout_semantics == "unknown":
        codes.append(RC_BOUNDARY_UNKNOWN_READOUT_SEMANTICS)
    if resolution_dcm is None:
        codes.append(RC_BOUNDARY_DCM_UNRESOLVED)

    if resolution_dcm == "DCM-002" and identity.readout_semantics in (
        "causal_interval",
        "significance_test",
    ):
        codes.append(RC_BOUNDARY_POINT_ONLY)
    if identity.interval_type not in (None, "none") and resolution_dcm == "DCM-002":
        if identity.interval_type != "none":
            codes.append(RC_BOUNDARY_INTERVAL_SEMANTICS_MISMATCH)

    if identity.readout_semantics == "forecast_interval":
        codes.append(RC_BOUNDARY_FORECAST_NOT_CAUSAL)
    if identity.readout_semantics == "null_monitor_interval":
        codes.append(RC_BOUNDARY_NULL_MONITOR_NOT_CAUSAL)
    if identity.readout_semantics == "directional_sign" and identity.requested_role == "significance_test":
        codes.append(RC_BOUNDARY_SIGN_NOT_SIGNIFICANCE)

    if resolution_dcm == "DCM-003":
        geo = (identity.geometry_id or "").lower()
        if geo == "unit_panel_single_cell" or geo == "":
            codes.append(RC_BOUNDARY_GEOMETRY_MISMATCH)

    if resolution_dcm == "DCM-007" or identity.pooled:
        codes.append(RC_BOUNDARY_POOLED_MULTICELL_BLOCKED)

    if resolution_dcm == "DCM-006":
        if not identity.cell_id:
            codes.append(RC_BOUNDARY_MISSING_CELL_ID)
        if identity.pooled:
            codes.append(RC_BOUNDARY_POOLED_MULTICELL_BLOCKED)
        if design_contract:
            multi = design_contract.get("multi_cell")
            if _is_mapping(multi) and multi.get("is_multi_cell"):
                if not multi.get("cell_ids"):
                    codes.append(RC_BOUNDARY_SHARED_CONTROL_DEPENDENCE)
                elif multi.get("shared_control_policy") is None:
                    codes.append(RC_BOUNDARY_SHARED_CONTROL_DEPENDENCE)

    if identity.estimand == "pooled_multicell_effect":
        codes.append(RC_BOUNDARY_ESTIMAND_MISMATCH)

    if identity.estimator_id == "scm" and identity.inference_id is None and identity.requested_role:
        codes.append(RC_BOUNDARY_UNKNOWN_INFERENCE)

    return codes


def evaluate_inference_boundary_guardrail(
    *,
    design_evidence: Mapping[str, Any] | Any,
    identity: InferenceBoundaryIdentity,
) -> InferenceBoundaryGuardrailResult:
    """Evaluate inference-boundary guardrails with real estimator/inference identity."""
    design_payload = _extract_design_payload(design_evidence)
    contract = design_payload.get("design_contract")
    validation = design_payload.get("contract_validation")
    design_guardrail = design_payload.get("design_guardrail")

    resolution = resolve_design_combination(identity, design_contract=contract)
    boundary_codes = _collect_boundary_violations(
        identity, resolution.dcm_row_id, design_contract=contract
    )

    readout_claim = _boundary_readout_claim_type(identity)
    cg = evaluate_design_combination_guardrails(
        design_contract=contract,
        contract_validation=validation,
        design_guardrail=design_guardrail,
        design_id=identity.design_id or resolution.design_id,
        estimator_id=identity.estimator_id,
        inference_id=identity.inference_id,
        geometry_id=identity.geometry_id or resolution.geometry_id,
        readout_semantics=identity.readout_semantics,
        requested_downstream_role=identity.requested_role,
        readout_claim_type=readout_claim,
    )

    enforcement: DesignGuardrailEnforcementResult = enforce_design_decision_path(
        design_contract=contract,
        contract_validation=validation,
        design_guardrail=design_guardrail,
        combination_guardrail=cg.to_dict(),
        design_id=identity.design_id or resolution.design_id,
        estimator_id=identity.estimator_id,
        inference_id=identity.inference_id,
        geometry_id=identity.geometry_id or resolution.geometry_id,
        readout_semantics=identity.readout_semantics,
        requested_downstream_role=identity.requested_role,
        readout_claim_type=readout_claim,
    )

    reason_codes = list(boundary_codes)
    for code in cg.reason_codes:
        if code not in reason_codes:
            reason_codes.append(code)
    for code in enforcement.reason_codes:
        if code not in reason_codes:
            reason_codes.append(code)

    warnings = list(enforcement.warnings)
    if resolution.dcm_row_id and resolution.combination_status != COMBINATION_STATUS_NOT_EVALUATED:
        warnings.append(
            f"Boundary resolved DCM row {resolution.dcm_row_id} "
            f"({resolution.combination_status})."
        )

    status = enforcement.status
    if boundary_codes and any(
        c
        in (
            RC_BOUNDARY_POINT_ONLY,
            RC_BOUNDARY_GEOMETRY_MISMATCH,
            RC_BOUNDARY_POOLED_MULTICELL_BLOCKED,
            RC_BOUNDARY_MISSING_CELL_ID,
            RC_BOUNDARY_FORECAST_NOT_CAUSAL,
            RC_BOUNDARY_NULL_MONITOR_NOT_CAUSAL,
            RC_BOUNDARY_SIGN_NOT_SIGNIFICANCE,
            RC_BOUNDARY_INTERVAL_SEMANTICS_MISMATCH,
            RC_BOUNDARY_ESTIMAND_MISMATCH,
            RC_BOUNDARY_UNKNOWN_INFERENCE,
        )
        for c in boundary_codes
    ):
        status = GUARDRAIL_BLOCK

    role = _norm_role(identity.requested_role)
    if role in DOWNSTREAM_BLOCKED_ROLES:
        status = GUARDRAIL_BLOCK
        if RC_BOUNDARY_DOWNSTREAM_ROLE_BLOCKED not in reason_codes:
            reason_codes.append(RC_BOUNDARY_DOWNSTREAM_ROLE_BLOCKED)

    allowed = enforcement.allowed
    if status == GUARDRAIL_BLOCK:
        allowed = False
    elif status == GUARDRAIL_WARN and role in RESEARCH_ALLOWED_ROLES:
        allowed = True
        if RC_BOUNDARY_RESEARCH_ONLY not in reason_codes:
            reason_codes.append(RC_BOUNDARY_RESEARCH_ONLY)
    else:
        allowed = False

    combination_status = (
        resolution.combination_status
        if resolution.resolution_status != RESOLUTION_UNKNOWN
        else cg.combination_status
    )

    return InferenceBoundaryGuardrailResult(
        status=status,
        severity=status if status in (GUARDRAIL_BLOCK, GUARDRAIL_WARN) else "UNKNOWN",
        allowed=allowed,
        reason_codes=tuple(reason_codes),
        warnings=tuple(warnings),
        dcm_row_id=resolution.dcm_row_id,
        combination_status=combination_status,
        design_id=identity.design_id or resolution.design_id,
        estimator_id=identity.estimator_id,
        inference_id=identity.inference_id,
        instrument_id=identity.instrument_id,
        geometry_id=identity.geometry_id or resolution.geometry_id,
        readout_semantics=identity.readout_semantics,
        interval_type=identity.interval_type,
        estimand=identity.estimand,
        cell_id=identity.cell_id,
        pooled=identity.pooled,
        requested_role=identity.requested_role,
        downstream_authorization_status=enforcement.downstream_authorization_status,
        enforcement=enforcement.to_dict(),
    )


def enforce_inference_boundary(
    *,
    design_evidence: Mapping[str, Any] | Any,
    identity: InferenceBoundaryIdentity,
) -> InferenceBoundaryGuardrailResult:
    """Evaluate boundary guardrails; raise if requested role is blocked."""
    result = evaluate_inference_boundary_guardrail(
        design_evidence=design_evidence,
        identity=identity,
    )
    if identity.requested_role and not result.allowed:
        raise InferenceBoundaryViolation(
            f"Inference boundary blocked for role '{identity.requested_role}' "
            f"(DCM={result.dcm_row_id}, status={result.status}).",
            result=result,
        )
    return result


def assert_inference_readout_allowed(
    boundary_result: InferenceBoundaryGuardrailResult | Mapping[str, Any],
    *,
    requested_role: str,
) -> None:
    """Raise ``InferenceBoundaryViolation`` when readout role is not permitted."""
    if _is_mapping(boundary_result) and not isinstance(
        boundary_result, InferenceBoundaryGuardrailResult
    ):
        result = InferenceBoundaryGuardrailResult(**dict(boundary_result))
    else:
        result = boundary_result  # type: ignore[assignment]

    role = _norm_role(requested_role)
    if role in DOWNSTREAM_BLOCKED_ROLES:
        raise InferenceBoundaryViolation(
            f"Downstream readout role '{requested_role}' is blocked.",
            result=result,
        )
    if role in RESEARCH_ALLOWED_ROLES:
        if result.status == GUARDRAIL_BLOCK or not result.allowed:
            raise InferenceBoundaryViolation(
                f"Research readout role '{requested_role}' not permitted "
                f"(status={result.status}).",
                result=result,
            )
        return
    raise InferenceBoundaryViolation(
        f"Unknown readout role '{requested_role}' — fail closed.",
        result=result,
    )


def build_boundary_identity_from_kwargs(**kwargs: Any) -> InferenceBoundaryIdentity:
    if isinstance(kwargs.get("identity"), InferenceBoundaryIdentity):
        return kwargs["identity"]
    if _is_mapping(kwargs.get("identity")):
        return identity_from_mapping(kwargs["identity"])
    return InferenceBoundaryIdentity.build(**kwargs)
