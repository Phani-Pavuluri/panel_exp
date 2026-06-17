"""DESIGN-GUARDRAIL-ENFORCEMENT-001 — design × estimator × inference combination guardrails.

Consumes executed combination-validation evidence (DCM-001–008) and enforces
geometry, readout, and multi-cell restrictions. No downstream promotion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from panel_exp.validation.design_guardrail_runtime_001 import (
    GUARDRAIL_BLOCK,
    GUARDRAIL_UNKNOWN,
    GUARDRAIL_WARN,
)

COMBINATION_GUARDRAIL_VERSION = "1.0.0"

# Enforcement reason codes (combination layer)
RC_ENFORCE_COMBINATION_UNKNOWN = "D-ENFORCE-COMBINATION-UNKNOWN"
RC_ENFORCE_COMBINATION_BLOCKED = "D-ENFORCE-COMBINATION-BLOCKED"
RC_ENFORCE_GEOMETRY_MISMATCH = "D-ENFORCE-GEOMETRY-MISMATCH"
RC_ENFORCE_READOUT_MISMATCH = "D-ENFORCE-READOUT-MISMATCH"
RC_ENFORCE_POINT_ONLY = "D-ENFORCE-POINT-ONLY"
RC_ENFORCE_NULL_MONITOR_ONLY = "D-ENFORCE-NULL-MONITOR-ONLY"
RC_ENFORCE_FORECAST_NOT_CAUSAL = "D-ENFORCE-FORECAST-NOT-CAUSAL"
RC_ENFORCE_POOLED_MULTICELL_BLOCKED = "D-ENFORCE-POOLED-MULTICELL-BLOCKED"
RC_ENFORCE_SHARED_CONTROL_DEPENDENCE = "D-ENFORCE-SHARED-CONTROL-DEPENDENCE"
RC_ENFORCE_ADAPTER_REQUIRED = "D-ENFORCE-ADAPTER-REQUIRED"
RC_ENFORCE_BRIDGE_REQUIRED = "D-ENFORCE-BRIDGE-REQUIRED"
RC_ENFORCE_STAT_VALIDATION_REQUIRED = "D-ENFORCE-STAT-VALIDATION-REQUIRED"
RC_ENFORCE_RESEARCH_ONLY = "D-ENFORCE-RESEARCH-ONLY"

COMBINATION_STATUS_NOT_EVALUATED = "not_evaluated"

_RESEARCH_SCOPES = ("research", "diagnostic", "validation")

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


@dataclass(frozen=True)
class CombinationRegistryEntry:
    combination_id: str
    combination_status: str
    research_permitted: bool
    downstream_permitted: bool
    interval_claim_permitted: bool
    point_only: bool = False
    per_cell_only: bool = False
    geometry_required: str | None = None
    reason_codes: tuple[str, ...] = ()
    enforcement_reason: str = RC_ENFORCE_RESEARCH_ONLY


EXECUTED_COMBINATION_REGISTRY: dict[str, CombinationRegistryEntry] = {
    "DCM-001": CombinationRegistryEntry(
        "DCM-001",
        "characterized_with_restrictions",
        research_permitted=True,
        downstream_permitted=False,
        interval_claim_permitted=True,
        enforcement_reason=RC_ENFORCE_STAT_VALIDATION_REQUIRED,
    ),
    "DCM-002": CombinationRegistryEntry(
        "DCM-002",
        "compatible_point_only",
        research_permitted=True,
        downstream_permitted=False,
        interval_claim_permitted=False,
        point_only=True,
        enforcement_reason=RC_ENFORCE_RESEARCH_ONLY,
    ),
    "DCM-003": CombinationRegistryEntry(
        "DCM-003",
        "blocked_due_to_geometry_mismatch",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        geometry_required="aggregate_two_row",
        reason_codes=(RC_ENFORCE_GEOMETRY_MISMATCH,),
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
    "DCM-004": CombinationRegistryEntry(
        "DCM-004",
        "characterized_with_restrictions",
        research_permitted=True,
        downstream_permitted=False,
        interval_claim_permitted=True,
        enforcement_reason=RC_ENFORCE_STAT_VALIDATION_REQUIRED,
    ),
    "DCM-006": CombinationRegistryEntry(
        "DCM-006",
        "compatible_per_cell_only",
        research_permitted=True,
        downstream_permitted=False,
        interval_claim_permitted=True,
        per_cell_only=True,
        geometry_required="multi_cell_per_cell",
        enforcement_reason=RC_ENFORCE_SHARED_CONTROL_DEPENDENCE,
    ),
    "DCM-007": CombinationRegistryEntry(
        "DCM-007",
        "blocked_for_pooled_claim",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_POOLED_MULTICELL_BLOCKED,),
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
    "DCM-008": CombinationRegistryEntry(
        "DCM-008",
        "characterized_with_restrictions",
        research_permitted=True,
        downstream_permitted=False,
        interval_claim_permitted=True,
        enforcement_reason=RC_ENFORCE_STAT_VALIDATION_REQUIRED,
    ),
}

PRIOR_COMBINATION_REGISTRY: dict[str, CombinationRegistryEntry] = {
    "DCM-005": CombinationRegistryEntry(
        "DCM-005",
        "restricted_requires_statistical_validation",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        enforcement_reason=RC_ENFORCE_STAT_VALIDATION_REQUIRED,
    ),
    "DCM-009": CombinationRegistryEntry(
        "DCM-009",
        "adapter_required",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_ADAPTER_REQUIRED,),
        enforcement_reason=RC_ENFORCE_ADAPTER_REQUIRED,
    ),
    "DCM-010": CombinationRegistryEntry(
        "DCM-010",
        "blocked_due_to_readout_mismatch",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_READOUT_MISMATCH,),
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
    "DCM-011": CombinationRegistryEntry(
        "DCM-011",
        "bridge_required",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_BRIDGE_REQUIRED,),
        enforcement_reason=RC_ENFORCE_BRIDGE_REQUIRED,
    ),
    "DCM-012": CombinationRegistryEntry(
        "DCM-012",
        "bridge_required",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_BRIDGE_REQUIRED,),
        enforcement_reason=RC_ENFORCE_BRIDGE_REQUIRED,
    ),
    "DCM-013": CombinationRegistryEntry(
        "DCM-013",
        "bridge_required",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_BRIDGE_REQUIRED,),
        enforcement_reason=RC_ENFORCE_BRIDGE_REQUIRED,
    ),
    "DCM-014": CombinationRegistryEntry(
        "DCM-014",
        "blocked_due_to_geometry_mismatch",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_GEOMETRY_MISMATCH,),
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
    "DCM-015": CombinationRegistryEntry(
        "DCM-015",
        "restricted_requires_contract_fields",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        enforcement_reason=RC_ENFORCE_STAT_VALIDATION_REQUIRED,
    ),
    "DCM-016": CombinationRegistryEntry(
        "DCM-016",
        "blocked_due_to_implementation_ambiguity",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
    "DCM-017": CombinationRegistryEntry(
        "DCM-017",
        "not_evaluated",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        enforcement_reason=RC_ENFORCE_COMBINATION_UNKNOWN,
    ),
    "DCM-018": CombinationRegistryEntry(
        "DCM-018",
        "not_evaluated",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        enforcement_reason=RC_ENFORCE_COMBINATION_UNKNOWN,
    ),
    "DCM-019": CombinationRegistryEntry(
        "DCM-019",
        "blocked_due_to_readout_mismatch",
        research_permitted=False,
        downstream_permitted=False,
        interval_claim_permitted=False,
        reason_codes=(RC_ENFORCE_FORECAST_NOT_CAUSAL,),
        enforcement_reason=RC_ENFORCE_COMBINATION_BLOCKED,
    ),
}

COMBINATION_REGISTRY: dict[str, CombinationRegistryEntry] = {
    **EXECUTED_COMBINATION_REGISTRY,
    **PRIOR_COMBINATION_REGISTRY,
}


@dataclass
class DesignCombinationGuardrailResult:
    status: str = GUARDRAIL_UNKNOWN
    combination_id: str | None = None
    combination_status: str = COMBINATION_STATUS_NOT_EVALUATED
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked_roles: list[str] = field(default_factory=lambda: list(_DEFAULT_BLOCKED_ROLES))
    design_id: str | None = None
    estimator_id: str | None = None
    inference_id: str | None = None
    geometry_id: str | None = None
    readout_semantics: str | None = None
    permitted_research_scopes: list[str] = field(default_factory=lambda: list(_RESEARCH_SCOPES))
    combination_guardrail_version: str = COMBINATION_GUARDRAIL_VERSION

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


def _normalize_id(value: str | None) -> str:
    return (value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _design_id_from_contract(contract: Mapping[str, Any] | None) -> str | None:
    if contract is None:
        return None
    identity = contract.get("design_identity")
    if _is_mapping(identity) and identity.get("design_inventory_id"):
        return str(identity["design_inventory_id"])
    return None


def _geometry_from_contract(contract: Mapping[str, Any] | None) -> str | None:
    if contract is None:
        return None
    geometry = contract.get("geometry")
    if _is_mapping(geometry) and geometry.get("geometry_id"):
        return str(geometry["geometry_id"])
    return None


def _readout_claim_blocked(readout_semantics: str | None, claim_type: str) -> tuple[bool, str | None]:
    rs = _normalize_id(readout_semantics)
    ct = _normalize_id(claim_type)
    if rs == "point_only" and ct in ("causal_interval", "significance_test", "uncertainty_claim"):
        return True, RC_ENFORCE_POINT_ONLY
    if rs == "forecast_interval" and ct == "causal_interval":
        return True, RC_ENFORCE_FORECAST_NOT_CAUSAL
    if rs == "directional_sign" and ct == "significance_test":
        return True, RC_ENFORCE_READOUT_MISMATCH
    if rs == "null_monitor" and ct == "causal_inference":
        return True, RC_ENFORCE_NULL_MONITOR_ONLY
    return False, None


def _resolve_combination_id(
    *,
    design_id: str | None,
    estimator_id: str | None,
    inference_id: str | None,
    geometry_id: str | None,
    design_contract: Mapping[str, Any] | None,
) -> str | None:
    if not estimator_id and not inference_id:
        return None

    des = (design_id or _design_id_from_contract(design_contract) or "").upper()
    est = _normalize_id(estimator_id)
    inf = _normalize_id(inference_id)
    geo = _normalize_id(geometry_id or _geometry_from_contract(design_contract))

    if geo == "pooled_multi_cell" or "pooled" in est:
        return "DCM-007"

    if des in ("DES-009",) or "trimmed" in est:
        return "DCM-011"
    if des in ("DES-010",) or "supergeo" in geo:
        return "DCM-013"
    if des in ("DES-005",):
        return "DCM-016"

    if geo == "multi_cell_per_cell" or (des == "DES-011" and geo != "pooled_multi_cell"):
        if "scm" in est or "synthetic" in est:
            return "DCM-006"

    if des == "DES-004" and ("scm" in est or "synthetic" in est):
        return "DCM-008"

    if "augsynth" in est or ("aug" in est and "synth" in est):
        return "DCM-002"

    if "tbr" in est and "ridge" not in est:
        return "DCM-003"

    if "did" in est:
        return "DCM-004"

    if "scm" in est or "synthetic" in est:
        return "DCM-001"

    if "tbrridge" in est or "tbr_ridge" in est:
        return "DCM-005"

    if "sarimax" in est:
        return "DCM-019"

    return None


def _multicell_metadata_ok(contract: Mapping[str, Any] | None) -> tuple[bool, list[str]]:
    if contract is None:
        return False, [RC_ENFORCE_SHARED_CONTROL_DEPENDENCE]
    multi = contract.get("multi_cell")
    if not _is_mapping(multi) or not multi.get("is_multi_cell"):
        return True, []
    reasons: list[str] = []
    if not multi.get("cell_ids"):
        reasons.append(RC_ENFORCE_SHARED_CONTROL_DEPENDENCE)
    if multi.get("shared_control_policy") is None:
        reasons.append(RC_ENFORCE_SHARED_CONTROL_DEPENDENCE)
    if multi.get("control_reuse_policy") is None:
        reasons.append(RC_ENFORCE_SHARED_CONTROL_DEPENDENCE)
    return len(reasons) == 0, reasons


def evaluate_design_combination_guardrails(
    *,
    design_contract: Mapping[str, Any] | None,
    contract_validation: Mapping[str, Any] | None = None,
    design_guardrail: Mapping[str, Any] | None = None,
    design_id: str | None = None,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    geometry_id: str | None = None,
    readout_semantics: str | None = None,
    requested_downstream_role: str | None = None,
    readout_claim_type: str | None = None,
) -> DesignCombinationGuardrailResult:
    """Evaluate combination guardrails for a design × estimator × inference path."""
    del contract_validation, design_guardrail, requested_downstream_role  # reserved for future layering

    resolved_design = design_id or _design_id_from_contract(design_contract)
    resolved_geometry = geometry_id or _geometry_from_contract(design_contract)
    combination_id = _resolve_combination_id(
        design_id=resolved_design,
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=resolved_geometry,
        design_contract=design_contract,
    )

    reason_codes: list[str] = []
    warnings: list[str] = []
    blocked_roles = list(_DEFAULT_BLOCKED_ROLES)

    if combination_id is None:
        return DesignCombinationGuardrailResult(
            status=GUARDRAIL_UNKNOWN,
            combination_id=None,
            combination_status=COMBINATION_STATUS_NOT_EVALUATED,
            reason_codes=[RC_ENFORCE_COMBINATION_UNKNOWN],
            warnings=["Estimator/inference identity absent; combination not evaluated."],
            blocked_roles=blocked_roles,
            design_id=resolved_design,
            estimator_id=estimator_id,
            inference_id=inference_id,
            geometry_id=resolved_geometry,
            readout_semantics=readout_semantics,
            permitted_research_scopes=[],
        )

    entry = COMBINATION_REGISTRY[combination_id]
    combination_status = entry.combination_status
    permitted = list(_RESEARCH_SCOPES) if entry.research_permitted else []

    for code in entry.reason_codes:
        _append_unique(reason_codes, code)

    # Geometry enforcement
    if entry.geometry_required and resolved_geometry:
        if _normalize_id(resolved_geometry) != _normalize_id(entry.geometry_required):
            if combination_id == "DCM-003" and _normalize_id(resolved_geometry) == "unit_panel_single_cell":
                _append_unique(reason_codes, RC_ENFORCE_GEOMETRY_MISMATCH)
                combination_status = "blocked_due_to_geometry_mismatch"
            elif entry.geometry_required and _normalize_id(resolved_geometry) != _normalize_id(
                entry.geometry_required
            ):
                _append_unique(reason_codes, RC_ENFORCE_GEOMETRY_MISMATCH)

    if combination_id == "DCM-003" and _normalize_id(resolved_geometry or "") == "unit_panel_single_cell":
        _append_unique(reason_codes, RC_ENFORCE_GEOMETRY_MISMATCH)

    # Readout enforcement
    claim_type = readout_claim_type
    if claim_type is None and readout_semantics:
        rs = _normalize_id(readout_semantics)
        if rs == "causal_interval" and entry.point_only:
            claim_type = "causal_interval"
        if rs in ("forecast_interval",) and claim_type is None:
            claim_type = "causal_interval"

    if claim_type:
        blocked, rc = _readout_claim_blocked(readout_semantics or ("point_only" if entry.point_only else ""), claim_type)
        if blocked and rc:
            _append_unique(reason_codes, rc)
        if entry.point_only and _normalize_id(claim_type) in (
            "causal_interval",
            "significance_test",
            "uncertainty_claim",
        ):
            _append_unique(reason_codes, RC_ENFORCE_POINT_ONLY)

    if combination_id == "DCM-007" or _normalize_id(readout_semantics or "") == "pooled_multicell_causal":
        _append_unique(reason_codes, RC_ENFORCE_POOLED_MULTICELL_BLOCKED)

    if entry.per_cell_only and design_contract is not None:
        ok, mc_reasons = _multicell_metadata_ok(design_contract)
        if not ok:
            for r in mc_reasons:
                _append_unique(reason_codes, r)

    if entry.enforcement_reason and not entry.research_permitted:
        _append_unique(reason_codes, entry.enforcement_reason)
    elif entry.research_permitted:
        _append_unique(reason_codes, entry.enforcement_reason)
        warnings.append("Combination characterized for research/diagnostic use only.")

    blocking_codes = {
        RC_ENFORCE_GEOMETRY_MISMATCH,
        RC_ENFORCE_POOLED_MULTICELL_BLOCKED,
        RC_ENFORCE_ADAPTER_REQUIRED,
        RC_ENFORCE_BRIDGE_REQUIRED,
        RC_ENFORCE_COMBINATION_BLOCKED,
        RC_ENFORCE_READOUT_MISMATCH,
        RC_ENFORCE_NULL_MONITOR_ONLY,
        RC_ENFORCE_FORECAST_NOT_CAUSAL,
    }
    if claim_type and entry.point_only and _normalize_id(claim_type) in (
        "causal_interval",
        "significance_test",
        "uncertainty_claim",
    ):
        blocking_codes.add(RC_ENFORCE_POINT_ONLY)

    if reason_codes and any(r in blocking_codes for r in reason_codes):
        status = GUARDRAIL_BLOCK
        permitted = []
    elif entry.research_permitted:
        status = GUARDRAIL_WARN
    else:
        status = GUARDRAIL_BLOCK
        permitted = []

    if status == GUARDRAIL_WARN and not entry.downstream_permitted:
        warnings.append("Downstream authorization remains blocked.")

    return DesignCombinationGuardrailResult(
        status=status,
        combination_id=combination_id,
        combination_status=combination_status,
        reason_codes=reason_codes,
        warnings=warnings,
        blocked_roles=blocked_roles,
        design_id=resolved_design,
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=resolved_geometry,
        readout_semantics=readout_semantics,
        permitted_research_scopes=permitted,
    )
