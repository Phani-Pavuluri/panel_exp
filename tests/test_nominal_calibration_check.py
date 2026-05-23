"""Nominal calibration smoke checks for aligned recovery interval configs."""

from __future__ import annotations

import pytest

from panel_exp.validation.calibration_report import MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
from panel_exp.validation.nominal_calibration import (
    NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS,
    is_nominal_calibration_eligible_config,
    run_nominal_calibration_check,
)
from panel_exp.validation.recovery_intervals import (
    INTERVAL_ESTIMAND_CUMULATIVE_ATT,
    INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
    POINT_ESTIMAND,
)


@pytest.mark.parametrize(
    "config_name,expected",
    [
        ("SCM_UnitJackKnife", True),
        ("TBRRidge_Kfold", True),
        ("TBRRidge_BlockResidualBootstrap", True),
        ("DID_Bootstrap", False),
        ("SCM", False),
        ("TBRRidge", False),
    ],
)
def test_config_eligibility_registry(config_name: str, expected: bool):
    assert is_nominal_calibration_eligible_config(config_name) is expected
    assert (config_name in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS) is expected


def test_aligned_config_nominal_check_eligible():
    out = run_nominal_calibration_check(
        "SCM_UnitJackKnife",
        "recovery_null_effect",
        n_simulations=3,
        random_state=0,
    )
    assert out["eligible_for_nominal_calibration"] is True
    assert out["interval_aligned"] is True
    assert out["interval_estimand"] == INTERVAL_ESTIMAND_RELATIVE_ATT_POST
    assert out["point_estimand"] == POINT_ESTIMAND
    assert out["interval_scale"] == "path_period_relative_mean"
    assert any("CI smoke is not production calibration" in w for w in out["warnings"])
    assert any(
        str(MIN_REPLICATIONS_FOR_STABLE_CALIBRATION) in w for w in out["warnings"]
    )


def test_did_bootstrap_not_eligible():
    out = run_nominal_calibration_check(
        "DID_Bootstrap",
        "recovery_null_effect",
        n_simulations=2,
        random_state=1,
    )
    assert out["eligible_for_nominal_calibration"] is False
    assert out["interval_aligned"] is False
    assert out["interval_estimand"] == INTERVAL_ESTIMAND_CUMULATIVE_ATT
    assert any("not eligible" in w.lower() or "not aligned" in w.lower() for w in out["warnings"])


def test_point_estimate_config_not_eligible():
    out = run_nominal_calibration_check(
        "SCM",
        "recovery_null_effect",
        n_simulations=2,
        random_state=2,
    )
    assert out["eligible_for_nominal_calibration"] is False
    assert out["interval_estimand"] == "unavailable"
    assert any("not eligible" in w.lower() for w in out["warnings"])


def test_metrics_bounded_when_finite():
    out = run_nominal_calibration_check(
        "TBRRidge_Kfold",
        "recovery_null_effect",
        n_simulations=2,
        random_state=3,
    )
    for key in ("coverage", "false_positive_rate", "power"):
        val = out[key]
        if val == val:
            assert 0.0 <= val <= 1.0


def test_small_n_warning_when_below_production_threshold():
    out = run_nominal_calibration_check(
        "SCM_UnitJackKnife",
        "recovery_null_effect",
        n_simulations=5,
        random_state=4,
    )
    assert out["n_simulations"] < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
    assert any("small simulation count" in w for w in out["warnings"])


def test_output_includes_estimand_metadata_keys():
    out = run_nominal_calibration_check(
        "TBRRidge_BlockResidualBootstrap",
        "recovery_positive_effect",
        n_simulations=2,
        random_state=5,
    )
    for key in (
        "point_estimand",
        "interval_estimand",
        "interval_scale",
        "scored_target_estimand",
        "coverage_status",
        "false_positive_rate_status",
    ):
        assert key in out
