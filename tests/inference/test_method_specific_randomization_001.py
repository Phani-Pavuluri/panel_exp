"""Tests for METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001."""

from __future__ import annotations

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.method_specific_randomization import (
    DCM_ADAPTER_NOTE,
    LOTO_SENSITIVITY_NOTE,
    MULTICELL_GLOBAL_NOTE,
    MethodFamily,
    MethodGeometry,
    MethodRandomizationValidationSpec,
    MethodSpecificDecision,
    MethodStatisticKind,
    RandomizationValidationRole,
    build_method_randomization_readiness_matrix,
    classify_method_from_scm_semantics,
    validate_method_randomization_inference,
)

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value


def _candidate(
    family: MethodFamily,
    **kwargs: object,
) -> MethodRandomizationValidationSpec:
    defaults = dict(
        method_family=family,
        statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
        geometry=MethodGeometry.MULTI_TREATED_SET,
        assignment_role=DESIGN,
        num_treated_units=3,
        num_valid_pseudo_assignments=10,
        has_observed_statistic=True,
        has_pseudo_statistics=True,
        uses_same_statistic_observed_and_pseudo=True,
    )
    defaults.update(kwargs)
    return MethodRandomizationValidationSpec(**defaults)


def test_scm_multi_treated_design_based_candidate():
    result = validate_method_randomization_inference(_candidate(MethodFamily.SCM))
    assert result.decision == MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE
    assert result.is_candidate


def test_scm_single_treated_placebo_falsification_only():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.SCM,
            statistic_kind=MethodStatisticKind.PLACEBO_TAIL_FRACTION,
            geometry=MethodGeometry.SINGLE_TREATED,
            assignment_role=DESIGN,
            num_treated_units=1,
            has_observed_statistic=True,
            has_pseudo_statistics=True,
            uses_same_statistic_observed_and_pseudo=True,
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_FALSIFICATION_DIAGNOSTIC_ONLY


def test_scm_missing_pseudo_statistics_blocked():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, has_pseudo_statistics=False)
    )
    assert result.is_blocked


def test_scm_statistic_mismatch_blocked():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, uses_same_statistic_observed_and_pseudo=False)
    )
    assert result.is_blocked


def test_did_design_based_candidate():
    result = validate_method_randomization_inference(_candidate(MethodFamily.DID))
    assert result.decision == MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE


def test_did_bootstrap_only_not_candidate():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.DID,
            statistic_kind=MethodStatisticKind.BOOTSTRAP_INTERVAL,
            geometry=MethodGeometry.MULTI_TREATED_SET,
            assignment_role=DESIGN,
            has_observed_statistic=True,
            uses_same_statistic_observed_and_pseudo=False,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY
    assert not result.is_candidate


def test_augsynth_point_candidate():
    result = validate_method_randomization_inference(_candidate(MethodFamily.AUGSYNTH_CVXPY))
    assert result.decision == MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE


def test_augsynth_jk_diagnostic_only():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.AUGSYNTH_CVXPY,
            statistic_kind=MethodStatisticKind.JACKKNIFE_INTERVAL,
            geometry=MethodGeometry.MULTI_TREATED_SET,
            assignment_role=DESIGN,
            has_observed_statistic=True,
            has_pseudo_statistics=True,
            uses_same_statistic_observed_and_pseudo=True,
            num_valid_pseudo_assignments=5,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY


def test_tbrridge_brb_diagnostic():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.TBRRIDGE,
            statistic_kind=MethodStatisticKind.BOOTSTRAP_INTERVAL,
            geometry=MethodGeometry.MULTI_TREATED_SET,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY


def test_tbrridge_kfold_diagnostic():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.TBRRIDGE,
            statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
            geometry=MethodGeometry.MULTI_TREATED_SET,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY


def test_tbrridge_placebo_diagnostic():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.TBRRIDGE,
            statistic_kind=MethodStatisticKind.PLACEBO_TAIL_FRACTION,
            geometry=MethodGeometry.SINGLE_TREATED,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY


def test_tbrridge_jk_blocked():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.TBRRIDGE, statistic_kind=MethodStatisticKind.JACKKNIFE_INTERVAL)
    )
    assert result.is_blocked


def test_tbr_aggregate_geometry_blocked():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.TBR,
            statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
            geometry=MethodGeometry.AGGREGATE,
        )
    )
    assert "geometry_mismatch" in result.blocked_reasons[0]


def test_bayesian_tbr_research_deferred():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.BAYESIAN_TBR,
            statistic_kind=MethodStatisticKind.POSTERIOR_INTERVAL,
            geometry=MethodGeometry.MULTI_TREATED_SET,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_RESEARCH_DEFERRED


def test_synthetic_did_deferred():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.SYNTHETIC_DID,
            statistic_kind=MethodStatisticKind.UNKNOWN,
            geometry=MethodGeometry.UNKNOWN,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_RESEARCH_DEFERRED


def test_trop_deferred():
    result = validate_method_randomization_inference(
        MethodRandomizationValidationSpec(
            method_family=MethodFamily.TROP,
            statistic_kind=MethodStatisticKind.UNKNOWN,
            geometry=MethodGeometry.UNKNOWN,
        )
    )
    assert result.decision == MethodSpecificDecision.METHOD_RESEARCH_DEFERRED


def test_falsification_role_downgraded():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, assignment_role=FALSIFICATION)
    )
    assert result.role == RandomizationValidationRole.FALSIFICATION_DIAGNOSTIC


def test_blocked_assignment_role():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, assignment_role=AssignmentRole.BLOCKED.value)
    )
    assert result.is_blocked


def test_final_p_value_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_final_p_value=True)
    ).is_blocked


def test_causal_ci_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_causal_interval=True)
    ).is_blocked


def test_trustreport_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_trustreport_authorization=True)
    ).is_blocked


def test_calibration_signal_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_calibration_signal=True)
    ).is_blocked


def test_mmm_ingestion_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_mmm_ingestion=True)
    ).is_blocked


def test_llm_decisioning_blocked():
    assert validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, requested_llm_decisioning=True)
    ).is_blocked


def test_production_live_scheduler_budget_blocked():
    result = validate_method_randomization_inference(
        _candidate(
            MethodFamily.SCM,
            requested_production_decisioning=True,
            requested_live_api=True,
            requested_scheduler=True,
            requested_budget_optimization=True,
        )
    )
    assert result.is_blocked


def test_multicell_global_blocked():
    result = validate_method_randomization_inference(
        _candidate(
            MethodFamily.SCM,
            geometry=MethodGeometry.MULTICELL_SHARED_CONTROL,
            notes=(MULTICELL_GLOBAL_NOTE,),
        )
    )
    assert result.is_blocked


def test_readiness_matrix_contains_expected_families():
    matrix = build_method_randomization_readiness_matrix()
    families = {row["method_family"] for row in matrix}
    assert "scm" in families
    assert "tbrridge" in families
    assert "tbr" in families


def test_classify_from_scm_semantics_bridge():
    result = classify_method_from_scm_semantics(
        method_family=MethodFamily.SCM,
        statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
        geometry=MethodGeometry.MULTI_TREATED_SET,
        scm_semantic_role="design_based_randomization_candidate",
        num_valid_pseudo_assignments=10,
    )
    assert result.is_candidate


def test_loto_sensitivity_only():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, notes=(LOTO_SENSITIVITY_NOTE,))
    )
    assert result.decision == MethodSpecificDecision.METHOD_SENSITIVITY_ONLY


def test_dcm_adapter_blocked():
    result = validate_method_randomization_inference(
        _candidate(MethodFamily.SCM, notes=(DCM_ADAPTER_NOTE,))
    )
    assert result.is_blocked
