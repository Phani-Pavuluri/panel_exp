# GEOX_NUMERICAL_TRUTH_FIXTURE_CASES_PLAN_001

## Metadata / Purpose
Concrete plan for twelve deterministic numerical-truth fixture cases supporting quarterly planning with experiment-informed budget reallocation.

## Prior dependency / Case table

| Case ID | Fixture class | Method | Intended status | Calibration | MIP handoff | Primary blocker/warning | Generator priority |
|---|---|---|---|---|---|---|---|
| geox_truth_scm_candidate_clean_001 | governed candidate | SCM | certified candidate | compatible | candidate | none | P0 |
| geox_truth_did_candidate_warning_001 | warning candidate | DID | candidate | compatible | warning | assumptions warning | P0 |
| geox_truth_infeasible_preperiod_001 | infeasible | SCM | blocked | incompatible | blocked | preperiod inadequate | P0 |
| geox_truth_weak_matchability_001 | weak matchability | SCM | diagnostic_only | review | diagnostic | weak matchability | P1 |
| geox_truth_unsupported_inference_001 | unsupported inference | DID | unsupported | incompatible | blocked | inference unsupported | P1 |
| geox_truth_tbrridge_diagnostic_only_001 | diagnostic method | TBRRidge | diagnostic_only | review | diagnostic | diagnostic route | P1 |
| geox_truth_bayesian_tbr_research_only_001 | research method | Bayesian TBR | research_only | none | research | research-only | P1 |
| geox_truth_stale_incompatible_evidence_001 | stale evidence | SCM | stale | stale | blocked | stale schema/version | P0 |
| geox_truth_conflicting_evidence_001 | conflict | DID | blocked | review | blocked | conflicting evidence | P0 |
| geox_truth_multicell_shared_control_block_001 | multicell block | multicell | blocked | incompatible | blocked | dependence/multiplicity | P0 |
| geox_truth_calibration_incompatible_001 | calibration conflict | SCM | candidate | incompatible | blocked | calibration mismatch | P0 |
| geox_truth_safe_blocked_readout_001 | blocked packet | SCM | blocked | incompatible | blocked | governed blocker | P0 |

## Case detail policy
Every case records intended input shape, panel grain, geo scope, pre/post periods, KPI, estimand, instrument, deterministic assignment seed, treatment/control units, known lift or explicit blocked truth, expected estimate/SE/interval, feasibility/design/assignment/readout status, warnings/blockers, calibration and MIP handoff status, tolerances, provenance/version, future generator, and future readout expectations.

## Truth-value policy
Future datasets use deterministic seeds, known treatment effects, counterfactual construction, absolute/relative lift, incremental outcome, estimator/uncertainty/interval tolerances. Blocked cases have explicit blocked truth and may omit estimates; diagnostic/research cases may contain numbers but never production authorization.

## Tolerance policy
Use exact structural, deterministic numerical, estimator numerical, uncertainty, blocked-state, warning/blocker, calibration-compatibility, and MIP-handoff exact-match categories.

## Future generator expectations
After this plan, a generator may create versioned local input datasets, truth metadata, expected readouts, blocked/diagnostic packets, manifest/index, and deterministic replay metadata. No generator is added here.

## Readout and MIP alignment
Successful cases become governed readout candidates; warning cases accepted-with-warning; blocked cases blocked packets; diagnostic/research cases remain constrained. Calibration-incompatible and multicell cases cannot export or make production claims. MIP consumes artifacts but does not certify GeoX truth.

## D6 Gate 1 alignment
This plan supports but does not complete D6 Gate 1. Remaining items are producer/consumer versions, compatibility matrix, fixture ownership, required/optional fields, failure semantics, release/rollback order, limitations, named owners, authorization flags, and migration/deprecation rules.

## Non-goals / Authorization boundary
No datasets, generator, readout runtime, estimator, assignment, MIP/MMM changes, exports, reporting, decisioning, agents, real-data pilot, or production authorization.

## Final verdict / Recommended next artifact
**PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_GENERATOR_PLAN**. Next: `GEOX_NUMERICAL_TRUTH_FIXTURE_GENERATOR_PLAN_001`.
