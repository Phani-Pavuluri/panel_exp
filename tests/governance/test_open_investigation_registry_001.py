"""OPEN_INVESTIGATIONS_001 — authoritative investigation registry tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import (
    DEFAULT_REGISTRY_PATH,
    investigations_by_id,
    load_registry,
    validate_registry,
)

_REPO = Path(__file__).resolve().parents[2]


class TestOpenInvestigationRegistry001:
    def test_registry_file_exists(self) -> None:
        assert DEFAULT_REGISTRY_PATH.is_file()

    def test_registry_is_authoritative_json(self) -> None:
        reg = load_registry()
        assert reg["authoritative"] is True
        assert reg["registry_id"] == "OPEN_INVESTIGATIONS_001"
        assert len(reg["investigations"]) >= 5

    def test_registry_validates_clean(self) -> None:
        issues = validate_registry()
        assert issues == [], "\n".join(f"{i.code}: {i.message}" for i in issues)

    def test_brb_variance_investigation_seeded(self) -> None:
        by_id = investigations_by_id()
        inv = by_id["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"]
        assert inv.status == "RESOLVED"
        assert inv.discovered_by == "TBRRIDGE-BRB-INTERVAL-CORRECTION-001"
        assert inv.revisit_trigger is None
        assert inv.decision_checkpoint is not None
        assert inv.blocking_policy is not None
        assert inv.resolution_artifact == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        assert inv.current_decision == "DIAGNOSTIC_ONLY"
        assert inv.evidence.get("post_remediation_decision") == "BRB_DIAGNOSTIC_ONLY"

    def test_brb_estimand_alignment_resolved(self) -> None:
        inv = investigations_by_id()["INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001"]
        assert inv.status == "RESOLVED"
        assert inv.resolution_artifact == "TBRRIDGE-BRB-INTERVAL-CORRECTION-001"

    def test_investigation_ids_unique(self) -> None:
        reg = load_registry()
        ids = [i["investigation_id"] for i in reg["investigations"]]
        assert len(ids) == len(set(ids))

    def test_complete_lanes_have_next_artifact_when_open_issues(self) -> None:
        reg = load_registry()
        for binding in reg.get("roadmap_lane_bindings", []):
            if binding.get("status") != "complete":
                continue
            if binding.get("open_investigations"):
                assert binding.get("next_artifact"), binding["lane_id"]

    def test_post_remediation_lane_resolves_brb_variance(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
        assert "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001" in lane["resolved_investigations"]
        assert lane["next_artifact"] == "TRUSTREPORT_DOWNSTREAM_PROMOTION_001"

    def test_downstream_promotion_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
        assert lane["next_artifact"] == "TRUSTREPORT_INTEGRATION_DRY_RUN_001"

    def test_integration_dry_run_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_RENDERER_001"

    def test_research_mode_renderer_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001"

    def test_research_mode_artifact_export_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001"

    def test_research_mode_review_workflow_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001"

    def test_research_mode_access_control_lane_complete(self) -> None:
        reg = load_registry()
        lane = next(
            b for b in reg["roadmap_lane_bindings"]
            if b["lane_id"] == "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
        )
        assert lane["status"] == "complete"
        assert lane["resolution_artifact"] == "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
        assert lane["next_artifact"] == "TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001"
