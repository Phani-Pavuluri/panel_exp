"""TRUSTREPORT-ELIGIBILITY-VALIDATION-001 — promotion candidacy evaluation (not authorization)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from panel_exp.evidence import ReadoutEvidence
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_BLOCK
from panel_exp.validation.downstream_readout_authorization_001 import (
    extract_readout_evidence_object,
)
from panel_exp.validation.estimator_readout_adapter_001 import GOVERNED_READOUT_MARKER

ELIGIBILITY_VERSION = "1.0.0"

STATUS_ELIGIBLE_CANDIDATE = "ELIGIBLE_CANDIDATE"
STATUS_ELIGIBLE_WITH_RESTRICTIONS = "ELIGIBLE_WITH_RESTRICTIONS"
STATUS_INELIGIBLE = "INELIGIBLE"
STATUS_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
STATUS_UNKNOWN = "UNKNOWN"

RC_MISSING_GOVERNED = "TR-ELIG-MISSING-GOVERNED-READOUT"
RC_INVALID_MARKER = "TR-ELIG-INVALID-GOVERNED-MARKER"
RC_MISSING_BOUNDARY = "TR-ELIG-MISSING-BOUNDARY-EVIDENCE"
RC_COMBINATION_BLOCKED = "TR-ELIG-COMBINATION-BLOCKED"
RC_COMBINATION_UNKNOWN = "TR-ELIG-COMBINATION-UNKNOWN"
RC_GEOMETRY_MISMATCH = "TR-ELIG-GEOMETRY-MISMATCH"
RC_POINT_ONLY = "TR-ELIG-POINT-ONLY"
RC_NULL_NOT_CAUSAL = "TR-ELIG-NULL-MONITOR-NOT-CAUSAL"
RC_FORECAST_NOT_CAUSAL = "TR-ELIG-FORECAST-NOT-CAUSAL"
RC_SIGN_NOT_SIG = "TR-ELIG-SIGN-NOT-SIGNIFICANCE"
RC_POOLED_MULTICELL = "TR-ELIG-POOLED-MULTICELL-BLOCKED"
RC_MISSING_CELL_ID = "TR-ELIG-MISSING-CELL-ID"
RC_SHARED_CONTROL_MISSING = "TR-ELIG-SHARED-CONTROL-METADATA-MISSING"
RC_ESTIMAND_MISMATCH = "TR-ELIG-ESTIMAND-MISMATCH"
RC_MISSING_COVERAGE = "TR-ELIG-MISSING-COVERAGE-EVIDENCE"
RC_TYPE_I_OUT = "TR-ELIG-TYPE-I-ERROR-OUT-OF-BOUNDS"
RC_POWER_INSUFFICIENT = "TR-ELIG-POWER-INSUFFICIENT"
RC_BIAS_OUT = "TR-ELIG-BIAS-OUT-OF-BOUNDS"
RC_RMSE_OUT = "TR-ELIG-RMSE-OUT-OF-BOUNDS"
RC_FAILURE_RATE_OUT = "TR-ELIG-FAILURE-RATE-OUT-OF-BOUNDS"
RC_WORST_WORLD_MISSING = "TR-ELIG-WORST-WORLD-EVIDENCE-MISSING"
RC_PROVENANCE_INCOMPLETE = "TR-ELIG-PROVENANCE-INCOMPLETE"
RC_FRESHNESS_STALE = "TR-ELIG-FRESHNESS-STALE"
RC_FRESHNESS_UNKNOWN = "TR-ELIG-FRESHNESS-UNKNOWN"
RC_INSUFFICIENT = "TR-ELIG-INSUFFICIENT-EVIDENCE"
RC_PROMOTION_CANDIDATE = "TR-ELIG-PROMOTION-CANDIDATE"
RC_AUTH_STILL_BLOCKED = "TR-ELIG-AUTHORIZATION-STILL-BLOCKED"

PROVISIONAL_THRESHOLDS: dict[str, Any] = {
    "label": "provisional_for_trustreport_eligibility_only",
    "coverage_nominal": 0.90,
    "coverage_deviation_max": 0.15,
    "coverage_positive_min": 0.50,
    "type_i_error_clean_null_max": 0.10,
    "type_i_error_weak_signal_max": 0.35,
    "failure_rate_max": 0.10,
    "failure_rate_characterization_max": 0.35,
    "power_min": 0.50,
    "bias_effect_scale_ratio_max": 1.0,
    "freshness_max_days": 365,
}

_FORECAST_SEMANTICS = frozenset(
    {"forecast_interval", "forecast_point", "predictive_interval"}
)
_NULL_MONITOR_SEMANTICS = frozenset(
    {"null_monitor_interval", "null_monitor_point", "placebo_interval"}
)
_CAUSAL_SEMANTICS = frozenset(
    {"causal_interval", "per_cell_interval", "significance_test"}
)


class TrustReportEligibilityViolation(RuntimeError):
    """Raised when promotion candidacy requirements are not met."""

    def __init__(self, message: str, *, result: "TrustReportEligibilityResult") -> None:
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class TrustReportEmpiricalEvidence:
    """Compact statistical and provenance evidence for eligibility evaluation."""

    artifact_id: str | None = None
    evidence_source: str = "not_evaluated"
    coverage: float | None = None
    coverage_null: float | None = None
    coverage_positive: float | None = None
    type_i_error: float | None = None
    power: float | None = None
    bias: float | None = None
    rmse: float | None = None
    interval_width: float | None = None
    failure_rate: float | None = None
    worst_world_status: str | None = None
    provenance_complete: bool = False
    freshness_status: str | None = None
    effect_scale: float | None = None
    dcm_row_id: str | None = None
    trust_role_allowed_in_source: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "TrustReportEmpiricalEvidence | None":
        if not data:
            return None
        return cls(
            artifact_id=data.get("artifact_id"),
            evidence_source=str(data.get("evidence_source", "not_evaluated")),
            coverage=_float_or_none(data.get("coverage")),
            coverage_null=_float_or_none(data.get("coverage_null")),
            coverage_positive=_float_or_none(data.get("coverage_positive")),
            type_i_error=_float_or_none(data.get("type_i_error")),
            power=_float_or_none(data.get("power")),
            bias=_float_or_none(data.get("bias")),
            rmse=_float_or_none(data.get("rmse")),
            interval_width=_float_or_none(data.get("interval_width")),
            failure_rate=_float_or_none(data.get("failure_rate")),
            worst_world_status=data.get("worst_world_status"),
            provenance_complete=bool(data.get("provenance_complete", False)),
            freshness_status=data.get("freshness_status"),
            effect_scale=_float_or_none(data.get("effect_scale")),
            dcm_row_id=data.get("dcm_row_id"),
            trust_role_allowed_in_source=data.get("trust_role_allowed_in_source"),
        )


@dataclass(frozen=True)
class TrustReportEligibilityResult:
    status: str
    eligible_for_promotion: bool
    trust_report_authorized: bool
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    design_id: str | None
    geometry_id: str | None
    estimator_id: str | None
    inference_id: str | None
    dcm_row_id: str | None
    combination_status: str | None
    readout_semantics: str | None
    interval_type: str | None
    estimand: str | None
    coverage: float | None
    type_i_error: float | None
    power: float | None
    bias: float | None
    rmse: float | None
    interval_width: float | None
    failure_rate: float | None
    worst_world_status: str | None
    provenance_complete: bool
    freshness_status: str | None
    eligibility_version: str = ELIGIBILITY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _append_unique(codes: list[str], code: str) -> None:
    if code and code not in codes:
        codes.append(code)


def _coerce_readout(readout_evidence: Any) -> tuple[ReadoutEvidence | None, bool]:
    if readout_evidence is None:
        return None, False
    if isinstance(readout_evidence, ReadoutEvidence):
        return readout_evidence, False
    if _is_mapping(readout_evidence):
        obj = extract_readout_evidence_object(readout_evidence)
        if obj is not None:
            return obj, False
        if readout_evidence.get("evidence_version"):
            return None, False
        if any(k in readout_evidence for k in ("y", "y_hat", "cumulative_att", "results")):
            return None, True
    return None, True


def _has_governed_marker(readout: ReadoutEvidence) -> bool:
    payload = readout.result_payload or {}
    meta = payload.get("metadata") if _is_mapping(payload.get("metadata")) else {}
    if meta.get(GOVERNED_READOUT_MARKER) is True:
        return True
    return payload.get(GOVERNED_READOUT_MARKER) is True


def _invalid_marker(readout: ReadoutEvidence) -> bool:
    payload = readout.result_payload or {}
    meta = payload.get("metadata") if _is_mapping(payload.get("metadata")) else {}
    for source in (meta, payload):
        if GOVERNED_READOUT_MARKER in source and source.get(GOVERNED_READOUT_MARKER) is not True:
            return True
    return False


def _validate_statistical_evidence(
    empirical: TrustReportEmpiricalEvidence | None,
    *,
    readout_semantics: str | None,
    dcm_row_id: str | None,
    codes: list[str],
    warnings: list[str],
) -> bool:
    """Return True when statistical evidence is complete enough for candidacy."""
    if empirical is None:
        _append_unique(codes, RC_INSUFFICIENT)
        _append_unique(codes, RC_MISSING_COVERAGE)
        _append_unique(codes, RC_WORST_WORLD_MISSING)
        _append_unique(codes, RC_PROVENANCE_INCOMPLETE)
        return False

    complete = True
    if not empirical.provenance_complete:
        _append_unique(codes, RC_PROVENANCE_INCOMPLETE)
        complete = False

    freshness = (empirical.freshness_status or "unknown").lower()
    if freshness == "stale":
        _append_unique(codes, RC_FRESHNESS_STALE)
        complete = False
    elif freshness == "unknown":
        _append_unique(codes, RC_FRESHNESS_UNKNOWN)
        complete = False

    if empirical.coverage is None and empirical.coverage_null is None and empirical.coverage_positive is None:
        if (readout_semantics or "").lower() in _CAUSAL_SEMANTICS:
            _append_unique(codes, RC_MISSING_COVERAGE)
            complete = False
    else:
        null_cov = empirical.coverage_null if empirical.coverage_null is not None else empirical.coverage
        pos_cov = empirical.coverage_positive
        rs = (readout_semantics or "").lower()
        if rs in _CAUSAL_SEMANTICS and pos_cov is not None:
            if pos_cov < PROVISIONAL_THRESHOLDS["coverage_positive_min"]:
                warnings.append(
                    f"Positive-scenario coverage {pos_cov:.3f} below provisional minimum "
                    f"{PROVISIONAL_THRESHOLDS['coverage_positive_min']}; causal interval not eligible."
                )
                complete = False
        elif null_cov is not None:
            nominal = PROVISIONAL_THRESHOLDS["coverage_nominal"]
            if abs(null_cov - nominal) > PROVISIONAL_THRESHOLDS["coverage_deviation_max"]:
                warnings.append(f"Null-world coverage {null_cov:.3f} deviates from nominal.")

    if empirical.type_i_error is not None:
        limit = PROVISIONAL_THRESHOLDS["type_i_error_clean_null_max"]
        if empirical.type_i_error > limit:
            _append_unique(codes, RC_TYPE_I_OUT)
            complete = False

    if empirical.failure_rate is not None:
        if empirical.failure_rate > PROVISIONAL_THRESHOLDS["failure_rate_max"]:
            _append_unique(codes, RC_FAILURE_RATE_OUT)
            complete = False

    if empirical.bias is not None and empirical.effect_scale is not None:
        if empirical.effect_scale > 0:
            ratio = abs(empirical.bias) / empirical.effect_scale
            if ratio > PROVISIONAL_THRESHOLDS["bias_effect_scale_ratio_max"]:
                warnings.append(
                    f"Positive-scenario bias ratio {ratio:.2f} exceeds provisional scale bound; "
                    "restricts causal-interval candidacy."
                )
                complete = False

    if empirical.power is not None and empirical.power < PROVISIONAL_THRESHOLDS["power_min"]:
        _append_unique(codes, RC_POWER_INSUFFICIENT)
        complete = False

    if not empirical.worst_world_status:
        _append_unique(codes, RC_WORST_WORLD_MISSING)
        complete = False

    if empirical.trust_role_allowed_in_source is False and dcm_row_id:
        warnings.append(f"D5 source for {dcm_row_id} marks trust_role_allowed=false.")

    return complete


def _apply_dcm_rules(
    *,
    dcm_row_id: str | None,
    combination_status: str | None,
    geometry_id: str | None,
    estimator_id: str | None,
    inference_id: str | None,
    readout_semantics: str | None,
    estimand: str | None,
    pooled: bool,
    cell_id: str | None,
    multi_cell: Mapping[str, Any] | None,
    codes: list[str],
    warnings: list[str],
) -> str | None:
    """Return provisional DCM status hint or None."""
    rs = (readout_semantics or "").lower()
    dcm = dcm_row_id or ""

    if pooled or dcm == "DCM-007" or rs in ("pooled_point", "pooled_interval"):
        _append_unique(codes, RC_POOLED_MULTICELL)
        return STATUS_INELIGIBLE

    if dcm == "DCM-003" or combination_status == "blocked_due_to_geometry_mismatch":
        _append_unique(codes, RC_GEOMETRY_MISMATCH)
        return STATUS_INELIGIBLE

    if dcm == "DCM-002":
        if rs in _CAUSAL_SEMANTICS:
            _append_unique(codes, RC_POINT_ONLY)
            return STATUS_INELIGIBLE
        if rs == "point_estimate":
            warnings.append("Point-only descriptive readout; not causal interval evidence.")
            return STATUS_ELIGIBLE_WITH_RESTRICTIONS

    if inference_id in ("placebo",) and rs in _CAUSAL_SEMANTICS:
        _append_unique(codes, RC_NULL_NOT_CAUSAL)
        return STATUS_INELIGIBLE

    if rs in _NULL_MONITOR_SEMANTICS and estimand not in (None, "", "unknown", "null_viability"):
        _append_unique(codes, RC_NULL_NOT_CAUSAL)

    if rs in _FORECAST_SEMANTICS:
        _append_unique(codes, RC_FORECAST_NOT_CAUSAL)
        return STATUS_INELIGIBLE

    if rs == "significance_test" and estimand in (None, "", "unknown"):
        _append_unique(codes, RC_SIGN_NOT_SIG)

    if dcm == "DCM-006" or geometry_id == "multi_cell_per_cell":
        if not cell_id:
            _append_unique(codes, RC_MISSING_CELL_ID)
        mc = multi_cell or {}
        if not mc.get("shared_control_policy") or not mc.get("control_reuse_policy"):
            _append_unique(codes, RC_SHARED_CONTROL_MISSING)
        warnings.append("Per-cell only; multiplicity and dependence limitations apply.")
        return STATUS_ELIGIBLE_WITH_RESTRICTIONS

    if dcm == "DCM-001" and rs == "causal_interval":
        warnings.append(
            "Causal interval TrustReport requires positive-scenario coverage evidence; "
            "default restricted to null-monitor / research CI unless proven."
        )
        return STATUS_ELIGIBLE_WITH_RESTRICTIONS

    if dcm == "DCM-008":
        warnings.append("Stratified lane requires separate design+inference evidence from generic DCM-001.")
        return STATUS_ELIGIBLE_WITH_RESTRICTIONS

    if dcm == "DCM-004":
        return STATUS_INSUFFICIENT_EVIDENCE

    if dcm == "DCM-005":
        warnings.append(f"TBRRidge path {inference_id} requires path-specific statistical evidence.")
        return STATUS_INSUFFICIENT_EVIDENCE

    if dcm == "DCM-001":
        return STATUS_ELIGIBLE_WITH_RESTRICTIONS

    return None


def evaluate_trustreport_eligibility(
    *,
    readout_evidence: Any,
    empirical_evidence: TrustReportEmpiricalEvidence | Mapping[str, Any] | None = None,
    consumer_context: Mapping[str, Any] | None = None,
) -> TrustReportEligibilityResult:
    """Evaluate TrustReport promotion candidacy; never authorizes downstream TrustReport."""
    del consumer_context
    codes: list[str] = []
    warnings: list[str] = []

    empirical: TrustReportEmpiricalEvidence | None
    if isinstance(empirical_evidence, TrustReportEmpiricalEvidence):
        empirical = empirical_evidence
    else:
        empirical = TrustReportEmpiricalEvidence.from_dict(empirical_evidence)

    readout, is_native = _coerce_readout(readout_evidence)
    if readout is None:
        if is_native:
            _append_unique(codes, RC_MISSING_GOVERNED)
        else:
            _append_unique(codes, RC_MISSING_GOVERNED)
        return _build_result(
            status=STATUS_UNKNOWN if not is_native else STATUS_INELIGIBLE,
            codes=codes,
            warnings=warnings,
            readout=None,
            empirical=empirical,
        )

    if _invalid_marker(readout):
        _append_unique(codes, RC_INVALID_MARKER)
    elif not _has_governed_marker(readout):
        _append_unique(codes, RC_MISSING_GOVERNED)

    boundary = readout.inference_boundary_guardrail or {}
    if not boundary:
        _append_unique(codes, RC_MISSING_BOUNDARY)
    elif boundary.get("status") == GUARDRAIL_BLOCK:
        _append_unique(codes, RC_COMBINATION_BLOCKED)

    combination = readout.combination_resolution or {}
    combination_status = combination.get("combination_status")
    dcm_row_id = combination.get("dcm_row_id")
    design_id = combination.get("design_id")
    geometry_id = combination.get("geometry_id") or (readout.estimator_identity or {}).get(
        "geometry_id"
    )

    estimator_id = (readout.estimator_identity or {}).get("estimator_id")
    inference_id = (readout.inference_identity or {}).get("inference_id")
    readout_identity = readout.readout_identity or {}
    readout_semantics = readout_identity.get("readout_semantics")
    interval_type = (readout.inference_identity or {}).get("interval_type")
    estimand = readout_identity.get("estimand")
    pooled = bool(readout_identity.get("pooled"))
    cell_id = readout_identity.get("cell_id")

    contract = readout.result_payload if hasattr(readout, "result_payload") else None
    multi_cell = None
    if _is_mapping(readout.result_payload):
        meta = (readout.result_payload or {}).get("metadata") or {}
        if _is_mapping(meta):
            geo_ctx = meta.get("geometry_context") or {}
            if _is_mapping(geo_ctx):
                multi_cell = geo_ctx

    if combination_status in (
        "blocked_for_pooled_claim",
        "blocked_due_to_geometry_mismatch",
    ):
        _append_unique(codes, RC_COMBINATION_BLOCKED)
    elif combination_status in (None, "not_evaluated"):
        _append_unique(codes, RC_COMBINATION_UNKNOWN)

    if not estimator_id:
        _append_unique(codes, RC_MISSING_GOVERNED)
    if not inference_id and (readout_semantics or "").lower() in _CAUSAL_SEMANTICS:
        _append_unique(codes, RC_MISSING_BOUNDARY)
    if not estimand or estimand == "unknown":
        _append_unique(codes, RC_ESTIMAND_MISMATCH)

    dcm_hint = _apply_dcm_rules(
        dcm_row_id=dcm_row_id,
        combination_status=combination_status,
        geometry_id=geometry_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=readout_semantics,
        estimand=estimand,
        pooled=pooled,
        cell_id=cell_id,
        multi_cell=multi_cell if _is_mapping(multi_cell) else None,
        codes=codes,
        warnings=warnings,
    )

    stats_complete = _validate_statistical_evidence(
        empirical,
        readout_semantics=readout_semantics,
        dcm_row_id=dcm_row_id,
        codes=codes,
        warnings=warnings,
    )

    _append_unique(codes, RC_AUTH_STILL_BLOCKED)

    hard_blocking = {
        RC_MISSING_GOVERNED,
        RC_INVALID_MARKER,
        RC_MISSING_BOUNDARY,
        RC_COMBINATION_BLOCKED,
        RC_GEOMETRY_MISMATCH,
        RC_POOLED_MULTICELL,
        RC_POINT_ONLY,
        RC_NULL_NOT_CAUSAL,
        RC_FORECAST_NOT_CAUSAL,
        RC_SIGN_NOT_SIG,
        RC_TYPE_I_OUT,
        RC_FAILURE_RATE_OUT,
    }
    soft_restriction = {
        RC_BIAS_OUT,
        RC_RMSE_OUT,
        RC_POWER_INSUFFICIENT,
        RC_MISSING_COVERAGE,
        RC_INSUFFICIENT,
        RC_PROVENANCE_INCOMPLETE,
        RC_FRESHNESS_STALE,
        RC_FRESHNESS_UNKNOWN,
        RC_WORST_WORLD_MISSING,
    }

    if any(c in hard_blocking for c in codes):
        status = STATUS_INELIGIBLE
    elif dcm_hint == STATUS_INELIGIBLE:
        status = STATUS_INELIGIBLE
    elif dcm_hint == STATUS_INSUFFICIENT_EVIDENCE:
        status = STATUS_INSUFFICIENT_EVIDENCE
        _append_unique(codes, RC_INSUFFICIENT)
    elif not stats_complete:
        if dcm_hint == STATUS_ELIGIBLE_WITH_RESTRICTIONS:
            status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
        else:
            status = STATUS_INSUFFICIENT_EVIDENCE
            _append_unique(codes, RC_INSUFFICIENT)
    elif stats_complete and dcm_hint == STATUS_ELIGIBLE_WITH_RESTRICTIONS:
        status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
    elif stats_complete and not any(c in hard_blocking | soft_restriction for c in codes):
        status = STATUS_ELIGIBLE_CANDIDATE
        _append_unique(codes, RC_PROMOTION_CANDIDATE)
    elif dcm_hint == STATUS_ELIGIBLE_WITH_RESTRICTIONS:
        status = STATUS_ELIGIBLE_WITH_RESTRICTIONS
    elif dcm_hint:
        status = dcm_hint
    else:
        status = STATUS_UNKNOWN

    # Candidacy requires full statistical pass and no blocking codes beyond auth marker.
    eligible_for_promotion = status == STATUS_ELIGIBLE_CANDIDATE

    return _build_result(
        status=status,
        codes=codes,
        warnings=warnings,
        readout=readout,
        empirical=empirical,
        eligible_for_promotion=eligible_for_promotion,
        combination_status=combination_status,
        design_id=design_id,
        geometry_id=geometry_id,
        dcm_row_id=dcm_row_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
    )


def _build_result(
    *,
    status: str,
    codes: list[str],
    warnings: list[str],
    readout: ReadoutEvidence | None,
    empirical: TrustReportEmpiricalEvidence | None,
    eligible_for_promotion: bool = False,
    combination_status: str | None = None,
    design_id: str | None = None,
    geometry_id: str | None = None,
    dcm_row_id: str | None = None,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
) -> TrustReportEligibilityResult:
    return TrustReportEligibilityResult(
        status=status,
        eligible_for_promotion=eligible_for_promotion,
        trust_report_authorized=False,
        reason_codes=tuple(codes),
        warnings=tuple(warnings),
        design_id=design_id,
        geometry_id=geometry_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        dcm_row_id=dcm_row_id,
        combination_status=combination_status,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        coverage=empirical.coverage if empirical else None,
        type_i_error=empirical.type_i_error if empirical else None,
        power=empirical.power if empirical else None,
        bias=empirical.bias if empirical else None,
        rmse=empirical.rmse if empirical else None,
        interval_width=empirical.interval_width if empirical else None,
        failure_rate=empirical.failure_rate if empirical else None,
        worst_world_status=empirical.worst_world_status if empirical else None,
        provenance_complete=bool(empirical and empirical.provenance_complete),
        freshness_status=empirical.freshness_status if empirical else None,
    )


def assert_trustreport_eligible_for_promotion(
    eligibility_result: TrustReportEligibilityResult | Mapping[str, Any],
) -> None:
    """Validate promotion candidacy only; does not authorize TrustReport downstream use."""
    if _is_mapping(eligibility_result) and not isinstance(
        eligibility_result, TrustReportEligibilityResult
    ):
        result = TrustReportEligibilityResult(**dict(eligibility_result))
    else:
        result = eligibility_result  # type: ignore[assignment]

    if result.eligible_for_promotion and result.status == STATUS_ELIGIBLE_CANDIDATE:
        return
    raise TrustReportEligibilityViolation(
        f"TrustReport promotion candidacy not satisfied "
        f"(status={result.status}, codes={result.reason_codes}).",
        result=result,
    )


__all__ = [
    "ELIGIBILITY_VERSION",
    "PROVISIONAL_THRESHOLDS",
    "STATUS_ELIGIBLE_CANDIDATE",
    "STATUS_ELIGIBLE_WITH_RESTRICTIONS",
    "STATUS_INELIGIBLE",
    "STATUS_INSUFFICIENT_EVIDENCE",
    "STATUS_UNKNOWN",
    "TrustReportEligibilityResult",
    "TrustReportEligibilityViolation",
    "TrustReportEmpiricalEvidence",
    "assert_trustreport_eligible_for_promotion",
    "evaluate_trustreport_eligibility",
]
