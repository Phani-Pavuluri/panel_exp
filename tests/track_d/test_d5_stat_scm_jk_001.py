"""D5-STAT-SCM-JK-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_stat_scm_jk_001 import (
    D5StatScmJk001Config,
    REQUIRED_WORLD_IDS,
    _assign_greedy_pre_period,
    _HISTORICAL_ARCHIVE,
    build_d5_stat_scm_jk_001,
    preserve_historical_archive,
    write_artifact,
)
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from dataclasses import replace

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_SCM_JK_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_SCM_JK_001_REPORT.md"
HARNESS_SOURCE = _REPO / "panel_exp/validation/track_d_d5_stat_scm_jk_001.py"
CORRECTION_REPORT = _REPO / "docs/track_d/D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
    }
)

ALLOWED_HARNESS_VERDICTS = frozenset(
    {
        "scm_jk_harness_corrected_level_consistent_baseline_established",
        "scm_jk_harness_corrected_support_gated_restrictions_remain",
        "scm_jk_harness_corrected_null_monitor_only",
        "scm_jk_harness_correction_inconclusive",
        "scm_jk_harness_correction_failed",
    }
)

AGG_METRIC_KEYS = frozenset(
    {
        "n_replicates",
        "feasible_runs",
        "failed_runs",
        "mean_point_estimate",
        "mean_bias",
        "mean_absolute_error",
        "coverage_level",
        "coverage_fractional_percent",
        "effect_scale_canonical",
        "interval_orientation_failure_rate",
        "negative_half_width_rate",
        "non_finite_output_rate",
    }
)

RUN_FIELD_KEYS = frozenset(
    {
        "world_id",
        "replicate_id",
        "seed",
        "callable_status",
        "point_estimate",
        "true_effect_level",
        "level_effect",
        "fractional_percent_effect",
        "effect_scale_canonical",
        "bias_level",
        "interval_contains_truth_level",
        "interval_contains_truth_fractional_percent",
        "interval_orientation_valid",
        "finite_outputs",
        "n_treated",
        "n_control",
    }
)

FORBIDDEN_REPORT_PHRASES = [
    r"\bproduction-ready\b",
    r"\bpromoted\b",
    r"\btrusted\b",
    r"\bgoverned uncertainty\b",
    r"\bCalibrationSignal eligible\b",
    r"\bMMM ready\b",
    r"\bprimary evidence\b",
    r"\bsecondary evidence\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _fast_cfg() -> D5StatScmJk001Config:
    return D5StatScmJk001Config(fast=True)


@pytest.mark.skipif(cvxpy_osqp_skip_reason() is not None, reason="cvxpy/osqp required")
class TestD5StatScmJk001:
    def test_no_groups_values_geometry_collapse_in_harness(self) -> None:
        text = HARNESS_SOURCE.read_text(encoding="utf-8")
        assert "for u in groups.values()" not in text
        assert "[u for units in groups.values()" not in text

    def test_assignment_explicit_test_and_control(self) -> None:
        scenario = replace(
            RECOVERY_SCENARIO_REGISTRY["scm_low_signal"],
            random_state=1,
            n_geos=16,
            n_periods=44,
            treatment_start=32,
            true_effect=0.0,
        )
        wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
        assignment = _assign_greedy_pre_period(
            wide, n_pre=28, seed=1, treatment_probability=0.35
        )
        assert assignment["n_treated"] > 0
        assert assignment["n_control"] > 0
        assert assignment["n_treated"] + assignment["n_control"] == wide.shape[0]
        assert not set(assignment["treated_units"]) & set(assignment["control_units"])

    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        a = _strip_timestamp(build_d5_stat_scm_jk_001(cfg))
        b = _strip_timestamp(build_d5_stat_scm_jk_001(cfg))
        assert a == b

    def test_required_worlds_exist(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        world_ids = {w["world_id"] for w in payload["worlds"]}
        assert set(REQUIRED_WORLD_IDS) <= world_ids
        assert set(payload["aggregate_metrics"]) >= set(REQUIRED_WORLD_IDS)

    def test_aggregate_metrics_per_world(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        for wid in REQUIRED_WORLD_IDS:
            metrics = payload["aggregate_metrics"][wid]
            assert AGG_METRIC_KEYS <= set(metrics)
            assert metrics["effect_scale_canonical"] == "level_effect"

    def test_run_results_fields(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        assert payload["run_results"]
        for row in payload["run_results"]:
            assert RUN_FIELD_KEYS <= set(row)
            if row.get("callable_status") == "callable_pass":
                assert row["n_treated"] > 0
                assert row["n_control"] >= 4

    def test_level_scale_canonical_coverage(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        pos = payload["aggregate_metrics"]["clean_positive_lift"]
        assert pos["coverage"] == pos["coverage_level"]
        if pos["coverage_fractional_percent"] is not None:
            assert pos["coverage_fractional_percent"] <= pos["coverage_level"] + 0.01

    def test_null_and_positive_coverage_separate(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        summary = payload["summary"]
        assert "null_coverage_level" in summary
        assert "positive_coverage_level" in summary
        assert summary["null_coverage_level"] is not None
        assert summary["positive_coverage_level"] is not None

    def test_failed_runs_preserved(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        failed = [r for r in payload["run_results"] if r["callable_status"] != "callable_pass"]
        assert len(payload["failure_register"]) == len(failed)

    def test_harness_correction_metadata(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        hc = payload["harness_correction"]
        assert hc["correction_artifact_id"] == "D5-STAT-SCM-JK-001-HARNESS-CORRECTION"
        assert hc["historical_evidence_retained"] is True
        assert "groups.values()" in hc["assignment_fix"]
        assert payload["harness_correction_verdict"] in ALLOWED_HARNESS_VERDICTS

    def test_forbidden_flags_false(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        for key, val in payload["forbidden_flags"].items():
            assert val is False, key

    def test_no_interval_orientation_failures(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        for row in payload["run_results"]:
            if row.get("interval_orientation_valid") is False:
                pytest.fail(f"orientation failure in {row['world_id']}")
        for m in payload["aggregate_metrics"].values():
            assert m["interval_orientation_failure_rate"] == 0.0

    def test_no_negative_half_width(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        for row in payload["run_results"]:
            if row.get("negative_half_width_detected"):
                pytest.fail(f"negative half-width in {row['world_id']}")
        for m in payload["aggregate_metrics"].values():
            assert m["negative_half_width_rate"] == 0.0

    def test_overall_verdict_allowed(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        assert payload["overall_verdict"] in ALLOWED_OVERALL

    def test_runtime_modest(self) -> None:
        t0 = time.perf_counter()
        build_d5_stat_scm_jk_001(_fast_cfg())
        elapsed = time.perf_counter() - t0
        assert elapsed < 120.0

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator for report")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT_PHRASES:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_historical_archive_preserved(self) -> None:
        preserve_historical_archive()
        assert _HISTORICAL_ARCHIVE.is_file()

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        cfg = D5StatScmJk001Config(n_replicates=15)
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_scm_jk_001(cfg))
        assert loaded == built

    def test_correction_report_exists(self) -> None:
        assert CORRECTION_REPORT.is_file()


def test_write_artifact(tmp_path: Path) -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip("cvxpy/osqp required")
    out = write_artifact(tmp_path / "scm_jk.json", cfg=_fast_cfg(), overwrite=True)
    assert out.is_file()
