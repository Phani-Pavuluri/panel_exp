"""
Recovery validation runner: Monte Carlo synthetic truth experiments per estimator.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Type, Union

import numpy as np

from panel_exp.spec import TargetEstimand
from panel_exp.validation.recovery_metrics import (
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_intervals import (
    POINT_ESTIMAND,
    extract_recovery_interval,
)
from panel_exp.validation.runner import (
    _path_relative_att,
    default_estimator_configs,
)
from panel_exp.validation.synthetic_scenarios import (
    get_recovery_scenario,
    get_scenario_recovery_support,
    scenarios_for_estimator,
)
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

EstimatorInput = Union[str, Type[Any]]

# Recovery scores predicted vs scalar truth on this estimand (see runner._path_relative_att).
SCORED_TARGET_ESTIMAND = TargetEstimand.RELATIVE_ATT_POST.value
PREDICTED_EFFECT_SCORING = "_path_relative_att"


@dataclass(frozen=True)
class RecoveryEstimatorConfig:
    """Recovery battery config (point estimate or inference-enabled)."""

    config_name: str
    estimator_name: str
    factory: Callable[[], Any]
    inference: Optional[str] = None
    run_kwargs: Dict[str, Any] = field(default_factory=dict)
    supports_significance: bool = False
    intervals_expected: bool = False
    significance_from_ci: bool = False


def _point_estimate_configs() -> Dict[str, RecoveryEstimatorConfig]:
    """Existing fast defaults (inference=None)."""
    out: Dict[str, RecoveryEstimatorConfig] = {}
    for cfg in default_estimator_configs():
        out[cfg.estimator_name] = RecoveryEstimatorConfig(
            config_name=cfg.estimator_name,
            estimator_name=cfg.estimator_name,
            factory=cfg.factory,
            inference=cfg.inference,
            run_kwargs=dict(cfg.run_kwargs),
            supports_significance=cfg.supports_significance,
            intervals_expected=False,
            significance_from_ci=False,
        )
    return out


def _inference_recovery_configs() -> Dict[str, RecoveryEstimatorConfig]:
    """Separate inference-enabled configs for calibration (small n for CI speed)."""
    from panel_exp.methods.DID import DID
    from panel_exp.methods.scm import SyntheticControl
    from panel_exp.methods.tbr import TBRRidge

    def _did_bootstrap_factory() -> DID:
        did = DID()
        did.n_bootstrap = 30
        did.bootstrap_block_size = 6
        return did

    return {
        "SCM_UnitJackKnife": RecoveryEstimatorConfig(
            config_name="SCM_UnitJackKnife",
            estimator_name="SCM",
            factory=lambda: SyntheticControl(inference="UnitJackKnife", alpha=0.05),
            inference="UnitJackKnife",
            run_kwargs={},
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=True,
        ),
        "TBRRidge_Kfold": RecoveryEstimatorConfig(
            config_name="TBRRidge_Kfold",
            estimator_name="TBRRidge",
            factory=lambda: TBRRidge(inference="Kfold", alpha=0.05),
            inference="Kfold",
            run_kwargs={},
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=True,
        ),
        "TBRRidge_BlockResidualBootstrap": RecoveryEstimatorConfig(
            config_name="TBRRidge_BlockResidualBootstrap",
            estimator_name="TBRRidge",
            factory=lambda: TBRRidge(
                inference="BlockResidualBootstrap", alpha=0.05
            ),
            inference="BlockResidualBootstrap",
            run_kwargs={
                "n_bootstrap": 25,
                "block_length": 6,
                "min_train_periods": 8,
                "show_progress": False,
                "random_state": 0,
            },
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=True,
        ),
        "DID_Bootstrap": RecoveryEstimatorConfig(
            config_name="DID_Bootstrap",
            estimator_name="DID",
            factory=_did_bootstrap_factory,
            inference="bootstrap",
            run_kwargs={"multiple_treated": "pooled"},
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=False,
        ),
    }


def all_recovery_configs() -> Dict[str, RecoveryEstimatorConfig]:
    """Point-estimate and inference-enabled recovery configs keyed by config name."""
    specs = _point_estimate_configs()
    from panel_exp.methods.tbr import TBRRidge
    from panel_exp.methods.triply_robust_est import TROP

    specs["TBRRidge"] = RecoveryEstimatorConfig(
        config_name="TBRRidge",
        estimator_name="TBRRidge",
        factory=lambda: TBRRidge(inference=None, alpha=0.05),
        inference=None,
        run_kwargs={},
        supports_significance=False,
        intervals_expected=False,
        significance_from_ci=False,
    )
    if "TBR" not in specs:
        specs["TBR"] = RecoveryEstimatorConfig(
            config_name="TBR",
            estimator_name="TBR",
            factory=lambda: TBRRidge(inference=None, alpha=0.05),
            inference=None,
            run_kwargs={},
            supports_significance=False,
            intervals_expected=False,
            significance_from_ci=False,
        )
    specs["TROP"] = RecoveryEstimatorConfig(
        config_name="TROP",
        estimator_name="TROP",
        factory=lambda: TROP(alpha=0.05),
        inference=None,
        run_kwargs={
            "lambda_unit_grid": [0.1],
            "lambda_time_grid": [0.1],
            "lambda_nuclear_grid": [0.05],
            "disable_internal_tuning": True,
            "cv_max_cycles": 1,
            "max_cv_placebos": 2,
            "show_progress": False,
        },
        supports_significance=False,
        intervals_expected=False,
        significance_from_ci=False,
    )
    specs.update(_inference_recovery_configs())
    return specs


def _extended_estimator_configs() -> Dict[str, RecoveryEstimatorConfig]:
    """Backward-compatible alias for tests and callers expecting extended specs."""
    return all_recovery_configs()


def _resolve_estimator_name(estimator: EstimatorInput) -> str:
    if isinstance(estimator, str):
        return estimator
    from panel_exp.method_registry import get_method_registry

    return get_method_registry().metadata_for_class(estimator.__name__).name


def _resolve_config_key(estimator: EstimatorInput) -> str:
    if isinstance(estimator, str) and estimator in all_recovery_configs():
        return estimator
    return _resolve_estimator_name(estimator)


def _run_simulation(
    config: RecoveryEstimatorConfig,
    world: SyntheticWorld,
    *,
    alpha: float = 0.05,
) -> SimulationRecord:
    truth = float(world.truth["true_effect"])
    try:
        estimator = config.factory()
        panel = world.to_panel_dataset()
        estimator.run_analysis(panel, **config.run_kwargs)
    except Exception as exc:
        exc_type = type(exc).__name__
        return SimulationRecord(
            predicted_effect=float("nan"),
            true_effect=truth,
            failed=True,
            failure_type=exc_type,
            failure_message=str(exc),
            intervals_available=False,
            intervals_unavailable_reason=f"run_failed:{exc_type}",
            point_estimand=POINT_ESTIMAND,
        )

    predicted = _path_relative_att(estimator, panel)
    interval = extract_recovery_interval(
        estimator,
        panel,
        alpha=alpha,
        significance_from_ci=config.significance_from_ci,
        supports_significance=config.supports_significance,
    )
    intervals_available = (
        interval.interval_aligned
        and interval.ci_lower is not None
        and interval.ci_upper is not None
        and np.isfinite(interval.ci_lower)
        and np.isfinite(interval.ci_upper)
    )
    significant = interval.significant if interval.significance_aligned else None

    failed = not np.isfinite(predicted)
    interval_reason = interval.unavailable_reason
    if config.intervals_expected and not intervals_available and interval_reason is None:
        interval_reason = "interval_estimand_mismatch"

    return SimulationRecord(
        predicted_effect=predicted,
        true_effect=truth,
        ci_lower=interval.ci_lower if interval.interval_aligned else None,
        ci_upper=interval.ci_upper if interval.interval_aligned else None,
        significant=significant,
        failed=failed,
        failure_type="non_finite_estimate" if failed else None,
        failure_message="non-finite predicted_effect" if failed else None,
        intervals_available=intervals_available if config.intervals_expected else None,
        intervals_unavailable_reason=interval_reason
        if config.intervals_expected and not intervals_available
        else None,
        point_estimand=interval.point_estimand,
        interval_estimand=interval.interval_estimand,
        interval_scale=interval.interval_scale,
        interval_aligned=interval.interval_aligned,
        significance_estimand=interval.significance_estimand,
        significance_aligned=interval.significance_aligned,
    )


class RecoveryRunner:
    """
    Run repeated synthetic recovery simulations for one estimator and scenario.

    Parameters
    ----------
    estimator : str or estimator class
        Registry name (e.g. ``SCM``, ``TBRRidge``) or config name
        (e.g. ``SCM_UnitJackKnife``).
    scenario : str or SyntheticScenario
        Recovery scenario name or explicit scenario spec.
    n_simulations : int
        Number of Monte Carlo draws.
    random_state : int
        Base seed; replication ``i`` uses ``random_state + i``.
    """

    def __init__(
        self,
        estimator: EstimatorInput,
        scenario: Union[str, SyntheticScenario],
        n_simulations: int,
        random_state: int = 0,
        *,
        alpha: float = 0.05,
        replication_seed_step: int = 1,
    ) -> None:
        self.config_key = _resolve_config_key(estimator)
        self.estimator_name = _resolve_estimator_name(estimator)
        if isinstance(scenario, str):
            self.scenario_name = scenario
            self._scenario_template = get_recovery_scenario(scenario)
        else:
            self.scenario_name = scenario.name
            self._scenario_template = scenario
        self.n_simulations = int(n_simulations)
        self.random_state = int(random_state)
        self.alpha = alpha
        self.replication_seed_step = replication_seed_step

    def run(self) -> Dict[str, Any]:
        specs = all_recovery_configs()
        if self.config_key not in specs:
            raise KeyError(
                f"Recovery config {self.config_key!r} not wired. "
                f"Known: {sorted(specs)}"
            )
        config = specs[self.config_key]

        t0 = time.perf_counter()
        records: List[SimulationRecord] = []
        last_world: Optional[SyntheticWorld] = None
        for i in range(self.n_simulations):
            seed = self.random_state + i * self.replication_seed_step
            sc = replace(self._scenario_template, random_state=seed)
            world = SyntheticWorld.generate(sc)
            last_world = world
            records.append(_run_simulation(config, world, alpha=self.alpha))

        result = aggregate_recovery_metrics(
            estimator=config.config_name,
            scenario=self.scenario_name,
            records=records,
            intervals_expected=config.intervals_expected,
        )
        elapsed = time.perf_counter() - t0
        payload = result.to_dict()
        payload["runtime_seconds"] = float(elapsed)
        payload["scored_target_estimand"] = SCORED_TARGET_ESTIMAND
        payload["point_estimand"] = payload.get("point_estimand", POINT_ESTIMAND)
        payload["predicted_effect_scoring"] = PREDICTED_EFFECT_SCORING
        payload["recovery_config"] = config.config_name
        payload["inference_mode"] = config.inference
        payload["intervals_expected"] = config.intervals_expected
        payload["scenario_recovery_support"] = get_scenario_recovery_support(
            self.scenario_name
        )
        if last_world is not None:
            dgp_meta = last_world.panel_conversion_metadata()
            donor = last_world.truth.get("donor_correlation_summary") or {}
            if isinstance(donor, dict):
                dgp_meta = {**dgp_meta, **donor}
            param = last_world.truth.get("cross_geo_correlation_param")
            if param is not None:
                dgp_meta["cross_geo_correlation_param"] = param
            payload["scenario_dgp_metadata"] = dgp_meta
        return payload


def run_recovery_battery(
    estimator: EstimatorInput,
    *,
    scenario_names: Optional[Sequence[str]] = None,
    n_simulations: int = 5,
    random_state: int = 0,
    alpha: float = 0.05,
) -> List[Dict[str, Any]]:
    """Run recovery for all (or selected) scenarios registered for an estimator."""
    name = _resolve_estimator_name(estimator)
    names = list(scenario_names) if scenario_names is not None else scenarios_for_estimator(name)
    return [
        RecoveryRunner(
            name,
            sc_name,
            n_simulations=n_simulations,
            random_state=random_state,
            alpha=alpha,
        ).run()
        for sc_name in names
    ]


def merge_validation_metadata(
    results: Dict[str, Any],
    recovery_payloads: Sequence[Mapping[str, Any]],
) -> None:
    """Attach additive validation evidence to ``results['validation_metadata']``."""
    scenarios_run: List[str] = []
    bias: Dict[str, float] = {}
    coverage: Dict[str, float] = {}
    fpr: Dict[str, float] = {}
    power: Dict[str, float] = {}

    for payload in recovery_payloads:
        sc = str(payload.get("scenario", ""))
        if sc:
            scenarios_run.append(sc)
            bias[sc] = float(payload.get("bias", float("nan")))
            coverage[sc] = float(payload.get("coverage", float("nan")))
            fpr[sc] = float(payload.get("false_positive_rate", float("nan")))
            power[sc] = float(payload.get("power", float("nan")))

    existing = dict(results.get("validation_metadata") or {})
    existing.update(
        {
            "validation_scenarios_run": scenarios_run,
            "validation_bias": bias,
            "validation_coverage": coverage,
            "validation_fpr": fpr,
            "validation_power": power,
        }
    )
    results["validation_metadata"] = existing


__all__ = [
    "RecoveryRunner",
    "RecoveryEstimatorConfig",
    "all_recovery_configs",
    "merge_validation_metadata",
    "run_recovery_battery",
    "SCORED_TARGET_ESTIMAND",
    "PREDICTED_EFFECT_SCORING",
]
