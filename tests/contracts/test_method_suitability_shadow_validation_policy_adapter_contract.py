import json
from panel_exp.contracts.method_suitability_shadow_validation_policy_adapter import *
def test_safe_builders_and_serialization():
    i=build_safe_policy_adapter_input(); o=build_safe_policy_adapter_observed_outcome(); assert not validate_policy_adapter_input(i); assert not validate_policy_adapter_observed_outcome(o); assert json.dumps(serialize_policy_adapter_observed_outcome(o),sort_keys=True)
def test_unsafe_claim_and_flags_rejected():
    o=build_safe_policy_adapter_observed_outcome(); assert 'policy_unsafe_production_claim' in validate_policy_adapter_observed_outcome(PolicyAdapterObservedOutcome(o.route_status,(),(),(),('lift',),True,True,None)); assert 'unsafe_readiness_flags_not_false' in validate_policy_adapter_observed_outcome(PolicyAdapterObservedOutcome(o.route_status,(),(),(),(),False,True,None))
