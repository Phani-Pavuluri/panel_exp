"""Nominal calibration smoke checks for aligned recovery interval configs."""

from __future__ import annotations

import pytest

from panel_exp.validation.calibration_report import MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
from panel_exp.validation.did_interval_policy import DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
from panel_exp.validation.nominal_calibration import (
    BRB_BOUNDS_INVERTED_RUN001,
    KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001,
    NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS,
    SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES,
    ineligible_reason_for_calibration,
    is_nominal_calibration_eligible_config,
    nominal_calibration_registry_skip_reason,
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
        ("TBRRidge_Kfold", False),
        ("TBRRidge_BlockResidualBootstrap", False),
        ("DID_Bootstrap", False),
        ("SCM", False),
        ("TBRRidge", False),
    ],
)
def test_config_eligibility_registry(config_name: str, expected: bool):
    assert is_nominal_calibration_eligible_config(config_name) is expected
    assert (config_name in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS) is expected


@pytest.mark.parametrize(
    "config_name,skip_reason",
    [
        ("TBRRidge_BlockResidualBootstrap", BRB_BOUNDS_INVERTED_RUN001),
        ("TBRRidge_Kfold", KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001),
    ],
)
def test_removed_config_registry_skip_reason(config_name: str, skip_reason: str):
    assert nominal_calibration_registry_skip_reason(config_name) == skip_reason


def test_aligned_config_nominal_check_eligible():
    out = run_nominal_calibration_check(
        "SCM_UnitJackKnife",
        "recovery_null_effect",
        n_simulations=3,
        random_state=0,
    )
    assert out["eligible_for_nominal_calibration"] is True
    assert out["ineligible_reason"] == "eligible"
    assert out["skip_reason"] is None
    assert out["interval_aligned"] is True
    assert out["interval_estimand"] == INTERVAL_ESTIMAND_RELATIVE_ATT_POST
    assert out["point_estimand"] == POINT_ESTIMAND
    assert out["interval_scale"] == "path_period_relative_mean"
    assert any("CI smoke is not production calibration" in w for w in out["warnings"])
    assert any(
        str(MIN_REPLICATIONS_FOR_STABLE_CALIBRATION) in w for w in out["warnings"]
    )
    for note in SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES:
        assert any(note in w for w in out["warnings"])


@pytest.mark.parametrize(
    "config_name,skip_reason",
    [
        ("TBRRidge_BlockResidualBootstrap", BRB_BOUNDS_INVERTED_RUN001),
        ("TBRRidge_Kfold", KFOLD_MULTI_TREATED_UNSUPPORTED_RUN001),
    ],
)
def test_removed_config_skipped_without_recovery_run(
    config_name: str, skip_reason: str
):
    out = run_nominal_calibration_check(
        config_name,
        "recovery_null_effect",
        n_simulations=2,
        random_state=0,
    )
    assert out["eligible_for_nominal_calibration"] is False
    assert out["ineligible_reason"] == skip_reason
    assert out["skip_reason"] == skip_reason
    assert out.get("skipped") is True
    assert any(skip_reason in w for w in out["warnings"])


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
    assert out["skip_reason"] == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    assert out["ineligible_reason"] == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
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


def test_ineligible_reason_for_removed_config_without_payload():
    assert (
        ineligible_reason_for_calibration(
            "TBRRidge_BlockResidualBootstrap",
            {},
        )
        == BRB_BOUNDS_INVERTED_RUN001
    )


def test_small_n_warning_when_below_production_threshold():
    out = run_nominal_calibration_check(
        "SCM_UnitJackKnife",
        "recovery_null_effect",
        n_simulations=5,
        random_state=4,
    )
    assert out["n_simulations"] < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
    assert any("small simulation count" in w for w in out["warnings"])
