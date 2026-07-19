# Method suitability selection shadow-validation fixture contract

## Metadata / Purpose
Typed, deterministic fixture input/output contract for future shadow validation; no selector runtime or execution.

## Prior artifact dependency and scope
Depends on `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_PLAN_001`. It captures design metadata, requested method/estimator/inference, readiness and release gate, downstream target, expected route, blockers, warnings, alternatives, and forbidden claims.

## Public API
`ShadowRouteStatus`, `MethodFamily`, `ReleaseGateState`, `DownstreamUseTarget`, `ShadowValidationFixtureInput`, `ExpectedShadowValidationOutcome`, `ShadowValidationFixture`, validation, serialization/deserialization, and `build_default_shadow_validation_fixtures`.

## Route and method semantics
Routes are shadow-only candidate, warning, diagnostic, research, blocked, release-gate, remediation, or retired/replaced. The 12 defaults cover SCM, DID, Synthetic DID, AugSynth, TBRRidge, Classic/Aggregate TBR, Bayesian TBR, TROP, multicell/shared-control, unknown method, and downstream export.

## Input and expected outcome schema
Inputs retain geometry, cells, shared control, assignment mechanism, KPI, grain, adequacy, diagnostics, requested family/estimator/inference, promotion, release gate, failures, and target. Outcomes retain route, blockers, warnings, alternatives, forbidden claims, and all-false readiness flags.

## Validation error codes
Stable codes include missing fixture/method/route, invalid cells/route, every unsafe readiness field, and `unsafe_downstream_export_target_requires_blocker`.

## Default fixture matrix
`build_default_shadow_validation_fixtures()` returns 12 structurally valid fixtures for future harness consumption.

## Serialization requirements
Stdlib dataclasses serialize to deterministic JSON-safe dictionaries and round-trip through deserialization.

## Production authorization boundary
Fixture contract only: selector runtime, harness execution, estimator/assignment changes, MIP integration, production inference, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, multicell claims, and agent work are disabled.

## Future harness / Final verdict / Recommended next artifact
The future harness should compare observed route decisions to `expected`, preserving blockers and warnings. Contract is complete; **PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_PLAN**. Next: `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_PLAN_001`.
