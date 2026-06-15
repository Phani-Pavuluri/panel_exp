"""Tests for DESIGN-GUARDRAIL-RUNTIME-INTEGRATION-001."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.validation.design_guardrail_runtime_001 import (
    GUARDRAIL_BLOCK,
    GUARDRAIL_UNKNOWN,
    GUARDRAIL_WARN,
    RC_GUARDRAIL_CONTRACT_BLOCKED,
    RC_GUARDRAIL_CONTRACT_COMPLETE_NOT_ALLOWED,
    RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION,
    RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN,
    RC_GUARDRAIL_MISSING_CONTRACT,
    RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION,
    RC_GUARDRAIL_OVERCLAIM_CALIBRATION_SIGNAL,
    RC_GUARDRAIL_OVERCLAIM_LLM,
    RC_GUARDRAIL_OVERCLAIM_MMM,
    RC_GUARDRAIL_OVERCLAIM_PRODUCTION,
    RC_GUARDRAIL_OVERCLAIM_TRUSTREPORT,
    RC_GUARDRAIL_REQUIRES_STATISTICAL_VALIDATION,
    DesignGuardrailRuntimeResult,
    evaluate_contract_validation_summary,
    evaluate_design_contract_guardrails,
    guardrail_result_from_contract_validation,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas" / "design_contract_golden_001"

POSITIVE_FIXTURES = [
    "tier1_complete_randomization_contract.json",
    "tier1_balanced_randomization_contract.json",
    "tier1_stratified_contract.json",
    "tier1_rerandomization_contract.json",
]

NEGATIVE_FIXTURES = [
    "negative_downstream_authorized_contract.json",
    "negative_missing_geometry_contract.json",
    "negative_empty_forbidden_claims_contract.json",
    "tier1_multicell_contract_blocked.json",
]

BLOCKED_ROLES = frozenset(
    {"trust_report", "calibration_signal", "mmm", "llm", "production"}
)


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text())


def _assert_no_downstream_promotion(result: DesignGuardrailRuntimeResult) -> None:
    assert result.suitability_may_proceed is False
    assert result.downstream_may_proceed is False
    assert result.contract_complete_allowed is False
    assert BLOCKED_ROLES.issubset(set(result.blocked_roles))


@pytest.mark.parametrize("fixture_name", POSITIVE_FIXTURES)
def test_positive_golden_fixtures_load_and_evaluate_without_mutation(fixture_name: str) -> None:
    payload = _load_fixture(fixture_name)
    snapshot = copy.deepcopy(payload)
    result = evaluate_design_contract_guardrails(payload)
    assert payload == snapshot
    _assert_no_downstream_promotion(result)
    assert result.status != GUARDRAIL_BLOCK
    assert RC_GUARDRAIL_REQUIRES_STATISTICAL_VALIDATION in result.reason_codes


def test_mechanically_valid_contract_non_block_metadata_downstream_false() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status in {GUARDRAIL_WARN, "PASS"}
    assert result.contract_status == "contract_valid"
    _assert_no_downstream_promotion(result)


def test_blocked_multicell_fixture_returns_block() -> None:
    payload = _load_fixture("tier1_multicell_contract_blocked.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status == GUARDRAIL_BLOCK
    assert result.contract_status == "contract_blocked"
    assert RC_GUARDRAIL_CONTRACT_BLOCKED in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_legacy_fixture_without_contract_returns_block_or_unknown() -> None:
    payload = _load_fixture("legacy_design_evidence_without_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status in {GUARDRAIL_BLOCK, GUARDRAIL_UNKNOWN}
    assert RC_GUARDRAIL_MISSING_CONTRACT in result.reason_codes
    assert RC_GUARDRAIL_LEGACY_CONTRACT_UNKNOWN in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_negative_downstream_authorized_fixture_returns_block() -> None:
    payload = _load_fixture("negative_downstream_authorized_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status == GUARDRAIL_BLOCK
    assert RC_GUARDRAIL_DOWNSTREAM_AUTH_VIOLATION in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_negative_missing_geometry_fixture_returns_block() -> None:
    payload = _load_fixture("negative_missing_geometry_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status == GUARDRAIL_BLOCK
    _assert_no_downstream_promotion(result)


def test_negative_empty_forbidden_claims_fixture_returns_block() -> None:
    payload = _load_fixture("negative_empty_forbidden_claims_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.status == GUARDRAIL_BLOCK
    _assert_no_downstream_promotion(result)


def test_guardrail_consumes_contract_validation_summary_directly() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    summary = payload["contract_validation"]
    contract = payload["design_contract"]
    result = evaluate_contract_validation_summary(summary, contract=contract)
    assert result.source == "contract_validation"
    assert result.status != GUARDRAIL_BLOCK
    _assert_no_downstream_promotion(result)


def test_guardrail_consumes_full_fixture_payload() -> None:
    payload = _load_fixture("tier1_stratified_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    assert result.source == "design_contract"
    assert result.contract_status == "contract_valid"
    _assert_no_downstream_promotion(result)


def test_missing_contract_validation_with_present_contract_revalidates() -> None:
    payload = _load_fixture("negative_missing_geometry_contract.json")
    contract_only = {"design_contract": payload["design_contract"]}
    result = evaluate_design_contract_guardrails(contract_only)
    assert result.status == GUARDRAIL_BLOCK
    assert RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_standalone_contract_without_validation_revalidates() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    contract = payload["design_contract"]
    result = evaluate_design_contract_guardrails(contract)
    assert RC_GUARDRAIL_MISSING_CONTRACT_VALIDATION in result.reason_codes
    assert result.status != GUARDRAIL_BLOCK
    _assert_no_downstream_promotion(result)


@pytest.mark.parametrize(
    ("field_path", "reason_code"),
    [
        ("governance.trust_report_eligible", RC_GUARDRAIL_OVERCLAIM_TRUSTREPORT),
        ("governance.calibration_signal_eligible", RC_GUARDRAIL_OVERCLAIM_CALIBRATION_SIGNAL),
        ("governance.mmm_ready", RC_GUARDRAIL_OVERCLAIM_MMM),
        ("governance.llm_authorized", RC_GUARDRAIL_OVERCLAIM_LLM),
        ("governance.production_ready", RC_GUARDRAIL_OVERCLAIM_PRODUCTION),
    ],
)
def test_no_overclaim_flags_block(field_path: str, reason_code: str) -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    summary = dict(payload["contract_validation"])
    contract = copy.deepcopy(payload["design_contract"])
    parts = field_path.split(".")
    block = contract[parts[0]]
    block[parts[1]] = True
    result = guardrail_result_from_contract_validation(summary, contract=contract)
    assert result.status == GUARDRAIL_BLOCK
    assert reason_code in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_contract_complete_allowed_false_prevents_downstream() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    summary = dict(payload["contract_validation"])
    assert summary["contract_complete_allowed"] is False
    result = guardrail_result_from_contract_validation(
        summary,
        contract=payload["design_contract"],
    )
    assert RC_GUARDRAIL_CONTRACT_COMPLETE_NOT_ALLOWED in result.reason_codes
    _assert_no_downstream_promotion(result)


def test_to_dict_is_json_serializable() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    result = evaluate_design_contract_guardrails(payload)
    serialized = json.dumps(result.to_dict())
    roundtrip = json.loads(serialized)
    assert roundtrip["status"] == result.status
    assert roundtrip["downstream_may_proceed"] is False


def test_input_immutability_on_negative_fixtures() -> None:
    for name in NEGATIVE_FIXTURES:
        payload = _load_fixture(name)
        snapshot = copy.deepcopy(payload)
        evaluate_design_contract_guardrails(payload)
        assert payload == snapshot


def test_nested_design_evidence_shape() -> None:
    payload = _load_fixture("tier1_complete_randomization_contract.json")
    nested = {
        "design": {
            "design_contract": payload["design_contract"],
            "contract_validation": payload["contract_validation"],
        }
    }
    result = evaluate_design_contract_guardrails(nested)
    assert result.status != GUARDRAIL_BLOCK
    _assert_no_downstream_promotion(result)


def test_no_trust_report_calibration_mmm_llm_may_proceed() -> None:
    for fixture_name in POSITIVE_FIXTURES + NEGATIVE_FIXTURES:
        result = evaluate_design_contract_guardrails(_load_fixture(fixture_name))
        assert result.suitability_may_proceed is False
        assert result.downstream_may_proceed is False
        for role in ("trust_report", "calibration_signal", "mmm", "llm", "production"):
            assert role in result.blocked_roles
