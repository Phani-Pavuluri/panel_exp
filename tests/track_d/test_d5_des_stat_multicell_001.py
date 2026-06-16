"""Tests for D5-DES-STAT-MULTICELL-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.assign import CompleteRandomization
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_stat_multicell_001 import (
    ARTIFACT_ID,
    MIN_CONTROL_THRESHOLD,
    POLICY_SPECS,
    WORLD_IDS,
    MulticellHarnessConfig,
    build_d5_des_stat_multicell_001,
    build_summary_payload,
    synthesize_panel,
    write_artifact_atomic,
    _world_spec,
)

ALLOWED = {
    "multicell_feasibility_fixed_requires_statistical_followup",
    "multicell_partially_validated_with_restrictions",
    "multicell_per_cell_only_pooled_claims_blocked",
    "multicell_infeasible_regimes_explicitly_blocked",
    "multicell_characterized_no_safe_fix",
    "multicell_harness_inconclusive",
    "multicell_harness_failed",
}

REPO = Path(__file__).resolve().parents[2]
SUMMARY = REPO / "docs" / "track_d" / "archives" / "D5_DES_STAT_MULTICELL_001_summary.json"


@pytest.fixture
def fast_cfg() -> MulticellHarnessConfig:
    return MulticellHarnessConfig(fast=True)


class TestMulticellHarness:
    def test_fast_build_verdict_allowed(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED
        assert payload["runtime"]["total_attempted_runs"] > 0

    def test_all_policies_represented(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        seen = {r["policy_id"] for r in payload["run_records"]}
        for pid, _, _ in POLICY_SPECS[:3]:
            assert pid in seen

    def test_worlds_and_cell_counts(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        worlds = {r["world_id"] for r in payload["run_records"]}
        assert worlds
        assert any(r["n_test_grps"] >= 2 for r in payload["run_records"])

    def test_failed_runs_preserved(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        failed = [r for r in payload["run_records"] if r["assignment_status"] == "failed"]
        assert payload["runtime"]["failed_runs"] == len(failed)

    def test_policy_comparisons_generated(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        assert isinstance(payload["policy_comparisons"], list)

    def test_summary_schema(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        summary = build_summary_payload(payload)
        for key in (
            "artifact_id",
            "aggregate_results",
            "failure_summary",
            "cell_balance_summary",
            "control_burden_summary",
            "geometry_summary",
            "contract_guardrail_summary",
            "policy_comparisons",
            "selected_policy",
            "verdict",
            "limitations",
        ):
            assert key in summary
        assert "run_records" not in summary

    def test_atomic_write_and_roundtrip(self, fast_cfg: MulticellHarnessConfig, tmp_path: Path) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        out = tmp_path / "summary.json"
        write_artifact_atomic(out, build_summary_payload(payload), overwrite=False)
        loaded = json.loads(out.read_text())
        assert loaded["verdict"] in ALLOWED
        assert loaded["selected_policy"] == payload["selected_policy"]

    def test_generated_local_archive_roundtrip(
        self, fast_cfg: MulticellHarnessConfig, tmp_path: Path
    ) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        out = tmp_path / "full.json"
        write_artifact_atomic(out, payload, overwrite=False)
        loaded = json.loads(out.read_text())
        assert len(loaded["run_records"]) > 0
        assert loaded["failure_summary"]["pooled_claims_blocked_rate"] == 1.0

    @pytest.mark.skipif(not SUMMARY.exists(), reason="summary not generated")
    def test_committed_summary_archive(self) -> None:
        summary = json.loads(SUMMARY.read_text())
        assert summary["artifact_id"] == ARTIFACT_ID
        assert summary["verdict"] in ALLOWED


class TestMulticellReproduction:
    def test_two_cell_feasible(self) -> None:
        spec = _world_spec("balanced_two_cell", 20, 0.35)
        wide = synthesize_panel(spec, 101)
        panel = PanelDataset(wide.copy())
        design = CompleteRandomization(
            treatment_probability=0.35,
            random_state=101,
            multicell_policy="control_reservation",
            min_control_units=MIN_CONTROL_THRESHOLD,
        )
        assignment = design.assign(panel_data=panel, n_test_grps=2)
        assert len(assignment["control"]) >= MIN_CONTROL_THRESHOLD
        assert design.last_multicell_metadata is not None

    def test_oversubscribed_high_tp(self) -> None:
        spec = _world_spec("treatment_share_exhaustion", 12, 0.65)
        wide = synthesize_panel(spec, 202)
        panel = PanelDataset(wide.copy())
        legacy = CompleteRandomization(
            treatment_probability=0.65, random_state=202, multicell_policy="legacy", min_control_units=3
        )
        fixed = CompleteRandomization(
            treatment_probability=0.65,
            random_state=202,
            multicell_policy="control_reservation",
            min_control_units=3,
        )
        a_legacy = legacy.assign(panel_data=panel, n_test_grps=4)
        a_fixed = fixed.assign(panel_data=panel, n_test_grps=4)
        assert len(a_fixed["control"]) >= 3

    def test_pooled_claim_blocked_in_geometry(self, fast_cfg: MulticellHarnessConfig) -> None:
        payload = build_d5_des_stat_multicell_001(fast_cfg)
        assert payload["geometry_summary"]["pooled_claims_blocked"] is True
