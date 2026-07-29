import importlib.util,json,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('readout','panel_exp/contracts/geox_governed_experiment_readout.py'); m=importlib.util.module_from_spec(s);sys.modules['readout']=m;s.loader.exec_module(m)
ROOT=Path('tests/fixtures/geox_governed_readouts')
def test_governed_readout_fixtures_validate():
    manifest=json.loads((ROOT/'manifest.json').read_text()); assert manifest['case_count']==12
    states=set()
    for item in manifest['cases']:
        d=ROOT/item['case_id']; r=m.deserialize_geox_governed_experiment_readout(json.loads((d/'governed_readout.json').read_text())); assert not m.validate_geox_governed_experiment_readout(r); states.add(r.readout_status); assert r.handoff_eligibility_status not in {'compatible','incompatible','stale'}
    assert {'success','warning','stale','incompatible','blocked','failed'}.issubset(states)
def test_no_mmm_compatibility_or_authorization():
    for p in ROOT.rglob('*.json'):
        text=p.read_text(); assert 'mmm_compatibility' not in text or 'false' in text; assert 'production_authorized": true' not in text
