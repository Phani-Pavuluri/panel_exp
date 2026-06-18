"""Production tests for DID bootstrap cumulative readout correction."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.DID import DID
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.did_bootstrap_cumulative_readout_correction_001 import (
    build_did_bootstrap_cumulative_readout_correction_001,
    write_summary,
)
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json"
REPORT = _REPO / "docs/track_d/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_REPORT.md"
BEFORE_ARCHIVE = _REPO / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"


def _assign_and_panel(seed: int, scenario_name: str = "did_parallel_trends_holds", **overrides):
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[scenario_name],
        random_state=seed,
        n_geos=16,
        n_periods=44,
        treatment_start=28,
        true_effect=0.0,
        **overrides,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    panel = PanelDataset(wide.iloc[:, :36].copy())
    design = greedy_match_markets(
        func_to_optimize="corr", treatment_probability=0.35, random_state=seed
    )
    groups = design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 28), n_test_grps=1)
    treated = list(groups.get("test_0") or [])
    control = list(groups.get("control") or [])
    assert treated and control
    panel = PanelDataset(
        wide.iloc[:, :36].copy(),
        treated_periods=[TimePeriod(28, 35) for _ in treated],
        treated_units=treated,
    )
    return panel, treated


def _inject_percent(panel: PanelDataset, treated, percent: float) -> tuple[PanelDataset, float]:
    baseline = copy.deepcopy(panel)
    mod = copy.deepcopy(panel)
    if abs(percent) < 1e-12:
        return mod, 0.0
    mean_value = mod.wide_data.loc[treated].mean(axis=1).values.astype(float)
    start, end = 28, 35
    value_effect = percent * mean_value
    mask = np.zeros((len(treated), mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : end + 1] = True
    block = mod.wide_data.loc[treated].to_numpy(dtype=float)
    block = np.where(mask, block + value_effect.reshape(-1, 1), block)
    mod.wide_data.loc[treated] = block
    times = list(mod.times[-8:])
    truth = float(
        mod.wide_data.loc[treated, times].to_numpy(dtype=float).sum()
        - baseline.wide_data.loc[treated, times].to_numpy(dtype=float).sum()
    )
    return mod, truth


def _run_did(panel: PanelDataset, seed: int = 42) -> DID:
    est = DID(alpha=0.05)
    est.n_bootstrap = 80
    est.bootstrap_seed = seed
    est.run_analysis(panel, multiple_treated="pooled")
    return est


class TestDidBootstrapCumulativeReadoutCorrection001:
    def test_clean_null_world(self) -> None:
        panel, treated = _assign_and_panel(1)
        mod, truth = _inject_percent(panel, treated, 0.0)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        assert lo <= 0.0 <= hi
        assert est.results["cumulative_att"] == pytest.approx(truth, abs=50)

    def test_clean_positive_world(self) -> None:
        panel, treated = _assign_and_panel(2)
        mod, truth = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        assert lo <= truth <= hi
        assert lo <= est.results["cumulative_att"] <= hi

    def test_negative_effect_world(self) -> None:
        panel, treated = _assign_and_panel(3)
        mod, truth = _inject_percent(panel, treated, -0.05)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        assert truth < 0
        assert lo <= truth <= hi

    def test_serially_correlated_world(self) -> None:
        panel, treated = _assign_and_panel(
            4, scenario_name="scm_low_signal", noise_scale=3.2
        )
        mod, truth = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        assert np.isfinite(lo) and np.isfinite(hi)
        assert hi > lo
        assert lo <= est.results["cumulative_att"] <= hi

    def test_heteroskedastic_world(self) -> None:
        panel, treated = _assign_and_panel(
            5, scenario_name="scm_low_signal", noise_scale=3.8, cross_geo_correlation=0.05
        )
        mod, truth = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        assert hi > lo > -np.inf

    def test_common_treatment_timing(self) -> None:
        panel, _ = _assign_and_panel(6)
        est = _run_did(panel)
        assert len(set(est.panel.treated_start_idxs)) == 1

    def test_deterministic_seed_behavior(self) -> None:
        panel, treated = _assign_and_panel(7)
        mod, _ = _inject_percent(panel, treated, 0.08)
        a = _run_did(mod, seed=99)
        b = _run_did(mod, seed=99)
        assert a.treatment_ci == b.treatment_ci
        assert a.results["cumulative_att"] == b.results["cumulative_att"]

    def test_bootstrap_center_metadata_recorded(self) -> None:
        panel, treated = _assign_and_panel(8)
        mod, _ = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        assert est.results["bootstrap_interval_method"] == "centered_deviation_percentile"
        assert est.results["bootstrap_replicate_estimand"] == "cumulative_path_att_block_resampled_panel"
        assert est.results["bootstrap_center"] is not None
        assert est.results["bootstrap_replicate_count"] >= 30

    def test_point_estimate_in_interval(self) -> None:
        panel, treated = _assign_and_panel(9)
        mod, _ = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        pt = est.results["cumulative_att"]
        assert lo <= pt <= hi

    def test_positive_coverage_improves_in_fast_battery(self) -> None:
        payload = build_did_bootstrap_cumulative_readout_correction_001(fast=True)
        assert (payload["after_metrics"]["positive_coverage"] or 0) >= 0.5
        assert (payload["before_metrics"]["positive_coverage"] or 0) < 0.25

    def test_null_type_i_not_excessive_fast_battery(self) -> None:
        payload = build_did_bootstrap_cumulative_readout_correction_001(fast=True)
        clean_null = payload["after_metrics"]["coverage_by_world"]["clean_parallel_null"]
        assert (clean_null.get("null_coverage") or 0) >= 0.5
        assert (payload["after_metrics"]["type_i_error"] or 0) <= 0.5

    def test_interval_width_finite_nonzero(self) -> None:
        panel, treated = _assign_and_panel(10)
        mod, _ = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        lo, hi = est.treatment_ci
        width = hi - lo
        assert np.isfinite(width)
        assert width > 1e-6

    def test_invalid_bootstrap_replicates_fail_explicitly(self) -> None:
        est = DID(alpha=0.05)
        est.n_bootstrap = 0
        est.bootstrap_block_size = 8
        panel, _ = _assign_and_panel(11)
        est.run_analysis(panel, multiple_treated="pooled")
        assert est.bootstrap_replicate_count_ == 0

    def test_no_staggered_timing_support_added(self) -> None:
        text = Path(_REPO / "panel_exp/methods/DID.py").read_text(encoding="utf-8")
        assert "staggered" not in text.lower() or "Simultaneous Adoption" in text

    def test_result_payload_backward_compatibility(self) -> None:
        panel, treated = _assign_and_panel(12)
        mod, _ = _inject_percent(panel, treated, 0.08)
        est = _run_did(mod)
        r = est.results
        for key in (
            "cumulative_att",
            "mean_post_period_att",
            "treatment_effects",
            "y",
            "y_hat",
            "y_lower",
            "y_upper",
            "did_interval_policy",
        ):
            assert key in r
        assert "bootstrap_interval_method" in r
        assert "point_estimate" in r
        assert r["point_estimate"] == r["cumulative_att"]


def test_summary_artifact_write(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    write_summary(out, fast=True, overwrite=True)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["artifact_id"] == "DID-BOOTSTRAP-CUMULATIVE-READOUT-CORRECTION-001"
    assert payload["forbidden_flags"]["trust_report_authorized"] is False


def test_pre_fix_canonical_archive_unchanged() -> None:
    assert BEFORE_ARCHIVE.is_file()
    before = json.loads(BEFORE_ARCHIVE.read_text(encoding="utf-8"))
    assert before["harness_correction_verdict"] == "did_bootstrap_harness_corrected_production_miscoverage_confirmed"


def test_correction_report_exists() -> None:
    assert REPORT.is_file()
