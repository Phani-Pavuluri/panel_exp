"""Tests for DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-001."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from panel_exp.validation.design_contract_validator_001 import (
    CONTRACT_BLOCKED,
    CONTRACT_UNKNOWN,
    CONTRACT_VALID,
    CONTRACT_VALID_WITH_WARNINGS,
    RC_EMPTY_FORBIDDEN_CLAIMS,
    RC_FALSE_COMPLETE_CLAIM,
    RC_INVALID_ENUM,
    RC_LEGACY_UNKNOWN,
    RC_MISSING_CELL_IDS,
    RC_MISSING_CONCURRENCY,
    RC_MISSING_DESIGN_CONTRACT,
    RC_MISSING_FORBIDDEN_CLAIMS,
    RC_MISSING_GEOMETRY_ID,
    RC_MISSING_RERANDOMIZATION_IDENTITY,
    RC_MISSING_SHARED_CONTROL_POLICY,
    RC_MISSING_STRATUM_IDS,
    RC_MISSING_SUPERGEO_MAP,
    RC_MISSING_TRIM_METADATA,
    RC_POWER_MDE_OVERCLAIM,
    RC_DOWNSTREAM_AUTH_VIOLATION,
    DesignContractValidationResult,
    compute_contract_status,
    validate_design_contract,
    validate_design_evidence_contract,
)


def _minimal_valid_contract(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_name": "DESIGN-CONTRACT-SCHEMA-001",
        "schema_version": "1.0.0",
        "artifact_type": "design_output_contract",
        "design_contract_status": "contract_incomplete",
        "producer": "geo_runner",
        "created_at": "2026-06-10T12:00:00Z",
        "design_identity": {
            "design_inventory_id": "DES-002",
            "design_name": "complete_randomization",
            "design_family": "standard_assignment",
            "design_method_class": "CompleteRandomization",
            "registry_key": "complete_randomization",
        },
        "geometry": {
            "geometry_id": "unit_panel_single_cell",
            "target_population_status": "full_panel",
        },
        "multi_cell": {"is_multi_cell": False},
        "concurrency": {
            "concurrent_multi_experiment_compatibility": "not_evaluated",
        },
        "governance": {
            "forbidden_downstream_claims": [
                "trust_report",
                "calibration_signal",
                "mmm_calibration",
                "llm_product_recommendation",
                "production_experiment_recommendation",
            ],
            "guardrail_status": "BLOCK",
            "suitability_status": "contract_blocked",
            "statistical_validation_status": "protocol_defined_not_executed",
            "downstream_authorization_status": "blocked",
        },
        "provenance": {
            "producer_module": "panel_exp.design.geo_runner",
            "producer_function": "run_geo_experiment_design",
            "spec_hash": "abc123",
            "run_id": "test-exp-001",
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            merged = copy.deepcopy(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = copy.deepcopy(value)
    return base


def test_legacy_evidence_without_design_contract_returns_unknown():
    result = validate_design_evidence_contract(
        {"design_method": "balanced_randomization", "assignment": {"control": ["u0"]}}
    )
    assert result.status == CONTRACT_UNKNOWN
    assert RC_LEGACY_UNKNOWN in result.reason_codes
    assert result.contract_complete_allowed is False


def test_missing_design_contract_mapping_returns_unknown():
    result = validate_design_contract(None)
    assert result.status == CONTRACT_UNKNOWN
    assert RC_MISSING_DESIGN_CONTRACT in result.reason_codes


def test_missing_geometry_id_blocks():
    contract = _minimal_valid_contract()
    contract["geometry"] = {}
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_GEOMETRY_ID in result.reason_codes


def test_missing_forbidden_downstream_claims_blocks():
    contract = _minimal_valid_contract()
    del contract["governance"]["forbidden_downstream_claims"]
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_FORBIDDEN_CLAIMS in result.reason_codes


def test_empty_forbidden_downstream_claims_blocks():
    contract = _minimal_valid_contract(
        governance={"forbidden_downstream_claims": []},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_EMPTY_FORBIDDEN_CLAIMS in result.reason_codes


def test_missing_concurrency_blocks():
    contract = _minimal_valid_contract()
    del contract["concurrency"]
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_CONCURRENCY in result.reason_codes


def test_invalid_enum_blocks():
    contract = _minimal_valid_contract(
        geometry={"geometry_id": "not_a_real_geometry"},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_INVALID_ENUM in result.reason_codes


def test_downstream_authorization_violation_blocks():
    contract = _minimal_valid_contract(
        governance={"downstream_authorization_status": "authorized"},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_DOWNSTREAM_AUTH_VIOLATION in result.reason_codes


def test_false_contract_complete_claim_blocks():
    contract = _minimal_valid_contract(design_contract_status="contract_complete")
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_FALSE_COMPLETE_CLAIM in result.reason_codes
    assert result.contract_complete_allowed is False


def test_minimal_valid_contract_passes_conservatively():
    result = validate_design_contract(_minimal_valid_contract())
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)
    assert result.contract_complete_allowed is False
    assert result.severity in ("PASS", "WARN")


def test_stratified_missing_stratum_metadata_blocks():
    contract = _minimal_valid_contract(
        design_identity={"design_family": "stratified_assignment"},
        structure={},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_STRATUM_IDS in result.reason_codes


def test_multicell_missing_cell_ids_blocks():
    contract = _minimal_valid_contract(
        geometry={"geometry_id": "multi_cell_per_cell"},
        multi_cell={"is_multi_cell": True},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_CELL_IDS in result.reason_codes


def test_multicell_missing_shared_control_policy_blocks():
    contract = _minimal_valid_contract(
        geometry={"geometry_id": "multi_cell_per_cell"},
        multi_cell={
            "is_multi_cell": True,
            "cell_ids": ["test_0", "test_1"],
        },
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_SHARED_CONTROL_POLICY in result.reason_codes


def test_rerandomization_missing_wrapper_identity_blocks():
    contract = _minimal_valid_contract(
        design_identity={
            "wrapper_identity": "Rerandomization",
            "design_method_class": None,
        },
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_RERANDOMIZATION_IDENTITY in result.reason_codes


def test_supergeo_missing_source_map_blocks():
    contract = _minimal_valid_contract(
        geometry={"geometry_id": "supergeo"},
        supergeo={"is_supergeo": True},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_SUPERGEO_MAP in result.reason_codes


def test_trim_metadata_missing_blocks():
    contract = _minimal_valid_contract(
        geometry={"geometry_id": "trimmed_geometry"},
        trim_thin={"is_trimmed": True},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_TRIM_METADATA in result.reason_codes


def test_power_mde_causal_overclaim_blocks():
    contract = _minimal_valid_contract(
        power_mde={"causal_readout_authorized": True, "planning_only_flag": True},
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_POWER_MDE_OVERCLAIM in result.reason_codes


def test_to_dict_is_json_serializable():
    result = validate_design_contract(_minimal_valid_contract())
    payload = result.to_dict()
    json.dumps(payload)
    assert payload["validator_version"] == "1.0.0"


def test_validate_design_evidence_contract_reads_nested_block():
    contract = _minimal_valid_contract()
    evidence = {"design_method": "complete_randomization", "design_contract": contract}
    result = validate_design_evidence_contract(evidence)
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)
    assert result.schema_name == "DESIGN-CONTRACT-SCHEMA-001"


def test_validator_does_not_mutate_input():
    contract = _minimal_valid_contract()
    evidence = {"design_contract": contract}
    contract_before = copy.deepcopy(contract)
    evidence_before = copy.deepcopy(evidence)
    validate_design_contract(contract)
    validate_design_evidence_contract(evidence)
    assert contract == contract_before
    assert evidence == evidence_before


def test_compute_contract_status_aggregates_blocked():
    result = DesignContractValidationResult(
        field_results={"geometry.geometry_id": "field_missing_block"},
        missing_required_fields=["geometry.geometry_id"],
    )
    assert compute_contract_status(result) == CONTRACT_BLOCKED


@pytest.mark.parametrize(
    "governance_key",
    [
        "trust_report_eligible",
        "calibration_signal_eligible",
        "mmm_ready",
        "llm_authorized",
        "production_ready",
    ],
)
def test_no_overclaim_governance_flags_block(governance_key: str):
    contract = _minimal_valid_contract(governance={governance_key: True})
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_DOWNSTREAM_AUTH_VIOLATION in result.reason_codes
