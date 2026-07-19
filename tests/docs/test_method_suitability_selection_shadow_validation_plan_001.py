import json
from pathlib import Path

ROOT=Path(__file__).parents[2]
DOC=ROOT/'docs/track_d/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_PLAN_001.md'
SUMMARY=ROOT/'docs/track_d/archives/METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_PLAN_001_summary.json'

def test_plan_boundaries_and_fixture_matrix():
    assert DOC.exists()
    data=json.loads(SUMMARY.read_text())
    assert data['fixture_matrix_case_count'] >= 12
    assert data['shadow_validation_plan_only'] is True
    for key,value in data.items():
        if key.endswith('_authorized') or key in {'selector_runtime_added','production_selector_router_authorized','runtime_code_changed','estimator_behavior_changed','assignment_logic_changed','mip_repository_modified','geox_to_mip_integration_started'}:
            assert value is False
    text=DOC.read_text()
    for term in ('SCM','DID','Synthetic DID','AugSynth CVXPY','Multicell/shared-control','shadow_blocked','blocked-reason taxonomy'):
        assert term in text
