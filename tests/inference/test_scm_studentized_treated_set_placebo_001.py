"""Tests for SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_studentized_treated_set_placebo import (
    SCMStudentizedCompatibility,
    SCMStudentizedIntegrationDecision,
    SCMStudentizedStatisticContract,
    SCMStudentizedStatisticSource,
    SCMStudentizedTreatedSetPlaceboSpec,
    build_scm_studentized_readiness_examples,
    evaluate_scm_studentized_treated_set_placebo,
    validate_scm_studentized_statistic_contract,
)

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED = AssignmentRole.BLOCKED.value


def _pseudo(n: int = 10) -> tuple[dict[str, float], dict[str, float]]:
    effects = {f"p{i}": 0.1 * i for i in range(1, n + 1)}
    scales = {k: 1.0 for k in effects}
    return effects, scales


def _contract(**kwargs) -> SCMStudentizedStatisticContract:
    effects, scales = _pseudo()
    defaults = dict(
        observed_effect=1.05,
        pseudo_effect_by_assignment=effects,
        observed_scale=1.0,
        pseudo_scale_by_assignment=scales,
        effect_direction="greater",
        scale_source="provided_standard_error",
        statistic_source=SCMStudentizedStatisticSource.PRECOMPUTED,
    )
    defaults.update(kwargs)
    return SCMStudentizedStatisticContract(**defaults)


def _spec(**kwargs) -> SCMStudentizedTreatedSetPlaceboSpec:
    defaults = dict(
        num_treated_units=3,
        assignment_role=DESIGN,
        assignment_family="complete_randomized_set",
        num_valid_pseudo_assignments=10,
        statistic_contract=_contract(),
        min_placebo_sets=10,
    )
    defaults.update(kwargs)
    return SCMStudentizedTreatedSetPlaceboSpec(**defaults)


def test_design_based_greater_candidate() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec())
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE
    assert result.is_candidate
    assert "not a final production p-value" in result.warnings[0]


def test_design_based_less_candidate() -> None:
    effects = {f"p{i}": -0.1 * i for i in range(1, 11)}
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            statistic_contract=_contract(
                observed_effect=-1.05,
                effect_direction="less",
                pseudo_effect_by_assignment=effects,
            )
        )
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE


def test_design_based_two_sided_candidate() -> None:
    effects = {f"p{i}": (-1) ** i * 0.1 * i for i in range(1, 11)}
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            statistic_contract=_contract(
                observed_effect=2.0,
                effect_direction="two_sided",
                pseudo_effect_by_assignment=effects,
            )
        )
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE


def test_falsification_diagnostic_only() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(assignment_role=FALSIFICATION, assignment_family="greedy_matched_market_falsification")
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY
    assert result.is_diagnostic_only


def test_blocked_assignment_role() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec(assignment_role=BLOCKED))
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_single_treated_not_candidate() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(num_treated_units=1, assignment_role=FALSIFICATION)
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY
    assert not result.is_candidate


def test_missing_observed_effect_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(observed_effect=None))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED
    assert validate_scm_studentized_statistic_contract(_contract(observed_effect=None)) == (
        SCMStudentizedCompatibility.MISSING_EFFECT
    )


def test_missing_observed_scale_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(observed_scale=None))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_missing_pseudo_effects_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(pseudo_effect_by_assignment={}))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_missing_pseudo_scales_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(pseudo_scale_by_assignment={}))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_effect_scale_mismatch_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            statistic_contract=_contract(
                pseudo_effect_by_assignment={"p1": 0.1},
                pseudo_scale_by_assignment={"p2": 1.0},
            ),
            min_placebo_sets=1,
            num_valid_pseudo_assignments=1,
        )
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_non_finite_observed_effect_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(observed_effect=math.nan))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_non_finite_pseudo_effect_blocked() -> None:
    effects, scales = _pseudo()
    effects = dict(effects)
    effects["p1"] = math.inf
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(pseudo_effect_by_assignment=effects))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_non_finite_observed_scale_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(observed_scale=math.nan))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_non_positive_pseudo_scale_blocked() -> None:
    effects, scales = _pseudo()
    scales = {k: -1.0 if k == "p3" else 1.0 for k in effects}
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(pseudo_scale_by_assignment=scales))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_effect_definition_mismatch_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(same_effect_definition_observed_and_pseudo=False))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_scale_definition_mismatch_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(same_scale_definition_observed_and_pseudo=False))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_insufficient_placebo_sets_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            statistic_contract=_contract(
                pseudo_effect_by_assignment={"p1": 0.1, "p2": 0.2},
                pseudo_scale_by_assignment={"p1": 1.0, "p2": 1.0},
            ),
            num_valid_pseudo_assignments=2,
        )
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_invalid_effect_direction_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(statistic_contract=_contract(effect_direction="invalid"))
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


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
    result = evaluate_scm_studentized_treated_set_placebo(_spec(**{field: True}))
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_production_live_scheduler_budget_blocked() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            requested_production_decisioning=True,
            requested_live_api=True,
            requested_scheduler=True,
            requested_budget_optimization=True,
        )
    )
    assert result.decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED


def test_studentized_bridge_rank_tail() -> None:
    effects = {f"p{i}": float(i) * 0.5 for i in range(1, 6)}
    scales = {k: 1.0 for k in effects}
    result = evaluate_scm_studentized_treated_set_placebo(
        _spec(
            statistic_contract=_contract(
                observed_effect=2.0,
                pseudo_effect_by_assignment=effects,
                pseudo_scale_by_assignment=scales,
            ),
            min_placebo_sets=5,
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.placebo_rank == 2
    assert math.isclose(result.empirical_tail_fraction or 0.0, 0.4)


def test_scm_treated_set_bridge() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec())
    assert result.scm_treated_set_summary["decision"] == "scm_treated_set_randomization_candidate"


def test_scm_semantics_bridge() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec())
    assert result.scm_semantics_summary["semantic_role"] == "design_based_randomization_candidate"


def test_method_randomization_bridge() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec())
    assert result.method_randomization_summary["method_family"] == "scm"
    assert result.method_randomization_summary["is_candidate"] is True


def test_governance_flags_false() -> None:
    result = evaluate_scm_studentized_treated_set_placebo(_spec())
    assert all(v is False for v in result.governance_flags.values())


def test_readiness_examples() -> None:
    examples = build_scm_studentized_readiness_examples()
    assert len(examples) >= 2
