"""Tests for MULTICELL_SHARED_CONTROL_MULTIPLICITY_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.inference.multicell_multiplicity import (
    MultiCellDecisionUseCase,
    MultiCellDependenceStructure,
    MultiCellMultiplicityDecision,
    MultiCellMultiplicityRole,
    MultiCellMultiplicitySpec,
    MultiplicityAdjustmentKind,
    build_multicell_multiplicity_readiness_matrix,
    compute_bonferroni_alpha,
    compute_independent_familywise_false_positive_risk,
    validate_multicell_multiplicity,
)


def _spec(**kwargs) -> MultiCellMultiplicitySpec:
    defaults = dict(
        use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
        num_cells=3,
        nominal_alpha=0.10,
        dependence_structure=MultiCellDependenceStructure.INDEPENDENT_APPROXIMATION,
    )
    defaults.update(kwargs)
    return MultiCellMultiplicitySpec(**defaults)


def test_per_cell_marginal_with_estimands() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
            has_cell_level_estimand_contracts=True,
        )
    )
    assert result.decision == (
        MultiCellMultiplicityDecision.MULTICELL_PER_CELL_MARGINAL_ALLOWED_AS_SEPARATE_READOUT
    )
    assert result.is_per_cell_marginal_only


def test_per_cell_marginal_missing_estimands_blocked() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
            has_cell_level_estimand_contracts=False,
        )
    )
    assert result.is_blocked


def test_multiple_cell_family_requires_adjustment() -> None:
    result = validate_multicell_multiplicity(
        _spec(use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY)
    )
    assert result.role == MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED
    assert result.is_adjustment_required


def test_bonferroni_does_not_authorize_global() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY,
            adjustment_kind=MultiplicityAdjustmentKind.BONFERRONI,
        )
    )
    assert result.governance_flags["global_multicell_decision_allowed"] is False


def test_holm_does_not_authorize_global() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY,
            adjustment_kind=MultiplicityAdjustmentKind.HOLM,
        )
    )
    assert result.governance_flags["global_multicell_decision_allowed"] is False


def test_shared_control_unresolved() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY,
            dependence_structure=MultiCellDependenceStructure.SHARED_CONTROL,
        )
    )
    assert result.role == MultiCellMultiplicityRole.SHARED_CONTROL_DEPENDENCE_UNRESOLVED
    assert result.is_shared_control_unresolved


def test_shared_control_dependence_no_joint_null_deferred() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY,
            dependence_structure=MultiCellDependenceStructure.SHARED_CONTROL,
            has_shared_control_dependence_model=True,
        )
    )
    assert result.decision == MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED


def test_global_decision_blocked() -> None:
    result = validate_multicell_multiplicity(
        _spec(use_case=MultiCellDecisionUseCase.GLOBAL_DECISION)
    )
    assert result.decision == MultiCellMultiplicityDecision.MULTICELL_GLOBAL_DECISION_BLOCKED


def test_winner_selection_blocked() -> None:
    result = validate_multicell_multiplicity(
        _spec(use_case=MultiCellDecisionUseCase.WINNER_SELECTION)
    )
    assert result.decision == MultiCellMultiplicityDecision.MULTICELL_WINNER_SELECTION_BLOCKED


def test_pooled_effect_blocked() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.POOLED_EFFECT,
            has_pooled_estimand_contract=True,
        )
    )
    assert result.decision == MultiCellMultiplicityDecision.MULTICELL_POOLED_EFFECT_BLOCKED


def test_pooled_effect_missing_estimand() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.POOLED_EFFECT,
            has_pooled_estimand_contract=False,
        )
    )
    assert result.is_blocked


def test_unknown_dependence_deferred() -> None:
    result = validate_multicell_multiplicity(
        _spec(dependence_structure=MultiCellDependenceStructure.UNKNOWN)
    )
    assert result.decision == MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED


def test_invalid_num_cells() -> None:
    result = validate_multicell_multiplicity(_spec(num_cells=0))
    assert result.is_blocked


@pytest.mark.parametrize("alpha", [-0.1, 0.0, 1.0, 1.5])
def test_invalid_alpha_blocked(alpha: float) -> None:
    result = validate_multicell_multiplicity(_spec(nominal_alpha=alpha))
    assert result.is_blocked


def test_fwer_formula() -> None:
    fwer = compute_independent_familywise_false_positive_risk(0.10, 3)
    assert math.isclose(fwer, 0.271)


def test_bonferroni_formula() -> None:
    bonf = compute_bonferroni_alpha(0.10, 3)
    assert math.isclose(bonf, 1.0 / 30.0)


@pytest.mark.parametrize(
    "field",
    [
        "requested_trustreport_authorization",
        "requested_calibration_signal",
        "requested_mmm_ingestion",
        "requested_llm_decisioning",
    ],
)
def test_overclaim_blocked(field: str) -> None:
    result = validate_multicell_multiplicity(_spec(**{field: True}))
    assert result.is_blocked


def test_production_live_scheduler_budget_blocked() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            requested_production_decisioning=True,
            requested_live_api=True,
            requested_scheduler=True,
            requested_budget_optimization=True,
        )
    )
    assert result.is_blocked


def test_governance_flags_false() -> None:
    result = validate_multicell_multiplicity(
        _spec(
            use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
            has_cell_level_estimand_contracts=True,
        )
    )
    assert all(v is False for v in result.governance_flags.values())


def test_readiness_matrix() -> None:
    matrix = build_multicell_multiplicity_readiness_matrix()
    assert len(matrix) >= len(MultiCellDecisionUseCase)
