"""Tests for SCM_TREATED_SET_PLACEBO_INTEGRATION_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_treated_set_placebo import (
    SCMStatisticCompatibility,
    SCMStatisticContract,
    SCMStatisticSource,
    SCMTreatedSetIntegrationDecision,
    SCMTreatedSetPlaceboIntegrationSpec,
    build_scm_treated_set_placebo_readiness_examples,
    evaluate_scm_treated_set_placebo_integration,
    validate_scm_statistic_contract,
)

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED = AssignmentRole.BLOCKED.value

_PSEUDO = {f"p{i}": 0.05 * i for i in range(1, 6)}


def _contract(**kwargs) -> SCMStatisticContract:
    defaults = dict(
        statistic_kind="signed_effect",
        effect_direction="greater",
        statistic_source=SCMStatisticSource.PRECOMPUTED,
        observed_statistic=0.42,
        pseudo_statistic_by_assignment=_PSEUDO,
    )
    defaults.update(kwargs)
    return SCMStatisticContract(**defaults)


def _spec(**kwargs) -> SCMTreatedSetPlaceboIntegrationSpec:
    defaults = dict(
        num_treated_units=3,
        assignment_role=DESIGN,
        assignment_family="complete_randomized_set",
        num_valid_pseudo_assignments=5,
        statistic_contract=_contract(),
    )
    defaults.update(kwargs)
    return SCMTreatedSetPlaceboIntegrationSpec(**defaults)


def test_valid_design_based_candidate() -> None:
    result = evaluate_scm_treated_set_placebo_integration(_spec())
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE
    assert result.is_candidate
    assert result.empirical_tail_fraction is not None
    assert result.placebo_rank is not None
    assert "not a final production p-value" in result.warnings[0]


def test_two_sided_candidate() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(effect_direction="two_sided"))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE


def test_falsification_only_diagnostic() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(assignment_role=FALSIFICATION, assignment_family="greedy_matched_market_falsification")
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC
    assert result.is_falsification_only


def test_blocked_assignment_role() -> None:
    result = evaluate_scm_treated_set_placebo_integration(_spec(assignment_role=BLOCKED))
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED
    assert result.is_blocked


def test_single_treated_not_candidate() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(num_treated_units=1, assignment_role=FALSIFICATION)
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC
    assert not result.is_candidate


def test_missing_observed_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(observed_statistic=None))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED
    assert validate_scm_statistic_contract(_contract(observed_statistic=None)) == (
        SCMStatisticCompatibility.MISSING_OBSERVED
    )


def test_missing_pseudo_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(pseudo_statistic_by_assignment={}))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_statistic_mismatch_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(same_statistic_observed_and_pseudo=False))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_non_numeric_observed_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(observed_statistic=math.nan))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_non_numeric_pseudo_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(statistic_contract=_contract(pseudo_statistic_by_assignment={"p1": 0.1, "p2": math.inf}))
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_insufficient_pseudo_assignments_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(
            num_valid_pseudo_assignments=1,
            statistic_contract=_contract(pseudo_statistic_by_assignment={"p1": 0.1}),
        )
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


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
    result = evaluate_scm_treated_set_placebo_integration(_spec(**{field: True}))
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_production_live_scheduler_budget_blocked() -> None:
    result = evaluate_scm_treated_set_placebo_integration(
        _spec(
            requested_production_decisioning=True,
            requested_live_api=True,
            requested_scheduler=True,
            requested_budget_optimization=True,
        )
    )
    assert result.decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED


def test_method_randomization_bridge_scm() -> None:
    result = evaluate_scm_treated_set_placebo_integration(_spec())
    assert result.method_randomization_summary["method_family"] == "scm"


def test_scm_semantics_bridge_design_based() -> None:
    result = evaluate_scm_treated_set_placebo_integration(_spec())
    assert result.scm_semantics_summary["semantic_role"] == "design_based_randomization_candidate"


def test_governance_flags_false() -> None:
    result = evaluate_scm_treated_set_placebo_integration(_spec())
    flags = result.governance_flags
    assert all(v is False for v in flags.values())


def test_readiness_examples() -> None:
    examples = build_scm_treated_set_placebo_readiness_examples()
    assert len(examples) >= 3
    labels = {e["label"] for e in examples}
    assert "multi_treated_design_based_candidate" in labels
