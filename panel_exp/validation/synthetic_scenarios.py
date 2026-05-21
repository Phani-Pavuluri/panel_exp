"""
Named recovery scenarios per estimator family (2–3 each).

Builds on :class:`~panel_exp.validation.synthetic_world.SyntheticScenario` /
:class:`~panel_exp.validation.synthetic_world.SyntheticWorld` without changing
estimator implementations.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Mapping, Sequence, Tuple

from panel_exp.validation.synthetic_world import SyntheticScenario

# Estimator registry key -> scenario names for recovery batteries
ESTIMATOR_RECOVERY_SCENARIOS: Dict[str, Tuple[str, ...]] = {
    "SCM": (
        "scm_low_signal",
        "scm_trend_mismatch",
        "scm_donor_contamination",
    ),
    "DID": (
        "did_parallel_trends_holds",
        "did_parallel_trends_violation",
    ),
    "TBR": (
        "tbr_seasonality",
        "tbr_outliers",
        "tbr_varying_lift",
    ),
    "TBRRidge": (
        "tbrridge_seasonality",
        "tbrridge_outliers",
        "tbrridge_varying_lift",
    ),
    "SyntheticDID": (
        "sdid_staggered_timing",
        "sdid_varying_timing",
    ),
    "TROP": (
        "trop_sparse_donors",
        "trop_unstable_donor_pool",
    ),
}


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


RECOVERY_SCENARIO_REGISTRY: Dict[str, SyntheticScenario] = {
    # SCM
    "scm_low_signal": _base(
        scenario_name="scm_low_signal",
        true_effect=0.10,
        noise_scale=2.2,
        cross_geo_correlation=0.08,
    ),
    "scm_trend_mismatch": _base(
        scenario_name="scm_trend_mismatch",
        true_effect=0.10,
        seasonality=5.0,
        trend=0.08,
    ),
    "scm_donor_contamination": _base(
        scenario_name="scm_donor_contamination",
        true_effect=0.10,
        spillover_strength=0.35,
    ),
    "scm_structural_break": _base(
        scenario_name="scm_structural_break",
        true_effect=0.10,
        outlier_probability=0.03,
    ),
    # DID
    "did_parallel_trends_holds": _base(
        scenario_name="did_parallel_trends_holds",
        true_effect=0.10,
        seasonality=0.5,
        trend=0.02,
    ),
    "did_parallel_trends_violation": _base(
        scenario_name="did_parallel_trends_violation",
        true_effect=0.10,
        seasonality=3.0,
        trend=0.12,
        heterogeneous_effects=True,
    ),
    # TBR / TBRRidge
    "tbr_seasonality": _base(
        scenario_name="tbr_seasonality",
        true_effect=0.10,
        seasonality=4.0,
    ),
    "tbr_outliers": _base(
        scenario_name="tbr_outliers",
        true_effect=0.10,
        outlier_probability=0.025,
    ),
    "tbr_varying_lift": _base(
        scenario_name="tbr_varying_lift",
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
    "tbrridge_seasonality": _base(
        scenario_name="tbrridge_seasonality",
        true_effect=0.10,
        seasonality=4.0,
    ),
    "tbrridge_outliers": _base(
        scenario_name="tbrridge_outliers",
        true_effect=0.10,
        outlier_probability=0.025,
    ),
    "tbrridge_varying_lift": _base(
        scenario_name="tbrridge_varying_lift",
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
    # SyntheticDID (staggered / timing variation proxied via heterogeneity + smaller panel)
    "sdid_staggered_timing": _base(
        scenario_name="sdid_staggered_timing",
        n_geos=14,
        n_treated=3,
        n_periods=45,
        treatment_start=30,
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
    "sdid_varying_timing": _base(
        scenario_name="sdid_varying_timing",
        n_geos=12,
        n_treated=2,
        n_periods=42,
        treatment_start=28,
        true_effect=0.08,
        seasonality=2.0,
    ),
    # TROP
    "trop_sparse_donors": _base(
        scenario_name="trop_sparse_donors",
        n_geos=10,
        n_treated=2,
        n_periods=40,
        treatment_start=28,
        true_effect=0.10,
        cross_geo_correlation=0.15,
    ),
    "trop_unstable_donor_pool": _base(
        scenario_name="trop_unstable_donor_pool",
        n_geos=9,
        n_treated=2,
        n_periods=38,
        treatment_start=26,
        true_effect=0.10,
        noise_scale=1.8,
        outlier_probability=0.02,
        cross_geo_correlation=0.1,
    ),
    # Null / power reference scenarios (shared)
    "recovery_null_effect": _base(
        scenario_name="recovery_null_effect",
        true_effect=0.0,
    ),
    "recovery_positive_effect": _base(
        scenario_name="recovery_positive_effect",
        true_effect=0.10,
    ),
}


def get_recovery_scenario(name: str) -> SyntheticScenario:
    if name not in RECOVERY_SCENARIO_REGISTRY:
        raise KeyError(
            f"Unknown recovery scenario {name!r}. "
            f"Available: {sorted(RECOVERY_SCENARIO_REGISTRY)}"
        )
    return RECOVERY_SCENARIO_REGISTRY[name]


def scenarios_for_estimator(estimator: str) -> List[str]:
    if estimator not in ESTIMATOR_RECOVERY_SCENARIOS:
        raise KeyError(
            f"Unknown estimator {estimator!r}. "
            f"Known: {sorted(ESTIMATOR_RECOVERY_SCENARIOS)}"
        )
    return list(ESTIMATOR_RECOVERY_SCENARIOS[estimator])


def materialize_scenario(
    name: str,
    *,
    random_state: int,
) -> SyntheticScenario:
    """Return scenario with an explicit ``random_state`` for reproducibility."""
    return replace(get_recovery_scenario(name), random_state=random_state)


def list_recovery_scenario_names() -> List[str]:
    return sorted(RECOVERY_SCENARIO_REGISTRY)


def estimator_scenario_map() -> Mapping[str, Sequence[str]]:
    return ESTIMATOR_RECOVERY_SCENARIOS
