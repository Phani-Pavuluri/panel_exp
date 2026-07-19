import json
from panel_exp.contracts.method_suitability_shadow_validation import *

def test_defaults_validate_and_round_trip():
    fixtures=build_default_shadow_validation_fixtures(); assert len(fixtures)==12
    for fixture in fixtures:
        assert not validate_shadow_validation_fixture(fixture)
        payload=serialize_shadow_validation_fixture(fixture); assert json.dumps(payload,sort_keys=True)
        assert deserialize_shadow_validation_fixture(payload)==fixture

def test_invalid_and_unsafe_inputs():
    f=build_default_shadow_validation_fixtures()[0]
    bad=ShadowValidationFixture(ShadowValidationFixtureInput("", "x","x",0,False,"x","x","x","x","x","x",{},"","x","x","x","x",(),"diagnostic"), f.expected)
    assert {"missing_fixture_id","invalid_number_of_cells","missing_requested_method_family"}.issubset(validate_shadow_validation_fixture(bad))
    unsafe=ExpectedShadowValidationOutcome(f.expected.expected_route_status,(),(),(),(),ready_for_production_inference=True)
    assert "unsafe_ready_for_production_inference" in validate_shadow_validation_fixture(ShadowValidationFixture(f.input,unsafe))
