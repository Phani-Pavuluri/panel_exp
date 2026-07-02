"""Tests for ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS."""

from __future__ import annotations

from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    EXECUTOR_NOT_EVALUATED,
    KNOWN_INSTRUMENT_IDS,
    build_governed_executor_result,
    evaluate_governed_executor_availability,
    get_governed_executor_registry,
    lookup_governed_executor,
)


def _context() -> dict:
    return {
        "assignment_artifact_id": "assignment_001",
        "execution_data_contract": {
            "required_columns": ["geo_id", "week", "sales", "treated"],
            "available_columns": ["geo_id", "week", "sales", "treated"],
        },
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "bootstrap"},
    }


def _instrument(instrument_id: str, role: str = "PRIMARY_EXECUTION_CANDIDATE") -> dict:
    return {
        "instrument_id": instrument_id,
        "execution_role": role,
        "governance_status": "GOVERNED",
        "assignment_artifact_id": "assignment_001",
        "estimand_type": "STANDARD_INCREMENTALITY",
        "metric_name": "sales",
        "uncertainty_semantics": "bootstrap",
    }


def test_registry_contains_known_instrument_ids() -> None:
    registry = get_governed_executor_registry()
    for instrument_id in KNOWN_INSTRUMENT_IDS:
        assert instrument_id in registry.specs


def test_lookup_known_instrument_deterministic() -> None:
    first = lookup_governed_executor("DID_BOOTSTRAP")
    second = lookup_governed_executor("DID_BOOTSTRAP")
    assert first.adapter_name == second.adapter_name
    assert first.adapter_version == second.adapter_version


def test_lookup_unknown_instrument_not_evaluated() -> None:
    lookup = lookup_governed_executor("UNKNOWN_INSTRUMENT_ABC")
    assert lookup.availability_status == EXECUTOR_NOT_EVALUATED
    assert lookup.executor_available is False


def test_default_registry_not_marked_executable() -> None:
    registry = get_governed_executor_registry()
    assert all(not spec.supports_execution for spec in registry.specs.values())


def test_did_bootstrap_adapter_not_executable_by_default() -> None:
    lookup = evaluate_governed_executor_availability(_instrument("DID_BOOTSTRAP"), _context())
    assert lookup.availability_status in (EXECUTOR_AVAILABLE_FOR_DRY_RUN, "EXECUTOR_NOT_IMPLEMENTED")
    assert lookup.supports_execution is False


def test_scm_placebo_diagnostic_not_primary_execution() -> None:
    lookup = evaluate_governed_executor_availability(
        _instrument("SCM_PLACEBO", role="PRIMARY_EXECUTION_CANDIDATE"),
        _context(),
    )
    assert lookup.executor_available is False or lookup.supports_execution is False


def test_blocked_role_remains_blocked() -> None:
    lookup = evaluate_governed_executor_availability(
        _instrument("DID_BOOTSTRAP", role="BLOCKED_EXECUTION_CANDIDATE"),
        _context(),
    )
    assert lookup.availability_status == "EXECUTOR_BLOCKED_BY_INSTRUMENT_STATUS"


def test_dry_run_envelope_not_completed() -> None:
    lookup, request, result = build_governed_executor_result(_instrument("DID_BOOTSTRAP"), _context())
    assert request.dry_run is True
    assert result.completed is False
    assert result.effect_estimate_report_status == "NOT_COMPUTED"
    assert result.uncertainty_report_status == "NOT_COMPUTED"
    assert lookup.supports_execution is False
