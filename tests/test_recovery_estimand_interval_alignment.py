"""Recovery interval estimand alignment vs scored relative_att_post point estimand."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.methods.DID import DID
from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.did_interval_policy import (
    DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
)
from panel_exp.validation.recovery_intervals import (
    INTERVAL_ESTIMAND_CUMULATIVE_ATT,
    INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
    PATH_INTERVAL_BOUNDS_INVERTED,
    POINT_ESTIMAND,
    extract_recovery_interval,
)
from panel_exp.validation.nominal_calibration import is_nominal_calibration_eligible_config
from panel_exp.methods.tbr import TBRRidge
from panel_exp.validation.recovery_metrics import (
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.runner import _path_relative_att
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld


def _panel(n_units: int = 10, n_periods: int = 30, seed: int = 0) -> PanelDataset:
    wide = np.random.default_rng(seed).normal(100, 5, size=(n_units, n_periods))
    wide = np.asarray(wide, dtype=float)
    import pandas as pd

    df = pd.DataFrame(
        wide,
        index=[f"u{i}" for i in range(n_units)],
        columns=pd.date_range("2020-01-01", periods=n_periods, freq="W"),
    )
    t0 = n_periods - 5
    return PanelDataset(
        df,
        treated_periods=[TimePeriod(df.columns[t0], df.columns[-1])],
        treated_units=["u0"],
    )


class _MockPathIntervalEstimator:
    """Aligned path relative intervals bracketing the point estimand."""

    def __init__(self, y, y_hat, rel_effect: float = 0.05):
        y = np.asarray(y, dtype=float).ravel()
        y_hat = np.asarray(y_hat, dtype=float).ravel()
        eff = rel_effect * y_hat
        self.results = {
            "y": y,
            "y_hat": y_hat,
            "y_lower": y_hat + eff - 0.01,
            "y_upper": y_hat + eff + 0.01,
        }


def test_extract_path_interval_declares_relative_att_post():
    panel = _panel()
    y = panel.treated_series(["u0"]).values.T.flatten()
    y_hat = panel.control_series(["u0"]).values.T.mean(axis=1)
    est = _MockPathIntervalEstimator(y, y_hat, rel_effect=0.04)
    ext = extract_recovery_interval(
        est,
        panel,
        alpha=0.05,
        significance_from_ci=True,
        supports_significance=True,
    )
    assert ext.point_estimand == POINT_ESTIMAND
    assert ext.interval_estimand == INTERVAL_ESTIMAND_RELATIVE_ATT_POST
    assert ext.interval_scale == "path_period_relative_mean"
    assert ext.interval_aligned is True
    assert ext.ci_lower is not None and ext.ci_upper is not None


def test_did_bootstrap_interval_marked_mismatch():
    panel = _panel(n_units=8)
    did = DID()
    did.n_bootstrap = 20
    did.run_analysis(panel, multiple_treated="pooled")
    ext = extract_recovery_interval(
        did,
        panel,
        alpha=0.05,
        significance_from_ci=False,
        supports_significance=True,
    )
    assert ext.point_estimand == POINT_ESTIMAND
    assert ext.interval_estimand == INTERVAL_ESTIMAND_CUMULATIVE_ATT
    assert ext.interval_aligned is False
    assert ext.unavailable_reason == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    assert ext.ci_lower is None and ext.ci_upper is None
    assert ext.significance_aligned is False


def test_aggregate_coverage_skips_mismatched_intervals():
    records = [
        SimulationRecord(
            predicted_effect=0.0,
            true_effect=0.0,
            ci_lower=-0.05,
            ci_upper=0.05,
            interval_aligned=True,
            point_estimand=POINT_ESTIMAND,
            interval_estimand=INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
            interval_scale="path_period_relative_mean",
            significance_aligned=True,
            significant=False,
        ),
        SimulationRecord(
            predicted_effect=0.0,
            true_effect=0.0,
            ci_lower=None,
            ci_upper=None,
            interval_aligned=False,
            intervals_unavailable_reason="interval_estimand_mismatch",
            point_estimand=POINT_ESTIMAND,
            interval_estimand=INTERVAL_ESTIMAND_CUMULATIVE_ATT,
            significance_aligned=False,
            significant=True,
        ),
    ]
    out = aggregate_recovery_metrics(
        estimator="DID_Bootstrap",
        scenario="recovery_null_effect",
        records=records,
        intervals_expected=True,
    )
    assert out.coverage == pytest.approx(1.0)
    assert out.coverage_status == "computed"
    assert out.false_positive_rate == pytest.approx(0.0)
    assert out.false_positive_rate_status == "computed"


def test_recovery_runner_payload_includes_estimand_metadata():
    scenario = SyntheticScenario(
        name="align_meta",
        n_geos=10,
        n_periods=36,
        treatment_start=28,
        true_effect=0.06,
        random_state=3,
    )
    payload = RecoveryRunner(
        "SCM",
        scenario,
        n_simulations=1,
        random_state=3,
    ).run()
    assert payload["point_estimand"] == POINT_ESTIMAND
    assert "interval_estimand" in payload
    assert "interval_scale" in payload


def test_did_inference_recovery_coverage_unavailable_not_fake_relative():
    payload = RecoveryRunner(
        "DID_Bootstrap",
        "recovery_null_effect",
        n_simulations=2,
        random_state=11,
    ).run()
    assert payload["point_estimand"] == POINT_ESTIMAND
    assert payload["interval_estimand"] == INTERVAL_ESTIMAND_CUMULATIVE_ATT
    assert payload["coverage_status"] == "unavailable"
    assert DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED in (
        payload["coverage_unavailable_reason"] or ""
    )


def test_point_estimate_recovery_unchanged():
    scenario = SyntheticScenario(
        name="pe",
        n_geos=10,
        n_periods=32,
        treatment_start=26,
        true_effect=0.07,
        random_state=1,
    )
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    pred = _path_relative_att(scm, panel)
    assert np.isfinite(pred)
    assert "estimator_diagnostics" not in scm.results


class _MockInvertedOutcomeBounds:
    """Outcome-level y_lower > y_upper (pre-fix BRB mapping)."""

    def __init__(self, y, y_hat, gap: float = 0.05):
        y = np.asarray(y, dtype=float).ravel()
        y_hat = np.asarray(y_hat, dtype=float).ravel()
        self.results = {
            "y": y,
            "y_hat": y_hat,
            "y_lower": y_hat + gap,
            "y_upper": y_hat - gap,
        }


def test_inverted_outcome_bounds_mark_unavailable_no_significance():
    panel = _panel()
    y = panel.treated_series(["u0"]).values.T.flatten()
    y_hat = panel.control_series(["u0"]).values.T.mean(axis=1)
    est = _MockInvertedOutcomeBounds(y, y_hat)
    ext = extract_recovery_interval(
        est,
        panel,
        alpha=0.05,
        significance_from_ci=True,
        supports_significance=True,
    )
    assert ext.interval_aligned is False
    assert ext.unavailable_reason == PATH_INTERVAL_BOUNDS_INVERTED
    assert ext.ci_lower is None and ext.ci_upper is None
    assert ext.significant is None
    assert ext.significance_aligned is False


def test_tbrridge_brb_null_does_not_force_fpr_one():
    """After bound-ordering fix, BRB must not silently mark every null rep significant."""
    payload = RecoveryRunner(
        "TBRRidge_BlockResidualBootstrap",
        "recovery_null_effect",
        n_simulations=6,
        random_state=42,
    ).run()
    assert is_nominal_calibration_eligible_config("TBRRidge_BlockResidualBootstrap") is False
    assert payload["interval_estimand"] == INTERVAL_ESTIMAND_RELATIVE_ATT_POST
    if payload["false_positive_rate_status"] == "computed":
        assert payload["false_positive_rate"] < 1.0
    assert payload.get("coverage_unavailable_reason") != PATH_INTERVAL_BOUNDS_INVERTED


def test_tbrridge_brb_interval_ordering_when_aligned():
    scenario = SyntheticScenario(
        name="brb_order",
        n_geos=12,
        n_periods=40,
        treatment_start=28,
        true_effect=0.08,
        random_state=7,
    )
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    est = TBRRidge(inference="BlockResidualBootstrap", alpha=0.05)
    est.n_bootstrap = 20
    est.block_length = 5
    est.run_analysis(panel, show_progress=False, random_state=7)
    ext = extract_recovery_interval(
        est,
        panel,
        alpha=0.05,
        significance_from_ci=True,
        supports_significance=True,
    )
    if ext.interval_aligned:
        assert ext.ci_lower is not None and ext.ci_upper is not None
        assert ext.ci_lower <= ext.ci_upper
    else:
        assert ext.unavailable_reason == PATH_INTERVAL_BOUNDS_INVERTED


def test_scm_jackknife_interval_aligned_when_finite():
    payload = RecoveryRunner(
        "SCM_UnitJackKnife",
        "recovery_positive_effect",
        n_simulations=1,
        random_state=5,
    ).run()
    if payload["interval_estimand"] == INTERVAL_ESTIMAND_RELATIVE_ATT_POST:
        assert payload["interval_scale"] == "path_period_relative_mean"
        if payload["coverage_status"] == "computed":
            assert payload["coverage"] == payload["coverage"]
