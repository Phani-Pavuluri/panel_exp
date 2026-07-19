# Non-Production GeoX/MIP Artifact Envelope Dry-Run Runtime

## Purpose

This artifact adds a deterministic, fixture-only runtime rehearsal for the governed GeoX/MIP envelope. It exercises Cases A–F without production integration, authorization, or claims.

## Public API

`GeoXMIPArtifactEnvelopeDryRunCase`, `GeoXMIPArtifactEnvelopeDryRunResult`, `build_non_production_geox_mip_artifact_envelope_dry_run`, and `serialize_geox_mip_artifact_envelope_dry_run_result` are exported from `panel_exp.contracts`.

## Cases

Cases A–F cover diagnostic assignment, blocked readout, failure propagation, post-test spend diagnostics, blocked calibration candidate, and blocked ExperimentEvidence candidate. Every envelope is validated and serialized; blocked reasons and warnings are retained.

## Safety boundary

All outputs are fixture-only and non-production. Assignment, causal readout, calibration export, ExperimentEvidence export, TrustReport assembly, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, selector/router runtime, multicell production claims, and agent work remain unauthorized. No MIP repository was modified.

## Determinism and validation

The runtime uses fixed fixture metadata and stable JSON-safe serialization. Focused tests verify six-case coverage, validation, boundary flags, and repeatability. Required validation: `git diff --check`, JSON parsing, focused pytest, and forbidden-authorization safety grep.

## Decision

**PROCEED_TO_MIP_SIDE_GEOX_ENVELOPE_CONSUMER_CONTRACT**

Recommended next artifact: `MIP_SIDE_GEOX_ENVELOPE_CONSUMER_CONTRACT_001`. Production assignment, readout, exports, and decisioning remain explicitly out of scope.
