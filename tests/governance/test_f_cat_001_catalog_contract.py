"""F-CAT-001 — registry/catalog cleanup contract tests."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.governance.catalog_contract import (
    CALIBRATION_SIGNAL_GOVERNED_ALIASES,
    CLASS_TBR_NAMES,
    TBRRIDGE_CLASS_NAMES,
    CatalogLayer,
    CatalogReadiness,
    assert_catalog_consistency,
    audit_estimator_catalog,
    audit_track_b_calibration_signal_map,
    canonical_catalog_combo_records,
    track_b_alias_governance,
    validate_catalog_combo_record,
)
from panel_exp.governance.geometry_adapter_contract import (
    GeometryClassification,
    GeometryReadoutRequest,
    GeometryType,
    ReadoutExportTier,
    classify_combined_readout,
    classify_geometry_support,
)
from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    classify_interval_semantics,
)
from panel_exp.governance.instrument_contract import assert_not_placebo_as_estimator
from panel_exp.inference_result import IntervalType
from panel_exp.method_metadata import estimator_catalog
from panel_exp.track_b._registry import CALIBRATION_SIGNAL_BY_CONFIG
from panel_exp.validation.nominal_calibration import NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS


class TestTaxonomy:
    def test_tbr_and_tbrridge_distinct_classes(self) -> None:
        classes = {m.class_name: m.name for m in estimator_catalog()}
        assert classes["TBR"] == "TBR"
        assert classes["TBRRidge"] == "TBRRidge"
        assert "TBR" in CLASS_TBR_NAMES
        assert "TBRRidge" in TBRRIDGE_CLASS_NAMES

    def test_placebo_not_estimator_catalog_name(self) -> None:
        names = {m.name for m in estimator_catalog()}
        assert "Placebo" not in names

    def test_placebo_as_estimator_raises(self) -> None:
        with pytest.raises(ValueError, match="inference/falsification"):
            assert_not_placebo_as_estimator("Placebo")

    def test_tbrridge_documents_inv015(self) -> None:
        tbrr = next(m for m in estimator_catalog() if m.name == "TBRRidge")
        combined = " ".join(tbrr.known_limitations).lower()
        assert "inv-015" in combined or "not" in combined and "mcmc" in combined


class TestStaleClaimsBlocked:
    def test_conformal_not_governed_uncertainty_in_catalog(self) -> None:
        rec = next(
            r
            for r in canonical_catalog_combo_records()
            if r.estimator_class_name == "AugSynthCVXPY" and r.inference_mode == "Conformal"
        )
        assert rec.interval_semantics_tier in (
            IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY,
            IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS,
            IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL,
        )
        assert rec.governed_uncertainty_claim is False
        violations = validate_catalog_combo_record(rec)
        assert not any(v.code == "governed_uncertainty_forbidden" for v in violations)

    def test_tbrridge_kfold_not_calibration_signal_eligible(self) -> None:
        gov = track_b_alias_governance("TBRRidge_Kfold")
        assert gov["calibration_signal_eligible"] is False
        assert gov["mmm_ready"] is False
        assert gov["governed_uncertainty"] is False

    def test_only_scm_jk_nominal_eligible(self) -> None:
        assert CALIBRATION_SIGNAL_GOVERNED_ALIASES == NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS

    def test_track_b_non_scm_signals_flagged(self) -> None:
        violations = audit_track_b_calibration_signal_map(CALIBRATION_SIGNAL_BY_CONFIG)
        flagged = {v.source for v in violations}
        assert "TBRRidge_Kfold" in flagged or any("TBRRidge" in v.message for v in violations)

    def test_pooled_multi_cell_blocked_in_catalog(self) -> None:
        rec = next(
            r
            for r in canonical_catalog_combo_records()
            if r.geometry_type == GeometryType.POOLED_MULTI_CELL
        )
        assert rec.geometry_tier == GeometryClassification.BLOCKED_MISSING_POOLING_RULE
        assert rec.export_tier == ReadoutExportTier.BLOCKED


class TestGeometryBeforeInterval:
    def test_valid_interval_on_blocked_geometry_stays_blocked(self) -> None:
        """F-INF interval status does not override F-GEO geometry blocking."""
        geo_req = GeometryReadoutRequest(
            estimator_name="TBR",
            inference_mode="Kfold",
            geometry_type=GeometryType.UNIT_PANEL,
            callable=True,
        )
        n = 8
        interval = classify_interval_semantics(
            IntervalReadout(
                estimator_name="TBR",
                inference_mode="Kfold",
                geometry_mode="single_cell",
                path_interval_type=IntervalType.CONFIDENCE_INTERVAL.value,
                y=np.full(n, 10.0),
                y_hat=np.full(n, 10.0),
                y_lower=np.full(n, 8.0),
                y_upper=np.full(n, 12.0),
                test_length=n,
                null_interval_exclusion_rate=0.0,
            ),
            require_metadata_bindings=False,
        )
        combined = classify_combined_readout(geo_req, interval)
        assert combined.geometry_blocks is True
        assert combined.export_tier == ReadoutExportTier.BLOCKED

        rec = next(
            r
            for r in canonical_catalog_combo_records()
            if r.estimator_class_name == "TBR" and r.geometry_type == GeometryType.UNIT_PANEL
        )
        assert rec.catalog_readiness == CatalogReadiness.BLOCKED


class TestCatalogAudits:
    def test_estimator_catalog_audit_passes(self) -> None:
        assert audit_estimator_catalog() == ()

    def test_canonical_records_validate(self) -> None:
        for rec in canonical_catalog_combo_records():
            violations = validate_catalog_combo_record(rec)
            assert violations == (), f"{rec}: {violations}"

    def test_assert_catalog_consistency_without_track_b_signals(self) -> None:
        assert_catalog_consistency(track_b_signals=None)

    def test_placebo_catalog_layer(self) -> None:
        rec = next(
            r
            for r in canonical_catalog_combo_records()
            if r.inference_mode == "Placebo"
        )
        assert rec.catalog_layer == CatalogLayer.INFERENCE_FALSIFICATION
