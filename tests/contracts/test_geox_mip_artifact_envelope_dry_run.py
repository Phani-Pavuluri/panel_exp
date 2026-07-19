import json
import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).parents[2]
pkg = types.ModuleType("panel_exp")
pkg.__path__ = [str(ROOT / "panel_exp")]
contracts_pkg = types.ModuleType("panel_exp.contracts")
contracts_pkg.__path__ = [str(ROOT / "panel_exp" / "contracts")]
sys.modules.setdefault("panel_exp", pkg)
sys.modules.setdefault("panel_exp.contracts", contracts_pkg)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_load("panel_exp.contracts.geox_mip_artifact_envelope", ROOT / "panel_exp/contracts/geox_mip_artifact_envelope.py")
runtime = _load("panel_exp.contracts.geox_mip_artifact_envelope_dry_run", ROOT / "panel_exp/contracts/geox_mip_artifact_envelope_dry_run.py")


def test_cases_a_through_f_are_valid_and_ordered():
    result = runtime.build_non_production_geox_mip_artifact_envelope_dry_run()
    assert [case.case_id for case in result.cases] == list("ABCDEF")
    assert result.all_cases_valid
    assert all(case.validation_passed for case in result.cases)


def test_case_boundaries_preserve_non_production_status():
    result = runtime.build_non_production_geox_mip_artifact_envelope_dry_run()
    by_id = {case.case_id: case.envelope for case in result.cases}
    assert by_id["A"].mip_consumption_status == "diagnostic_context_only"
    assert by_id["A"].authorization_status == "not_authorized"
    assert by_id["B"].mip_consumption_status == "blocked"
    assert by_id["B"].downstream_eligibility == "explain_only"
    assert by_id["C"].mip_consumption_status == "answerability_context_only"
    assert "no_recommendation_generated" in by_id["C"].warnings
    assert by_id["D"].mip_consumption_status == "diagnostic_context_only"
    assert "no_calibration_export" in by_id["D"].warnings
    assert by_id["E"].mip_consumption_status == "blocked"
    assert by_id["F"].mip_consumption_status == "blocked"
    assert "evidence_mapping_missing" in by_id["F"].blocked_reasons


def test_summary_has_no_authorization_flags_and_no_mip_mutation():
    result = runtime.build_non_production_geox_mip_artifact_envelope_dry_run()
    assert result.mip_repository_modified is False
    assert result.production_authorization_preserved is True
    assert result.summary["non_production_fixture_only"] is True
    assert all(value is False for key, value in result.summary.items() if key.endswith("_authorized"))


def test_serialization_is_repeatable_and_json_safe():
    first = runtime.serialize_geox_mip_artifact_envelope_dry_run_result(runtime.build_non_production_geox_mip_artifact_envelope_dry_run())
    second = runtime.serialize_geox_mip_artifact_envelope_dry_run_result(runtime.build_non_production_geox_mip_artifact_envelope_dry_run())
    assert first == second
    assert json.dumps(first, sort_keys=True)
