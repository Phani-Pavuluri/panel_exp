"""Tests for PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.panel_exp_artifact_registry_and_provenance_contract_001 import (
    ARTIFACT_TYPE_TAXONOMY,
    GOVERNANCE_STATUSES,
    LIFECYCLE_STATES,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_CONTRACTS,
    REVISED_ROADMAP_SEQUENCE,
    SCENARIO_TESTS,
    _AUTH_FLAGS,
    build_panel_exp_artifact_registry_provenance_contract,
    build_scenarios,
    run_validation,
    validate_panel_exp_artifact_registry_provenance_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001_REPORT.md"


def test_registry_first_principles() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    assert contract.registry_first_provenance_always
    assert contract.no_artifact_id_no_durable_claim
    assert contract.no_provenance_no_downstream_use
    assert contract.no_validation_status_no_validation_claim
    assert contract.no_governance_status_no_claim_boundary
    assert contract.no_allowed_downstream_use_no_downstream_routing


def test_required_contracts() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    assert contract.required_contracts == REQUIRED_CONTRACTS
    assert "PanelExpArtifactRegistryEntry" in contract.required_contracts
    assert "PanelExpArtifactProvenance" in contract.required_contracts
    assert "PanelExpArtifactDownstreamUsePolicy" in contract.required_contracts


def test_taxonomy_lifecycle_and_governance() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    assert contract.artifact_type_taxonomy == ARTIFACT_TYPE_TAXONOMY
    assert contract.lifecycle_states == LIFECYCLE_STATES
    assert contract.governance_statuses == GOVERNANCE_STATUSES
    assert "validated" in contract.lifecycle_states
    assert "diagnostic_only" in contract.governance_statuses


def test_revised_roadmap_sequence() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    assert contract.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001")
    assert contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT


def test_all_authorization_flags_false() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_panel_exp_artifact_registry_provenance_contract()
    result = validate_panel_exp_artifact_registry_provenance_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["registry_first_provenance_always"] is True
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert (
        data["final_verdict"]
        == "panel_exp_artifact_registry_provenance_contract_defined_no_runtime_authorization"
    )


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "registry-first" in text.lower() or "registry first" in text.lower()
    assert "provenance" in text.lower()
    assert len(SCENARIO_TESTS) >= 20
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
