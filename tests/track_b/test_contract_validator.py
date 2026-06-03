"""B5d — Track B contract bundle validator tests."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from tests.track_b.contract_fixtures import FixtureCase, iter_all_fixture_cases
from tests.track_b.contract_validator import (
    ValidationIssue,
    ValidationResult,
    main,
    validate_all_track_b_contracts,
    validate_contract_case,
    validate_fixture_document,
    validate_manifest,
)


class TestManifestValidation:
    def test_manifest_validates_clean(self) -> None:
        assert validate_manifest() == []

    def test_manifest_detects_missing_gold_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tests.track_b import contract_fixtures as cf

        real_load = cf.load_manifest

        def _bad_manifest() -> dict:
            m = json.loads(json.dumps(real_load()))
            m["fixtures"] = m["fixtures"][:-1]
            return m

        monkeypatch.setattr(cf, "load_manifest", _bad_manifest)
        issues = validate_manifest()
        assert issues
        messages = " ".join(i.message for i in issues)
        assert "missing fixture_ids" in messages or "expected 10 entries" in messages


class TestFixtureDocumentsValidate:
    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.filename)
    def test_each_fixture_file_passes_document_validation(self, case) -> None:
        issues = validate_fixture_document(case.filename)
        assert not issues, "\n".join(str(i) for i in issues)


class TestContractBundleValidation:
    def test_all_golden_cases_validate(self) -> None:
        result = validate_all_track_b_contracts()
        assert result.ok, result.format_messages()

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_each_case_validates(self, case) -> None:
        issues = validate_contract_case(case)
        assert not issues, "\n".join(str(i) for i in issues)


class TestValidatorDetectsViolations:
    def _first_case(self) -> FixtureCase:
        return next(iter_all_fixture_cases())

    def test_detects_trust_verdict_on_evidence(self) -> None:
        case = self._first_case()
        adapter = dict(case.adapter_expected_output)
        evidence = dict(adapter.get("experiment_evidence") or {})
        evidence["trust_outcome"] = "supported"
        adapter["experiment_evidence"] = evidence
        bad = replace(case, adapter_expected_output=adapter)
        issues = validate_contract_case(bad)
        assert any("trust_outcome" in str(i) for i in issues)

    def test_detects_invalid_export_status(self) -> None:
        case = self._first_case()
        adapter = dict(case.adapter_expected_output)
        adapter["export_status"] = "bogus"
        bad = replace(case, adapter_expected_output=adapter)
        issues = validate_contract_case(bad)
        assert any("export_status" in str(i) for i in issues)

    def test_detects_missing_trust_scenario_fields(self) -> None:
        case = self._first_case()
        tr = dict(case.trust_report_expected_output)
        scenarios = [dict(s) for s in tr["scenarios"]]
        del scenarios[0]["alignment_verdict"]
        tr["scenarios"] = scenarios
        bad = replace(case, trust_report_expected_output=tr)
        issues = validate_contract_case(bad)
        assert any("alignment_verdict" in str(i) for i in issues)

    def test_detects_composition_mismatch(self) -> None:
        case = self._first_case()
        tr = dict(case.trust_report_expected_output)
        scenarios = [dict(s) for s in tr["scenarios"]]
        lift = next(s for s in scenarios if s["scenario_id"] == "lift_launch")
        lift["trust_outcome"] = "supported"
        tr["scenarios"] = scenarios
        bad = replace(case, trust_report_expected_output=tr)
        issues = validate_contract_case(bad)
        assert any(
            "lift_launch" in str(i) and "trust_outcome" in str(i) and "oracle" in str(i)
            for i in issues
        )

    def test_f1_guard_flags_complete_export_without_declaration(self) -> None:
        case = self._first_case()
        adapter = dict(case.adapter_expected_output)
        adapter["legacy_mapping_applied"] = False
        evidence = dict(adapter["experiment_evidence"] or {})
        evidence["declared_estimand_id"] = None
        adapter["experiment_evidence"] = evidence
        spec = dict(case.spec)
        spec["declared_estimand_id"] = None
        bad = replace(
            case,
            spec=spec,
            adapter_expected_output=adapter,
            forbidden_regressions=["F1"],
        )
        issues = validate_contract_case(bad)
        assert any("F1:" in str(i) for i in issues)


class TestValidatorCli:
    def test_cli_exits_zero_on_valid_fixtures(self) -> None:
        assert main([]) == 0

    def test_cli_exits_nonzero_when_validation_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tests.track_b import contract_validator as cv

        monkeypatch.setattr(
            cv,
            "validate_all_track_b_contracts",
            lambda: ValidationResult(
                issues=[ValidationIssue("test", "forced failure")]
            ),
        )
        assert main([]) == 1
