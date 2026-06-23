"""Tests for AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.augsynth_point_randomization import (
    AugSynthCompatibility,
    AugSynthInferenceMode,
    AugSynthPointRandomizationSpec,
    AugSynthPointStatisticContract,
    AugSynthRandomizationDecision,
    AugSynthStatisticKind,
    build_augsynth_point_randomization_readiness_matrix,
    evaluate_augsynth_point_randomization,
    validate_augsynth_point_statistic_contract,
)
from panel_exp.inference.method_specific_randomization import (
    MethodFamily,
    RandomizationValidationRole,
)

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED = AssignmentRole.BLOCKED.value

_PSEUDO = {f"p{i}": 0.05 * i for i in range(1, 12)}


def _contract(**kwargs) -> AugSynthPointStatisticContract:
    defaults = dict(
        observed_statistic=0.42,
        pseudo_statistic_by_assignment=dict(_PSEUDO),
        statistic_kind=AugSynthStatisticKind.POINT_EFFECT,
        inference_mode=AugSynthInferenceMode.POINT_ONLY,
        effect_direction="greater",
        estimand_id="ate",
        outcome_scale="absolute",
        pre_period_id="pre",
        post_period_id="post",
        donor_eligibility_rule_id="default",
        augmentation_config_id="ridge_v1",
    )
    defaults.update(kwargs)
    return AugSynthPointStatisticContract(**defaults)


def _spec(**kwargs) -> AugSynthPointRandomizationSpec:
    if "contract" in kwargs:
        kwargs["statistic_contract"] = kwargs.pop("contract")
    defaults = dict(
        assignment_role=DESIGN,
        assignment_family="complete_randomized_set",
        num_treated_units=2,
        num_valid_pseudo_assignments=11,
        statistic_contract=_contract(),
    )
    defaults.update(kwargs)
    return AugSynthPointRandomizationSpec(**defaults)


def test_point_design_candidate() -> None:
    result = evaluate_augsynth_point_randomization(_spec())
    assert result.decision == AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE
    assert result.is_candidate
    assert result.governance_flags["augsynth_jk_authorized"] is False


def test_relative_point_candidate() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.RELATIVE_POINT_EFFECT))
    )
    assert result.is_candidate


def test_studentized_point_candidate() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(
            contract=_contract(
                statistic_kind=AugSynthStatisticKind.STUDENTIZED_POINT_EFFECT,
                inference_mode=AugSynthInferenceMode.STUDENTIZED_PLACEBO_RANK,
            )
        )
    )
    assert result.is_candidate


def test_falsification_diagnostic_only() -> None:
    result = evaluate_augsynth_point_randomization(_spec(assignment_role=FALSIFICATION))
    assert result.decision == AugSynthRandomizationDecision.AUGSYNTH_POINT_DIAGNOSTIC_ONLY
    assert result.is_diagnostic_only


def test_blocked_assignment() -> None:
    result = evaluate_augsynth_point_randomization(_spec(assignment_role=BLOCKED))
    assert result.is_blocked


def test_jk_statistic_diagnostic_only() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.JACKKNIFE_EFFECT))
    )
    assert result.decision == AugSynthRandomizationDecision.AUGSYNTH_JK_DIAGNOSTIC_ONLY
    assert not result.is_candidate


def test_jk_production_request_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(requested_jackknife_production_inference=True)
    )
    assert result.is_blocked


def test_missing_observed_blocked() -> None:
    compat = validate_augsynth_point_statistic_contract(_contract(observed_statistic=None))
    assert compat == AugSynthCompatibility.MISSING_OBSERVED_STATISTIC


def test_missing_pseudo_blocked() -> None:
    compat = validate_augsynth_point_statistic_contract(_contract(pseudo_statistic_by_assignment={}))
    assert compat == AugSynthCompatibility.MISSING_PSEUDO_STATISTICS


def test_unsupported_statistic_kind_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.UNKNOWN))
    )
    assert result.is_blocked


def test_unsupported_inference_mode_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(inference_mode=AugSynthInferenceMode.UNKNOWN))
    )
    assert result.is_blocked


@pytest.mark.parametrize(
    "field",
    [
        "same_statistic_definition_observed_and_pseudo",
        "same_estimand_observed_and_pseudo",
        "same_outcome_scale_observed_and_pseudo",
        "same_time_window_observed_and_pseudo",
        "same_donor_eligibility_observed_and_pseudo",
        "same_augmentation_config_observed_and_pseudo",
    ],
)
def test_contract_mismatch_blocked(field: str) -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(**{field: False}))
    )
    assert result.is_blocked


def test_non_finite_observed_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(observed_statistic=float("nan")))
    )
    assert result.is_blocked


def test_non_finite_pseudo_blocked() -> None:
    pseudo = {"p1": float("inf"), **{f"p{i}": 0.1 for i in range(2, 12)}}
    result = evaluate_augsynth_point_randomization(_spec(contract=_contract(pseudo_statistic_by_assignment=pseudo)))
    assert result.is_blocked


def test_insufficient_pseudo_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(
            contract=_contract(pseudo_statistic_by_assignment={f"p{i}": 0.1 for i in range(1, 6)}),
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.is_blocked


def test_invalid_effect_direction_blocked() -> None:
    result = evaluate_augsynth_point_randomization(
        _spec(contract=_contract(effect_direction="invalid"))
    )
    assert result.is_blocked


@pytest.mark.parametrize(
    "flag",
    [
        "requested_final_p_value",
        "requested_causal_interval",
        "requested_trustreport_authorization",
        "requested_calibration_signal",
        "requested_mmm_ingestion",
        "requested_llm_decisioning",
        "requested_production_decisioning",
        "requested_live_api",
        "requested_scheduler",
        "requested_budget_optimization",
    ],
)
def test_platform_requests_blocked(flag: str) -> None:
    result = evaluate_augsynth_point_randomization(_spec(**{flag: True}))
    assert result.is_blocked


def test_placebo_bridge_rank_tail() -> None:
    pseudo = {"p1": 0.1, "p2": 0.2, "p3": 0.3, "p4": 0.4, "p5": 0.5, "p6": 0.6}
    result = evaluate_augsynth_point_randomization(
        _spec(
            contract=_contract(
                observed_statistic=0.5,
                pseudo_statistic_by_assignment=pseudo,
                effect_direction="greater",
                inference_mode=AugSynthInferenceMode.PLACEBO_RANK,
            ),
            num_valid_pseudo_assignments=6,
            min_pseudo_assignments=6,
        )
    )
    assert result.placebo_rank == 2
    assert math.isclose(result.empirical_tail_fraction or 0, 2 / 6, rel_tol=0, abs_tol=1e-9)


def test_method_bridge_augsynth_family() -> None:
    result = evaluate_augsynth_point_randomization(_spec())
    assert result.method_randomization_summary["method_family"] == MethodFamily.AUGSYNTH_CVXPY.value
    assert (
        result.method_randomization_summary["role"]
        == RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
    )


def test_readiness_matrix_covers_statistic_kinds() -> None:
    matrix = build_augsynth_point_randomization_readiness_matrix()
    kinds = {row["statistic_kind"] for row in matrix}
    assert kinds == {k.value for k in AugSynthStatisticKind}
