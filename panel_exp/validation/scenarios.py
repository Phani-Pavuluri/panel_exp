"""
Fixed library of synthetic validation scenarios.
"""

from __future__ import annotations

from typing import Dict

from panel_exp.validation.synthetic_world import SyntheticScenario


def _base(**overrides) -> SyntheticScenario:
    defaults = dict(
        n_geos=20,
        n_periods=50,
        treatment_start=35,
        n_treated=4,
        true_effect=0.0,
        effect_type="relative",
        seasonality=0.0,
        trend=0.02,
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
    "aa_zero_effect": _base(
        scenario_name="aa_zero_effect",
        true_effect=0.0,
    ),
    "constant_positive_10pct": _base(
        scenario_name="constant_positive_10pct",
        true_effect=0.10,
    ),
    "constant_negative_10pct": _base(
        scenario_name="constant_negative_10pct",
        true_effect=-0.10,
    ),
    "seasonality": _base(
        scenario_name="seasonality",
        true_effect=0.10,
        seasonality=4.0,
    ),
    "outlier_world": _base(
        scenario_name="outlier_world",
        true_effect=0.10,
        outlier_probability=0.02,
    ),
    "small_geo": _base(
        scenario_name="small_geo",
        n_geos=8,
        n_treated=2,
        n_periods=40,
        treatment_start=28,
        true_effect=0.10,
    ),
    "heterogeneous_effects": _base(
        scenario_name="heterogeneous_effects",
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
}


def get_scenario(name: str) -> SyntheticScenario:
    if name not in SCENARIO_REGISTRY:
        raise KeyError(
            f"Unknown scenario {name!r}. Available: {sorted(SCENARIO_REGISTRY)}"
        )
    return SCENARIO_REGISTRY[name]
