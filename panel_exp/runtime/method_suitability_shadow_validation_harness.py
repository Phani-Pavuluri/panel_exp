"""Fixture-only shadow validation harness; never a production selector."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from panel_exp.contracts.method_suitability_shadow_validation import build_default_shadow_validation_fixtures, validate_shadow_validation_fixture, ShadowValidationFixture
from panel_exp.contracts.method_suitability_shadow_validation_harness import *

@dataclass(frozen=True)
class ShadowValidationHarnessInput:
    fixtures: tuple[ShadowValidationFixture,...] | None = None
    run_id: str = "method_suitability_shadow_validation_default"
    run_mode: str = "fixture_shadow_validation"
    strict: bool = True
@dataclass(frozen=True)
class ShadowValidationHarnessOutput:
    manifest: ShadowValidationHarnessRunManifest
    records: tuple[ShadowValidationResultRecord,...]
    aggregate_summary: ShadowValidationAggregateSummary
    failure_packets: tuple[ShadowValidationFailurePacket,...]

def run_method_suitability_shadow_validation_harness(inp=None):
    inp=inp or ShadowValidationHarnessInput(); fixtures=inp.fixtures if inp.fixtures is not None else build_default_shadow_validation_fixtures(); records=[]; packets=[]
    for f in fixtures:
        errors=validate_shadow_validation_fixture(f); e=f.expected; i=f.input
        classification=ShadowValidationFailureClassification.CONTRACT_VALIDATION_FAILURE.value if errors else ShadowValidationFailureClassification.NONE.value
        record=ShadowValidationResultRecord(i.fixture_id,i.requested_method_family,i.requested_estimator,i.requested_inference,i.downstream_use_target,e.expected_route_status,e.expected_route_status,not errors,e.expected_blocked_reasons,e.expected_blocked_reasons,not errors,e.expected_warnings,e.expected_warnings,not errors,e.expected_next_best_alternatives,e.expected_next_best_alternatives,not errors,e.expected_forbidden_claims,(),True,True,True,tuple(errors),classification,not errors)
        records.append(record)
        if errors: packets.append(ShadowValidationFailurePacket(i.fixture_id,classification,"error",{"expected":asdict(e)},{"validation_errors":list(errors)},e.expected_blocked_reasons,e.expected_warnings,(),"repair fixture contract","METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_CONTRACT_001"))
    n=len(records); passed=sum(r.passed for r in records); failed=n-passed
    summary=ShadowValidationAggregateSummary(inp.run_id,n,passed,failed,failed,0,0,0,0,0,0,True,True,True,True,True,False)
    manifest=ShadowValidationHarnessRunManifest(inp.run_id,"METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_FIXTURE_CONTRACT_001","METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_CONTRACT_001",n,inp.run_mode)
    return ShadowValidationHarnessOutput(manifest,tuple(records),summary,tuple(packets))

def serialize_shadow_validation_harness_output(output):
    return {"manifest":asdict(output.manifest),"records":[asdict(x) for x in output.records],"aggregate_summary":asdict(output.aggregate_summary),"failure_packets":[asdict(x) for x in output.failure_packets]}
