"""Tests for MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001."""

from __future__ import annotations

from pathlib import Path

import pytest

from panel_exp.validation.multicell_decision_policy_contract_001 import (
    CONTRACT_ID,
    CellRelationship,
    DecisionPolicy,
    SharedControlPolicy,
    contract_metadata,
    derive_multicell_decision_requirements,
    validate_multicell_decision_policy,
)

_REPO = Path(__file__).resolve().parents[2]
DOC = _REPO / "docs/MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md"


def test_enum_values_stable():
    assert [e.value for e in CellRelationship] == [
        "SINGLE_CELL",
        "PARALLEL_MARGINAL_CELLS",
        "COMPETING_CELLS",
        "POOLED_COMPONENT_CELLS",
        "UNKNOWN",
    ]
    assert [e.value for e in DecisionPolicy] == [
        "REPORT_EACH_CELL_ONLY",
        "DECLARE_ANY_CELL_SUCCESS",
        "SELECT_OR_RANK_CELLS",
        "POOL_CELLS",
    ]


def test_platform_marginal_allows_per_cell_reporting():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        shared_control_policy=SharedControlPolicy.COMMON_CONTROL,
    )
    assert req.marginal_per_cell_readout_allowed is True
    assert "marginal_per_cell_causal_claim" in req.allowed_claims
    assert req.multiplicity_required is False


def test_platform_marginal_blocks_winner_selection():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert "winner_selection" in req.blocked_claims
    assert "rank_order_decision" in req.blocked_claims
    assert req.cross_cell_selection_allowed is False


def test_platform_marginal_blocks_any_cell_success():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert "any_cell_success" in req.blocked_claims
    assert req.global_success_claim_allowed is False


def test_platform_marginal_blocks_pooled_readout():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert req.pooled_readout_allowed is False
    assert "pooled_multi_cell_causal_claim" in req.blocked_claims


def test_common_control_requires_shared_control_warning():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        shared_control_policy=SharedControlPolicy.COMMON_CONTROL,
    )
    assert req.shared_control_warning_required is True
    assert "dependent evidence streams" in req.readout_label


def test_disjoint_control_no_shared_warning_by_policy():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        shared_control_policy=SharedControlPolicy.DISJOINT_CONTROL,
    )
    assert req.shared_control_warning_required is False


def test_competing_cells_report_only_descriptive_marginal():
    req = derive_multicell_decision_requirements(
        CellRelationship.COMPETING_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert req.multiplicity_required is False
    assert req.selection_adjustment_required is True
    assert req.marginal_per_cell_readout_allowed is True
    assert "marginal_per_cell_descriptive_display" in req.allowed_claims
    assert req.cross_cell_selection_allowed is False


def test_competing_cells_select_rank_requires_multiplicity():
    req = derive_multicell_decision_requirements(
        CellRelationship.COMPETING_CELLS,
        DecisionPolicy.SELECT_OR_RANK_CELLS,
    )
    assert req.multiplicity_required is True
    assert req.selection_adjustment_required is True
    assert req.cross_cell_selection_allowed is False
    assert "selection-aware inference" in req.readout_label


def test_competing_cells_any_cell_success_requires_multiplicity():
    req = derive_multicell_decision_requirements(
        CellRelationship.COMPETING_CELLS,
        DecisionPolicy.DECLARE_ANY_CELL_SUCCESS,
    )
    assert req.multiplicity_required is True
    assert req.global_success_claim_allowed is False
    assert "any_cell_success" in req.blocked_claims


def test_pooled_component_requires_pooled_estimand():
    req = derive_multicell_decision_requirements(
        CellRelationship.POOLED_COMPONENT_CELLS,
        DecisionPolicy.POOL_CELLS,
    )
    assert req.pooled_estimand_required is True
    assert req.pooled_readout_allowed is False
    assert "pooled inference" in req.readout_label.lower()


def test_pooled_component_allows_pooled_readout_with_inference():
    req = derive_multicell_decision_requirements(
        CellRelationship.POOLED_COMPONENT_CELLS,
        DecisionPolicy.POOL_CELLS,
        has_pooled_inference=True,
    )
    assert req.pooled_readout_allowed is True


def test_unknown_fails_closed():
    req = derive_multicell_decision_requirements(
        CellRelationship.UNKNOWN,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert req.diagnostic_only is True
    assert req.fail_closed is True
    assert req.marginal_per_cell_readout_allowed is False


def test_invalid_single_cell_select_rank_fails_closed():
    req = derive_multicell_decision_requirements(
        CellRelationship.SINGLE_CELL,
        DecisionPolicy.SELECT_OR_RANK_CELLS,
    )
    assert req.invalid_combination is True
    assert req.diagnostic_only is True


@pytest.mark.parametrize(
    "policy",
    [
        DecisionPolicy.DECLARE_ANY_CELL_SUCCESS,
        DecisionPolicy.POOL_CELLS,
    ],
)
def test_invalid_single_cell_policies_fail_closed(policy: DecisionPolicy):
    req = derive_multicell_decision_requirements(CellRelationship.SINGLE_CELL, policy)
    assert req.invalid_combination is True


def test_allowed_blocked_claims_deterministic():
    a = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        shared_control_policy=SharedControlPolicy.COMMON_CONTROL,
    )
    b = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        shared_control_policy=SharedControlPolicy.COMMON_CONTROL,
    )
    assert a.allowed_claims == b.allowed_claims
    assert a.blocked_claims == b.blocked_claims


def test_trustreport_global_decision_blocked():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        has_corrected_multiplicity_inference=True,
    )
    assert req.trustreport_global_decision_allowed is False
    meta = contract_metadata()
    assert meta["trust_report_authorized"] is False
    assert meta["trust_report_ready"] is False


def test_validate_blocks_requested_claim():
    result = validate_multicell_decision_policy(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
        requested_claims=("winner_selection",),
    )
    assert result["valid"] is False
    assert any("winner_selection" in v for v in result["violations"])


def test_segment_marginal_example():
    req = derive_multicell_decision_requirements(
        CellRelationship.PARALLEL_MARGINAL_CELLS,
        DecisionPolicy.REPORT_EACH_CELL_ONLY,
    )
    assert req.multiplicity_required is False
    assert "winner_selection" in req.blocked_claims
    assert "any_cell_success" in req.blocked_claims


def test_spend_level_competing_arm_example():
    req = derive_multicell_decision_requirements(
        CellRelationship.COMPETING_CELLS,
        DecisionPolicy.SELECT_OR_RANK_CELLS,
        shared_control_policy=SharedControlPolicy.COMMON_CONTROL,
    )
    assert req.multiplicity_required is True
    assert req.selection_adjustment_required is True
    assert req.cross_cell_selection_allowed is False


def test_docs_mention_dcm006_and_no_trustreport():
    assert DOC.is_file(), "contract doc must exist"
    text = DOC.read_text()
    assert "DCM-006" in text
    assert "does not authorize TrustReport" in text or "not authorize TrustReport" in text
    assert CONTRACT_ID in text
