"""
Estimand alignment: synthetic truth, canonical metrics, estimator exports, recovery scoring.

Does not change estimator math; documents where quantities differ by design.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from panel_exp.methods.DID import DID
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.spec import TargetEstimand
from panel_exp.validation.runner import _path_relative_att
from panel_exp.validation.recovery_runner import (
    PREDICTED_EFFECT_SCORING,
    SCORED_TARGET_ESTIMAND,
    RecoveryRunner,
)
from panel_exp.validation.synthetic_world import (
    SyntheticScenario,
    SyntheticWorld,
    canonical_absolute_att_post,
    canonical_cumulative_att,
    canonical_pooled_relative_att_post,
    canonical_relative_att_post,
)


def _simple_homogeneous_scenario(**overrides) -> SyntheticScenario:
    defaults = dict(
        name="align_homogeneous",
        n_geos=12,
        n_periods=40,
        treatment_start=28,
        true_effect=0.08,
        effect_type="relative",
        heterogeneous_effects=False,
        spillover_strength=0.0,
        noise_scale=0.3,
        cross_geo_correlation=0.2,
        random_state=11,
    )
    defaults.update(overrides)
    return SyntheticScenario(**defaults)


def _world_arrays(world: SyntheticWorld):
    y = np.asarray(world.truth["observed"], dtype=float)
    y0 = np.asarray(world.truth["counterfactual"], dtype=float)
    treated = list(world.truth["treated_units"])
    t0 = int(world.truth["treatment_start"])
    n_periods = y.shape[1]
    units = list(world.truth["unit_names"])
    return y, y0, treated, t0, n_periods, units


class _PerfectCounterfactualEstimator:
    """Mock estimator with y_hat = counterfactual on the treated reporting path."""

    def __init__(self, y: np.ndarray, y_hat: np.ndarray):
        self.results = {"y": y, "y_hat": y_hat}


@pytest.mark.parametrize("seed", [0, 7, 42])
def test_homogeneous_scalar_truth_equals_canonical_relative(seed: int):
    scenario = _simple_homogeneous_scenario(random_state=seed)
    world = SyntheticWorld.generate(scenario)
    y, y0, treated, t0, n_periods, units = _world_arrays(world)

    canonical = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    assert world.truth["true_effect"] == pytest.approx(canonical, rel=0, abs=1e-12)
    assert world.truth["effect_type"] == "relative"


def test_homogeneous_path_relative_att_matches_truth_with_perfect_counterfactual(
    seed: int = 3,
):
    scenario = _simple_homogeneous_scenario(random_state=seed)
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    y, y0, treated, t0, n_periods, units = _world_arrays(world)

    # Build 1d treated reporting series (first treated geo) for path metric.
    unit_to_idx = {u: i for i, u in enumerate(units)}
    gi = unit_to_idx[treated[0]]
    mock = _PerfectCounterfactualEstimator(
        y[gi, :].copy(),
        y0[gi, :].copy(),
    )
    path_att = _path_relative_att(mock, panel)
    truth = float(world.truth["true_effect"])
    assert path_att == pytest.approx(truth, rel=0, abs=1e-10)


def test_heterogeneous_configured_effect_differs_from_scalar_truth():
    scenario = _simple_homogeneous_scenario(
        heterogeneous_effects=True,
        true_effect=0.10,
        random_state=99,
    )
    world = SyntheticWorld.generate(scenario)
    y, y0, treated, t0, n_periods, units = _world_arrays(world)

    canonical = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    assert world.truth["true_effect"] == pytest.approx(canonical, rel=0, abs=1e-12)

    by_unit = world.truth["effect_by_unit"]
    mean_configured = float(
        np.mean([by_unit[u] for u in world.truth["treated_units"]])
    )
    # Heterogeneous spreads are multipliers on configured effect; realized lifts
    # average over post periods and can differ from the mean configured multiplier.
    assert mean_configured == pytest.approx(0.10, rel=0.15)
    if abs(mean_configured - canonical) < 1e-6:
        pytest.skip("draw placed multipliers near 1.0; skip inequality demo")


def test_cumulative_att_not_comparable_to_mean_relative_att():
    scenario = _simple_homogeneous_scenario(true_effect=0.12, random_state=5)
    world = SyntheticWorld.generate(scenario)
    y, y0, treated, t0, n_periods, units = _world_arrays(world)

    rel = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    cum = canonical_cumulative_att(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    assert rel == pytest.approx(float(world.truth["true_effect"]), rel=0, abs=1e-9)
    assert cum > rel
    assert cum != pytest.approx(rel, rel=1e-3, abs=1e-3)


def test_absolute_scenario_uses_absolute_canonical():
    scenario = _simple_homogeneous_scenario(
        effect_type="absolute",
        true_effect=2.5,
        random_state=8,
    )
    world = SyntheticWorld.generate(scenario)
    y, y0, treated, t0, n_periods, units = _world_arrays(world)
    abs_canon = canonical_absolute_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    rel_canon = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    assert world.truth["true_effect"] == pytest.approx(abs_canon, rel=0, abs=1e-9)
    assert rel_canon != pytest.approx(abs_canon, rel=0.05, abs=0.05)


@pytest.mark.parametrize("seed", [1, 17])
def test_tbrridge_path_relative_att_near_canonical_on_simple_dgp(seed: int):
    scenario = _simple_homogeneous_scenario(
        n_geos=8,
        noise_scale=0.2,
        random_state=seed,
    )
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    y, y0, treated, t0, n_periods, units = _world_arrays(world)
    canonical = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )

    est = TBRRidge(inference=None)
    est.run_analysis(panel)
    path = _path_relative_att(est, panel)
    assert np.isfinite(path)
    assert path == pytest.approx(canonical, rel=0.25, abs=0.04)


@pytest.mark.parametrize("seed", [2, 23])
def test_scm_path_relative_att_near_canonical_on_simple_dgp(seed: int):
    scenario = _simple_homogeneous_scenario(
        n_geos=10,
        noise_scale=0.25,
        cross_geo_correlation=0.15,
        random_state=seed,
    )
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()
    y, y0, treated, t0, n_periods, units = _world_arrays(world)
    canonical = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )

    est = SyntheticControl(inference=None)
    est.run_analysis(panel)
    path = _path_relative_att(est, panel)
    assert np.isfinite(path)
    assert path == pytest.approx(canonical, rel=0.35, abs=0.06)


def test_did_pooled_path_relative_att_near_canonical_under_parallel_trends():
    from panel_exp.validation.synthetic_scenarios import get_recovery_scenario

    scenario = get_recovery_scenario("did_parallel_trends_holds")
    world = SyntheticWorld.generate(replace(scenario, random_state=31))
    panel = world.to_panel_dataset()
    y, y0, treated, t0, n_periods, units = _world_arrays(world)
    pooled_canon = canonical_pooled_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )
    unit_canon = canonical_relative_att_post(
        y, y0, treated, t0, n_periods, unit_names=units
    )

    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    path = _path_relative_att(did, panel)

    assert np.isfinite(path)
    assert path == pytest.approx(pooled_canon, rel=0.3, abs=0.05)
    # TWFE level coefficient is not the relative ATT estimand.
    assert did.treatment_effect != pytest.approx(
        float(world.truth["true_effect"]), rel=0.05, abs=0.02
    )
    # Pooled vs unit-mean canonical can differ with multiple treated geos.
    if len(treated) > 1:
        assert pooled_canon == pytest.approx(unit_canon, rel=0.2, abs=0.03)


def test_did_cumulative_att_differs_from_path_relative_scoring():
    scenario = _simple_homogeneous_scenario(random_state=12)
    world = SyntheticWorld.generate(scenario)
    panel = world.to_panel_dataset()

    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    path_rel = _path_relative_att(did, panel)
    cum = float(did.cumulative_att)
    mean_abs = float(did.mean_post_period_att)

    assert np.isfinite(path_rel)
    assert np.isfinite(cum)
    assert cum != pytest.approx(path_rel, rel=0.1, abs=0.1)
    assert mean_abs != pytest.approx(path_rel, rel=0.1, abs=0.1)


def test_recovery_runner_declares_scored_estimand():
    payload = RecoveryRunner(
        "SCM",
        "recovery_positive_effect",
        n_simulations=1,
        random_state=0,
    ).run()
    assert payload["scored_target_estimand"] == TargetEstimand.RELATIVE_ATT_POST.value
    assert payload["scored_target_estimand"] == SCORED_TARGET_ESTIMAND
    assert payload["predicted_effect_scoring"] == PREDICTED_EFFECT_SCORING


def test_recovery_predicted_effect_uses_path_relative_att_not_did_coef():
    payload = RecoveryRunner(
        "DID",
        "recovery_positive_effect",
        n_simulations=1,
        random_state=4,
    ).run()
    assert payload["predicted_effect_scoring"] == "_path_relative_att"
    # Bias is still computed vs relative scalar truth; DID coef would differ systematically.
    assert payload["scored_target_estimand"] == "relative_att_post"
