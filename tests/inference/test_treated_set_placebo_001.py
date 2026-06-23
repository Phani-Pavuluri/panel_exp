"""Tests for MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001."""

from __future__ import annotations

import pytest

from panel_exp.design.assignment_generators import (
    AssignmentDesignSpec,
    AssignmentFamily,
    AssignmentRole,
    AssignmentUnit,
    generate_pseudo_assignments,
)
from panel_exp.inference.treated_set_placebo import (
    PlaceboDecision,
    PlaceboSemanticRole,
    TreatedSetPlaceboSpec,
    compute_placebo_rank,
    evaluate_treated_set_placebo,
    reject_leave_one_treated_out_as_placebo,
)


def _units_complete(n: int = 8) -> list[AssignmentUnit]:
    return [AssignmentUnit(unit_id=f"u{i}", eligible=True) for i in range(n)]


def _stats_for_spec(spec: AssignmentDesignSpec, *, base: float = 0.1) -> dict[str, float]:
    assignments = generate_pseudo_assignments(spec)
    return {a.assignment_id: base + i * 0.01 for i, a in enumerate(assignments)}


def _evaluate(
    family: AssignmentFamily,
    *,
    units: list[AssignmentUnit] | None = None,
    observed: tuple[str, ...] = ("u0", "u1"),
    constraints: dict | None = None,
    min_placebo: int = 5,
    observed_stat: float = 0.5,
    metadata: dict | None = None,
    stats: dict[str, float] | None = None,
    seed: int = 7,
) -> object:
    units = units or _units_complete()
    design = AssignmentDesignSpec(
        family=family,
        units=units,
        observed_treated_unit_ids=observed,
        constraints=constraints,
        seed=seed,
        min_assignments=min_placebo,
        max_assignments=min_placebo + 5,
    )
    if stats is None:
        stats = _stats_for_spec(design)
    spec = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=observed_stat,
        pseudo_statistic_by_assignment=stats,
        minimum_valid_placebo_sets=min_placebo,
        metadata=metadata,
    )
    return evaluate_treated_set_placebo(spec)


def test_design_based_complete_randomized_supported():
    result = _evaluate(AssignmentFamily.COMPLETE_RANDOMIZED_SET)
    assert result.decision == PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED
    assert result.semantic_role == PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    assert result.placebo_rank is not None
    assert result.empirical_tail_fraction is not None


def test_design_based_stratified_supported():
    units = [
        AssignmentUnit(unit_id="s0a", stratum_id="s0"),
        AssignmentUnit(unit_id="s0b", stratum_id="s0"),
        AssignmentUnit(unit_id="s0c", stratum_id="s0"),
        AssignmentUnit(unit_id="s1a", stratum_id="s1"),
        AssignmentUnit(unit_id="s1b", stratum_id="s1"),
        AssignmentUnit(unit_id="s1c", stratum_id="s1"),
    ]
    result = _evaluate(
        AssignmentFamily.STRATIFIED_RANDOMIZED,
        units=units,
        observed=("s0a", "s1b"),
        min_placebo=4,
    )
    assert result.decision == PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED
    assert result.semantic_role == PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE


def test_design_based_matched_pair_supported():
    units = [
        AssignmentUnit(unit_id="a1", pair_id="p1"),
        AssignmentUnit(unit_id="a2", pair_id="p1"),
        AssignmentUnit(unit_id="b1", pair_id="p2"),
        AssignmentUnit(unit_id="b2", pair_id="p2"),
        AssignmentUnit(unit_id="c1", pair_id="p3"),
        AssignmentUnit(unit_id="c2", pair_id="p3"),
    ]
    result = _evaluate(
        AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
        units=units,
        observed=("a1", "b2", "c1"),
        min_placebo=4,
    )
    assert result.decision == PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED


def test_falsification_only_design_does_not_claim_design_based():
    result = _evaluate(AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION, min_placebo=3)
    assert result.decision == PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY
    assert result.semantic_role == PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    assert any("falsification-only" in w.lower() for w in result.warnings)


def test_unknown_assignment_blocks_placebo():
    result = _evaluate(AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED, min_placebo=2)
    assert result.decision == PlaceboDecision.UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED
    assert result.semantic_role == PlaceboSemanticRole.BLOCKED


def test_too_few_pseudo_assignments_blocks():
    design = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(5),
        observed_treated_unit_ids=("u0", "u1", "u2", "u3"),
        seed=1,
        min_assignments=50,
        max_assignments=60,
    )
    spec = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=0.2,
        pseudo_statistic_by_assignment={},
        minimum_valid_placebo_sets=20,
    )
    result = evaluate_treated_set_placebo(spec)
    assert result.decision == PlaceboDecision.TOO_FEW_VALID_PSEUDO_ASSIGNMENTS


def test_leave_one_treated_out_rejected_as_placebo():
    result = _evaluate(
        AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        metadata={"leave_one_treated_out_requested": True},
    )
    assert result.decision == PlaceboDecision.LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO
    assert result.semantic_role == PlaceboSemanticRole.BLOCKED


def test_tail_fraction_greater():
    rank, tail = compute_placebo_rank(0.5, [0.1, 0.3, 0.5, 0.7], "greater")
    assert rank == 2
    assert tail == pytest.approx(0.5)


def test_tail_fraction_less():
    rank, tail = compute_placebo_rank(0.5, [0.1, 0.3, 0.5, 0.7], "less")
    assert rank == 3
    assert tail == pytest.approx(0.75)


def test_tail_fraction_two_sided():
    rank, tail = compute_placebo_rank(-0.5, [0.1, -0.5, 0.5, -0.9], "two_sided")
    assert rank == 3
    assert tail == pytest.approx(0.75)


def test_missing_pseudo_statistic_blocks_or_warns():
    design = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(),
        observed_treated_unit_ids=("u0", "u1"),
        seed=3,
        min_assignments=5,
        max_assignments=10,
    )
    assignments = generate_pseudo_assignments(design)
    partial = {assignments[0].assignment_id: 0.1}
    spec = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=0.5,
        pseudo_statistic_by_assignment=partial,
        minimum_valid_placebo_sets=5,
    )
    blocked = evaluate_treated_set_placebo(spec)
    assert blocked.decision == PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED

    spec_warn = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=0.5,
        pseudo_statistic_by_assignment=partial,
        minimum_valid_placebo_sets=1,
        metadata={"strict_missing_stats": False},
    )
    warned = evaluate_treated_set_placebo(spec_warn)
    assert warned.decision == PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED
    assert warned.num_valid_placebo_sets == 1


def test_assignment_id_mismatch_blocks():
    design = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(),
        observed_treated_unit_ids=("u0", "u1"),
        seed=4,
        min_assignments=5,
        max_assignments=10,
    )
    assignments = generate_pseudo_assignments(design)
    stats = _stats_for_spec(design)
    stats["extra:bad:id"] = 9.9
    spec = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=0.5,
        pseudo_statistic_by_assignment=stats,
        minimum_valid_placebo_sets=5,
    )
    result = evaluate_treated_set_placebo(spec)
    assert result.decision == PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED
    assert "mismatch" in result.blocked_reasons[0]


def test_semantic_role_counts_preserved():
    result = _evaluate(AssignmentFamily.COMPLETE_RANDOMIZED_SET)
    assert result.assignment_role_counts.get(
        AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value, 0
    ) == result.num_valid_placebo_sets


def test_multicell_global_claim_blocked_if_requested():
    result = _evaluate(
        AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        metadata={"multicell_global_claim_requested": True},
    )
    assert result.decision == PlaceboDecision.MULTICELL_GLOBAL_CLAIM_BLOCKED


def test_reject_leave_one_treated_out_helper():
    spec = TreatedSetPlaceboSpec(
        design_spec=AssignmentDesignSpec(
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=_units_complete(),
            observed_treated_unit_ids=("u0",),
            seed=1,
            min_assignments=2,
            max_assignments=5,
        ),
        observed_statistic=0.0,
    )
    result = reject_leave_one_treated_out_as_placebo(spec)
    assert result.decision == PlaceboDecision.LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO
