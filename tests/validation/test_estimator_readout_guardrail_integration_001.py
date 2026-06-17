"""Tests for ESTIMATOR-READOUT-GUARDRAIL-INTEGRATION-001."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from panel_exp.evidence import DesignEvidence, ReadoutEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_guardrail_enforcement_001 import build_producer_guardrail_bundle
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_WARN
from panel_exp.validation.estimator_readout_adapter_001 import (
    ADAPTER_VERSION,
    adapt_native_result_payload,
    build_estimator_readout,
    extract_geometry_context,
    infer_estimator_id_from_analyzer,
    run_governed_analysis,
)
from panel_exp.validation.inference_boundary_guardrail_001 import InferenceBoundaryViolation

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas"
CONTRACT_DIR = FIXTURE_DIR / "design_contract_golden_001"
SCENARIO_DIR = FIXTURE_DIR / "estimator_readout_guardrail_integration_001"
SCENARIOS = json.loads((SCENARIO_DIR / "scenarios.json").read_text())

DOWNSTREAM_ROLES = ("TrustReport", "CalibrationSignal", "MMM", "LLM", "production_decision")


def _load_contract(name: str) -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text())


def _design_evidence_from_contract(
    name: str = "tier1_complete_randomization_contract.json",
    *,
    design_override: str | None = None,
) -> DesignEvidence:
    payload = _load_contract(name)
    contract = dict(payload["design_contract"])
    validation = payload["contract_validation"]

    if design_override == "multicell_percell":
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

    bundle = build_producer_guardrail_bundle(
        design_contract=contract,
        contract_validation=validation,
    )
    spec = spec_from_geo_design(
        "adapter-test",
        "y",
        "unit",
        "time",
        pre_period=TimePeriod(0, 10),
        experiment_period=TimePeriod(10, 20),
        design_method="completerandomization",
        random_state=1,
        treatment_probability=0.5,
    )
    return DesignEvidence.from_assignment(
        spec,
        {"control": ["a", "b"], "test_0": ["c"]},
        design_contract=contract,
        contract_validation=validation,
        design_guardrail=bundle["design_guardrail"],
        combination_guardrail=bundle["combination_guardrail"],
        guardrail_enforcement=bundle["guardrail_enforcement"],
    )


def _scenario_design_evidence(scenario: dict[str, Any]) -> DesignEvidence:
    contract_name = scenario.get("design_contract", "tier1_complete_randomization_contract.json")
    return _design_evidence_from_contract(
        contract_name,
        design_override=scenario.get("design_override"),
    )


def _build_from_scenario(scenario: dict[str, Any], *, enforce: bool = True) -> ReadoutEvidence:
    design_ev = _scenario_design_evidence(scenario)
    geo = scenario.get("geometry_id")
    if geo:
        contract = dict(design_ev.design_contract or {})
        geometry = dict(contract.get("geometry") or {})
        geometry["geometry_id"] = geo
        contract["geometry"] = geometry
        design_ev = DesignEvidence.from_dict({**design_ev.to_dict(), "design_contract": contract})

    return build_estimator_readout(
        design_evidence=design_ev,
        estimator_id=scenario.get("estimator_id"),
        inference_id=scenario.get("inference_id"),
        result_payload=scenario.get("native"),
        readout_semantics=scenario.get("readout_semantics"),
        interval_type=scenario.get("interval_type"),
        cell_id=scenario.get("cell_id"),
        pooled=bool(scenario.get("pooled", False)),
        requested_role=scenario.get("requested_role", "research"),
        enforce=enforce,
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s["fixture_id"])
def test_fixture_scenarios(scenario: dict[str, Any]) -> None:
    expected = scenario["expected_status"]
    if expected == "BLOCK":
        with pytest.raises(InferenceBoundaryViolation):
            _build_from_scenario(scenario)
        return
    readout = _build_from_scenario(scenario)
    guardrail = readout.inference_boundary_guardrail or {}
    assert guardrail.get("status") == GUARDRAIL_WARN
    assert guardrail.get("allowed") is True
    if scenario.get("expected_dcm"):
        resolution = readout.combination_resolution or {}
        assert resolution.get("dcm_row_id") == scenario["expected_dcm"]


class TestNativeAdaptation:
    def test_scm_native_converts(self) -> None:
        native = {
            "y": [1.0, 2.0, 3.0, 4.0],
            "y_hat": [1.0, 1.0, 2.0, 2.0],
            "y_lower": [0.9, 1.9, 1.9, 1.9],
            "y_upper": [1.1, 2.1, 2.1, 2.1],
        }
        adapted = adapt_native_result_payload(
            estimator_id="scm",
            inference_id="unit_jackknife",
            native=native,
        )
        assert adapted.point_estimate is not None
        assert adapted.interval is not None
        assert adapted.readout_semantics == "causal_interval"

    def test_augsynth_point_only_no_interval_inference(self) -> None:
        native = {"y": [1, 2, 3, 4], "y_hat": [1, 1, 2, 2], "y_lower": [0, 0, 0, 0], "y_upper": [2, 2, 2, 2]}
        adapted = adapt_native_result_payload(
            estimator_id="augsynth",
            inference_id="point_only",
            native=native,
        )
        assert adapted.interval is None
        assert adapted.readout_semantics == "point_estimate"

    def test_did_bootstrap_interval(self) -> None:
        native = {"cumulative_att": 0.04, "treatment_ci": [-0.02, 0.10]}
        adapted = adapt_native_result_payload(
            estimator_id="did",
            inference_id="bootstrap",
            native=native,
        )
        assert adapted.point_estimate == pytest.approx(0.04)
        assert adapted.interval == pytest.approx((-0.02, 0.10))

    def test_tbrridge_inference_id_preserved_in_readout(self) -> None:
        for inf, itype in (("brb", "brb_interval"), ("kfold", "kfold_interval"), ("placebo", "placebo_interval")):
            design_ev = _design_evidence_from_contract()
            readout = build_estimator_readout(
                design_evidence=design_ev,
                estimator_id="tbrridge",
                inference_id=inf,
                result_payload={
                    "y": [1, 2, 3, 4],
                    "y_hat": [1, 1, 2, 2],
                    "y_lower": [0.8, 1.8, 1.8, 1.8],
                    "y_upper": [1.2, 2.2, 2.2, 2.2],
                },
                readout_semantics="causal_interval" if inf != "placebo" else "null_monitor_interval",
                interval_type=itype,
                enforce=False,
            )
            assert (readout.inference_identity or {}).get("inference_id") == inf
            assert (readout.inference_identity or {}).get("interval_type") == itype


class TestGeometryPropagation:
    def test_design_geometry_not_estimator(self) -> None:
        design_ev = _design_evidence_from_contract(
            "tier1_complete_randomization_contract.json",
            design_override="multicell_percell",
        )
        ctx = extract_geometry_context(design_ev)
        assert ctx["is_multi_cell"] is True
        assert ctx["geometry_id"] == "multi_cell_per_cell"
        readout = build_estimator_readout(
            design_evidence=design_ev,
            estimator_id="scm",
            inference_id="unit_jackknife",
            result_payload={"y": [1, 2, 3, 4], "y_hat": [1, 1, 2, 2]},
            readout_semantics="per_cell_point",
            cell_id="test_0",
        )
        assert (readout.estimator_identity or {}).get("estimator_id") == "scm"
        assert (readout.readout_identity or {}).get("cell_id") == "test_0"
        meta = (readout.result_payload or {}).get("metadata") or {}
        assert meta.get("geometry_context", {}).get("is_multi_cell") is True

    def test_no_multicell_estimator_identity(self) -> None:
        src = Path(__file__).resolve().parents[2] / "panel_exp" / "validation" / "estimator_readout_adapter_001.py"
        text = src.read_text()
        assert "estimator_id = \"multicell\"" not in text.lower()


class TestAutomaticDCMResolution:
    def test_scm_jk_dcm001(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "scm_jk_research"))
        assert (readout.combination_resolution or {}).get("dcm_row_id") == "DCM-001"

    def test_augsynth_point_dcm002(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "augsynth_point"))
        assert (readout.combination_resolution or {}).get("dcm_row_id") == "DCM-002"

    def test_tbr_unit_panel_dcm003_block(self) -> None:
        with pytest.raises(InferenceBoundaryViolation):
            _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "tbr_unit_panel_blocked"))


class TestEnforcement:
    def test_research_warn_not_production(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "scm_jk_research"))
        g = readout.inference_boundary_guardrail or {}
        assert g.get("status") == GUARDRAIL_WARN
        assert g.get("allowed") is True
        enforcement = readout.guardrail_enforcement or {}
        assert enforcement.get("downstream_authorization_status") != "authorized"

    @pytest.mark.parametrize("role", DOWNSTREAM_ROLES)
    def test_downstream_blocked(self, role: str) -> None:
        design_ev = _design_evidence_from_contract()
        with pytest.raises(InferenceBoundaryViolation):
            build_estimator_readout(
                design_evidence=design_ev,
                estimator_id="scm",
                inference_id="unit_jackknife",
                result_payload={
                    "y": [1, 2, 3, 4],
                    "y_hat": [1, 1, 2, 2],
                    "y_lower": [0.9, 1.9, 1.9, 1.9],
                    "y_upper": [1.1, 2.1, 2.1, 2.1],
                },
                readout_semantics="causal_interval",
                requested_role=role,
            )

    def test_no_bypass_in_adapter(self) -> None:
        src = inspect.getsource(build_estimator_readout)
        assert "override_guardrail" not in src
        assert "bypass_guardrail" not in src


class TestBackwardCompatibility:
    def test_legacy_run_analysis_return_unchanged(self) -> None:
        analyzer = MagicMock()
        analyzer.run_analysis.return_value = {"y": [1, 2], "y_hat": [1, 1]}
        analyzer.results = {"y": [1, 2], "y_hat": [1, 1]}
        analyzer.inference = "UnitJackKnife"
        analyzer.__class__.__name__ = "SyntheticControlCVXPY"

        panel = MagicMock()
        out = analyzer.run_analysis(panel)
        assert out == {"y": [1, 2], "y_hat": [1, 1]}
        assert infer_estimator_id_from_analyzer(analyzer) == "scm"

    def test_governed_wrapper_returns_readout_evidence(self) -> None:
        analyzer = MagicMock()
        analyzer.run_analysis.return_value = {
            "y": [1.0, 2.0, 3.0, 4.0],
            "y_hat": [1.0, 1.0, 2.0, 2.0],
            "y_lower": [0.9, 1.9, 1.9, 1.9],
            "y_upper": [1.1, 2.1, 2.1, 2.1],
        }
        analyzer.results = analyzer.run_analysis.return_value
        analyzer.inference = "UnitJackKnife"
        analyzer.__class__.__name__ = "SyntheticControlCVXPY"
        analyzer.inference_result = None

        design_ev = _design_evidence_from_contract()
        governed = run_governed_analysis(
            analyzer,
            MagicMock(),
            design_ev,
            readout_semantics="causal_interval",
        )
        assert isinstance(governed.readout_evidence, ReadoutEvidence)
        assert governed.native_results["y"] == [1.0, 2.0, 3.0, 4.0]

    def test_serialization_round_trip(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "scm_jk_research"))
        restored = ReadoutEvidence.from_dict(readout.to_dict())
        assert restored.combination_resolution == readout.combination_resolution
        assert restored.inference_boundary_guardrail == readout.inference_boundary_guardrail

    def test_deterministic_adapter_version(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "scm_jk_research"))
        meta = (readout.result_payload or {}).get("metadata") or {}
        assert meta.get("adapter_version") == ADAPTER_VERSION


class TestRuntimeDemonstrations:
    def test_scm_to_warn_research(self) -> None:
        readout = _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "scm_jk_research"))
        assert (readout.combination_resolution or {}).get("dcm_row_id") == "DCM-001"
        assert (readout.inference_boundary_guardrail or {}).get("status") == GUARDRAIL_WARN

    def test_augsynth_interval_block(self) -> None:
        with pytest.raises(InferenceBoundaryViolation):
            _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "augsynth_interval_blocked"))

    def test_multicell_pooled_block(self) -> None:
        with pytest.raises(InferenceBoundaryViolation):
            _build_from_scenario(next(s for s in SCENARIOS if s["fixture_id"] == "multicell_pooled_blocked"))

    def test_adapter_calls_guarded_builder_not_duplicate(self) -> None:
        src = Path(__file__).resolve().parents[2] / "panel_exp" / "validation" / "estimator_readout_adapter_001.py"
        text = src.read_text()
        assert "build_guarded_readout" in text
        assert "evaluate_inference_boundary_guardrail" not in text
        assert "resolve_design_combination" not in text


class TestDownstreamAuthorizationBoundary:
    def test_trustreport_wiring_warns_without_governed_readout(self) -> None:
        from panel_exp.track_b.readout_evidence_wiring import (
            DOWNSTREAM_READOUT_NOT_AUTHORIZED,
            build_trust_report_decision_inputs_from_bundle,
        )

        bundle = {
            "evidence": {
                "inference_metadata": {
                    "estimator_name": "SCM",
                    "inference_mode": "UnitJackKnife",
                },
                "track_b_export_hints": {"run_status": "success"},
            }
        }
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert any(DOWNSTREAM_READOUT_NOT_AUTHORIZED in w for w in inputs.extraction_warnings)

    def test_governed_marker_hint_does_not_authorize_trust_report(self) -> None:
        from panel_exp.validation.estimator_readout_adapter_001 import GOVERNED_READOUT_MARKER
        from panel_exp.track_b.readout_evidence_wiring import (
            DOWNSTREAM_READOUT_NOT_AUTHORIZED,
            build_trust_report_decision_inputs_from_bundle,
        )

        bundle = {
            "evidence": {
                "readout_evidence": {"evidence_version": "1.0"},
                "inference_metadata": {"estimator_name": "SCM", "inference_mode": "UnitJackKnife"},
                "track_b_export_hints": {GOVERNED_READOUT_MARKER: True},
            }
        }
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert any(DOWNSTREAM_READOUT_NOT_AUTHORIZED in w for w in inputs.extraction_warnings)
        assert inputs.trust_report_ready is False
        assert inputs.downstream_authorization is not None
        assert inputs.downstream_authorization["authorized"] is False


class TestDesignTimeEnforcementIntact:
    def test_design_guardrail_fields_present(self) -> None:
        design_ev = _design_evidence_from_contract()
        assert design_ev.guardrail_enforcement is not None
        readout = build_estimator_readout(
            design_evidence=design_ev,
            estimator_id="scm",
            inference_id="unit_jackknife",
            result_payload={
                "y": [1, 2, 3, 4],
                "y_hat": [1, 1, 2, 2],
                "y_lower": [0.9, 1.9, 1.9, 1.9],
                "y_upper": [1.1, 2.1, 2.1, 2.1],
            },
            readout_semantics="causal_interval",
        )
        assert readout.guardrail_enforcement is not None
