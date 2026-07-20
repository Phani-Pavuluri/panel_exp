# Method suitability shadow-validation harness contract

## Metadata / Purpose
Typed JSON-safe contracts for future shadow harness result records, aggregate summaries, failure packets, and run manifests.

## Prior artifact dependency / Contract scope
Depends on the fixture contract and harness plan. This adds no harness or selector runtime.

## Public API
`ShadowValidationFailureClassification`, `ShadowValidationResultRecord`, `ShadowValidationAggregateSummary`, `ShadowValidationFailurePacket`, `ShadowValidationHarnessRunManifest`, validators, serializers, and helper builders.

## Schemas and semantics
Result records compare expected/observed routes, blockers, warnings, alternatives, forbidden claims, readiness, authorization, and failure classification. Aggregate summaries count outcomes and require all safety flags false. Failure packets preserve expected/observed values, blockers, warnings, unsafe claims, resolution, and next artifact. Run manifests identify fixture/harness contracts and remain fixture-only.

## Validation and serialization
Stable validation codes cover missing IDs, counts, classifications, unsafe claims/readiness/authorization, unsafe production authorization, runtime, estimator, or MIP flags, and missing resolutions. Dataclass serialization is deterministic JSON-safe and converts tuples to lists without mutation.

## Helper builders / Future harness consumption
Builders provide safe representative records, summaries, failure packets, and manifests. A later harness may consume these contracts after fixture evaluation; this artifact does not execute that harness.

## Production authorization boundary / Final verdict
No selector runtime, estimator execution, assignment, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, MIP integration, multicell claims, or agent work is authorized. **PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_RUNTIME**.

## Recommended next artifact
`METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_RUNTIME_001`.
