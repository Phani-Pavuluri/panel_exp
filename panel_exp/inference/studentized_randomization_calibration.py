"""STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001 — empirical null calibration harness.

Simulation-based diagnostics for studentized placebo-rank mechanics under known null
DGPs and governed assignment families. Empirical tail fractions are not production
p-values and no causal confidence intervals are authorized.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

import numpy as np

from panel_exp.design.assignment_generators import (
    AssignmentDesignSpec,
    AssignmentFamily,
    AssignmentUnit,
    ValidityStatus,
    generate_pseudo_assignments,
)
from panel_exp.inference.studentized_placebo_rank import (
    StudentizedEffectDirection,
    compute_studentized_placebo_rank,
)

CALIBRATION_WARNING = (
    "Empirical null-calibration diagnostic only — tail fractions are not production "
    "p-values and no causal confidence interval is authorized."
)


class NullDGPKind(str, Enum):
    IID_NORMAL = "iid_normal"
    UNIT_FIXED_EFFECT = "unit_fixed_effect"
    UNIT_AND_TIME_FIXED_EFFECT = "unit_and_time_fixed_effect"
    HETEROSKEDASTIC = "heteroskedastic"
    AUTOCORRELATED = "autocorrelated"


class CalibrationAssignmentFamily(str, Enum):
    COMPLETE_RANDOMIZED_SET = "complete_randomized_set"
    MATCHED_PAIR_RANDOMIZED = "matched_pair_randomized"
    MATCHED_BLOCK_RANDOMIZED = "matched_block_randomized"
    STRATIFIED_RANDOMIZED = "stratified_randomized"
    RERANDOMIZED_DESIGN_CANDIDATE = "rerandomized_design_candidate"


class CalibrationStatisticMode(str, Enum):
    STUDENTIZED = "studentized"
    UNSTUDENTIZED = "unstudentized"


class CalibrationVerdict(str, Enum):
    CALIBRATED_UNDER_TESTED_NULLS = "calibrated_under_tested_nulls"
    BORDERLINE_REQUIRES_MORE_SIMULATION = "borderline_requires_more_simulation"
    NOT_CALIBRATED_DIAGNOSTIC_ONLY = "not_calibrated_diagnostic_only"
    INVALID_CALIBRATION_SPEC = "invalid_calibration_spec"


_FAMILY_MAP: dict[CalibrationAssignmentFamily, AssignmentFamily] = {
    CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET: (
        AssignmentFamily.COMPLETE_RANDOMIZED_SET
    ),
    CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED: (
        AssignmentFamily.MATCHED_PAIR_RANDOMIZED
    ),
    CalibrationAssignmentFamily.MATCHED_BLOCK_RANDOMIZED: (
        AssignmentFamily.MATCHED_BLOCK_RANDOMIZED
    ),
    CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED: (
        AssignmentFamily.STRATIFIED_RANDOMIZED
    ),
    CalibrationAssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE: (
        AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE
    ),
}


@dataclass(frozen=True)
class StudentizedNullSimulationSpec:
    dgp_kind: NullDGPKind
    assignment_family: CalibrationAssignmentFamily
    statistic_mode: CalibrationStatisticMode
    num_units: int
    num_treated: int
    num_pre_periods: int
    num_post_periods: int
    num_replications: int
    num_pseudo_assignments: int
    alpha_levels: tuple[float, ...] = (0.10, 0.05)
    seed: int = 123
    effect_direction: str = "two_sided"
    min_replications: int = 100
    min_pseudo_assignments: int = 20


@dataclass(frozen=True)
class NullSimulationReplicationResult:
    replication_id: int
    observed_statistic: float
    empirical_tail_fraction: float
    placebo_rank: int
    num_placebo_sets: int
    rejected_by_alpha: Mapping[str, bool]


@dataclass(frozen=True)
class StudentizedNullCalibrationResult:
    spec: StudentizedNullSimulationSpec
    replication_results: tuple[NullSimulationReplicationResult, ...]
    empirical_type_i_by_alpha: Mapping[str, float]
    expected_type_i_by_alpha: Mapping[str, float]
    type_i_excess_by_alpha: Mapping[str, float]
    tail_fraction_quantiles: Mapping[str, float]
    verdict: CalibrationVerdict
    warnings: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    governance_flags: Mapping[str, bool]


def _governance_flags() -> dict[str, bool]:
    return {
        "production_p_value_authorized": False,
        "causal_confidence_interval_authorized": False,
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
    }


def _direction(effect_direction: str) -> StudentizedEffectDirection:
    mapping = {
        "greater": StudentizedEffectDirection.GREATER,
        "less": StudentizedEffectDirection.LESS,
        "two_sided": StudentizedEffectDirection.TWO_SIDED,
    }
    return mapping.get(effect_direction, StudentizedEffectDirection.TWO_SIDED)


def validate_studentized_null_simulation_spec(
    spec: StudentizedNullSimulationSpec,
) -> tuple[bool, tuple[str, ...]]:
    """Validate null-calibration simulation specification."""
    reasons: list[str] = []
    if spec.num_units < 4:
        reasons.append("num_units must be >= 4")
    if spec.num_treated < 1:
        reasons.append("num_treated must be >= 1")
    if spec.num_treated >= spec.num_units:
        reasons.append("num_treated must be < num_units")
    if spec.assignment_family == CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        if spec.num_units % 2 != 0:
            reasons.append("matched_pair requires even num_units")
        if spec.num_treated != spec.num_units // 2:
            reasons.append(
                "matched_pair requires num_treated == num_units // 2 (one treated per pair)"
            )
    if spec.num_pre_periods < 2:
        reasons.append("num_pre_periods must be >= 2")
    if spec.num_post_periods < 1:
        reasons.append("num_post_periods must be >= 1")
    if spec.num_replications < spec.min_replications:
        reasons.append(
            f"num_replications {spec.num_replications} < min_replications "
            f"{spec.min_replications}"
        )
    if spec.num_pseudo_assignments < spec.min_pseudo_assignments:
        reasons.append(
            f"num_pseudo_assignments {spec.num_pseudo_assignments} < "
            f"min_pseudo_assignments {spec.min_pseudo_assignments}"
        )
    for alpha in spec.alpha_levels:
        if not (0.0 < alpha < 1.0):
            reasons.append(f"alpha {alpha} must be in (0, 1)")
    return (len(reasons) == 0, tuple(reasons))


def _build_units(spec: StudentizedNullSimulationSpec) -> list[AssignmentUnit]:
    units: list[AssignmentUnit] = []
    n = spec.num_units
    family = spec.assignment_family
    if family == CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        for i in range(n):
            units.append(AssignmentUnit(unit_id=f"u{i:02d}", pair_id=f"p{i // 2}"))
    elif family in {
        CalibrationAssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
        CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
    }:
        n_strata = max(2, min(4, n // 3))
        per = n // n_strata
        key = (
            "block_id"
            if family == CalibrationAssignmentFamily.MATCHED_BLOCK_RANDOMIZED
            else "stratum_id"
        )
        for i in range(n):
            group = f"g{i // per}"
            if key == "block_id":
                units.append(AssignmentUnit(unit_id=f"u{i:02d}", block_id=group))
            else:
                units.append(AssignmentUnit(unit_id=f"u{i:02d}", stratum_id=group))
    else:
        for i in range(n):
            units.append(AssignmentUnit(unit_id=f"u{i:02d}"))
    return units


def _group_units(
    units: list[AssignmentUnit],
    key: str,
) -> dict[str, list[AssignmentUnit]]:
    groups: dict[str, list[AssignmentUnit]] = {}
    for unit in units:
        group_key = getattr(unit, key)
        if group_key is not None:
            groups.setdefault(str(group_key), []).append(unit)
    return groups


def _select_observed_treated(
    spec: StudentizedNullSimulationSpec,
    units: list[AssignmentUnit],
    rng: np.random.Generator,
) -> tuple[str, ...]:
    k = spec.num_treated
    family = spec.assignment_family
    if family == CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        pairs = _group_units(units, "pair_id")
        treated: list[str] = []
        for members in pairs.values():
            member_ids = [m.unit_id for m in members]
            treated.append(str(rng.choice(member_ids)))
        return tuple(sorted(treated))
    if family in {
        CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
        CalibrationAssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
    }:
        key = (
            "stratum_id"
            if family == CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED
            else "block_id"
        )
        groups = _group_units(units, key)
        treated_ids: list[str] = []
        per_group = max(1, k // max(1, len(groups)))
        for members in groups.values():
            ids = [m.unit_id for m in members]
            take = min(per_group, len(ids), k - len(treated_ids))
            if take > 0:
                chosen_ids = rng.choice(ids, size=take, replace=False)
                treated_ids.extend(str(x) for x in chosen_ids)
            if len(treated_ids) >= k:
                break
        return tuple(sorted(treated_ids[:k]))
    all_ids = [u.unit_id for u in units]
    chosen = rng.choice(all_ids, size=k, replace=False)
    return tuple(sorted(str(x) for x in chosen))


def _generate_null_outcomes(
    spec: StudentizedNullSimulationSpec,
    rng: np.random.Generator,
) -> np.ndarray:
    n_units = spec.num_units
    n_periods = spec.num_pre_periods + spec.num_post_periods
    dgp = spec.dgp_kind

    unit_effects = rng.normal(0.0, 1.0, size=n_units)
    time_effects = rng.normal(0.0, 0.5, size=n_periods)

    if dgp == NullDGPKind.HETEROSKEDASTIC:
        noise_sd = rng.uniform(0.5, 2.0, size=n_units)
        noise = rng.normal(0.0, 1.0, size=(n_units, n_periods)) * noise_sd[:, None]
    elif dgp == NullDGPKind.AUTOCORRELATED:
        noise = np.zeros((n_units, n_periods))
        for g in range(n_units):
            eps = rng.normal(0.0, 1.0)
            for t in range(n_periods):
                eps = 0.6 * eps + rng.normal(0.0, 0.8)
                noise[g, t] = eps
    else:
        noise = rng.normal(0.0, 1.0, size=(n_units, n_periods))

    y = np.zeros((n_units, n_periods))
    for g in range(n_units):
        for t in range(n_periods):
            val = noise[g, t]
            if dgp in {
                NullDGPKind.UNIT_FIXED_EFFECT,
                NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT,
                NullDGPKind.HETEROSKEDASTIC,
                NullDGPKind.AUTOCORRELATED,
            }:
                val += unit_effects[g]
            if dgp == NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT:
                val += time_effects[t]
            y[g, t] = val
    return y


def _unit_index_map(units: list[AssignmentUnit]) -> dict[str, int]:
    return {u.unit_id: i for i, u in enumerate(units)}


def _mean_post(
    outcomes: np.ndarray,
    unit_indices: list[int],
    pre_periods: int,
) -> float:
    if not unit_indices:
        return float("nan")
    post = outcomes[unit_indices, pre_periods:]
    return float(np.mean(post))


def _compute_effect(
    outcomes: np.ndarray,
    unit_index: dict[str, int],
    treated_ids: tuple[str, ...],
    control_ids: tuple[str, ...],
    pre_periods: int,
) -> float:
    t_idx = [unit_index[uid] for uid in treated_ids]
    c_idx = [unit_index[uid] for uid in control_ids]
    return _mean_post(outcomes, t_idx, pre_periods) - _mean_post(
        outcomes, c_idx, pre_periods
    )


def _compute_scale(outcomes: np.ndarray, pre_periods: int) -> float:
    pre = outcomes[:, :pre_periods]
    demeaned = pre - pre.mean(axis=1, keepdims=True)
    scale = float(np.std(demeaned, ddof=1))
    if not math.isfinite(scale) or scale <= 0:
        unit_means = pre.mean(axis=1)
        scale = float(np.std(unit_means, ddof=1))
    if not math.isfinite(scale) or scale <= 0:
        scale = 1.0
    return scale


def _to_statistic(effect: float, scale: float, mode: CalibrationStatisticMode) -> float:
    if mode == CalibrationStatisticMode.UNSTUDENTIZED:
        return effect
    if scale <= 0 or not math.isfinite(scale):
        return float("nan")
    return effect / scale


def _run_one_replication(
    spec: StudentizedNullSimulationSpec,
    replication_id: int,
) -> tuple[NullSimulationReplicationResult | None, str | None]:
    rep_seed = spec.seed + replication_id * 9973
    rng = np.random.default_rng(rep_seed)
    units = _build_units(spec)
    unit_index = _unit_index_map(units)
    outcomes = _generate_null_outcomes(spec, rng)
    observed_treated = _select_observed_treated(spec, units, rng)
    all_ids = {u.unit_id for u in units}
    observed_control = tuple(sorted(all_ids - set(observed_treated)))

    family = _FAMILY_MAP[spec.assignment_family]
    assign_spec = AssignmentDesignSpec(
        family=family,
        units=units,
        observed_treated_unit_ids=observed_treated,
        seed=rep_seed,
        max_assignments=max(spec.num_pseudo_assignments, spec.min_pseudo_assignments),
        min_assignments=spec.min_pseudo_assignments,
    )
    pseudo_assignments = generate_pseudo_assignments(assign_spec)
    supported = ValidityStatus.ASSIGNMENT_GENERATION_SUPPORTED.value
    valid = [
        a
        for a in pseudo_assignments
        if a.pseudo_treated_unit_ids and a.validity_status == supported
    ]
    if len(valid) < spec.min_pseudo_assignments:
        valid = [a for a in pseudo_assignments if a.pseudo_treated_unit_ids]
    if len(valid) < spec.min_pseudo_assignments:
        return None, "insufficient_valid_pseudo_assignments"

    valid = valid[: spec.num_pseudo_assignments]
    scale = _compute_scale(outcomes, spec.num_pre_periods)
    observed_effect = _compute_effect(
        outcomes, unit_index, observed_treated, observed_control, spec.num_pre_periods
    )
    observed_stat = _to_statistic(observed_effect, scale, spec.statistic_mode)
    if not math.isfinite(observed_stat):
        return None, "non_finite_observed_statistic"

    pseudo_stats: dict[str, float] = {}
    for assignment in valid:
        effect = _compute_effect(
            outcomes,
            unit_index,
            assignment.pseudo_treated_unit_ids,
            assignment.pseudo_control_unit_ids,
            spec.num_pre_periods,
        )
        stat = _to_statistic(effect, scale, spec.statistic_mode)
        if math.isfinite(stat):
            pseudo_stats[assignment.assignment_id] = stat

    if len(pseudo_stats) < spec.min_pseudo_assignments:
        return None, "insufficient_finite_pseudo_statistics"

    rank, tail = compute_studentized_placebo_rank(
        observed_stat,
        pseudo_stats,
        _direction(spec.effect_direction),
    )
    rejected = {str(alpha): tail <= alpha for alpha in spec.alpha_levels}
    return (
        NullSimulationReplicationResult(
            replication_id=replication_id,
            observed_statistic=observed_stat,
            empirical_tail_fraction=tail,
            placebo_rank=rank,
            num_placebo_sets=len(pseudo_stats),
            rejected_by_alpha=rejected,
        ),
        None,
    )


def _assign_verdict(
    spec: StudentizedNullSimulationSpec,
    empirical_type_i: Mapping[str, float],
) -> CalibrationVerdict:
    if not empirical_type_i:
        return CalibrationVerdict.INVALID_CALIBRATION_SPEC
    calibrated = all(
        empirical_type_i[str(alpha)] <= alpha + 0.03 for alpha in spec.alpha_levels
    )
    borderline = all(
        empirical_type_i[str(alpha)] <= alpha + 0.06 for alpha in spec.alpha_levels
    )
    if calibrated:
        return CalibrationVerdict.CALIBRATED_UNDER_TESTED_NULLS
    if borderline:
        return CalibrationVerdict.BORDERLINE_REQUIRES_MORE_SIMULATION
    return CalibrationVerdict.NOT_CALIBRATED_DIAGNOSTIC_ONLY


def run_studentized_null_calibration(
    spec: StudentizedNullSimulationSpec,
) -> StudentizedNullCalibrationResult:
    """Run empirical null calibration for one simulation specification."""
    valid, reasons = validate_studentized_null_simulation_spec(spec)
    if not valid:
        return StudentizedNullCalibrationResult(
            spec=spec,
            replication_results=(),
            empirical_type_i_by_alpha={},
            expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
            type_i_excess_by_alpha={},
            tail_fraction_quantiles={},
            verdict=CalibrationVerdict.INVALID_CALIBRATION_SPEC,
            warnings=(CALIBRATION_WARNING,),
            blocked_reasons=reasons,
            governance_flags=_governance_flags(),
        )

    warnings: list[str] = [CALIBRATION_WARNING]
    results: list[NullSimulationReplicationResult] = []
    skip_reasons: list[str] = []

    for rep in range(spec.num_replications):
        rep_result, skip = _run_one_replication(spec, rep)
        if rep_result is None:
            if skip:
                skip_reasons.append(skip)
            continue
        results.append(rep_result)

    if len(results) < spec.min_replications:
        return StudentizedNullCalibrationResult(
            spec=spec,
            replication_results=tuple(results),
            empirical_type_i_by_alpha={},
            expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
            type_i_excess_by_alpha={},
            tail_fraction_quantiles={},
            verdict=CalibrationVerdict.INVALID_CALIBRATION_SPEC,
            warnings=tuple(warnings),
            blocked_reasons=tuple(
                list(skip_reasons[:3])
                + [f"completed_replications {len(results)} < min_replications"]
            ),
            governance_flags=_governance_flags(),
        )

    tails = [r.empirical_tail_fraction for r in results]
    empirical_type_i: dict[str, float] = {}
    type_i_excess: dict[str, float] = {}
    for alpha in spec.alpha_levels:
        key = str(alpha)
        rejects = [r.rejected_by_alpha[key] for r in results]
        empirical_type_i[key] = sum(rejects) / len(rejects)
        type_i_excess[key] = empirical_type_i[key] - alpha

    quantiles = {
        "q10": float(np.quantile(tails, 0.10)),
        "q50": float(np.quantile(tails, 0.50)),
        "q90": float(np.quantile(tails, 0.90)),
    }

    return StudentizedNullCalibrationResult(
        spec=spec,
        replication_results=tuple(results),
        empirical_type_i_by_alpha=empirical_type_i,
        expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
        type_i_excess_by_alpha=type_i_excess,
        tail_fraction_quantiles=quantiles,
        verdict=_assign_verdict(spec, empirical_type_i),
        warnings=tuple(warnings),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def summarize_studentized_null_calibration_result(
    result: StudentizedNullCalibrationResult,
) -> dict[str, Any]:
    """Serialize null-calibration result for validation archives."""
    return {
        "dgp_kind": result.spec.dgp_kind.value,
        "assignment_family": result.spec.assignment_family.value,
        "statistic_mode": result.spec.statistic_mode.value,
        "num_replications_requested": result.spec.num_replications,
        "num_replications_completed": len(result.replication_results),
        "empirical_type_i_by_alpha": dict(result.empirical_type_i_by_alpha),
        "expected_type_i_by_alpha": dict(result.expected_type_i_by_alpha),
        "type_i_excess_by_alpha": dict(result.type_i_excess_by_alpha),
        "tail_fraction_quantiles": dict(result.tail_fraction_quantiles),
        "verdict": result.verdict.value,
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


def run_studentized_null_calibration_grid(
    specs: tuple[StudentizedNullSimulationSpec, ...],
) -> tuple[StudentizedNullCalibrationResult, ...]:
    """Run null calibration across a grid of specifications."""
    return tuple(run_studentized_null_calibration(spec) for spec in specs)


def summarize_studentized_null_calibration_grid(
    results: tuple[StudentizedNullCalibrationResult, ...],
) -> dict[str, Any]:
    """Summarize grid calibration results."""
    verdict_counts: dict[str, int] = {}
    dgp_coverage: dict[str, bool] = {}
    family_coverage: dict[str, bool] = {}
    mode_coverage: dict[str, bool] = {}
    max_excess = 0.0

    for result in results:
        verdict_counts[result.verdict.value] = verdict_counts.get(result.verdict.value, 0) + 1
        dgp_coverage[result.spec.dgp_kind.value] = True
        family_coverage[result.spec.assignment_family.value] = True
        mode_coverage[result.spec.statistic_mode.value] = True
        for excess in result.type_i_excess_by_alpha.values():
            max_excess = max(max_excess, excess)

    return {
        "grid_result_count": len(results),
        "verdict_counts": verdict_counts,
        "dgp_coverage": dgp_coverage,
        "assignment_family_coverage": family_coverage,
        "statistic_mode_coverage": mode_coverage,
        "max_empirical_type_i_excess": max_excess if results else None,
        "governance_flags": _governance_flags(),
    }


def _base_spec(
    *,
    dgp: NullDGPKind,
    family: CalibrationAssignmentFamily,
    mode: CalibrationStatisticMode,
    seed: int = 123,
    num_replications: int = 100,
    min_replications: int = 100,
) -> StudentizedNullSimulationSpec:
    num_units = 16 if family != CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED else 12
    num_treated = num_units // 2 if family == CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED else (
        4 if num_units >= 16 else 3
    )
    return StudentizedNullSimulationSpec(
        dgp_kind=dgp,
        assignment_family=family,
        statistic_mode=mode,
        num_units=num_units,
        num_treated=num_treated,
        num_pre_periods=6,
        num_post_periods=3,
        num_replications=num_replications,
        num_pseudo_assignments=30,
        seed=seed,
        min_replications=min_replications,
        min_pseudo_assignments=20,
    )


def build_default_studentized_null_calibration_grid() -> tuple[
    StudentizedNullSimulationSpec, ...
]:
    """Small deterministic grid for validation harness."""
    return (
        _base_spec(
            dgp=NullDGPKind.IID_NORMAL,
            family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=101,
        ),
        _base_spec(
            dgp=NullDGPKind.IID_NORMAL,
            family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=CalibrationStatisticMode.UNSTUDENTIZED,
            seed=102,
        ),
        _base_spec(
            dgp=NullDGPKind.UNIT_FIXED_EFFECT,
            family=CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=103,
        ),
        _base_spec(
            dgp=NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT,
            family=CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=104,
        ),
        _base_spec(
            dgp=NullDGPKind.HETEROSKEDASTIC,
            family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=105,
        ),
        _base_spec(
            dgp=NullDGPKind.UNIT_FIXED_EFFECT,
            family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=106,
        ),
        _base_spec(
            dgp=NullDGPKind.IID_NORMAL,
            family=CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=107,
        ),
        _base_spec(
            dgp=NullDGPKind.IID_NORMAL,
            family=CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
            mode=CalibrationStatisticMode.STUDENTIZED,
            seed=108,
        ),
    )


__all__ = [
    "CALIBRATION_WARNING",
    "CalibrationAssignmentFamily",
    "CalibrationStatisticMode",
    "CalibrationVerdict",
    "NullDGPKind",
    "NullSimulationReplicationResult",
    "StudentizedNullCalibrationResult",
    "StudentizedNullSimulationSpec",
    "build_default_studentized_null_calibration_grid",
    "run_studentized_null_calibration",
    "run_studentized_null_calibration_grid",
    "summarize_studentized_null_calibration_grid",
    "summarize_studentized_null_calibration_result",
    "validate_studentized_null_simulation_spec",
]
