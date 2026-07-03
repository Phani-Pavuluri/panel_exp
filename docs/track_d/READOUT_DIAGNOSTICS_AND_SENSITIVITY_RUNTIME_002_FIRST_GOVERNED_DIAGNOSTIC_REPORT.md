# READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC

**Artifact ID:** `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC`  
**Status:** completed  
**Base commit:** `cf9e462`  
**Final verdict:** `first_governed_did_coverage_diagnostic_implemented_no_inference_or_claim_authorization`

## Source files inspected

- `panel_exp/validation/estimator_inference_did_executor_003.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_contract_001.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

## Implementation scope

This artifact adds the first governed diagnostic path:

- DID group coverage validation (treated/control pre/post cells)
- simple pre-period baseline means and difference
- optional descriptive normalized pre-period gap
- typed diagnostic result packet and trace
- integration with diagnostics/sensitivity runtime 001 behind config gate

Forbidden: statistical parallel-trends tests, bootstrap/jackknife/placebo/conformal diagnostics, p-values, CIs, uncertainty, claim authorization, production readout authorization, estimator/inference execution, effect/lift/ROI computation.

## Why DID coverage/pre-period diagnostic first

After the first governed DID point-estimate executor, the narrowest diagnostic lane is structural coverage and descriptive pre-period baseline evidence. This supports evidence sufficiency review without statistical inference.

## Relationship to DID point-estimate executor

Reuses panel parsing conventions and `GOVERNED_DID_INSTRUMENT_IDS` from the DID executor. Does not recompute DID treatment effects.

## Relationship to diagnostics/sensitivity runtime 001

`evaluate_readout_diagnostics_sensitivity(...)` calls `evaluate_did_coverage_diagnostic(...)` when `enable_governed_did_coverage_diagnostic=True` and requirement type is a governed DID diagnostic.

## Public API

- `evaluate_did_coverage_diagnostic(input_data, config=None) -> DIDCoverageDiagnosticResult`
- alias: `evaluate_governed_did_diagnostic(...)`

## Input contract

Minimum fields: `panel_data`, field mappings, pre/post mapping, `instrument_id`, `requirement_id`, `execution_artifact_id`, `claim_scope`.

## Validation gates

Blocks on missing panel, missing columns, invalid outcomes, missing requirement/execution artifact, unsupported instrument or diagnostic type.

## Diagnostic formula/logic

Computes cell counts, treated/control pre-period means, `pre_period_baseline_difference`, optional `normalized_pre_period_gap`.

## Status logic

- zero required cell coverage → `DIAGNOSTIC_FAILED`
- missing/invalid inputs → `DIAGNOSTIC_BLOCKED`
- optional normalized gap threshold → `DIAGNOSTIC_FAILED` or `DIAGNOSTIC_PASSED_WITH_WARNINGS`
- otherwise → `DIAGNOSTIC_PASSED`

## Evidence sufficiency integration

Passed diagnostics update evidence packets and may support `EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW`. Evidence sufficiency is not claim authorization.

## Claim boundary treatment

Allowed positive flags:

- `first_governed_diagnostic_implemented: true`
- `did_coverage_diagnostic_implemented: true`
- `diagnostic_result_computed: true/false per input`
- `diagnostic_pass_fail_computed: true/false per input`

Authorization flags remain false.

## Failure packet semantics

Failure packets include retry categories such as `FIX_DIAGNOSTIC_INPUTS`, `FIX_INPUT_DATA_CONTRACT`, `RERUN_EXECUTION_WITH_REQUIRED_TRACE`, `BLOCK_INSTRUMENT`.

## Tests added

`tests/validation/test_readout_did_diagnostics_002.py` plus runtime integration tests.

## Validation results

Targeted pytest and regressions run in implementation workflow.

## Known limitations

- only DID coverage/pre-period structural diagnostic implemented
- no statistical parallel-trends or placebo diagnostics
- no sensitivity execution
- no claim authorization

## Recommended next artifact

`CLAIM_AUTHORIZATION_CONTRACT_001`

Alternative: `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE_CONTRACT`
