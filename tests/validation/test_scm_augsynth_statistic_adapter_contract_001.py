"""Tests for SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001 validation harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_augsynth_statistic_adapter_contract_001 import (
    NEXT_ARTIFACT,
    run_scm_augsynth_statistic_adapter_contract_harness,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_scm_augsynth_statistic_adapter_contract_harness()
    assert summary["failed_scenarios"] == []
    assert summary["verdict"] == (
        "scm_augsynth_statistic_adapter_contract_defined_no_downstream_authorization"
    )


def test_readiness_matrix_rows() -> None:
    summary = run_scm_augsynth_statistic_adapter_contract_harness()
    assert summary["readiness_matrix_rows"] >= 5


def test_authorization_flags_false() -> None:
    summary = run_scm_augsynth_statistic_adapter_contract_harness()
    for key in (
        "production_p_value_authorized",
        "causal_confidence_interval_authorized",
        "trustreport_authorized",
        "calibration_signal_allowed",
    ):
        assert summary[key] is False


def test_recommended_next_artifact() -> None:
    summary = run_scm_augsynth_statistic_adapter_contract_harness()
    assert summary["recommended_next_artifact"] == NEXT_ARTIFACT


def test_summary_json_flags_false() -> None:
    if not _SUMMARY.exists():
        return
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["production_p_value_authorized"] is False
