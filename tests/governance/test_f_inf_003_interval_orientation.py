"""F-INF-003 — interval orientation fix (Conformal, TimeSeriesKfold)."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    classify_interval_semantics,
)
from panel_exp.inference_result import IntervalType
from panel_exp.methods.tbr import TBRRidge
from tests.inference_registry_helpers import make_tbr_panel

try:
    from panel_exp.methods.scm import AugSynthCVXPY

    _HAS_AUGSYNTH = True
except ImportError:
    _HAS_AUGSYNTH = False

cvxpy = pytest.importorskip("cvxpy", reason="AugSynthCVXPY conformal tests need cvxpy")


def _post_window_metrics(results: dict, pre_t: int) -> tuple[float, float, float]:
    lo = np.asarray(results["y_lower"], dtype=float)[pre_t:]
    hi = np.asarray(results["y_upper"], dtype=float)[pre_t:]
    mask = np.isfinite(lo) & np.isfinite(hi)
    if not np.any(mask):
        return float("nan"), float("nan"), float("nan")
    lo_m = lo[mask]
    hi_m = hi[mask]
    hw = (hi_m - lo_m) / 2.0
    inv_frac = float(np.mean(lo_m > hi_m))
    neg_hw_frac = float(np.mean(hw < 0))
    return neg_hw_frac, inv_frac, float(np.nanmean(hw))


def _classify_tbrridge(results: dict, panel, inference: str, null_fpr: float = 1.0):
    pre = panel.treated_start_idxs[0]
    interval_type = (
        IntervalType.CONFORMAL_INTERVAL.value
        if inference == "Conformal"
        else IntervalType.CONFIDENCE_INTERVAL.value
    )
    return classify_interval_semantics(
        IntervalReadout(
            estimator_name="TBRRidge",
            inference_mode=inference,
            geometry_mode="single_cell",
            path_interval_type=interval_type,
            y=np.asarray(results["y"], dtype=float),
            y_hat=np.asarray(results["y_hat"], dtype=float),
            y_lower=np.asarray(results["y_lower"], dtype=float),
            y_upper=np.asarray(results["y_upper"], dtype=float),
            test_length=len(results["y"]) - pre,
            null_interval_exclusion_rate=null_fpr,
        ),
        require_metadata_bindings=False,
    )


class TestStructuralValidity:
    @pytest.mark.parametrize("inference", ["Conformal", "TimeSeriesKfold"])
    def test_tbrridge_post_window_non_negative_halfwidth(self, inference: str) -> None:
        panel = make_tbr_panel(seed=42)
        est = TBRRidge(inference=inference, alpha=0.05)
        kw = {"k": 3, "show_progress": False, "n_jobs": 1} if inference == "TimeSeriesKfold" else {}
        est.run_analysis(panel, **kw)
        pre = est.panel_data.treated_start_idxs[0]
        neg_hw, inv_frac, mean_hw = _post_window_metrics(est.results, pre)
        assert neg_hw == 0.0, f"{inference}: negative half-width on post window"
        assert inv_frac == 0.0, f"{inference}: inverted bounds on post window"
        assert mean_hw > 0, f"{inference}: expected positive mean half-width, got {mean_hw}"

    def test_tbrridge_lower_le_upper_post_window(self) -> None:
        panel = make_tbr_panel(seed=42)
        est = TBRRidge(inference="TimeSeriesKfold", alpha=0.05)
        est.run_analysis(panel, k=3, show_progress=False, n_jobs=1)
        pre = est.panel_data.treated_start_idxs[0]
        lo = est.results["y_lower"][pre:]
        hi = est.results["y_upper"][pre:]
        mask = np.isfinite(lo) & np.isfinite(hi)
        assert np.all(lo[mask] <= hi[mask])

    @pytest.mark.skipif(not _HAS_AUGSYNTH, reason="AugSynthCVXPY not importable")
    def test_augsynth_conformal_non_negative_halfwidth(self) -> None:
        from tests.inference_registry_helpers import make_scm_panel

        panel = make_scm_panel(seed=42, n_ctrl=8, n_time=35, treat_start=20)
        est = AugSynthCVXPY(inference="Conformal", alpha=0.05)
        est.run_analysis(panel)
        pre = est.panel_data.treated_start_idxs[0]
        neg_hw, inv_frac, _ = _post_window_metrics(est.results, pre)
        assert neg_hw == 0.0
        assert inv_frac == 0.0


class TestFInf001Preserved:
    def test_classifier_still_blocks_inverted_readout(self) -> None:
        n = 8
        readout = IntervalReadout(
            estimator_name="AugSynthCVXPY",
            inference_mode="Conformal",
            geometry_mode="single_cell",
            path_interval_type=IntervalType.CONFORMAL_INTERVAL.value,
            y=np.full(n, 10.0),
            y_hat=np.full(n, 10.0),
            y_lower=np.full(n, 20.0),
            y_upper=np.full(n, 4.0),
            test_length=n,
            null_interval_exclusion_rate=0.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
        assert verdict.classification == IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL
        assert verdict.is_governed_uncertainty is False

    def test_not_governed_uncertainty_after_orientation_fix(self) -> None:
        panel = make_tbr_panel(seed=42)
        est = TBRRidge(inference="Conformal", alpha=0.05)
        est.run_analysis(panel)
        verdict = _classify_tbrridge(est.results, panel, "Conformal", null_fpr=1.0)
        assert verdict.is_governed_uncertainty is False
        assert verdict.classification != IntervalSemanticsClassification.GOVERNED_UNCERTAINTY

    def test_structurally_valid_but_null_fpr_still_unverified(self) -> None:
        """Orientation fix does not weaken null-FPR semantics gate."""
        panel = make_tbr_panel(seed=42)
        est = TBRRidge(inference="Conformal", alpha=0.05)
        est.run_analysis(panel)
        verdict = _classify_tbrridge(est.results, panel, "Conformal", null_fpr=1.0)
        assert verdict.classification in (
            IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS,
            IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
            IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL,
        )
        assert verdict.classification != IntervalSemanticsClassification.GOVERNED_UNCERTAINTY
