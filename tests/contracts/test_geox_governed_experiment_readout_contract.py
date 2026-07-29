import importlib.util,json,sys
s=importlib.util.spec_from_file_location('readout','panel_exp/contracts/geox_governed_experiment_readout.py'); m=importlib.util.module_from_spec(s); sys.modules['readout']=m; s.loader.exec_module(m)
def test_examples_validate_and_round_trip():
    for fn in (m.build_example_geox_success_readout,m.build_example_geox_warning_readout,m.build_example_geox_stale_readout,m.build_example_geox_incompatible_readout,m.build_example_geox_blocked_readout,m.build_example_geox_failed_readout):
        r=fn(); assert not m.validate_geox_governed_experiment_readout(r); assert m.deserialize_geox_governed_experiment_readout(m.serialize_geox_governed_experiment_readout(r))==r; assert json.dumps(m.serialize_geox_governed_experiment_readout(r),sort_keys=True)
