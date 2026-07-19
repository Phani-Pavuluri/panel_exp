import json
from pathlib import Path
ROOT=Path(__file__).parents[2]
DOC=ROOT/'docs/track_d/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_PLAN_001.md'; SUMMARY=ROOT/'docs/track_d/archives/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_PLAN_001_summary.json'
def test_harness_plan_boundaries_and_schemas():
    assert DOC.exists(); data=json.loads(SUMMARY.read_text()); text=DOC.read_text()
    for key in ('harness_runtime_added','selector_runtime_added','production_selector_router_authorized','runtime_execution_added','estimator_behavior_changed','assignment_logic_changed','mip_repository_modified','geox_to_mip_integration_started','production_inference_authorized','assignment_authorized','causal_readout_authorized','calibration_signal_export_authorized','mip_experiment_evidence_export_authorized','trust_report_production_assembly_authorized','decision_surface_authorized','recommendation_contract_authorized','llm_decisioning_authorized','budget_optimization_authorized','multicell_production_claim_authorized','agent_work_authorized','safe_to_authorize_production_selector_router'):
        assert data[key] is False
    for term in ('load_fixtures','validate_fixture_contract','emit_failure_packets','fixture_id','blocked_reasons_match','failure_classification','safe_to_proceed_to_harness_runtime','contract_validation_failure','serialization_failure','SCM candidate','Downstream MIP/CalibrationSignal'):
        assert term in text
