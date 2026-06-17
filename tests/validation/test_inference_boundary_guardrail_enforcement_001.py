"""Tests for INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.design.assign import CompleteRandomization
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.evidence import DesignEvidence, ReadoutEvidence
from panel_exp.validation.design_combination_resolver_001 import resolve_design_combination
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_BLOCK, GUARDRAIL_WARN
from panel_exp.validation.inference_boundary_guardrail_001 import (
    InferenceBoundaryViolation,
    RC_BOUNDARY_POINT_ONLY,
    assert_inference_readout_allowed,
    evaluate_inference_boundary_guardrail,
)
from panel_exp.validation.inference_boundary_identity_001 import (
    InferenceBoundaryIdentity,
    normalize_estimator_id,
    normalize_inference_id,
)
from panel_exp.validation.readout_boundary_builder_001 import build_guarded_readout
from tests.design_registry_helpers import make_geo_panel

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas"
CONTRACT_DIR = FIXTURE_DIR / "design_contract_golden_001"
BOUNDARY_DIR = FIXTURE_DIR / "inference_boundary_guardrail_001"
SCENARIOS = json.loads((BOUNDARY_DIR / "scenarios.json").read_text())

DOWNSTREAM_ROLES = ("TrustReport", "CalibrationSignal", "MMM", "LLM", "production_decision")


def _load_contract(name: str) -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text())


def _design_evidence_from_contract(name: str = "tier1_complete_randomization_contract.json") -> dict[str, Any]:
    payload = _load_contract(name)
    from panel_exp.spec import spec_from_geo_design
    from panel_exp.panel_data import TimePeriod
    from panel_exp.validation.design_guardrail_enforcement_001 import build_producer_guardrail_bundle

    contract = payload["design_contract"]
    validation = payload["contract_validation"]
    bundle = build_producer_guardrail_bundle(
        design_contract=contract,
        contract_validation=validation,
    )
    spec = spec_from_geo_design(
        "boundary-test",
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
        {"control": ["a", "b"], "test_0": ["c"]},
        design_contract=contract,
        contract_validation=validation,
        design_guardrail=bundle["design_guardrail"],
        combination_guardrail=bundle["combination_guardrail"],
        guardrail_enforcement=bundle["guardrail_enforcement"],
    )
    return ev.to_dict()


def _evaluate_scenario(scenario: dict[str, Any]) -> Any:
    if scenario.get("legacy"):
        design_ev = {"design_method": "greedy_match_markets", "assignment": {"control": ["a"]}}
    elif scenario.get("design_id") == "DES-004":
        design_ev = _design_evidence_from_contract("tier1_stratified_contract.json")
    elif scenario.get("design_id") == "DES-011":
        if scenario.get("fixture_id") == "multicell_percell_warn":
            design_ev = _design_evidence_from_contract("tier1_complete_randomization_contract.json")
            contract = dict(design_ev["design_contract"])
            identity = dict(contract.get("design_identity") or {})
            identity["design_inventory_id"] = "DES-011"
            contract["design_identity"] = identity
            geometry = dict(contract.get("geometry") or {})
            geometry["geometry_id"] = "multi_cell_per_cell"
            contract["geometry"] = geometry
            contract["multi_cell"] = {
                "is_multi_cell": True,
                "cell_ids": ["test_0", "test_1"],
                "shared_control_policy": "explicit_reservation",
                "control_reuse_policy": "per_cell_isolated",
                "pooled_claims_allowed": False,
            }
            design_ev = dict(design_ev)
            design_ev["design_contract"] = contract
        else:
            design_ev = _design_evidence_from_contract("tier1_multicell_contract_blocked.json")
    else:
        design_ev = _design_evidence_from_contract()

    identity = InferenceBoundaryIdentity.build(
        design_id=scenario.get("design_id"),
        estimator_id=scenario.get("estimator_id"),
        inference_id=scenario.get("inference_id"),
        geometry_id=scenario.get("geometry_id"),
        readout_semantics=scenario.get("readout_semantics"),
        interval_type=scenario.get("interval_type"),
        cell_id=scenario.get("cell_id"),
        pooled=bool(scenario.get("pooled", False)),
        requested_role=scenario.get("requested_role"),
    )
    return evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=identity)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["fixture_id"] for s in SCENARIOS])
def test_fixture_scenarios(scenario: dict[str, Any]) -> None:
    result = _evaluate_scenario(scenario)
    assert result.status == scenario["expected_status"]
    assert result.allowed is scenario["expected_allowed"]
    if scenario.get("expected_dcm"):
        assert result.dcm_row_id == scenario["expected_dcm"]
    if scenario.get("expected_combination_status"):
        assert result.combination_status == scenario["expected_combination_status"]


class TestIdentityNormalization:
    def test_estimator_aliases(self) -> None:
        assert normalize_estimator_id("SyntheticControlCVXPY") == "scm"
        assert normalize_estimator_id("AugSynth") == "augsynth"

    def test_inference_aliases(self) -> None:
        assert normalize_inference_id("UnitJackknife") == "unit_jackknife"
        assert normalize_inference_id("jackknife") == "unit_jackknife"

    def test_explicit_registry_preferred(self) -> None:
        assert normalize_estimator_id("foo", explicit_registry_id="augsynth") == "augsynth"

    def test_identity_immutable(self) -> None:
        ident = InferenceBoundaryIdentity.build(estimator_id="SCM", inference_id="UnitJackknife")
        with pytest.raises(Exception):
            ident.estimator_id = "did"  # type: ignore[misc]


class TestDCMResolution:
    def test_scm_jk_dcm001(self) -> None:
        ident = InferenceBoundaryIdentity.build(estimator_id="SCM", inference_id="UnitJackknife")
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-001"

    def test_augsynth_dcm002(self) -> None:
        ident = InferenceBoundaryIdentity.build(estimator_id="AugSynth", inference_id="point_only")
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-002"

    def test_tbr_dcm003(self) -> None:
        ident = InferenceBoundaryIdentity.build(
            estimator_id="TBR", inference_id="aggregate_point", geometry_id="unit_panel_single_cell"
        )
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-003"

    def test_did_dcm004(self) -> None:
        ident = InferenceBoundaryIdentity.build(estimator_id="DID", inference_id="bootstrap")
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-004"

    def test_multicell_pooled_dcm007(self) -> None:
        ident = InferenceBoundaryIdentity.build(
            estimator_id="SCM", inference_id="unit_jackknife", pooled=True
        )
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-007"

    def test_stratified_dcm008(self) -> None:
        ident = InferenceBoundaryIdentity.build(
            design_id="DES-004", estimator_id="SCM", inference_id="UnitJackknife"
        )
        res = resolve_design_combination(ident)
        assert res.dcm_row_id == "DCM-008"


class TestReadoutRules:
    def test_augsynth_interval_blocked(self) -> None:
        design_ev = _design_evidence_from_contract()
        ident = InferenceBoundaryIdentity.build(
            estimator_id="AugSynth",
            inference_id="point_only",
            readout_semantics="causal_interval",
            interval_type="jackknife_interval",
            requested_role="research",
        )
        result = evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=ident)
        assert result.status == GUARDRAIL_BLOCK
        assert RC_BOUNDARY_POINT_ONLY in result.reason_codes

    def test_pooled_multicell_blocked(self) -> None:
        design_ev = _design_evidence_from_contract("tier1_multicell_contract_blocked.json")
        ident = InferenceBoundaryIdentity.build(
            design_id="DES-011",
            estimator_id="SCM",
            inference_id="unit_jackknife",
            geometry_id="pooled_multi_cell",
            pooled=True,
            readout_semantics="pooled_point",
            requested_role="research",
        )
        result = evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=ident)
        assert result.status == GUARDRAIL_BLOCK


class TestDownstreamRoles:
    @pytest.mark.parametrize("role", DOWNSTREAM_ROLES)
    def test_downstream_blocked(self, role: str) -> None:
        design_ev = _design_evidence_from_contract()
        ident = InferenceBoundaryIdentity.build(
            estimator_id="SCM",
            inference_id="UnitJackknife",
            requested_role=role,
        )
        result = evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=ident)
        assert result.allowed is False
        assert result.status == GUARDRAIL_BLOCK
        with pytest.raises(InferenceBoundaryViolation):
            assert_inference_readout_allowed(result, requested_role=role)


class TestSerialization:
    def test_readout_evidence_round_trip(self) -> None:
        design_ev = _design_evidence_from_contract()
        readout = build_guarded_readout(
            design_evidence=design_ev,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            readout_semantics="causal_interval",
            interval_type="jackknife_interval",
            requested_role="research",
            point_estimate=0.05,
            interval=(0.01, 0.09),
            enforce=False,
        )
        restored = ReadoutEvidence.from_dict(readout.to_dict())
        assert restored.inference_boundary_guardrail is not None
        assert restored.combination_resolution is not None
        dcm = dict(restored.combination_resolution or {}).get("dcm_row_id")
        assert dcm == "DCM-001"

    def test_deterministic_boundary(self) -> None:
        design_ev = _design_evidence_from_contract()
        ident = InferenceBoundaryIdentity.build(
            estimator_id="SCM", inference_id="UnitJackknife", requested_role="research"
        )
        a = evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=ident)
        b = evaluate_inference_boundary_guardrail(design_evidence=design_ev, identity=ident)
        assert a == b


class TestIntegration:
    def test_design_not_evaluated_becomes_concrete_at_boundary(self) -> None:
        design_ev = _design_evidence_from_contract()
        assert design_ev["combination_guardrail"]["combination_status"] == "not_evaluated"
        readout = build_guarded_readout(
            design_evidence=design_ev,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            readout_semantics="causal_interval",
            interval_type="jackknife_interval",
            requested_role="research",
            point_estimate=0.1,
            interval=(0.0, 0.2),
            enforce=False,
        )
        boundary = dict(readout.inference_boundary_guardrail or {})
        assert boundary["dcm_row_id"] == "DCM-001"
        assert boundary["combination_status"] == "characterized_with_restrictions"
        assert boundary["status"] == GUARDRAIL_WARN

    def test_augsynth_point_warn_interval_block(self) -> None:
        design_ev = _design_evidence_from_contract()
        point = build_guarded_readout(
            design_evidence=design_ev,
            estimator_id="AugSynth",
            inference_id="point_only",
            readout_semantics="point_estimate",
            requested_role="research",
            point_estimate=0.02,
            enforce=False,
        )
        assert dict(point.inference_boundary_guardrail or {})["status"] == GUARDRAIL_WARN
        with pytest.raises(InferenceBoundaryViolation):
            build_guarded_readout(
                design_evidence=design_ev,
                estimator_id="AugSynth",
                inference_id="point_only",
                readout_semantics="causal_interval",
                interval_type="jackknife_interval",
                requested_role="research",
                point_estimate=0.02,
                interval=(0.0, 0.04),
                enforce=True,
            )

    def test_geo_runner_design_then_boundary(self, monkeypatch) -> None:
        def _fake_metrics(self, *args, **kwargs):
            import pandas as pd

            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
        design_dict = geo.last_evidence.design.to_dict()
        assert design_dict["combination_guardrail"]["combination_status"] == "not_evaluated"
        readout = build_guarded_readout(
            design_evidence=design_dict,
            estimator_id="SCM",
            inference_id="UnitJackknife",
            readout_semantics="causal_interval",
            requested_role="research",
            point_estimate=0.0,
            enforce=False,
        )
        assert dict(readout.combination_resolution or {})["dcm_row_id"] == "DCM-001"


def test_no_bypass_in_boundary_modules() -> None:
    import inspect
    from panel_exp.validation import inference_boundary_guardrail_001 as mod

    src = inspect.getsource(mod)
    assert "force=True" not in src
    assert "override_guardrail" not in src
    assert "bypass_guardrail" not in src
