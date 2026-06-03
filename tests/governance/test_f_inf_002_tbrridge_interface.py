"""F-INF-002 — TBRRidge multi-treated inference interface (A16, A18, A21)."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    classify_interval_semantics,
)
from panel_exp.inference_result import IntervalType
from panel_exp.methods.tbr import TBRRidge
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inst_tbrridge_001 import _build_unit_panel
from panel_exp.validation.track_d_d5_pow_001e import _assign
from tests.inference_registry_helpers import make_tbr_panel


def _001e_multi_treated_panel(seed: int = 42):
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY["scm_low_signal"],
        random_state=0,
        n_geos=16,
        n_periods=44,
        treatment_start=28,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    assignment = _assign(
        "greedy_match_markets",
        wide,
        train_length=28,
        seed=seed,
        treatment_probability=0.35,
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    return _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=28,
        test_length=8,
    )


def _post_metrics(results: dict, pre: int) -> tuple[bool, float, float]:
    lo = np.asarray(results["y_lower"], dtype=float)[pre:]
    hi = np.asarray(results["y_upper"], dtype=float)[pre:]
    mask = np.isfinite(lo) & np.isfinite(hi)
    if not np.any(mask):
        return False, float("nan"), float("nan")
    return (
        True,
        float(np.mean(lo[mask] > hi[mask])),
        float(np.mean((hi[mask] - lo[mask]) / 2.0 < 0)),
    )


@pytest.mark.parametrize("inference", ["UnitJackKnife", "JKP", "Conformal"])
class TestTbrridgeMultiTreated001eInterface:
    def test_no_broadcast_failure(self, inference: str) -> None:
        panel = _001e_multi_treated_panel()
        assert len(panel.treated_units) > 1
        est = TBRRidge(inference=inference, alpha=0.05)
        est.run_analysis(panel)
        assert est.results.get("readout_family") == "tbrridge_pooled_counterfactual_multi_treated"

    def test_post_window_structurally_valid(self, inference: str) -> None:
        panel = _001e_multi_treated_panel()
        est = TBRRidge(inference=inference, alpha=0.05)
        est.run_analysis(panel)
        pre = panel.treated_start_idxs[0]
        ok, inv, neg_hw = _post_metrics(est.results, pre)
        assert ok, f"{inference}: no finite post-period bounds"
        assert inv == 0.0
        assert neg_hw == 0.0

    def test_not_governed_uncertainty(self, inference: str) -> None:
        panel = _001e_multi_treated_panel()
        est = TBRRidge(inference=inference, alpha=0.05)
        est.run_analysis(panel)
        pre = panel.treated_start_idxs[0]
        itype = (
            IntervalType.CONFORMAL_INTERVAL.value
            if inference == "Conformal"
            else IntervalType.CONFIDENCE_INTERVAL.value
        )
        verdict = classify_interval_semantics(
            IntervalReadout(
                estimator_name="TBRRidge",
                inference_mode=inference,
                geometry_mode="single_cell",
                path_interval_type=itype,
                y=np.asarray(est.results["y"], dtype=float),
                y_hat=np.asarray(est.results["y_hat"], dtype=float),
                y_lower=np.asarray(est.results["y_lower"], dtype=float),
                y_upper=np.asarray(est.results["y_upper"], dtype=float),
                test_length=len(est.results["y"]) - pre,
                null_interval_exclusion_rate=1.0,
            ),
            require_metadata_bindings=False,
        )
        assert verdict.is_governed_uncertainty is False
        assert verdict.classification != IntervalSemanticsClassification.GOVERNED_UNCERTAINTY


@pytest.mark.parametrize("inference", ["UnitJackKnife", "JKP", "Conformal"])
def test_single_treated_completes_without_multi_readout(inference: str) -> None:
    panel = make_tbr_panel(seed=7)
    est = TBRRidge(inference=inference, alpha=0.05)
    est.run_analysis(panel)
    assert "readout_family" not in est.results
    for key in ("y_lower", "y_upper"):
        assert key in est.results


@pytest.mark.parametrize("inference", ["UnitJackKnife", "Conformal"])
def test_single_treated_post_window_ordered(inference: str) -> None:
    panel = make_tbr_panel(seed=7)
    est = TBRRidge(inference=inference, alpha=0.05)
    est.run_analysis(panel)
    pre = panel.treated_start_idxs[0]
    ok, inv, neg_hw = _post_metrics(est.results, pre)
    assert ok
    assert inv == 0.0
    assert neg_hw == 0.0
