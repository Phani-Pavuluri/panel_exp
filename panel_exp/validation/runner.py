"""
Run estimators on synthetic worlds and collect validation metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from panel_exp.panel_data import PanelDataset
from panel_exp.validation.metrics import (
    ReplicationOutcome,
    ValidationMetrics,
    aggregate_outcomes,
)
from panel_exp.validation.report import EstimatorValidationReport
from panel_exp.validation.scenarios import SCENARIO_REGISTRY, get_scenario
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

SKIPPED_ESTIMATORS = frozenset({"TROP", "Bayesian", "MTGP", "SDID"})


@dataclass(frozen=True)
class EstimatorConfig:
    estimator_name: str
    factory: Callable[[], Any]
    inference: Optional[str] = None
    run_kwargs: Dict[str, Any] = field(default_factory=dict)
    supports_significance: bool = False


def default_estimator_configs() -> List[EstimatorConfig]:
    """Stable estimators only (no optional-dep failures, no unstable SDID)."""
    from panel_exp.methods.DID import DID
    from panel_exp.methods.scm import SyntheticControl
    from panel_exp.methods.tbr import TBRRidge

    return [
        EstimatorConfig(
            estimator_name="SCM",
            factory=lambda: SyntheticControl(inference=None),
            inference=None,
            supports_significance=False,
        ),
        EstimatorConfig(
            estimator_name="TBR",
            factory=lambda: TBRRidge(inference=None),
            inference=None,
            supports_significance=False,
        ),
        EstimatorConfig(
            estimator_name="DID",
            factory=lambda: DID(),
            inference=None,
            run_kwargs={"multiple_treated": "pooled"},
            supports_significance=True,
        ),
    ]


def _path_relative_att(estimator, panel: PanelDataset) -> float:
    """Path-based mean relative post-period ATT from exported y / y_hat."""
    results = getattr(estimator, "results", None) or {}
    y = np.asarray(results.get("y", []), dtype=float)
    y_hat = np.asarray(results.get("y_hat", []), dtype=float)
    if y.size and y_hat.size:
        if y.ndim == 2:
            y = np.nanmean(y, axis=1)
        if y_hat.ndim == 2:
            y_hat = np.nanmean(y_hat, axis=1)
        y = y.ravel()
        y_hat = y_hat.ravel()

        start = panel.treated_start_idxs[0]
        n_times = panel.num_timepoints
        n_post = n_times - start

        if len(y) == n_times and len(y_hat) == n_times:
            y_post, yh_post = y[start:], y_hat[start:]
        elif len(y_hat) == n_post:
            y_post = y[start:] if len(y) == n_times else y[-n_post:]
            yh_post = y_hat
        else:
            n_align = min(len(y), len(y_hat), n_post)
            y_post = y[-n_align:]
            yh_post = y_hat[-n_align:]

        mask = np.isfinite(y_post) & np.isfinite(yh_post) & (yh_post != 0)
        if np.any(mask):
            return float(np.mean((y_post[mask] - yh_post[mask]) / yh_post[mask]))

    if hasattr(estimator, "summary"):
        try:
            summary = estimator.summary()
            rel = float(summary.loc["Relative Effect", "Average"])
            if np.isfinite(rel):
                return rel / 100.0
        except Exception:
            pass

    return float("nan")


def _relative_ci(
    estimator, panel: PanelDataset
) -> Tuple[Optional[float], Optional[float]]:
    ci = getattr(estimator, "treatment_ci", None)
    if ci is None:
        return None, None
    try:
        lo, hi = float(ci[0]), float(ci[1])
    except (TypeError, ValueError, IndexError):
        return None, None
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return None, None

    results = getattr(estimator, "results", None) or {}
    y_hat = np.asarray(results.get("y_hat", []), dtype=float).ravel()
    if y_hat.size == 0:
        return None, None
    start = panel.treated_start_idxs[0]
    yh_post = y_hat[start:]
    mean_cf = float(np.nanmean(yh_post))
    if not np.isfinite(mean_cf) or mean_cf == 0:
        return None, None

    n_post = int(np.sum(np.isfinite(yh_post)))
    if n_post <= 0:
        return None, None
    return lo / (n_post * mean_cf), hi / (n_post * mean_cf)


def _is_significant(estimator, alpha: float) -> Optional[bool]:
    pvalue = getattr(estimator, "treatment_pvalue", None)
    if pvalue is None:
        results = getattr(estimator, "results", None) or {}
        pvalue = results.get("p_value")
    if pvalue is None:
        return None
    try:
        return bool(float(pvalue) < alpha)
    except (TypeError, ValueError):
        return None


def _run_replication(
    config: EstimatorConfig,
    world: SyntheticWorld,
    *,
    alpha: float,
) -> ReplicationOutcome:
    truth = float(world.truth["true_effect"])
    try:
        estimator = config.factory()
        panel = world.to_panel_dataset()
        estimator.run_analysis(panel, **config.run_kwargs)
    except Exception as exc:
        return ReplicationOutcome(
            estimate=float("nan"),
            truth=truth,
            failed=True,
            error_message=str(exc),
        )

    estimate = _path_relative_att(estimator, panel)
    ci_lower, ci_upper = _relative_ci(estimator, panel)
    significant: Optional[bool] = None
    if config.supports_significance and ci_lower is not None and ci_upper is not None:
        significant = _is_significant(estimator, alpha)

    return ReplicationOutcome(
        estimate=estimate,
        truth=truth,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        significant=significant,
        failed=not np.isfinite(estimate),
        error_message=None if np.isfinite(estimate) else "non-finite estimate",
    )


class EstimatorValidationRunner:
    """Run synthetic-truth validation across scenarios and estimator configs."""

    def __init__(
        self,
        *,
        scenarios: Optional[Sequence[SyntheticScenario]] = None,
        estimator_configs: Optional[Sequence[EstimatorConfig]] = None,
        n_replications: int = 1,
        random_state: int = 0,
        replication_seed_step: int = 1,
        alpha: float = 0.05,
    ) -> None:
        self.scenarios = (
            list(scenarios)
            if scenarios is not None
            else list(SCENARIO_REGISTRY.values())
        )
        self.estimator_configs = (
            list(estimator_configs)
            if estimator_configs is not None
            else default_estimator_configs()
        )
        self.n_replications = n_replications
        self.random_state = random_state
        self.replication_seed_step = replication_seed_step
        self.alpha = alpha

    def run(self) -> EstimatorValidationReport:
        metrics: List[ValidationMetrics] = []
        failures: List[Dict[str, str]] = []
        warnings: List[str] = []

        for scenario in self.scenarios:
            for config in self.estimator_configs:
                if config.estimator_name in SKIPPED_ESTIMATORS:
                    continue
                outcomes: List[ReplicationOutcome] = []
                base_seed = (
                    scenario.random_state
                    if scenario.random_state is not None
                    else self.random_state
                )
                for rep in range(self.n_replications):
                    rep_scenario = replace(
                        scenario,
                        random_state=int(base_seed)
                        + rep * self.replication_seed_step,
                    )
                    world = SyntheticWorld.generate(rep_scenario)
                    outcome = _run_replication(
                        config, world, alpha=self.alpha
                    )
                    outcomes.append(outcome)
                    if outcome.failed:
                        failures.append(
                            {
                                "estimator_name": config.estimator_name,
                                "scenario_name": scenario.name,
                                "replication": str(rep),
                                "error": outcome.error_message or "unknown",
                            }
                        )

                metrics.append(
                    aggregate_outcomes(
                        estimator_name=config.estimator_name,
                        scenario_name=scenario.name,
                        outcomes=outcomes,
                    )
                )

        if not metrics:
            warnings.append("No validation metrics produced")

        return EstimatorValidationReport.build(
            scenarios=self.scenarios,
            estimator_configs=self.estimator_configs,
            metrics=metrics,
            failures=failures,
            warnings=warnings,
        )


# Convenience helpers (not wired into production paths)
def run_scenario_validation(
    scenario: SyntheticScenario,
    *,
    estimator_configs: Optional[Sequence[EstimatorConfig]] = None,
    n_replications: int = 1,
    random_state: int = 0,
) -> List[ValidationMetrics]:
    runner = EstimatorValidationRunner(
        scenarios=[scenario],
        estimator_configs=estimator_configs,
        n_replications=n_replications,
        random_state=random_state,
    )
    return runner.run().metrics


def run_estimator_validation(
    *,
    scenario_names: Optional[Sequence[str]] = None,
    estimator_names: Optional[Sequence[str]] = None,
    n_replications: int = 1,
    random_state: int = 0,
) -> EstimatorValidationReport:
    scenarios = (
        [get_scenario(n) for n in scenario_names]
        if scenario_names is not None
        else list(SCENARIO_REGISTRY.values())
    )
    configs = default_estimator_configs()
    if estimator_names is not None:
        names = set(estimator_names)
        configs = [c for c in configs if c.estimator_name in names]
    return EstimatorValidationRunner(
        scenarios=scenarios,
        estimator_configs=configs,
        n_replications=n_replications,
        random_state=random_state,
    ).run()
