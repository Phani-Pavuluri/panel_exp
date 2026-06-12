"""Tests for DESIGN-CONTRACT-GOLDEN-FIXTURES-001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.design.assign import CompleteRandomization
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import build_and_validate_tier1_contract
from panel_exp.validation.design_contract_validator_001 import (
    CONTRACT_BLOCKED,
    CONTRACT_UNKNOWN,
    CONTRACT_VALID,
    CONTRACT_VALID_WITH_WARNINGS,
    RC_EMPTY_FORBIDDEN_CLAIMS,
    RC_LEGACY_UNKNOWN,
    RC_MISSING_GEOMETRY_ID,
    RC_MISSING_SHARED_CONTROL_POLICY,
    RC_MISSING_STRATUM_IDS,
    RC_DOWNSTREAM_AUTH_VIOLATION,
    validate_design_contract,
    validate_design_evidence_contract,
)
from tests.design_registry_helpers import make_geo_panel

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas" / "design_contract_golden_001"

REQUIRED_CONTRACT_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "artifact_type",
        "design_contract_status",
        "design_identity",
        "geometry",
        "assignment",
        "units",
        "time_windows",
        "multi_cell",
        "concurrency",
        "governance",
        "compatibility",
        "provenance",
    }
)

POSITIVE_FIXTURES = [
    "tier1_complete_randomization_contract.json",
    "tier1_balanced_randomization_contract.json",
    "tier1_stratified_contract.json",
    "tier1_rerandomization_contract.json",
]

NEGATIVE_CONTRACT_FIXTURES = [
    "negative_downstream_authorized_contract.json",
    "negative_missing_geometry_contract.json",
    "negative_empty_forbidden_claims_contract.json",
]

ALL_FIXTURE_FILES = POSITIVE_FIXTURES + [
    "tier1_multicell_contract_blocked.json",
    "legacy_design_evidence_without_contract.json",
] + NEGATIVE_CONTRACT_FIXTURES


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text())


def _contract_from_fixture(name: str) -> dict[str, Any]:
    payload = _load_fixture(name)
    return payload["design_contract"]


def _assert_conservative_governance(contract: dict[str, Any]) -> None:
    governance = contract["governance"]
    forbidden = governance["forbidden_downstream_claims"]
    assert isinstance(forbidden, list)
    assert len(forbidden) > 0
    assert governance["downstream_authorization_status"] in ("blocked", "not_authorized")
    assert governance.get("trust_report_eligible") is not True
    assert governance.get("calibration_signal_eligible") is not True
    assert governance.get("mmm_ready") is not True
    assert governance.get("llm_authorized") is not True
    assert governance.get("production_ready") is not True
    compatibility = contract.get("compatibility", {})
    assert compatibility.get("trust_report_eligible") is not True
    assert compatibility.get("calibration_signal_eligible") is not True
    assert compatibility.get("mmm_eligible") is not True
    assert compatibility.get("llm_authorized") is not True


@pytest.mark.parametrize("fixture_name", ALL_FIXTURE_FILES)
def test_golden_fixtures_load_as_json(fixture_name: str):
    payload = _load_fixture(fixture_name)
    assert isinstance(payload, dict)


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES)
def test_positive_tier1_fixtures_validate(fixture_name: str):
    contract = _contract_from_fixture(fixture_name)
    result = validate_design_contract(contract)
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)
    assert result.contract_complete_allowed is False


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES + ["tier1_multicell_contract_blocked.json"])
def test_fixture_status_is_validator_derived(fixture_name: str):
    payload = _load_fixture(fixture_name)
    contract = payload["design_contract"]
    summary = payload.get("contract_validation")
    if summary is not None:
        result = validate_design_contract(contract)
        assert contract["design_contract_status"] == result.status
        assert summary["status"] == result.status
        assert summary["contract_complete_allowed"] is False


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES)
def test_positive_fixtures_no_downstream_authorization(fixture_name: str):
    _assert_conservative_governance(_contract_from_fixture(fixture_name))


def test_stratified_fixture_has_stratum_metadata():
    contract = _contract_from_fixture("tier1_stratified_contract.json")
    structure = contract.get("structure", {})
    assert structure.get("stratum_ids")
    assert structure.get("unit_to_stratum_map")
    result = validate_design_contract(contract)
    assert RC_MISSING_STRATUM_IDS not in result.reason_codes


def test_rerandomization_fixture_preserves_wrapper_identity():
    identity = _contract_from_fixture("tier1_rerandomization_contract.json")["design_identity"]
    assert identity.get("wrapper_identity") == "Rerandomization"
    assert identity.get("design_method_class") == "CompleteRandomization"


def test_multicell_blocked_fixture_surfaces_reason_codes():
    payload = _load_fixture("tier1_multicell_contract_blocked.json")
    contract = payload["design_contract"]
    summary = payload["contract_validation"]
    assert contract["design_contract_status"] == CONTRACT_BLOCKED
    assert summary["status"] == CONTRACT_BLOCKED
    assert RC_MISSING_SHARED_CONTROL_POLICY in summary["reason_codes"]
    assert summary["contract_complete_allowed"] is False


def test_legacy_fixture_without_design_contract_returns_unknown():
    evidence = _load_fixture("legacy_design_evidence_without_contract.json")
    assert "design_contract" not in evidence
    result = validate_design_evidence_contract(evidence)
    assert result.status == CONTRACT_UNKNOWN
    assert RC_LEGACY_UNKNOWN in result.reason_codes


def test_negative_downstream_authorized_fixture_blocks():
    contract = _contract_from_fixture("negative_downstream_authorized_contract.json")
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_DOWNSTREAM_AUTH_VIOLATION in result.reason_codes


def test_negative_missing_geometry_fixture_blocks():
    contract = _contract_from_fixture("negative_missing_geometry_contract.json")
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_GEOMETRY_ID in result.reason_codes


def test_negative_empty_forbidden_claims_fixture_blocks():
    contract = _contract_from_fixture("negative_empty_forbidden_claims_contract.json")
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_EMPTY_FORBIDDEN_CLAIMS in result.reason_codes


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES + ["tier1_multicell_contract_blocked.json"])
def test_fixture_required_top_level_keys_exist(fixture_name: str):
    contract = _contract_from_fixture(fixture_name)
    missing = REQUIRED_CONTRACT_TOP_LEVEL_KEYS - set(contract.keys())
    assert not missing, f"missing keys: {sorted(missing)}"


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES)
def test_fixture_json_is_canonical_sorted(fixture_name: str):
    raw = (FIXTURE_DIR / fixture_name).read_text()
    payload = json.loads(raw)
    assert raw == json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_runtime_builder_matches_golden_shape_keys():
    panel = make_geo_panel(seed=42, n_units=8, n_times=30)
    spec = spec_from_geo_design(
        "runtime-shape-check",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(start=0, end=18),
        experiment_period=TimePeriod(start=18, end=None),
        design_method="completerandomization",
        random_state=42,
    )
    assignment = {"control": ["u0", "u1", "u2", "u3"], "test_0": ["u4", "u5", "u6", "u7"]}
    contract, summary = build_and_validate_tier1_contract(
        spec=spec,
        assignment=assignment,
        registry_key="completerandomization",
        base_randomizer_cls=CompleteRandomization,
        n_test_grps=1,
        treatment_probability=0.5,
        wide_data=panel.wide_data,
        created_at="2026-06-10T12:00:00+00:00",
        spec_hash="runtime-shape-check",
        assignment_hash_value="runtime-shape-check",
        package_version="0.2.1",
    )
    golden = _contract_from_fixture("tier1_complete_randomization_contract.json")
    assert REQUIRED_CONTRACT_TOP_LEVEL_KEYS <= set(contract.keys())
    assert contract["design_contract_status"] == summary["status"]
    assert summary["contract_complete_allowed"] is False
    _assert_conservative_governance(contract)
    assert contract["geometry"]["geometry_id"] == golden["geometry"]["geometry_id"]
    assert contract["governance"]["downstream_authorization_status"] == golden["governance"][
        "downstream_authorization_status"
    ]
    assert set(contract["governance"]["forbidden_downstream_claims"]) == set(
        golden["governance"]["forbidden_downstream_claims"]
    )
