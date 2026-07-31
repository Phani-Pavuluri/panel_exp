"""Fresh-process checks for public package import surfaces."""

from __future__ import annotations

import subprocess
import sys


def _run(statement: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", statement], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def test_public_imports_work_in_isolation_and_both_orders() -> None:
    statements = [
        "from panel_exp.artifacts import export_geo_run_bundle; print(export_geo_run_bundle.__name__)",
        "from panel_exp.track_b import build_geo_run_artifact_bundle; print(build_geo_run_artifact_bundle.__name__)",
        "from panel_exp.track_b._registry import CALIBRATION_SIGNAL_BY_CONFIG; print(type(CALIBRATION_SIGNAL_BY_CONFIG).__name__)",
        "from panel_exp import BalancedRandomization; from panel_exp.design.assign import BalancedRandomization as Expected; assert BalancedRandomization is Expected; print(BalancedRandomization.__name__)",
        "from panel_exp.artifacts import export_geo_run_bundle; from panel_exp.track_b import build_geo_run_artifact_bundle; print('artifact-then-track')",
        "from panel_exp.track_b import build_geo_run_artifact_bundle; from panel_exp.artifacts import export_geo_run_bundle; print('track-then-artifact')",
    ]
    assert [_run(statement) for statement in statements] == [
        "export_geo_run_bundle",
        "build_geo_run_artifact_bundle",
        "dict",
        "BalancedRandomization",
        "artifact-then-track",
        "track-then-artifact",
    ]
