"""SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001 — SCM-specific null calibration harness.

Empirical null calibration for SCM-style treated-set placebo rank mechanics under known
null DGPs. Uses a lightweight SCM-style statistic adapter — not production SCM fitting.
Empirical tail fractions are not production p-values.
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
    "SCM-specific empirical null-calibration diagnostic only — SCM-style statistic adapter "
    "is not production SCM fitting; tail fractions are not production p-values."
)


class SCMNullDGPKind(str, Enum):
    IID_NORMAL = "iid_normal"
    UNIT_FIXED_EFFECT = "unit_fixed_effect"
    UNIT_AND_TIME_FIXED_EFFECT = "unit_and_time_fixed_effect"
    HETEROSKEDASTIC = "heteroskedastic"
    DONOR_MATCHED_LATENT_FACTOR = "donor_matched_latent_factor"


class SCMAssignmentFamily(str, Enum):
    COMPLETE_RANDOMIZED_SET = "complete_randomized_set"
    MATCHED_PAIR_RANDOMIZED = "matched_pair_randomized"
    STRATIFIED_RANDOMIZED = "stratified_randomized"


class SCMStatisticMode(str, Enum):
    SCM_STYLE_EFFECT = "scm_style_effect"
    SCM_STYLE_STUDENTIZED_EFFECT = "scm_style_studentized_effect"
    SIMPLE_DIFF_IN_MEANS_BASELINE = "simple_diff_in_means_baseline"


class SCMCalibrationVerdict(str, Enum):
    CALIBRATED_UNDER_TESTED_NULLS = "calibrated_under_tested_nulls"
    BORDERLINE_REQUIRES_MORE_SIMULATION = "borderline_requires_more_simulation"
    NOT_CALIBRATED_DIAGNOSTIC_ONLY = "not_calibrated_diagnostic_only"
    INVALID_CALIBRATION_SPEC = "invalid_calibration_spec"


_FAMILY_MAP: dict[SCMAssignmentFamily, AssignmentFamily] = {
    SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET: AssignmentFamily.COMPLETE_RANDOMIZED_SET,
    SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED: AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
    SCMAssignmentFamily.STRATIFIED_RANDOMIZED: AssignmentFamily.STRATIFIED_RANDOMIZED,
}


@dataclass(frozen=True)
class OutcomePanel:
    """Lightweight outcome panel for null-calibration simulations."""

    outcomes: np.ndarray
    unit_ids: tuple[str, ...]


@dataclass(frozen=True)
class SCMTreatedSetNullSimulationSpec:
    dgp_kind: SCMNullDGPKind
    assignment_family: SCMAssignmentFamily
    statistic_mode: SCMStatisticMode
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
class SCMNullReplicationResult:
    replication_id: int
    observed_statistic: float
    empirical_tail_fraction: float
    placebo_rank: int
    num_placebo_sets: int
    rejected_by_alpha: Mapping[str, bool]
    diagnostic_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SCMTreatedSetNullCalibrationResult:
    spec: SCMTreatedSetNullSimulationSpec
    replication_results: tuple[SCMNullReplicationResult, ...]
    empirical_type_i_by_alpha: Mapping[str, float]
    expected_type_i_by_alpha: Mapping[str, float]
    type_i_excess_by_alpha: Mapping[str, float]
    tail_fraction_quantiles: Mapping[str, float]
    verdict: SCMCalibrationVerdict
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


def _period_indices(period_ids: tuple[str, ...]) -> list[int]:
    return [int(p.replace("p", "")) for p in period_ids]


def validate_scm_treated_set_null_simulation_spec(
    spec: SCMTreatedSetNullSimulationSpec,
) -> tuple[bool, tuple[str, ...]]:
    """Validate SCM treated-set null-calibration simulation specification."""
    reasons: list[str] = []
    if spec.num_units < 4:
        reasons.append("num_units must be >= 4")
    if spec.num_treated < 1:
        reasons.append("num_treated must be >= 1")
    if spec.num_treated >= spec.num_units:
        reasons.append("num_treated must be < num_units")
    if spec.assignment_family == SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
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


def _fit_donor_weights(treated_pre: np.ndarray, donor_pre: np.ndarray) -> np.ndarray:
    """Non-negative donor weights summing to 1 (numpy-only ridge/inverse-distance proxy)."""
    n_donors = donor_pre.shape[0]
    if n_donors == 0:
        return np.array([])
    if n_donors == 1:
        return np.array([1.0])
    try:
        w, _, _, _ = np.linalg.lstsq(donor_pre.T, treated_pre, rcond=1e-8)
        w = np.maximum(w, 0.0)
        if float(w.sum()) > 1e-12:
            return w / w.sum()
    except np.linalg.LinAlgError:
        pass
    distances = np.linalg.norm(donor_pre - treated_pre, axis=1)
    inv = 1.0 / (distances + 1e-6)
    return inv / inv.sum()


def _scm_style_effect(
    panel: OutcomePanel,
    treated_unit_ids: tuple[str, ...],
    pre_indices: list[int],
    post_indices: list[int],
) -> float:
    unit_index = {uid: i for i, uid in enumerate(panel.unit_ids)}
    treated_idx = [unit_index[uid] for uid in treated_unit_ids]
    control_idx = [i for i, uid in enumerate(panel.unit_ids) if uid not in treated_unit_ids]
    if not treated_idx or not control_idx:
        return float("nan")

    treated_pre = panel.outcomes[treated_idx][:, pre_indices].mean(axis=0)
    donor_pre = panel.outcomes[control_idx][:, pre_indices]
    donor_post = panel.outcomes[control_idx][:, post_indices].mean(axis=1)
    weights = _fit_donor_weights(treated_pre, donor_pre)
    synthetic_post = float(np.dot(weights, donor_post))
    treated_post = float(panel.outcomes[treated_idx][:, post_indices].mean())
    return treated_post - synthetic_post


def _diff_in_means_effect(
    panel: OutcomePanel,
    treated_unit_ids: tuple[str, ...],
    pre_indices: list[int],
    post_indices: list[int],
) -> float:
    unit_index = {uid: i for i, uid in enumerate(panel.unit_ids)}
    treated_idx = [unit_index[uid] for uid in treated_unit_ids]
    control_idx = [i for i, uid in enumerate(panel.unit_ids) if uid not in treated_unit_ids]
    if not treated_idx or not control_idx:
        return float("nan")
    treated_post = float(panel.outcomes[treated_idx][:, post_indices].mean())
    control_post = float(panel.outcomes[control_idx][:, post_indices].mean())
    return treated_post - control_post


def _pre_period_scale(panel: OutcomePanel, pre_indices: list[int]) -> float:
    pre = panel.outcomes[:, pre_indices]
    demeaned = pre - pre.mean(axis=1, keepdims=True)
    scale = float(np.std(demeaned, ddof=1))
    if not math.isfinite(scale) or scale <= 0:
        scale = float(np.std(pre.mean(axis=1), ddof=1))
    if not math.isfinite(scale) or scale <= 0:
        scale = 1.0
    return scale


def compute_scm_style_treated_set_statistic(
    outcome_panel: object,
    treated_unit_ids: tuple[str, ...],
    pre_period_ids: tuple[str, ...],
    post_period_ids: tuple[str, ...],
    statistic_mode: SCMStatisticMode,
) -> float:
    """Compute SCM-style treated-set statistic for null calibration."""
    if not isinstance(outcome_panel, OutcomePanel):
        raise TypeError("outcome_panel must be OutcomePanel")
    pre_idx = _period_indices(pre_period_ids)
    post_idx = _period_indices(post_period_ids)

    if statistic_mode == SCMStatisticMode.SIMPLE_DIFF_IN_MEANS_BASELINE:
        return _diff_in_means_effect(outcome_panel, treated_unit_ids, pre_idx, post_idx)

    effect = _scm_style_effect(outcome_panel, treated_unit_ids, pre_idx, post_idx)
    if statistic_mode == SCMStatisticMode.SCM_STYLE_EFFECT:
        return effect
    scale = _pre_period_scale(outcome_panel, pre_idx)
    if scale <= 0 or not math.isfinite(scale):
        return float("nan")
    return effect / scale


def _build_units(spec: SCMTreatedSetNullSimulationSpec) -> list[AssignmentUnit]:
    units: list[AssignmentUnit] = []
    n = spec.num_units
    family = spec.assignment_family
    if family == SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        for i in range(n):
            units.append(AssignmentUnit(unit_id=f"u{i:02d}", pair_id=f"p{i // 2}"))
    elif family == SCMAssignmentFamily.STRATIFIED_RANDOMIZED:
        n_strata = max(2, min(4, n // 3))
        per = n // n_strata
        for i in range(n):
            units.append(AssignmentUnit(unit_id=f"u{i:02d}", stratum_id=f"g{i // per}"))
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
    spec: SCMTreatedSetNullSimulationSpec,
    units: list[AssignmentUnit],
    rng: np.random.Generator,
) -> tuple[str, ...]:
    k = spec.num_treated
    family = spec.assignment_family
    if family == SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        pairs = _group_units(units, "pair_id")
        treated: list[str] = []
        for members in pairs.values():
            member_ids = [m.unit_id for m in members]
            treated.append(str(rng.choice(member_ids)))
        return tuple(sorted(treated))
    if family == SCMAssignmentFamily.STRATIFIED_RANDOMIZED:
        groups = _group_units(units, "stratum_id")
        treated_ids: list[str] = []
        per_group = max(1, k // max(1, len(groups)))
        for members in groups.values():
            ids = [m.unit_id for m in members]
            take = min(per_group, len(ids), k - len(treated_ids))
            if take > 0:
                chosen = rng.choice(ids, size=take, replace=False)
                treated_ids.extend(str(x) for x in chosen)
            if len(treated_ids) >= k:
                break
        return tuple(sorted(treated_ids[:k]))
    all_ids = [u.unit_id for u in units]
    chosen = rng.choice(all_ids, size=k, replace=False)
    return tuple(sorted(str(x) for x in chosen))


def _generate_null_outcomes(
    spec: SCMTreatedSetNullSimulationSpec,
    rng: np.random.Generator,
) -> np.ndarray:
    n_units = spec.num_units
    n_periods = spec.num_pre_periods + spec.num_post_periods
    dgp = spec.dgp_kind

    unit_effects = rng.normal(0.0, 1.0, size=n_units)
    time_effects = rng.normal(0.0, 0.5, size=n_periods)

    if dgp == SCMNullDGPKind.DONOR_MATCHED_LATENT_FACTOR:
        latent = rng.normal(0.0, 1.0, size=n_periods)
        loadings = rng.normal(1.0, 0.3, size=n_units)
        noise = rng.normal(0.0, 0.5, size=(n_units, n_periods))
        y = np.zeros((n_units, n_periods))
        for g in range(n_units):
            for t in range(n_periods):
                y[g, t] = (
                    loadings[g] * latent[t]
                    + unit_effects[g]
                    + time_effects[t]
                    + noise[g, t]
                )
        return y

    if dgp == SCMNullDGPKind.HETEROSKEDASTIC:
        noise_sd = rng.uniform(0.5, 2.0, size=n_units)
        noise = rng.normal(0.0, 1.0, size=(n_units, n_periods)) * noise_sd[:, None]
    else:
        noise = rng.normal(0.0, 1.0, size=(n_units, n_periods))

    y = np.zeros((n_units, n_periods))
    for g in range(n_units):
        for t in range(n_periods):
            val = noise[g, t]
            if dgp in {
                SCMNullDGPKind.UNIT_FIXED_EFFECT,
                SCMNullDGPKind.UNIT_AND_TIME_FIXED_EFFECT,
                SCMNullDGPKind.HETEROSKEDASTIC,
            }:
                val += unit_effects[g]
            if dgp == SCMNullDGPKind.UNIT_AND_TIME_FIXED_EFFECT:
                val += time_effects[t]
            y[g, t] = val
    return y


def _period_id_tuples(spec: SCMTreatedSetNullSimulationSpec) -> tuple[tuple[str, ...], tuple[str, ...]]:
    pre = tuple(f"p{i}" for i in range(spec.num_pre_periods))
    post = tuple(
        f"p{i}" for i in range(spec.num_pre_periods, spec.num_pre_periods + spec.num_post_periods)
    )
    return pre, post


def _run_one_replication(
    spec: SCMTreatedSetNullSimulationSpec,
    replication_id: int,
) -> tuple[SCMNullReplicationResult | None, str | None]:
    rep_seed = spec.seed + replication_id * 9973
    rng = np.random.default_rng(rep_seed)
    units = _build_units(spec)
    unit_ids = tuple(u.unit_id for u in units)
    outcomes = _generate_null_outcomes(spec, rng)
    panel = OutcomePanel(outcomes=outcomes, unit_ids=unit_ids)
    pre_ids, post_ids = _period_id_tuples(spec)

    observed_treated = _select_observed_treated(spec, units, rng)
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
    observed_stat = compute_scm_style_treated_set_statistic(
        panel, observed_treated, pre_ids, post_ids, spec.statistic_mode
    )
    if not math.isfinite(observed_stat):
        return None, "non_finite_observed_statistic"

    pseudo_stats: dict[str, float] = {}
    for assignment in valid:
        stat = compute_scm_style_treated_set_statistic(
            panel,
            assignment.pseudo_treated_unit_ids,
            pre_ids,
            post_ids,
            spec.statistic_mode,
        )
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
        SCMNullReplicationResult(
            replication_id=replication_id,
            observed_statistic=observed_stat,
            empirical_tail_fraction=tail,
            placebo_rank=rank,
            num_placebo_sets=len(pseudo_stats),
            rejected_by_alpha=rejected,
            diagnostic_notes=("scm_style_statistic_adapter",),
        ),
        None,
    )


def _assign_verdict(
    spec: SCMTreatedSetNullSimulationSpec,
    empirical_type_i: Mapping[str, float],
) -> SCMCalibrationVerdict:
    if not empirical_type_i:
        return SCMCalibrationVerdict.INVALID_CALIBRATION_SPEC
    calibrated = all(
        empirical_type_i[str(alpha)] <= alpha + 0.03 for alpha in spec.alpha_levels
    )
    borderline = all(
        empirical_type_i[str(alpha)] <= alpha + 0.06 for alpha in spec.alpha_levels
    )
    if calibrated:
        return SCMCalibrationVerdict.CALIBRATED_UNDER_TESTED_NULLS
    if borderline:
        return SCMCalibrationVerdict.BORDERLINE_REQUIRES_MORE_SIMULATION
    return SCMCalibrationVerdict.NOT_CALIBRATED_DIAGNOSTIC_ONLY


def run_scm_treated_set_null_calibration(
    spec: SCMTreatedSetNullSimulationSpec,
) -> SCMTreatedSetNullCalibrationResult:
    """Run SCM treated-set null calibration for one simulation specification."""
    valid, reasons = validate_scm_treated_set_null_simulation_spec(spec)
    if not valid:
        return SCMTreatedSetNullCalibrationResult(
            spec=spec,
            replication_results=(),
            empirical_type_i_by_alpha={},
            expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
            type_i_excess_by_alpha={},
            tail_fraction_quantiles={},
            verdict=SCMCalibrationVerdict.INVALID_CALIBRATION_SPEC,
            warnings=(CALIBRATION_WARNING,),
            blocked_reasons=reasons,
            governance_flags=_governance_flags(),
        )

    results: list[SCMNullReplicationResult] = []
    skip_reasons: list[str] = []

    for rep in range(spec.num_replications):
        rep_result, skip = _run_one_replication(spec, rep)
        if rep_result is None:
            if skip:
                skip_reasons.append(skip)
            continue
        results.append(rep_result)

    if len(results) < spec.min_replications:
        return SCMTreatedSetNullCalibrationResult(
            spec=spec,
            replication_results=tuple(results),
            empirical_type_i_by_alpha={},
            expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
            type_i_excess_by_alpha={},
            tail_fraction_quantiles={},
            verdict=SCMCalibrationVerdict.INVALID_CALIBRATION_SPEC,
            warnings=(CALIBRATION_WARNING,),
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

    return SCMTreatedSetNullCalibrationResult(
        spec=spec,
        replication_results=tuple(results),
        empirical_type_i_by_alpha=empirical_type_i,
        expected_type_i_by_alpha={str(a): a for a in spec.alpha_levels},
        type_i_excess_by_alpha=type_i_excess,
        tail_fraction_quantiles=quantiles,
        verdict=_assign_verdict(spec, empirical_type_i),
        warnings=(CALIBRATION_WARNING,),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def summarize_scm_treated_set_null_calibration_result(
    result: SCMTreatedSetNullCalibrationResult,
) -> dict[str, Any]:
    """Serialize SCM null-calibration result for validation archives."""
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


def _max_type_i_excess(result: SCMTreatedSetNullCalibrationResult) -> float:
    if not result.type_i_excess_by_alpha:
        return 0.0
    return max(result.type_i_excess_by_alpha.values())


def _build_comparison_summary(
    results: tuple[SCMTreatedSetNullCalibrationResult, ...],
) -> dict[str, Any]:
    max_by_mode: dict[str, float] = {}
    fragile_families: set[str] = set()
    fragile_dgps: set[str] = set()
    family_excess: dict[str, float] = {}
    dgp_excess: dict[str, float] = {}

    for result in results:
        mode = result.spec.statistic_mode.value
        excess = _max_type_i_excess(result)
        max_by_mode[mode] = max(max_by_mode.get(mode, 0.0), excess)

        fam = result.spec.assignment_family.value
        dgp = result.spec.dgp_kind.value
        family_excess[fam] = max(family_excess.get(fam, 0.0), excess)
        dgp_excess[dgp] = max(dgp_excess.get(dgp, 0.0), excess)

        if result.verdict == SCMCalibrationVerdict.NOT_CALIBRATED_DIAGNOSTIC_ONLY:
            fragile_families.add(fam)
            fragile_dgps.add(dgp)

    scm_eff = max_by_mode.get(SCMStatisticMode.SCM_STYLE_EFFECT.value, 0.0)
    scm_stud = max_by_mode.get(SCMStatisticMode.SCM_STYLE_STUDENTIZED_EFFECT.value, 0.0)
    dim = max_by_mode.get(SCMStatisticMode.SIMPLE_DIFF_IN_MEANS_BASELINE.value, 0.0)

    if scm_stud < scm_eff:
        stud_note = (
            "preliminary grid: SCM-style studentization reduces max type-I excess "
            f"({scm_stud:.3f} vs {scm_eff:.3f})"
        )
    else:
        stud_note = (
            "preliminary grid: SCM-style studentization does not reduce max type-I excess "
            f"({scm_stud:.3f} vs {scm_eff:.3f})"
        )

    latent_results = [
        r for r in results if r.spec.dgp_kind == SCMNullDGPKind.DONOR_MATCHED_LATENT_FACTOR
    ]
    latent_scm = max((_max_type_i_excess(r) for r in latent_results if r.spec.statistic_mode == SCMStatisticMode.SCM_STYLE_EFFECT), default=float("nan"))
    latent_dim = max((_max_type_i_excess(r) for r in latent_results if r.spec.statistic_mode == SCMStatisticMode.SIMPLE_DIFF_IN_MEANS_BASELINE), default=float("nan"))
    if math.isfinite(latent_scm) and math.isfinite(latent_dim):
        if latent_scm < latent_dim:
            scm_vs_dim = (
                "under donor-matched latent-factor null, SCM-style effect shows lower "
                f"max type-I excess than diff-in-means ({latent_scm:.3f} vs {latent_dim:.3f})"
            )
        else:
            scm_vs_dim = (
                "under donor-matched latent-factor null, SCM-style effect does not beat "
                f"diff-in-means baseline ({latent_scm:.3f} vs {latent_dim:.3f})"
            )
    else:
        scm_vs_dim = "donor-matched latent-factor comparison not available in grid"

    worst_family = max(family_excess, key=family_excess.get) if family_excess else None
    worst_dgp = max(dgp_excess, key=dgp_excess.get) if dgp_excess else None
    worst_mode = max(max_by_mode, key=max_by_mode.get) if max_by_mode else None

    return {
        "max_type_i_excess_by_statistic_mode": max_by_mode,
        "studentized_vs_unstudentized_note": stud_note,
        "scm_vs_diff_in_means_note": scm_vs_dim,
        "fragile_assignment_families": sorted(fragile_families),
        "fragile_dgps": sorted(fragile_dgps),
        "max_type_i_excess_mode": worst_mode,
        "most_fragile_assignment_family": worst_family,
        "most_fragile_dgp": worst_dgp,
    }


def run_scm_treated_set_null_calibration_grid(
    specs: tuple[SCMTreatedSetNullSimulationSpec, ...],
) -> tuple[SCMTreatedSetNullCalibrationResult, ...]:
    """Run SCM null calibration across a grid of specifications."""
    return tuple(run_scm_treated_set_null_calibration(spec) for spec in specs)


def summarize_scm_treated_set_null_calibration_grid(
    results: tuple[SCMTreatedSetNullCalibrationResult, ...],
) -> dict[str, Any]:
    """Summarize SCM null-calibration grid results."""
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
        max_excess = max(max_excess, _max_type_i_excess(result))

    comparison = _build_comparison_summary(results)

    return {
        "grid_result_count": len(results),
        "verdict_counts": verdict_counts,
        "dgp_coverage": dgp_coverage,
        "assignment_family_coverage": family_coverage,
        "statistic_mode_coverage": mode_coverage,
        "max_empirical_type_i_excess": max_excess if results else None,
        "comparison_summary": comparison,
        "governance_flags": _governance_flags(),
    }


def _base_spec(
    *,
    dgp: SCMNullDGPKind,
    family: SCMAssignmentFamily,
    mode: SCMStatisticMode,
    seed: int = 123,
    num_replications: int = 100,
    min_replications: int = 100,
) -> SCMTreatedSetNullSimulationSpec:
    num_units = 16 if family != SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED else 12
    num_treated = (
        num_units // 2
        if family == SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED
        else (4 if num_units >= 16 else 3)
    )
    return SCMTreatedSetNullSimulationSpec(
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


def build_default_scm_treated_set_null_calibration_grid() -> tuple[
    SCMTreatedSetNullSimulationSpec, ...
]:
    """Small deterministic grid for validation harness."""
    return (
        _base_spec(
            dgp=SCMNullDGPKind.IID_NORMAL,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SCM_STYLE_EFFECT,
            seed=201,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.IID_NORMAL,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SCM_STYLE_STUDENTIZED_EFFECT,
            seed=202,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.IID_NORMAL,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SIMPLE_DIFF_IN_MEANS_BASELINE,
            seed=203,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.UNIT_FIXED_EFFECT,
            family=SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            mode=SCMStatisticMode.SCM_STYLE_STUDENTIZED_EFFECT,
            seed=204,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.UNIT_AND_TIME_FIXED_EFFECT,
            family=SCMAssignmentFamily.STRATIFIED_RANDOMIZED,
            mode=SCMStatisticMode.SCM_STYLE_EFFECT,
            seed=205,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.HETEROSKEDASTIC,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SCM_STYLE_STUDENTIZED_EFFECT,
            seed=206,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.DONOR_MATCHED_LATENT_FACTOR,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SCM_STYLE_EFFECT,
            seed=207,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.DONOR_MATCHED_LATENT_FACTOR,
            family=SCMAssignmentFamily.COMPLETE_RANDOMIZED_SET,
            mode=SCMStatisticMode.SIMPLE_DIFF_IN_MEANS_BASELINE,
            seed=208,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.IID_NORMAL,
            family=SCMAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            mode=SCMStatisticMode.SCM_STYLE_EFFECT,
            seed=209,
        ),
        _base_spec(
            dgp=SCMNullDGPKind.IID_NORMAL,
            family=SCMAssignmentFamily.STRATIFIED_RANDOMIZED,
            mode=SCMStatisticMode.SCM_STYLE_STUDENTIZED_EFFECT,
            seed=210,
        ),
    )


__all__ = [
    "CALIBRATION_WARNING",
    "OutcomePanel",
    "SCMAssignmentFamily",
    "SCMCalibrationVerdict",
    "SCMNullDGPKind",
    "SCMNullReplicationResult",
    "SCMStatisticMode",
    "SCMTreatedSetNullCalibrationResult",
    "SCMTreatedSetNullSimulationSpec",
    "build_default_scm_treated_set_null_calibration_grid",
    "compute_scm_style_treated_set_statistic",
    "run_scm_treated_set_null_calibration",
    "run_scm_treated_set_null_calibration_grid",
    "summarize_scm_treated_set_null_calibration_grid",
    "summarize_scm_treated_set_null_calibration_result",
    "validate_scm_treated_set_null_simulation_spec",
]
