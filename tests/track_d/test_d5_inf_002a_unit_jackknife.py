"""D5-INF-002a — SCM Unit Jackknife LOO target characterization tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inf_002a import (
    D5Inf002aConfig,
    run_d5_inf_002a,
    run_one_replicate,
    unit_jk_literature_reference,
    write_artifact,
)
from panel_exp.inference.unit_jackknife import unit_jk
from panel_exp.methods.scm import SyntheticControl

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INF_002a_results.json"
)


class TestD5Inf002aUnitJackknife:
    def test_reference_runs_on_synthetic_panel(self) -> None:
        scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
        panel = SyntheticWorld.generate(scenario).to_panel_dataset()
        ref = unit_jk_literature_reference(panel, SyntheticControl, alpha=0.05)
        prod = unit_jk(panel, SyntheticControl, variation=1, alpha=0.05)
        assert np.shape(ref) == np.shape(prod)
        assert np.all(np.isfinite(ref))

    def test_replicate_metrics_finite(self) -> None:
        scenario = RECOVERY_SCENARIO_REGISTRY["scm_low_signal"]
        panel = SyntheticWorld.generate(scenario).to_panel_dataset()
        m = run_one_replicate(
            panel,
            alpha=0.05,
            treated_post_noise_sd=30.0,
            control_post_noise_sd=30.0,
            seed=42,
        )
        assert np.isfinite(m["post_hw_production"])
        assert np.isfinite(m["post_hw_reference"])

    def test_characterization_runs(self) -> None:
        payload = run_d5_inf_002a(
            D5Inf002aConfig(n_mc=6, scenarios=("scm_low_signal",))
        )
        assert payload["artifact_id"] == "D5-INF-002a"
        assert payload["recommendation"] in {
            "accepted_deviation",
            "characterization_required",
            "restricted",
            "open_inv_d3_001",
            "continue_investigation",
        }
        assert payload["n_replicates"] >= 1
        assert payload["calibration_eligibility_changed"] is False

    def test_committed_artifact_matches_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-INF-002a generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-INF-002a"
        assert loaded["recommendation"] in {
            "accepted_deviation",
            "characterization_required",
            "restricted",
            "open_inv_d3_001",
            "continue_investigation",
        }
