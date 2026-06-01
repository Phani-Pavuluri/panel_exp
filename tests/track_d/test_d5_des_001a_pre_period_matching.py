"""D5-DES-001a characterization tests (research lane)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_des_001a import (
    D5Des001aConfig,
    run_d5_des_001a,
    run_one_replicate,
    synthesize_panel,
    write_artifact,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_DES_001a_results.json"
)


class TestD5Des001aPrePeriodMatching:
    def test_replicate_metrics_finite(self) -> None:
        wide, n_pre = synthesize_panel(
            n_units=12, n_pre=30, n_post=10, seed=1, post_unit_shift_sd=10.0
        )
        m = run_one_replicate(wide, n_pre, seed=1, treatment_probability=0.5)
        assert 0.0 <= m["jaccard_test_sets"] <= 1.0
        assert all(map(lambda k: k in m, ("post_corr_full", "post_corr_pre_only")))

    def test_characterization_runs(self) -> None:
        payload = run_d5_des_001a(D5Des001aConfig(n_mc=24, n_units=16))
        assert payload["artifact_id"] == "D5-DES-001a"
        assert payload["recommendation"] in {
            "fix",
            "restrict",
            "accepted_deviation",
            "continue_investigation",
        }
        assert "primary_metrics" in payload

    def test_write_committed_artifact(self) -> None:
        payload = run_d5_des_001a(D5Des001aConfig())
        write_artifact(payload, ARTIFACT_PATH)
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["recommendation"] == payload["recommendation"]
