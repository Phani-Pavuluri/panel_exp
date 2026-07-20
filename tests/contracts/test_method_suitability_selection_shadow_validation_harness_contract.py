import json
from panel_exp.contracts.method_suitability_shadow_validation_harness import *
def test_builders_validate_and_serialize():
    r=build_passing_shadow_validation_result_record(); a=build_valid_shadow_validation_aggregate_summary(); p=build_shadow_validation_failure_packet(); m=build_shadow_validation_harness_run_manifest()
    assert not validate_shadow_validation_result_record(r); assert not validate_shadow_validation_aggregate_summary(a); assert not validate_shadow_validation_failure_packet(p); assert not validate_shadow_validation_harness_run_manifest(m)
    assert json.dumps(serialize_shadow_validation_result_record(r),sort_keys=True)
def test_unsafe_flags_and_counts():
    a=build_valid_shadow_validation_aggregate_summary(); assert 'unsafe_safe_to_authorize_production_selector_router' in validate_shadow_validation_aggregate_summary(ShadowValidationAggregateSummary(**{**a.__dict__,'safe_to_authorize_production_selector_router':True}))
    m=build_shadow_validation_harness_run_manifest(); assert 'unsafe_production_authorization_true' in validate_shadow_validation_harness_run_manifest(ShadowValidationHarnessRunManifest(**{**m.__dict__,'production_authorization':True}))
