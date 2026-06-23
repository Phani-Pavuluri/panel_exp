"""Tests for SCM_PLACEBO_GOVERNED_SEMANTICS_001."""

from __future__ import annotations

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_placebo_semantics import (
    LOTO_AS_PLACEBO_NOTE,
    SCMPlaceboDecision,
    SCMPlaceboSemanticRole,
    SCMPlaceboSemanticsSpec,
    SCMPlaceboUseCase,
    classify_scm_placebo_semantics,
    reject_scm_leave_one_treated_out_as_placebo,
)
from panel_exp.inference.treated_set_placebo import (
    PlaceboDecision,
    PlaceboSemanticRole,
    TreatedSetPlaceboResult,
)
from panel_exp.inference.scm_placebo_semantics import classify_from_treated_set_placebo_result


def test_single_treated_placebo_is_null_monitor_only():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=1,
        )
    )
    assert result.semantic_role == SCMPlaceboSemanticRole.NULL_MONITOR_ONLY
    assert result.decision == SCMPlaceboDecision.SCM_PLACEBO_SINGLE_TREATED_FALSIFICATION_ONLY
    assert result.is_falsification_only
    assert not result.governance_flags["trustreport_authorized"]


def test_single_treated_cannot_emit_final_p_value():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=1,
            requested_as_final_p_value=True,
        )
    )
    assert result.is_blocked
    assert "final production p-value" in result.blocked_reasons[0]


def test_single_treated_cannot_emit_ci_semantics():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=1,
            requested_as_causal_interval=True,
        )
    )
    assert result.is_blocked
    assert "confidence interval" in result.blocked_reasons[0]


def test_treated_set_design_based_maps_to_candidate():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
            num_treated_units=3,
            assignment_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
            has_valid_pseudo_assignments=True,
            num_valid_pseudo_assignments=10,
        )
    )
    assert result.semantic_role == SCMPlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    assert result.is_design_based_candidate


def test_falsification_role_maps_to_falsification_diagnostic():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
            num_treated_units=2,
            assignment_role=AssignmentRole.FALSIFICATION_ONLY.value,
            has_valid_pseudo_assignments=True,
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.semantic_role == SCMPlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    assert result.is_falsification_only


def test_blocked_assignment_role_maps_to_blocked():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
            num_treated_units=2,
            assignment_role=AssignmentRole.BLOCKED.value,
            has_valid_pseudo_assignments=True,
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.is_blocked


def test_leave_one_treated_out_rejected_as_placebo():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
            num_treated_units=3,
            notes=(LOTO_AS_PLACEBO_NOTE,),
        )
    )
    assert result.decision == SCMPlaceboDecision.SCM_LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO


def test_invalid_treated_count_blocked():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=0,
        )
    )
    assert result.is_blocked


def test_trustreport_authorization_blocked():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=1,
            requested_as_trustreport_authorization=True,
        )
    )
    assert result.is_blocked
    assert "TrustReport" in result.blocked_reasons[0]


def test_calibration_signal_blocked():
    result = classify_scm_placebo_semantics(
        SCMPlaceboSemanticsSpec(
            use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
            num_treated_units=1,
            requested_as_calibration_signal=True,
        )
    )
    assert result.is_blocked


def test_production_live_scheduler_budget_blocked():
    for field in (
        "requested_as_production_decisioning",
        "requested_as_live_api",
        "requested_as_scheduler",
        "requested_as_budget_optimization",
    ):
        result = classify_scm_placebo_semantics(
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                **{field: True},
            )
        )
        assert result.is_blocked, field


def test_classify_from_treated_set_placebo_result():
    placebo = TreatedSetPlaceboResult(
        decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        semantic_role=PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        observed_statistic=0.5,
        pseudo_statistics=(0.1, 0.2, 0.3),
        placebo_rank=1,
        empirical_tail_fraction=0.33,
        num_valid_placebo_sets=3,
        minimum_valid_placebo_sets=2,
        assignment_role_counts={"design_based_randomization_candidate": 3},
        blocked_reasons=(),
        warnings=(),
        metadata={},
    )
    result = classify_from_treated_set_placebo_result(num_treated_units=3, placebo_result=placebo)
    assert result.is_design_based_candidate


def test_reject_loto_helper():
    spec = SCMPlaceboSemanticsSpec(
        use_case=SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
        num_treated_units=2,
    )
    result = reject_scm_leave_one_treated_out_as_placebo(spec)
    assert result.decision == SCMPlaceboDecision.SCM_LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO
