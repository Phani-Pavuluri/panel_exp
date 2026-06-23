"""Tests for DESIGN-AWARE-ASSIGNMENT-GENERATORS-001."""

from __future__ import annotations

import pytest

from panel_exp.design.assignment_generators import (
    AssignmentDesignSpec,
    AssignmentFamily,
    AssignmentRole,
    AssignmentUnit,
    ValidityStatus,
    generate_pseudo_assignments,
    summarize_assignment_generation,
    validate_pseudo_assignment,
)


def _units_complete(n: int = 6, *, excluded: set[str] | None = None) -> list[AssignmentUnit]:
    excluded = excluded or set()
    return [
        AssignmentUnit(
            unit_id=f"u{i}",
            eligible=True,
            excluded=(f"u{i}" in excluded),
        )
        for i in range(n)
    ]


def test_complete_randomized_preserves_treated_size():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(8),
        observed_treated_unit_ids=("u0", "u1"),
        seed=7,
        min_assignments=5,
        max_assignments=10,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(len(a.pseudo_treated_unit_ids) == 2 for a in assignments)
    assert all(a.role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE for a in assignments)


def test_complete_randomized_excludes_ineligible_and_excluded_units():
    units = [
        AssignmentUnit(unit_id="u0", eligible=True),
        AssignmentUnit(unit_id="u1", eligible=False),
        AssignmentUnit(unit_id="u2", eligible=True, excluded=True),
        AssignmentUnit(unit_id="u3", eligible=True),
        AssignmentUnit(unit_id="u4", eligible=True),
        AssignmentUnit(unit_id="u5", eligible=True),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=units,
        observed_treated_unit_ids=("u0",),
        seed=1,
        min_assignments=2,
        max_assignments=5,
    )
    assignments = generate_pseudo_assignments(spec)
    treated_union = {uid for a in assignments for uid in a.pseudo_treated_unit_ids}
    assert "u1" not in treated_union
    assert "u2" not in treated_union


def test_complete_randomized_is_deterministic_by_seed():
    spec_a = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(10),
        observed_treated_unit_ids=("u0", "u1"),
        seed=42,
        min_assignments=5,
        max_assignments=8,
    )
    spec_b = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(10),
        observed_treated_unit_ids=("u0", "u1"),
        seed=99,
        min_assignments=5,
        max_assignments=8,
    )
    a1 = generate_pseudo_assignments(spec_a)
    a2 = generate_pseudo_assignments(spec_a)
    a3 = generate_pseudo_assignments(spec_b)
    assert [x.pseudo_treated_unit_ids for x in a1] == [x.pseudo_treated_unit_ids for x in a2]
    assert [x.pseudo_treated_unit_ids for x in a1] != [x.pseudo_treated_unit_ids for x in a3]


def test_complete_randomized_blocks_too_few_assignments():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(4),
        observed_treated_unit_ids=("u0", "u1", "u2"),
        seed=1,
        min_assignments=10,
        max_assignments=20,
    )
    assert generate_pseudo_assignments(spec) == []


def test_matched_pair_selects_one_per_pair():
    units = [
        AssignmentUnit(unit_id="a1", pair_id="p1"),
        AssignmentUnit(unit_id="a2", pair_id="p1"),
        AssignmentUnit(unit_id="b1", pair_id="p2"),
        AssignmentUnit(unit_id="b2", pair_id="p2"),
        AssignmentUnit(unit_id="c1", pair_id="p3"),
        AssignmentUnit(unit_id="c2", pair_id="p3"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("a1", "b2", "c1"),
        seed=3,
        min_assignments=4,
        max_assignments=8,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    for assignment in assignments:
        treated = set(assignment.pseudo_treated_unit_ids)
        assert len(treated & {"a1", "a2"}) == 1
        assert len(treated & {"b1", "b2"}) == 1
        assert len(treated & {"c1", "c2"}) == 1


def test_matched_pair_blocks_malformed_pairs():
    units = [
        AssignmentUnit(unit_id="a1", pair_id="p1"),
        AssignmentUnit(unit_id="a2", pair_id="p1"),
        AssignmentUnit(unit_id="a3", pair_id="p1"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("a1",),
        seed=1,
        min_assignments=1,
        max_assignments=5,
    )
    assert generate_pseudo_assignments(spec) == []


def test_matched_block_preserves_treated_count_per_block():
    units = [
        AssignmentUnit(unit_id="b1u1", block_id="b1"),
        AssignmentUnit(unit_id="b1u2", block_id="b1"),
        AssignmentUnit(unit_id="b1u3", block_id="b1"),
        AssignmentUnit(unit_id="b2u1", block_id="b2"),
        AssignmentUnit(unit_id="b2u2", block_id="b2"),
        AssignmentUnit(unit_id="b2u3", block_id="b2"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("b1u1", "b1u2", "b2u1"),
        seed=5,
        min_assignments=2,
        max_assignments=6,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    for assignment in assignments:
        treated = assignment.pseudo_treated_unit_ids
        b1 = [u for u in treated if u.startswith("b1")]
        b2 = [u for u in treated if u.startswith("b2")]
        assert len(b1) == 2
        assert len(b2) == 1


def test_matched_block_blocks_impossible_block():
    units = [
        AssignmentUnit(unit_id="b1u1", block_id="b1", eligible=True),
        AssignmentUnit(unit_id="b1u2", block_id="b1", eligible=False),
        AssignmentUnit(unit_id="b2u1", block_id="b2"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("b1u1", "b1u2", "b2u1"),
        seed=1,
        min_assignments=1,
        max_assignments=5,
    )
    assert generate_pseudo_assignments(spec) == []


def test_stratified_preserves_treated_count_per_stratum():
    units = [
        AssignmentUnit(unit_id="s1a", stratum_id="s1"),
        AssignmentUnit(unit_id="s1b", stratum_id="s1"),
        AssignmentUnit(unit_id="s1c", stratum_id="s1"),
        AssignmentUnit(unit_id="s2a", stratum_id="s2"),
        AssignmentUnit(unit_id="s2b", stratum_id="s2"),
        AssignmentUnit(unit_id="s2c", stratum_id="s2"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.STRATIFIED_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("s1a", "s2a", "s2b"),
        seed=11,
        min_assignments=2,
        max_assignments=6,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    for assignment in assignments:
        treated = assignment.pseudo_treated_unit_ids
        assert len([u for u in treated if u.startswith("s1")]) == 1
        assert len([u for u in treated if u.startswith("s2")]) == 2


def test_stratified_blocks_impossible_stratum():
    units = [
        AssignmentUnit(unit_id="s1a", stratum_id="s1", eligible=True),
        AssignmentUnit(unit_id="s1b", stratum_id="s1", eligible=False),
        AssignmentUnit(unit_id="s2a", stratum_id="s2"),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.STRATIFIED_RANDOMIZED,
        units=units,
        observed_treated_unit_ids=("s1a", "s1b", "s2a"),
        seed=1,
        min_assignments=1,
        max_assignments=5,
    )
    assert generate_pseudo_assignments(spec) == []


def test_rerandomized_without_acceptance_rule_downgrades():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
        units=_units_complete(8),
        observed_treated_unit_ids=("u0", "u1"),
        seed=2,
        min_assignments=3,
        max_assignments=5,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(a.role == AssignmentRole.FALSIFICATION_ONLY for a in assignments)
    assert all(
        a.validity_status
        == ValidityStatus.ASSIGNMENT_GENERATION_DOWNGRADED_TO_FALSIFICATION_ONLY.value
        for a in assignments
    )


def test_rerandomized_with_simple_balance_rule_filters_assignments():
    units = [
        AssignmentUnit(unit_id="u0", covariates={"x": 1.0}),
        AssignmentUnit(unit_id="u1", covariates={"x": 1.0}),
        AssignmentUnit(unit_id="u2", covariates={"x": 10.0}),
        AssignmentUnit(unit_id="u3", covariates={"x": 10.0}),
        AssignmentUnit(unit_id="u4", covariates={"x": 5.0}),
        AssignmentUnit(unit_id="u5", covariates={"x": 5.0}),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
        units=units,
        observed_treated_unit_ids=("u0", "u4"),
        constraints={"balance_key": "x", "max_imbalance": 3.0},
        seed=4,
        min_assignments=2,
        max_assignments=10,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(a.role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE for a in assignments)


def test_greedy_matched_market_is_falsification_only():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION,
        units=_units_complete(7),
        observed_treated_unit_ids=("u0", "u1"),
        seed=1,
        min_assignments=3,
        max_assignments=5,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(a.role == AssignmentRole.FALSIFICATION_ONLY for a in assignments)


def test_kernel_thinning_is_falsification_only():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.KERNEL_THINNING_FALSIFICATION,
        units=_units_complete(7),
        observed_treated_unit_ids=("u0",),
        seed=1,
        min_assignments=3,
        max_assignments=5,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(a.role == AssignmentRole.FALSIFICATION_ONLY for a in assignments)


def test_fixed_deterministic_is_falsification_only():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION,
        units=_units_complete(6),
        observed_treated_unit_ids=("u2",),
        seed=1,
        min_assignments=2,
        max_assignments=4,
    )
    assignments = generate_pseudo_assignments(spec)
    assert assignments
    assert all(a.role == AssignmentRole.FALSIFICATION_ONLY for a in assignments)


def test_unknown_assignment_is_blocked():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED,
        units=_units_complete(5),
        observed_treated_unit_ids=("u0",),
        seed=1,
        min_assignments=1,
        max_assignments=5,
    )
    assert generate_pseudo_assignments(spec) == []


def test_no_generated_assignment_uses_excluded_units():
    units = [
        AssignmentUnit(unit_id="u0", eligible=True),
        AssignmentUnit(unit_id="u1", eligible=True, excluded=True),
        AssignmentUnit(unit_id="u2", eligible=True),
        AssignmentUnit(unit_id="u3", eligible=True),
        AssignmentUnit(unit_id="u4", eligible=True),
    ]
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=units,
        observed_treated_unit_ids=("u0",),
        seed=8,
        min_assignments=2,
        max_assignments=4,
    )
    assignments = generate_pseudo_assignments(spec)
    assert all("u1" not in a.pseudo_treated_unit_ids for a in assignments)


def test_summary_reports_role_counts_and_validity():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(8),
        observed_treated_unit_ids=("u0",),
        seed=1,
        min_assignments=3,
        max_assignments=5,
    )
    assignments = generate_pseudo_assignments(spec)
    summary = summarize_assignment_generation(spec, assignments)
    assert summary["assignment_count"] == len(assignments)
    assert summary["role_counts"][AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value] == len(
        assignments
    )
    assert summary["eligible_unit_count"] == 8


def test_validate_flags_excluded_unit_in_treated_set():
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=_units_complete(4),
        observed_treated_unit_ids=("u0",),
        seed=1,
        min_assignments=1,
        max_assignments=2,
    )
    bad = generate_pseudo_assignments(spec)[0]
    tampered = bad.__class__(
        **{
            **bad.__dict__,
            "pseudo_treated_unit_ids": ("u0", "u1"),
            "pseudo_control_unit_ids": ("u2", "u3"),
        }
    )
    validated = validate_pseudo_assignment(spec, tampered)
    assert validated.validity_status == ValidityStatus.ASSIGNMENT_GENERATION_INVALID.value
