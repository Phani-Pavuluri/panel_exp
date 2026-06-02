"""TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001 artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.track_d_conceptual_validity_audit_001 import (
    build_conceptual_validity_audit_001,
    write_artifact,
)

ARCHIVE = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001_results.json"
)


def test_build_matches_required_families():
    payload = build_conceptual_validity_audit_001()
    ids = {r["audit_id"] for r in payload["method_records"]}
    assert "CV-EST-SCM" in ids
    assert "CV-EST-TBR" in ids
    assert "CV-INF-PLACEBO" in ids
    assert "CV-INF-CONFORMAL" in ids
    assert payload["governance"]["synthetic_oc_not_conceptual_validity"] is True
    assert payload["summary"]["production_ready_count"] == 0


def test_archive_on_disk_is_valid_json():
    assert ARCHIVE.is_file()
    data = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001"
    assert len(data["method_records"]) >= 12


def test_write_artifact_roundtrip(tmp_path):
    out = write_artifact(tmp_path / "cv.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["overall_verdict"] == "continue_with_restricted_diagnostics_only"
