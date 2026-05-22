"""Smoke test for examples/readiness_profile_comparison.py."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_compare_profiles_returns_three_profiles():
    from examples.readiness_profile_comparison import compare_readiness_profiles

    t0 = time.perf_counter()
    summaries = compare_readiness_profiles()
    elapsed = time.perf_counter() - t0
    assert elapsed < 5.0
    assert len(summaries) == 3
    names = {row["profile"] for row in summaries}
    assert names == {"exploratory", "standard", "strict"}
    for row in summaries:
        assert row["status"]
        assert isinstance(row["reasons"], list)
        assert isinstance(row["recommended_actions"], list)


def test_profiles_can_differ_on_borderline_calibration():
    from examples.readiness_profile_comparison import compare_readiness_profiles

    summaries = compare_readiness_profiles()
    by_name = {row["profile"]: row["status"] for row in summaries}
    assert by_name["exploratory"] != by_name["strict"] or by_name["standard"] != by_name["strict"]


def test_script_entrypoint():
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "examples" / "readiness_profile_comparison.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "exploratory" in proc.stdout
    assert "standard" in proc.stdout
    assert "strict" in proc.stdout

