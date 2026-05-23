"""DID pretrend contract metadata and waiver behavior."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict

import numpy as np
import pandas as pd
import pytest

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.evidence import (
    ExperimentEvidence,
    attach_did_pretrend_contract,
)
from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.methods.DID import DID
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.synthetic_scenarios import get_recovery_scenario
from panel_exp.validation.synthetic_world import SyntheticWorld


def _run_did_on_scenario(scenario_name: str, *, allow_pretrend_violation: bool = False):
    scenario = get_recovery_scenario(scenario_name)
    world = SyntheticWorld.generate(replace(scenario, random_state=99))
    panel = world.to_panel_dataset()
    did = DID()
    did.run_analysis(
        panel,
        multiple_treated="pooled",
        allow_pretrend_violation=allow_pretrend_violation,
    )
    return did, world


def _panel_with_divergent_pre_trends() -> PanelDataset:
    """Hand-built panel: treated geos trend up in pre-period; controls flat."""
    n_periods = 36
    times = list(range(n_periods))
    t0 = 28
    rows = []
    for unit, slope in [("c0", 0.0), ("c1", 0.0), ("c2", 0.0), ("t0", 4.0), ("t1", 4.0)]:
        for t in times:
            base = 100.0 + slope * t
            rows.append({"geo": unit, "time": t, "outcome": base})
    wide = pd.DataFrame(rows).pivot(index="geo", columns="time", values="outcome")
    period = TimePeriod(t0, times[-1])
    return PanelDataset(
        wide,
        treated_periods=[period, period],
        treated_units=["t0", "t1"],
    )


def _fake_violating_event_study(self) -> Dict[str, Any]:
    return {
        "parallel_trends_test_type": "event_study_preperiod",
        "reference_pre_period": "t=-1",
        "pretrend_coefficients": {"t=-2": 2.0},
        "pretrend_standard_errors": {"t=-2": 0.5},
        "pretrend_pvalues": {"t=-2": 0.01},
        "parallel_trends_joint_pvalue": 0.01,
        "parallel_trends_violated": True,
        "largest_pretrend_deviation": 2.0,
        "largest_pretrend_period": "t=-2",
        "fallback_reason": None,
        "pretrend_binning_used": False,
        "n_pre_periods_original": 10,
        "n_pre_bins_used": 4,
        "parallel_trends_joint_pvalue_method": "f_test",
    }


def _fake_passing_linear(self) -> Dict[str, Any]:
    return {"parallel_trends_violated": False, "interaction_pvalue": 0.5}


def test_did_pretrend_contract_in_results():
    did, _ = _run_did_on_scenario("did_parallel_trends_holds")
    contract = did.results["did_pretrend_contract"]
    assert contract["pretrend_checked"] is True
    assert contract["pretrend_status"] in ("pass", "warn", "fail", "unavailable")
    assert "joint_pretrend_p_value" in contract
    assert "requires_waiver" in contract
    assert "waiver_provided" in contract


def test_violation_scenario_still_produces_estimate_and_contract():
    """Registry violation scenario stresses DGP; pretrend test may still pass."""
    did, _ = _run_did_on_scenario("did_parallel_trends_violation")
    contract = did.results["did_pretrend_contract"]
    assert np.isfinite(did.treatment_effect)
    assert contract["pretrend_checked"] is True
    assert contract["pretrend_status"] in ("pass", "warn", "fail", "unavailable")


def test_handbuilt_panel_triggers_fail_without_waiver():
    did = DID()
    did.run_analysis(_panel_with_divergent_pre_trends(), multiple_treated="pooled")
    contract = did.results["did_pretrend_contract"]
    assert contract["pretrend_status"] in ("fail", "warn")
    assert contract["requires_waiver"] is True


def test_mocked_violation_requires_waiver_without_flag(monkeypatch):
    monkeypatch.setattr(DID, "_run_event_study_pretrend_test", _fake_violating_event_study)
    monkeypatch.setattr(DID, "_run_linear_pretrend_test", _fake_passing_linear)
    did, _ = _run_did_on_scenario("did_parallel_trends_holds")
    contract = did.results["did_pretrend_contract"]
    assert contract["requires_waiver"] is True
    assert contract["waiver_provided"] is False
    assert contract["pretrend_status"] == "fail"


def test_mocked_violation_with_waiver(monkeypatch):
    monkeypatch.setattr(DID, "_run_event_study_pretrend_test", _fake_violating_event_study)
    monkeypatch.setattr(DID, "_run_linear_pretrend_test", _fake_passing_linear)
    did, _ = _run_did_on_scenario(
        "did_parallel_trends_holds",
        allow_pretrend_violation=True,
    )
    contract = did.results["did_pretrend_contract"]
    assert contract["waiver_provided"] is True
    assert contract["pretrend_status"] == "warn"


def test_mocked_violation_emits_warning_without_waiver(monkeypatch):
    monkeypatch.setattr(DID, "_run_event_study_pretrend_test", _fake_violating_event_study)
    monkeypatch.setattr(DID, "_run_linear_pretrend_test", _fake_passing_linear)
    with pytest.warns(UserWarning, match="should not be interpreted as credible"):
        _run_did_on_scenario("did_parallel_trends_holds")


def test_coefficients_unchanged_by_waiver_flag():
    panel = _panel_with_divergent_pre_trends()
    d1 = DID()
    d1.run_analysis(panel, multiple_treated="pooled", allow_pretrend_violation=False)
    d2 = DID()
    d2.run_analysis(panel, multiple_treated="pooled", allow_pretrend_violation=True)
    assert d1.treatment_effect == pytest.approx(d2.treatment_effect)
    assert d1.cumulative_att == pytest.approx(d2.cumulative_att)


def test_get_detailed_results_includes_contract():
    did, _ = _run_did_on_scenario("did_parallel_trends_holds")
    detailed = did.get_detailed_results()
    assert "did_pretrend_contract" in detailed
    assert detailed["did_pretrend_contract"]["pretrend_status"] == did.results[
        "did_pretrend_contract"
    ]["pretrend_status"]


def test_experiment_card_renders_pretrend_section(monkeypatch):
    monkeypatch.setattr(DID, "_run_event_study_pretrend_test", _fake_violating_event_study)
    monkeypatch.setattr(DID, "_run_linear_pretrend_test", _fake_passing_linear)
    did, _ = _run_did_on_scenario("did_parallel_trends_violation")
    contract = did.results["did_pretrend_contract"]
    artifacts: Dict[str, Any] = {}
    attach_did_pretrend_contract(artifacts, contract)
    spec = spec_from_geo_design(
        "did-pretrend-1",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
    )
    ir = InferenceResult.for_path_intervals(
        method="point_estimate",
        alpha=0.05,
        path_interval_type=IntervalType.UNAVAILABLE,
    )
    evidence = ExperimentEvidence.build(
        spec,
        {"control": ("a",), "test_0": ("b",)},
        validation_summary={},
        inference_result=ir,
        inference_method="point_estimate",
        artifacts=artifacts,
        created_at="2026-01-01T00:00:00+00:00",
    )
    md = build_experiment_card(evidence).to_markdown()
    assert "## DID Pretrend Contract" in md
    assert "Requires waiver" in md
    assert "parallel trends" in md.lower()


def test_recovery_runner_did_violation_scenario_completes():
    payload = RecoveryRunner(
        "DID",
        "did_parallel_trends_violation",
        n_simulations=1,
        random_state=3,
    ).run()
    assert payload["n_simulations"] == 1
    assert np.isfinite(payload["bias"]) or payload["bias"] != payload["bias"]
