"""Production tests for TBRRIDGE_BRB_INTERVAL_CORRECTION_001."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

from panel_exp.methods.tbr import TBRRidge
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    DIAGNOSTIC_WORLDS,
    BrbTrustConfig,
    _build_unit_panel,
    _inject_percent_effect,
    _level_true_effect,
    _mean_treated_baseline,
    _readout_level_scale,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json"


def _run_brb(spec, seed: int = 42, **kwargs):
    cfg = BrbTrustConfig(fast=True)
    panel = _build_unit_panel(spec, cfg, seed=seed)
    mean_val = _mean_treated_baseline(panel)
    pct = spec.percent_effect
    pds = _inject_percent_effect(panel, pct, mean_val)
    est = TBRRidge(inference="BlockResidualBootstrap", alpha=0.05)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        est.run_analysis(
            pds,
            n_bootstrap=30,
            block_length=kwargs.get("block_length", 3),
            min_train_periods=5,
            show_progress=False,
            random_state=seed,
            **{k: v for k, v in kwargs.items() if k != "block_length"},
        )
    true_level = _level_true_effect(pct, mean_val)
    readout = _readout_level_scale(
        est.results,
        test_len=8,
        true_effect_level=true_level,
        brb_stats=est.results.get("block_residual_bootstrap_stats"),
    )
    return est, readout, true_level


def test_bootstrap_center_near_point_clean_positive():
    _, readout, _ = _run_brb(DIAGNOSTIC_WORLDS[1])
    brb = readout  # stats merged in readout from results - get from est
    est, r, _ = _run_brb(DIAGNOSTIC_WORLDS[1])
    brb_stats = est.results["block_residual_bootstrap_stats"]
    gap = abs(brb_stats["bootstrap_center_minus_point"])
    assert gap < 0.5
    assert brb_stats["bootstrap_interval_method"] == "centered_deviation_percentile_mean_effect"
    assert brb_stats["bootstrap_replicate_estimand"] == "post_window_mean_effect_level"


def test_point_estimate_unchanged_by_interval_fix():
    est1, r1, _ = _run_brb(DIAGNOSTIC_WORLDS[1], seed=7)
    point = r1["point_estimate"]
    assert np.isfinite(point)


def test_clean_null_finite_interval():
    est, r, _ = _run_brb(DIAGNOSTIC_WORLDS[0])
    assert r["interval_width"] is not None and r["interval_width"] > 0
    assert r["finite_outputs"]


def test_clean_negative_characterized():
    est, r, true = _run_brb(DIAGNOSTIC_WORLDS[2])
    assert true < 0
    assert r["point_estimate"] is not None


def test_interval_contains_point_clean_positive():
    est, r, _ = _run_brb(DIAGNOSTIC_WORLDS[1], seed=42)
    pe = r["point_estimate"]
    assert r["interval_lower"] <= pe <= r["interval_upper"]


def test_deterministic_seeds():
    _, r1, _ = _run_brb(DIAGNOSTIC_WORLDS[1], seed=99)
    _, r2, _ = _run_brb(DIAGNOSTIC_WORLDS[1], seed=99)
    assert r1["point_estimate"] == r2["point_estimate"]
    assert r1["interval_lower"] == r2["interval_lower"]


def test_block_length_sweep():
    for bl in (2, 3, 7):
        est, r, _ = _run_brb(DIAGNOSTIC_WORLDS[1], seed=11, block_length=bl)
        assert r["finite_outputs"]
        assert est.results["block_residual_bootstrap_stats"]["block_length"] == bl


def test_backward_compatible_result_keys():
    est, _, _ = _run_brb(DIAGNOSTIC_WORLDS[1])
    res = est.results
    for key in (
        "y",
        "y_hat",
        "y_lower",
        "y_upper",
        "block_residual_bootstrap_stats",
        "effect_cumulative_brb",
        "effect_mean_brb",
        "bootstrap_interval_method",
    ):
        assert key in res


def test_serial_correlation_world_runs():
    spec = next(w for w in DIAGNOSTIC_WORLDS if w.world_id == "serial_correlation")
    est, r, _ = _run_brb(spec)
    assert r["finite_outputs"]


def test_heteroskedastic_world_runs():
    spec = next(w for w in DIAGNOSTIC_WORLDS if w.world_id == "heteroskedastic_residuals")
    est, r, _ = _run_brb(spec)
    assert r["finite_outputs"]


def test_committed_summary_authorization_blocked():
    if not SUMMARY.exists():
        pytest.skip("summary not generated")
    payload = json.loads(SUMMARY.read_text())
    assert payload["authorization_summary"]["trust_report_authorized"] is False
    assert payload["verdict"] in {
        "tbrridge_brb_interval_corrected_requires_reassessment",
        "tbrridge_brb_centering_corrected_variance_issue_remains",
        "tbrridge_brb_serial_dependence_restricted",
        "tbrridge_brb_correction_inconclusive",
        "tbrridge_brb_correction_failed",
    }
