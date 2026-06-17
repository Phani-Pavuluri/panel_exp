"""Tests for D5-DES-STAT-STRATIFIED-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.assign import StratifiedRandomization
from panel_exp.design.validation import standardized_mean_difference
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_stat_stratified_001 import (
    ARTIFACT_ID,
    POLICY_SPECS,
    WORLD_IDS,
    StratifiedHarnessConfig,
    _world_spec,
    build_d5_des_stat_stratified_001,
    synthesize_panel,
    write_artifact_atomic,
)

ALLOWED = {
    "stratified_feasibility_fixed_requires_statistical_followup",
    "stratified_feasibility_partially_fixed_with_restrictions",
    "stratified_infeasible_regimes_explicitly_blocked",
    "stratified_characterized_no_safe_fix",
    "stratified_harness_inconclusive",
    "stratified_harness_failed",
}


@pytest.fixture
def fast_cfg() -> StratifiedHarnessConfig:
    return StratifiedHarnessConfig(fast=True)


def _poor_strata_panel(seed: int = 101, n_units: int = 10) -> PanelDataset:
    import numpy as np
    import pandas as pd
    from panel_exp.panel_data import PanelDataset

    rng = np.random.default_rng(seed)
    n_pre, n_post = 30, 10
    units = [f"u{i}" for i in range(n_units)]
    rows = []
    for _ in range(n_units):
        level = rng.normal(100, 15)
        rows.append(
            np.concatenate([level + rng.normal(0, 2, n_pre), level + rng.normal(0, 2, n_post)])
        )
    wide = pd.DataFrame(rows, index=units, columns=list(range(n_pre + n_post)))
    return PanelDataset(wide.copy())


class TestStratifiedReproduction:
    def test_legacy_elevated_smd(self) -> None:
        panel = _poor_strata_panel(101)
        d = StratifiedRandomization(0.35, random_state=101, stratification_policy="legacy")
        a = d.assign(panel, n_percentiles=12)
        w = panel.wide_data
        smd = standardized_mean_difference(
            w.loc[a["control"], :30].mean(axis=1).values,
            w.loc[a["test_0"], :30].mean(axis=1).values,
        )
        assert smd > 0.7

    def test_adaptive_lower_smd(self) -> None:
        panel = _poor_strata_panel(101)
        d = StratifiedRandomization(0.35, random_state=101, stratification_policy="adaptive_strata")
        a = d.assign(panel, pre_treatment_period=TimePeriod(0, 30), n_percentiles=12)
        w = panel.wide_data
        smd = standardized_mean_difference(
            w.loc[a["control"], :30].mean(axis=1).values,
            w.loc[a["test_0"], :30].mean(axis=1).values,
        )
        assert smd < 0.6
        assert d.last_stratification_metadata["realized_n_strata"] < 12

    def test_deterministic_seed(self) -> None:
        panel = _poor_strata_panel(404)
        kw = dict(treatment_probability=0.35, random_state=404, stratification_policy="adaptive_strata")
        a1 = StratifiedRandomization(**kw).assign(
            panel, pre_treatment_period=TimePeriod(0, 30), n_percentiles=8
        )
        a2 = StratifiedRandomization(**kw).assign(
            panel, pre_treatment_period=TimePeriod(0, 30), n_percentiles=8
        )
        assert {k: sorted(v) for k, v in a1.items()} == {k: sorted(v) for k, v in a2.items()}


class TestStratifiedHarness:
    def test_schema(self, fast_cfg: StratifiedHarnessConfig) -> None:
        p = build_d5_des_stat_stratified_001(fast_cfg)
        assert p["artifact_id"] == ARTIFACT_ID
        assert p["verdict"] in ALLOWED
        for k in (
            "run_records",
            "aggregate_results",
            "policy_comparisons",
            "failure_summary",
            "strata_summary",
            "balance_summary",
            "selected_policy",
        ):
            assert k in p

    def test_policies_worlds(self, fast_cfg: StratifiedHarnessConfig) -> None:
        p = build_d5_des_stat_stratified_001(fast_cfg)
        assert {r["policy"] for r in p["run_records"]} == {x[1] for x in POLICY_SPECS}
        assert {r["world_id"] for r in p["run_records"]} >= set(WORLD_IDS[:4])

    def test_failed_preserved(self, fast_cfg: StratifiedHarnessConfig) -> None:
        p = build_d5_des_stat_stratified_001(fast_cfg)
        assert p["runtime"]["failed_runs"] == sum(
            1 for r in p["run_records"] if r["assignment_status"] == "failed"
        )

    def test_atomic_write(self, fast_cfg: StratifiedHarnessConfig, tmp_path: Path) -> None:
        p = build_d5_des_stat_stratified_001(fast_cfg)
        out = tmp_path / "a.json"
        write_artifact_atomic(out, p)
        assert json.loads(out.read_text())["artifact_id"] == ARTIFACT_ID

    def test_generated_archive_roundtrip(self, fast_cfg: StratifiedHarnessConfig, tmp_path: Path) -> None:
        payload = build_d5_des_stat_stratified_001(fast_cfg)
        out = tmp_path / "D5_DES_STAT_STRATIFIED_001_results.json"
        write_artifact_atomic(out, payload, overwrite=False)
        loaded = json.loads(out.read_text())
        assert loaded["artifact_id"] == ARTIFACT_ID
        assert loaded["verdict"] in ALLOWED
        assert len(loaded["run_records"]) > 0
        assert loaded["runtime"]["failed_runs"] == sum(
            1 for r in loaded["run_records"] if r["assignment_status"] == "failed"
        )
        assert any(r["policy"] == "legacy" for r in loaded["run_records"])
        assert loaded["failure_summary"]["n_assignment_failures"] >= 0
