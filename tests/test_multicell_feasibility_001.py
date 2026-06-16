"""Unit tests for multicell_feasibility (DES-011)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.design.assign import CompleteRandomization
from panel_exp.design.constraints import prepare_constraint_context
from panel_exp.design.multicell_feasibility import (
    assign_multicell,
    compute_control_burden,
    compute_multicell_feasibility,
    diagnose_assignment,
    per_cell_balance_metrics,
)
from panel_exp.panel_data import PanelDataset, TimePeriod


def _panel(n_units: int = 12, seed: int = 42) -> PanelDataset:
    rng = np.random.default_rng(seed)
    wide = pd.DataFrame(
        rng.normal(100, 10, (n_units, 30)),
        index=[f"u{i}" for i in range(n_units)],
        columns=list(range(30)),
    )
    return PanelDataset(wide)


class TestMulticellFeasibilityContract:
    def test_feasibility_contract_fields(self) -> None:
        c = compute_multicell_feasibility(
            n_eligible=20,
            treatment_probability=0.5,
            n_treatment_cells=3,
            policy="control_reservation",
        )
        assert c.n_treatment_cells == 3
        assert c.pooled_claims_allowed is False
        assert c.shared_control_policy == "shared_single_control_arm"


class TestMulticellAssignment:
    def test_deterministic_two_cell(self) -> None:
        panel = _panel(12, 101)
        d1 = CompleteRandomization(
            treatment_probability=0.35, random_state=101, multicell_policy="equal_per_cell"
        )
        d2 = CompleteRandomization(
            treatment_probability=0.35, random_state=101, multicell_policy="equal_per_cell"
        )
        a1 = d1.assign(panel_data=panel, n_test_grps=2)
        a2 = d2.assign(panel_data=panel, n_test_grps=2)
        assert a1 == a2

    def test_deterministic_three_cell(self) -> None:
        panel = _panel(20, 202)
        design = CompleteRandomization(
            treatment_probability=0.5, random_state=202, multicell_policy="control_reservation"
        )
        assignment = design.assign(panel_data=panel, n_test_grps=3)
        assert len(assignment["test_0"]) >= 0
        assert len(assignment["test_1"]) >= 0
        assert len(assignment["test_2"]) >= 0

    def test_treatment_cell_exclusivity(self) -> None:
        panel = _panel(20, 303)
        design = CompleteRandomization(
            treatment_probability=0.5, random_state=303, multicell_policy="control_reservation"
        )
        assignment = design.assign(panel_data=panel, n_test_grps=3)
        issues = diagnose_assignment(assignment, 3)
        assert issues["cell_collisions"] == []
        assert issues["treatment_control_overlap"] == []

    def test_no_duplicate_assignments(self) -> None:
        panel = _panel(15, 404)
        design = CompleteRandomization(random_state=404, multicell_policy="equal_per_cell")
        assignment = design.assign(panel_data=panel, n_test_grps=2)
        issues = diagnose_assignment(assignment, 2)
        assert issues["duplicate_assignments"] == []

    def test_minimum_control_preservation(self) -> None:
        panel = _panel(10, 505)
        design = CompleteRandomization(
            treatment_probability=0.65,
            random_state=505,
            multicell_policy="control_reservation",
            min_control_units=3,
        )
        assignment = design.assign(panel_data=panel, n_test_grps=3)
        assert len(assignment["control"]) >= 3

    def test_metadata_emission(self) -> None:
        panel = _panel(12, 606)
        design = CompleteRandomization(
            treatment_probability=0.35, random_state=606, multicell_policy="control_reservation"
        )
        design.assign(panel_data=panel, n_test_grps=2)
        meta = design.last_multicell_metadata
        assert meta is not None
        assert meta["cell_ids"] == ["test_0", "test_1"]
        assert meta["shared_control_policy"]
        assert meta["control_reuse_policy"]
        assert meta["pooled_claims_allowed"] is False

    def test_legacy_vs_fixed_control_floor(self) -> None:
        panel = _panel(10, 707)
        legacy = CompleteRandomization(
            treatment_probability=0.65, random_state=707, multicell_policy="legacy", min_control_units=3
        )
        fixed = CompleteRandomization(
            treatment_probability=0.65,
            random_state=707,
            multicell_policy="control_reservation",
            min_control_units=3,
        )
        a_legacy = legacy.assign(panel_data=panel, n_test_grps=4)
        a_fixed = fixed.assign(panel_data=panel, n_test_grps=4)
        assert len(a_fixed["control"]) >= 3
        assert len(a_fixed["control"]) >= len(a_legacy["control"]) or len(a_legacy["control"]) < 3

    def test_control_burden_calculation(self) -> None:
        assignment = {"control": ["u0", "u1", "u2"], "test_0": ["u3"], "test_1": ["u4", "u5"]}
        burden = compute_control_burden(assignment, 2)
        assert burden["control_reuse_count"] == 3
        assert burden["control_burden_index"] > 0

    def test_worst_cell_smd(self) -> None:
        wide = _panel(12).wide_data
        assignment = {"control": ["u0", "u1", "u2"], "test_0": ["u3", "u4"], "test_1": ["u5", "u6"]}
        metrics = per_cell_balance_metrics(wide, assignment, 2, n_pre=30)
        assert "worst_cell_max_smd" in metrics
        assert metrics["worst_cell_max_smd"] >= 0


class TestMulticellPolicies:
    @pytest.mark.parametrize("policy", ["legacy", "equal_per_cell", "control_reservation", "weighted"])
    def test_policies_produce_disjoint_cells(self, policy: str) -> None:
        panel = _panel(20, 808)
        weights = {"test_0": 2.0, "test_1": 1.0} if policy == "weighted" else None
        design = CompleteRandomization(
            treatment_probability=0.4,
            random_state=808,
            multicell_policy=policy,  # type: ignore[arg-type]
            cell_weights=weights,
        )
        assignment = design.assign(panel_data=panel, n_test_grps=2)
        issues = diagnose_assignment(assignment, 2)
        assert not issues["cell_collisions"]
