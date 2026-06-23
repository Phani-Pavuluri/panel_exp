"""Tests for studentized_randomization_calibration inference module."""

from __future__ import annotations

from panel_exp.inference.studentized_randomization_calibration import (
    CalibrationAssignmentFamily,
    CalibrationStatisticMode,
    CalibrationVerdict,
    NullDGPKind,
    StudentizedNullSimulationSpec,
    build_default_studentized_null_calibration_grid,
    run_studentized_null_calibration,
    run_studentized_null_calibration_grid,
    summarize_studentized_null_calibration_grid,
    validate_studentized_null_simulation_spec,
)


def _spec(**kwargs) -> StudentizedNullSimulationSpec:
    defaults = dict(
        dgp_kind=NullDGPKind.IID_NORMAL,
        assignment_family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
        statistic_mode=CalibrationStatisticMode.STUDENTIZED,
        num_units=12,
        num_treated=3,
        num_pre_periods=4,
        num_post_periods=2,
        num_replications=30,
        num_pseudo_assignments=25,
        seed=11,
        min_replications=20,
        min_pseudo_assignments=20,
    )
    defaults.update(kwargs)
    return StudentizedNullSimulationSpec(**defaults)


def test_valid_spec_passes() -> None:
    ok, reasons = validate_studentized_null_simulation_spec(_spec())
    assert ok
    assert not reasons


def test_invalid_unit_count_blocked() -> None:
    ok, reasons = validate_studentized_null_simulation_spec(_spec(num_units=2))
    assert not ok
    assert reasons


def test_invalid_treated_count_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(_spec(num_treated=0))
    assert not ok


def test_treated_ge_units_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(_spec(num_treated=12))
    assert not ok


def test_invalid_periods_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(_spec(num_pre_periods=1))
    assert not ok


def test_invalid_alpha_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(_spec(alpha_levels=(0.0,)))
    assert not ok


def test_too_few_replications_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(
        _spec(num_replications=5, min_replications=100)
    )
    assert not ok


def test_too_few_pseudo_assignments_blocked() -> None:
    ok, _ = validate_studentized_null_simulation_spec(
        _spec(num_pseudo_assignments=5, min_pseudo_assignments=20)
    )
    assert not ok


def test_iid_simulation_runs() -> None:
    result = run_studentized_null_calibration(_spec(dgp_kind=NullDGPKind.IID_NORMAL))
    assert len(result.replication_results) >= 20
    assert result.verdict != CalibrationVerdict.INVALID_CALIBRATION_SPEC


def test_unit_fixed_effect_runs() -> None:
    result = run_studentized_null_calibration(_spec(dgp_kind=NullDGPKind.UNIT_FIXED_EFFECT))
    assert len(result.replication_results) >= 20


def test_unit_time_fixed_effect_runs() -> None:
    result = run_studentized_null_calibration(
        _spec(dgp_kind=NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT)
    )
    assert len(result.replication_results) >= 20


def test_heteroskedastic_runs() -> None:
    result = run_studentized_null_calibration(_spec(dgp_kind=NullDGPKind.HETEROSKEDASTIC))
    assert len(result.replication_results) >= 20


def test_complete_randomized_covered() -> None:
    result = run_studentized_null_calibration(
        _spec(assignment_family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET)
    )
    assert len(result.replication_results) >= 20


def test_matched_pair_covered() -> None:
    result = run_studentized_null_calibration(
        _spec(
            assignment_family=CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            num_units=12,
            num_treated=6,
        )
    )
    assert len(result.replication_results) >= 20


def test_stratified_covered() -> None:
    result = run_studentized_null_calibration(
        _spec(
            assignment_family=CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
            num_units=16,
            num_treated=4,
        )
    )
    assert len(result.replication_results) >= 20


def test_studentized_mode() -> None:
    result = run_studentized_null_calibration(
        _spec(statistic_mode=CalibrationStatisticMode.STUDENTIZED)
    )
    assert result.replication_results


def test_unstudentized_mode() -> None:
    result = run_studentized_null_calibration(
        _spec(statistic_mode=CalibrationStatisticMode.UNSTUDENTIZED)
    )
    assert result.replication_results


def test_tail_fraction_bounded() -> None:
    result = run_studentized_null_calibration(_spec())
    for rep in result.replication_results:
        assert 0.0 <= rep.empirical_tail_fraction <= 1.0


def test_empirical_type_i_bounded() -> None:
    result = run_studentized_null_calibration(_spec())
    for val in result.empirical_type_i_by_alpha.values():
        assert 0.0 <= val <= 1.0


def test_type_i_excess_computed() -> None:
    result = run_studentized_null_calibration(_spec())
    for alpha, val in result.empirical_type_i_by_alpha.items():
        assert result.type_i_excess_by_alpha[alpha] == val - float(alpha)


def test_quantiles_computed() -> None:
    result = run_studentized_null_calibration(_spec())
    assert "q50" in result.tail_fraction_quantiles


def test_seed_reproducibility() -> None:
    r1 = run_studentized_null_calibration(_spec(seed=5))
    r2 = run_studentized_null_calibration(_spec(seed=5))
    assert (
        r1.replication_results[0].empirical_tail_fraction
        == r2.replication_results[0].empirical_tail_fraction
    )


def test_different_seed_changes_path() -> None:
    r1 = run_studentized_null_calibration(_spec(seed=5))
    r2 = run_studentized_null_calibration(_spec(seed=6))
    assert (
        r1.replication_results[0].empirical_tail_fraction
        != r2.replication_results[0].empirical_tail_fraction
    )


def test_verdict_assigned() -> None:
    result = run_studentized_null_calibration(_spec())
    assert result.verdict in CalibrationVerdict


def test_grid_summary_valid() -> None:
    grid = build_default_studentized_null_calibration_grid()
    small = tuple(
        StudentizedNullSimulationSpec(
            dgp_kind=s.dgp_kind,
            assignment_family=s.assignment_family,
            statistic_mode=s.statistic_mode,
            num_units=s.num_units,
            num_treated=s.num_treated,
            num_pre_periods=s.num_pre_periods,
            num_post_periods=s.num_post_periods,
            num_replications=25,
            num_pseudo_assignments=25,
            seed=s.seed,
            min_replications=20,
            min_pseudo_assignments=20,
        )
        for s in grid[:3]
    )
    results = run_studentized_null_calibration_grid(small)
    summary = summarize_studentized_null_calibration_grid(results)
    assert summary["grid_result_count"] == 3


def test_no_production_p_value_authorization() -> None:
    result = run_studentized_null_calibration(_spec())
    assert result.governance_flags["production_p_value_authorized"] is False


def test_no_causal_ci_authorization() -> None:
    result = run_studentized_null_calibration(_spec())
    assert result.governance_flags["causal_confidence_interval_authorized"] is False


def test_no_trustreport_authorization() -> None:
    result = run_studentized_null_calibration(_spec())
    assert result.governance_flags["trustreport_authorized"] is False


def test_no_calibration_signal() -> None:
    result = run_studentized_null_calibration(_spec())
    assert result.governance_flags["calibration_signal_allowed"] is False


def test_no_mmm_llm_production_flags() -> None:
    result = run_studentized_null_calibration(_spec())
    for key in (
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    ):
        assert result.governance_flags[key] is False
