"""DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-001 — tier-1 design_contract builder.

Builds conservative ``design_contract`` blocks for geo-run tier-1 designs and
validates via ``design_contract_validator_001``. Does not authorize downstream use.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import numpy as np

from panel_exp.spec import DesignSpec
from panel_exp.validation.design_contract_validator_001 import (
    SCHEMA_NAME_EXPECTED,
    VALIDATOR_VERSION,
    compute_contract_status,
    validate_design_contract,
)

BUILDER_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
ARTIFACT_TYPE = "design_output_contract"

FORBIDDEN_DOWNSTREAM_CLAIMS = [
    "trust_report",
    "calibration_signal",
    "mmm_calibration",
    "llm_product_recommendation",
    "production_experiment_recommendation",
]

_REGISTRY_TIER1_META: dict[str, tuple[str, str, str]] = {
    "greedy_match_markets": ("DES-001", "matching_assignment", "greedy_match_markets"),
    "completerandomization": ("DES-002", "standard_assignment", "complete_randomization"),
    "balancedrandomization": ("DES-003", "standard_assignment", "balanced_randomization"),
    "stratifiedrandomization": ("DES-004", "stratified_assignment", "stratified_randomization"),
}

RERANDOMIZATION_WRAPPER = "Rerandomization"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_registry_key(registry_key: str) -> str:
    return registry_key.lower().replace("_", "").replace(" ", "")


def _lookup_tier1_meta(registry_key: str) -> tuple[str, str, str]:
    key = _normalize_registry_key(registry_key)
    if key in _REGISTRY_TIER1_META:
        return _REGISTRY_TIER1_META[key]
    return ("DES-UNKNOWN", "standard_assignment", registry_key)


def _assignment_lists(assignment: Mapping[str, Any]) -> dict[str, list[str]]:
    return {k: [str(u) for u in v] for k, v in assignment.items()}


def _treated_units(assignment: Mapping[str, list[str]]) -> list[str]:
    treated: list[str] = []
    for key, units in assignment.items():
        if key.startswith("test_"):
            treated.extend(units)
    return sorted(set(treated))


def _cell_ids(assignment: Mapping[str, list[str]]) -> list[str]:
    return sorted(k for k in assignment if k.startswith("test_"))


def _derive_stratified_structure(
    wide_data: Any,
    *,
    treatment_probability: float,
    n_test_grps: int,
    n_percentiles: int,
    control_whitelist: list | None,
    test_whitelist: list | None,
    control_blacklist: list | None,
    test_blacklist: list | None,
    control_test_blacklist: list | None,
) -> dict[str, Any]:
    from panel_exp.design.constraints import prepare_constraint_context

    ctx = prepare_constraint_context(
        wide_data,
        treatment_probability,
        n_test_grps,
        control_whitelist,
        test_whitelist,
        control_blacklist,
        test_blacklist,
        control_test_blacklist,
    )
    units_for_strata = list(ctx.free_units) or list(ctx.all_units)
    if not units_for_strata:
        return {"stratum_ids": [], "unit_to_stratum_map": {}}
    covariate_values = wide_data.loc[units_for_strata].mean(axis=1)
    percentiles = np.linspace(0, 100, n_percentiles + 1)
    stratum_labels = np.percentile(covariate_values.values, percentiles)
    strata = np.digitize(covariate_values.values, bins=stratum_labels, right=True)
    unit_to_stratum = {str(u): int(s) for u, s in zip(covariate_values.index, strata)}
    stratum_ids = sorted({str(s) for s in unit_to_stratum.values()})
    return {
        "stratum_ids": stratum_ids,
        "unit_to_stratum_map": unit_to_stratum,
        "requires_strata": True,
    }


def _units_block(
    wide_data: Any | None,
    *,
    treatment_probability: float,
    n_test_grps: int,
    control_whitelist: list | None,
    test_whitelist: list | None,
    control_blacklist: list | None,
    test_blacklist: list | None,
    control_test_blacklist: list | None,
    assignment: Mapping[str, list[str]],
) -> dict[str, Any]:
    if wide_data is None:
        all_units = sorted(
            {u for units in assignment.values() for u in units}
        )
        return {
            "all_units": all_units,
            "eligible_units": all_units,
            "excluded_units": [],
            "donor_pool_units": list(assignment.get("control", [])),
        }
    from panel_exp.design.constraints import prepare_constraint_context

    ctx = prepare_constraint_context(
        wide_data,
        treatment_probability,
        n_test_grps,
        control_whitelist,
        test_whitelist,
        control_blacklist,
        test_blacklist,
        control_test_blacklist,
    )
    eligible = sorted(set(ctx.pinned_control) | set(ctx.free_units))
    for units in ctx.pinned_test.values():
        eligible.extend(units)
    eligible = sorted(set(eligible))
    return {
        "all_units": list(ctx.all_units),
        "eligible_units": eligible,
        "excluded_units": sorted(ctx.excluded),
        "donor_pool_units": list(assignment.get("control", [])),
    }


def build_tier1_design_contract(
    *,
    spec: DesignSpec,
    assignment: Mapping[str, Any],
    registry_key: str,
    base_randomizer_cls: type,
    n_test_grps: int,
    treatment_probability: float,
    is_rerandomization_wrapped: bool = True,
    validation_summary: Mapping[str, Any] | None = None,
    wide_data: Any | None = None,
    design_kwargs: Mapping[str, Any] | None = None,
    spec_hash: str | None = None,
    assignment_hash_value: str | None = None,
    package_version: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a candidate tier-1 ``design_contract`` dict (pre-validator status)."""
    assignment_map = _assignment_lists(assignment)
    des_id, design_family, design_name = _lookup_tier1_meta(registry_key)
    base_cls_name = base_randomizer_cls.__name__
    is_multi_cell = n_test_grps > 1
    geometry_id = "multi_cell_per_cell" if is_multi_cell else "unit_panel_single_cell"
    concurrency_value = "restricted" if is_multi_cell else "not_evaluated"
    kwargs = dict(design_kwargs or {})

    identity: dict[str, Any] = {
        "design_inventory_id": des_id,
        "design_name": design_name,
        "design_family": design_family,
        "design_method_class": base_cls_name,
        "registry_key": registry_key,
        "random_seed": spec.random_state,
    }
    if is_rerandomization_wrapped:
        identity["wrapper_identity"] = RERANDOMIZATION_WRAPPER
        identity["is_rerandomization_wrapped"] = True

    structure: dict[str, Any] | None = None
    if design_family == "stratified_assignment" and wide_data is not None:
        n_percentiles = int(kwargs.get("n_percentiles", 10))
        structure = _derive_stratified_structure(
            wide_data,
            treatment_probability=treatment_probability,
            n_test_grps=n_test_grps,
            n_percentiles=n_percentiles,
            control_whitelist=list(spec.control_whitelist),
            test_whitelist=list(spec.test_whitelist),
            control_blacklist=list(spec.control_blacklist),
            test_blacklist=list(spec.test_blacklist),
            control_test_blacklist=list(spec.control_test_blacklist),
        )

    multi_cell: dict[str, Any] = {
        "is_multi_cell": is_multi_cell,
        "pooled_claims_allowed": False,
        "portfolio_claims_allowed": False,
    }
    if is_multi_cell:
        cell_ids = _cell_ids(assignment_map)
        multicell_meta = kwargs.get("last_multicell_metadata") or {}
        multi_cell.update(
            {
                "cell_ids": cell_ids,
                "shared_control_mode": "shared",
                "shared_control_policy": multicell_meta.get(
                    "shared_control_policy", "shared_single_control_arm"
                ),
                "control_reuse_policy": multicell_meta.get(
                    "control_reuse_policy", "shared_donor_pool_across_cells"
                ),
                "requested_total_treatment_share": multicell_meta.get(
                    "requested_total_treatment_share", treatment_probability
                ),
                "realized_total_treatment_share": multicell_meta.get(
                    "realized_total_treatment_share"
                ),
                "requested_per_cell_shares": multicell_meta.get("requested_per_cell_shares"),
                "realized_per_cell_shares": multicell_meta.get("realized_per_cell_shares"),
                "per_cell_unit_counts": multicell_meta.get("per_cell_unit_counts"),
                "concurrency_compatibility": multicell_meta.get(
                    "concurrency_compatibility", "restricted"
                ),
            }
        )

    contract: dict[str, Any] = {
        "schema_name": SCHEMA_NAME_EXPECTED,
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "design_contract_status": "contract_incomplete",
        "producer": "geo_runner",
        "created_at": created_at or _utc_now_iso(),
        "design_identity": identity,
        "geometry": {
            "geometry_id": geometry_id,
            "target_population_status": "full_panel",
            "bridge_status": "direct",
        },
        "assignment": {
            "assignment_map": assignment_map,
            "treated_units": _treated_units(assignment_map),
            "control_units": list(assignment_map.get("control", [])),
            "treatment_labels": [k for k in assignment_map if k.startswith("test_")],
            "control_labels": ["control"],
            "assignment_probability": treatment_probability,
        },
        "units": _units_block(
            wide_data,
            treatment_probability=treatment_probability,
            n_test_grps=n_test_grps,
            control_whitelist=list(spec.control_whitelist),
            test_whitelist=list(spec.test_whitelist),
            control_blacklist=list(spec.control_blacklist),
            test_blacklist=list(spec.test_blacklist),
            control_test_blacklist=list(spec.control_test_blacklist),
            assignment=assignment_map,
        ),
        "time_windows": {
            "pre_period_start": spec.pre_period.start,
            "pre_period_end": spec.pre_period.end,
            "test_period_start": spec.experiment_period.start,
            "test_period_end": spec.experiment_period.end,
        },
        "outcomes": {
            "primary_outcome": spec.outcome_column,
        },
        "multi_cell": multi_cell,
        "concurrency": {
            "concurrent_multi_experiment_compatibility": concurrency_value,
        },
        "governance": {
            "forbidden_downstream_claims": list(FORBIDDEN_DOWNSTREAM_CLAIMS),
            "downstream_authorization_status": "blocked",
            "statistical_validation_status": "protocol_defined_not_executed",
            "guardrail_status": "REQUIRES_STATISTICAL_VALIDATION",
            "suitability_status": "contract_blocked",
            "trust_report_eligible": False,
            "calibration_signal_eligible": False,
            "mmm_ready": False,
            "llm_authorized": False,
            "production_ready": False,
        },
        "compatibility": {
            "requires_statistical_validation": True,
            "requires_adapter": False,
            "trust_report_eligible": False,
            "calibration_signal_eligible": False,
            "mmm_eligible": False,
            "llm_authorized": False,
            "advisory_only": True,
        },
        "diagnostics": {
            "validation_summary_present": bool(validation_summary),
            "diagnostic_completeness_status": "partial",
        },
        "provenance": {
            "producer_module": "panel_exp.design.geo_runner",
            "producer_function": "run_geo_experiment_design",
            "builder_version": BUILDER_VERSION,
            "spec_hash": spec_hash,
            "assignment_hash": assignment_hash_value,
            "run_id": spec.experiment_id,
            "package_version": package_version,
        },
    }
    if structure is not None:
        contract["structure"] = structure
    return contract


def contract_validation_summary_from_result(result: Any) -> dict[str, Any]:
    return {
        "status": result.status,
        "severity": result.severity,
        "reason_codes": list(result.reason_codes),
        "contract_complete_allowed": result.contract_complete_allowed,
        "blocked_downstream_roles": list(result.blocked_downstream_roles),
        "validator_version": result.validator_version,
    }


def build_and_validate_tier1_contract(
    *,
    spec: DesignSpec,
    assignment: Mapping[str, Any],
    registry_key: str,
    base_randomizer_cls: type,
    n_test_grps: int,
    treatment_probability: float,
    is_rerandomization_wrapped: bool = True,
    validation_summary: Mapping[str, Any] | None = None,
    wide_data: Any | None = None,
    design_kwargs: Mapping[str, Any] | None = None,
    spec_hash: str | None = None,
    assignment_hash_value: str | None = None,
    package_version: str | None = None,
    created_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build tier-1 contract, validate, and return (contract, compact summary)."""
    contract = build_tier1_design_contract(
        spec=spec,
        assignment=assignment,
        registry_key=registry_key,
        base_randomizer_cls=base_randomizer_cls,
        n_test_grps=n_test_grps,
        treatment_probability=treatment_probability,
        is_rerandomization_wrapped=is_rerandomization_wrapped,
        validation_summary=validation_summary,
        wide_data=wide_data,
        design_kwargs=design_kwargs,
        spec_hash=spec_hash,
        assignment_hash_value=assignment_hash_value,
        package_version=package_version,
        created_at=created_at,
    )
    result = validate_design_contract(contract)
    status = compute_contract_status(result)
    finalized = dict(contract)
    finalized["design_contract_status"] = status
    summary = contract_validation_summary_from_result(result)
    summary["validator_version"] = VALIDATOR_VERSION
    return finalized, summary
