"""Production tests for StratifiedRandomization feasibility fix (DES-004)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.design.assign import CompleteRandomization, StratifiedRandomization
from panel_exp.design.stratified_feasibility import compute_stratified_feasibility
from panel_exp.design.validation import standardized_mean_difference
from panel_exp.panel_data import PanelDataset, TimePeriod


def _poor_strata_panel(seed: int = 101, n_units: int = 10) -> PanelDataset:
    rng = np.random.default_rng(seed)
    n_pre, n_post = 30, 10
    units = [f"u{i}" for i in range(n_units)]
    rows = []
    for i in range(n_units):
        level = rng.normal(100, 15)
        rows.append(
            np.concatenate([level + rng.normal(0, 2, n_pre), level + rng.normal(0, 2, n_post)])
        )
    wide = pd.DataFrame(rows, index=units, columns=list(range(n_pre + n_post)))
    return PanelDataset(wide.copy())


def test_default_policy_is_adaptive_strata() -> None:
    design = StratifiedRandomization()
    assert design.stratification_policy == "adaptive_strata"
    assert design.min_units_per_stratum == 2


def test_compute_stratified_feasibility_max_strata() -> None:
    c = compute_stratified_feasibility(
        n_eligible=12, requested_n_strata=12, min_units_per_stratum=2, policy="adaptive_strata"
    )
    assert c.max_feasible_n_strata == 6
    assert c.realized_n_strata == 6


def test_legacy_reproduces_elevated_smd() -> None:
    panel = _poor_strata_panel(101)
    design = StratifiedRandomization(
        treatment_probability=0.35, random_state=101, stratification_policy="legacy"
    )
    # Legacy stratifies on full-panel mean (tier-1 path); evaluate balance on pre-period.
    a = design.assign(panel, n_test_grps=1, n_percentiles=12)
    wide = panel.wide_data
    smd = standardized_mean_difference(
        wide.loc[a["control"], :30].mean(axis=1).values,
        wide.loc[a["test_0"], :30].mean(axis=1).values,
    )
    assert smd > 0.7
    assert design.last_stratification_metadata is None


def test_adaptive_reduces_smd_and_preserves_strata() -> None:
    panel = _poor_strata_panel(101)
    pre = TimePeriod(0, 30)
    design = StratifiedRandomization(
        treatment_probability=0.35, random_state=101, stratification_policy="adaptive_strata"
    )
    a = design.assign(panel, pre_treatment_period=pre, n_test_grps=1, n_percentiles=12)
    wide = panel.wide_data
    smd = standardized_mean_difference(
        wide.loc[a["control"], :30].mean(axis=1).values,
        wide.loc[a["test_0"], :30].mean(axis=1).values,
    )
    assert smd < 0.5
    meta = design.last_stratification_metadata
    assert meta is not None
    assert meta["requested_n_strata"] == 12
    assert meta["realized_n_strata"] <= 6
    assert all(v >= 2 for v in meta["stratum_sizes"].values())


def test_no_stratum_lacks_both_arms_when_size_ge_2() -> None:
    panel = _poor_strata_panel(202)
    pre = TimePeriod(0, 30)
    design = StratifiedRandomization(
        treatment_probability=0.35, random_state=202, stratification_policy="adaptive_strata"
    )
    a = design.assign(panel, pre_treatment_period=pre, n_test_grps=1, n_percentiles=8)
    meta = design.last_stratification_metadata
    assert meta is not None
    unit_to_stratum = meta["unit_to_stratum_map"]
    for sid in meta["stratum_ids"]:
        units = [u for u, s in unit_to_stratum.items() if str(s) == sid]
        if len(units) < 2:
            continue
        has_ctrl = any(u in a["control"] for u in units)
        has_trt = any(u in a["test_0"] for u in units)
        assert has_ctrl and has_trt


def test_preflight_fail_rejects_infeasible() -> None:
    panel = _poor_strata_panel(303)
    design = StratifiedRandomization(
        treatment_probability=0.35,
        random_state=303,
        stratification_policy="preflight_fail",
    )
    with pytest.raises(ValueError, match="infeasible"):
        design.assign(
            panel,
            pre_treatment_period=TimePeriod(0, 30),
            n_test_grps=1,
            n_percentiles=12,
        )


def test_public_api_backward_compatible() -> None:
    panel = _poor_strata_panel(42)
    design = StratifiedRandomization(treatment_probability=0.5, random_state=42)
    result = design.assign(panel, n_test_grps=1, n_percentiles=4)
    assert isinstance(result, dict)
    assert "control" in result and "test_0" in result
