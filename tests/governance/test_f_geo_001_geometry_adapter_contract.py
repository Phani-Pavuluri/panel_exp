"""F-GEO-001 — geometry adapter contract tests."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.geometry_adapter_contract import (
    GeometryClassification,
    GeometryReadoutRequest,
    GeometryType,
    ReadoutExportTier,
    classify_combined_readout,
    classify_geometry_support,
    expected_track_f_geometry_classification,
)
from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    classify_interval_semantics,
)
from panel_exp.inference_result import IntervalType

SupportedCaveats = GeometryClassification.GEOMETRY_SUPPORTED_WITH_CAVEATS
BlockedGeometry = GeometryClassification.BLOCKED_GEOMETRY
BlockedPooling = GeometryClassification.BLOCKED_MISSING_POOLING_RULE
BlockedAdapter = GeometryClassification.BLOCKED_MISSING_ADAPTER
BlockedBridge = GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE


def _valid_interval_readout(
    estimator: str,
    inference: str,
    geometry: str,
) -> IntervalReadout:
    n = 8
    center = 10.0
    margin = 2.0
    return IntervalReadout(
        estimator_name=estimator,
        inference_mode=inference,
        geometry_mode=geometry,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
        interval_units="level_outcome",
        target_estimand="unit_level_att",
        y=np.full(n, center),
        y_hat=np.full(n, center),
        y_lower=np.full(n, center - margin),
        y_upper=np.full(n, center + margin),
        test_length=n,
        null_interval_exclusion_rate=0.0,
    )


class TestClassTBRGeometry:
    def test_tbr_unit_panel_blocked(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="point_estimate",
            geometry_type=GeometryType.UNIT_PANEL,
            callable=True,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedGeometry
        assert verdict.export_tier == ReadoutExportTier.BLOCKED
        assert not verdict.geometry_supported

    def test_tbr_aggregate_1x1_supported_with_caveats(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="point_estimate",
            geometry_type=GeometryType.AGGREGATE_TWO_SERIES_1X1,
            n_treated=1,
            n_control=1,
            callable=True,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == SupportedCaveats
        assert verdict.geometry_supported
        assert verdict.export_tier == ReadoutExportTier.RESTRICTED

    def test_tbr_aggregate_wrong_row_counts_blocked(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="Kfold",
            geometry_type=GeometryType.AGGREGATE_TWO_SERIES_1X1,
            n_treated=2,
            n_control=1,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedGeometry


class TestMultiCellAndPooling:
    def test_pooled_multi_cell_blocked_without_rule(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBRRidge",
            inference_mode="Kfold",
            geometry_type=GeometryType.POOLED_MULTI_CELL,
            n_test_grps=2,
            pooled_claim=True,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedPooling
        assert verdict.export_tier == ReadoutExportTier.BLOCKED

    def test_multi_cell_per_cell_augsynth_allowed_restricted(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="AugSynthCVXPY",
            inference_mode="Kfold",
            geometry_type=GeometryType.MULTI_CELL_PER_CELL,
            n_test_grps=2,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == SupportedCaveats
        assert verdict.export_tier == ReadoutExportTier.RESTRICTED


class TestSupergeoAndTrim:
    def test_supergeo_blocked_without_adapter(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="SyntheticControl",
            inference_mode="UnitJackKnife",
            geometry_type=GeometryType.SUPERGEO_UNIT,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedAdapter

    def test_trim_blocked_without_bridge(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="SyntheticControl",
            inference_mode="UnitJackKnife",
            geometry_type=GeometryType.TRIMMED_POPULATION,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedBridge


class TestReadoutFamilies:
    def test_tbrridge_unit_panel_restricted(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBRRidge",
            inference_mode="Kfold",
            geometry_type=GeometryType.UNIT_PANEL,
            callable=True,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == SupportedCaveats

    def test_tbrridge_non_unit_blocked(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBRRidge",
            inference_mode="Kfold",
            geometry_type=GeometryType.AGGREGATE_TWO_SERIES_1X1,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedGeometry

    def test_scm_unit_diagnostic(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="SyntheticControl",
            inference_mode="UnitJackKnife",
            geometry_type=GeometryType.UNIT_PANEL,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == SupportedCaveats
        assert verdict.export_tier == ReadoutExportTier.FUTURE_CALIBRATION_SIGNAL_ELIGIBLE

    def test_placebo_multi_treated_blocked(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="SyntheticControl",
            inference_mode="Placebo",
            geometry_type=GeometryType.UNIT_PANEL,
            n_treated=3,
            single_treated_geometry=False,
        )
        verdict = classify_geometry_support(req)
        assert verdict.classification == BlockedGeometry

    def test_callable_does_not_imply_geometry_support(self) -> None:
        req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="point_estimate",
            geometry_type=GeometryType.UNIT_PANEL,
            callable=True,
        )
        verdict = classify_geometry_support(req)
        assert req.callable is True
        assert not verdict.geometry_supported


class TestCombinedGeometryAndInterval:
    def test_interval_does_not_override_geometry_block(self) -> None:
        """Valid-looking F-INF interval cannot rescue TBR on unit_panel."""
        geo_req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="Kfold",
            geometry_type=GeometryType.UNIT_PANEL,
            callable=True,
        )
        interval = classify_interval_semantics(
            _valid_interval_readout("TBR", "Kfold", "unit_panel"),
            require_metadata_bindings=False,
        )
        assert interval.classification == IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY

        combined = classify_combined_readout(geo_req, interval)
        assert combined.geometry_blocks is True
        assert combined.export_tier == ReadoutExportTier.BLOCKED
        assert combined.governed_export is False
        assert "Geometry blocking takes precedence" in combined.policy_note

    def test_supergeo_blocked_even_with_valid_interval(self) -> None:
        geo_req = GeometryReadoutRequest(
            estimator_name="SyntheticControl",
            inference_mode="UnitJackKnife",
            geometry_type=GeometryType.SUPERGEO_UNIT,
        )
        interval = classify_interval_semantics(
            _valid_interval_readout("SyntheticControl", "UnitJackKnife", "supergeo"),
            require_metadata_bindings=False,
        )
        combined = classify_combined_readout(geo_req, interval)
        assert combined.export_tier == ReadoutExportTier.BLOCKED
        assert combined.geometry_blocks is True


class TestTrackFRegistry:
    @pytest.mark.parametrize(
        "estimator,inference,geometry,expected",
        [
            ("TBR", "point_estimate", GeometryType.UNIT_PANEL, BlockedGeometry),
            ("TBR", "point_estimate", GeometryType.AGGREGATE_TWO_SERIES_1X1, SupportedCaveats),
            ("TBRRidge", "Kfold", GeometryType.POOLED_MULTI_CELL, BlockedPooling),
            ("SyntheticControl", "UnitJackKnife", GeometryType.SUPERGEO_UNIT, BlockedAdapter),
        ],
    )
    def test_known_geometry_dispositions(
        self,
        estimator: str,
        inference: str,
        geometry: GeometryType,
        expected: GeometryClassification,
    ) -> None:
        got = expected_track_f_geometry_classification(estimator, inference, geometry)
        assert got == expected
