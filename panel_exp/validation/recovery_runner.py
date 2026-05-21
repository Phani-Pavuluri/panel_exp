"""
Recovery validation runner: Monte Carlo synthetic truth experiments per estimator.
"""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Type, Union

from panel_exp.validation.recovery_metrics import (
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.runner import (
    EstimatorConfig,
    _is_significant,
    _path_relative_att,
    _relative_ci,
    default_estimator_configs,
)
from panel_exp.validation.synthetic_scenarios import (
    get_recovery_scenario,
    scenarios_for_estimator,
)
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

EstimatorInput = Union[str, Type[Any]]


def _extended_estimator_configs() -> Dict[str, EstimatorConfig]:
    """Built-in configs plus TBRRidge alias and TROP (validation-only wiring)."""
    specs = {c.estimator_name: c for c in default_estimator_configs()}
    from panel_exp.methods.tbr import TBRRidge
    from panel_exp.methods.triply_robust_est import TROP

    specs["TBRRidge"] = EstimatorConfig(
        estimator_name="TBRRidge",
        factory=lambda: TBRRidge(inference=None, alpha=0.05),
        inference=None,
        run_kwargs={},
        supports_significance=False,
    )
    specs["TBR"] = EstimatorConfig(
        estimator_name="TBR",
        factory=lambda: TBRRidge(inference=None, alpha=0.05),
        inference=None,
        run_kwargs={},
        supports_significance=False,
    )
    specs["TROP"] = EstimatorConfig(
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
    )
    return specs


def _resolve_estimator_name(estimator: EstimatorInput) -> str:
    if isinstance(estimator, str):
        return estimator
    from panel_exp.method_registry import get_method_registry

    return get_method_registry().metadata_for_class(estimator.__name__).name


def _run_simulation(
    config: EstimatorConfig,
    world: SyntheticWorld,
    *,
    alpha: float = 0.05,
) -> SimulationRecord:
    truth = float(world.truth["true_effect"])
    try:
        estimator = config.factory()
        panel = world.to_panel_dataset()
        estimator.run_analysis(panel, **config.run_kwargs)
    except Exception:
        return SimulationRecord(
            predicted_effect=float("nan"),
            true_effect=truth,
        )

    predicted = _path_relative_att(estimator, panel)
    ci_lower, ci_upper = _relative_ci(estimator, panel)
    significant = (
        _is_significant(estimator, alpha=alpha)
        if config.supports_significance
        else None
    )
    return SimulationRecord(
        predicted_effect=predicted,
        true_effect=truth,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        significant=significant,
    )


class RecoveryRunner:
    """
    Run repeated synthetic recovery simulations for one estimator and scenario.

    Parameters
    ----------
    estimator : str or estimator class
        Registry name (e.g. ``SCM``, ``TBRRidge``) or ImpactAnalyzer subclass.
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
        specs = _extended_estimator_configs()
        if self.estimator_name not in specs:
            raise KeyError(
                f"Estimator {self.estimator_name!r} not wired for recovery runs. "
                f"Known: {sorted(specs)}"
            )
        config = specs[self.estimator_name]

        t0 = time.perf_counter()
        records: List[SimulationRecord] = []
        for i in range(self.n_simulations):
            seed = self.random_state + i * self.replication_seed_step
            sc = replace(self._scenario_template, random_state=seed)
            world = SyntheticWorld.generate(sc)
            records.append(_run_simulation(config, world, alpha=self.alpha))

        result = aggregate_recovery_metrics(
            estimator=self.estimator_name,
            scenario=self.scenario_name,
            records=records,
        )
        elapsed = time.perf_counter() - t0
        payload = result.to_dict()
        payload["runtime_seconds"] = float(elapsed)
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
    "merge_validation_metadata",
    "run_recovery_battery",
]
