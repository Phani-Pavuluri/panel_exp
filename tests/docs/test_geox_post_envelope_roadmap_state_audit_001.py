import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
DOC = ROOT / "docs/track_d/GEOX_POST_ENVELOPE_ROADMAP_STATE_AUDIT_001.md"
SUMMARY = ROOT / "docs/track_d/archives/GEOX_POST_ENVELOPE_ROADMAP_STATE_AUDIT_001_summary.json"


def test_audit_summary_and_boundaries():
    assert DOC.exists() and SUMMARY.exists()
    data = json.loads(SUMMARY.read_text())
    assert data["roadmap_audit_only"] is True
    for key in ("runtime_code_changed", "mip_repository_modified", "geox_to_mip_integration_started", "production_inference_authorized", "assignment_authorized", "causal_readout_authorized", "calibration_signal_export_authorized", "mip_experiment_evidence_export_authorized", "trust_report_production_assembly_authorized", "decision_surface_authorized", "recommendation_contract_authorized", "llm_decisioning_authorized", "budget_optimization_authorized", "selector_router_production_authorized", "multicell_production_claim_authorized", "agent_work_authorized"):
        assert data[key] is False
    assert data["decision"] == "PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_PLAN"
    assert "Candidate next-lane evaluation" in DOC.read_text()
