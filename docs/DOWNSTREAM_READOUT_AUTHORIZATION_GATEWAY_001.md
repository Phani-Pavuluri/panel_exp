# Downstream Readout Authorization Gateway 001

**Artifact ID:** DOWNSTREAM-READOUT-AUTHORIZATION-GATEWAY-001  
**Verdict:** `downstream_readout_authorization_gateway_implemented_fail_closed_no_promotion`

## 1. Executive summary

Implements the single authoritative gateway that every downstream consumer must pass before a governed readout can be used. The gateway consumes governed `ReadoutEvidence`, evaluates role-specific authorization, and **fails closed** for all production-facing roles in this artifact.

**Current behavior:** TrustReport → BLOCK; CalibrationSignal → BLOCK; MMM → BLOCK; LLM → BLOCK; production recommendation → BLOCK; automated budget action → BLOCK; external export → BLOCK. Research-safe roles may return RESTRICTED (never AUTHORIZED).

## 2. Why inference-boundary enforcement was insufficient

`INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001` blocks invalid estimator×inference×readout combinations at the readout boundary but does not:

- Enforce consumer-role authorization (TrustReport vs research)
- Validate promotion evidence for downstream export
- Serialize durable authorization results for Track B bundles
- Prevent LLM or caller reinterpretation of native `run_analysis()` output

## 3. Scope

- `evaluate_downstream_readout_authorization()` gateway API
- `DownstreamReadoutAuthorizationResult` frozen result object
- `DownstreamPromotionEvidence` input contract
- Consumer role registry (production vs research-safe)
- D-AUTH reason codes
- Track B wiring (`readout_evidence_wiring.py`)
- Fail-closed enforcement for all production-facing roles
- Fixtures and tests

## 4. Non-goals

- Promoting any method to downstream-authorized
- Estimator, inference, or design algorithm changes
- Live MMM ingestion or LLM execution
- Operator approval workflows or API deployment
- Creating production TrustReport or CalibrationSignal output

## 5. Gateway architecture

```
ReadoutEvidence (governed)
  → evaluate_downstream_readout_authorization(requested_role, promotion_evidence?)
  → DownstreamReadoutAuthorizationResult
  → assert_downstream_readout_authorized()  [raises on production roles]
```

Upstream stack (unchanged):

```
design assignment → contract → validation → guardrail → enforcement
  → estimator execution → inference → inference-boundary identity
  → DCM resolution → inference-boundary guardrail → ReadoutEvidence
```

## 6. ReadoutEvidence requirements

A downstream request must BLOCK unless all are present:

- `ReadoutEvidence` object (not native dict)
- Governed readout marker (`metadata.governed_readout_evidence = true`)
- Estimator identity
- Inference identity (when readout semantics require it)
- Readout identity
- Combination resolution
- Inference-boundary guardrail result
- Guardrail enforcement metadata
- Result payload

## 7. Governed-readout marker

Marker constant: `governed_readout_evidence` (from `estimator_readout_adapter_001.GOVERNED_READOUT_MARKER`). Set by `build_estimator_readout()` / `run_governed_analysis()`. Track B hint markers alone do not authorize.

## 8. Role registry

**Production-facing (always BLOCKED in this artifact):**

`trust_report`, `calibration_signal`, `mmm_calibration`, `llm_decision_support`, `production_recommendation`, `automated_budget_action`, `external_export`

**Research-safe (RESTRICTED when governed readout valid):**

`research`, `diagnostic`, `validation`, `blocked_status_explanation`

## 9. Status taxonomy

| Status | Meaning |
|--------|---------|
| AUTHORIZED | Reserved for future promotion artifacts; not emitted for production roles here |
| RESTRICTED | Internal research/diagnostic inspection only; no downstream export |
| BLOCKED | Missing/invalid governed readout, blocked role, or auth failure |
| UNKNOWN | Inspection with no execution request; downstream requests convert to BLOCKED |

## 10. Result object

`DownstreamReadoutAuthorizationResult` — frozen, JSON-serializable. Invariant for this artifact: `authorized = False` for every role.

## 11. Reason-code registry

D-AUTH codes (stable):

- `D-AUTH-MISSING-READOUT-EVIDENCE`
- `D-AUTH-NOT-GOVERNED-READOUT`
- `D-AUTH-MISSING-GOVERNED-MARKER`
- `D-AUTH-INVALID-GOVERNED-MARKER`
- `D-AUTH-MISSING-INFERENCE-BOUNDARY`
- `D-AUTH-INFERENCE-BOUNDARY-BLOCKED`
- `D-AUTH-COMBINATION-BLOCKED`
- `D-AUTH-COMBINATION-UNKNOWN`
- `D-AUTH-POINT-ONLY`
- `D-AUTH-READOUT-SEMANTICS-MISMATCH`
- `D-AUTH-POOLED-MULTICELL-BLOCKED`
- `D-AUTH-LEGACY-NATIVE-RESULT`
- `D-AUTH-MISSING-PROMOTION-EVIDENCE`
- `D-AUTH-PROMOTION-NOT-APPROVED`
- `D-AUTH-ROLE-NOT-APPROVED`
- `D-AUTH-DOWNSTREAM-ROLE-BLOCKED`
- `D-AUTH-TRUSTREPORT-BLOCKED`
- `D-AUTH-CALIBRATION-SIGNAL-BLOCKED`
- `D-AUTH-MMM-BLOCKED`
- `D-AUTH-LLM-BLOCKED`
- `D-AUTH-PRODUCTION-RECOMMENDATION-BLOCKED`
- `D-AUTH-AUTOMATED-BUDGET-ACTION-BLOCKED`
- `D-AUTH-EXTERNAL-EXPORT-BLOCKED`
- `D-AUTH-RESEARCH-ONLY`

Upstream D-CONTRACT, D-GUARDRAIL, D-ENFORCE, and I-BOUNDARY codes are preserved in the result but do not alone determine downstream auth status.

## 12. Promotion-evidence model

`DownstreamPromotionEvidence` — minimal contract with `artifact_id`, `status`, `approved_roles`, `approved_dcm_rows`, `approved_estimators`, `approved_inference_paths`, `approved_readout_semantics`, `expires_at`, `evidence_version`.

In this artifact: missing, malformed, or expired promotion → BLOCK contribution; promotion cannot authorize production roles.

## 13. TrustReport policy

BLOCK. Track B `build_trust_report_decision_inputs_from_bundle()` evaluates `trust_report` role, attaches `downstream_authorization`, sets `trust_report_ready=False`.

## 14. CalibrationSignal policy

BLOCK. No production-valid CalibrationSignal may be emitted.

## 15. MMM policy

BLOCK. No live MMM ingestion wired.

## 16. LLM policy

BLOCK. LLM payloads require gateway authorization; no prompt bypass.

## 17. Production recommendation policy

BLOCK. `assert_downstream_readout_authorized()` raises `DownstreamReadoutAuthorizationViolation`.

## 18. Automated budget action policy

BLOCK. Same as production recommendation.

## 19. External export policy

BLOCK.

## 20. Research and diagnostic policy

RESTRICTED when governed readout is valid and no D-AUTH blocking codes apply. `assert_downstream_readout_authorized()` returns without raising for research-safe RESTRICTED results.

## 21. Track B integration

`panel_exp/track_b/readout_evidence_wiring.py`:

- `evaluate_bundle_downstream_authorization()`
- `build_trust_report_decision_inputs_from_bundle()` attaches authorization block
- `assert_trust_report_bundle_authorized()` fail-closed helper

## 22. Evidence serialization

`TrustReportDecisionInputs.downstream_authorization` holds serialized gateway result. Additive; legacy bundles load with `authorized=False`.

## 23. Consumer API

```python
result = evaluate_downstream_readout_authorization(
    readout_evidence=readout,
    requested_role="trust_report",
    promotion_evidence=None,
)
assert_downstream_readout_authorized(result, requested_role="trust_report")
```

## 24. Exception semantics

`DownstreamReadoutAuthorizationViolation(RuntimeError)` — carries `.result` with full reason codes. No bypass parameter.

## 25. Legacy behavior

Legacy Track B bundles without governed `ReadoutEvidence` load but remain unauthorized. Native `run_analysis()` output is not accepted.

## 26. Fixture inventory

22 scenarios in `tests/fixtures/artifact_schemas/downstream_readout_authorization_gateway_001/scenarios.json`. No production-authorized fixture.

## 27. Test coverage

`tests/validation/test_downstream_readout_authorization_gateway_001.py` — governed validation, role authorization, promotion evidence, Track B integration, serialization, security.

## 28. Security/no-bypass properties

No `force=True`, `override_authorization`, `bypass_authorization`, or `ignore_authorization`. No LLM exemption.

## 29. Current governance status

Gateway implemented. All downstream production roles blocked. TrustReport eligibility validation implemented ([`TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md`](track_d/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md)); zero promotion candidates; authorization still BLOCKED.

## 30. Remaining limitations

- Promotion evidence cannot authorize production in this artifact
- Research RESTRICTED still requires governed readout construction via adapter
- MMM/LLM paths documented but not live-wired

## 31. Promotion prerequisites

Future promotion artifacts must supply role-specific approved evidence per DCM row, estimator, inference path, and readout semantics.

## 32. Follow-up work

- Role-specific promotion artifacts (TrustReport, CalibrationSignal, MMM)
- Mandatory governed readout path for all product exports
- Operator approval workflow integration

## 33. Verdict

`downstream_readout_authorization_gateway_implemented_fail_closed_no_promotion`
