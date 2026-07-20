# Method suitability shadow-validation policy-adapter contract

## Metadata / Purpose
Typed, deterministic boundary for future policy-adapter input, observed outcomes, diagnostics, applied rules, and failure codes.

## Prior artifact dependency / Scope
Depends on the policy-adapter plan. This contract adds no policy runtime, selector, estimator, MIP integration, or authorization.

## Public API
`PolicyAdapterFailureCode`, `PolicyAdapterWarningCode`, `PolicyRuleId`, `PolicyAdapterInput`, `PolicyAdapterObservedOutcome`, `PolicyAdapterDiagnostics`, `PolicyAdapterFailure`, validators, serializers, and safe builders.

## Semantics and validation
Inputs carry fixture metadata and governance state. Outcomes carry route, blocked reasons, warnings, alternatives, forbidden claims, and all-false safety flags. Diagnostics carry rule IDs, readiness/gate state, targets, completeness, failures, blockers, warnings, alternatives, unsafe claims, and notes. Validation rejects missing metadata, unsafe flags, and production claims.

## Serialization / Future runtime
Serializers produce JSON-safe dictionaries without mutation. A future policy runtime may consume this contract to derive observations independently of expected outcomes and feed the existing harness.

## Production authorization boundary / Final verdict
Production inference, assignment, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, multicell claims, and agent work remain unauthorized. **PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_RUNTIME**.

## Recommended next artifact
`METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_RUNTIME_001`.
