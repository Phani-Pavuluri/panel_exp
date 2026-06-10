"""DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-001 — design_contract schema validator.

Validates emitted ``design_contract`` blocks per DESIGN-CONTRACT-SCHEMA-001,
DESIGN-CONTRACT-VALIDATION-TEST-PLAN-001, and DESIGN-CONTRACT-VALIDATOR-
IMPLEMENTATION-PLAN-001. Conservative: blocks overclaiming; does not authorize
downstream product use. Does not emit contract fields.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

VALIDATOR_VERSION = "1.0.0"
SCHEMA_NAME_EXPECTED = "DESIGN-CONTRACT-SCHEMA-001"

# Contract status (validator output)
CONTRACT_VALID = "contract_valid"
CONTRACT_VALID_WITH_WARNINGS = "contract_valid_with_warnings"
CONTRACT_INCOMPLETE = "contract_incomplete"
CONTRACT_BLOCKED = "contract_blocked"
CONTRACT_UNKNOWN = "contract_unknown"
CONTRACT_NOT_APPLICABLE = "contract_not_applicable"

# Emitter-claimed status that must not appear without validator pass
EMITTER_STATUS_COMPLETE = "contract_complete"

# Field result outcomes
FIELD_VALID = "field_valid"
FIELD_MISSING_BLOCK = "field_missing_block"
FIELD_MISSING_WARN = "field_missing_warn"
FIELD_INVALID_BLOCK = "field_invalid_block"
FIELD_INVALID_WARN = "field_invalid_warn"
FIELD_NOT_APPLICABLE = "field_not_applicable"
FIELD_FUTURE_RESERVED = "field_future_reserved"

# Severity
SEVERITY_PASS = "PASS"
SEVERITY_WARN = "WARN"
SEVERITY_BLOCK = "BLOCK"
SEVERITY_UNKNOWN = "UNKNOWN"

# Reason codes
RC_MISSING_DESIGN_CONTRACT = "D-CONTRACT-MISSING-DESIGN-CONTRACT"
RC_MISSING_GEOMETRY_ID = "D-CONTRACT-MISSING-GEOMETRY-ID"
RC_MISSING_FORBIDDEN_CLAIMS = "D-CONTRACT-MISSING-FORBIDDEN-CLAIMS"
RC_MISSING_CONCURRENCY = "D-CONTRACT-MISSING-CONCURRENCY"
RC_INVALID_ENUM = "D-CONTRACT-INVALID-ENUM"
RC_EMPTY_FORBIDDEN_CLAIMS = "D-CONTRACT-EMPTY-FORBIDDEN-CLAIMS"
RC_DOWNSTREAM_AUTH_VIOLATION = "D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION"
RC_FALSE_COMPLETE_CLAIM = "D-CONTRACT-CONTRACT-COMPLETE-FALSE-CLAIM"
RC_MISSING_CELL_IDS = "D-CONTRACT-MISSING-CELL-IDS"
RC_MISSING_SHARED_CONTROL_POLICY = "D-CONTRACT-MISSING-SHARED-CONTROL-POLICY"
RC_MISSING_STRATUM_IDS = "D-CONTRACT-MISSING-STRATUM-IDS"
RC_MISSING_RERANDOMIZATION_IDENTITY = "D-CONTRACT-MISSING-RERANDOMIZATION-IDENTITY"
RC_MISSING_TRIM_METADATA = "D-CONTRACT-MISSING-TRIM-METADATA"
RC_MISSING_SUPERGEO_MAP = "D-CONTRACT-MISSING-SUPERGEO-MAP"
RC_POWER_MDE_OVERCLAIM = "D-CONTRACT-POWER-MDE-OVERCLAIM"
RC_LEGACY_UNKNOWN = "D-CONTRACT-LEGACY-UNKNOWN"

GEOMETRY_IDS = frozenset(
    {
        "unit_panel_single_cell",
        "aggregate_two_row",
        "pooled_treated_control_panel",
        "multi_cell_per_cell",
        "pooled_multi_cell",
        "supergeo",
        "trimmed_geometry",
        "time_series_operator_geometry",
    }
)

CONCURRENCY_COMPATIBILITY = frozenset(
    {
        "compatible",
        "compatible_with_constraints",
        "restricted",
        "blocked_without_bridge",
        "not_evaluated",
    }
)

DOWNSTREAM_AUTH_STATUSES = frozenset(
    {
        "blocked",
        "not_authorized",
        "requires_guardrail_pass",
        "requires_statistical_validation",
        "authorized",
    }
)

ARTIFACT_TYPES = frozenset(
    {"design_output_contract", "helper_output", "planning_metadata"}
)

REQUIRED_FORBIDDEN_CLAIMS = frozenset(
    {
        "trust_report",
        "calibration_signal",
        "mmm_calibration",
        "llm_product_recommendation",
        "production_experiment_recommendation",
    }
)

DOWNSTREAM_ROLE_KEYS = (
    "trust_report_eligible",
    "trustreport_eligible",
    "calibration_signal_eligible",
    "mmm_ready",
    "mmm_eligible",
    "llm_authorized",
    "llm_eligible",
    "production_ready",
    "production_ready_status",
    "causal_readout_authorized",
)

STRATIFIED_FAMILIES = frozenset({"stratified_assignment"})
RERANDOMIZATION_WRAPPER = "Rerandomization"


@dataclass
class DesignContractValidationResult:
    status: str = CONTRACT_UNKNOWN
    severity: str = SEVERITY_UNKNOWN
    reason_codes: list[str] = field(default_factory=list)
    field_results: dict[str, str] = field(default_factory=dict)
    missing_required_fields: list[str] = field(default_factory=list)
    missing_conditional_fields: list[str] = field(default_factory=list)
    invalid_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked_downstream_roles: list[str] = field(default_factory=list)
    contract_complete_allowed: bool = False
    guardrail_inputs: dict[str, Any] = field(default_factory=dict)
    suitability_inputs: dict[str, Any] = field(default_factory=dict)
    schema_name: str | None = None
    schema_version: str | None = None
    validator_version: str = VALIDATOR_VERSION

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


def _new_result() -> DesignContractValidationResult:
    return DesignContractValidationResult(
        validator_version=VALIDATOR_VERSION,
        blocked_downstream_roles=[
            "trust_report",
            "calibration_signal",
            "mmm",
            "llm",
            "production",
        ],
    )


def _record_field(
    result: DesignContractValidationResult,
    path: str,
    outcome: str,
    *,
    reason_code: str | None = None,
    missing: bool = False,
    conditional: bool = False,
    invalid: bool = False,
    message: str | None = None,
) -> None:
    result.field_results[path] = outcome
    if reason_code and reason_code not in result.reason_codes:
        result.reason_codes.append(reason_code)
    if missing and path not in result.missing_required_fields:
        if conditional:
            if path not in result.missing_conditional_fields:
                result.missing_conditional_fields.append(path)
        else:
            result.missing_required_fields.append(path)
    if invalid and path not in result.invalid_fields:
        result.invalid_fields.append(path)
    if message and outcome in (FIELD_MISSING_WARN, FIELD_INVALID_WARN):
        result.warnings.append(message)


def _has_block(result: DesignContractValidationResult) -> bool:
    block_outcomes = {FIELD_MISSING_BLOCK, FIELD_INVALID_BLOCK}
    return any(o in block_outcomes for o in result.field_results.values())


def _has_warn_only(result: DesignContractValidationResult) -> bool:
    warn_outcomes = {FIELD_MISSING_WARN, FIELD_INVALID_WARN}
    return any(o in warn_outcomes for o in result.field_results.values())


def _is_legacy_unknown(result: DesignContractValidationResult) -> bool:
    if RC_LEGACY_UNKNOWN in result.reason_codes:
        return True
    if RC_MISSING_DESIGN_CONTRACT in result.reason_codes and not any(
        k for k in result.field_results if k != "design_contract"
    ):
        return True
    return False


def compute_contract_status(result: DesignContractValidationResult) -> str:
    """Aggregate field outcomes into contract status enum."""
    if result.status == CONTRACT_NOT_APPLICABLE:
        return CONTRACT_NOT_APPLICABLE
    if not result.field_results or _is_legacy_unknown(result):
        return CONTRACT_UNKNOWN
    if _has_block(result):
        return CONTRACT_BLOCKED
    if result.missing_required_fields or result.missing_conditional_fields:
        return CONTRACT_INCOMPLETE
    if result.invalid_fields:
        return CONTRACT_BLOCKED
    if _has_warn_only(result):
        return CONTRACT_VALID_WITH_WARNINGS
    if result.field_results and all(
        o in (FIELD_VALID, FIELD_NOT_APPLICABLE, FIELD_FUTURE_RESERVED)
        for o in result.field_results.values()
    ):
        return CONTRACT_VALID
    return CONTRACT_INCOMPLETE


def _finalize_result(result: DesignContractValidationResult) -> DesignContractValidationResult:
    result.status = compute_contract_status(result)
    if _is_legacy_unknown(result):
        result.severity = SEVERITY_UNKNOWN
        result.contract_complete_allowed = False
        result.guardrail_inputs = {
            "guardrail_status": "BLOCK",
            "guardrail_reason_codes": list(result.reason_codes),
        }
        result.suitability_inputs = {
            "suitability_status": "contract_blocked",
            "suitability_reason_codes": ["D-SUIT-CONTRACT-BLOCKED"],
        }
        return result
    if _has_block(result) or result.missing_required_fields or result.missing_conditional_fields:
        result.severity = SEVERITY_BLOCK
        result.contract_complete_allowed = False
        result.guardrail_inputs = {
            "guardrail_status": "BLOCK",
            "guardrail_reason_codes": list(result.reason_codes),
        }
        result.suitability_inputs = {
            "suitability_status": "contract_blocked",
            "suitability_reason_codes": ["D-SUIT-CONTRACT-BLOCKED"],
        }
    elif result.status == CONTRACT_UNKNOWN:
        result.severity = SEVERITY_UNKNOWN
        result.contract_complete_allowed = False
        result.guardrail_inputs = {
            "guardrail_status": "BLOCK",
            "guardrail_reason_codes": [RC_LEGACY_UNKNOWN],
        }
        result.suitability_inputs = {
            "suitability_status": "contract_blocked",
            "suitability_reason_codes": ["D-SUIT-CONTRACT-BLOCKED"],
        }
    elif result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS):
        result.severity = SEVERITY_PASS if result.status == CONTRACT_VALID else SEVERITY_WARN
        # Conservative: metadata pass does not authorize contract_complete or production.
        result.contract_complete_allowed = False
        result.guardrail_inputs = {
            "guardrail_status": "REQUIRES_STATISTICAL_VALIDATION",
            "guardrail_reason_codes": ["D-COMB-STAT-VALIDATION-REQUIRED"],
        }
        result.suitability_inputs = {
            "suitability_status": "stat_validation_required",
            "suitability_reason_codes": ["D-SUIT-STAT-VALIDATION-REQUIRED"],
        }
    else:
        result.severity = SEVERITY_BLOCK if result.status == CONTRACT_BLOCKED else SEVERITY_WARN
        result.contract_complete_allowed = False
        result.guardrail_inputs = {
            "guardrail_status": "BLOCK",
            "guardrail_reason_codes": list(result.reason_codes),
        }
        result.suitability_inputs = {
            "suitability_status": "contract_blocked",
            "suitability_reason_codes": ["D-SUIT-CONTRACT-BLOCKED"],
        }
    return result


def _validate_universal(contract: Mapping[str, Any], result: DesignContractValidationResult) -> None:
    schema_name = contract.get("schema_name")
    result.schema_name = str(schema_name) if schema_name is not None else None
    if schema_name is None:
        _record_field(
            result,
            "schema_name",
            FIELD_MISSING_BLOCK,
            reason_code=RC_INVALID_ENUM,
            missing=True,
        )
    elif schema_name != SCHEMA_NAME_EXPECTED:
        _record_field(
            result,
            "schema_name",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    else:
        _record_field(result, "schema_name", FIELD_VALID)

    schema_version = contract.get("schema_version")
    result.schema_version = str(schema_version) if schema_version is not None else None
    if not schema_version:
        _record_field(
            result,
            "schema_version",
            FIELD_MISSING_BLOCK,
            reason_code=RC_INVALID_ENUM,
            missing=True,
        )
    else:
        _record_field(result, "schema_version", FIELD_VALID)

    artifact_type = contract.get("artifact_type")
    if artifact_type is None:
        _record_field(
            result,
            "artifact_type",
            FIELD_MISSING_BLOCK,
            reason_code=RC_INVALID_ENUM,
            missing=True,
        )
    elif artifact_type not in ARTIFACT_TYPES:
        _record_field(
            result,
            "artifact_type",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    else:
        _record_field(result, "artifact_type", FIELD_VALID)

    emitter_status = contract.get("design_contract_status")
    if emitter_status == EMITTER_STATUS_COMPLETE:
        _record_field(
            result,
            "design_contract_status",
            FIELD_INVALID_BLOCK,
            reason_code=RC_FALSE_COMPLETE_CLAIM,
            invalid=True,
        )

    geometry_id = _nested_get(contract, "geometry.geometry_id")
    if geometry_id is None:
        _record_field(
            result,
            "geometry.geometry_id",
            FIELD_MISSING_BLOCK,
            reason_code=RC_MISSING_GEOMETRY_ID,
            missing=True,
        )
    elif geometry_id not in GEOMETRY_IDS:
        _record_field(
            result,
            "geometry.geometry_id",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    else:
        _record_field(result, "geometry.geometry_id", FIELD_VALID)

    forbidden = _nested_get(contract, "governance.forbidden_downstream_claims")
    if forbidden is None:
        _record_field(
            result,
            "governance.forbidden_downstream_claims",
            FIELD_MISSING_BLOCK,
            reason_code=RC_MISSING_FORBIDDEN_CLAIMS,
            missing=True,
        )
    elif not isinstance(forbidden, list):
        _record_field(
            result,
            "governance.forbidden_downstream_claims",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    elif len(forbidden) == 0:
        _record_field(
            result,
            "governance.forbidden_downstream_claims",
            FIELD_INVALID_BLOCK,
            reason_code=RC_EMPTY_FORBIDDEN_CLAIMS,
            invalid=True,
        )
    else:
        _record_field(result, "governance.forbidden_downstream_claims", FIELD_VALID)
        missing_forbids = REQUIRED_FORBIDDEN_CLAIMS - {str(x) for x in forbidden}
        if missing_forbids:
            _record_field(
                result,
                "governance.forbidden_downstream_claims",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
                message=f"Missing required forbidden claims: {sorted(missing_forbids)}",
            )

    concurrency = _nested_get(contract, "concurrency.concurrent_multi_experiment_compatibility")
    if concurrency is None:
        _record_field(
            result,
            "concurrency.concurrent_multi_experiment_compatibility",
            FIELD_MISSING_BLOCK,
            reason_code=RC_MISSING_CONCURRENCY,
            missing=True,
        )
    elif concurrency not in CONCURRENCY_COMPATIBILITY:
        _record_field(
            result,
            "concurrency.concurrent_multi_experiment_compatibility",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    else:
        _record_field(
            result,
            "concurrency.concurrent_multi_experiment_compatibility",
            FIELD_VALID,
        )

    downstream_auth = _nested_get(contract, "governance.downstream_authorization_status")
    if downstream_auth is None:
        _record_field(
            result,
            "governance.downstream_authorization_status",
            FIELD_MISSING_BLOCK,
            reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
            missing=True,
        )
    elif downstream_auth not in DOWNSTREAM_AUTH_STATUSES:
        _record_field(
            result,
            "governance.downstream_authorization_status",
            FIELD_INVALID_BLOCK,
            reason_code=RC_INVALID_ENUM,
            invalid=True,
        )
    elif downstream_auth not in ("blocked", "not_authorized", "requires_statistical_validation"):
        _record_field(
            result,
            "governance.downstream_authorization_status",
            FIELD_INVALID_BLOCK,
            reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
            invalid=True,
        )
    else:
        _record_field(result, "governance.downstream_authorization_status", FIELD_VALID)

    stat_status = _nested_get(contract, "governance.statistical_validation_status")
    if stat_status in ("validated", "complete", "statistically_validated"):
        _record_field(
            result,
            "governance.statistical_validation_status",
            FIELD_INVALID_BLOCK,
            reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
            invalid=True,
        )


def _validate_no_overclaim(contract: Mapping[str, Any], result: DesignContractValidationResult) -> None:
    governance = contract.get("governance")
    if _is_mapping(governance):
        for key in DOWNSTREAM_ROLE_KEYS:
            if key in governance and governance[key] is True:
                _record_field(
                    result,
                    f"governance.{key}",
                    FIELD_INVALID_BLOCK,
                    reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                    invalid=True,
                )

    compatibility = contract.get("compatibility")
    if _is_mapping(compatibility):
        if compatibility.get("trust_report_eligible") is True:
            _record_field(
                result,
                "compatibility.trust_report_eligible",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
            )
        if compatibility.get("calibration_signal_eligible") is True:
            _record_field(
                result,
                "compatibility.calibration_signal_eligible",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
            )
        if compatibility.get("mmm_eligible") is True:
            _record_field(
                result,
                "compatibility.mmm_eligible",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
            )
        if compatibility.get("llm_authorized") is True:
            _record_field(
                result,
                "compatibility.llm_authorized",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
            )

    power_mde = contract.get("power_mde")
    if _is_mapping(power_mde):
        if power_mde.get("causal_readout_authorized") is True:
            _record_field(
                result,
                "power_mde.causal_readout_authorized",
                FIELD_INVALID_BLOCK,
                reason_code=RC_POWER_MDE_OVERCLAIM,
                invalid=True,
            )
        if power_mde.get("trust_report_eligible") is True or power_mde.get("mmm_ready") is True:
            _record_field(
                result,
                "power_mde",
                FIELD_INVALID_BLOCK,
                reason_code=RC_POWER_MDE_OVERCLAIM,
                invalid=True,
            )


def _is_stratified(contract: Mapping[str, Any]) -> bool:
    identity = contract.get("design_identity")
    if _is_mapping(identity):
        if identity.get("design_family") in STRATIFIED_FAMILIES:
            return True
        method = identity.get("design_method_class") or identity.get("design_name")
        if method and "stratified" in str(method).lower():
            return True
    structure = contract.get("structure")
    if _is_mapping(structure) and structure.get("requires_strata") is True:
        return True
    return False


def _is_multi_cell(contract: Mapping[str, Any]) -> bool:
    multi_cell = contract.get("multi_cell")
    if _is_mapping(multi_cell) and multi_cell.get("is_multi_cell") is True:
        return True
    geometry_id = _nested_get(contract, "geometry.geometry_id")
    return geometry_id == "multi_cell_per_cell"


def _is_rerandomization_wrapped(contract: Mapping[str, Any]) -> bool:
    identity = contract.get("design_identity")
    if not _is_mapping(identity):
        return False
    wrapper = identity.get("wrapper_identity")
    if wrapper == RERANDOMIZATION_WRAPPER:
        return True
    if identity.get("is_rerandomization_wrapped") is True:
        return True
    return False


def _validate_conditional(contract: Mapping[str, Any], result: DesignContractValidationResult) -> None:
    if _is_stratified(contract):
        stratum_ids = _nested_get(contract, "structure.stratum_ids")
        stratum_map = _nested_get(contract, "structure.unit_to_stratum_map")
        if not stratum_ids:
            _record_field(
                result,
                "structure.stratum_ids",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_STRATUM_IDS,
                missing=True,
                conditional=True,
            )
        if not stratum_map:
            _record_field(
                result,
                "structure.unit_to_stratum_map",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_STRATUM_IDS,
                missing=True,
                conditional=True,
            )

    if _is_multi_cell(contract):
        cell_ids = _nested_get(contract, "multi_cell.cell_ids")
        if not cell_ids:
            _record_field(
                result,
                "multi_cell.cell_ids",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_CELL_IDS,
                missing=True,
                conditional=True,
            )
        shared_policy = _nested_get(contract, "multi_cell.shared_control_policy")
        control_reuse = _nested_get(contract, "multi_cell.control_reuse_policy")
        shared_mode = _nested_get(contract, "multi_cell.shared_control_mode")
        if not (shared_policy or control_reuse or shared_mode):
            _record_field(
                result,
                "multi_cell.shared_control_policy",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_SHARED_CONTROL_POLICY,
                missing=True,
                conditional=True,
            )
        pooled_allowed = _nested_get(contract, "multi_cell.pooled_claims_allowed")
        if pooled_allowed is True:
            _record_field(
                result,
                "multi_cell.pooled_claims_allowed",
                FIELD_INVALID_BLOCK,
                reason_code=RC_DOWNSTREAM_AUTH_VIOLATION,
                invalid=True,
            )

    if _is_rerandomization_wrapped(contract):
        wrapper = _nested_get(contract, "design_identity.wrapper_identity")
        base = _nested_get(contract, "design_identity.design_method_class") or _nested_get(
            contract, "design_identity.base_randomizer_cls"
        )
        if not wrapper:
            _record_field(
                result,
                "design_identity.wrapper_identity",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_RERANDOMIZATION_IDENTITY,
                missing=True,
                conditional=True,
            )
        if not base:
            _record_field(
                result,
                "design_identity.design_method_class",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_RERANDOMIZATION_IDENTITY,
                missing=True,
                conditional=True,
            )

    trim_thin = contract.get("trim_thin")
    geometry_id = _nested_get(contract, "geometry.geometry_id")
    trim_triggered = geometry_id == "trimmed_geometry"
    if _is_mapping(trim_thin):
        trim_triggered = trim_triggered or trim_thin.get("is_trimmed") is True or trim_thin.get(
            "is_thinned"
        ) is True
    if trim_triggered:
        if not _is_mapping(trim_thin) or not trim_thin.get("trim_policy") and not trim_thin.get(
            "thin_policy"
        ):
            _record_field(
                result,
                "trim_thin",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_TRIM_METADATA,
                missing=True,
                conditional=True,
            )

    supergeo_block = contract.get("supergeo")
    supergeo_triggered = geometry_id == "supergeo"
    if _is_mapping(supergeo_block) and supergeo_block.get("is_supergeo") is True:
        supergeo_triggered = True
    if supergeo_triggered:
        source_map = _nested_get(contract, "supergeo.supergeo_source_unit_map")
        if not source_map:
            _record_field(
                result,
                "supergeo.supergeo_source_unit_map",
                FIELD_MISSING_BLOCK,
                reason_code=RC_MISSING_SUPERGEO_MAP,
                missing=True,
                conditional=True,
            )


def validate_design_contract(contract: Mapping[str, Any] | None) -> DesignContractValidationResult:
    """Validate a standalone design_contract mapping."""
    result = _new_result()
    if contract is None or not _is_mapping(contract) or len(contract) == 0:
        result.status = CONTRACT_UNKNOWN
        result.reason_codes.append(RC_MISSING_DESIGN_CONTRACT)
        result.field_results["design_contract"] = FIELD_MISSING_BLOCK
        return _finalize_result(result)

    if contract.get("artifact_type") == "helper_output":
        result.status = CONTRACT_NOT_APPLICABLE
        result.severity = SEVERITY_PASS
        _record_field(result, "artifact_type", FIELD_NOT_APPLICABLE)
        return _finalize_result(result)

    _validate_universal(contract, result)
    _validate_conditional(contract, result)
    _validate_no_overclaim(contract, result)
    return _finalize_result(result)


def validate_design_evidence_contract(
    evidence: Mapping[str, Any] | None,
) -> DesignContractValidationResult:
    """Validate design_contract nested in a DesignEvidence / ExperimentEvidence dict."""
    result = _new_result()
    if evidence is None or not _is_mapping(evidence):
        result.status = CONTRACT_UNKNOWN
        result.reason_codes.append(RC_LEGACY_UNKNOWN)
        result.field_results["design_contract"] = FIELD_MISSING_BLOCK
        return _finalize_result(result)

    contract = evidence.get("design_contract")
    if contract is None:
        result.status = CONTRACT_UNKNOWN
        result.reason_codes.append(RC_LEGACY_UNKNOWN)
        result.field_results["design_contract"] = FIELD_MISSING_BLOCK
        return _finalize_result(result)

    if not _is_mapping(contract):
        result.status = CONTRACT_UNKNOWN
        result.reason_codes.append(RC_MISSING_DESIGN_CONTRACT)
        result.field_results["design_contract"] = FIELD_INVALID_BLOCK
        return _finalize_result(result)

    return validate_design_contract(contract)
