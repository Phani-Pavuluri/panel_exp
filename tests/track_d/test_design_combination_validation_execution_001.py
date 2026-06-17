"""Tests for DESIGN-COMBINATION-VALIDATION-EXECUTION-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_design_combination_validation_execution_001 import (
    ARTIFACT_ID,
    DCM_ROWS,
    CORRECTED_DESIGNS,
    DCVExecutionConfig,
    build_payload,
    build_summary_payload,
    evaluate_readout_compatibility,
    write_artifact_atomic,
)

REPO = Path(__file__).resolve().parents[2]
SUMMARY = REPO / "docs/track_d/archives/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_summary.json"

ALLOWED_VERDICTS = {
    "design_combinations_characterized_no_promotion",
    "design_combinations_mixed_with_method_specific_restrictions",
    "design_combinations_partially_validated_remaining_blocks",
    "design_combinations_empirically_blocked",
    "design_combination_execution_inconclusive",
    "design_combination_execution_failed",
}

REQUIRED_SUMMARY_KEYS = (
    "artifact_id",
    "artifact_version",
    "generated_at",
    "git_commit",
    "config",
    "matrix_rows",
    "designs",
    "estimators",
    "inference_paths",
    "worlds",
    "run_counts",
    "aggregate_results",
    "combination_results",
    "geometry_results",
    "readout_results",
    "pairwise_comparisons",
    "failure_summary",
    "reason_code_summary",
    "contract_guardrail_summary",
    "multicell_summary",
    "promotion_summary",
    "verdict",
    "limitations",
)


@pytest.fixture
def fast_cfg() -> DCVExecutionConfig:
    return DCVExecutionConfig(fast=True)


class TestCombinationExecutionHarness:
    def test_all_matrix_rows_represented(self) -> None:
        ids = {r["combination_id"] for r in DCM_ROWS}
        assert ids == {f"DCM-{i:03d}" for i in range(1, 20)}

    def test_fast_build_verdict(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED_VERDICTS
        assert payload["config"]["legacy_tier1_not_default"] is True

    def test_corrected_designs_used(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        labels = {
            r["design_label"]
            for r in payload["run_records"]
            if r.get("design_label") and r.get("lane") == "A"
        }
        for spec in CORRECTED_DESIGNS:
            assert spec.label in labels

    def test_multicell_lane_separated(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        mc = [r for r in payload["run_records"] if r.get("lane") == "D"]
        assert mc
        assert payload["multicell_summary"]["per_cell_lane_separated"] is True

    def test_pooled_claims_blocked(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        assert payload["multicell_summary"]["pooled_claims_blocked"] is True
        dcm007 = [r for r in payload["run_records"] if r.get("combination_id") == "DCM-007"]
        assert dcm007
        assert all(r.get("block_enforced") for r in dcm007)

    def test_geometry_mismatch_rows_block(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        dcm003 = [
            r
            for r in payload["run_records"]
            if r.get("combination_id") == "DCM-003"
        ]
        assert dcm003
        assert all(
            r.get("combination_status") == "blocked_due_to_geometry_mismatch"
            for r in dcm003
            if r.get("assignment_status") == "success"
        )

    def test_readout_mismatch_rows_block(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        readout = payload["readout_results"]
        assert len(readout) >= 4
        assert all(r.get("block_enforced") for r in readout if "block_enforced" in r)

    def test_point_only_cannot_claim_intervals(self) -> None:
        status, reasons = evaluate_readout_compatibility("point_only", "causal_interval")
        assert status == "blocked_due_to_readout_mismatch"
        assert reasons

    def test_forecast_interval_cannot_claim_causal(self) -> None:
        status, _ = evaluate_readout_compatibility("forecast_interval", "causal_interval")
        assert status == "blocked_due_to_readout_mismatch"

    def test_null_monitor_cannot_claim_causal(self) -> None:
        status, _ = evaluate_readout_compatibility("null_monitor", "causal_inference")
        assert status == "blocked_due_to_readout_mismatch"

    def test_pairwise_comparisons_generated(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        assert isinstance(payload["pairwise_comparisons"], list)

    def test_failed_runs_preserved(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        assert payload["failure_summary"]["preserved_failed_runs"] is True

    def test_summary_schema_complete(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        summary = build_summary_payload(payload)
        for key in REQUIRED_SUMMARY_KEYS:
            assert key in summary, f"missing {key}"
        assert "run_records" not in summary

    def test_no_production_promotion(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        assert payload["promotion_summary"]["promotion_allowed"] is False
        assert payload["promotion_summary"]["production_ready"] is False

    def test_deterministic_paired_seeds(self, fast_cfg: DCVExecutionConfig) -> None:
        a = build_payload(fast_cfg)
        b = build_payload(fast_cfg)
        assert a["run_counts"]["total_records"] == b["run_counts"]["total_records"]
        assert a["verdict"] == b["verdict"]

    def test_atomic_summary_write(self, fast_cfg: DCVExecutionConfig, tmp_path: Path) -> None:
        payload = build_payload(fast_cfg)
        summary = build_summary_payload(payload)
        out = tmp_path / "summary.json"
        write_artifact_atomic(out, summary, overwrite=True)
        loaded = json.loads(out.read_text())
        assert loaded["artifact_id"] == ARTIFACT_ID

    def test_full_local_archive_generation(self, fast_cfg: DCVExecutionConfig, tmp_path: Path) -> None:
        payload = build_payload(fast_cfg)
        out = tmp_path / "full.json"
        write_artifact_atomic(out, payload, overwrite=True)
        loaded = json.loads(out.read_text())
        assert "run_records" in loaded
        assert len(loaded["run_records"]) > 0

    def test_committed_summary_not_oversized(self) -> None:
        if not SUMMARY.exists():
            pytest.skip("summary not generated yet")
        size_kb = SUMMARY.stat().st_size / 1024
        assert size_kb < 500, f"summary too large: {size_kb:.0f} KB"

    def test_lane_e_rows_not_executed(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        lane_e = [r for r in payload["run_records"] if r.get("lane") == "E"]
        assert lane_e
        assert all(r.get("execution_attempted") is False for r in lane_e)

    def test_shared_control_surfaced_multicell(self, fast_cfg: DCVExecutionConfig) -> None:
        payload = build_payload(fast_cfg)
        dcm006 = [r for r in payload["run_records"] if r.get("combination_id") == "DCM-006"]
        assert any("shared_control_burden" in r for r in dcm006)
