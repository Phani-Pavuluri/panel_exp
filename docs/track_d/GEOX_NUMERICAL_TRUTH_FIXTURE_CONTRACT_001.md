# GeoX numerical-truth fixture contract

## Metadata / Purpose
Typed, JSON-safe contract for future certified GeoX truth fixtures aligned to quarterly planning with experiment-informed budget reallocation.

## Prior artifact dependency / Contract scope
Depends on `GEOX_NUMERICAL_TRUTH_FIXTURE_CERTIFICATION_PLAN_001`. Contract examples are not datasets or generators.

## Public API and statuses
Exports certification/fixture-class enums, time window, tolerance, provenance, dataset, readout, calibration, MIP handoff, and main fixture dataclasses plus validation, serialization, deserialization, and 12-fixture catalog builder. Statuses include certified, candidate, diagnostic_only, research_only, blocked, unsupported, stale, superseded.

## Analytical truth and schemas
Fields cover fixture/dataset/truth versions, design/method/instrument, seed, grain, scope/window, KPI/estimand, units, known lifts/incremental outcome, expected estimate/SE/interval/uncertainty, feasibility/design/assignment/readout statuses, blockers/warnings, calibration, MIP handoff, tolerances, and provenance.

## Minimum 12-fixture catalog
Catalog classes are successful governed readout, warning readout, infeasible design, weak matchability, unsupported inference, diagnostic-only, research-only, stale/incompatible, conflicting evidence, multicell/shared-control block, calibration-incompatible, and safe blocked readout packet.

## Validation / Serialization
Stable errors cover missing identity/schema fields, invalid class/status/interval/tolerance, and missing provenance/calibration/handoff. Serialization is deterministic JSON-safe, tuple-to-list, and non-mutating. D6 Gate 1 still requires compatibility, ownership, failure, release/rollback, limitations, authorization, and migration rules.

## Authorization boundary / Final verdict / Recommended next artifact
No datasets, runtime, estimator, assignment, exports, MIP/MMM changes, or production authorization. **PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_CASES_PLAN**. Next: `GEOX_NUMERICAL_TRUTH_FIXTURE_CASES_PLAN_001`.
