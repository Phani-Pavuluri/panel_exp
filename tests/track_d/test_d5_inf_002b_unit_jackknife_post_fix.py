"""D5-INF-002b post-fix validation tests (INV-D3-001)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inf_002a import write_artifact
from panel_exp.validation.track_d_d5_inf_002b import D5Inf002bConfig, run_d5_inf_002b

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INF_002b_results.json"
)


class TestD5Inf002bPostFix:
    def test_post_fix_characterization_runs(self) -> None:
        payload = run_d5_inf_002b(D5Inf002bConfig(n_mc=6, scenarios=("scm_low_signal",)))
        assert payload["artifact_id"] == "D5-INF-002b"
        assert payload["inv_d3_001_fix_applied"] is True
        assert payload["recommendation"] in {
            "accepted_deviation",
            "characterization_required",
            "restricted",
            "regression_open_inv",
        }

    def test_committed_artifact_if_present(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-INF-002b generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["inv_d3_001_fix_applied"] is True
        assert loaded["inv_d3_001_disposition"] in {
            "fix_accepted",
            "characterization_required",
            "continue_investigation",
        }
