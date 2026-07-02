# READOUT_METHOD_GOVERNANCE_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `READOUT_METHOD_GOVERNANCE_CONTRACT_001` |
| **Artifact type** | `readout_method_governance_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_readout_plan_generation_or_estimator_execution` |
| **Base commit** | `d8dfbc3` (Implement deterministic design assignment runtime) |
| **Final verdict** | `readout_method_governance_contract_defined_no_estimator_execution_or_causal_claim_authorization` |

This artifact is a **contract/specification document only**. It defines the governance contract that sits between assignment artifacts plus the method/instrument suitability matrix and future readout planning, estimator execution, and reporting claims. **No readout plan generation, primary/sensitivity/diagnostic stack selection, estimator execution, inference execution, effect/lift/ROI computation, p-values/CIs, causal claim authorization, or production readout authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_ASSIGNMENT_RUNTIME_001` | Assignment artifact upstream |
| `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001` | Assignment plan/candidate/reproducibility contract |
| `METHOD_SUITABILITY_RUNTIME_001` | Instrument suitability matrix upstream |
| `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` | Estimand and handoff contract |
| `INFERENCE_READOUT_SEMANTICS_001` | Readout semantics and uncertainty taxonomy |
| `DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001` | Production readout role blockers |
| `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` | Assignment feasibility upstream |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Design structure upstream |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario policy upstream |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE readiness upstream |

---

## 3. Why this contract is needed

The current stack validates:

Profiler/data readiness → Geo/unit feasibility → Spend manipulation feasibility → Power/MDE readiness → Design cell structure → Scenario policy feasibility → Assignment feasibility → Method suitability with instrument matrix → **Design assignment runtime** (deterministic explicit-pool allocation).

The next unanswered question is:

> Given a governed assignment artifact and instrument suitability matrix, what must be true before an assignment–instrument pair can be considered eligible for a future causal readout plan?

Without this contract, future planners may:

- treat assignment generation as causal readout authorization
- select estimators or inference paths without instrument governance review
- emit causal interval or lift/ROI claims without uncertainty-semantics alignment
- pool multi-cell readouts without explicit governance blockers
- bypass estimand declaration when authorizing readout claims
- conflate diagnostic-only instruments with production-readout eligibility
- authorize TrustReport, CalibrationSignal, MMM, or LLM roles from governance eligibility alone

This contract defines eligibility governance, claim boundaries, and production-readout blockers — without generating readout plans or executing estimators.

---

## 4. Core goal statement

`READOUT_METHOD_GOVERNANCE_CONTRACT_001` defines the governance contract between assignment artifacts and method/instrument suitability on one side and future readout planning plus reporting claims on the other. It specifies readout governance statuses, instrument governance statuses, claim eligibility statuses, readout claim types, assignment artifact governance, estimand governance treatment, uncertainty semantics treatment, diagnostic/sensitivity slot treatment, and production-readout blockers. It does not implement readout planning, stack selection, estimator execution, inference execution, effect estimation, or production authorization.

---

## 5. Relationship to design assignment runtime

`DESIGN_ASSIGNMENT_RUNTIME_001` generates deterministic explicit-pool assignment artifacts: assignment plan, candidate, allocations, constraint/exclusion traces, and reproducibility manifest. It does not authorize causal readout.

Future readout method governance must consume `DesignAssignmentRuntimeReport`, `AssignmentPlan`, `AssignmentCandidate`, `assignment_reproducibility_manifest`, and `assignment_unit_allocations`. Assignment artifact governance statuses classify whether the artifact is ready for readout governance review. **Assignment generation does not imply readout governance eligibility or causal claim authorization.**

---

## 6. Relationship to method suitability runtime

`METHOD_SUITABILITY_RUNTIME_001` emits `method_instrument_suitability_matrix` with per-instrument design, estimand, assignment, power/MDE, scenario-policy, and governance compatibility. It classifies instruments but does not select a winner or readout stack.

Future readout method governance must preserve instrument suitability statuses and map them to instrument governance statuses. If all relevant instruments are blocked, readout governance must be blocked. If only diagnostic-only instruments remain, readout governance is restricted to diagnostic/research paths. **Instrument eligibility for review does not authorize estimator execution or causal claims.**

---

## 7. Relationship to inference readout semantics

`INFERENCE_READOUT_SEMANTICS_001` defines estimand naming, interval targets, uncertainty-source taxonomy, and readout classifications (`point_only_no_uncertainty`, `prediction_interval_only`, `causal_interval_candidate_requires_validation`, etc.).

Future readout method governance must consume uncertainty semantics classifications and block causal-interval or lift claims when semantics are mismatched, ambiguous, or leakage-blocked. **This contract defines governance treatment only; it does not compute intervals or score coverage.**

---

## 8. Relationship to downstream readout authorization gateway

`DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001` blocks production-facing roles (TrustReport, CalibrationSignal, MMM, LLM, production recommendation, external export) even when governed readout evidence exists.

This contract aligns production-readout blocker roles with that gateway. Readout governance eligibility for planning **never** authorizes production-facing roles. Production readout authorization remains a separate future promotion path.

---

## 9. Conceptual distinctions

| # | Concept | Question answered | Rule |
|---|---------|-------------------|------|
| 1 | **Assignment artifact** | Were units allocated under governed constraints? | Produced by `DESIGN_ASSIGNMENT_RUNTIME_001`; does not authorize readout |
| 2 | **Instrument suitability matrix** | Which estimator×inference instruments are review-eligible? | Produced by `METHOD_SUITABILITY_RUNTIME_001`; does not select winner |
| 3 | **Readout method governance** | Is assignment+instrument pair eligible for future readout planning? | This artifact; does not generate plans |
| 4 | **Readout plan** | Which primary/sensitivity/diagnostic stack will run? | Future `READOUT_PLAN_CONTRACT_001` / runtime only |
| 5 | **Estimator/inference execution** | What numeric readout is computed? | Future runtime only |
| 6 | **Claim authorization** | May a causal/incremental-lift/ROI claim be reported? | Always false here |
| 7 | **Production readout authorization** | May TrustReport/MMM/LLM consume readout? | Always false here |

---

## 10. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `ReadoutMethodGovernanceInput` | Bundled upstream reports, assignment artifacts, instrument matrix |
| `ReadoutMethodGovernanceConfig` | Blocking modes, claim-boundary policy |
| `ReadoutMethodGovernanceReport` | Top-level governance report |
| `ReadoutGovernanceEligibilityPacket` | Eligibility summary for future readout planner |
| `AssignmentArtifactGovernanceSummary` | Assignment artifact readiness for readout governance |
| `InstrumentGovernanceSummary` | Per-instrument governance stance |
| `EstimandGovernanceSummary` | Estimand declaration and claim compatibility |
| `UncertaintySemanticsGovernanceSummary` | Readout semantics alignment for claim types |
| `DiagnosticSensitivityGovernanceSummary` | Diagnostic/sensitivity slot eligibility (not selection) |
| `ReadoutClaimEligibilityReport` | Per-claim-type eligibility outcome |
| `ReadoutClaimBoundaryReport` | Authorization boundary flags |
| `ProductionReadoutBlockerReport` | Production role blockers |
| `ReadoutMethodGovernanceFailurePacket` | Structured failure when governance cannot proceed |

---

## 11. Readout governance statuses

| Status | Meaning |
|--------|---------|
| `READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING` | Assignment artifact and at least one instrument pass governance gates for future readout **planning**; does not authorize execution or claims |
| `READOUT_GOVERNANCE_ELIGIBLE_WITH_WARNINGS` | Eligible with preserved warnings |
| `READOUT_GOVERNANCE_PROVISIONAL` | Incomplete clarity; governed policy may allow provisional planning review |
| `READOUT_GOVERNANCE_RESTRICTED_RESEARCH_ONLY` | Research-only path; production readout blocked |
| `READOUT_GOVERNANCE_DIAGNOSTIC_ONLY` | Diagnostic instruments only; no primary causal readout planning |
| `READOUT_GOVERNANCE_BLOCKED_BY_ASSIGNMENT_ARTIFACT` | Missing or invalid assignment artifact |
| `READOUT_GOVERNANCE_BLOCKED_BY_ASSIGNMENT_RUNTIME_STATUS` | Assignment runtime blocked or not ready |
| `READOUT_GOVERNANCE_BLOCKED_BY_INSTRUMENT_GOVERNANCE` | All relevant instruments blocked |
| `READOUT_GOVERNANCE_BLOCKED_BY_METHOD_SUITABILITY` | Method suitability handoff blocked |
| `READOUT_GOVERNANCE_BLOCKED_BY_ESTIMAND_GOVERNANCE` | Estimand declaration insufficient |
| `READOUT_GOVERNANCE_BLOCKED_BY_UNCERTAINTY_SEMANTICS` | Uncertainty/readout semantics incompatible |
| `READOUT_GOVERNANCE_BLOCKED_BY_SCENARIO_POLICY` | Scenario policy blocked |
| `READOUT_GOVERNANCE_BLOCKED_BY_POWER_MDE_READINESS` | Power/MDE readiness blocks inference-ready planning |
| `READOUT_GOVERNANCE_BLOCKED_BY_DESIGN_STRUCTURE` | Design structure blocked |
| `READOUT_GOVERNANCE_BLOCKED_BY_DATA_READINESS` | Profiler/data gate blocked |
| `READOUT_GOVERNANCE_BLOCKED_BY_INFERENCE_BOUNDARY` | Inference boundary guardrail would block |
| `READOUT_GOVERNANCE_BLOCKED_BY_READOUT_SEMANTICS_MISMATCH` | Point/interval target mismatch |
| `READOUT_GOVERNANCE_BLOCKED_BY_GEOMETRY_MISMATCH` | Geometry incompatible with instrument |
| `READOUT_GOVERNANCE_BLOCKED_BY_POOLED_MULTICELL` | Pooled multi-cell claim path blocked |
| `READOUT_GOVERNANCE_REQUIRES_REDESIGN_RECHECK` | Redesign/recheck required before governance |
| `READOUT_GOVERNANCE_REQUIRES_REVIEW` | Human review required |
| `READOUT_GOVERNANCE_NOT_EVALUATED` | Governance not yet evaluated |

---

## 12. Instrument governance statuses

| Status | Meaning |
|--------|---------|
| `INSTRUMENT_ELIGIBLE_FOR_READOUT_REVIEW` | Instrument may be considered in future readout planning review |
| `INSTRUMENT_ELIGIBLE_WITH_WARNINGS` | Review-eligible with warnings |
| `INSTRUMENT_RESTRICTED` | Restricted research path only |
| `INSTRUMENT_DIAGNOSTIC_ONLY` | Diagnostic slot only; not primary causal readout |
| `INSTRUMENT_BLOCKED` | Instrument blocked for readout governance |
| `INSTRUMENT_NOT_EVALUATED` | Instrument governance not evaluated |

Instrument governance preserves `method_instrument_suitability_matrix` compatibility dimensions (design, estimand, assignment, power/MDE, scenario policy, catalog governance) without re-running method suitability.

---

## 13. Claim eligibility statuses

| Status | Meaning |
|--------|---------|
| `CLAIM_ELIGIBILITY_NOT_AUTHORIZED` | Claim type not authorized at governance layer |
| `CLAIM_ELIGIBILITY_RESEARCH_POINT_ONLY` | Point-estimate research claim may be planned with caveats |
| `CLAIM_ELIGIBILITY_RESEARCH_DIAGNOSTIC_ONLY` | Diagnostic claim path only |
| `CLAIM_ELIGIBILITY_RESTRICTED_CAVEATED` | Caveated restricted eligibility |
| `CLAIM_ELIGIBILITY_ELIGIBLE_FOR_GOVERNED_PLANNING` | Claim type may appear in future governed readout plan spec; **not execution authorization** |
| `CLAIM_ELIGIBILITY_BLOCKED_BY_ASSIGNMENT` | Assignment artifact blocks claim |
| `CLAIM_ELIGIBILITY_BLOCKED_BY_INSTRUMENT` | Instrument governance blocks claim |
| `CLAIM_ELIGIBILITY_BLOCKED_BY_ESTIMAND` | Estimand governance blocks claim |
| `CLAIM_ELIGIBILITY_BLOCKED_BY_UNCERTAINTY_SEMANTICS` | Uncertainty semantics block claim |
| `CLAIM_ELIGIBILITY_BLOCKED_BY_PRODUCTION_READOUT_POLICY` | Production policy blocks claim |
| `CLAIM_ELIGIBILITY_NOT_EVALUATED` | Claim eligibility not evaluated |

---

## 14. Readout claim types

| Claim type | Default governance stance |
|------------|---------------------------|
| `POINT_ESTIMATE_READOUT_CLAIM` | Research planning only when estimand + semantics aligned |
| `PERIOD_LEVEL_EFFECT_CLAIM` | Requires estimand + geometry alignment |
| `CUMULATIVE_EFFECT_CLAIM` | Requires interval target alignment |
| `AVERAGE_POST_PERIOD_EFFECT_CLAIM` | Requires estimand declaration |
| `FRACTIONAL_LIFT_CLAIM` | Blocked unless scale explicitly governed |
| `LEVEL_LIFT_CLAIM` | Research planning only with estimand |
| `INCREMENTAL_OUTCOME_CLAIM` | Research planning only with estimand |
| `DIRECTIONAL_SIGNAL_CLAIM` | Not equivalent to null rejection |
| `NULL_DECISION_CLAIM` | Requires explicit null-decision rule |
| `INTERVAL_COVERAGE_CLAIM` | Requires coverage target naming |
| `CAUSAL_INTERVAL_CLAIM` | Blocked unless uncertainty semantics support causal target |
| `PREDICTION_INTERVAL_CLAIM` | Prediction/forecast classification only |
| `FORECAST_INTERVAL_CLAIM` | Forecast classification only |
| `DIAGNOSTIC_DISAGREEMENT_CLAIM` | Diagnostic slot only |
| `SENSITIVITY_ANALYSIS_CLAIM` | Sensitivity slot only |
| `MULTICELL_PER_CELL_CLAIM` | Per-cell only; no pooling |
| `POOLED_MULTICELL_CLAIM` | **Blocked by default** |
| `INCREMENTAL_LIFT_ROI_CLAIM` | **Blocked by default** at governance layer |
| `PRODUCTION_TRUST_REPORT_CLAIM` | **Always blocked** |
| `CALIBRATION_SIGNAL_CLAIM` | **Always blocked** |
| `MMM_INGESTION_CLAIM` | **Always blocked** |

---

## 15. Assignment artifact governance

Future governance evaluates assignment artifacts against:

| Status | Meaning |
|--------|---------|
| `ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE` | Plan, candidate, allocations, and reproducibility manifest present |
| `ASSIGNMENT_ARTIFACT_READY_WITH_WARNINGS` | Ready with warnings |
| `ASSIGNMENT_ARTIFACT_PROVISIONAL` | Provisional artifact |
| `ASSIGNMENT_ARTIFACT_MISSING_REPRODUCIBILITY_MANIFEST` | Reproducibility manifest missing |
| `ASSIGNMENT_ARTIFACT_MISSING_ALLOCATIONS` | Unit/cell allocations missing |
| `ASSIGNMENT_ARTIFACT_BLOCKED_BY_CONSTRAINTS` | Constraint violations block governance |
| `ASSIGNMENT_ARTIFACT_BLOCKED_BY_RUNTIME` | Assignment runtime blocked |
| `ASSIGNMENT_ARTIFACT_NOT_GENERATED` | No assignment artifact |
| `ASSIGNMENT_ARTIFACT_NOT_EVALUATED` | Not evaluated |

Required fields: `assignment_plan`, `assignment_candidate`, `assignment_unit_allocations`, `assignment_reproducibility_manifest`, `assignment_runtime_status`, `constraint_summary`, `exclusion_trace`, `method_suitability_handoff_summary`.

---

## 16. Instrument governance treatment

- Consume `method_instrument_suitability_matrix` without recomputing method suitability.
- Map instrument `suitability_status` to instrument governance status.
- Preserve `blocking_reasons`, `warnings`, `diagnostic_only_reason`, and `restricted_reason`.
- Block readout governance when all instruments are `INSTRUMENT_BLOCKED`.
- Restrict to diagnostic governance when only `INSTRUMENT_DIAGNOSTIC_ONLY` instruments remain.
- **Do not** select primary, sensitivity, or diagnostic stack winner.
- **Do not** execute estimators or inference.

---

## 17. Estimand governance treatment

- Consume `estimand_labels` and `estimand_gate_report` from method suitability handoff.
- Block claim eligibility when estimand declaration is missing or incompatible with contrast type.
- Preserve dosage, difference-in-policy, budget-reallocation, and go-live review requirements.
- Map claim types to declared estimand (period-level, cumulative, average post-period, lift).
- Estimand presence does **not** authorize causal claims or production readout.

---

## 18. Uncertainty semantics treatment

Align with `INFERENCE_READOUT_SEMANTICS_001` classifications:

| Classification | Governance effect |
|----------------|-------------------|
| `point_only_no_uncertainty` | Interval/coverage claims blocked |
| `prediction_interval_only` | Causal interval claims blocked |
| `forecast_interval_only` | Causal interval claims blocked |
| `resampling_interval_target_ambiguous` | Causal interval claims restricted |
| `causal_interval_candidate_requires_validation` | Causal interval planning caveated only |
| `causal_interval_validated_in_scope` | Future promotion path only; not authorized here |
| `blocked_due_to_readout_mismatch` | All interval claims blocked |
| `blocked_due_to_geometry_mismatch` | Readout governance blocked |
| `blocked_due_to_leakage_risk` | Causal claims blocked |

Governance records `uncertainty_sources_included` / `uncertainty_sources_excluded` requirements for future readout plans without computing uncertainty.

---

## 19. Diagnostic and sensitivity treatment

Diagnostic/sensitivity **slot types** are defined for future readout plan contracts only:

| Slot type | Purpose |
|-----------|---------|
| `PRIMARY_READOUT_SLOT` | Future primary readout position (not selected here) |
| `SENSITIVITY_READOUT_SLOT` | Future sensitivity position (not selected here) |
| `DIAGNOSTIC_READOUT_SLOT` | Diagnostic readout position |
| `NULL_PLACEBO_DIAGNOSTIC_SLOT` | Placebo/null diagnostic position |
| `DISAGREEMENT_DIAGNOSTIC_SLOT` | Cross-method disagreement diagnostic |

When instruments are diagnostic-only, only diagnostic/sensitivity slots may be governance-eligible. **No stack selection or diagnostic execution occurs in this artifact.**

---

## 20. Production-readout blockers

The following roles are **always blocked** at readout method governance:

- `trust_report`
- `calibration_signal`
- `mmm_ingestion`
- `llm_decisioning`
- `production_recommendation`
- `automated_budget_action`
- `external_export`
- `production_decision`

Aligned with `DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001`. Governance eligibility for planning does not relax these blockers.

---

## 21. Readiness gates

1. `profiler_data_readiness_gate`
2. `geo_unit_market_feasibility_gate`
3. `spend_feasibility_gate`
4. `power_mde_readiness_gate`
5. `design_cell_structure_gate`
6. `scenario_policy_feasibility_gate`
7. `assignment_feasibility_gate`
8. `method_suitability_gate`
9. `assignment_artifact_gate`
10. `assignment_reproducibility_manifest_gate`
11. `instrument_governance_gate`
12. `estimand_governance_gate`
13. `uncertainty_semantics_gate`
14. `inference_boundary_gate`
15. `readout_governance_packet_gate`

---

## 22. Claim boundaries (authorization flags)

All authorization flags are **false** in this contract, including:

- `readout_plan_generated`
- `primary_readout_stack_selected` / `sensitivity_stack_selected` / `diagnostic_stack_selected`
- `method_winner_selected`
- `estimator_execution_implemented` / `inference_execution_implemented`
- `diagnostic_sensitivity_execution`
- `p_value_computed` / `confidence_interval_computed`
- `lift_computed` / `roi_computed`
- `causal_claim_authorized` / `incremental_lift_roi_claim_authorized`
- `production_readout_authorization_granted`
- `mmm_runtime_calls_implemented` / `llm_decisioning_authorized`

---

## 23. Future implementation tests

Documented for `READOUT_METHOD_GOVERNANCE_RUNTIME_001`:

- blocked upstream gates block readout governance
- missing assignment artifact blocks governance
- all instruments blocked blocks governance
- diagnostic-only instruments restrict governance
- estimand missing blocks claim eligibility
- uncertainty semantics mismatch blocks causal interval claims
- pooled multicell claim blocked by default
- production roles always blocked
- assignment generated does not authorize causal claims
- instrument eligible does not authorize estimator execution
- governance eligible does not generate readout plan

---

## 24. Non-goals

- No readout plan generation
- No primary/sensitivity/diagnostic stack selection
- No estimator or inference execution
- No effect, lift, or ROI computation
- No p-values or confidence intervals
- No causal or incremental-lift/ROI claim authorization
- No production readout authorization
- No MMM runtime calls or LLM decisioning
- No assignment generation or method winner selection

---

## 25. Recommended next artifact

**Primary:** `READOUT_PLAN_CONTRACT_001`

**Alternative:** `READOUT_METHOD_GOVERNANCE_RUNTIME_001`

`READOUT_PLAN_CONTRACT_001` should define the future governed readout plan contract (primary/sensitivity/diagnostic stack specification) consuming this governance eligibility packet — still without estimator execution or claim authorization unless explicitly scoped in that contract.

---

## 26. Completion confirmation

| Area | Confirmed |
|------|-----------|
| Readout governance statuses | ✅ 22 statuses defined |
| Instrument governance statuses | ✅ 6 statuses defined |
| Claim eligibility statuses | ✅ 11 statuses defined |
| Readout claim types | ✅ 21 claim types defined |
| Assignment artifact governance | ✅ 9 statuses + required fields |
| Instrument governance treatment | ✅ Matrix preservation rules defined |
| Estimand governance treatment | ✅ Gate and claim mapping defined |
| Uncertainty semantics treatment | ✅ 9 classifications aligned to INFERENCE_READOUT_SEMANTICS_001 |
| Diagnostic/sensitivity treatment | ✅ 5 slot types defined; no selection |
| Production-readout blockers | ✅ 8 roles always blocked |
| Future tests | ✅ 24 tests documented |
| Claim boundaries | ✅ All authorization flags false |

**Final verdict:** `readout_method_governance_contract_defined_no_estimator_execution_or_causal_claim_authorization`
