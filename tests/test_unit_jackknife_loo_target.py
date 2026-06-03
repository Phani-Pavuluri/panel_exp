"""Shared unit jackknife LOO target semantics (INV-D3-001)."""

from __future__ import annotations

import numpy as np

from panel_exp.inference.unit_jackknife import unit_jk
from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inf_002a import (
    _mean_post_halfwidth,
    _perturb_post_outcomes,
    unit_jk_literature_reference,
)


def test_unit_jk_matches_literature_counterfactual_anchor() -> None:
    """Production unit_jk uses y_hat vs leave-one-out y_hat (shared primitive)."""
    scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
    panel = SyntheticWorld.generate(scenario).to_panel_dataset()
    prod = np.asarray(unit_jk(panel, SyntheticControl, variation=1, alpha=0.05))
    ref = unit_jk_literature_reference(panel, SyntheticControl, alpha=0.05)
    assert prod.shape == ref.shape
    np.testing.assert_allclose(prod, ref, rtol=1e-9, atol=1e-9)


def test_scm_jk_invariant_to_treated_post_outcome_noise() -> None:
    """SCM + UnitJackKnife: noised treated post y must not move JK when y_hat is unchanged."""
    scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
    panel = SyntheticWorld.generate(scenario).to_panel_dataset()
    errors = unit_jk(panel, SyntheticControl, variation=1, alpha=0.05)
    hw_before = _mean_post_halfwidth(panel, errors)

    noisy = _perturb_post_outcomes(
        panel,
        units=list(panel.treated_units),
        noise_sd=80.0,
        seed=99,
    )
    errors_noisy = unit_jk(noisy, SyntheticControl, variation=1, alpha=0.05)
    hw_after = _mean_post_halfwidth(noisy, errors_noisy)

    assert np.isfinite(hw_before) and hw_before > 0
    rel_change = abs(hw_after - hw_before) / hw_before
    assert rel_change < 0.05, f"JK half-width shifted {rel_change:.3f} under treated post noise"
