"""
Run estimators on synthetic worlds and collect validation metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from panel_exp.panel_data import PanelDataset
from panel_exp.validation.metrics import (
    ReplicationRecord,
    ValidationResult,
    aggregate_replications,
)
from panel_exp.validation.report import EstimatorValidationReport
from panel_exp.validation.scenarios import SCENARIO_REGISTRY, get_scenario
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

# Estimators intentionally excluded until baseline framework is stable:
# TROP, Bayesian, MTGP
SKIPPED_ESTIMATORS = frozenset({"TROP", "Bayesian", "MTGP"})

SUPPORTED_ESTIMATORS = ("SCM", "TBR", "DID", "SDID")


@dataclass(frozen=True)
class EstimatorSpec:
    name: str
    factory: Callable[[], Any]
    run_kwargs: Dict[str, Any]
    supports_significance: bool = True


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
    estimator,
    panel: PanelDataset,
    estimate: float,
) -> Tuple[Optional[float], Optional[float]]:
    """Map estimator CI to relative scale when possible."""
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

    name = estimator.__class__.__name__
    if name in ("SyntheticDID",):
        return lo / mean_cf, hi / mean_cf

    n_post = int(np.sum(np.isfinite(yh_post)))
    if n_post <= 0:
        return None, None
    # DID stores cumulative path CI; normalize to relative mean.
    return lo / (n_post * mean_cf), hi / (n_post * mean_cf)


def _is_significant(estimator, alpha: float = 0.05) -> Optional[bool]:
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


def _build_estimator_specs() -> Dict[str, EstimatorSpec]:
    from panel_exp.methods.DID import DID
    from panel_exp.methods.scm import SyntheticControl
    from panel_exp.methods.synthetic_did import SyntheticDID
    from panel_exp.methods.tbr import TBRRidge

    return {
        "SCM": EstimatorSpec(
            name="SCM",
            factory=lambda: SyntheticControl(inference=None, alpha=0.05),
            run_kwargs={},
            supports_significance=False,
        ),
        "TBR": EstimatorSpec(
            name="TBR",
            factory=lambda: TBRRidge(inference=None, alpha=0.05),
            run_kwargs={},
            supports_significance=False,
        ),
        "DID": EstimatorSpec(
            name="DID",
            factory=lambda: DID(alpha=0.05),
            run_kwargs={"multiple_treated": "pooled"},
            supports_significance=True,
        ),
        "SDID": EstimatorSpec(
            name="SDID",
            factory=lambda: SyntheticDID(
                use_uniform_lambda=True,
                variance_method="time_block_bootstrap",
                n_bootstrap=30,
                alpha=0.05,
            ),
            run_kwargs={},
            supports_significance=True,
        ),
    }


def _run_single(
    spec: EstimatorSpec,
    world: SyntheticWorld,
    *,
    alpha: float = 0.05,
) -> ReplicationRecord:
    estimator = spec.factory()
    try:
        estimator.run_analysis(world.panel, **spec.run_kwargs)
    except Exception:
        return ReplicationRecord(
            estimate=float("nan"),
            truth=world.truth_mean_relative_att,
        )

    estimate = _path_relative_att(estimator, world.panel)
    ci_lower, ci_upper = _relative_ci(estimator, world.panel, estimate)
    significant = (
        _is_significant(estimator, alpha=alpha)
        if spec.supports_significance
        else None
    )
    return ReplicationRecord(
        estimate=estimate,
        truth=world.truth_mean_relative_att,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        significant=significant,
    )


def run_scenario_validation(
    scenario: SyntheticScenario,
    *,
    estimators: Optional[Sequence[str]] = None,
    n_replications: int = 1,
    alpha: float = 0.05,
    replication_seed_step: int = 1,
) -> List[ValidationResult]:
    """
    Run validation for one scenario across estimators.

    Each replication bumps ``random_state`` by ``replication_seed_step`` so runs
    are deterministic but not identical.
    """
    specs = _build_estimator_specs()
    names = list(estimators) if estimators is not None else list(SUPPORTED_ESTIMATORS)
    results: List[ValidationResult] = []

    for name in names:
        if name in SKIPPED_ESTIMATORS:
            continue
        if name not in specs:
            continue
        spec = specs[name]
        records: List[ReplicationRecord] = []
        for rep in range(n_replications):
            rep_scenario = replace(
                scenario,
                random_state=scenario.random_state + rep * replication_seed_step,
            )
            world = SyntheticWorld.generate(rep_scenario)
            records.append(_run_single(spec, world, alpha=alpha))

        results.append(
            aggregate_replications(
                estimator_name=name,
                scenario_name=scenario.scenario_name,
                records=records,
            )
        )
    return results


def run_estimator_validation(
    *,
    scenario_names: Optional[Sequence[str]] = None,
    estimators: Optional[Sequence[str]] = None,
    n_replications: int = 5,
    alpha: float = 0.05,
) -> EstimatorValidationReport:
    """Run the full validation battery and return a JSON-serializable report."""
    names = (
        list(scenario_names)
        if scenario_names is not None
        else list(SCENARIO_REGISTRY.keys())
    )
    all_results: List[ValidationResult] = []
    warnings: List[str] = []

    for scenario_name in names:
        scenario = get_scenario(scenario_name)
        try:
            batch = run_scenario_validation(
                scenario,
                estimators=estimators,
                n_replications=n_replications,
                alpha=alpha,
            )
            all_results.extend(batch)
        except Exception as exc:
            warnings.append(f"Scenario {scenario_name} failed: {exc}")

    assumptions = [
        "Truth metric is mean post-period relative lift on treated units.",
        "Estimates use path-based mean relative ATT from exported y and y_hat.",
        "Results describe recovery under tested scenarios only; not general correctness.",
        "TROP, Bayesian, and MTGP are excluded from this validation pass.",
    ]
    return EstimatorValidationReport.build(
        scenario_names=names,
        results=all_results,
        warnings=warnings,
        assumptions=assumptions,
    )
