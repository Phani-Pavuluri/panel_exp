# METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_PLAN_001

## Metadata / Purpose
Plan for a future non-authorizing harness consuming the typed shadow fixture contract. No harness runtime is implemented.

## Prior-artifact dependencies / Fixture contract inventory
Depends on `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_FIXTURE_CONTRACT_001` and its 12 default fixtures covering SCM candidate, DID conditional/blocked, AugSynth remediation, TBRRidge diagnostic, Classic/Aggregate retired, Bayesian/TROP research, Synthetic DID readiness, multicell blocked, unknown method, and downstream export blocked. The matrix includes a **Downstream MIP/CalibrationSignal** request blocked from GeoX.

## Harness objective and non-goals
Load fixtures, validate them, compare expected versus observed shadow decisions, preserve blockers/warnings/alternatives, emit deterministic records and summaries, and never authorize production. No selector, estimator, assignment, MIP integration, or execution is added.

## Planned harness phases
`load_fixtures` → `validate_fixture_contract` → `build_shadow_selection_candidate` → `evaluate_shadow_route` → `compare_expected_vs_observed` → `check_forbidden_claims` → `emit_result_record` → `emit_aggregate_summary` → `emit_failure_packets`. These are planned future phases, not implemented here.

## Fixture loading / validation flow
Load default and external JSON fixtures, deserialize, validate stable error codes, and fail closed on missing required fixtures or unsafe readiness flags.

## Shadow-evaluation adapter boundary
The future adapter is a pure shadow evaluator: it receives fixture input and returns observed route/status metadata. It cannot call production selectors, estimators, GeoX jobs, or MIP.

## Expected vs observed comparison model
Compare route status, blocked reasons, warnings, next-best alternatives, forbidden claims, readiness flags, and authorization flags. Route and production/downstream blocker mismatches are hard failures; warning and alternative mismatches are review failures unless unsafe.

## Result record schema
Each record contains `fixture_id`, `requested_method_family`, `requested_estimator`, `requested_inference`, `downstream_use_target`, `expected_route_status`, `observed_route_status`, `route_status_match`, `expected_blocked_reasons`, `observed_blocked_reasons`, `blocked_reasons_match`, `expected_warnings`, `observed_warnings`, `warnings_match`, `expected_next_best_alternatives`, `observed_next_best_alternatives`, `next_best_alternatives_match`, `expected_forbidden_claims`, `observed_forbidden_claims`, `forbidden_claims_absent`, `readiness_flags_all_false`, `authorization_flags_all_false`, `validation_errors`, `failure_classification`, `passed`, and `notes`.

## Aggregate summary schema
Future summary contains `artifact_id`, `fixture_count`, `passed_count`, `failed_count`, `contract_failure_count`, `selection_policy_failure_count`, `fixture_expectation_failure_count`, `environment_failure_count`, `forbidden_claim_failure_count`, `readiness_flag_failure_count`, `authorization_flag_failure_count`, `all_required_fixtures_present`, `all_forbidden_claims_absent`, `all_readiness_flags_false`, `all_authorization_flags_false`, `safe_to_proceed_to_harness_runtime`, and `safe_to_authorize_production_selector_router` (always false).

## Failure packet schema
Packets contain `fixture_id`, `failure_classification`, `severity`, `expected`, `observed`, `blocked_reasons`, `warnings`, `unsafe_claims`, `recommended_resolution`, and `next_safe_artifact`.

## Failure classification taxonomy
`contract_validation_failure`, `selection_policy_mismatch`, `fixture_expectation_mismatch`, `missing_required_fixture`, `forbidden_claim_emitted`, `readiness_flag_violation`, `authorization_flag_violation`, `release_gate_violation`, `method_readiness_violation`, `environment_execution_failure`, `serialization_failure`.

## Acceptance thresholds
All 12 fixtures load and validate; records are JSON-safe; no forbidden claims; readiness and authorization flags false; production selector/router unauthorized. Unsafe claims/true flags are hard failures; route and production blocker mismatches are hard failures; warning/alternative mismatches are review failures unless unsafe.

## Release-gate / method-readiness dependency
The harness preserves release-gate and method-readiness blockers and never upgrades a candidate to production.

## MIP handoff pause / Validation strategy
MIP-owned fixture integration remains paused from GeoX. Validate plan, schemas, fixture coverage, JSON, diff, and safety boundaries before implementing contracts/runtime.

## Authorization boundary / Final verdict / Recommended next artifact
No production inference, assignment, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, multicell claims, or agent work is authorized. **PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_CONTRACT**. Next: `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_HARNESS_CONTRACT_001`.
