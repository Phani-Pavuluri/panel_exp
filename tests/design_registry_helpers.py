"""Helpers for design registry equivalence tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "design_golden"

# Legacy geo allowlist (must match panel_exp.design.registry.LEGACY_GEO_RUN_DESIGN_SUPPORTED).
LEGACY_GEO_RUN_DESIGN_SUPPORTED = frozenset(
    {
        "greedy_match_markets",
        "thinningdesign",
        "balancedrandomization",
        "completerandomization",
        "stratifiedrandomization",
    }
)

LEGACY_ASSIGNMENT_GROUP_LABELS = ("control", "test_0")

LEGACY_MDE_PRC_COLUMNS = frozenset(
    {
        "4wk_percent",
        "control_dmas",
        "test_dmas",
        "test_prc",
        "control_prc",
    }
)

LEGACY_MDE_VAL_COLUMNS = frozenset(
    {
        "4wk_val",
        "control_dmas",
        "test_dmas",
        "test_prc",
        "control_prc",
    }
)


def make_geo_panel(seed: int = 42, n_units: int = 12, n_times: int = 50) -> PanelDataset:
    rng = np.random.default_rng(seed)
    units = [f"u{i}" for i in range(n_units)]
    cols = list(range(n_times))
    wide = pd.DataFrame(
        rng.uniform(50, 200, (n_units, n_times)), index=units, columns=cols
    )
    return PanelDataset(wide)


def assignment_to_golden_payload(assignment: dict) -> dict:
    """Serialize assignment with explicit group labels and per-group unit lists."""
    assignments = {k: sorted(v) for k, v in assignment.items()}
    group_labels = sorted(assignments.keys())
    return {
        "group_labels": group_labels,
        "assignments": assignments,
    }


def save_assignment(path: Path, assignment: dict) -> None:
    path.write_text(json.dumps(assignment_to_golden_payload(assignment), sort_keys=True, indent=2))


def load_assignment(path: Path) -> dict:
    payload = json.loads(path.read_text())
    if "group_labels" in payload and "assignments" in payload:
        labels = payload["group_labels"]
        assignments = payload["assignments"]
        assert set(labels) == set(assignments.keys()), (
            f"group_labels {labels} != assignment keys {list(assignments.keys())}"
        )
        return assignments
    # Legacy flat dict (keys only)
    return payload


def assert_assignment_group_labels(assignment: dict, n_test_grps: int = 1) -> None:
    assert "control" in assignment
    for i in range(n_test_grps):
        assert f"test_{i}" in assignment
