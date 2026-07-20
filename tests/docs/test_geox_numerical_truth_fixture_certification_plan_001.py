import json
from pathlib import Path
ROOT=Path(__file__).parents[2]; DOC=ROOT/'docs/track_d/GEOX_NUMERICAL_TRUTH_FIXTURE_CERTIFICATION_PLAN_001.md'; SUMMARY=ROOT/'docs/track_d/archives/GEOX_NUMERICAL_TRUTH_FIXTURE_CERTIFICATION_PLAN_001_summary.json'
def test_certification_plan_boundaries_and_content():
    text=DOC.read_text(); data=json.loads(SUMMARY.read_text()); assert DOC.exists()
    for k,v in data.items():
        if k.endswith('_authorized') or k.endswith('_added') and k in {'fixture_generator_added','readout_artifact_runtime_added','package_entrypoint_added','estimator_execution_added','assignment_logic_changed','calibration_adapter_added','production_selector_runtime_added'}: assert v is False
    for term in ('quarterly planning with experiment-informed budget reallocation','known_lift_absolute','expected_confidence_interval','certified','MIP handoff','D6 Gate 1','safe blocked readout packet','calibration-incompatible result'): assert term in text
    assert data['decision']=='PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_CONTRACT'
