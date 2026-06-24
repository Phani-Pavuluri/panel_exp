"""Tests for ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001."""

from __future__ import annotations

from panel_exp.inference.estimator_design_inference_suitability import (
    DesignFamily,
    EstimatorFamily,
    FORBIDDEN_OUTPUTS,
    InferenceFamily,
    RECOMMENDED_NEXT_ARTIFACTS,
    SuitabilityStatus,
    build_estimator_design_inference_suitability_matrix,
    filter_suitability_rows,
    summarize_estimator_design_inference_suitability_matrix,
    validate_estimator_design_inference_suitability_matrix,
)

_AUTH_FLAGS = (
    "production_p_value_authorized",
    "causal_confidence_interval_authorized",
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


def test_matrix_builds() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    assert len(rows) >= 35


def test_row_ids_unique() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    ids = [row.row_id for row in rows]
    assert len(ids) == len(set(ids))


def test_all_estimator_families_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    present = {row.estimator_family for row in rows}
    assert present == set(EstimatorFamily)


def test_all_design_families_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    present = {row.design_family for row in rows}
    assert present == set(DesignFamily)


def test_all_inference_families_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    present = {row.inference_family for row in rows}
    assert present == set(InferenceFamily)


def test_scm_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    ids = {row.row_id for row in rows}
    assert "scm_single_treated_unit_jackknife" in ids
    assert "scm_multi_treated_treated_set_placebo" in ids
    assert "scm_multi_treated_studentized_placebo" in ids
    assert "scm_leave_one_treated_out" in ids


def test_augsynth_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    scm_rows = filter_suitability_rows(rows, estimator_family=EstimatorFamily.AUGSYNTH_CVXPY)
    assert scm_rows
    assert any(r.inference_family == InferenceFamily.DESIGN_BASED_RANDOMIZATION for r in scm_rows)
    assert any(r.suitability_status == SuitabilityStatus.RETIRE_OR_REPLACE for r in scm_rows)


def test_did_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    did_rows = filter_suitability_rows(rows, estimator_family=EstimatorFamily.DID)
    assert any(r.inference_family == InferenceFamily.DID_BOOTSTRAP for r in did_rows)
    assert any(r.inference_family == InferenceFamily.PERMUTATION for r in did_rows)


def test_tbrridge_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    tbr_rows = filter_suitability_rows(rows, estimator_family=EstimatorFamily.TBRRIDGE)
    assert any(r.inference_family == InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP for r in tbr_rows)
    assert any(r.inference_family == InferenceFamily.KFOLD_CROSS_FIT for r in tbr_rows)
    assert any(
        r.inference_family == InferenceFamily.UNIT_JACKKNIFE
        and r.suitability_status == SuitabilityStatus.KNOWN_FAILURE_BLOCKED
        for r in tbr_rows
    )


def test_tbr_bayesian_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    assert any(
        row.estimator_family == EstimatorFamily.TBR
        and row.suitability_status == SuitabilityStatus.GEOMETRY_MISMATCH_BLOCKED
        for row in rows
    )
    bayes = filter_suitability_rows(rows, estimator_family=EstimatorFamily.BAYESIAN_TBR)
    assert any(r.inference_family == InferenceFamily.BAYESIAN_POSTERIOR_INTERVAL for r in bayes)
    assert any(r.inference_family == InferenceFamily.BAYESIAN_POSTERIOR_PREDICTIVE_CHECK for r in bayes)


def test_synthetic_did_trop_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    assert filter_suitability_rows(rows, estimator_family=EstimatorFamily.SYNTHETIC_DID)
    assert filter_suitability_rows(rows, estimator_family=EstimatorFamily.TROP)


def test_multicell_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    assert any(
        row.design_family == DesignFamily.MULTICELL_SHARED_CONTROL
        and row.inference_family == InferenceFamily.MAX_T_MULTIPLICITY
        for row in rows
    )
    assert any(row.suitability_status == SuitabilityStatus.BLOCKED for row in rows)


def test_stratified_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    strat = filter_suitability_rows(rows, design_family=DesignFamily.STRATIFIED)
    assert len(strat) >= 2


def test_unknown_assignment_blocked() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    blocked = filter_suitability_rows(
        rows,
        design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
        suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
    )
    assert len(blocked) >= 3


def test_falsification_only_rows_present() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    ids = {row.row_id for row in rows}
    assert "fixed_deterministic_placebo_falsification" in ids
    assert "greedy_matched_market_placebo_falsification" in ids
    assert "kernel_thinning_placebo_falsification" in ids


def test_every_row_has_evidence_or_blocked_reason() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    for row in rows:
        assert row.required_evidence or row.known_failure_modes


def test_every_row_has_forbidden_outputs() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    for row in rows:
        assert row.forbidden_outputs == FORBIDDEN_OUTPUTS


def test_summary_counts() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    assert summary["estimator_family_counts"]
    assert summary["design_family_counts"]
    assert summary["inference_family_counts"]
    assert summary["suitability_status_counts"]


def test_placebo_not_only_inference_layer() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    assert summary["placebo_is_only_inference_layer"] is False
    assert summary["downstream_work_paused"] is True


def test_recommended_next_artifacts() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    for artifact in RECOMMENDED_NEXT_ARTIFACTS:
        assert artifact in summary["recommended_next_artifacts"]


def test_no_downstream_authorization() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_validate_matrix_clean() -> None:
    rows = build_estimator_design_inference_suitability_matrix()
    validation = validate_estimator_design_inference_suitability_matrix(rows)
    assert validation["valid"]
    assert validation["issues"] == []
