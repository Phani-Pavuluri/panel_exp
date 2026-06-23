"""Tests for STUDENTIZED_PLACEBO_RANK_INFERENCE_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.studentized_placebo_rank import (
    ScaleSource,
    ScaleValidity,
    StudentizedEffectDirection,
    StudentizedPlaceboRankSpec,
    StudentizedRankDecision,
    compute_studentized_placebo_rank,
    compute_studentized_statistics,
    evaluate_studentized_placebo_rank,
    validate_studentized_scale_contract,
)

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED = AssignmentRole.BLOCKED.value


def _pseudo(n: int = 10) -> tuple[dict[str, float], dict[str, float]]:
    effects = {f"p{i}": 0.1 * i for i in range(1, n + 1)}
    scales = {k: 1.0 for k in effects}
    return effects, scales


def _spec(**kwargs) -> StudentizedPlaceboRankSpec:
    effects, scales = _pseudo()
    defaults = dict(
        observed_effect=1.05,
        pseudo_effect_by_assignment=effects,
        observed_scale=1.0,
        pseudo_scale_by_assignment=scales,
        effect_direction=StudentizedEffectDirection.GREATER,
        scale_source=ScaleSource.PROVIDED_STANDARD_ERROR,
        assignment_role=DESIGN,
        min_placebo_sets=10,
    )
    defaults.update(kwargs)
    return StudentizedPlaceboRankSpec(**defaults)


def test_design_based_greater_candidate() -> None:
    result = evaluate_studentized_placebo_rank(_spec())
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE
    assert result.is_candidate
    assert result.placebo_rank is not None


def test_design_based_less_candidate() -> None:
    effects, scales = _pseudo()
    result = evaluate_studentized_placebo_rank(
        _spec(
            observed_effect=-1.05,
            effect_direction=StudentizedEffectDirection.LESS,
            pseudo_effect_by_assignment={k: -v for k, v in effects.items()},
        )
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE


def test_design_based_two_sided_candidate() -> None:
    effects = {f"p{i}": (-1) ** i * 0.1 * i for i in range(1, 11)}
    scales = {k: 1.0 for k in effects}
    result = evaluate_studentized_placebo_rank(
        _spec(
            observed_effect=2.0,
            effect_direction=StudentizedEffectDirection.TWO_SIDED,
            pseudo_effect_by_assignment=effects,
            pseudo_scale_by_assignment=scales,
        )
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE


def test_falsification_diagnostic_only() -> None:
    result = evaluate_studentized_placebo_rank(_spec(assignment_role=FALSIFICATION))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_DIAGNOSTIC_ONLY
    assert result.is_diagnostic_only


def test_blocked_assignment_role() -> None:
    result = evaluate_studentized_placebo_rank(_spec(assignment_role=BLOCKED))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_missing_observed_scale_blocked() -> None:
    result = evaluate_studentized_placebo_rank(_spec(observed_scale=None))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED
    assert validate_studentized_scale_contract(_spec(observed_scale=None)) == (
        ScaleValidity.MISSING_OBSERVED_SCALE
    )


def test_missing_pseudo_scale_blocked() -> None:
    result = evaluate_studentized_placebo_rank(_spec(pseudo_scale_by_assignment={}))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_effect_scale_mismatch_blocked() -> None:
    result = evaluate_studentized_placebo_rank(
        _spec(
            pseudo_effect_by_assignment={"p1": 0.1},
            pseudo_scale_by_assignment={"p2": 1.0},
            min_placebo_sets=1,
        )
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_zero_observed_scale_blocked() -> None:
    result = evaluate_studentized_placebo_rank(_spec(observed_scale=0.0))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_negative_pseudo_scale_blocked() -> None:
    effects, _ = _pseudo()
    scales = {k: -1.0 if k == "p3" else 1.0 for k in effects}
    result = evaluate_studentized_placebo_rank(_spec(pseudo_scale_by_assignment=scales))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_nan_observed_effect_blocked() -> None:
    result = evaluate_studentized_placebo_rank(_spec(observed_effect=math.nan))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_infinite_pseudo_effect_blocked() -> None:
    effects, scales = _pseudo()
    effects = dict(effects)
    effects["p1"] = math.inf
    result = evaluate_studentized_placebo_rank(
        _spec(pseudo_effect_by_assignment=effects, pseudo_scale_by_assignment=scales)
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_nan_observed_scale_blocked() -> None:
    result = evaluate_studentized_placebo_rank(_spec(observed_scale=math.nan))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_insufficient_placebo_sets_blocked() -> None:
    result = evaluate_studentized_placebo_rank(
        _spec(
            pseudo_effect_by_assignment={"p1": 0.1, "p2": 0.2},
            pseudo_scale_by_assignment={"p1": 1.0, "p2": 1.0},
            min_placebo_sets=10,
        )
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


@pytest.mark.parametrize(
    "field",
    [
        "requested_final_p_value",
        "requested_causal_interval",
        "requested_trustreport_authorization",
        "requested_calibration_signal",
        "requested_mmm_ingestion",
        "requested_llm_decisioning",
    ],
)
def test_overclaim_blocked(field: str) -> None:
    result = evaluate_studentized_placebo_rank(_spec(**{field: True}))
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_production_live_scheduler_budget_blocked() -> None:
    result = evaluate_studentized_placebo_rank(
        _spec(
            requested_production_decisioning=True,
            requested_live_api=True,
            requested_scheduler=True,
            requested_budget_optimization=True,
        )
    )
    assert result.decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED


def test_greater_rank_tail_fraction() -> None:
    pseudo = {"p1": 0.5, "p2": 1.0, "p3": 1.5, "p4": 2.0, "p5": 2.5}
    rank, tail = compute_studentized_placebo_rank(
        2.0, pseudo, StudentizedEffectDirection.GREATER
    )
    assert rank == 2
    assert math.isclose(tail, 0.4)


def test_less_rank_tail_fraction() -> None:
    pseudo = {"p1": -0.3, "p2": -0.8, "p3": -1.0, "p4": -1.2, "p5": -1.5}
    rank, tail = compute_studentized_placebo_rank(
        -1.0, pseudo, StudentizedEffectDirection.LESS
    )
    assert rank == 3
    assert math.isclose(tail, 0.6)


def test_two_sided_rank_tail_fraction() -> None:
    pseudo = {"p1": -2.0, "p2": 0.5, "p3": 1.0, "p4": 2.0, "p5": 1.8}
    rank, tail = compute_studentized_placebo_rank(
        2.0, pseudo, StudentizedEffectDirection.TWO_SIDED
    )
    assert rank == 2
    assert math.isclose(tail, 0.4)


def test_compute_studentized_statistics() -> None:
    spec = _spec(observed_effect=2.0, observed_scale=2.0, null_value=0.5)
    observed, pseudo = compute_studentized_statistics(spec)
    assert math.isclose(observed, 0.75)
    assert math.isclose(pseudo["p1"], -0.4)


def test_governance_flags_false() -> None:
    result = evaluate_studentized_placebo_rank(_spec())
    assert all(v is False for v in result.governance_flags.values())
