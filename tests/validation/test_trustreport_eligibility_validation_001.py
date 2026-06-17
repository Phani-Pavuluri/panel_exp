"""Tests for TRUSTREPORT-ELIGIBILITY-VALIDATION-001."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from panel_exp.evidence import DesignEvidence, ReadoutEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.track_b.readout_evidence_wiring import build_trust_report_decision_inputs_from_bundle
from panel_exp.validation.design_guardrail_enforcement_001 import build_producer_guardrail_bundle
from panel_exp.validation.estimator_readout_adapter_001 import (
    GOVERNED_READOUT_MARKER,
    build_estimator_readout,
)
from panel_exp.validation.trustreport_eligibility_001 import (
    ELIGIBILITY_VERSION,
    STATUS_ELIGIBLE_CANDIDATE,
    STATUS_ELIGIBLE_WITH_RESTRICTIONS,
    STATUS_INELIGIBLE,
    STATUS_INSUFFICIENT_EVIDENCE,
    STATUS_UNKNOWN,
    TrustReportEligibilityViolation,
    TrustReportEmpiricalEvidence,
    assert_trustreport_eligible_for_promotion,
    evaluate_trustreport_eligibility,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas"
CONTRACT_DIR = FIXTURE_DIR / "design_contract_golden_001"
ESTIMATOR_SCENARIOS = json.loads(
    (FIXTURE_DIR / "estimator_readout_guardrail_integration_001" / "scenarios.json").read_text()
)
ELIG_SCENARIOS = json.loads(
    (FIXTURE_DIR / "trustreport_eligibility_validation_001" / "scenarios.json").read_text()
)

_TEMPLATE_MAP = {
    "scm_jk": "scm_jk_research",
    "scm_placebo_causal": "scm_placebo_null_monitor",
    "stratified_scm_jk": "stratified_scm_jk",
    "augsynth_point": "augsynth_point",
    "augsynth_interval": "augsynth_interval_blocked",
    "did_bootstrap": "did_bootstrap",
    "tbr_unit_panel": "tbr_unit_panel_blocked",
    "tbrridge_brb": "tbrridge_brb",
    "tbrridge_kfold": "tbrridge_kfold",
    "tbrridge_placebo": "tbrridge_placebo",
    "multicell_percell": "multicell_per_cell",
    "multicell_pooled": "multicell_pooled_blocked",
}


def _load_contract(name: str = "tier1_complete_randomization_contract.json") -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text())


def _design_evidence(
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
        "elig-test",
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


def _build_readout(template: str, *, enforce: bool = True) -> ReadoutEvidence:
    fixture_id = _TEMPLATE_MAP[template]
    scenario = next(s for s in ESTIMATOR_SCENARIOS if s["fixture_id"] == fixture_id)
    design_ev = _design_evidence(
        scenario.get("design_contract", "tier1_complete_randomization_contract.json"),
        design_override=scenario.get("design_override"),
    )
    if scenario.get("geometry_id"):
        contract = dict(design_ev.design_contract or {})
        geometry = dict(contract.get("geometry") or {})
        geometry["geometry_id"] = scenario["geometry_id"]
        contract["geometry"] = geometry
        design_ev = DesignEvidence.from_dict({**design_ev.to_dict(), "design_contract": contract})
    if template == "scm_placebo_causal":
        return build_estimator_readout(
            design_evidence=design_ev,
            estimator_id="scm",
            inference_id="placebo",
            result_payload=scenario.get("native"),
            readout_semantics="causal_interval",
            interval_type="placebo_interval",
            enforce=enforce,
        )
    return build_estimator_readout(
        design_evidence=design_ev,
        estimator_id=scenario.get("estimator_id"),
        inference_id=scenario.get("inference_id"),
        result_payload=scenario.get("native"),
        readout_semantics=scenario.get("readout_semantics"),
        interval_type=scenario.get("interval_type"),
        cell_id=scenario.get("cell_id"),
        pooled=bool(scenario.get("pooled", False)),
        enforce=enforce,
    )


def _empirical(kind: str | None) -> TrustReportEmpiricalEvidence | None:
    if kind is None or kind == "missing":
        return None
    if kind == "scm_jk_full":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-SCM-JK-001",
            evidence_source="evidence_reused",
            coverage_null=0.93,
            coverage_positive=0.07,
            type_i_error=0.067,
            failure_rate=0.057,
            worst_world_status="post_shock_null",
            provenance_complete=True,
            freshness_status="valid",
            effect_scale=0.08,
            bias=8.59,
            dcm_row_id="DCM-001",
            trust_role_allowed_in_source=False,
        )
    if kind == "missing_coverage":
        return TrustReportEmpiricalEvidence(
            provenance_complete=True,
            freshness_status="valid",
            worst_world_status="evaluated",
        )
    if kind == "augsynth_point":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-AUGSYNTH-POINT-001",
            evidence_source="evidence_reused",
            provenance_complete=True,
            freshness_status="valid",
            worst_world_status="clean_null",
            failure_rate=0.057,
            dcm_row_id="DCM-002",
        )
    if kind == "did_bootstrap":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-DID-BOOTSTRAP-001",
            evidence_source="evidence_reused",
            coverage_null=1.0,
            coverage_positive=0.0,
            type_i_error=0.0,
            failure_rate=0.019,
            worst_world_status="clean_parallel_null",
            provenance_complete=True,
            freshness_status="valid",
            dcm_row_id="DCM-004",
        )
    if kind == "tbrridge_brb" or kind == "tbrridge_kfold":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-TBRRIDGE-INF-001",
            evidence_source="evidence_reused",
            coverage_null=1.0,
            type_i_error=0.0,
            failure_rate=0.0,
            worst_world_status="clean_null",
            provenance_complete=True,
            freshness_status="valid",
            dcm_row_id="DCM-005",
        )
    if kind == "tbrridge_placebo":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-TBRRIDGE-INF-001",
            evidence_source="evidence_reused",
            provenance_complete=True,
            freshness_status="valid",
            dcm_row_id="DCM-005",
        )
    if kind == "mcell":
        return TrustReportEmpiricalEvidence(
            artifact_id="D5-STAT-MCELL-PERCELL-001",
            evidence_source="evidence_reused",
            provenance_complete=True,
            freshness_status="valid",
            worst_world_status="clean_null",
            failure_rate=0.0,
            dcm_row_id="DCM-006",
        )
    if kind == "no_provenance":
        return TrustReportEmpiricalEvidence(
            coverage_null=0.93,
            freshness_status="valid",
            worst_world_status="clean_null",
            provenance_complete=False,
        )
    if kind == "stale":
        return TrustReportEmpiricalEvidence(
            coverage_null=0.93,
            provenance_complete=True,
            freshness_status="stale",
            worst_world_status="clean_null",
        )
    return None


def _build_scenario_readout(scenario: dict[str, Any]) -> Any:
    if scenario.get("native"):
        return scenario["native"]
    if scenario.get("readout") is not None:
        return scenario["readout"]
    template = scenario.get("template")
    if not template:
        return None
    enforce = template not in (
        "augsynth_interval",
        "multicell_pooled",
        "tbr_unit_panel",
        "scm_placebo_causal",
        "tbrridge_brb",
        "tbrridge_kfold",
        "tbrridge_placebo",
    )
    readout = _build_readout(template, enforce=enforce)
    if scenario.get("strip_boundary"):
        readout = ReadoutEvidence.from_dict(
            {**readout.to_dict(), "inference_boundary_guardrail": None}
        )
    if scenario.get("strip_shared_control"):
        payload = dict(readout.result_payload or {})
        meta = dict(payload.get("metadata") or {})
        geo = dict(meta.get("geometry_context") or {})
        geo.pop("shared_control_policy", None)
        geo.pop("control_reuse_policy", None)
        meta["geometry_context"] = geo
        payload["metadata"] = meta
        readout = ReadoutEvidence.from_dict(
            {**readout.to_dict(), "result_payload": payload}
        )
    return readout


@pytest.mark.parametrize("scenario", ELIG_SCENARIOS, ids=lambda s: s["fixture_id"])
def test_fixture_scenarios(scenario: dict[str, Any]) -> None:
    readout = _build_scenario_readout(scenario)
    empirical = _empirical(scenario.get("empirical"))
    result = evaluate_trustreport_eligibility(
        readout_evidence=readout,
        empirical_evidence=empirical,
    )
    assert result.trust_report_authorized is False
    assert result.status == scenario["expected_status"]


class TestEligibilityEvaluation:
    def test_governed_readout_required(self) -> None:
        result = evaluate_trustreport_eligibility(readout_evidence=None)
        assert result.status in (STATUS_INELIGIBLE, STATUS_UNKNOWN)
        assert result.trust_report_authorized is False

    def test_authorization_always_false(self) -> None:
        readout = _build_readout("scm_jk")
        result = evaluate_trustreport_eligibility(
            readout_evidence=readout,
            empirical_evidence=_empirical("scm_jk_full"),
        )
        assert result.trust_report_authorized is False

    def test_no_promotion_candidate_without_full_pass(self) -> None:
        readout = _build_readout("scm_jk")
        result = evaluate_trustreport_eligibility(
            readout_evidence=readout,
            empirical_evidence=_empirical("scm_jk_full"),
        )
        assert result.eligible_for_promotion is False
        assert result.status != STATUS_ELIGIBLE_CANDIDATE
        with pytest.raises(TrustReportEligibilityViolation):
            assert_trustreport_eligible_for_promotion(result)


class TestAuthorizationSeparation:
    def test_eligible_restricted_still_blocked_downstream(self) -> None:
        readout = _build_readout("scm_jk")
        elig = evaluate_trustreport_eligibility(
            readout_evidence=readout,
            empirical_evidence=_empirical("scm_jk_full"),
        )
        assert elig.status == STATUS_ELIGIBLE_WITH_RESTRICTIONS
        bundle = {"evidence": {"readout_evidence": readout.to_dict()}}
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert inputs.trust_report_ready is False
        assert inputs.downstream_authorization is not None
        assert inputs.downstream_authorization["authorized"] is False
        assert inputs.trustreport_eligibility is not None
        assert inputs.trust_report_promotion_candidate is False


class TestSerialization:
    def test_result_serializes(self) -> None:
        readout = _build_readout("scm_jk")
        result = evaluate_trustreport_eligibility(
            readout_evidence=readout,
            empirical_evidence=_empirical("scm_jk_full"),
        )
        payload = result.to_dict()
        roundtrip = json.loads(json.dumps(payload))
        assert roundtrip["eligibility_version"] == ELIGIBILITY_VERSION
        assert roundtrip["trust_report_authorized"] is False


class TestSecurity:
    def test_no_bypass_parameters(self) -> None:
        src = inspect.getsource(evaluate_trustreport_eligibility)
        assert "override_eligibility" not in src
        assert "bypass_eligibility" not in src
        assert "ignore_eligibility" not in src
