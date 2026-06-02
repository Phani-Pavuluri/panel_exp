"""D5-INST-AUDIT-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_audit_001 import (
    ProbeConfig,
    build_d5_inst_audit_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUDIT_001_results.json"
)


class TestD5InstAudit001:
    def test_build_structure(self) -> None:
        payload = build_d5_inst_audit_001(ProbeConfig())
        assert payload["artifact_id"] == "D5-INST-AUDIT-001"
        assert payload["governance"]["inventory_only"] is True
        assert len(payload["estimators"]) >= 10
        assert len(payload["compatibility_matrix"]) > 50

    def test_explicit_answers(self) -> None:
        payload = build_d5_inst_audit_001(ProbeConfig())
        ans = payload["explicit_answers"]
        assert "normal_tbr_geometry" in ans
        assert "bayesian_tbr_uncertainty_object" in ans
        assert "trop_status" in ans

    def test_roadmap(self) -> None:
        payload = build_d5_inst_audit_001(ProbeConfig())
        ids = {r["battery_id"] for r in payload["oc_battery_roadmap"]}
        assert "D5-INST-AUGSYNTH-001" in ids
        assert "D5-INST-TBR-001" in ids
        assert "D5-INST-DID-001" in ids

    def test_scm_jk_probe_success(self) -> None:
        payload = build_d5_inst_audit_001(ProbeConfig())
        hits = [
            r
            for r in payload["compatibility_matrix"]
            if r.get("estimator") == "SCM"
            and r.get("inference") == "UnitJackKnife"
            and r.get("geometry_mode") == "single_cell_unit_level"
        ]
        assert hits
        assert hits[0].get("callable_status") == "probe_success"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-AUDIT-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "inventory_complete_augsynth_tbr_then_mmm_readiness_audit_010"


def test_write_artifact(tmp_path: Path) -> None:
    out = write_artifact(tmp_path / "audit.json", cfg=ProbeConfig())
    assert out.is_file()
