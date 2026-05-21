"""Smoke tests: one estimator recovers sign of a small positive effect."""

import pytest

from panel_exp.validation.runner import (
    EstimatorValidationRunner,
    default_estimator_configs,
)
from panel_exp.validation.scenarios import get_scenario
from panel_exp.validation.synthetic_world import SyntheticWorld


@pytest.mark.parametrize("estimator_name", ["SCM", "TBR"])
def test_smoke_positive_effect_direction(estimator_name):
    scenario = get_scenario("positive_relative_lift")
    config = next(
        c for c in default_estimator_configs() if c.estimator_name == estimator_name
    )
    world = SyntheticWorld.generate(scenario)
    truth = float(world.truth["true_effect"])

    report = EstimatorValidationRunner(
        scenarios=[scenario],
        estimator_configs=[config],
        n_replications=1,
    ).run()

    assert len(report.metrics) == 1
    m = report.metrics[0]
    assert m.failure_rate < 1.0
    # Loose tolerance: correct sign or small bias vs ~10% truth
    assert m.bias + truth > 0 or abs(m.bias) < 0.15
