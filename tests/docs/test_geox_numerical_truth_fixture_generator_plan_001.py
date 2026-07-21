import json
from pathlib import Path
ROOT=Path(__file__).parents[2]; DOC=ROOT/'docs/track_d/GEOX_NUMERICAL_TRUTH_FIXTURE_GENERATOR_PLAN_001.md'; SUMMARY=ROOT/'docs/track_d/archives/GEOX_NUMERICAL_TRUTH_FIXTURE_GENERATOR_PLAN_001_summary.json'
IDS=['geox_truth_scm_candidate_clean_001','geox_truth_did_candidate_warning_001','geox_truth_infeasible_preperiod_001','geox_truth_weak_matchability_001','geox_truth_unsupported_inference_001','geox_truth_tbrridge_diagnostic_only_001','geox_truth_bayesian_tbr_research_only_001','geox_truth_stale_incompatible_evidence_001','geox_truth_conflicting_evidence_001','geox_truth_multicell_shared_control_block_001','geox_truth_calibration_incompatible_001','geox_truth_safe_blocked_readout_001']
def test_generator_plan_content_and_boundaries():
    text=DOC.read_text(); data=json.loads(SUMMARY.read_text()); assert DOC.exists() and all(i in text for i in IDS)
    for term in ('input_panel.csv','truth.json','expected_readout.json','replay.json','idempotent','build_geox_numerical_truth_fixture_artifacts','Validation plan','MIP handoff','D6 Gate 1'): assert term in text
    for k,v in data.items():
        if k.endswith('_authorized') or k in {'fixture_files_created','fixture_datasets_created','fixture_generator_added','readout_artifact_runtime_added','package_entrypoint_added','estimator_execution_added','calibration_adapter_added','production_selector_runtime_added'}: assert v is False
    assert data['decision']=='PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_DATASET_GENERATOR'
