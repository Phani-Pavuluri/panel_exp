import json
from pathlib import Path
ROOT=Path(__file__).parents[2]; DOC=ROOT/'docs/track_d/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_PLAN_001.md'; SUMMARY=ROOT/'docs/track_d/archives/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_PLAN_001_summary.json'
def test_policy_plan_boundaries_and_rules():
    text=DOC.read_text(); data=json.loads(SUMMARY.read_text()); assert DOC.exists()
    for k,v in data.items():
        if k.endswith('_authorized') or k in {'policy_adapter_runtime_added','harness_runtime_changed','production_selector_runtime_added','estimator_execution_added','estimator_behavior_changed','assignment_logic_changed','mip_repository_modified','geox_to_mip_integration_started'}: assert v is False
    for term in ('shadow_eligible_candidate','missing_release_gate','shadow_validation_only','next-best alternatives','policy_unknown_method_family','Downstream MIP/CalibrationSignal'): assert term in text
