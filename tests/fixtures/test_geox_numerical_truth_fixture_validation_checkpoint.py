import importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('g','panel_exp/fixtures/geox_numerical_truth_generator.py'); g=importlib.util.module_from_spec(s); s.loader.exec_module(g)
ROOT=Path('tests/fixtures/geox_numerical_truth')
def test_checkpoint_validates_generated_fixtures():
    data=json.loads((ROOT/'manifest.json').read_text()); assert data['case_count']==12; assert not g.validate_generated_geox_truth_fixture_artifacts(ROOT)
    for item in data['cases']:
        d=ROOT/item['case_id']; assert (d/'truth.json').exists() and (d/'input_panel.csv').exists() and (d/'replay.json').exists(); assert any((d/n).exists() for n in ('expected_readout.json','expected_packet.json'))
def test_checkpoint_summary_and_handoff_boundary():
    summary=json.loads(Path('docs/track_d/archives/GEOX_NUMERICAL_TRUTH_FIXTURE_VALIDATION_CHECKPOINT_001_summary.json').read_text()); assert summary['fixture_case_count']==12 and summary['handoff_eligibility_boundary_confirmed']; assert summary['decision']=='PROCEED_TO_GEOX_GOVERNED_READOUT_ARTIFACT_CONTRACT'
