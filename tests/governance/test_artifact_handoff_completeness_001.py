"""Artifact handoff completeness — INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import (
    REQUIRED_HANDOFF_KEYS,
    validate_artifact_handoff,
    validate_report_handoff_section,
)

_REPO = Path(__file__).resolve().parents[2]

# Governed TBRRidge artifacts with mandatory handoff (expand as contract rolls out).
REQUIRED_HANDOFF_SUMMARIES = (
    _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json",
    _REPO / "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json",
)

REQUIRED_HANDOFF_REPORTS = (
    _REPO / "docs/track_d/D5_TRUST_TBRRIDGE_BRB_001_REPORT.md",
    _REPO / "docs/track_d/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_REPORT.md",
)


class TestArtifactHandoffCompleteness001:
    @pytest.mark.parametrize("summary_path", REQUIRED_HANDOFF_SUMMARIES)
    def test_summary_has_investigation_handoff(self, summary_path: Path) -> None:
        if not summary_path.exists():
            pytest.skip(f"Missing {summary_path.name}")
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        issues = validate_artifact_handoff(payload)
        assert issues == [], "\n".join(i.message for i in issues)

    @pytest.mark.parametrize("summary_path", REQUIRED_HANDOFF_SUMMARIES)
    def test_summary_handoff_keys_complete(self, summary_path: Path) -> None:
        if not summary_path.exists():
            pytest.skip(f"Missing {summary_path.name}")
        handoff = json.loads(summary_path.read_text(encoding="utf-8")).get("investigation_handoff", {})
        assert REQUIRED_HANDOFF_KEYS <= set(handoff.keys())

    @pytest.mark.parametrize("report_path", REQUIRED_HANDOFF_REPORTS)
    def test_report_has_residual_handoff_section(self, report_path: Path) -> None:
        if not report_path.exists():
            pytest.skip(f"Missing {report_path.name}")
        text = report_path.read_text(encoding="utf-8")
        issues = validate_report_handoff_section(text, artifact_id=report_path.stem)
        assert issues == [], "\n".join(i.message for i in issues)

    def test_interval_correction_opens_variance_investigation(self) -> None:
        path = _REPO / "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json"
        if not path.exists():
            pytest.skip("correction summary missing")
        handoff = json.loads(path.read_text(encoding="utf-8"))["investigation_handoff"]
        assert "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001" in handoff["follow_up_issues"]
        assert "INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001" in handoff["resolved_issues"]

    def test_characterization_routes_to_interval_correction(self) -> None:
        path = _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json"
        if not path.exists():
            pytest.skip("characterization summary missing")
        handoff = json.loads(path.read_text(encoding="utf-8"))["investigation_handoff"]
        assert handoff["next_artifact"] == "TBRRIDGE-BRB-INTERVAL-CORRECTION-001"
        assert "INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001" in handoff["follow_up_issues"]
