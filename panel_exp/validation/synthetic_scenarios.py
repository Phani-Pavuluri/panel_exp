"""
Named recovery scenarios per estimator family (2–3 each).

Builds on :class:`~panel_exp.validation.synthetic_world.SyntheticScenario` /
:class:`~panel_exp.validation.synthetic_world.SyntheticWorld` without changing
estimator implementations.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from panel_exp.validation.synthetic_world import SyntheticScenario

ESTIMATOR_RECOVERY_SCENARIOS: Dict[str, Tuple[str, ...]] = {
    "SCM": (
        "scm_low_signal",
        "scm_trend_mismatch",
        "scm_donor_contamination",
        "scm_high_collinearity",
        "scm_structural_break",
        "scm_missing_outcomes",
        "scm_multi_treated",
    ),
    "DID": (
        "did_parallel_trends_holds",
        "did_parallel_trends_violation",
    ),
    "TBR": (
        "tbr_seasonality",
        "tbr_outliers",
        "tbr_varying_lift",
        "tbr_multi_treated",
        "recovery_missing_outcomes",
    ),
    "TBRRidge": (
        "tbrridge_seasonality",
        "tbrridge_outliers",
        "tbrridge_varying_lift",
        "tbrridge_multi_treated",
        "recovery_missing_outcomes",
    ),
    "SyntheticDID": (
        "sdid_staggered_adoption",
        "sdid_seasonal_heterogeneity",
    ),
    "TROP": (
        "trop_sparse_donors",
        "trop_unstable_donor_pool",
    ),
}


def _base(name: str, **overrides) -> SyntheticScenario:
    defaults = dict(
        name=name,
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
        missingness_policy="none",
        spillover_strength=0.0,
        heterogeneous_effects=False,
        random_state=0,
    )
    defaults.update(overrides)
    return SyntheticScenario(**defaults)


RECOVERY_SCENARIO_REGISTRY: Dict[str, SyntheticScenario] = {
    "scm_low_signal": _base(
        "scm_low_signal",
        true_effect=0.10,
        noise_scale=2.2,
        cross_geo_correlation=0.08,
    ),
    "scm_trend_mismatch": _base(
        "scm_trend_mismatch",
        true_effect=0.10,
        seasonality_amplitude=5.0,
        trend=0.08,
    ),
    "scm_donor_contamination": _base(
        "scm_donor_contamination",
        true_effect=0.10,
        spillover_strength=0.35,
    ),
    "scm_high_collinearity": _base(
        "scm_high_collinearity",
        n_geos=24,
        true_effect=0.10,
        cross_geo_correlation=0.98,
        noise_scale=0.25,
        autocorrelation=0.5,
    ),
    "scm_structural_break": _base(
        "scm_structural_break",
        true_effect=0.10,
        structural_break_shift=18.0,
        outlier_probability=0.01,
    ),
    "scm_missing_outcomes": _base(
        "scm_missing_outcomes",
        true_effect=0.10,
        missing_probability=0.06,
        missingness_policy="fill_zero",
        noise_scale=0.6,
    ),
    "scm_multi_treated": _base(
        "scm_multi_treated",
        n_geos=20,
        true_effect=0.10,
        treated_units=("geo_0", "geo_1", "geo_2", "geo_3"),
        treatment_timing="simultaneous",
        cross_geo_correlation=0.35,
    ),
    "recovery_missing_outcomes": _base(
        "recovery_missing_outcomes",
        true_effect=0.10,
        missing_probability=0.05,
        missingness_policy="fill_zero",
        noise_scale=0.6,
    ),
    "tbr_multi_treated": _base(
        "tbr_multi_treated",
        n_geos=16,
        n_periods=45,
        treatment_start=32,
        true_effect=0.10,
        treated_units=("geo_0", "geo_1", "geo_2"),
        treatment_timing="simultaneous",
    ),
    "tbrridge_multi_treated": _base(
        "tbrridge_multi_treated",
        n_geos=16,
        n_periods=45,
        treatment_start=32,
        true_effect=0.10,
        treated_units=("geo_0", "geo_1", "geo_2"),
        treatment_timing="simultaneous",
    ),
    "did_parallel_trends_holds": _base(
        "did_parallel_trends_holds",
        true_effect=0.10,
        seasonality_amplitude=0.5,
        trend=0.02,
    ),
    "did_parallel_trends_violation": _base(
        "did_parallel_trends_violation",
        true_effect=0.10,
        seasonality_amplitude=3.0,
        trend=0.12,
        heterogeneous_effects=True,
    ),
    "tbr_seasonality": _base(
        "tbr_seasonality",
        true_effect=0.10,
        seasonality_amplitude=4.0,
    ),
    "tbr_outliers": _base(
        "tbr_outliers",
        true_effect=0.10,
        outlier_probability=0.025,
    ),
    "tbr_varying_lift": _base(
        "tbr_varying_lift",
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
    "tbrridge_seasonality": _base(
        "tbrridge_seasonality",
        true_effect=0.10,
        seasonality_amplitude=4.0,
    ),
    "tbrridge_outliers": _base(
        "tbrridge_outliers",
        true_effect=0.10,
        outlier_probability=0.025,
    ),
    "tbrridge_varying_lift": _base(
        "tbrridge_varying_lift",
        true_effect=0.10,
        heterogeneous_effects=True,
    ),
    "sdid_staggered_adoption": _base(
        "sdid_staggered_adoption",
        n_geos=14,
        n_periods=45,
        treatment_start=30,
        true_effect=0.10,
        heterogeneous_effects=True,
        treated_units=("geo_0", "geo_1", "geo_2"),
        treatment_timing="staggered",
        staggered_starts=(30, 33, 36),
    ),
    "sdid_seasonal_heterogeneity": _base(
        "sdid_seasonal_heterogeneity",
        n_geos=12,
        n_periods=42,
        treatment_start=28,
        true_effect=0.08,
        seasonality_amplitude=2.0,
        treatment_timing="simultaneous",
    ),
    "trop_sparse_donors": _base(
        "trop_sparse_donors",
        n_geos=10,
        n_periods=40,
        treatment_start=28,
        true_effect=0.10,
        cross_geo_correlation=0.15,
    ),
    "trop_unstable_donor_pool": _base(
        "trop_unstable_donor_pool",
        n_geos=9,
        n_periods=38,
        treatment_start=26,
        true_effect=0.10,
        noise_scale=1.8,
        outlier_probability=0.02,
        cross_geo_correlation=0.1,
    ),
    "recovery_null_effect": _base(
        "recovery_null_effect",
        true_effect=0.0,
        missingness_policy="none",
    ),
    "recovery_positive_effect": _base(
        "recovery_positive_effect",
        true_effect=0.10,
        missingness_policy="none",
    ),
}

# Recovery-runner support notes (DGP may exist but PanelDataset / estimators may not).
SCENARIO_RECOVERY_SUPPORT: Dict[str, Dict[str, Any]] = {
    "sdid_staggered_adoption": {
        "recovery_supported": False,
        "skip_reason": (
            "Staggered DGP is supported (per-unit treatment_start_by_unit), but "
            "SyntheticDID recovery configs are not registered in RecoveryRunner."
        ),
    },
    "sdid_seasonal_heterogeneity": {
        "recovery_supported": False,
        "skip_reason": "SyntheticDID recovery configs are not registered in RecoveryRunner.",
    },
}


def get_scenario_recovery_support(scenario_name: str) -> Dict[str, Any]:
    """Whether a scenario can be run end-to-end by RecoveryRunner today."""
    return dict(
        SCENARIO_RECOVERY_SUPPORT.get(
            scenario_name,
            {
                "recovery_supported": True,
                "skip_reason": None,
            },
        )
    )


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


__all__ = [
    "ESTIMATOR_RECOVERY_SCENARIOS",
    "RECOVERY_SCENARIO_REGISTRY",
    "SCENARIO_RECOVERY_SUPPORT",
    "estimator_scenario_map",
    "get_recovery_scenario",
    "get_scenario_recovery_support",
    "list_recovery_scenario_names",
    "materialize_scenario",
    "scenarios_for_estimator",
]
