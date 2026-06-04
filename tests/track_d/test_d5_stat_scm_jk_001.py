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
    build_d5_stat_scm_jk_001,
    write_artifact,
)
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_SCM_JK_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_SCM_JK_001_REPORT.md"

ALLOWED_OVERALL = frozenset(
    {
        "characterization_pass_with_caveats",
        "characterization_mixed_requires_followup",
        "characterization_fail_requires_fix",
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
        "true_effect",
        "bias",
        "absolute_error",
        "interval_orientation_valid",
        "finite_outputs",
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
    return D5StatScmJk001Config(n_replicates=4)


@pytest.mark.skipif(cvxpy_osqp_skip_reason() is not None, reason="cvxpy/osqp required")
class TestD5StatScmJk001:
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

    def test_run_results_fields(self) -> None:
        payload = build_d5_stat_scm_jk_001(_fast_cfg())
        assert payload["run_results"]
        for row in payload["run_results"]:
            assert RUN_FIELD_KEYS <= set(row)

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

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        cfg = D5StatScmJk001Config(n_replicates=15)
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_scm_jk_001(cfg))
        assert loaded == built


def test_write_artifact(tmp_path: Path) -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip("cvxpy/osqp required")
    out = write_artifact(tmp_path / "scm_jk.json", cfg=_fast_cfg())
    assert out.is_file()
