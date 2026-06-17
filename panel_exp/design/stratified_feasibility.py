"""Feasibility contract and stratum construction for StratifiedRandomization (DES-004)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import floor
from typing import Any, Literal

import numpy as np
import pandas as pd

StratificationPolicy = Literal[
    "legacy",
    "preflight_fail",
    "adaptive_strata",
    "sparse_merge",
    "complete_randomization_fallback",
]

DEFAULT_MIN_UNITS_PER_STRATUM = 2


@dataclass(frozen=True)
class StratifiedFeasibilityContract:
    n_eligible: int
    requested_n_strata: int
    realized_n_strata: int
    max_feasible_n_strata: int
    min_units_per_stratum: int
    requested_treatment_probability: float
    feasible: bool
    feasibility_reason: str | None
    policy: StratificationPolicy

    def to_metadata(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StrataBuildResult:
    unit_to_stratum: dict[str, int]
    stratum_ids: list[str]
    stratum_sizes: dict[str, int]
    realized_n_strata: int
    sparse_strata: list[str]
    singleton_strata: list[str]
    empty_strata: list[str]
    merged_strata: list[tuple[str, str]]
    duplicate_boundary_collapses: int


def compute_stratified_feasibility(
    *,
    n_eligible: int,
    requested_n_strata: int,
    min_units_per_stratum: int = DEFAULT_MIN_UNITS_PER_STRATUM,
    treatment_probability: float = 0.5,
    policy: StratificationPolicy = "adaptive_strata",
) -> StratifiedFeasibilityContract:
    min_per = max(2, int(min_units_per_stratum))
    max_feasible = max(1, n_eligible // min_per) if n_eligible > 0 else 0
    realized = min(max(1, requested_n_strata), max_feasible) if max_feasible else 0

    feasible = True
    reason: str | None = None
    if n_eligible < 2:
        feasible = False
        reason = "insufficient_eligible_units"
    elif requested_n_strata > max_feasible and policy == "preflight_fail":
        feasible = False
        reason = "requested_strata_exceeds_max_feasible"
    elif requested_n_strata > max_feasible and policy in (
        "adaptive_strata",
        "sparse_merge",
        "complete_randomization_fallback",
    ):
        reason = "requested_strata_reduced"

    return StratifiedFeasibilityContract(
        n_eligible=n_eligible,
        requested_n_strata=requested_n_strata,
        realized_n_strata=realized if feasible or policy != "preflight_fail" else 0,
        max_feasible_n_strata=max_feasible,
        min_units_per_stratum=min_per,
        requested_treatment_probability=treatment_probability,
        feasible=feasible,
        feasibility_reason=reason,
        policy=policy,
    )


def _merge_small_strata(
    unit_to_stratum: dict[str, int],
    covariate: pd.Series,
    *,
    min_size: int,
) -> tuple[dict[str, int], list[tuple[str, str]]]:
    merged: list[tuple[str, str]] = []
    changed = True
    mapping = dict(unit_to_stratum)
    while changed:
        changed = False
        sizes: dict[int, list[str]] = {}
        for u, s in mapping.items():
            sizes.setdefault(s, []).append(u)
        small = [s for s, units in sizes.items() if len(units) < min_size]
        if not small:
            break
        sid = min(small, key=lambda s: (len(sizes[s]), float(covariate.loc[sizes[s]].median())))
        units = sizes[sid]
        med = float(covariate.loc[units].median())
        others = [s for s in sizes if s != sid]
        if not others:
            break
        neighbor = min(others, key=lambda s: abs(float(covariate.loc[sizes[s]].median()) - med))
        merged.append((str(sid), str(neighbor)))
        for u in units:
            mapping[u] = neighbor
        changed = True
    return mapping, merged


def build_strata(
    covariate: pd.Series,
    *,
    requested_n_strata: int,
    min_units_per_stratum: int,
    policy: StratificationPolicy,
) -> StrataBuildResult:
    n = len(covariate)
    contract = compute_stratified_feasibility(
        n_eligible=n,
        requested_n_strata=requested_n_strata,
        min_units_per_stratum=min_units_per_stratum,
        policy=policy,
    )
    if n == 0:
        return StrataBuildResult({}, [], {}, 0, [], [], [], [], 0)

    target_strata = (
        requested_n_strata
        if policy == "legacy"
        else contract.realized_n_strata
    )
    target_strata = max(1, min(target_strata, n))

    try:
        labels = pd.qcut(
            covariate.rank(method="first"),
            q=target_strata,
            labels=False,
            duplicates="drop",
        )
        realized = int(labels.nunique())
    except ValueError:
        labels = pd.Series(0, index=covariate.index)
        realized = 1

    unit_to_stratum = {str(u): int(labels.loc[u]) for u in covariate.index}
    merged_pairs: list[tuple[str, str]] = []
    if policy == "sparse_merge":
        unit_to_stratum, merged_pairs = _merge_small_strata(
            unit_to_stratum,
            covariate,
            min_size=min_units_per_stratum,
        )
        realized = len(set(unit_to_stratum.values()))

    sizes: dict[str, int] = {}
    for s in unit_to_stratum.values():
        key = str(s)
        sizes[key] = sizes.get(key, 0) + 1

    sparse = [k for k, v in sizes.items() if v < min_units_per_stratum]
    singleton = [k for k, v in sizes.items() if v == 1]
    stratum_ids = sorted(sizes.keys(), key=lambda x: int(x) if x.isdigit() else x)

    return StrataBuildResult(
        unit_to_stratum=unit_to_stratum,
        stratum_ids=stratum_ids,
        stratum_sizes=sizes,
        realized_n_strata=realized,
        sparse_strata=sparse,
        singleton_strata=singleton,
        empty_strata=[],
        merged_strata=merged_pairs,
        duplicate_boundary_collapses=max(0, target_strata - realized),
    )


def assign_within_stratum(
    units: list[str],
    *,
    treatment_probability: float,
    rng: np.random.Generator,
    method: Literal["legacy_volume", "bernoulli"] = "bernoulli",
    wide: pd.DataFrame | None = None,
    total_volume: float | None = None,
    group_shares: dict[str, float] | None = None,
    target_shares: dict[str, float] | None = None,
    n_test_grps: int = 1,
) -> tuple[list[str], list[str]]:
    """Return (control_units, treated_units) for one stratum."""
    if not units:
        return [], []
    shuffled = list(units)
    rng.shuffle(shuffled)
    n = len(shuffled)

    if method == "legacy_volume" and wide is not None and group_shares and target_shares:
        control: list[str] = []
        treated: list[str] = []
        tv = total_volume or float(wide.sum().sum())
        shares = dict(group_shares)
        for unit in shuffled:
            unit_share = float(wide.loc[unit].sum()) / tv if tv > 0 else 0.0
            share_gaps = {g: target_shares[g] - shares[g] for g in target_shares}
            best_group = max(share_gaps, key=share_gaps.get)
            if best_group == "control":
                control.append(unit)
            else:
                treated.append(unit)
            shares[best_group] += unit_share
        if group_shares is not None:
            group_shares.clear()
            group_shares.update(shares)
        return control, treated

    if n == 1:
        if rng.random() < treatment_probability:
            return [], shuffled
        return shuffled, []

    n_treated = max(1, min(n - 1, floor(n * treatment_probability + 0.5)))
    if n_treated == 0:
        n_treated = 1
    if n_treated >= n:
        n_treated = n - 1
    treated = shuffled[:n_treated]
    control = shuffled[n_treated:]
    return control, treated


def build_stratification_metadata(
    contract: StratifiedFeasibilityContract,
    strata: StrataBuildResult,
    *,
    realized_treatment_probability: float | None,
    fallback_used: bool,
    fallback_reason: str | None,
    stratification_variable: str = "pre_period_mean",
) -> dict[str, Any]:
    return {
        **contract.to_metadata(),
        "stratum_sizes": strata.stratum_sizes,
        "unit_to_stratum_map": strata.unit_to_stratum,
        "stratum_ids": strata.stratum_ids,
        "sparse_strata": strata.sparse_strata,
        "singleton_strata": strata.singleton_strata,
        "empty_strata": strata.empty_strata,
        "merged_strata": [{"from": a, "to": b} for a, b in strata.merged_strata],
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "stratification_variable": stratification_variable,
        "realized_treatment_probability": realized_treatment_probability,
        "duplicate_boundary_collapses": strata.duplicate_boundary_collapses,
    }
