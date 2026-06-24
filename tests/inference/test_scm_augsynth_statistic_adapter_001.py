"""Tests for scm_augsynth_statistic_adapter inference module."""

from __future__ import annotations

import math

from panel_exp.inference.scm_augsynth_statistic_adapter import (
    AdapterCompatibilityStatus,
    AdapterStatisticKind,
    AdapterUsageBoundary,
    StatisticAdapterFamily,
    build_adapted_statistic_set_from_dict,
    build_augsynth_adapter_statistic_set_from_randomization_result,
    build_scm_style_adapter_statistic_set_from_calibration_result,
    build_statistic_adapter_readiness_matrix,
    compare_observed_and_pseudo_statistic_contract,
    validate_adapted_statistic_set,
)

_PSEUDO = {f"a{i}": 0.03 * i for i in range(1, 26)}


def _set(
    *,
    family: str = "scm",
    kind: str = "point_effect",
    observed: float | None = 0.12,
    pseudo: dict[str, float] | None = None,
    effect_direction: str = "two_sided",
    studentization_scale_id: str | None = None,
) -> object:
    return build_adapted_statistic_set_from_dict(
        {
            "observed_statistic": observed,
            "pseudo_statistic_by_assignment": pseudo if pseudo is not None else dict(_PSEUDO),
            "config": {
                "estimand_id": "treated_set_att",
                "outcome_scale": "absolute_level",
                "pre_period_id": "pre_main",
                "post_period_id": "post_main",
                "donor_eligibility_rule_id": "eligible_donors_v1",
                "estimator_config_id": "default_v1",
                "treated_set_aggregation_rule_id": "mean_across_treated",
                "effect_direction": effect_direction,
                "missing_data_policy_id": "complete_case_v1",
                "statistic_kind": kind,
                "studentization_scale_id": studentization_scale_id,
            },
            "provenance": {
                "estimator_family": family,
                "estimator_version": "v1",
                "adapter_version": "1.0.0",
                "config_hash": "hash",
                "source_artifact_id": "TEST",
                "computation_mode": "statistic_first",
            },
        }
    )


def test_scm_style_calibration_harness_only() -> None:
    s = _set(family="scm_style_calibration", kind="scm_style_effect")
    r = compare_observed_and_pseudo_statistic_contract(s)
    assert r.is_calibration_harness_only
    assert r.usage_boundary == AdapterUsageBoundary.CALIBRATION_HARNESS_ONLY


def test_scm_randomization_candidate_only() -> None:
    s = _set(family="scm", kind="point_effect")
    r = compare_observed_and_pseudo_statistic_contract(s)
    assert r.is_randomization_candidate_compatible


def test_augsynth_point_relative_studentized() -> None:
    for kind, scale in (
        ("point_effect", None),
        ("relative_effect", None),
        ("studentized_effect", "pre_period_residual_scale"),
    ):
        s = _set(family="augsynth_cvxpy", kind=kind, studentization_scale_id=scale, observed=0.4)
        r = compare_observed_and_pseudo_statistic_contract(s)
        assert r.is_randomization_candidate_compatible


def test_config_match_accepted() -> None:
    a = _set(family="scm", kind="point_effect")
    b = _set(family="scm", kind="point_effect")
    assert not compare_observed_and_pseudo_statistic_contract(a, b).is_blocked


def test_cross_family_diagnostic() -> None:
    scm = _set(family="scm", kind="point_effect")
    aug = _set(family="augsynth_cvxpy", kind="point_effect", observed=0.4)
    r = compare_observed_and_pseudo_statistic_contract(scm, aug)
    assert r.is_diagnostic_only


def test_missing_observed_blocked() -> None:
    s = _set(family="scm", kind="point_effect", observed=None)
    assert (
        compare_observed_and_pseudo_statistic_contract(s).status
        == AdapterCompatibilityStatus.MISSING_OBSERVED_STATISTIC
    )


def test_missing_pseudo_blocked() -> None:
    s = _set(family="scm", kind="point_effect", pseudo={})
    assert compare_observed_and_pseudo_statistic_contract(s).is_blocked


def test_non_finite_observed_blocked() -> None:
    s = _set(family="scm", kind="point_effect", observed=float("nan"))
    assert (
        compare_observed_and_pseudo_statistic_contract(s).status
        == AdapterCompatibilityStatus.NON_NUMERIC_STATISTIC
    )


def test_non_finite_pseudo_blocked() -> None:
    bad = dict(_PSEUDO)
    bad["a1"] = math.inf
    s = _set(family="scm", kind="point_effect", pseudo=bad)
    assert compare_observed_and_pseudo_statistic_contract(s).is_blocked


def test_too_few_pseudo_blocked() -> None:
    s = _set(family="scm", kind="point_effect", pseudo={"a1": 0.1})
    assert (
        compare_observed_and_pseudo_statistic_contract(s).status
        == AdapterCompatibilityStatus.INSUFFICIENT_PSEUDO_STATISTICS
    )


def test_unsupported_family_blocked() -> None:
    s = _set(family="unknown", kind="point_effect")
    assert (
        compare_observed_and_pseudo_statistic_contract(s).status
        == AdapterCompatibilityStatus.UNSUPPORTED_FAMILY
    )


def test_unknown_kind_blocked() -> None:
    s = _set(family="scm", kind="unknown")
    assert compare_observed_and_pseudo_statistic_contract(s).is_blocked


def test_missing_provenance_blocked() -> None:
    s = build_adapted_statistic_set_from_dict(
        {
            "observed_statistic": 0.1,
            "pseudo_statistic_by_assignment": dict(_PSEUDO),
            "config": {
                "estimand_id": "x",
                "outcome_scale": "y",
                "pre_period_id": "pre",
                "post_period_id": "post",
                "donor_eligibility_rule_id": "d",
                "estimator_config_id": "e",
                "treated_set_aggregation_rule_id": "t",
                "effect_direction": "two_sided",
                "missing_data_policy_id": "m",
                "statistic_kind": "point_effect",
            },
            "provenance": {
                "estimator_family": "scm",
                "estimator_version": "",
                "adapter_version": "",
                "config_hash": "",
                "source_artifact_id": "",
                "computation_mode": "",
            },
        }
    )
    assert (
        compare_observed_and_pseudo_statistic_contract(s).status
        == AdapterCompatibilityStatus.PROVENANCE_MISSING
    )


def test_estimand_mismatch() -> None:
    a = _set(family="scm", kind="point_effect")
    b = _set(family="scm", kind="point_effect")
    b2 = build_adapted_statistic_set_from_dict(
        {
            "observed_statistic": b.observed_statistic,
            "pseudo_statistic_by_assignment": dict(b.pseudo_statistic_by_assignment),
            "config": {
                **{
                    "estimand_id": "other",
                    "outcome_scale": "absolute_level",
                    "pre_period_id": "pre_main",
                    "post_period_id": "post_main",
                    "donor_eligibility_rule_id": "eligible_donors_v1",
                    "estimator_config_id": "default_v1",
                    "treated_set_aggregation_rule_id": "mean_across_treated",
                    "effect_direction": "two_sided",
                    "missing_data_policy_id": "complete_case_v1",
                    "statistic_kind": "point_effect",
                }
            },
            "provenance": {
                "estimator_family": "scm",
                "estimator_version": "v1",
                "adapter_version": "1.0.0",
                "config_hash": "hash",
                "source_artifact_id": "TEST",
                "computation_mode": "statistic_first",
            },
        }
    )
    assert (
        compare_observed_and_pseudo_statistic_contract(a, b2).status
        == AdapterCompatibilityStatus.ESTIMAND_MISMATCH
    )


def test_studentization_scale_mismatch() -> None:
    a = _set(
        family="augsynth_cvxpy",
        kind="studentized_effect",
        studentization_scale_id="scale_a",
    )
    b = _set(
        family="augsynth_cvxpy",
        kind="studentized_effect",
        studentization_scale_id="scale_b",
    )
    assert (
        compare_observed_and_pseudo_statistic_contract(a, b).status
        == AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH
    )


def test_invalid_effect_direction() -> None:
    s = _set(family="scm", kind="point_effect", effect_direction="bad")
    ok, reasons = validate_adapted_statistic_set(s)
    assert not ok
    assert compare_observed_and_pseudo_statistic_contract(s).is_blocked


def test_readiness_matrix_rows() -> None:
    rows = build_statistic_adapter_readiness_matrix()
    ids = {r["row_id"] for r in rows}
    assert "scm_style_calibration_harness" in ids
    assert "scm_treated_set_randomization_candidate" in ids
    assert "augsynth_point_randomization" in ids


def test_build_from_calibration_dict() -> None:
    s = build_scm_style_adapter_statistic_set_from_calibration_result(
        {"observed_statistic": 0.1, "spec": {"statistic_mode": "scm_style_effect"}}
    )
    assert s.provenance.estimator_family == StatisticAdapterFamily.SCM_STYLE_CALIBRATION


def test_build_from_augsynth_contract() -> None:
    s = build_augsynth_adapter_statistic_set_from_randomization_result(
        {"observed_statistic": 0.4, "pseudo_statistic_by_assignment": dict(_PSEUDO)},
        contract={"statistic_kind": "point_effect", "estimand_id": "treated_set_att"},
    )
    assert s.provenance.estimator_family == StatisticAdapterFamily.AUGSYNTH_CVXPY


def test_no_production_authorization() -> None:
    r = compare_observed_and_pseudo_statistic_contract(_set())
    assert r.governance_flags["production_p_value_authorized"] is False
    assert r.governance_flags["trustreport_authorized"] is False
