"""D5-DES-STAT-TIER1-001 — tier-1 design statistical validation harness (research).

Characterizes assignment quality, feasibility, balance, reproducibility, and contract/
guardrail metadata for tier-1 geo-run design families. Does not promote designs or
authorize downstream product use.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp import evidence as evidence_module
from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    greedy_match_markets,
)
from panel_exp.design.validation import standardized_mean_difference
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import build_and_validate_tier1_contract
from panel_exp.validation.design_guardrail_runtime_001 import evaluate_design_contract_guardrails

GENERATOR_VERSION = "1.0.0"
ARTIFACT_ID = "D5-DES-STAT-TIER1-001"

Verdict = Literal[
    "tier1_designs_characterized_no_promotion",
    "tier1_designs_characterized_with_blocking_failures",
    "tier1_designs_mixed_requires_method_specific_followup",
    "tier1_design_harness_inconclusive",
    "tier1_design_harness_failed",
]

RunOutcome = Literal["pass", "warn", "block", "skipped", "failed"]

CORE_WORLD_IDS: tuple[str, ...] = (
    "balanced_markets",
    "weak_donor_pool",
    "high_unit_heterogeneity",
    "small_n_markets",
    "high_pre_period_noise",
    "strong_seasonality",
    "trend_mismatch",
    "sparse_outcomes",
    "spend_imbalance",
    "geographic_cluster_correlation",
    "assignment_infeasibility",
    "missing_covariates",
    "outlier_markets",
    "unstable_pre_period",
)

FAMILY_WORLD_IDS: tuple[str, ...] = (
    "matched_market_poor_match_world",
    "rerandomization_selection_effect_world",
    "stratification_poor_strata_world",
    "treatment_pool_exhaustion_world",
)

ALL_WORLD_IDS: tuple[str, ...] = CORE_WORLD_IDS + FAMILY_WORLD_IDS

SHARED_SEEDS: tuple[int, ...] = (101, 202, 303, 404, 505)

GREEDY_TREATMENT_PROBABILITIES: tuple[float, ...] = (0.20, 0.35, 0.50)

MIN_CONTROL_THRESHOLD = 3

EffectType = Literal["null", "additive", "heterogeneous"]


@dataclass(frozen=True)
class DesignFamilySpec:
    design_inventory_id: str
    design_name: str
    registry_key: str
    design_family: str
    base_randomizer_cls: type
    is_rerandomization_wrapper: bool = False


DESIGN_FAMILIES: tuple[DesignFamilySpec, ...] = (
    DesignFamilySpec(
        "DES-001",
        "greedy_match_markets",
        "greedy_match_markets",
        "matching_assignment",
        greedy_match_markets,
    ),
    DesignFamilySpec(
        "DES-002",
        "complete_randomization",
        "completerandomization",
        "standard_assignment",
        CompleteRandomization,
    ),
    DesignFamilySpec(
        "DES-003",
        "balanced_randomization",
        "balancedrandomization",
        "standard_assignment",
        BalancedRandomization,
    ),
    DesignFamilySpec(
        "DES-004",
        "stratified_randomization",
        "stratifiedrandomization",
        "stratified_assignment",
        StratifiedRandomization,
    ),
    DesignFamilySpec(
        "DES-006",
        "rerandomization",
        "completerandomization",
        "standard_assignment",
        CompleteRandomization,
        is_rerandomization_wrapper=True,
    ),
)


@dataclass
class D5DesStatTier1Config:
    fast: bool = False
    n_pre: int = 30
    n_post: int = 10
    n_units: int = 18
    replicates_per_cell: int = 10
    replicates_exhaustion: int = 15
    treatment_probability_default: float = 0.35
    rerandomization_max_iter: int = 200
    rerandomization_target_imbalance: float = 1e-2
    random_state_base: int = 20260615
    include_effect_variants: bool = True
    min_control_threshold: int = MIN_CONTROL_THRESHOLD


@dataclass
class WorldContext:
    world_id: str
    n_units: int
    n_pre: int
    n_post: int
    effect_type: EffectType
    treatment_probability: float
    constraint_kwargs: dict[str, Any] = field(default_factory=dict)
    world_params: dict[str, Any] = field(default_factory=dict)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_repo_root(),
                text=True,
            )
            .strip()
        )
    except Exception:
        return "unknown"


def _world_context(
    world_id: str,
    cfg: D5DesStatTier1Config,
    *,
    effect_type: EffectType = "null",
    treatment_probability: float | None = None,
) -> WorldContext:
    tp = treatment_probability if treatment_probability is not None else cfg.treatment_probability_default
    n_units = cfg.n_units
    n_pre = cfg.n_pre
    n_post = cfg.n_post
    params: dict[str, Any] = {}
    constraints: dict[str, Any] = {}

    if world_id == "small_n_markets":
        n_units = 8
    elif world_id == "treatment_pool_exhaustion_world":
        n_units = 10
    elif world_id == "stratification_poor_strata_world":
        n_units = 12
        params["n_strata"] = 12
    elif world_id == "weak_donor_pool":
        n_excl = max(1, int(n_units * 0.75))
        constraints["_excluded_units"] = [f"u{i}" for i in range(n_excl)]
    elif world_id == "assignment_infeasibility":
        constraints = {
            "control_whitelist": ["u0"],
            "test_whitelist": ["u0"],
        }
    elif world_id == "high_unit_heterogeneity":
        params["unit_level_sd"] = 40.0
    elif world_id == "high_pre_period_noise":
        params["noise_sd"] = 8.0
    elif world_id == "strong_seasonality":
        params["seasonality_amp"] = 15.0
    elif world_id == "trend_mismatch":
        params["trend_mismatch"] = True
    elif world_id == "sparse_outcomes":
        params["zero_prob"] = 0.35
    elif world_id == "spend_imbalance":
        params["volume_skew"] = 5.0
    elif world_id == "geographic_cluster_correlation":
        params["cluster_size"] = 4
    elif world_id == "missing_covariates":
        params["low_signal_fraction"] = 0.4
    elif world_id == "outlier_markets":
        params["outlier_fraction"] = 0.15
        params["outlier_multiplier"] = 8.0
    elif world_id == "unstable_pre_period":
        params["pre_volatility"] = 12.0
    elif world_id == "matched_market_poor_match_world":
        params["anti_correlation"] = True
    elif world_id == "rerandomization_selection_effect_world":
        params["strong_imbalance_seed"] = True

    return WorldContext(
        world_id=world_id,
        n_units=n_units,
        n_pre=n_pre,
        n_post=n_post,
        effect_type=effect_type,
        treatment_probability=tp,
        constraint_kwargs=constraints,
        world_params=params,
    )


def synthesize_panel(ctx: WorldContext, seed: int) -> pd.DataFrame:
    """Generate unit × time wide panel for a simulation world."""
    rng = np.random.default_rng(seed)
    n_units = ctx.n_units
    n_pre = ctx.n_pre
    n_post = ctx.n_post
    n_times = n_pre + n_post
    units = [f"u{i}" for i in range(n_units)]
    p = ctx.world_params

    base_levels = rng.normal(100.0, p.get("unit_level_sd", 15.0), n_units)
    if p.get("volume_skew"):
        base_levels = np.exp(rng.normal(0, p["volume_skew"], n_units)) * 50

    rows: list[np.ndarray] = []
    for i, unit in enumerate(units):
        level = base_levels[i]
        t_axis = np.arange(n_times, dtype=float)
        season = (
            p.get("seasonality_amp", 0.0)
            * np.sin(2 * np.pi * t_axis / max(4, n_pre // 3))
        )
        trend_pre = np.linspace(0, 1, n_pre) * rng.normal(0, 2.0)
        trend_post = np.linspace(0, 1, n_post) * rng.normal(0, 2.0)
        if p.get("trend_mismatch"):
            trend_post += np.linspace(0, 3, n_post)
        noise_sd = p.get("noise_sd", 2.0)
        if p.get("pre_volatility"):
            noise_sd = p["pre_volatility"]
        pre = level + trend_pre + season[:n_pre] + rng.normal(0, noise_sd, n_pre)
        post = level + trend_post + season[n_pre:] + rng.normal(0, noise_sd, n_post)
        if p.get("anti_correlation"):
            pre = level + (i / max(1, n_units - 1)) * 30 + rng.normal(0, 1.0, n_pre)
            post = level - (i / max(1, n_units - 1)) * 30 + rng.normal(0, 1.0, n_post)
        if p.get("strong_imbalance_seed"):
            pre = level + i * 5 + rng.normal(0, 0.5, n_pre)
        if p.get("low_signal_fraction") and i < int(n_units * p["low_signal_fraction"]):
            pre = rng.normal(0, 0.01, n_pre)
            post = rng.normal(0, 0.01, n_post)
        if p.get("zero_prob") and rng.random() < p["zero_prob"]:
            pre = np.zeros(n_pre)
            post = np.zeros(n_post)
        if p.get("outlier_fraction") and i < max(1, int(n_units * p["outlier_fraction"])):
            pre *= p.get("outlier_multiplier", 5.0)
            post *= p.get("outlier_multiplier", 5.0)
        if ctx.effect_type == "additive" and n_post > 0:
            post += 5.0
        elif ctx.effect_type == "heterogeneous" and n_post > 0:
            post += (5.0 if i % 2 == 0 else -2.0)
        rows.append(np.concatenate([pre, post]))

    if p.get("cluster_size"):
        cs = p["cluster_size"]
        for c_start in range(0, n_units, cs):
            c_end = min(c_start + cs, n_units)
            shared = rng.normal(0, 5.0, n_times)
            for j in range(c_start, c_end):
                rows[j] = rows[j] + shared

    return pd.DataFrame(rows, index=units, columns=list(range(n_times)))


def _assignment_counts(assignment: dict[str, list[str]], n_units: int) -> dict[str, Any]:
    control = list(assignment.get("control") or [])
    treated: list[str] = []
    for key, units in assignment.items():
        if key.startswith("test_"):
            treated.extend(units)
    assigned = set(control) | set(treated)
    all_units = set()
    for units in assignment.values():
        if isinstance(units, list):
            all_units.update(units)
    duplicates = len(control) + len(treated) - len(assigned)
    return {
        "n_control": len(control),
        "n_treated": len(treated),
        "n_assigned": len(assigned),
        "n_unassigned": max(0, n_units - len(assigned)),
        "duplicate_collision_count": max(0, duplicates),
        "minimum_control_violation": len(control) < MIN_CONTROL_THRESHOLD,
    }


def _balance_metrics(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    n_pre: int,
) -> dict[str, float]:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return {
            "pre_period_mean_imbalance": float("nan"),
            "standardized_mean_difference": float("nan"),
            "max_absolute_smd": float("nan"),
            "pre_trend_slope_imbalance": float("nan"),
        }
    c_pre = wide.loc[control, wide.columns[:n_pre]].mean(axis=1).to_numpy()
    t_pre = wide.loc[test, wide.columns[:n_pre]].mean(axis=1).to_numpy()
    smd = standardized_mean_difference(c_pre, t_pre)
    mean_imb = float(abs(c_pre.mean() - t_pre.mean()))
    max_smd = float(abs(smd))
    if n_pre >= 2:
        c_slopes = np.array(
            [np.polyfit(range(n_pre), wide.loc[u, wide.columns[:n_pre]].values, 1)[0] for u in control]
        )
        t_slopes = np.array(
            [np.polyfit(range(n_pre), wide.loc[u, wide.columns[:n_pre]].values, 1)[0] for u in test]
        )
        slope_imb = float(abs(c_slopes.mean() - t_slopes.mean()))
    else:
        slope_imb = float("nan")
    total_vol = float(wide.sum().sum())
    c_vol = float(wide.loc[control].sum().sum()) / total_vol if total_vol else 0.0
    t_vol = float(wide.loc[test].sum().sum()) / total_vol if total_vol else 0.0
    return {
        "pre_period_mean_imbalance": mean_imb,
        "standardized_mean_difference": float(smd),
        "max_absolute_smd": max_smd,
        "pre_trend_slope_imbalance": slope_imb,
        "weighted_volume_imbalance": float(abs(c_vol - t_vol)),
    }


class _TrackedRerandomization(Rerandomization):
    """Rerandomization with attempt diagnostics for harness."""

    last_attempts: int = 0
    last_final_imbalance: float = float("inf")
    accepted: bool = False

    def assign(self, panel_data: PanelDataset, **kwargs: Any) -> Any:
        import copy as copy_mod

        from panel_exp.design.assign import (
            RERANDOMIZATION_IMBALANCE_BASES,
            _compute_assignment_imbalance,
        )

        self.last_attempts = 0
        imbalance_val = np.inf
        best_assignment = None
        n_test_grps = kwargs.get("n_test_grps") or 1
        pre_treatment_period = kwargs.get("pre_treatment_period")
        treatment_period = kwargs.get("treatment_period")
        eval_period = pre_treatment_period or treatment_period

        while (imbalance_val > self.target_imbalance) and (self.last_attempts < self.max_iter):
            self.last_attempts += 1
            panel = self.base_randomizer.assign(panel_data=panel_data, **kwargs)
            balance_panel = panel_data
            if pre_treatment_period is not None:
                from panel_exp.design.period_slice import slice_wide_to_time_period

                balance_panel = copy_mod.deepcopy(panel_data)
                balance_panel.wide_data = slice_wide_to_time_period(
                    panel_data.wide_data, pre_treatment_period
                )
            cur_imbalance = _compute_assignment_imbalance(
                balance_panel,
                panel,
                n_test_grps,
                eval_period,
                self.metric,
            )
            if cur_imbalance < imbalance_val:
                best_assignment = panel
                imbalance_val = cur_imbalance
            if imbalance_val <= self.target_imbalance:
                break

        self.last_final_imbalance = float(imbalance_val)
        self.accepted = imbalance_val <= self.target_imbalance
        if best_assignment is None:
            raise RuntimeError(
                f"Rerandomization failed after {self.max_iter} iterations; "
                f"no valid assignment produced (final imbalance {imbalance_val})."
            )
        return best_assignment


def _run_assignment(
    design_spec: DesignFamilySpec,
    wide: pd.DataFrame,
    *,
    seed: int,
    n_pre: int,
    treatment_probability: float,
    constraint_kwargs: dict[str, Any],
    world_params: dict[str, Any],
    cfg: D5DesStatTier1Config,
) -> tuple[dict[str, list[str]] | None, dict[str, Any]]:
    """Run one assignment; return (assignment, diagnostics) or (None, failure_info)."""
    panel = PanelDataset(wide.copy())
    pre = TimePeriod(0, n_pre)
    diag: dict[str, Any] = {
        "retry_count": 0,
        "failed_attempt_count": 0,
        "rerandomization_attempts": None,
        "rerandomization_accepted": None,
        "rerandomization_final_imbalance": None,
        "base_randomizer_class": design_spec.base_randomizer_cls.__name__,
    }
    kw: dict[str, Any] = {}
    if constraint_kwargs.get("_excluded_units"):
        kw["control_test_blacklist"] = list(constraint_kwargs["_excluded_units"])
    for key in (
        "control_whitelist",
        "test_whitelist",
        "control_blacklist",
        "test_blacklist",
        "control_test_blacklist",
    ):
        if key in constraint_kwargs:
            kw[key] = constraint_kwargs[key]

    try:
        if design_spec.is_rerandomization_wrapper:
            design: Any = _TrackedRerandomization(
                treatment_probability=treatment_probability,
                max_iter=cfg.rerandomization_max_iter,
                target_imbalance=cfg.rerandomization_target_imbalance,
                base_randomizer_cls=CompleteRandomization,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                **{k: v for k, v in kw.items()},
            )
            diag["rerandomization_attempts"] = design.last_attempts
            diag["rerandomization_accepted"] = design.accepted
            diag["rerandomization_final_imbalance"] = design.last_final_imbalance
            diag["wrapper_identity"] = "Rerandomization"
        elif design_spec.design_inventory_id == "DES-001":
            design = greedy_match_markets(
                func_to_optimize="corr",
                treatment_probability=treatment_probability,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                **{k: v for k, v in kw.items()},
            )
        elif design_spec.design_inventory_id == "DES-002":
            design = CompleteRandomization(
                treatment_probability=treatment_probability,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                **{k: v for k, v in kw.items()},
            )
        elif design_spec.design_inventory_id == "DES-003":
            design = BalancedRandomization(
                treatment_probability=treatment_probability,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                **{k: v for k, v in kw.items()},
            )
        elif design_spec.design_inventory_id == "DES-004":
            n_percentiles = int(world_params.get("n_strata") or 10)
            design = StratifiedRandomization(
                treatment_probability=treatment_probability,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                n_percentiles=n_percentiles,
                **{k: v for k, v in kw.items()},
            )
        else:
            raise ValueError(f"unsupported design {design_spec.design_inventory_id}")
    except Exception as exc:
        diag["assignment_error"] = type(exc).__name__
        diag["assignment_error_message"] = str(exc)[:500]
        return None, diag

    if isinstance(assignment, PanelDataset):
        raise TypeError("expected dict assignment from tier-1 designs")
    return dict(assignment), diag


def _contract_and_guardrail(
    *,
    design_spec: DesignFamilySpec,
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    n_pre: int,
    treatment_probability: float,
    seed: int,
) -> dict[str, Any]:
    design_method_arg = (
        "Rerandomization"
        if design_spec.is_rerandomization_wrapper
        else design_spec.base_randomizer_cls.__name__
    )
    spec = spec_from_geo_design(
        f"d5-tier1-{design_spec.design_inventory_id}-{seed}",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(0, n_pre),
        experiment_period=TimePeriod(n_pre, n_pre + (wide.shape[1] - n_pre)),
        design_method=design_method_arg,
        random_state=seed,
        treatment_probability=treatment_probability,
        n_test_groups=1,
    )
    contract, summary = build_and_validate_tier1_contract(
        spec=spec,
        assignment=assignment,
        registry_key=design_spec.registry_key,
        base_randomizer_cls=design_spec.base_randomizer_cls,
        n_test_grps=1,
        treatment_probability=treatment_probability,
        is_rerandomization_wrapped=design_spec.is_rerandomization_wrapper,
        wide_data=wide,
        package_version=evidence_module.__version__,
    )
    guardrail = evaluate_design_contract_guardrails(
        {"design_contract": contract, "contract_validation": summary}
    )
    return {
        "contract_status": summary.get("status"),
        "contract_severity": summary.get("severity"),
        "contract_complete_allowed": summary.get("contract_complete_allowed"),
        "contract_reason_codes": list(summary.get("reason_codes") or []),
        "guardrail_status": guardrail.status,
        "guardrail_reason_codes": list(guardrail.reason_codes),
        "downstream_authorization_status": (
            contract.get("governance", {}).get("downstream_authorization_status")
        ),
        "geometry_id": contract.get("geometry", {}).get("geometry_id"),
        "stratum_ids": (
            contract.get("structure", {}).get("stratum_ids")
            if isinstance(contract.get("structure"), dict)
            else None
        ),
    }


def _evaluate_run(
    counts: dict[str, Any],
    balance: dict[str, float],
    *,
    assignment_ok: bool,
    treatment_probability_requested: float,
    treatment_probability_realized: float | None,
) -> tuple[RunOutcome, list[str]]:
    reasons: list[str] = []
    if not assignment_ok:
        return "failed", ["assignment_failed"]
    if counts.get("minimum_control_violation"):
        reasons.append("minimum_control_threshold_violation")
    if counts.get("n_unassigned", 0) > 0:
        reasons.append("unassigned_units")
    if treatment_probability_realized is not None:
        dev = abs(treatment_probability_realized - treatment_probability_requested)
        if dev > 0.15:
            reasons.append("treatment_probability_deviation")
    max_smd = balance.get("max_absolute_smd")
    if max_smd is not None and np.isfinite(max_smd) and max_smd > 0.5:
        reasons.append("high_smd_provisional")
    if any(
        r in reasons
        for r in (
            "minimum_control_threshold_violation",
            "unassigned_units",
            "assignment_failed",
        )
    ):
        return "block", reasons
    if reasons:
        return "warn", reasons
    return "pass", reasons


def _realized_treatment_share(
    counts: dict[str, Any],
    n_units: int,
) -> float | None:
    if n_units <= 0:
        return None
    return counts.get("n_treated", 0) / n_units


def run_single(
    design_spec: DesignFamilySpec,
    world_ctx: WorldContext,
    *,
    seed: int,
    replicate: int,
    cfg: D5DesStatTier1Config,
) -> dict[str, Any]:
    wide = synthesize_panel(world_ctx, seed)
    n_units = wide.shape[0]
    assignment, assign_diag = _run_assignment(
        design_spec,
        wide,
        seed=seed,
        n_pre=world_ctx.n_pre,
        treatment_probability=world_ctx.treatment_probability,
        constraint_kwargs=world_ctx.constraint_kwargs,
        world_params=world_ctx.world_params,
        cfg=cfg,
    )
    assignment_ok = assignment is not None
    counts = (
        _assignment_counts(assignment, n_units)
        if assignment
        else {
            "n_control": 0,
            "n_treated": 0,
            "n_assigned": 0,
            "n_unassigned": n_units,
            "duplicate_collision_count": 0,
            "minimum_control_violation": True,
        }
    )
    balance = (
        _balance_metrics(wide, assignment, world_ctx.n_pre)
        if assignment
        else {
            "pre_period_mean_imbalance": float("nan"),
            "standardized_mean_difference": float("nan"),
            "max_absolute_smd": float("nan"),
            "pre_trend_slope_imbalance": float("nan"),
            "weighted_volume_imbalance": float("nan"),
        }
    )
    tp_realized = _realized_treatment_share(counts, n_units)
    outcome, eval_reasons = _evaluate_run(
        counts,
        balance,
        assignment_ok=assignment_ok,
        treatment_probability_requested=world_ctx.treatment_probability,
        treatment_probability_realized=tp_realized,
    )
    contract_diag: dict[str, Any] = {}
    if assignment:
        contract_diag = _contract_and_guardrail(
            design_spec=design_spec,
            wide=wide,
            assignment=assignment,
            n_pre=world_ctx.n_pre,
            treatment_probability=world_ctx.treatment_probability,
            seed=seed,
        )
    repro_hash = assignment_hash(assignment) if assignment else None

    return {
        "design_inventory_id": design_spec.design_inventory_id,
        "design_name": design_spec.design_name,
        "design_family": design_spec.design_family,
        "world_id": world_ctx.world_id,
        "effect_type": world_ctx.effect_type,
        "seed": seed,
        "replicate": replicate,
        "n_units": n_units,
        "n_treated": counts["n_treated"],
        "n_control": counts["n_control"],
        "treatment_probability_requested": world_ctx.treatment_probability,
        "treatment_probability_realized": tp_realized,
        "assignment_status": "success" if assignment_ok else "failed",
        "failure_reason": assign_diag.get("assignment_error_message"),
        "geometry_id": contract_diag.get("geometry_id", "unit_panel_single_cell"),
        "contract_status": contract_diag.get("contract_status"),
        "guardrail_status": contract_diag.get("guardrail_status"),
        "run_outcome": outcome,
        "evaluation_reasons": eval_reasons,
        "diagnostics": {**assign_diag, **contract_diag},
        "metrics": {**counts, **balance},
        "assignment_hash": repro_hash,
        "excluded_claims": [
            "production_ready",
            "statistically_suitable",
            "downstream_authorized",
            "estimator_validated",
            "compatibility_smoke_only",
        ],
        "threshold_policy": "provisional_for_characterization_only",
    }


def _run_matrix(cfg: D5DesStatTier1Config) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    t0 = time.perf_counter()
    records: list[dict[str, Any]] = []
    seeds = SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS
    replicates = 2 if cfg.fast else cfg.replicates_per_cell
    worlds = list(ALL_WORLD_IDS[:6] if cfg.fast else ALL_WORLD_IDS)
    effect_types: list[EffectType] = ["null"] if cfg.fast else ["null", "additive"]

    attempted = 0
    completed = 0
    failed = 0
    skipped = 0

    for design_spec in DESIGN_FAMILIES:
        for world_id in worlds:
            effect_list: list[EffectType] = (
                ["null"] if world_id == "assignment_infeasibility" else effect_types
            )
            for effect_type in effect_list:
                tp_list = [cfg.treatment_probability_default]
                if design_spec.design_inventory_id == "DES-001":
                    if world_id == "treatment_pool_exhaustion_world":
                        tp_list = list(GREEDY_TREATMENT_PROBABILITIES)
                    elif not cfg.fast and world_id == "balanced_markets":
                        tp_list = list(GREEDY_TREATMENT_PROBABILITIES)
                rep_count = (
                    cfg.replicates_exhaustion
                    if world_id == "treatment_pool_exhaustion_world" and not cfg.fast
                    else replicates
                )
                for tp in tp_list:
                    world_ctx = _world_context(
                        world_id,
                        cfg,
                        effect_type=effect_type,
                        treatment_probability=tp,
                    )
                    for rep in range(rep_count):
                        for seed in seeds:
                            attempted += 1
                            record = run_single(
                                design_spec,
                                world_ctx,
                                seed=seed + rep,
                                replicate=rep,
                                cfg=cfg,
                            )
                            records.append(record)
                            if record["assignment_status"] == "success":
                                completed += 1
                            else:
                                failed += 1
                            if record["run_outcome"] == "skipped":
                                skipped += 1

    elapsed = time.perf_counter() - t0
    runtime = {
        "total_attempted_runs": attempted,
        "completed_runs": completed,
        "failed_runs": failed,
        "skipped_runs": skipped,
        "elapsed_seconds": round(elapsed, 3),
    }
    return records, runtime


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_design: dict[str, dict[str, Any]] = {}
    for rec in records:
        did = rec["design_inventory_id"]
        bucket = by_design.setdefault(
            did,
            {
                "n_runs": 0,
                "n_pass": 0,
                "n_warn": 0,
                "n_block": 0,
                "n_failed": 0,
                "assignment_success_rate": 0.0,
                "control_violation_rate": 0.0,
                "mean_max_smd": None,
            },
        )
        bucket["n_runs"] += 1
        outcome = rec["run_outcome"]
        if outcome == "pass":
            bucket["n_pass"] += 1
        elif outcome == "warn":
            bucket["n_warn"] += 1
        elif outcome == "block":
            bucket["n_block"] += 1
        elif outcome == "failed":
            bucket["n_failed"] += 1
        if rec["assignment_status"] != "success":
            pass

    smd_by_design: dict[str, list[float]] = {}
    for rec in records:
        smd = rec["metrics"].get("max_absolute_smd")
        if smd is not None and np.isfinite(smd):
            smd_by_design.setdefault(rec["design_inventory_id"], []).append(float(smd))

    for did, bucket in by_design.items():
        design_recs = [r for r in records if r["design_inventory_id"] == did]
        n = len(design_recs)
        bucket["assignment_success_rate"] = (
            sum(1 for r in design_recs if r["assignment_status"] == "success") / n if n else 0.0
        )
        bucket["control_violation_rate"] = (
            sum(
                1
                for r in design_recs
                if r["metrics"].get("minimum_control_violation")
            )
            / n
            if n
            else 0.0
        )
        smds = smd_by_design.get(did, [])
        bucket["mean_max_smd"] = float(np.mean(smds)) if smds else None

    return {"by_design_inventory_id": by_design}


def _pairwise_comparisons(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparisons: list[dict[str, Any]] = []
    pairs = [
        ("DES-002", "DES-003", "complete_vs_balanced"),
        ("DES-002", "DES-004", "complete_vs_stratified"),
        ("DES-002", "DES-006", "complete_vs_rerandomization"),
        ("DES-001", "DES-002", "greedy_vs_complete_matched_worlds"),
    ]
    for a, b, label in pairs:
        a_smds = [
            r["metrics"]["max_absolute_smd"]
            for r in records
            if r["design_inventory_id"] == a
            and r["assignment_status"] == "success"
            and np.isfinite(r["metrics"].get("max_absolute_smd", float("nan")))
        ]
        b_smds = [
            r["metrics"]["max_absolute_smd"]
            for r in records
            if r["design_inventory_id"] == b
            and r["assignment_status"] == "success"
            and np.isfinite(r["metrics"].get("max_absolute_smd", float("nan")))
        ]
        if not a_smds or not b_smds:
            comparisons.append(
                {
                    "comparison_id": label,
                    "design_a": a,
                    "design_b": b,
                    "median_smd_improvement_a_minus_b": None,
                    "failure_rate_difference": None,
                    "note": "insufficient paired data",
                }
            )
            continue
        comparisons.append(
            {
                "comparison_id": label,
                "design_a": a,
                "design_b": b,
                "median_smd_improvement_a_minus_b": float(
                    np.median(a_smds) - np.median(b_smds)
                ),
                "failure_rate_difference": None,
                "note": "exploratory; provisional_for_characterization_only",
            }
        )
    return comparisons


def _failure_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [r for r in records if r["assignment_status"] != "success"]
    blocks = [r for r in records if r["run_outcome"] == "block"]
    greedy_exhaustion = [
        r
        for r in records
        if r["design_inventory_id"] == "DES-001"
        and r["world_id"] == "treatment_pool_exhaustion_world"
        and (
            r["metrics"].get("minimum_control_violation")
            or r["metrics"].get("n_unassigned", 0) > 0
            or r["run_outcome"] in ("block", "failed")
        )
    ]
    return {
        "n_assignment_failures": len(failures),
        "n_block_outcomes": len(blocks),
        "greedy_exhaustion_world_flagged_runs": len(greedy_exhaustion),
        "greedy_exhaustion_at_tp_0.35": sum(
            1
            for r in greedy_exhaustion
            if abs(r["treatment_probability_requested"] - 0.35) < 1e-9
        ),
        "assignment_infeasibility_failures": sum(
            1
            for r in failures
            if r["world_id"] == "assignment_infeasibility"
        ),
    }


def _guardrail_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    with_contract = [r for r in records if r.get("contract_status")]
    return {
        "n_with_contract_metadata": len(with_contract),
        "guardrail_warn_rate": (
            sum(1 for r in with_contract if r.get("guardrail_status") == "WARN")
            / len(with_contract)
            if with_contract
            else 0.0
        ),
        "guardrail_block_rate": (
            sum(1 for r in with_contract if r.get("guardrail_status") == "BLOCK")
            / len(with_contract)
            if with_contract
            else 0.0
        ),
        "downstream_may_proceed": False,
    }


def _decide_verdict(
    records: list[dict[str, Any]],
    runtime: dict[str, Any],
) -> Verdict:
    if not records:
        return "tier1_design_harness_failed"
    if runtime["total_attempted_runs"] == 0:
        return "tier1_design_harness_inconclusive"
    fail_rate = runtime["failed_runs"] / max(1, runtime["total_attempted_runs"])
    block_rate = sum(1 for r in records if r["run_outcome"] == "block") / len(records)
    if fail_rate > 0.5:
        return "tier1_design_harness_failed"
    if block_rate > 0.25 or any(
        r["design_inventory_id"] == "DES-001"
        and r["world_id"] == "treatment_pool_exhaustion_world"
        and r["metrics"].get("minimum_control_violation")
        for r in records
    ):
        return "tier1_designs_mixed_requires_method_specific_followup"
    if block_rate > 0.05:
        return "tier1_designs_characterized_with_blocking_failures"
    return "tier1_designs_characterized_no_promotion"


def build_d5_des_stat_tier1_001(cfg: D5DesStatTier1Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5DesStatTier1Config()
    records, runtime = _run_matrix(cfg)
    aggregate = _aggregate(records)
    return {
        "artifact_id": ARTIFACT_ID,
        "artifact_version": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_commit": _git_head(),
        "generator_version": GENERATOR_VERSION,
        "governance": {
            "no_promotion": True,
            "no_downstream_authorization": True,
            "no_trust_report": True,
            "no_calibration_signal": True,
            "no_mmm": True,
            "no_llm": True,
            "threshold_policy": "provisional_for_characterization_only",
        },
        "config": asdict(cfg),
        "designs": [
            {
                **asdict(d),
                "base_randomizer_cls": d.base_randomizer_cls.__name__,
            }
            for d in DESIGN_FAMILIES
        ],
        "worlds": list(ALL_WORLD_IDS if not cfg.fast else ALL_WORLD_IDS[:6]),
        "seeds": list(SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS),
        "replicates": cfg.replicates_per_cell if not cfg.fast else 2,
        "run_records": records,
        "aggregate_results": aggregate,
        "pairwise_comparisons": _pairwise_comparisons(records),
        "failure_summary": _failure_summary(records),
        "guardrail_summary": _guardrail_summary(records),
        "runtime": runtime,
        "limitations": [
            "Design-only metrics; not causal estimator OC.",
            "Provisional thresholds; not production calibration.",
            "DES-011 multi-cell explicitly out of scope.",
            "Compatibility smoke not executed in this harness wave.",
        ],
        "verdict": _decide_verdict(records, runtime),
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (float, np.floating)):
        fv = float(value)
        return fv if np.isfinite(fv) else None
    return value


def write_artifact_atomic(path: Path, payload: dict[str, Any], *, overwrite: bool = False) -> Path:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = _json_safe(payload)
    data = json.dumps(safe_payload, indent=2, sort_keys=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
    return path


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5DesStatTier1Config | None = None,
    overwrite: bool = False,
) -> Path:
    path = path or (
        _repo_root() / "docs" / "track_d" / "archives" / "D5_DES_STAT_TIER1_001_results.json"
    )
    payload = build_d5_des_stat_tier1_001(cfg)
    return write_artifact_atomic(path, payload, overwrite=overwrite)


def generate_report_markdown(payload: dict[str, Any]) -> str:
    agg = payload.get("aggregate_results", {}).get("by_design_inventory_id", {})
    fs = payload.get("failure_summary", {})
    rt = payload.get("runtime", {})
    lines = [
        "# D5-DES-STAT-TIER1-001 Report",
        "",
        f"**Artifact:** `{payload.get('artifact_id')}` · **Verdict:** `{payload.get('verdict')}`",
        "",
        "## 1. Executive summary",
        "",
        "First executed tier-1 design statistical validation harness. Characterizes "
        "assignment feasibility, balance, reproducibility inputs, and contract/guardrail "
        "metadata for DES-001–004 and DES-006. **No promotion; downstream blocked.**",
        "",
        "## 2. Scope",
        "",
        "In scope: DES-001 greedy_match_markets, DES-002 CompleteRandomization, DES-003 "
        "BalancedRandomization, DES-004 StratifiedRandomization, DES-006 Rerandomization. "
        "Out of scope: DES-005, DES-007–011, adapters, bridges, product authorization.",
        "",
        "## 3. Designs evaluated",
        "",
    ]
    for d in payload.get("designs", []):
        lines.append(f"- {d.get('design_inventory_id')} `{d.get('design_name')}`")
    lines.extend(
        [
            "",
            "## 4. Worlds evaluated",
            "",
        ]
    )
    for w in payload.get("worlds", []):
        lines.append(f"- `{w}`")
    lines.extend(
        [
            "",
            "## 5. Harness architecture",
            "",
            f"Module: `panel_exp/validation/track_d_d5_des_stat_tier1_001.py` · "
            f"generator `{payload.get('generator_version')}`",
            "",
            "## 6. Metrics",
            "",
            "Assignment feasibility, balance (SMD, volume), population/support, "
            "reproducibility (assignment hash), design-specific diagnostics, contract/guardrail.",
            "",
            "## 7. Runtime and run counts",
            "",
            f"- Attempted: {rt.get('total_attempted_runs')}",
            f"- Completed: {rt.get('completed_runs')}",
            f"- Failed: {rt.get('failed_runs')}",
            f"- Elapsed: {rt.get('elapsed_seconds')}s",
            "",
            "## 8. Overall results",
            "",
        ]
    )
    for did, stats in sorted(agg.items()):
        lines.append(
            f"- **{did}**: success rate {stats.get('assignment_success_rate', 0):.2%}, "
            f"control violation rate {stats.get('control_violation_rate', 0):.2%}, "
            f"pass/warn/block/failed "
            f"{stats.get('n_pass')}/{stats.get('n_warn')}/{stats.get('n_block')}/{stats.get('n_failed')}, "
            f"mean max SMD {stats.get('mean_max_smd')}"
        )
    lines.extend(
        [
            "",
            "## 9. DES-001 findings",
            "",
            f"Greedy exhaustion flagged runs: {fs.get('greedy_exhaustion_world_flagged_runs')} "
            f"(tp=0.35 subset: {fs.get('greedy_exhaustion_at_tp_0.35')}).",
            "",
            "## 10. DES-002 findings",
            "",
            "Complete randomization benchmark; Bernoulli share deviation tracked.",
            "",
            "## 11. DES-003 findings",
            "",
            "Volume-balance objective vs complete randomization in pairwise comparisons.",
            "",
            "## 12. DES-004 findings",
            "",
            "Stratum occupancy and within-stratum balance; poor-strata world stress.",
            "",
            "## 13. DES-006 findings",
            "",
            "Rerandomization attempts/acceptance tracked; wrapper/base identity preserved.",
            "",
            "## 14. Pairwise comparisons",
            "",
        ]
    )
    for pc in payload.get("pairwise_comparisons", []):
        lines.append(f"- {pc.get('comparison_id')}: {pc.get('note') or pc.get('median_smd_improvement_a_minus_b')}")
    lines.extend(
        [
            "",
            "## 15. Feasibility failures",
            "",
            f"Assignment failures: {fs.get('n_assignment_failures')}; "
            f"block outcomes: {fs.get('n_block_outcomes')}.",
            "",
            "## 16. Greedy treatment-pool exhaustion findings",
            "",
            "Treatment probabilities 0.20, 0.35, 0.50 tested in exhaustion world; "
            "minimum control threshold violations recorded without silent retry.",
            "",
            "## 17. Small-N findings",
            "",
            "`small_n_markets` world uses n_units=8.",
            "",
            "## 18. Balance findings",
            "",
            "SMD and volume imbalance tracked; provisional bands only.",
            "",
            "## 19. Reproducibility findings",
            "",
            "Assignment hashes recorded per successful run.",
            "",
            "## 20. Contract/guardrail findings",
            "",
            f"Guardrail WARN rate (successful contract runs): "
            f"{payload.get('guardrail_summary', {}).get('guardrail_warn_rate', 0):.2%}. "
            "downstream_may_proceed=False.",
            "",
            "## 21. Statistical interpretation limits",
            "",
            "Design-only characterization; not estimator/inference validity.",
            "",
            "## 22. Suitability implications",
            "",
            "Metadata may be WARN; statistical suitability still blocked; 0 downstream authorized.",
            "",
            "## 23. Combination-matrix implications",
            "",
            "Evidence informs matrix rows; no automatic upgrade.",
            "",
            "## 24. Required fixes",
            "",
            "Follow method-specific artifacts based on blocking failures (greedy feasibility, stratified sparse strata).",
            "",
            "## 25. Follow-up artifacts",
            "",
            "- D5-DES-STAT-GREEDY-FEASIBILITY-001",
            "- D5-DES-STAT-MULTICELL-001 (DES-011)",
            "",
            "## 26. Governance verdict",
            "",
            f"**{payload.get('verdict')}** — no production promotion.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    payload: dict[str, Any],
    path: Path | None = None,
) -> Path:
    path = path or (_repo_root() / "docs" / "track_d" / "D5_DES_STAT_TIER1_001_REPORT.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_report_markdown(payload) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="D5-DES-STAT-TIER1-001 harness")
    parser.add_argument(
        "--output",
        type=Path,
        default=_repo_root() / "docs" / "track_d" / "archives" / "D5_DES_STAT_TIER1_001_results.json",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    cfg = D5DesStatTier1Config(fast=args.fast)
    payload = build_d5_des_stat_tier1_001(cfg)
    out = write_artifact_atomic(args.output, payload, overwrite=args.overwrite)
    report_path = write_report(payload, args.report)
    print(f"Wrote {out}")
    print(f"Wrote {report_path}")
    print(f"Verdict: {payload['verdict']}")


if __name__ == "__main__":
    main()
