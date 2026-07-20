import json
from panel_exp.runtime.method_suitability_shadow_validation_harness import *
def test_default_run_is_safe_and_deterministic():
    out=run_method_suitability_shadow_validation_harness(); assert len(out.records)==12; assert out.aggregate_summary.passed_count==12; assert out.aggregate_summary.failed_count==0; assert not out.failure_packets; assert not out.aggregate_summary.safe_to_authorize_production_selector_router; assert all(r.passed and r.route_status_match and r.blocked_reasons_match for r in out.records); assert json.dumps(serialize_shadow_validation_harness_output(out),sort_keys=True)
def test_malformed_fixture_emits_failure_packet():
    out=run_method_suitability_shadow_validation_harness(ShadowValidationHarnessInput((build_default_shadow_validation_fixtures()[0].__class__(build_default_shadow_validation_fixtures()[0].input.__class__("", "x","x",0,False,"x","x","x","x","x","x",{},"","x","x","x","x",(),"diagnostic"),build_default_shadow_validation_fixtures()[0].expected),))); assert out.failure_packets
