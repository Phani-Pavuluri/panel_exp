"""Tests for SCM/AugSynth diagnostic helpers (D5-DIAG-SCM-AUGSYNTH-001)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.scm_augsynth_diagnostics import (
    CONFLICT_DIAGNOSTIC_FIELDS,
    INSTRUMENT_DIAGNOSTIC_FIELDS,
    PANEL_DIAGNOSTIC_FIELDS,
    compute_instrument_diagnostics,
    compute_method_disagreement,
    false_confidence_flag,
    hull_min_donor_z_distance,
    narrow_interval_poor_fit_flag,
    normalized_pre_period_error,
    pre_period_rmse,
    relative_fit_improvement,
    scale_bridge_pre_std_ratio,
    treated_pre_period_std,
    weight_diagnostics,
)


def _make_panel(n_control: int = 8, n_pre: int = 10) -> PanelDataset:
    rng = np.random.default_rng(0)
    control = [f"c{i}" for i in range(n_control)]
    treated = ["t0"]
    n_cols = n_pre + 3
    rows = {u: rng.normal(0, 1, n_cols) for u in control}
    rows["t0"] = rng.normal(0.5, 1.2, n_cols)
    wide = pd.DataFrame(rows).T
    return PanelDataset(
        wide,
        treated_units=treated,
        treated_periods=[TimePeriod(n_pre, n_cols - 1)],
    )


class TestPrePeriodRmse:
    def test_perfect_fit_is_zero(self) -> None:
        y = np.array([1.0, 2.0, 3.0, 4.0])
        results = {"y": y, "y_hat": y.copy()}
        assert pre_period_rmse(results, 4) == pytest.approx(0.0)

    def test_known_rmse(self) -> None:
        y = np.array([0.0, 0.0])
        y_hat = np.array([3.0, 4.0])
        results = {"y": y, "y_hat": y_hat}
        assert pre_period_rmse(results, 2) == pytest.approx(3.5355339, rel=1e-5)

    def test_normalized_error(self) -> None:
        panel = _make_panel()
        y = panel.wide_data.loc["t0"].values.astype(float)
        results = {"y": y, "y_hat": y.copy()}
        assert normalized_pre_period_error(results, 10, panel) == pytest.approx(0.0)


class TestWeightDiagnostics:
    def test_uniform_weights(self) -> None:
        w = np.array([0.25, 0.25, 0.25, 0.25])
        diag = weight_diagnostics(w)
        assert diag["weight_herfindahl"] == pytest.approx(0.25)
        assert diag["effective_donor_count"] == pytest.approx(4.0)
        assert diag["max_weight"] == pytest.approx(0.25)
        assert diag["n_negative_weights"] == 0.0

    def test_missing_weights_returns_nan(self) -> None:
        diag = weight_diagnostics(None)
        assert np.isnan(diag["weight_herfindahl"])
        assert np.isnan(diag["effective_donor_count"])
        assert np.isnan(diag["max_weight"])

    def test_concentrated_weights(self) -> None:
        w = np.array([0.9, 0.05, 0.05])
        diag = weight_diagnostics(w)
        assert diag["effective_donor_count"] == pytest.approx(1.0 / np.sum((w / w.sum()) ** 2))


class TestScaleBridge:
    def test_scale_ratio_computed(self) -> None:
        panel = _make_panel()
        w = np.ones(len(panel.control_units)) / len(panel.control_units)
        bridge = scale_bridge_pre_std_ratio(panel, 10, scm_weights=w)
        assert np.isfinite(bridge["treated_pre_period_std"])
        assert np.isfinite(bridge["donor_weighted_pre_period_std"])
        assert np.isfinite(bridge["scale_bridge_ratio"])

    def test_missing_weights_use_uniform_donor_mean(self) -> None:
        panel = _make_panel()
        bridge = scale_bridge_pre_std_ratio(panel, 10, scm_weights=None)
        assert np.isfinite(bridge["scale_bridge_ratio"])


class TestHullStress:
    def test_hull_distance_non_negative(self) -> None:
        panel = _make_panel()
        dist = hull_min_donor_z_distance(panel, 10)
        assert np.isfinite(dist)
        assert dist >= 0.0


class TestMethodDisagreement:
    def test_sign_disagreement(self) -> None:
        conflict = compute_method_disagreement(
            {"mean_point_effect": 0.1},
            {"mean_point_effect": -0.2, "feasible": 1.0},
            material_point_mismatch_threshold=0.05,
        )
        assert conflict["null_sign_disagreement"] == 1.0
        assert conflict["null_material_point_mismatch"] == 1.0
        assert set(conflict) == set(CONFLICT_DIAGNOSTIC_FIELDS)

    def test_infeasible_returns_nan(self) -> None:
        conflict = compute_method_disagreement(
            {"mean_point_effect": 0.1},
            {"feasible": 0.0},
            material_point_mismatch_threshold=0.05,
        )
        assert np.isnan(conflict["null_sign_disagreement"])


class TestFalseConfidence:
    def test_flags_large_point_with_poor_fit_and_hull_stress(self) -> None:
        panel_diag = {"scm_pre_rmse": 1.5, "hull_min_donor_z_distance": 3.0}
        inst = {"mean_point_effect": 0.12, "feasible": 1.0}
        assert false_confidence_flag(inst, panel_diag) == 1.0

    def test_small_point_not_flagged(self) -> None:
        panel_diag = {"scm_pre_rmse": 2.0, "hull_min_donor_z_distance": 4.0}
        inst = {"mean_point_effect": 0.01, "feasible": 1.0}
        assert false_confidence_flag(inst, panel_diag) == 0.0


class TestNarrowIntervalPoorFit:
    def test_narrow_interval_with_poor_fit(self) -> None:
        panel_diag = {"scm_pre_rmse": 1.2, "hull_min_donor_z_distance": 1.0}
        inst = {
            "mean_point_effect": 0.2,
            "mean_interval_halfwidth": 0.01,
            "feasible": 1.0,
        }
        assert narrow_interval_poor_fit_flag(inst, panel_diag) == 1.0

    def test_no_interval_returns_zero(self) -> None:
        panel_diag = {"scm_pre_rmse": 2.0, "hull_min_donor_z_distance": 4.0}
        inst = {"mean_point_effect": 0.2, "feasible": 1.0}
        assert narrow_interval_poor_fit_flag(inst, panel_diag) == 0.0


class TestInstrumentDiagnostics:
    def test_fields_present(self) -> None:
        panel_diag = {"scm_pre_rmse": 1.5, "hull_min_donor_z_distance": 3.0}
        inst = {
            "mean_point_effect": 0.12,
            "mean_jk_halfwidth": 0.01,
            "feasible": 1.0,
        }
        out = compute_instrument_diagnostics(inst, panel_diag)
        assert set(out) == set(INSTRUMENT_DIAGNOSTIC_FIELDS)


class TestRelativeImprovement:
    def test_relative_improvement(self) -> None:
        assert relative_fit_improvement(2.0, 1.0) == pytest.approx(0.5)

    def test_invalid_denominator(self) -> None:
        assert np.isnan(relative_fit_improvement(float("nan"), 1.0))


class TestPanelFieldCatalog:
    def test_panel_field_names_stable(self) -> None:
        assert "scm_pre_rmse_normalized" in PANEL_DIAGNOSTIC_FIELDS
        assert "scale_bridge_ratio" in PANEL_DIAGNOSTIC_FIELDS
        assert "outcome_model_alpha" in PANEL_DIAGNOSTIC_FIELDS
        assert "effective_donor_count" in PANEL_DIAGNOSTIC_FIELDS
