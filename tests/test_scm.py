"""
Tests for SyntheticControlCVXPY and AugSynthCVXPY.

Covers:
  - Correlation pre-filtering (threshold, min_donors fallback)
  - L2 regularisation (lambda_reg spreads weights)
  - Parameter propagation through AugSynthCVXPY
  - Backward compatibility (default params produce valid simplex weights)
"""
import warnings

import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path

# Allow running from repo root without install
_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.methods.scm import SyntheticControlCVXPY, AugSynthCVXPY
from tests.cvxpy_test_helpers import skip_without_cvxpy_osqp

pytestmark = skip_without_cvxpy_osqp


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_panel(
    n_ctrl: int = 10,
    n_time: int = 40,
    treat_start: int = 30,
    n_high_corr: int = 3,
    seed: int = 0,
) -> PanelDataset:
    """
    Build a PanelDataset with one treated unit and n_ctrl control units.

    The first n_high_corr control units are co-linear with the treated series
    (correlation > 0.9). The remaining controls are independent noise.
    """
    rng = np.random.default_rng(seed)
    base = np.cumsum(rng.standard_normal(n_time))

    # High-correlation donors
    high_corr = np.column_stack([
        base + rng.standard_normal(n_time) * 0.05
        for _ in range(n_high_corr)
    ])
    # Low-correlation donors (pure noise, different scale)
    low_corr = rng.standard_normal((n_time, n_ctrl - n_high_corr)) * 10.0

    C = np.hstack([high_corr, low_corr])          # (n_time, n_ctrl)
    y = base + rng.standard_normal(n_time) * 0.1  # (n_time,)

    data = np.vstack([y, C.T])                    # (1 + n_ctrl, n_time)
    geos = ["treated"] + [f"ctrl_{i}" for i in range(n_ctrl)]
    wide = pd.DataFrame(data, index=geos, columns=range(n_time))

    return PanelDataset(wide, [TimePeriod(treat_start, None)], ["treated"])


# ---------------------------------------------------------------------------
# test 1: correlation filter removes low-correlation donors
# ---------------------------------------------------------------------------

def test_scm_cvxpy_correlation_filter_removes_low_corr_donors():
    """Donors below the correlation threshold get zero weight."""
    pds = _make_panel(n_ctrl=10, n_high_corr=3, seed=1)

    m = SyntheticControlCVXPY(donor_correlation_threshold=0.7)
    m.fit_data(pds)
    fitted = m.fit_model()

    w = fitted.weights.ravel()

    # Simplex constraint still holds
    assert abs(w.sum() - 1.0) < 1e-4, f"weights sum={w.sum():.6f}"
    assert np.all(w >= -1e-6), f"negative weight: {w.min():.6f}"

    # The 7 low-corr donors should have zero weight
    # kept_indices identifies which donors were retained
    n_kept = len(m._kept_donor_indices)
    assert n_kept <= 5, f"Expected ≤5 donors kept, got {n_kept}"

    # Donors NOT in kept_indices must have exactly zero weight
    all_idx = np.arange(w.shape[0])
    filtered_idx = np.setdiff1d(all_idx, m._kept_donor_indices)
    assert np.all(w[filtered_idx] == 0.0), \
        f"Filtered donors have non-zero weight: {w[filtered_idx]}"

    # Metadata
    assert m._n_donors_filtered == 10 - n_kept
    assert m._donor_correlations is not None
    assert len(m._donor_correlations) == 10


# ---------------------------------------------------------------------------
# test 2: min_donors fallback when too few donors pass threshold
# ---------------------------------------------------------------------------

def test_scm_cvxpy_min_donors_fallback():
    """When fewer than min_donors pass the threshold, keep exactly min_donors."""
    # Use a very strict threshold so only the 3 high-corr donors pass,
    # but min_donors=5 forces a fallback.
    pds = _make_panel(n_ctrl=10, n_high_corr=3, seed=2)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        m = SyntheticControlCVXPY(
            donor_correlation_threshold=0.99,  # only 3 pass naturally
            min_donors=5,
        )
        m.fit_data(pds)
        fitted = m.fit_model()

    w = fitted.weights.ravel()

    # Exactly min_donors=5 donors kept
    assert len(m._kept_donor_indices) == 5, \
        f"Expected 5 donors kept, got {len(m._kept_donor_indices)}"

    # A UserWarning was raised
    user_warns = [c for c in caught if issubclass(c.category, UserWarning)]
    assert len(user_warns) >= 1, "Expected a UserWarning for min_donors fallback"
    assert "Keeping top 5 donors" in str(user_warns[0].message)

    # Simplex still holds
    assert abs(w.sum() - 1.0) < 1e-4, f"weights sum={w.sum():.6f}"
    assert np.all(w >= -1e-6)


# ---------------------------------------------------------------------------
# test 3: lambda_reg spreads weights across more donors
# ---------------------------------------------------------------------------

def test_scm_cvxpy_lambda_reg_spreads_weights():
    """Higher lambda_reg produces more uniform weights and lower max weight."""
    # Panel where one donor strongly dominates (corr ~ 1.0)
    pds = _make_panel(n_ctrl=8, n_high_corr=1, seed=3)

    m_no_reg = SyntheticControlCVXPY(lambda_reg=0.0)
    m_no_reg.fit_data(pds)
    fitted_no_reg = m_no_reg.fit_model()
    w_no_reg = fitted_no_reg.weights.ravel()

    m_reg = SyntheticControlCVXPY(lambda_reg=0.5)
    m_reg.fit_data(pds)
    fitted_reg = m_reg.fit_model()
    w_reg = fitted_reg.weights.ravel()

    # Both satisfy simplex constraint
    for label, w in [("lambda=0", w_no_reg), ("lambda=0.5", w_reg)]:
        assert abs(w.sum() - 1.0) < 1e-4, f"{label} weights sum={w.sum():.6f}"
        assert np.all(w >= -1e-6), f"{label} negative weight: {w.min():.6f}"

    # Regularisation spreads weights: max weight should be lower
    assert w_reg.max() < w_no_reg.max(), (
        f"Expected max_weight to decrease with lambda_reg. "
        f"lambda=0: {w_no_reg.max():.4f}, lambda=0.5: {w_reg.max():.4f}"
    )

    # Effective donors (w > 0.01) should be higher with regularisation
    n_eff_no_reg = int((w_no_reg > 0.01).sum())
    n_eff_reg    = int((w_reg > 0.01).sum())
    assert n_eff_reg >= n_eff_no_reg, (
        f"Expected more effective donors with lambda_reg. "
        f"lambda=0: {n_eff_no_reg}, lambda=0.5: {n_eff_reg}"
    )

    # Metadata
    assert m_reg._lambda_reg_used == 0.5
    assert m_no_reg._lambda_reg_used == 0.0


# ---------------------------------------------------------------------------
# test 4: AugSynthCVXPY propagates donor params and exposes metadata
# ---------------------------------------------------------------------------

def test_augsynth_cvxpy_propagates_donor_params():
    """AugSynthCVXPY passes new params to inner SCM and exposes metadata."""
    pds = _make_panel(n_ctrl=10, n_high_corr=4, seed=4)

    m = AugSynthCVXPY(
        inference=None,
        donor_correlation_threshold=0.5,
        min_donors=3,
        lambda_reg=0.05,
    )
    m.fit_data(pds)
    fitted = m.fit_model()

    # Inner SCM params were propagated
    assert m.scm.donor_correlation_threshold == 0.5
    assert m.scm.min_donors == 3
    assert m.scm.lambda_reg == 0.05

    # Metadata exposed on AugSynthCVXPY instance
    assert m._donor_correlations is not None
    assert len(m._donor_correlations) == 10
    assert m._n_donors_filtered >= 0

    # SCM weights satisfy simplex
    w = fitted.scm_weights.ravel()
    assert abs(w.sum() - 1.0) < 1e-4, f"scm_weights sum={w.sum():.6f}"
    assert np.all(w >= -1e-6), f"negative scm_weight: {w.min():.6f}"


# ---------------------------------------------------------------------------
# test 5: backward compatibility — default params, no warnings, valid weights
# ---------------------------------------------------------------------------

def test_backward_compatibility_default_params():
    """Default params (no filtering, no reg) produce valid simplex weights."""
    pds = _make_panel(n_ctrl=8, n_high_corr=3, seed=5)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        m = SyntheticControlCVXPY()   # all defaults
        m.fit_data(pds)
        fitted = m.fit_model()

    w = fitted.weights.ravel()

    # Valid simplex weights
    assert abs(w.sum() - 1.0) < 1e-4, f"weights sum={w.sum():.6f}"
    assert np.all(w >= -1e-6), f"negative weight: {w.min():.6f}"

    # No filter applied — all donors kept
    assert m._n_donors_filtered == 0
    assert len(m._kept_donor_indices) == 8

    # No UserWarning raised (threshold=0.0 means no filter)
    user_warns = [c for c in caught if issubclass(c.category, UserWarning)]
    assert len(user_warns) == 0, f"Unexpected warnings: {[str(w.message) for w in user_warns]}"

    # Lambda=0 metadata
    assert m._lambda_reg_used == 0.0
