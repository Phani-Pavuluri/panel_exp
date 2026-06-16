"""Feasibility contract and preflight for greedy_match_markets (DES-001)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import floor
from typing import Any, Literal

FeasibilityPolicy = Literal[
    "legacy",
    "preflight_fail",
    "feasibility_cap",
    "control_reservation",
]

DEFAULT_MIN_CONTROL_UNITS = 1


@dataclass(frozen=True)
class GreedyFeasibilityContract:
    n_eligible: int
    requested_treatment_probability: float
    requested_n_treated: int
    min_control_units: int
    min_treated_units: int
    max_feasible_n_treated: int
    max_feasible_n_control: int
    pinned_control: int
    pinned_test: int
    feasible: bool
    feasibility_reason: str | None
    policy: FeasibilityPolicy

    def to_metadata(self) -> dict[str, Any]:
        return asdict(self)


def compute_greedy_feasibility(
    *,
    n_assignable: int,
    treatment_probability: float,
    n_test_grps: int,
    pinned_control: int,
    pinned_test: int,
    min_control_units: int = DEFAULT_MIN_CONTROL_UNITS,
    policy: FeasibilityPolicy = "control_reservation",
) -> GreedyFeasibilityContract:
    """Derive unit-count feasibility bounds for greedy assignment."""
    min_control = max(1, int(min_control_units))
    min_treated = max(int(n_test_grps), 1)
    requested_n_treated = max(floor(treatment_probability * n_assignable), pinned_test)
    max_feasible_n_treated = max(0, n_assignable - min_control)
    max_feasible_n_control = max(0, n_assignable - min_treated)

    feasible = True
    reason: str | None = None

    if n_assignable < min_control + min_treated:
        feasible = False
        reason = "insufficient_assignable_units_for_min_control_and_test"
    elif pinned_test > max_feasible_n_treated:
        feasible = False
        reason = "pinned_test_exceeds_max_feasible_treated"
    elif pinned_control > max_feasible_n_control:
        feasible = False
        reason = "pinned_control_exceeds_max_feasible_control"
    elif requested_n_treated > max_feasible_n_treated:
        if policy == "preflight_fail":
            feasible = False
            reason = "requested_treated_exceeds_max_feasible"
        elif policy in ("feasibility_cap", "control_reservation"):
            reason = "requested_treated_will_be_capped"

    return GreedyFeasibilityContract(
        n_eligible=n_assignable,
        requested_treatment_probability=treatment_probability,
        requested_n_treated=requested_n_treated,
        min_control_units=min_control,
        min_treated_units=min_treated,
        max_feasible_n_treated=max_feasible_n_treated,
        max_feasible_n_control=max_feasible_n_control,
        pinned_control=pinned_control,
        pinned_test=pinned_test,
        feasible=feasible,
        feasibility_reason=reason,
        policy=policy,
    )


def build_feasibility_metadata(
    contract: GreedyFeasibilityContract,
    *,
    realized_n_treated: int,
    realized_n_control: int,
    feasibility_adjusted: bool,
    candidate_pool_exhausted: bool,
    retry_count: int = 0,
) -> dict[str, Any]:
    n_assigned = realized_n_treated + realized_n_control
    realized_tp = (
        float(realized_n_treated) / float(n_assigned) if n_assigned > 0 else None
    )
    return {
        **contract.to_metadata(),
        "realized_n_treated": realized_n_treated,
        "realized_n_control": realized_n_control,
        "realized_treatment_probability": realized_tp,
        "minimum_control_units": contract.min_control_units,
        "max_feasible_n_treated": contract.max_feasible_n_treated,
        "feasibility_adjusted": feasibility_adjusted,
        "feasibility_policy": contract.policy,
        "feasibility_reason": contract.feasibility_reason,
        "candidate_pool_exhausted": candidate_pool_exhausted,
        "retry_count": retry_count,
    }
