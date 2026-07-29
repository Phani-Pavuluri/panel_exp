# GEOX_CERTIFIED_GOVERNED_READOUT_FIXTURES_001

## Metadata / Purpose
Fixture-backed `GeoXGovernedExperimentReadout` artifacts sourced from the validated 12-case numerical-truth set.

## Dependencies / Layout
Depends on the numerical-truth validation checkpoint and governed readout contract. `tests/fixtures/geox_governed_readouts/` contains manifest, per-case `governed_readout.json`, `source_truth.json`, and replay metadata.

## Manifest / State coverage
The manifest indexes all 12 source cases, schema/producer version, paths, and non-production boundary. Fixtures cover success, warning, stale, incompatible, blocked, failed, diagnostic-only, and research-only states.

## Handoff / MMM ownership
Fixtures emit GeoX handoff eligibility only. MMM owns final compatibility states; no final MMM compatibility is emitted. MIP may consume these for routing, explanation, and reporting design.

## Validation / Runtime blockers
Every fixture deserializes and validates against the canonical contract; replay is deterministic and authorization flags are false. A builder package entrypoint and runtime integration remain future work.

## Authorization boundary / Final verdict
No estimator, production readout authorization, CalibrationSignal, ExperimentEvidence, TrustReport, DecisionSurface, RecommendationContract, LLM, budget, selector/router, assignment, or MIP/MMM changes are enabled. **PROCEED_TO_GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT**.

## Recommended next artifact
`GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`.
