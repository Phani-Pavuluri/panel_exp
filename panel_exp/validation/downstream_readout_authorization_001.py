"""DOWNSTREAM-READOUT-AUTHORIZATION-GATEWAY-001 — fail-closed downstream consumer gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from panel_exp.evidence import ReadoutEvidence
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_BLOCK
from panel_exp.validation.estimator_readout_adapter_001 import GOVERNED_READOUT_MARKER
from panel_exp.validation.inference_boundary_guardrail_001 import DOWNSTREAM_BLOCKED_ROLES

AUTHORIZATION_VERSION = "1.0.0"

STATUS_AUTHORIZED = "AUTHORIZED"
STATUS_RESTRICTED = "RESTRICTED"
STATUS_BLOCKED = "BLOCKED"
STATUS_UNKNOWN = "UNKNOWN"

RC_AUTH_MISSING_READOUT = "D-AUTH-MISSING-READOUT-EVIDENCE"
RC_AUTH_NOT_GOVERNED = "D-AUTH-NOT-GOVERNED-READOUT"
RC_AUTH_MISSING_MARKER = "D-AUTH-MISSING-GOVERNED-MARKER"
RC_AUTH_INVALID_MARKER = "D-AUTH-INVALID-GOVERNED-MARKER"
RC_AUTH_MISSING_BOUNDARY = "D-AUTH-MISSING-INFERENCE-BOUNDARY"
RC_AUTH_BOUNDARY_BLOCKED = "D-AUTH-INFERENCE-BOUNDARY-BLOCKED"
RC_AUTH_COMBINATION_BLOCKED = "D-AUTH-COMBINATION-BLOCKED"
RC_AUTH_COMBINATION_UNKNOWN = "D-AUTH-COMBINATION-UNKNOWN"
RC_AUTH_POINT_ONLY = "D-AUTH-POINT-ONLY"
RC_AUTH_READOUT_MISMATCH = "D-AUTH-READOUT-SEMANTICS-MISMATCH"
RC_AUTH_POOLED_MULTICELL = "D-AUTH-POOLED-MULTICELL-BLOCKED"
RC_AUTH_LEGACY_NATIVE = "D-AUTH-LEGACY-NATIVE-RESULT"
RC_AUTH_MISSING_PROMOTION = "D-AUTH-MISSING-PROMOTION-EVIDENCE"
RC_AUTH_PROMOTION_NOT_APPROVED = "D-AUTH-PROMOTION-NOT-APPROVED"
RC_AUTH_ROLE_NOT_APPROVED = "D-AUTH-ROLE-NOT-APPROVED"
RC_AUTH_DOWNSTREAM_BLOCKED = "D-AUTH-DOWNSTREAM-ROLE-BLOCKED"
RC_AUTH_TRUSTREPORT = "D-AUTH-TRUSTREPORT-BLOCKED"
RC_AUTH_CALIBRATION_SIGNAL = "D-AUTH-CALIBRATION-SIGNAL-BLOCKED"
RC_AUTH_MMM = "D-AUTH-MMM-BLOCKED"
RC_AUTH_LLM = "D-AUTH-LLM-BLOCKED"
RC_AUTH_PRODUCTION_REC = "D-AUTH-PRODUCTION-RECOMMENDATION-BLOCKED"
RC_AUTH_AUTOMATED_BUDGET = "D-AUTH-AUTOMATED-BUDGET-ACTION-BLOCKED"
RC_AUTH_EXTERNAL_EXPORT = "D-AUTH-EXTERNAL-EXPORT-BLOCKED"
RC_AUTH_RESEARCH_ONLY = "D-AUTH-RESEARCH-ONLY"

PRODUCTION_FACING_ROLES: frozenset[str] = frozenset(
    {
        "trust_report",
        "trustreport",
        "calibration_signal",
        "calibrationsignal",
        "mmm_calibration",
        "mmm",
        "llm_decision_support",
        "llm",
        "production_recommendation",
        "automated_budget_action",
        "external_export",
        "production",
        "production_decision",
    }
)

RESEARCH_SAFE_ROLES: frozenset[str] = frozenset(
    {
        "research",
        "diagnostic",
        "validation",
        "blocked_status_explanation",
    }
)

_ROLE_REASON_CODES: dict[str, str] = {
    "trust_report": RC_AUTH_TRUSTREPORT,
    "trustreport": RC_AUTH_TRUSTREPORT,
    "calibration_signal": RC_AUTH_CALIBRATION_SIGNAL,
    "calibrationsignal": RC_AUTH_CALIBRATION_SIGNAL,
    "mmm_calibration": RC_AUTH_MMM,
    "mmm": RC_AUTH_MMM,
    "llm_decision_support": RC_AUTH_LLM,
    "llm": RC_AUTH_LLM,
    "production_recommendation": RC_AUTH_PRODUCTION_REC,
    "automated_budget_action": RC_AUTH_AUTOMATED_BUDGET,
    "external_export": RC_AUTH_EXTERNAL_EXPORT,
}

_DEFAULT_BLOCKED_ROLES: tuple[str, ...] = tuple(sorted(PRODUCTION_FACING_ROLES))


class DownstreamReadoutAuthorizationViolation(RuntimeError):
    """Raised when a downstream consumer is not authorized to use a readout."""

    def __init__(
        self,
        message: str,
        *,
        result: "DownstreamReadoutAuthorizationResult",
    ) -> None:
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class DownstreamPromotionEvidence:
    artifact_id: str
    status: str
    approved_roles: tuple[str, ...]
    approved_dcm_rows: tuple[str, ...]
    approved_estimators: tuple[str, ...]
    approved_inference_paths: tuple[str, ...]
    approved_readout_semantics: tuple[str, ...]
    expires_at: str | None
    evidence_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DownstreamPromotionEvidence":
        return cls(
            artifact_id=str(data.get("artifact_id", "")),
            status=str(data.get("status", "")),
            approved_roles=tuple(str(x) for x in (data.get("approved_roles") or ())),
            approved_dcm_rows=tuple(str(x) for x in (data.get("approved_dcm_rows") or ())),
            approved_estimators=tuple(str(x) for x in (data.get("approved_estimators") or ())),
            approved_inference_paths=tuple(
                str(x) for x in (data.get("approved_inference_paths") or ())
            ),
            approved_readout_semantics=tuple(
                str(x) for x in (data.get("approved_readout_semantics") or ())
            ),
            expires_at=data.get("expires_at"),
            evidence_version=str(data.get("evidence_version", "1.0.0")),
        )


@dataclass(frozen=True)
class DownstreamReadoutAuthorizationResult:
    status: str
    severity: str
    authorized: bool
    requested_role: str
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    blocked_roles: tuple[str, ...]
    governed_readout_present: bool
    governed_readout_valid: bool
    inference_boundary_status: str | None
    combination_status: str | None
    dcm_row_id: str | None
    design_id: str | None
    estimator_id: str | None
    inference_id: str | None
    readout_semantics: str | None
    interval_type: str | None
    estimand: str | None
    downstream_authorization_status: str | None
    promotion_status: str | None
    authorization_version: str = AUTHORIZATION_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _norm_role(role: str | None) -> str:
    return (role or "").strip().lower().replace("-", "_")


def _append_unique(codes: list[str], code: str) -> None:
    if code and code not in codes:
        codes.append(code)


def _auth_blocking_codes(codes: Sequence[str]) -> list[str]:
    """Return D-AUTH codes that block downstream consumption (research or production)."""
    exempt = {
        RC_AUTH_RESEARCH_ONLY,
        RC_AUTH_MISSING_PROMOTION,
        RC_AUTH_PROMOTION_NOT_APPROVED,
    }
    return [c for c in codes if c.startswith("D-AUTH-") and c not in exempt]


def _coerce_readout_evidence(
    readout_evidence: Any,
) -> tuple[ReadoutEvidence | None, bool]:
    """Return (evidence, is_native_dict)."""
    if readout_evidence is None:
        return None, False
    if isinstance(readout_evidence, ReadoutEvidence):
        return readout_evidence, False
    if _is_mapping(readout_evidence):
        if readout_evidence.get("evidence_version") and readout_evidence.get("created_at"):
            try:
                return ReadoutEvidence.from_dict(dict(readout_evidence)), False
            except (KeyError, TypeError, ValueError):
                return None, True
        if any(k in readout_evidence for k in ("y", "y_hat", "cumulative_att", "results")):
            return None, True
        return None, True
    return None, True


def _has_governed_marker(readout: ReadoutEvidence) -> bool:
    payload = readout.result_payload or {}
    meta = payload.get("metadata") if _is_mapping(payload.get("metadata")) else {}
    if meta.get(GOVERNED_READOUT_MARKER) is True:
        return True
    if payload.get(GOVERNED_READOUT_MARKER) is True:
        return True
    return False


def _has_invalid_governed_marker(readout: ReadoutEvidence) -> bool:
    payload = readout.result_payload or {}
    meta = payload.get("metadata") if _is_mapping(payload.get("metadata")) else {}
    for source in (meta, payload):
        if GOVERNED_READOUT_MARKER in source and source.get(GOVERNED_READOUT_MARKER) is not True:
            return True
    return False


def _readout_fields_complete(readout: ReadoutEvidence) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if not readout.estimator_identity:
        missing.append("estimator_identity")
    if not readout.readout_identity:
        missing.append("readout_identity")
    if not readout.combination_resolution:
        missing.append("combination_resolution")
    if not readout.inference_boundary_guardrail:
        missing.append("inference_boundary_guardrail")
    if not readout.guardrail_enforcement:
        missing.append("guardrail_enforcement")
    if readout.result_payload is None:
        missing.append("result_payload")
    rs = (readout.readout_identity or {}).get("readout_semantics")
    inf = (readout.inference_identity or {}).get("inference_id")
    if rs in ("causal_interval", "per_cell_interval", "significance_test") and not inf:
        missing.append("inference_identity")
    return len(missing) == 0, missing


def _validate_promotion_evidence(
    promotion: DownstreamPromotionEvidence | Mapping[str, Any] | None,
    *,
    role: str,
    dcm_row_id: str | None,
    estimator_id: str | None,
    inference_id: str | None,
    readout_semantics: str | None,
) -> tuple[list[str], str | None]:
    codes: list[str] = []
    if promotion is None:
        _append_unique(codes, RC_AUTH_MISSING_PROMOTION)
        return codes, "missing"
    if isinstance(promotion, Mapping):
        try:
            promo = DownstreamPromotionEvidence.from_dict(promotion)
        except (TypeError, ValueError):
            _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)
            return codes, "malformed"
    else:
        promo = promotion

    if not promo.artifact_id or not promo.status:
        _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)
        return codes, "malformed"

    if promo.expires_at:
        try:
            expires = datetime.fromisoformat(promo.expires_at.replace("Z", "+00:00"))
            if expires < datetime.now(timezone.utc):
                _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)
                return codes, "expired"
        except ValueError:
            _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)
            return codes, "malformed"

    role_norm = _norm_role(role)
    if promo.approved_roles and role_norm not in {_norm_role(r) for r in promo.approved_roles}:
        _append_unique(codes, RC_AUTH_ROLE_NOT_APPROVED)

    if dcm_row_id and promo.approved_dcm_rows and dcm_row_id not in promo.approved_dcm_rows:
        _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)

    if estimator_id and promo.approved_estimators:
        est = (estimator_id or "").lower()
        if est not in {e.lower() for e in promo.approved_estimators}:
            _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)

    if inference_id and promo.approved_inference_paths:
        inf = (inference_id or "").lower()
        if inf not in {p.lower() for p in promo.approved_inference_paths}:
            _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)

    if readout_semantics and promo.approved_readout_semantics:
        rs = (readout_semantics or "").lower()
        if rs not in {s.lower() for s in promo.approved_readout_semantics}:
            _append_unique(codes, RC_AUTH_READOUT_MISMATCH)

    # This artifact never authorizes production from promotion evidence alone.
    if role_norm in PRODUCTION_FACING_ROLES:
        _append_unique(codes, RC_AUTH_PROMOTION_NOT_APPROVED)

    return codes, promo.status


def evaluate_downstream_readout_authorization(
    *,
    readout_evidence: Any,
    requested_role: str,
    promotion_evidence: DownstreamPromotionEvidence | Mapping[str, Any] | None = None,
    consumer_context: Mapping[str, Any] | None = None,
) -> DownstreamReadoutAuthorizationResult:
    """Evaluate whether a governed readout may be consumed by a downstream role."""
    del consumer_context  # reserved for future gateway context
    role = _norm_role(requested_role) or STATUS_UNKNOWN.lower()
    reason_codes: list[str] = []
    warnings: list[str] = []

    readout, is_native = _coerce_readout_evidence(readout_evidence)
    governed_present = readout is not None
    governed_valid = False

    estimator_id = None
    inference_id = None
    readout_semantics = None
    interval_type = None
    estimand = None
    design_id = None
    dcm_row_id = None
    combination_status = None
    boundary_status = None

    if readout is None:
        if is_native:
            _append_unique(reason_codes, RC_AUTH_LEGACY_NATIVE)
            _append_unique(reason_codes, RC_AUTH_NOT_GOVERNED)
        else:
            _append_unique(reason_codes, RC_AUTH_MISSING_READOUT)
    else:
        estimator_id = (readout.estimator_identity or {}).get("estimator_id")
        inference_id = (readout.inference_identity or {}).get("inference_id")
        interval_type = (readout.inference_identity or {}).get("interval_type")
        readout_semantics = (readout.readout_identity or {}).get("readout_semantics")
        estimand = (readout.readout_identity or {}).get("estimand")
        design_id = (readout.combination_resolution or {}).get("design_id")
        dcm_row_id = (readout.combination_resolution or {}).get("dcm_row_id")
        combination_status = (readout.combination_resolution or {}).get("combination_status")
        boundary = readout.inference_boundary_guardrail or {}
        boundary_status = boundary.get("status")
        for code in boundary.get("reason_codes") or ():
            if code not in reason_codes:
                reason_codes.append(str(code))

        if _has_invalid_governed_marker(readout):
            _append_unique(reason_codes, RC_AUTH_INVALID_MARKER)
            _append_unique(reason_codes, RC_AUTH_NOT_GOVERNED)
        elif not _has_governed_marker(readout):
            _append_unique(reason_codes, RC_AUTH_MISSING_MARKER)
            _append_unique(reason_codes, RC_AUTH_NOT_GOVERNED)

        complete, missing = _readout_fields_complete(readout)
        if not complete:
            for field in missing:
                if field == "inference_boundary_guardrail":
                    _append_unique(reason_codes, RC_AUTH_MISSING_BOUNDARY)
                elif field == "inference_identity":
                    _append_unique(reason_codes, RC_AUTH_MISSING_BOUNDARY)
            _append_unique(reason_codes, RC_AUTH_NOT_GOVERNED)
        else:
            governed_valid = _has_governed_marker(readout)

        if boundary_status == GUARDRAIL_BLOCK:
            _append_unique(reason_codes, RC_AUTH_BOUNDARY_BLOCKED)

        if combination_status in ("blocked_for_pooled_claim", "blocked_due_to_geometry_mismatch"):
            _append_unique(reason_codes, RC_AUTH_COMBINATION_BLOCKED)
        elif combination_status == "not_evaluated":
            _append_unique(reason_codes, RC_AUTH_COMBINATION_UNKNOWN)

        pooled = (readout.readout_identity or {}).get("pooled")
        rs_norm = (readout_semantics or "").lower()
        if pooled or rs_norm in ("pooled_point", "pooled_interval"):
            _append_unique(reason_codes, RC_AUTH_POOLED_MULTICELL)

        if dcm_row_id == "DCM-002" and rs_norm in ("causal_interval", "significance_test"):
            _append_unique(reason_codes, RC_AUTH_POINT_ONLY)

    promo_codes, promo_status = _validate_promotion_evidence(
        promotion_evidence,
        role=role,
        dcm_row_id=dcm_row_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=readout_semantics,
    )
    for code in promo_codes:
        _append_unique(reason_codes, code)

    if role in PRODUCTION_FACING_ROLES or role in DOWNSTREAM_BLOCKED_ROLES:
        role_code = _ROLE_REASON_CODES.get(role, RC_AUTH_DOWNSTREAM_BLOCKED)
        _append_unique(reason_codes, role_code)
        _append_unique(reason_codes, RC_AUTH_DOWNSTREAM_BLOCKED)

    if role in RESEARCH_SAFE_ROLES and governed_valid and not _auth_blocking_codes(reason_codes):
        _append_unique(reason_codes, RC_AUTH_RESEARCH_ONLY)
        warnings.append("Research-only inspection; downstream export not authorized.")

    # Status resolution — never AUTHORIZED for production-facing roles in this artifact.
    if role in PRODUCTION_FACING_ROLES or role in DOWNSTREAM_BLOCKED_ROLES:
        status = STATUS_BLOCKED
        authorized = False
    elif not requested_role:
        status = STATUS_UNKNOWN
        authorized = False
        _append_unique(reason_codes, RC_AUTH_DOWNSTREAM_BLOCKED)
    elif _auth_blocking_codes(reason_codes):
        status = STATUS_BLOCKED
        authorized = False
    elif role in RESEARCH_SAFE_ROLES and governed_valid:
        status = STATUS_RESTRICTED
        authorized = False
    else:
        status = STATUS_BLOCKED
        authorized = False

    downstream_auth_status = "blocked" if status == STATUS_BLOCKED else "restricted"

    return DownstreamReadoutAuthorizationResult(
        status=status,
        severity=status,
        authorized=authorized,
        requested_role=requested_role,
        reason_codes=tuple(reason_codes),
        warnings=tuple(warnings),
        blocked_roles=_DEFAULT_BLOCKED_ROLES,
        governed_readout_present=governed_present,
        governed_readout_valid=governed_valid,
        inference_boundary_status=boundary_status,
        combination_status=combination_status,
        dcm_row_id=dcm_row_id,
        design_id=design_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        downstream_authorization_status=downstream_auth_status,
        promotion_status=promo_status,
    )


def assert_downstream_readout_authorized(
    authorization_result: DownstreamReadoutAuthorizationResult | Mapping[str, Any],
    *,
    requested_role: str,
) -> None:
    """Raise when downstream consumption is not permitted."""
    if _is_mapping(authorization_result) and not isinstance(
        authorization_result, DownstreamReadoutAuthorizationResult
    ):
        result = DownstreamReadoutAuthorizationResult(**dict(authorization_result))
    else:
        result = authorization_result  # type: ignore[assignment]

    role = _norm_role(requested_role)
    if role in RESEARCH_SAFE_ROLES and result.status == STATUS_RESTRICTED:
        return
    if result.authorized:
        return
    raise DownstreamReadoutAuthorizationViolation(
        f"Downstream role '{requested_role}' is not authorized "
        f"(status={result.status}, codes={result.reason_codes}).",
        result=result,
    )


def extract_readout_evidence_object(
    payload: Mapping[str, Any] | Any,
) -> ReadoutEvidence | None:
    """Extract governed ``ReadoutEvidence`` from bundle evidence or mapping."""
    if isinstance(payload, ReadoutEvidence):
        return payload
    if not _is_mapping(payload):
        return None
    raw = payload.get("readout_evidence")
    if raw is None and payload.get("evidence_version"):
        raw = payload
    if raw is None:
        return None
    readout, is_native = _coerce_readout_evidence(raw)
    if is_native:
        return None
    return readout


__all__ = [
    "AUTHORIZATION_VERSION",
    "DOWNSTREAM_READOUT_NOT_AUTHORIZED",
    "DownstreamPromotionEvidence",
    "DownstreamReadoutAuthorizationResult",
    "DownstreamReadoutAuthorizationViolation",
    "PRODUCTION_FACING_ROLES",
    "RESEARCH_SAFE_ROLES",
    "STATUS_AUTHORIZED",
    "STATUS_BLOCKED",
    "STATUS_RESTRICTED",
    "STATUS_UNKNOWN",
    "assert_downstream_readout_authorized",
    "evaluate_downstream_readout_authorization",
    "extract_readout_evidence_object",
]

# Re-export for Track B wiring compatibility.
DOWNSTREAM_READOUT_NOT_AUTHORIZED = "downstream_readout_not_authorized"
