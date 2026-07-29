# GEOX_GOVERNED_READOUT_ARTIFACT_CONTRACT_001

## Metadata / Purpose
Canonical analytical artifact contract: `GeoXGovernedExperimentReadout` for MIP P2 and MMM calibration compatibility evaluation.

## Envelope transport boundary
`GeoXArtifactEnvelope` is a transport wrapper only. It does not replace the canonical analytical readout.

## Ownership split
GeoX asks: Is this experiment readout analytically valid and eligible to be evaluated? MMM asks: Is this valid readout compatible with this specific model? MIP asks: How should resulting evidence be routed, explained, and reported?

## Required fields / States
The contract covers identity/version, KPI/estimand/effect, scope, freshness/uncertainty, method/instrument, feasibility/status, warnings/blockers/failures, lineage, provenance, replay, and authorization flags. Readout states are success, warning, stale, incompatible, blocked, and failed; diagnostic-only/research-only methods remain non-authorizing.

## Handoff and MMM compatibility
GeoX emits only `eligible_for_compatibility_evaluation`, `ineligible_for_calibration_handoff`, or `blocked_for_handoff`. MMM owns final `compatible`, `compatible_with_warning`, `stale`, `incompatible`, and `blocked` states.

## Fixture-backed certification / Validation
Six deterministic examples cover success, warning, stale, incompatible, blocked, and failed states. Validation enforces reasons, coherent uncertainty, typed states, non-production flags, and no overlap with MMM compatibility ownership. Serialization round-trips deterministically.

## Limitations / MIP blockers
No readout builder, package entrypoint, estimator execution, or MIP runtime integration exists yet; fixture artifacts remain local and synthetic.

## Authorization boundary / Final verdict
No production inference, assignment, readout authorization, CalibrationSignal, ExperimentEvidence, TrustReport, DecisionSurface, RecommendationContract, LLM, budget, or multicell production claim is enabled. **PROCEED_TO_GEOX_CERTIFIED_GOVERNED_READOUT_FIXTURES**.

## Next evidence-producing artifact
`GEOX_CERTIFIED_GOVERNED_READOUT_FIXTURES_001`.
