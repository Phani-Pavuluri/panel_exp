"""D5-STAT-DID-BOOTSTRAP-001 tests."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import (
    D5StatDidBootstrap001Config,
    REQUIRED_WORLD_IDS,
    build_d5_stat_did_bootstrap_001,
    write_artifact,
)

_REPO = Path(__file__).resolve().parents[2]
ARTIFACT = _REPO / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"
REPORT = _REPO / "docs/track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md"

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
        "median_point_estimate",
        "mean_true_effect",
        "mean_bias",
        "mean_absolute_error",
        "rmse",
        "median_absolute_error",
        "sign_error_rate",
        "null_false_positive_rate",
        "coverage",
        "mean_interval_width",
        "median_interval_width",
        "interval_orientation_failure_rate",
        "negative_half_width_rate",
        "degenerate_interval_rate",
        "non_finite_output_rate",
        "notes",
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
        "interval_lower",
        "interval_upper",
        "interval_width",
        "interval_contains_truth",
        "interval_orientation_valid",
        "negative_half_width_detected",
        "finite_outputs",
        "exception_type",
        "exception_message",
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


def _fast_cfg() -> D5StatDidBootstrap001Config:
    return D5StatDidBootstrap001Config(n_replicates=2)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_stat_did_bootstrap_001(_fast_cfg())


class TestD5StatDidBootstrap001:
    def test_build_deterministic_excluding_timestamp(self) -> None:
        cfg = _fast_cfg()
        assert _strip_timestamp(build_d5_stat_did_bootstrap_001(cfg)) == _strip_timestamp(
            build_d5_stat_did_bootstrap_001(cfg)
        )

    def test_required_worlds_exist(self, fast_payload: dict) -> None:
        assert set(REQUIRED_WORLD_IDS) <= {w["world_id"] for w in fast_payload["worlds"]}
        assert set(REQUIRED_WORLD_IDS) <= set(fast_payload["aggregate_metrics"])

    def test_aggregate_metrics_per_world(self, fast_payload: dict) -> None:
        for wid in REQUIRED_WORLD_IDS:
            assert AGG_KEYS <= set(fast_payload["aggregate_metrics"][wid])

    def test_run_results_fields(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert RUN_KEYS <= set(row)

    def test_forbidden_flags_false(self, fast_payload: dict) -> None:
        for key, val in fast_payload["forbidden_flags"].items():
            assert val is False, key

    def test_interval_orientation_sane(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            lo = row.get("interval_lower")
            hi = row.get("interval_upper")
            if lo is not None and hi is not None:
                assert lo <= hi, row

    def test_no_negative_half_width(self, fast_payload: dict) -> None:
        for row in fast_payload["run_results"]:
            assert row.get("negative_half_width_detected") is not True

    def test_non_finite_rate_tracked(self, fast_payload: dict) -> None:
        for m in fast_payload["aggregate_metrics"].values():
            assert "non_finite_output_rate" in m

    def test_overall_verdict_allowed(self, fast_payload: dict) -> None:
        assert fast_payload["overall_verdict"] in ALLOWED_OVERALL

    def test_report_guardrail_wording(self) -> None:
        if not REPORT.is_file():
            pytest.skip("Run generator")
        text = REPORT.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_REPORT:
            assert re.search(pattern, text, re.I) is None, pattern

    def test_runtime_modest(self) -> None:
        t0 = time.perf_counter()
        build_d5_stat_did_bootstrap_001(_fast_cfg())
        assert time.perf_counter() - t0 < 180.0

    def test_committed_artifact_matches_build(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run generator")
        cfg = D5StatDidBootstrap001Config(n_replicates=15)
        loaded = _strip_timestamp(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        built = _strip_timestamp(build_d5_stat_did_bootstrap_001(cfg))
        assert loaded == built


def test_write_artifact(tmp_path: Path) -> None:
    assert write_artifact(tmp_path / "did.json", cfg=_fast_cfg()).is_file()
