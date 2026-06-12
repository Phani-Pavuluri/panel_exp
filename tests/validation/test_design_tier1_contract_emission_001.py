"""Tests for DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-001."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    StratifiedRandomization,
)
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.evidence import DesignEvidence
from panel_exp.validation.design_contract_builder_001 import (
    build_and_validate_tier1_contract,
    build_tier1_design_contract,
)
from panel_exp.validation.design_contract_validator_001 import (
    CONTRACT_BLOCKED,
    CONTRACT_VALID,
    CONTRACT_VALID_WITH_WARNINGS,
    RC_MISSING_STRATUM_IDS,
    RC_MISSING_SHARED_CONTROL_POLICY,
    validate_design_contract,
    validate_design_evidence_contract,
)
from tests.design_registry_helpers import make_geo_panel


def _stub_mde(monkeypatch):
    def _fake_metrics(self, *args, **kwargs):
        import pandas as pd

        empty = pd.DataFrame()
        return empty, empty, empty

    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _fake_metrics)


def _run_geo(
    monkeypatch,
    *,
    base_cls: type,
    n_test_grps: int = 1,
    validate_after_assign: bool = False,
    **geo_kwargs: Any,
) -> GeoExperimentDesign:
    _stub_mde(monkeypatch)
    panel = make_geo_panel(seed=7, n_units=10, n_times=40)
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=base_cls,
        n_test_grps=n_test_grps,
        random_state=11,
        validate_after_assign=validate_after_assign,
        test_lengths=[28],
        max_iter=5,
        **geo_kwargs,
    )
    geo.run_design()
    return geo


def _design_dict(geo: GeoExperimentDesign) -> dict[str, Any]:
    assert geo.last_evidence is not None
    return geo.last_evidence.design.to_dict()


def test_tier1_output_contains_design_contract(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    payload = _design_dict(geo)
    assert "design_contract" in payload
    assert payload["design_contract"]["schema_name"] == "DESIGN-CONTRACT-SCHEMA-001"


def test_emitted_contract_validates_with_standalone_validator(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    payload = _design_dict(geo)
    result = validate_design_evidence_contract(payload)
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)


def test_contract_validation_summary_exists(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=BalancedRandomization)
    payload = _design_dict(geo)
    assert "contract_validation" in payload
    summary = payload["contract_validation"]
    assert "status" in summary
    assert "severity" in summary
    assert "reason_codes" in summary
    assert "validator_version" in summary


def test_emitted_status_is_validator_derived(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    payload = _design_dict(geo)
    contract = payload["design_contract"]
    summary = payload["contract_validation"]
    assert contract["design_contract_status"] == summary["status"]


def test_no_contract_complete_allowed(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    summary = _design_dict(geo)["contract_validation"]
    assert summary["contract_complete_allowed"] is False


def test_no_downstream_authorization_allowed(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    governance = _design_dict(geo)["design_contract"]["governance"]
    assert governance["downstream_authorization_status"] in ("blocked", "not_authorized")
    assert governance.get("trust_report_eligible") is not True
    assert governance.get("llm_authorized") is not True


def test_forbidden_downstream_claims_nonempty(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    forbidden = _design_dict(geo)["design_contract"]["governance"]["forbidden_downstream_claims"]
    assert isinstance(forbidden, list)
    assert len(forbidden) > 0
    assert "trust_report" in forbidden


def test_legacy_evidence_without_design_contract_supported():
    legacy = {
        "evidence_version": "1.0",
        "experiment_id": "legacy-exp",
        "created_at": "2026-01-01T00:00:00+00:00",
        "package_version": "0.2.1",
        "code_version": None,
        "spec_hash": "abc",
        "assignment_hash": "def",
        "input_data_hash": None,
        "design_name": "complete_randomization",
        "assignment": {"control": ["u0"], "test_0": ["u1"]},
        "validation_summary": {},
        "inference_metadata": {},
        "warnings": [],
        "errors": [],
        "artifacts": {},
        "diagnostics": {},
    }
    ev = DesignEvidence.from_dict(legacy)
    payload = ev.to_dict()
    assert "design_contract" not in payload
    assert "contract_validation" not in payload


def test_stratified_emits_structure_metadata(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=StratifiedRandomization)
    structure = _design_dict(geo)["design_contract"].get("structure", {})
    assert structure.get("stratum_ids")
    assert structure.get("unit_to_stratum_map")
    result = validate_design_contract(_design_dict(geo)["design_contract"])
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)
    assert RC_MISSING_STRATUM_IDS not in result.reason_codes


def test_rerandomization_wrapper_identity_emitted(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    identity = _design_dict(geo)["design_contract"]["design_identity"]
    assert identity.get("wrapper_identity") == "Rerandomization"
    assert identity.get("design_method_class") == "CompleteRandomization"


def test_multicell_emits_cell_and_shared_control_metadata(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=BalancedRandomization, n_test_grps=2)
    multi_cell = _design_dict(geo)["design_contract"]["multi_cell"]
    assert multi_cell.get("is_multi_cell") is True
    assert multi_cell.get("cell_ids")
    assert multi_cell.get("shared_control_policy")
    result = validate_design_contract(_design_dict(geo)["design_contract"])
    assert result.status in (CONTRACT_VALID, CONTRACT_VALID_WITH_WARNINGS)
    assert RC_MISSING_SHARED_CONTROL_POLICY not in result.reason_codes


def test_multicell_blocks_when_shared_control_missing():
    from panel_exp.spec import spec_from_geo_design
    from panel_exp.panel_data import TimePeriod

    panel = make_geo_panel()
    spec = spec_from_geo_design(
        "mc-test",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(start=0, end=20),
        experiment_period=TimePeriod(start=20, end=None),
        design_method="balancedrandomization",
        n_test_groups=2,
    )
    assignment = {"control": ["u0", "u1"], "test_0": ["u2"], "test_1": ["u3"]}
    contract = build_tier1_design_contract(
        spec=spec,
        assignment=assignment,
        registry_key="balancedrandomization",
        base_randomizer_cls=BalancedRandomization,
        n_test_grps=2,
        treatment_probability=0.5,
    )
    contract["multi_cell"] = {"is_multi_cell": True, "cell_ids": ["test_0", "test_1"]}
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_SHARED_CONTROL_POLICY in result.reason_codes


def test_stratified_blocks_when_structure_missing():
    from panel_exp.spec import spec_from_geo_design
    from panel_exp.panel_data import TimePeriod

    panel = make_geo_panel()
    spec = spec_from_geo_design(
        "strat-test",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(start=0, end=20),
        experiment_period=TimePeriod(start=20, end=None),
        design_method="stratifiedrandomization",
    )
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    contract = build_tier1_design_contract(
        spec=spec,
        assignment=assignment,
        registry_key="stratifiedrandomization",
        base_randomizer_cls=StratifiedRandomization,
        n_test_grps=1,
        treatment_probability=0.5,
        wide_data=None,
    )
    result = validate_design_contract(contract)
    assert result.status == CONTRACT_BLOCKED
    assert RC_MISSING_STRATUM_IDS in result.reason_codes


def test_builder_does_not_mutate_inputs():
    from panel_exp.spec import spec_from_geo_design
    from panel_exp.panel_data import TimePeriod

    spec = spec_from_geo_design(
        "mut-test",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(start=0, end=20),
        experiment_period=TimePeriod(start=20, end=None),
        design_method="completerandomization",
    )
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    assignment_before = copy.deepcopy(assignment)
    build_and_validate_tier1_contract(
        spec=spec,
        assignment=assignment,
        registry_key="completerandomization",
        base_randomizer_cls=CompleteRandomization,
        n_test_grps=1,
        treatment_probability=0.5,
    )
    assert assignment == assignment_before


def test_never_emits_contract_complete_status(monkeypatch):
    geo = _run_geo(monkeypatch, base_cls=CompleteRandomization)
    status = _design_dict(geo)["design_contract"]["design_contract_status"]
    assert status != "contract_complete"
