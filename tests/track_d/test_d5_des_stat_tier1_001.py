"""Tests for D5-DES-STAT-TIER1-001 tier-1 design statistical validation harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_des_stat_tier1_001 import (
    ALL_WORLD_IDS,
    ARTIFACT_ID,
    DESIGN_FAMILIES,
    D5DesStatTier1Config,
    SHARED_SEEDS,
    _world_context,
    build_d5_des_stat_tier1_001,
    run_single,
    synthesize_panel,
    write_artifact_atomic,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_DES_STAT_TIER1_001_results.json"
)

ALLOWED_VERDICTS = frozenset(
    {
        "tier1_designs_characterized_no_promotion",
        "tier1_designs_characterized_with_blocking_failures",
        "tier1_designs_mixed_requires_method_specific_followup",
        "tier1_design_harness_inconclusive",
        "tier1_design_harness_failed",
    }
)


@pytest.fixture
def fast_cfg() -> D5DesStatTier1Config:
    return D5DesStatTier1Config(fast=True)


class TestD5DesStatTier1Harness:
    def test_deterministic_world_generation(self) -> None:
        ctx = _world_context("balanced_markets", D5DesStatTier1Config(fast=True))
        a = synthesize_panel(ctx, seed=42)
        b = synthesize_panel(ctx, seed=42)
        assert a.equals(b)

    def test_deterministic_assignment_fixed_seed(self, fast_cfg: D5DesStatTier1Config) -> None:
        design = DESIGN_FAMILIES[1]
        ctx = _world_context("balanced_markets", fast_cfg)
        r1 = run_single(design, ctx, seed=999, replicate=0, cfg=fast_cfg)
        r2 = run_single(design, ctx, seed=999, replicate=0, cfg=fast_cfg)
        assert r1["assignment_hash"] == r2["assignment_hash"]
        assert r1["assignment_status"] == "success"

    def test_fast_payload_schema(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        assert payload["artifact_id"] == ARTIFACT_ID
        assert payload["verdict"] in ALLOWED_VERDICTS
        for key in (
            "artifact_version",
            "generated_at",
            "git_commit",
            "config",
            "designs",
            "worlds",
            "seeds",
            "replicates",
            "run_records",
            "aggregate_results",
            "pairwise_comparisons",
            "failure_summary",
            "guardrail_summary",
            "limitations",
            "verdict",
        ):
            assert key in payload

    def test_all_design_families_represented(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        ids = {r["design_inventory_id"] for r in payload["run_records"]}
        assert ids == {d.design_inventory_id for d in DESIGN_FAMILIES}

    def test_all_required_world_ids_in_full_config(self) -> None:
        cfg = D5DesStatTier1Config(fast=False, replicates_per_cell=1, replicates_exhaustion=1)
        payload = build_d5_des_stat_tier1_001(cfg)
        worlds = {r["world_id"] for r in payload["run_records"]}
        assert set(ALL_WORLD_IDS).issubset(worlds)

    def test_failed_runs_not_silently_dropped(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        failures = [r for r in payload["run_records"] if r["assignment_status"] != "success"]
        assert payload["runtime"]["failed_runs"] == len(failures)
        assert len(payload["run_records"]) == payload["runtime"]["total_attempted_runs"]

    def test_treatment_pool_exhaustion_recorded(self, fast_cfg: D5DesStatTier1Config) -> None:
        greedy = next(d for d in DESIGN_FAMILIES if d.design_inventory_id == "DES-001")
        ctx = _world_context(
            "treatment_pool_exhaustion_world",
            fast_cfg,
            treatment_probability=0.35,
        )
        record = run_single(greedy, ctx, seed=777, replicate=0, cfg=fast_cfg)
        assert record["world_id"] == "treatment_pool_exhaustion_world"
        assert record["treatment_probability_requested"] == 0.35

    def test_pairwise_comparisons_generated(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        assert payload["pairwise_comparisons"]
        assert any(pc["comparison_id"] == "complete_vs_balanced" for pc in payload["pairwise_comparisons"])

    def test_contract_guardrail_fields_on_success(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        success = [r for r in payload["run_records"] if r["assignment_status"] == "success"]
        assert success
        for rec in success[:5]:
            assert rec["contract_status"] is not None
            assert rec["guardrail_status"] in {"WARN", "BLOCK", "PASS", "UNKNOWN"}

    def test_rerandomization_wrapper_identity(self, fast_cfg: D5DesStatTier1Config) -> None:
        rerand = next(d for d in DESIGN_FAMILIES if d.design_inventory_id == "DES-006")
        ctx = _world_context("balanced_markets", fast_cfg)
        record = run_single(rerand, ctx, seed=555, replicate=0, cfg=fast_cfg)
        if record["assignment_status"] == "success":
            assert record["diagnostics"].get("wrapper_identity") == "Rerandomization"

    def test_json_serializable(self, fast_cfg: D5DesStatTier1Config) -> None:
        from panel_exp.validation.track_d_d5_des_stat_tier1_001 import _json_safe

        payload = build_d5_des_stat_tier1_001(fast_cfg)
        json.dumps(_json_safe(payload))

    def test_atomic_archive_write(self, fast_cfg: D5DesStatTier1Config, tmp_path: Path) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        out = tmp_path / "tier1.json"
        write_artifact_atomic(out, payload, overwrite=True)
        loaded = json.loads(out.read_text())
        assert loaded["artifact_id"] == ARTIFACT_ID

    def test_no_downstream_promotion_claims(self, fast_cfg: D5DesStatTier1Config) -> None:
        payload = build_d5_des_stat_tier1_001(fast_cfg)
        assert payload["governance"]["no_promotion"] is True
        assert payload["guardrail_summary"]["downstream_may_proceed"] is False


class TestD5DesStatTier1CommittedArtifact:
    def test_committed_artifact_if_present(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run full D5-DES-STAT-TIER1-001 generator with --overwrite")
        loaded = json.loads(ARTIFACT_PATH.read_text())
        assert loaded["artifact_id"] == ARTIFACT_ID
        assert loaded["verdict"] in ALLOWED_VERDICTS
        ids = {r["design_inventory_id"] for r in loaded["run_records"]}
        assert len(ids) == 5
