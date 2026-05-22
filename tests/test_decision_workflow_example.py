"""Smoke test for examples/decision_workflow_example.py."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_decision_workflow_example_runs():
    from examples.decision_workflow_example import run_decision_workflow

    t0 = time.perf_counter()
    result = run_decision_workflow(seed=0)
    elapsed = time.perf_counter() - t0
    assert elapsed < 30.0

    assert result["card_markdown"]
    assert "# Experiment Card" in result["card_markdown"]
    assert result["calibration_report"]
    assert "false_positive_rate" in result["calibration_report"]
    assert result["maturity_evidence"]
    assert result["maturity_evidence"]["estimator_name"] == "TBRRidge"
    assert result["readiness_assessment"]
    assert result["readiness_assessment"]["status"]


def test_decision_workflow_script_entrypoint():
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "examples" / "decision_workflow_example.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "# Experiment Card" in proc.stdout
