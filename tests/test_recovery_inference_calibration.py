"""Recovery calibration with inference-enabled configs and failure metadata."""

from __future__ import annotations

import math

import pytest

from panel_exp.validation.recovery_metrics import (
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_runner import (
    RecoveryRunner,
    all_recovery_configs,
)
from panel_exp.validation.synthetic_world import SyntheticScenario


def _single_treated_null_scenario() -> SyntheticScenario:
    return SyntheticScenario(
        name="recovery_null_single_treated",
        n_geos=12,
        n_periods=40,
        treatment_start=28,
        true_effect=0.0,
        treated_units=("geo_0",),
        heterogeneous_effects=False,
        spillover_strength=0.0,
        noise_scale=0.3,
        cross_geo_correlation=0.2,
        random_state=0,
    )


def _assert_finite_or_explicit(payload: dict, metric: str, status_key: str) -> None:
    value = payload[metric]
    status = payload[status_key]
    reason_key = {
        "coverage": "coverage_unavailable_reason",
        "false_positive_rate": "false_positive_rate_unavailable_reason",
        "power": "power_unavailable_reason",
    }[metric]
    if value == value:
        assert 0.0 <= value <= 1.0
        assert status == "computed"
    else:
        assert status == "unavailable"
        assert payload.get(reason_key)


@pytest.mark.parametrize(
    "config_name",
    ["SCM_UnitJackKnife", "TBRRidge_BlockResidualBootstrap", "DID_Bootstrap"],
)
def test_inference_config_null_calibration_metrics(config_name: str):
    payload = RecoveryRunner(
        config_name,
        "recovery_null_effect",
        n_simulations=4,
        random_state=10,
    ).run()
    assert payload["recovery_config"] == config_name
    assert payload["intervals_expected"] is True
    assert payload["inference_mode"] is not None
    _assert_finite_or_explicit(payload, "coverage", "coverage_status")
    _assert_finite_or_explicit(payload, "false_positive_rate", "false_positive_rate_status")


def test_tbrridge_kfold_null_on_single_treated_panel():
    payload = RecoveryRunner(
        "TBRRidge_Kfold",
        _single_treated_null_scenario(),
        n_simulations=3,
        random_state=20,
    ).run()
    assert payload["recovery_config"] == "TBRRidge_Kfold"
    assert payload["intervals_expected"] is True
    _assert_finite_or_explicit(payload, "coverage", "coverage_status")
    _assert_finite_or_explicit(payload, "false_positive_rate", "false_positive_rate_status")


def test_point_estimate_scm_still_works():
    payload = RecoveryRunner(
        "SCM",
        "recovery_positive_effect",
        n_simulations=2,
        random_state=1,
    ).run()
    assert payload["recovery_config"] == "SCM"
    assert payload["intervals_expected"] is False
    assert payload["coverage_status"] == "not_requested"
    assert math.isnan(payload["coverage"])
    assert payload["failure_rate"] == pytest.approx(0.0, abs=1e-9)


def test_failed_simulation_records_failure_metadata():
    records = [
        SimulationRecord(
            predicted_effect=float("nan"),
            true_effect=0.0,
            failed=True,
            failure_type="ValueError",
            failure_message="too few donors",
            intervals_available=False,
            intervals_unavailable_reason="run_failed:ValueError",
        ),
        SimulationRecord(
            predicted_effect=0.01,
            true_effect=0.0,
            ci_lower=-0.05,
            ci_upper=0.05,
            significant=False,
            failed=False,
            intervals_available=True,
        ),
    ]
    result = aggregate_recovery_metrics(
        estimator="SCM_UnitJackKnife",
        scenario="recovery_null_effect",
        records=records,
        intervals_expected=True,
    )
    assert result.failure_rate == pytest.approx(0.5)
    assert result.failure_types == {"ValueError": 1}
    assert result.coverage_status == "computed"
    assert result.coverage == pytest.approx(1.0)


def test_aggregate_payload_includes_failure_fields():
    payload = RecoveryRunner(
        "SCM_UnitJackKnife",
        "recovery_null_effect",
        n_simulations=3,
        random_state=5,
    ).run()
    assert "failure_rate" in payload
    assert "failure_types" in payload
    assert isinstance(payload["failure_types"], dict)
    assert 0.0 <= payload["failure_rate"] <= 1.0


def test_inference_configs_registered():
    configs = all_recovery_configs()
    for name in (
        "SCM",
        "SCM_UnitJackKnife",
        "TBRRidge_Kfold",
        "TBRRidge_BlockResidualBootstrap",
        "DID_Bootstrap",
    ):
        assert name in configs
    assert configs["SCM_UnitJackKnife"].intervals_expected is True
    assert configs["SCM"].intervals_expected is False


def test_did_bootstrap_positive_scenario_power_metric():
    payload = RecoveryRunner(
        "DID_Bootstrap",
        "recovery_positive_effect",
        n_simulations=4,
        random_state=30,
    ).run()
    assert payload["power_status"] in ("computed", "unavailable")
    if payload["power"] == payload["power"]:
        assert 0.0 <= payload["power"] <= 1.0
