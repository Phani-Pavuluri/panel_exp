"""Tests for TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_kfold_leakage_diagnostic_contract_001 import (
    ALLOWED_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    DIAGNOSTIC_STATUSES,
    FAILURE_CODES,
    FOLD_OVERLAP_RULES,
    FUTURE_RUNTIME_TESTS,
    LEAKAGE_TYPES,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    TEMPORAL_LEAKAGE_RULES,
    UNSUPPORTED_GEOMETRY_RULES,
    _AUTH_FLAGS,
    _VERDICT,
    build_tbrridge_kfold_leakage_diagnostic_contract,
    build_scenarios,
    evaluate_kfold_leakage_diagnostic,
    get_tbrridge_kfold_leakage_diagnostic_contract_metadata,
    list_diagnostic_statuses,
    list_leakage_types,
    list_future_runtime_tests,
    run_validation,
    validate_tbrridge_kfold_leakage_diagnostic_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_REPORT.md"


def test_contract_metadata_exists() -> None:
    meta = get_tbrridge_kfold_leakage_diagnostic_contract_metadata()
    assert meta["artifact_id"] == "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001"
    assert meta["kfold_leakage_diagnostic_contract_defined"] is True


def test_diagnostic_statuses_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.diagnostic_statuses == DIAGNOSTIC_STATUSES
    assert list_diagnostic_statuses() == DIAGNOSTIC_STATUSES
    assert "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE" in contract.diagnostic_statuses


def test_leakage_type_taxonomy_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.leakage_types == LEAKAGE_TYPES
    assert list_leakage_types() == LEAKAGE_TYPES
    assert "MULTI_TREATED_GEOMETRY_UNSUPPORTED" in contract.leakage_types


def test_required_evidence_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert "fold_assignment_manifest" in contract.required_evidence
    assert contract.required_evidence == REQUIRED_EVIDENCE


def test_unsupported_geometry_rules_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.unsupported_geometry_rules == UNSUPPORTED_GEOMETRY_RULES
    assert "kfold_multi_treated_unsupported_run001" in " ".join(contract.unsupported_geometry_rules)


def test_temporal_leakage_rules_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.temporal_leakage_rules == TEMPORAL_LEAKAGE_RULES
    assert any("pre_post" in r for r in contract.temporal_leakage_rules)


def test_fold_overlap_rules_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.fold_overlap_rules == FOLD_OVERLAP_RULES


def test_allowed_prohibited_surfaces_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "KFOLD_UNCERTAINTY_CLAIM" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.failure_packet_semantics_defined
    assert contract.failure_codes == FAILURE_CODES
    result = evaluate_kfold_leakage_diagnostic(evidence={})
    packet = result.to_failure_packet()
    assert packet is not None
    assert "failure_code" in packet


def test_future_runtime_tests_documented() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert contract.future_runtime_tests_documented
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "blocks_kfold_uncertainty_ci_significance_coverage_surfaces" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_flags_false() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_tbrridge_kfold_leakage_diagnostic_contract_metadata()
    assert meta["kfold_inference_implemented"] is False
    assert meta["coverage_computed"] is False


def test_evaluate_blocks_multi_treated_geometry() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_kfold_leakage_diagnostic(evidence=evidence, treated_geometry="multi_treated")
    assert result.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY"
    assert result.failure_code == "MULTI_TREATED_GEOMETRY_UNSUPPORTED"


def test_evaluate_blocks_uncertainty_surface() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_kfold_leakage_diagnostic(
        evidence=evidence,
        requested_surface="CONFIDENCE_INTERVAL_CLAIM",
    )
    assert result.failure_code == "KFOLD_UNCERTAINTY_SURFACE_BLOCKED"


def test_contract_validation_and_scenarios_pass() -> None:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    assert validate_tbrridge_kfold_leakage_diagnostic_contract(contract)["valid"] is True
    failed = [s["scenario_id"] for s in build_scenarios() if not s["passed"]]
    assert failed == []


def test_positive_flags_true() -> None:
    for key, val in CONTRACT_POSITIVE_FLAGS.items():
        assert val is True


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "kfold_multi_treated_unsupported_run001" in text


def test_run_validation_verdict() -> None:
    result = run_validation(write_summary=False)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []
