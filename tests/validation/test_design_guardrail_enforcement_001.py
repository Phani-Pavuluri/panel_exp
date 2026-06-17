"""Tests for DESIGN-GUARDRAIL-ENFORCEMENT-001."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.design.assign import CompleteRandomization
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.validation.design_combination_guardrail_001 import (
    COMBINATION_STATUS_NOT_EVALUATED,
    RC_ENFORCE_GEOMETRY_MISMATCH,
    RC_ENFORCE_POINT_ONLY,
    RC_ENFORCE_POOLED_MULTICELL_BLOCKED,
    evaluate_design_combination_guardrails,
)
from panel_exp.validation.design_guardrail_enforcement_001 import (
    ENFORCEMENT_VERSION,
    RC_ENFORCE_CONTRACT_BLOCKED,
    RC_ENFORCE_DOWNSTREAM_ROLE_BLOCKED,
    RC_ENFORCE_GUARDRAIL_BLOCKED,
    RC_ENFORCE_MISSING_CONTRACT,
    DesignGuardrailEnforcementResult,
    DesignGuardrailViolation,
    assert_design_path_allowed,
    build_producer_guardrail_bundle,
    enforce_design_decision_path,
)
from panel_exp.validation.design_guardrail_runtime_001 import (
    GUARDRAIL_BLOCK,
    GUARDRAIL_UNKNOWN,
    GUARDRAIL_WARN,
    evaluate_design_contract_guardrails,
)
from tests.design_registry_helpers import make_geo_panel

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas"
CONTRACT_DIR = FIXTURE_DIR / "design_contract_golden_001"
ENFORCE_DIR = FIXTURE_DIR / "design_guardrail_enforcement_001"
SCENARIOS = json.loads((ENFORCE_DIR / "scenarios.json").read_text())

DOWNSTREAM_ROLES = (
    "TrustReport",
    "CalibrationSignal",
    "MMM",
    "LLM",
    "production_decision",
    "production_recommendation",
    "automated_budget_action",
    "pooled_causal_claim",
)


def _load_contract(name: str) -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text())


def _contract_payload(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _load_contract(name)
    return payload["design_contract"], payload["contract_validation"]


def _enforce_from_scenario(scenario: dict[str, Any]) -> DesignGuardrailEnforcementResult:
    if scenario.get("missing_contract"):
        return enforce_design_decision_path(
            design_contract=None,
            requested_downstream_role=scenario.get("requested_downstream_role"),
        )
    contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
    return enforce_design_decision_path(
        design_contract=contract,
        contract_validation=validation,
        design_id=scenario.get("design_id"),
        estimator_id=scenario.get("estimator_id"),
        inference_id=scenario.get("inference_id"),
        geometry_id=scenario.get("geometry_id"),
        readout_semantics=scenario.get("readout_semantics"),
        readout_claim_type=scenario.get("readout_claim_type"),
        requested_downstream_role=scenario.get("requested_downstream_role"),
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["fixture_id"] for s in SCENARIOS])
def test_fixture_scenarios(scenario: dict[str, Any]) -> None:
    result = _enforce_from_scenario(scenario)
    assert result.status == scenario["expected_status"]
    assert result.allowed is scenario["expected_allowed"]
    if scenario.get("expected_combination_id"):
        assert result.combination_id == scenario["expected_combination_id"]


class TestContractEnforcement:
    def test_missing_contract_fails_closed_on_enforced_role(self) -> None:
        result = enforce_design_decision_path(
            design_contract=None,
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_BLOCK
        assert RC_ENFORCE_MISSING_CONTRACT in result.reason_codes
        assert result.allowed is False

    def test_contract_block_propagates(self) -> None:
        payload = _load_contract("tier1_multicell_contract_blocked.json")
        result = enforce_design_decision_path(
            design_contract=payload["design_contract"],
            contract_validation=payload["contract_validation"],
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_BLOCK
        assert RC_ENFORCE_GUARDRAIL_BLOCKED in result.reason_codes

    def test_contract_warn_cannot_promote_downstream(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            requested_downstream_role="TrustReport",
        )
        assert result.allowed is False
        assert RC_ENFORCE_DOWNSTREAM_ROLE_BLOCKED in result.reason_codes

    def test_false_downstream_authorization_blocks(self) -> None:
        payload = _load_contract("negative_downstream_authorized_contract.json")
        result = enforce_design_decision_path(
            design_contract=payload["design_contract"],
            contract_validation=payload.get("contract_validation"),
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_BLOCK


class TestCombinationEnforcement:
    def test_dcm001_research_warn(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_WARN
        assert result.combination_id == "DCM-001"
        assert result.allowed is True

    def test_dcm002_point_only_warn(self) -> None:
        contract, _ = _contract_payload("tier1_complete_randomization_contract.json")
        cg = evaluate_design_combination_guardrails(
            design_contract=contract,
            estimator_id="AugSynth",
            inference_id="point_only",
            geometry_id="unit_panel_single_cell",
            readout_semantics="point_only",
        )
        assert cg.combination_id == "DCM-002"
        assert cg.status == GUARDRAIL_WARN

    def test_dcm002_interval_block(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="AugSynth",
            inference_id="point_only",
            geometry_id="unit_panel_single_cell",
            readout_semantics="point_only",
            readout_claim_type="causal_interval",
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_BLOCK
        assert RC_ENFORCE_POINT_ONLY in result.reason_codes

    def test_dcm003_geometry_block(self) -> None:
        contract, _ = _contract_payload("tier1_complete_randomization_contract.json")
        cg = evaluate_design_combination_guardrails(
            design_contract=contract,
            estimator_id="TBR",
            inference_id="aggregate_point",
            geometry_id="unit_panel_single_cell",
        )
        assert cg.combination_id == "DCM-003"
        assert cg.status == GUARDRAIL_BLOCK
        assert RC_ENFORCE_GEOMETRY_MISMATCH in cg.reason_codes

    def test_dcm004_research_warn(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="DID",
            inference_id="bootstrap",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role="research",
        )
        assert result.combination_id == "DCM-004"
        assert result.status == GUARDRAIL_WARN

    def test_dcm006_per_cell_warn(self) -> None:
        contract, _ = _contract_payload("tier1_multicell_contract_blocked.json")
        cg = evaluate_design_combination_guardrails(
            design_contract=contract,
            design_id="DES-011",
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="multi_cell_per_cell",
        )
        assert cg.combination_id == "DCM-006"

    def test_dcm007_pooled_block(self) -> None:
        contract, _ = _contract_payload("tier1_complete_randomization_contract.json")
        cg = evaluate_design_combination_guardrails(
            design_contract=contract,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="pooled_multi_cell",
        )
        assert cg.combination_id == "DCM-007"
        assert cg.status == GUARDRAIL_BLOCK
        assert RC_ENFORCE_POOLED_MULTICELL_BLOCKED in cg.reason_codes

    def test_dcm008_stratified_warn(self) -> None:
        contract, validation = _contract_payload("tier1_stratified_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role="research",
        )
        assert result.combination_id == "DCM-008"
        assert result.status == GUARDRAIL_WARN


class TestReadoutEnforcement:
    def test_forecast_to_causal_block(self) -> None:
        contract, _ = _contract_payload("tier1_complete_randomization_contract.json")
        cg = evaluate_design_combination_guardrails(
            design_contract=contract,
            estimator_id="SARIMAX",
            inference_id="forecast",
            geometry_id="time_series_operator_geometry",
            readout_semantics="forecast_interval",
            readout_claim_type="causal_interval",
        )
        assert cg.status == GUARDRAIL_BLOCK

    def test_null_monitor_to_causal_block(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            readout_semantics="null_monitor",
            readout_claim_type="causal_inference",
            requested_downstream_role="research",
        )
        assert result.status == GUARDRAIL_BLOCK


class TestDownstreamRoles:
    @pytest.mark.parametrize("role", DOWNSTREAM_ROLES)
    def test_downstream_roles_always_block(self, role: str) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role=role,
        )
        assert result.allowed is False
        assert result.status == GUARDRAIL_BLOCK
        with pytest.raises(DesignGuardrailViolation):
            assert_design_path_allowed(result, requested_role=role)


class TestSerialization:
    def test_enforcement_json_serializable(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            requested_downstream_role="research",
        )
        payload = result.to_dict()
        json.dumps(payload)
        assert payload["enforcement_version"] == ENFORCEMENT_VERSION

    def test_design_evidence_round_trip_with_enforcement(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        bundle = build_producer_guardrail_bundle(
            design_contract=contract,
            contract_validation=validation,
        )
        from panel_exp.spec import spec_from_geo_design
        from panel_exp.panel_data import TimePeriod

        spec = spec_from_geo_design(
            "e1",
            "y",
            "unit",
            "time",
            pre_period=TimePeriod(0, 10),
            experiment_period=TimePeriod(10, 20),
            design_method="completerandomization",
            random_state=1,
            treatment_probability=0.5,
        )
        ev = DesignEvidence.from_assignment(
            spec,
            {"control": ["a"], "test_0": ["b"]},
            design_contract=contract,
            contract_validation=validation,
            design_guardrail=bundle["design_guardrail"],
            combination_guardrail=bundle["combination_guardrail"],
            guardrail_enforcement=bundle["guardrail_enforcement"],
        )
        restored = DesignEvidence.from_dict(ev.to_dict())
        assert restored.guardrail_enforcement is not None
        assert restored.combination_guardrail is not None
        assert restored.design_guardrail is not None

    def test_legacy_evidence_loads_without_enforcement_fields(self) -> None:
        legacy = _load_contract("legacy_design_evidence_without_contract.json")
        assert legacy.get("guardrail_enforcement") is None
        result = enforce_design_decision_path(evidence_payload=legacy, requested_downstream_role="research")
        assert result.status == GUARDRAIL_BLOCK

    def test_deterministic_enforcement(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        a = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role="research",
        )
        b = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            geometry_id="unit_panel_single_cell",
            requested_downstream_role="research",
        )
        assert a == b


class TestExceptions:
    def test_typed_exception_with_reason_codes(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        result = enforce_design_decision_path(
            design_contract=contract,
            contract_validation=validation,
            requested_downstream_role="TrustReport",
        )
        with pytest.raises(DesignGuardrailViolation) as exc:
            assert_design_path_allowed(result, requested_role="TrustReport")
        assert exc.value.result.reason_codes
        assert not hasattr(assert_design_path_allowed, "force")


class TestGeoRunnerIntegration:
    def test_geo_runner_emits_guardrail_enforcement(self, monkeypatch) -> None:
        def _fake_metrics(self, *args, **kwargs):
            import pandas as pd

            empty = pd.DataFrame()
            return empty, empty, empty

        monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _fake_metrics)
        panel = make_geo_panel(seed=7, n_units=10, n_times=40)
        geo = GeoExperimentDesign(
            panel_data=panel,
            base_randomizer_cls=CompleteRandomization,
            n_test_grps=1,
            random_state=11,
            test_lengths=[28],
            max_iter=5,
        )
        geo.run_design()
        assert geo.last_evidence is not None
        design = geo.last_evidence.design.to_dict()
        assert "design_guardrail" in design
        assert "combination_guardrail" in design
        assert "guardrail_enforcement" in design
        enf = design["guardrail_enforcement"]
        assert enf["allowed"] is False
        assert enf["combination_status"] == COMBINATION_STATUS_NOT_EVALUATED
        with pytest.raises(DesignGuardrailViolation):
            assert_design_path_allowed(enf, requested_role="TrustReport")

    def test_immutable_contract_on_evaluate(self) -> None:
        contract, validation = _contract_payload("tier1_complete_randomization_contract.json")
        snap = copy.deepcopy(contract)
        evaluate_design_contract_guardrails(
            {"design_contract": contract, "contract_validation": validation}
        )
        assert contract == snap


def test_no_bypass_api_in_enforcement_module() -> None:
    import inspect
    from panel_exp.validation import design_guardrail_enforcement_001 as mod

    src = inspect.getsource(mod)
    assert "force=True" not in src
    assert "override_guardrail" not in src
    assert "bypass_guardrail" not in src
