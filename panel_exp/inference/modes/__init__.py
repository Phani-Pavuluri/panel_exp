"""Built-in inference mode registrations for ImpactAnalyzer."""

from __future__ import annotations

from panel_exp.inference.modes import impl
from panel_exp.inference.registry import FailureBehavior, InferenceModeSpec, InferenceRegistry
from panel_exp.inference_result import IntervalType


def register_builtin_inference_modes(registry: InferenceRegistry) -> None:
    registry.register(
        InferenceModeSpec(
            name="point_estimate",
            aliases=(),
            run=impl.run_point_estimate,
            output_keys=("times", "y", "y_hat"),
            path_interval_type=IntervalType.UNAVAILABLE,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="UnitJackKnife",
            run=impl.run_unit_jackknife,
            output_keys=("times", "y", "y_hat", "y_lower", "y_upper"),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
            estimator_check=lambda a: (
                "UnitJackKnife requires at least 2 control units"
                if a.panel_data.num_control_units < 2
                else None
            ),
        )
    )
    registry.register(
        InferenceModeSpec(
            name="JKP",
            run=impl.run_jkp,
            output_keys=("times", "y", "y_hat", "y_lower", "y_upper"),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="Bayesian",
            run=impl.run_bayesian,
            output_keys=("times", "y", "y_hat", "y_lower", "y_upper"),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CREDIBLE_INTERVAL,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="BlockResidualBootstrap",
            run=impl.run_block_residual_bootstrap,
            output_keys=(
                "times",
                "y",
                "y_hat",
                "y_lower",
                "y_upper",
                "block_residual_bootstrap_stats",
                "effect_cumulative_brb",
                "effect_ci_lower_cumulative_brb",
                "effect_ci_upper_cumulative_brb",
            ),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
            default_kwargs={
                "center_residuals": True,
                "refit_in_bootstrap": False,
                "refit_mode": "post_only",
                "ci_method": "percentile",
                "bootstrap_type": "block",
                "pool_donor_residuals": False,
            },
        )
    )
    registry.register(
        InferenceModeSpec(
            name="Conformal",
            run=impl.run_conformal,
            output_keys=("times", "y", "y_hat", "y_lower", "y_upper"),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFORMAL_INTERVAL,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="Kfold",
            run=impl.run_kfold,
            output_keys=("times", "y", "y_hat", "y_lower", "y_upper"),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="Placebo",
            run=impl.run_placebo,
            output_keys=(
                "times",
                "y",
                "y_hat",
                "y_lower",
                "y_upper",
                "placebo_stats",
                "effect_ci_lower_inversion",
                "effect_ci_upper_inversion",
                "placebo_unsupported",
                "intervals_available",
                "interval_type",
            ),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.PLACEBO_BAND,
            default_kwargs={"placebo_strict": True},
            failure_behavior=FailureBehavior.SILENT,
        )
    )
    registry.register(
        InferenceModeSpec(
            name="TimeSeriesKfold",
            run=impl.run_timeseries_kfold,
            output_keys=(
                "times",
                "y",
                "y_hat",
                "y_lower",
                "y_upper",
                "effect_cumulative_tsk",
                "effect_ci_lower_cumulative_tsk",
                "effect_ci_upper_cumulative_tsk",
            ),
            interval_keys=("y_lower", "y_upper"),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
            default_kwargs={
                "k": 5,
                "debias_flag": True,
                "block_scheme": "expanding",
                "n_jobs": 1,
                "show_progress": True,
            },
        )
    )
