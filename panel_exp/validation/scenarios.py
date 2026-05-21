"""
Fixed catalog of synthetic validation scenarios.
"""

from __future__ import annotations

from typing import Dict

from panel_exp.validation.synthetic_world import SyntheticScenario


def _base(**overrides) -> SyntheticScenario:
    defaults = dict(
        n_geos=20,
        n_periods=50,
        treatment_start=35,
        treated_units=(),
        true_effect=0.0,
        effect_type="relative",
        baseline_level=100.0,
        trend=0.02,
        seasonality_amplitude=0.0,
        noise_scale=0.8,
        autocorrelation=0.3,
        cross_geo_correlation=0.4,
        outlier_probability=0.0,
        missing_probability=0.0,
        spillover_strength=0.0,
        heterogeneous_effects=False,
        random_state=0,
    )
    defaults.update(overrides)
    return SyntheticScenario(**defaults)


SCENARIO_REGISTRY: Dict[str, SyntheticScenario] = {
    "aa_null": _base(name="aa_null", true_effect=0.0),
    "positive_relative_lift": _base(
        name="positive_relative_lift",
        true_effect=0.10,
        effect_type="relative",
    ),
    "negative_relative_lift": _base(
        name="negative_relative_lift",
        true_effect=-0.10,
        effect_type="relative",
    ),
    "seasonal_positive_lift": _base(
        name="seasonal_positive_lift",
        true_effect=0.10,
        effect_type="relative",
        seasonality_amplitude=4.0,
    ),
    "outlier_positive_lift": _base(
        name="outlier_positive_lift",
        true_effect=0.10,
        effect_type="relative",
        outlier_probability=0.02,
    ),
    "small_geo_positive_lift": _base(
        name="small_geo_positive_lift",
        n_geos=8,
        n_periods=40,
        treatment_start=28,
        true_effect=0.10,
        effect_type="relative",
    ),
    "heterogeneous_positive_lift": _base(
        name="heterogeneous_positive_lift",
        true_effect=0.10,
        effect_type="relative",
        heterogeneous_effects=True,
    ),
}


def get_scenario(name: str) -> SyntheticScenario:
    if name not in SCENARIO_REGISTRY:
        raise KeyError(
            f"Unknown scenario {name!r}. Available: {sorted(SCENARIO_REGISTRY)}"
        )
    return SCENARIO_REGISTRY[name]
