"""Tests for GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.geo_kpi_spend_data_contract_and_profiler_spec_001 import (
    ACCEPTED_INPUT_MODES,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_FIELDS,
    REQUIRED_PROFILER_REPORTS,
    SCENARIO_TESTS,
    SUPPORTED_GEO_UNIT_TYPES,
    SUPPORTED_TIME_GRAINS,
    ZERO_MISSING_RULES,
    _AUTH_FLAGS,
    build_geo_kpi_spend_data_contract_and_profiler_spec,
    build_scenarios,
    run_validation,
    validate_geo_kpi_spend_data_contract_and_profiler_spec,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001_summary.json"
_REPORT = _REPO / "docs/track_d/GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001_REPORT.md"


def test_accepted_input_modes() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    assert spec.accepted_input_modes == ACCEPTED_INPUT_MODES
    assert "full_panel_mode" in spec.accepted_input_modes
    assert "ballpark_mode_provisional_only" in spec.accepted_input_modes


def test_required_fields_and_grains() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    assert spec.required_fields == REQUIRED_FIELDS
    assert spec.supported_time_grains == SUPPORTED_TIME_GRAINS
    assert spec.supported_geo_unit_types == SUPPORTED_GEO_UNIT_TYPES


def test_zero_missing_rules() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    assert spec.zero_missing_rules == ZERO_MISSING_RULES
    assert spec.zero_missing_rules["missing_spend_is_not_zero_spend"]


def test_profiler_reports() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    assert spec.required_profiler_reports == REQUIRED_PROFILER_REPORTS
    assert "UnitEligibilityReport" in spec.required_profiler_reports


def test_llm_and_claim_boundaries() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    assert not spec.sample_schema_mode_final_claims_allowed
    assert not spec.ballpark_mode_final_claims_allowed
    assert not spec.profiler_outputs_authorize_design_feasibility
    assert not spec.profiler_outputs_authorize_p_values_or_cis
    assert spec.llm_answerability_boundaries_defined


def test_scenario_tests_listed() -> None:
    assert len(SCENARIO_TESTS) >= 20
    assert "missing_spend_not_treated_as_zero" in SCENARIO_TESTS
    assert "llm_cannot_claim_final_feasibility_from_ballpark_mode" in SCENARIO_TESTS


def test_all_authorization_flags_false() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    for flag, expected in _AUTH_FLAGS.items():
        assert spec.authorization_flags[flag] is expected


def test_validate_spec() -> None:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    result = validate_geo_kpi_spend_data_contract_and_profiler_spec(spec)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
    assert data["failed_scenarios"] == []
    assert data["sample_schema_mode_final_claims_allowed"] is False
    assert data["ballpark_mode_final_claims_allowed"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == "geo_kpi_spend_data_contract_profiler_spec_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "missing spend" in text.lower() or "missing_spend" in text.lower()
    assert "ballpark" in text.lower()
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
    assert "geo_unit_id" in text.lower() or "geo unit" in text.lower()
