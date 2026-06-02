"""D5-INST-COMBO-AUDIT-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_combo_audit_001 import (
    ComboAuditConfig,
    ProbeConfig,
    build_d5_inst_combo_audit_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_COMBO_AUDIT_001_results.json"
)


class TestD5InstComboAudit001:
    def test_build_structure(self) -> None:
        cfg = ComboAuditConfig(run_probes=False)
        payload = build_d5_inst_combo_audit_001(cfg)
        assert payload["artifact_id"] == "D5-INST-COMBO-AUDIT-001"
        assert payload["governance"]["no_cartesian_product"] is True
        assert len(payload["compatibility_matrix"]) >= 20

    def test_tbr_unit_invalid_geometry(self) -> None:
        cfg = ComboAuditConfig(run_probes=False)
        payload = build_d5_inst_combo_audit_001(cfg)
        hit = next(
            r
            for r in payload["compatibility_matrix"]
            if r["estimator_class"] == "TBR"
            and r["inference"] == "point_estimate"
            and r["geometry_mode"] == "single_cell_unit_level"
        )
        assert hit["status"] == "invalid_by_geometry"

    def test_augsynth_kfold_unvalidated_or_candidate(self) -> None:
        cfg = ComboAuditConfig(run_probes=False)
        payload = build_d5_inst_combo_audit_001(cfg)
        hit = next(
            r
            for r in payload["compatibility_matrix"]
            if r["estimator_class"] == "AugSynthCVXPY" and r["inference"] == "Kfold"
        )
        assert hit["status"] in (
            "implemented_but_unvalidated",
            "valid_candidate",
            "already_characterized",
        )

    def test_scm_jk_already_characterized(self) -> None:
        cfg = ComboAuditConfig(run_probes=False)
        payload = build_d5_inst_combo_audit_001(cfg)
        hit = next(
            r
            for r in payload["compatibility_matrix"]
            if r["estimator_class"] == "SyntheticControl"
            and r["inference"] == "UnitJackKnife"
            and r["geometry_mode"] == "single_cell_unit_level"
        )
        assert hit["status"] == "already_characterized"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-COMBO-AUDIT-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "compatibility_audited_curated_combinations_only"


def test_write_artifact(tmp_path: Path) -> None:
    cfg = ComboAuditConfig(run_probes=False)
    out = write_artifact(tmp_path / "combo.json", cfg=cfg)
    assert out.is_file()
