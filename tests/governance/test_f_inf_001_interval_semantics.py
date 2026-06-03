"""F-INF-001 — interval semantics contract tests."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    IntervalSemanticsVerdict,
    TRACK_F_KNOWN_INTERVAL_DISPOSITIONS,
    assert_not_governed_uncertainty,
    classify_interval_semantics,
    classify_track_f_combo,
    detect_inverted_bounds,
    detect_negative_halfwidth,
    detect_null_interval_exclusion_fpr,
    expected_track_f_classification,
    post_window_band_metrics,
)
from panel_exp.inference_result import IntervalType

BlockedInvalid = IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL
CallableUnverified = IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS
DiagnosticOnly = IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY
BlockedInterface = IntervalSemanticsClassification.BLOCKED_INTERFACE
Governed = IntervalSemanticsClassification.GOVERNED_UNCERTAINTY


def _band_readout(
    *,
    estimator: str,
    inference: str,
    geometry: str,
    y_lo: np.ndarray,
    y_hi: np.ndarray,
    path_interval_type: str = IntervalType.CONFIDENCE_INTERVAL.value,
    null_fpr: float | None = None,
    blocked: str | None = None,
    **kwargs,
) -> IntervalReadout:
    n = len(y_lo)
    y = np.linspace(10.0, 10.0 + n, n)
    y_hat = y.copy()
    defaults = dict(
        interval_units="level_outcome",
        target_estimand="unit_level_att",
    )
    defaults.update(kwargs)
    return IntervalReadout(
        estimator_name=estimator,
        inference_mode=inference,
        geometry_mode=geometry,
        callable=blocked is None,
        blocked_interface_reason=blocked,
        path_interval_type=path_interval_type,
        y=y,
        y_hat=y_hat,
        y_lower=y_lo,
        y_upper=y_hi,
        test_length=n,
        null_interval_exclusion_rate=null_fpr,
        **defaults,
    )


class TestIntervalDetectors:
    def test_negative_halfwidth_detected(self) -> None:
        issue = detect_negative_halfwidth(-8.2)
        assert issue is not None
        assert issue.code == "negative_half_width"

    def test_positive_halfwidth_ok(self) -> None:
        assert detect_negative_halfwidth(3.5) is None

    def test_inverted_bounds_detected(self) -> None:
        lo = np.array([5.0, 6.0])
        hi = np.array([4.0, 7.0])
        issue = detect_inverted_bounds(lo, hi)
        assert issue is not None
        assert issue.code == "inverted_lower_upper_bounds"

    def test_null_fpr_concerning(self) -> None:
        issue = detect_null_interval_exclusion_fpr(1.0)
        assert issue is not None
        assert issue.code == "null_interval_exclusion_fpr"


class TestClassification:
    def test_blocked_interface(self) -> None:
        readout = IntervalReadout(
            estimator_name="TBRRidge",
            inference_mode="UnitJackKnife",
            geometry_mode="single_cell",
            callable=False,
            blocked_interface_reason="broadcast shape error",
        )
        verdict = classify_interval_semantics(readout)
        assert verdict.classification == BlockedInterface
        assert verdict.is_governed_uncertainty is False
        assert_not_governed_uncertainty(verdict)

    def test_negative_halfwidth_is_blocked_invalid_not_governed(self) -> None:
        n = 8
        readout = _band_readout(
            estimator="AugSynthCVXPY",
            inference="Conformal",
            geometry="single_cell",
            y_lo=np.full(n, 20.0),
            y_hi=np.full(n, 4.0),
            path_interval_type=IntervalType.CONFORMAL_INTERVAL.value,
            null_fpr=1.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
        assert verdict.classification == BlockedInvalid
        assert verdict.is_governed_uncertainty is False
        assert verdict.mean_interval_halfwidth < 0
        assert_not_governed_uncertainty(verdict)

    def test_null_fpr_only_is_callable_unverified(self) -> None:
        n = 8
        margin = 2.0
        center = 10.0
        readout = _band_readout(
            estimator="TBR",
            inference="JKP",
            geometry="aggregate_two_series",
            y_lo=np.full(n, center - margin),
            y_hi=np.full(n, center + margin),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
            null_fpr=1.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
        assert verdict.classification == CallableUnverified
        assert verdict.is_governed_uncertainty is False
        assert_not_governed_uncertainty(verdict)

    def test_valid_band_restricted_diagnostic_not_governed(self) -> None:
        n = 8
        margin = 1.5
        center = 10.0
        readout = _band_readout(
            estimator="TBRRidge",
            inference="Kfold",
            geometry="single_cell",
            y_lo=np.full(n, center - margin),
            y_hi=np.full(n, center + margin),
            null_fpr=0.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
        assert verdict.classification == DiagnosticOnly
        assert verdict.is_governed_uncertainty is False
        assert verdict.mean_interval_halfwidth > 0
        assert_not_governed_uncertainty(verdict)

    def test_augsynth_jk_diagnostic_only(self) -> None:
        n = 8
        margin = 1.0
        center = 10.0
        readout = _band_readout(
            estimator="AugSynthCVXPY",
            inference="UnitJackKnife",
            geometry="single_cell",
            y_lo=np.full(n, center - margin),
            y_hi=np.full(n, center + margin),
            null_fpr=0.0,
        )
        verdict = classify_track_f_combo(readout)
        assert verdict.classification == DiagnosticOnly
        assert_not_governed_uncertainty(verdict)

    def test_missing_metadata_is_callable_unverified(self) -> None:
        n = 8
        readout = IntervalReadout(
            estimator_name="AugSynthCVXPY",
            inference_mode="Kfold",
            geometry_mode="single_cell",
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
            y=np.full(n, 10.0),
            y_hat=np.full(n, 10.0),
            y_lower=np.full(n, 8.0),
            y_upper=np.full(n, 12.0),
            test_length=n,
            null_interval_exclusion_rate=0.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=True)
        assert verdict.classification == CallableUnverified
        assert any(i.code == "missing_interval_units" for i in verdict.issues)
        assert_not_governed_uncertainty(verdict)

    def test_callable_invalid_cannot_become_governed(self) -> None:
        readout = _band_readout(
            estimator="TBRRidge",
            inference="TimeSeriesKfold",
            geometry="single_cell",
            y_lo=np.full(8, 15.0),
            y_hi=np.full(8, 3.0),
            path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
            null_fpr=1.0,
        )
        verdict = classify_track_f_combo(readout, require_metadata_bindings=False)
        assert verdict.classification in (BlockedInvalid, CallableUnverified)
        with pytest.raises(ValueError, match="governed_uncertainty"):
            assert_not_governed_uncertainty(
                IntervalSemanticsVerdict(
                    classification=Governed,
                    is_governed_uncertainty=True,
                )
            )

    def test_governed_allowlist_empty(self) -> None:
        n = 8
        readout = _band_readout(
            estimator="SyntheticControl",
            inference="UnitJackKnife",
            geometry="single_cell",
            y_lo=np.full(n, 8.0),
            y_hi=np.full(n, 12.0),
            null_fpr=0.0,
        )
        verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
        assert verdict.classification == DiagnosticOnly
        assert verdict.is_governed_uncertainty is False


class TestTrackFRegistry:
    @pytest.mark.parametrize(
        "estimator,inference,geometry,expected",
        [
            ("TBRRidge", "TimeSeriesKfold", "single_cell", DiagnosticOnly),
            ("AugSynthCVXPY", "Conformal", "single_cell", DiagnosticOnly),
            ("TBR", "JKP", "aggregate_two_series", CallableUnverified),
            ("TBRRidge", "UnitJackKnife", "single_cell", CallableUnverified),
            ("TBRRidge", "Conformal", "single_cell", CallableUnverified),
            ("TBRRidge", "JKP", "single_cell", CallableUnverified),
            ("TBRRidge", "Kfold", "single_cell", DiagnosticOnly),
            ("AugSynthCVXPY", "Kfold", "single_cell", DiagnosticOnly),
        ],
    )
    def test_known_dispositions_registered(
        self,
        estimator: str,
        inference: str,
        geometry: str,
        expected: IntervalSemanticsClassification,
    ) -> None:
        got = expected_track_f_classification(estimator, inference, geometry)
        assert got == expected

    def test_registry_covers_p2_findings(self) -> None:
        assert ("AugSynthCVXPY", "Conformal", "single_cell") in TRACK_F_KNOWN_INTERVAL_DISPOSITIONS
        assert ("TBRRidge", "TimeSeriesKfold", "single_cell") in TRACK_F_KNOWN_INTERVAL_DISPOSITIONS


class TestPostWindowMetrics:
    def test_signed_halfwidth_not_abs(self) -> None:
        readout = IntervalReadout(
            estimator_name="X",
            inference_mode="Conformal",
            geometry_mode="single_cell",
            y_lower=np.array([10.0, 10.0]),
            y_upper=np.array([2.0, 2.0]),
            test_length=2,
        )
        _, _, _, _, hw = post_window_band_metrics(readout)
        assert hw < 0
