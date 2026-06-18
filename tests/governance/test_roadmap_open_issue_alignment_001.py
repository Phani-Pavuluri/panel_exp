"""Roadmap ↔ open investigation alignment — registry lane bindings."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import (
    INVESTIGATION_ID_PATTERN,
    load_registry,
)

_REPO = Path(__file__).resolve().parents[2]
MIP_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
ROADMAP_V4 = _REPO / "docs/ROADMAP_V4.md"


class TestRoadmapOpenIssueAlignment001:
    def test_mip_references_authoritative_registry(self) -> None:
        text = MIP_REGISTRY.read_text(encoding="utf-8")
        assert "OPEN_INVESTIGATIONS_001.json" in text

    def test_roadmap_references_authoritative_registry(self) -> None:
        text = ROADMAP_V4.read_text(encoding="utf-8")
        assert "OPEN_INVESTIGATIONS_001.json" in text

    def test_registry_lane_bindings_align_with_complete_artifacts(self) -> None:
        reg = load_registry()
        mip = MIP_REGISTRY.read_text(encoding="utf-8")
        for binding in reg.get("roadmap_lane_bindings", []):
            lane = binding["lane_id"]
            if binding.get("status") != "complete":
                continue
            assert lane.replace("-", "_") in mip or lane in mip, f"Complete lane {lane} missing from MIP registry"

    def test_open_brb_variance_in_mip_points_to_registry_id(self) -> None:
        mip = MIP_REGISTRY.read_text(encoding="utf-8")
        assert "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001" in mip
        assert "OPEN_INVESTIGATIONS_001.json" in mip

    def test_no_duplicate_investigation_registry_sections_in_mip(self) -> None:
        mip = MIP_REGISTRY.read_text(encoding="utf-8")
        count = len(re.findall(r"^## INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001", mip, flags=re.MULTILINE))
        assert count <= 1

    def test_dcm005_reassessment_cannot_close_with_unconsumed_open_issues(self) -> None:
        reg = load_registry()
        binding = next(b for b in reg["roadmap_lane_bindings"] if b["lane_id"] == "DCM-005-ELIGIBILITY-REASSESSMENT")
        assert binding["must_consume_before_close"]
        assert binding["status"] == "complete"
        assert binding.get("resolved_investigations") or binding.get("deferred_investigations")

    def test_roadmap_ordered_next_lists_variance_before_kfold(self) -> None:
        text = ROADMAP_V4.read_text(encoding="utf-8")
        assert "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001" in text
        inv_pos = text.index("INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001")
        kfold_pos = text.index("D5-TRUST-TBRRIDGE-KFOLD-001")
        assert inv_pos < kfold_pos
