"""Tests for STRATIFIED_POOLED_ESTIMAND_CONTRACT_001."""

from __future__ import annotations

import math

import pytest

from panel_exp.inference.stratified_pooled_estimand import (
    HeterogeneityPolicy,
    PooledEstimandDecision,
    PooledEstimandGeometry,
    PooledEstimandRole,
    PooledEstimandUseCase,
    PoolingWeightKind,
    StratifiedPooledEstimandSpec,
    StratumEstimandSpec,
    build_stratified_pooled_estimand_readiness_matrix,
    normalize_pooling_weights,
    validate_stratified_pooled_estimand,
)


def _stratum(stratum_id: str, **kwargs) -> StratumEstimandSpec:
    defaults = dict(
        estimand_id="ate",
        metric="revenue",
        effect_scale="absolute",
        target_population="geo",
        time_window="post",
        is_compatible=True,
    )
    defaults.update(kwargs)
    return StratumEstimandSpec(stratum_id=stratum_id, **defaults)


def _spec(**kwargs) -> StratifiedPooledEstimandSpec:
    s1 = _stratum("s1")
    s2 = _stratum("s2")
    defaults = dict(
        use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT,
        geometry=PooledEstimandGeometry.MULTI_STRATUM,
        strata=(s1, s2),
        weighting_kind=PoolingWeightKind.NONE,
        has_common_metric=True,
        has_common_effect_scale=True,
        has_common_time_window=True,
        has_common_target_population=True,
    )
    defaults.update(kwargs)
    return StratifiedPooledEstimandSpec(**defaults)


def _contract_spec(**kwargs) -> StratifiedPooledEstimandSpec:
    defaults = dict(
        use_case=PooledEstimandUseCase.STRATIFIED_AGGREGATE,
        geometry=PooledEstimandGeometry.MULTI_STRATUM,
        weighting_kind=PoolingWeightKind.PRE_SPECIFIED_POPULATION,
        weights_by_stratum={"s1": 0.6, "s2": 0.4},
        weights_pre_specified=True,
        heterogeneity_policy=HeterogeneityPolicy.ALLOW_WITH_PRE_SPECIFIED_POOLING,
        heterogeneity_assessed=True,
        material_heterogeneity_detected=False,
        has_valid_pooled_estimand_statement=True,
        has_valid_inference_for_pooling=True,
        has_multiplicity_adjustment=True,
        has_shared_control_dependence_resolution=True,
    )
    defaults.update(kwargs)
    return _spec(**defaults)


def test_stratum_level_readout_allowed_only() -> None:
    result = validate_stratified_pooled_estimand(
        _spec(use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT, strata=(_stratum("s1"),))
    )
    assert result.decision == PooledEstimandDecision.STRATUM_LEVEL_READOUT_ALLOWED
    assert result.is_stratum_level_only
    assert "stratum-level readout only" in result.warnings[0].lower()


def test_multiple_stratum_readouts_not_pooled() -> None:
    result = validate_stratified_pooled_estimand(
        _spec(use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT)
    )
    assert result.role == PooledEstimandRole.STRATUM_LEVEL_ONLY
    assert not result.is_contract_candidate


def test_contract_candidate_not_production() -> None:
    result = validate_stratified_pooled_estimand(_contract_spec())
    assert result.decision == PooledEstimandDecision.POOLED_ESTIMAND_CONTRACT_CANDIDATE
    assert result.is_contract_candidate
    assert result.governance_flags["pooled_effect_authorized"] is False


def test_diagnostic_only_without_pooling_inference() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(has_valid_inference_for_pooling=False)
    )
    assert result.decision == PooledEstimandDecision.STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY
    assert result.is_diagnostic_only


def test_heterogeneity_not_assessed_review_required() -> None:
    result = validate_stratified_pooled_estimand(_contract_spec(heterogeneity_assessed=False))
    assert result.decision == PooledEstimandDecision.HETEROGENEITY_REVIEW_REQUIRED
    assert "heterogeneity_assessment" in result.required_next_evidence


def test_material_heterogeneity_block_policy() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(
            material_heterogeneity_detected=True,
            heterogeneity_policy=HeterogeneityPolicy.BLOCK_IF_MATERIAL_HETEROGENEITY,
        )
    )
    assert result.is_blocked
    assert "material_heterogeneity_blocks_pooling" in result.blocked_reasons


def test_material_heterogeneity_report_separately() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(
            material_heterogeneity_detected=True,
            heterogeneity_policy=HeterogeneityPolicy.REPORT_SEPARATELY,
        )
    )
    assert result.is_diagnostic_only
    assert not result.is_contract_candidate


@pytest.mark.parametrize(
    "field,kwargs",
    [
        ("metric", {"strata": (_stratum("s1"), _stratum("s2", metric="orders")), "has_common_metric": False}),
        ("effect_scale", {"strata": (_stratum("s1"), _stratum("s2", effect_scale="relative")), "has_common_effect_scale": False}),
        ("time_window", {"strata": (_stratum("s1"), _stratum("s2", time_window="long_run")), "has_common_time_window": False}),
        ("target_population", {"strata": (_stratum("s1"), _stratum("s2", target_population="national")), "has_common_target_population": False}),
    ],
)
def test_incompatible_strata_blocked(field: str, kwargs: dict) -> None:
    result = validate_stratified_pooled_estimand(_contract_spec(**kwargs))
    assert result.is_blocked


def test_missing_pooled_estimand_statement_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(has_valid_pooled_estimand_statement=False)
    )
    assert result.is_blocked


def test_missing_weights_blocked() -> None:
    result = validate_stratified_pooled_estimand(_contract_spec(weights_by_stratum=None))
    assert result.is_blocked


def test_weight_id_mismatch_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weights_by_stratum={"s1": 1.0, "s3": 0.0})
    )
    assert result.is_blocked


def test_negative_weight_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weights_by_stratum={"s1": -0.5, "s2": 1.5})
    )
    assert result.is_blocked


def test_zero_total_weights_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weights_by_stratum={"s1": 0.0, "s2": 0.0})
    )
    assert result.is_blocked


def test_non_finite_weight_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weights_by_stratum={"s1": float("inf"), "s2": 0.0})
    )
    assert result.is_blocked


def test_post_hoc_effect_size_weights_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weighting_kind=PoolingWeightKind.POST_HOC_EFFECT_SIZE)
    )
    assert result.is_blocked


def test_winner_selected_weights_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(weighting_kind=PoolingWeightKind.WINNER_SELECTED)
    )
    assert result.is_blocked


def test_pooled_multicell_effect_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _spec(
            use_case=PooledEstimandUseCase.POOLED_MULTICELL_EFFECT,
            geometry=PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
            weighting_kind=PoolingWeightKind.PRE_SPECIFIED_POPULATION,
            weights_by_stratum={"s1": 0.5, "s2": 0.5},
        )
    )
    assert result.decision == PooledEstimandDecision.MULTICELL_POOLED_EFFECT_BLOCKED


def test_shared_control_unresolved_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _contract_spec(
            geometry=PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
            has_shared_control_dependence_resolution=False,
            has_multiplicity_adjustment=False,
        )
    )
    assert result.role == PooledEstimandRole.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED


def test_global_summary_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _spec(use_case=PooledEstimandUseCase.GLOBAL_SUMMARY)
    )
    assert result.decision == PooledEstimandDecision.GLOBAL_SUMMARY_BLOCKED


def test_winner_selected_summary_blocked() -> None:
    result = validate_stratified_pooled_estimand(
        _spec(use_case=PooledEstimandUseCase.WINNER_SELECTED_SUMMARY)
    )
    assert result.decision == PooledEstimandDecision.WINNER_SELECTED_SUMMARY_BLOCKED


@pytest.mark.parametrize(
    "flag",
    [
        "requested_trustreport_authorization",
        "requested_calibration_signal",
        "requested_mmm_ingestion",
        "requested_llm_decisioning",
        "requested_production_decisioning",
        "requested_live_api",
        "requested_scheduler",
        "requested_budget_optimization",
        "requested_pooled_effect_authorization",
    ],
)
def test_platform_requests_blocked(flag: str) -> None:
    result = validate_stratified_pooled_estimand(_spec(**{flag: True}))
    assert result.is_blocked


def test_normalize_pooling_weights_sum_to_one() -> None:
    normalized = normalize_pooling_weights({"s1": 3.0, "s2": 1.0})
    assert math.isclose(sum(normalized.values()), 1.0, rel_tol=0, abs_tol=1e-9)


def test_readiness_matrix_covers_use_cases() -> None:
    matrix = build_stratified_pooled_estimand_readiness_matrix()
    use_cases = {row["use_case"] for row in matrix}
    assert use_cases == {uc.value for uc in PooledEstimandUseCase}
