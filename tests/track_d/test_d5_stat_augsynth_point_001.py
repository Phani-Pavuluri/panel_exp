"""D5-STAT-AUGSYNTH-POINT-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_stat_augsynth_point_001 import (
    D5StatAugSynthPoint001Config,
    REQUIRED_WORLD_IDS,
    build_d5_stat_augsynth_point_001,
    write_artifact,
)

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
    }
)

AGG_KEYS = frozenset(
    {
        "n_replicates",
        "feasible_runs",
        "failed_runs",
        "callable_failure_rate",
        "mean_point_estimate",
        "mean_bias",
        "mean_absolute_error",
        "rmse",
        "null_false_positive_directional_rate",
        "point_recovery_ratio_mean",
        "non_finite_output_rate",
    }
)

RUN_KEYS = frozenset(
    {
        "world_id",
        "replicate_id",
        "seed",
        "callable_status",
        "point_estimate",
        "true_effect",
        "bias",
        "absolute_error",
        "squared_error",
        "sign_correct",
        "finite_outputs",
        "interval_present",
        "interval_validation_applicable",
    }
)

FORBIDDEN_REPORT = [
    r"\bis production-ready\b",
    r"\bis promoted\b",
    r"\bis trusted\b",
    r"\bgoverned uncertainty eligible\b",
    r"\bCalibrationSignal eligible\b",
    r"\bMMM ready for production\b",
    r"\bprimary evidence role\b",
    r"\bsecondary evidence role\b",
    r"\bis suitable for production\b",
]


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def _fast_cfg() -> D5StatAugSynthPoint001Config:
    return D5StatAugSynthPoint001Config(n_replicates=4)


@pytest.mark.skipif(cvxpy_osqp_skip_reason() is not None, reason="cvxpy/osqp required")
class TestD5StatAugSynthPoint001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        assert _strip_timestamp(build_d5_stat_augsynth_point_001(cfg)) == _strip_timestamp(
            build_d5_stat_augsynth_point_001(cfg)
        )

    def test_required_worlds_exist(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        assert set(REQUIRED_WORLD_IDS) <= {w["world_id"] for w in payload["worlds"]}
        assert set(REQUIRED_WORLD_IDS) <= set(payload["aggregate_metrics"])

    def test_aggregate_metrics_per_world(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        for wid in REQUIRED_WORLD_IDS:
            assert AGG_KEYS <= set(payload["aggregate_metrics"][wid])

    def test_run_results_fields(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        for row in payload["run_results"]:
            assert RUN_KEYS <= set(row)

    def test_forbidden_flags_false(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        for key, val in payload["forbidden_flags"].items():
            assert val is False, key

    def test_interval_not_applicable(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        for row in payload["run_results"]:
            assert row["interval_present"] is False
            assert row["interval_validation_applicable"] is False

    def test_non_finite_rate_tracked(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        for m in payload["aggregate_metrics"].values():
            assert "non_finite_output_rate" in m

    def test_overall_verdict_allowed(self) -> None:
        payload = build_d5_stat_augsynth_point_001(_fast_cfg())
        assert payload["overall_verdict"] in ALLOWED_OVERALL

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_runtime_modest(self) -> None:
        t0 = time.perf_counter()
        build_d5_stat_augsynth_point_001(_fast_cfg())
        assert time.perf_counter() - t0 < 180.0

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        cfg = D5StatAugSynthPoint001Config(n_replicates=15)
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_augsynth_point_001(cfg))
        assert loaded == built


def test_write_artifact(tmp_path: Path) -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip("cvxpy/osqp required")
    assert write_artifact(tmp_path / "augsynth.json", cfg=_fast_cfg()).is_file()
