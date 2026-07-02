# READOUT_PLAN_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `READOUT_PLAN_CONTRACT_001` |
| **Artifact type** | `readout_plan_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_estimator_execution_or_claim_authorization` |
| **Base commit** | `b4bb46f` (Define readout method governance contract) |
| **Final verdict** | `readout_plan_contract_defined_no_estimator_execution_or_claim_authorization` |

This artifact is a **contract/specification document only**. It defines the future governed contract for constructing a causal readout plan from assignment artifacts, method-suitability instrument matrices, readout-method governance packets, estimand governance, uncertainty semantics, diagnostics requirements, and sensitivity requirements. **No readout plan runtime, estimator execution, inference execution, diagnostic/sensitivity execution, claim authorization, or production readout authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `READOUT_METHOD_GOVERNANCE_CONTRACT_001` | Upstream governance eligibility contract |
| `DESIGN_ASSIGNMENT_RUNTIME_001` | Assignment artifact upstream |
| `METHOD_SUITABILITY_RUNTIME_001` | Instrument suitability matrix upstream |
| `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` | Estimand handoff upstream |
| `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001` | Assignment plan/candidate contract |
| `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` | Assignment feasibility upstream |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Design structure upstream |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario policy upstream |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE readiness upstream |
| `INFERENCE_READOUT_SEMANTICS_001` | Uncertainty semantics taxonomy |
| `DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001` | Production readout blockers |

---

## 3. Why this contract is needed

The current stack validates through assignment generation and readout method governance eligibility:

Profiler/data readiness → … → Method suitability with instrument matrix → Design assignment runtime → **Readout method governance eligibility**.

The next unanswered question is:

> Given governance eligibility, what must a future readout plan contain before estimator/inference execution may even be attempted?

Without this contract, future runtimes may:

- execute estimators without a governed planned stack
- treat governance eligibility as claim authorization
- select a method winner without preserving blocked/restricted instruments
- plan primary candidates from diagnostic-only instruments
- omit required diagnostics or sensitivity prerequisites
- emit lift/ROI claims without explicit claim-scope boundaries
- bypass reproducibility manifest or uncertainty semantics requirements

This contract defines the future readout plan packet structure, stack roles, instrument planning categories, readiness gates, claim scope, and reporting caveats — without generating or executing a plan.

---

## 4. Core goal statement

`READOUT_PLAN_CONTRACT_001` defines the future governed contract for constructing a causal readout plan from assignment artifacts, method-suitability instrument matrices, readout-method governance packets, estimand governance, uncertainty semantics, diagnostics requirements, and sensitivity requirements. It defines planned primary candidates, planned sensitivity checks, planned diagnostic checks, blocked instruments, execution prerequisites, claim-scope boundaries, and reporting caveats. It does not execute estimators, compute inference, estimate lift, calculate p-values/CIs, run diagnostics, run sensitivity checks, authorize causal claims, or authorize production readout.

---

## 5. Relationship to readout method governance contract

`READOUT_METHOD_GOVERNANCE_CONTRACT_001` decides whether assignment artifacts and instruments may **enter planning**. It emits readout governance statuses, claim eligibility statuses, and production-readout blockers.

This contract consumes `readout_method_governance_report` and `readout_method_governance_packet`. If readout governance is blocked, readout plan is blocked. **Governance eligibility does not mean a plan has been constructed, executed, or authorized.**

---

## 6. Relationship to assignment runtime

`DESIGN_ASSIGNMENT_RUNTIME_001` produces assignment plan, candidate, unit allocations, constraint/exclusion traces, and reproducibility manifest.

Future readout plan runtime must consume `design_assignment_runtime_report`, `assignment_plan`, `assignment_candidate`, `unit_allocation_report`, `constraint_trace`, `exclusion_trace`, and `reproducibility_manifest`. Missing or failed assignment artifacts block readout planning. Deterministic explicit-pool assignment limitations must be preserved in reporting caveats.

---

## 7. Relationship to method suitability runtime

`METHOD_SUITABILITY_RUNTIME_001` emits `instrument_suitability_matrix` with per-instrument governance compatibility.

Future readout plan runtime must consume `method_suitability_report`, `instrument_suitability_matrix`, and derived `eligible_instruments_for_planning`, `restricted_instruments`, `diagnostic_only_instruments`, and `blocked_instruments`. Planning operates on governed estimator/inference instruments, not broad method-family labels alone.

---

## 8. Conceptual distinctions

| # | Concept | Question answered | Rule |
|---|---------|-------------------|------|
| 1 | **Readout method governance** | May instruments/artifacts enter planning? | `READOUT_METHOD_GOVERNANCE_CONTRACT_001`; already defined |
| 2 | **Readout plan contract** | What must a future readout plan contain? | This artifact; does not plan at runtime |
| 3 | **Readout plan runtime** | What is the concrete planned stack? | Future `READOUT_PLAN_RUNTIME_001` only |
| 4 | **Estimator/inference execution** | What numeric readout is computed? | Future execution runtime only |
| 5 | **Diagnostic/sensitivity execution** | Are required checks satisfied? | Future execution runtime only |
| 6 | **Claim authorization** | Which claims are allowed? | Future governance layer; always false here |
| 7 | **Production readout report** | Product-facing reporting artifact | Future reporting layer; not implemented here |

---

## 9. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `ReadoutPlanInput` | Bundled governance packet, assignment artifacts, instrument matrix |
| `ReadoutPlanConfig` | Blocking modes, claim-scope policy |
| `ReadoutPlanReport` | Top-level readout plan contract report |
| `ReadoutPlanPacket` | Governed planned stack packet for downstream execution |
| `PlannedReadoutStack` | Container for primary/sensitivity/diagnostic candidates |
| `PrimaryReadoutCandidate` | Planned primary instrument candidate (not executed) |
| `SensitivityReadoutCandidate` | Planned sensitivity instrument candidate |
| `DiagnosticReadoutCandidate` | Planned diagnostic instrument candidate |
| `BlockedReadoutInstrument` | Instrument that must remain blocked in plan |
| `ReadoutExecutionPrerequisite` | Prerequisite before execution may be attempted |
| `ReadoutPlanEstimandScope` | Declared estimand scope for planned readout |
| `ReadoutPlanUncertaintyScope` | Uncertainty semantics scope for planned readout |
| `ReadoutPlanDiagnosticRequirement` | Required diagnostic check (not executed here) |
| `ReadoutPlanSensitivityRequirement` | Required sensitivity check (not executed here) |
| `ReadoutPlanClaimScope` | Planned claim scope (not authorized here) |
| `ReadoutPlanCaveat` | Reporting caveat attached to plan |
| `ReadoutPlanBlockingReason` | Structured blocking reason |
| `ReadoutPlanWarning` | Non-blocking warning |
| `ReadoutPlanStatus` | Readout plan readiness status enum |
| `ReadoutStackRole` | Role within planned stack |
| `ReadoutPlanClaimBoundaryReport` | Authorization boundary flags |

---

## 10. Readout plan statuses

| Status | Meaning |
|--------|---------|
| `READOUT_PLAN_READY_FOR_RUNTIME_PLANNING` | Future runtime may construct a plan; **does not mean stack selected, executed, or authorized** |
| `READOUT_PLAN_READY_WITH_WARNINGS` | Planning may proceed with preserved warnings |
| `READOUT_PLAN_PROVISIONAL` | Incomplete clarity; governed policy may allow provisional planning |
| `READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE` | Upstream governance blocked |
| `READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT` | Assignment artifact missing or failed |
| `READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS` | All instruments blocked |
| `READOUT_PLAN_BLOCKED_BY_ESTIMAND` | Estimand scope missing or incompatible |
| `READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS` | Uncertainty semantics missing or incompatible |
| `READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS` | Required diagnostics not specified |
| `READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS` | Required sensitivity checks not specified |
| `READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE` | Production governance blocks planning path |
| `READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN` | Diagnostic plan must be specified before execution |
| `READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN` | Sensitivity plan must be specified before execution |
| `READOUT_PLAN_NOT_EVALUATED` | Readout plan not yet evaluated |

---

## 11. Stack roles

| Role | Meaning |
|------|---------|
| `PRIMARY_READOUT_CANDIDATE` | Planned primary readout position; **not an executed estimator** |
| `SENSITIVITY_READOUT_CANDIDATE` | Planned sensitivity readout position |
| `DIAGNOSTIC_READOUT_CANDIDATE` | Planned diagnostic readout position |
| `BLOCKED_READOUT_INSTRUMENT` | Instrument that must remain blocked |
| `REFERENCE_ONLY_INSTRUMENT` | Reference context only; not a candidate |
| `NOT_EVALUATED_INSTRUMENT` | Instrument not yet evaluated for planning |

A planned primary candidate is not an executed estimator and not a production-authorized method.

---

## 12. Instrument planning categories

| Category | Meaning |
|----------|---------|
| `PLANNING_ELIGIBLE_PRIMARY_CANDIDATE` | May be planned as primary candidate |
| `PLANNING_ELIGIBLE_WITH_WARNINGS` | May be planned with warnings |
| `PLANNING_RESTRICTED_REQUIRES_REVIEW` | Restricted; requires review, caveats, and diagnostics |
| `PLANNING_DIAGNOSTIC_ONLY` | Diagnostic candidate only; not primary |
| `PLANNING_BLOCKED` | Must remain blocked |
| `PLANNING_NOT_EVALUATED` | Not evaluated for planning |

---

## 13. Future input dependencies

| Dependency | Source |
|------------|--------|
| `readout_method_governance_report` | Governance contract/runtime |
| `readout_method_governance_packet` | Governance eligibility packet |
| `design_assignment_runtime_report` | Assignment runtime |
| `assignment_plan` | Assignment runtime |
| `assignment_candidate` | Assignment runtime |
| `unit_allocation_report` | Assignment runtime |
| `constraint_trace` | Assignment runtime |
| `exclusion_trace` | Assignment runtime |
| `reproducibility_manifest` | Assignment runtime |
| `method_suitability_report` | Method suitability runtime |
| `instrument_suitability_matrix` | Method suitability runtime |
| `eligible_instruments_for_planning` | Derived from matrix |
| `restricted_instruments` | Derived from matrix |
| `diagnostic_only_instruments` | Derived from matrix |
| `blocked_instruments` | Derived from matrix |
| `estimand_governance_summary` | Governance/handoff |
| `uncertainty_governance_summary` | Governance/semantics |
| `required_diagnostics` | Plan specification |
| `required_sensitivity_checks` | Plan specification |
| `claim_eligibility_reports` | Governance contract |
| `production_governance_config` | Production blockers |

---

## 14. Future output concepts

| Output | Purpose |
|--------|---------|
| `ReadoutPlanReport` | Top-level plan contract report |
| `ReadoutPlanPacket` | Governed planned stack packet |
| `PlannedReadoutStack` | Primary/sensitivity/diagnostic candidate container |
| `PrimaryReadoutCandidate` | Planned primary candidate record |
| `SensitivityReadoutCandidate` | Planned sensitivity candidate record |
| `DiagnosticReadoutCandidate` | Planned diagnostic candidate record |
| `BlockedReadoutInstrument` | Blocked instrument record |
| `ReadoutExecutionPrerequisiteReport` | Execution prerequisites summary |
| `ReadoutPlanClaimScopeReport` | Planned claim scope (not authorization) |
| `ReadoutPlanCaveatReport` | Reporting caveats |
| `ReadoutPlanClaimBoundaryReport` | Authorization boundary flags |

---

## 15. ReadoutPlanPacket fields

| Field | Purpose |
|-------|---------|
| `artifact_id` | Artifact identifier |
| `design_id` | Design identifier |
| `readout_plan_status` | Plan readiness status |
| `assignment_artifact_summary` | Assignment artifact handoff summary |
| `readout_governance_summary` | Governance eligibility summary |
| `planned_primary_candidates` | Planned primary candidates only — **not executed, ranked, or production-authorized** |
| `planned_sensitivity_candidates` | Planned sensitivity candidates |
| `planned_diagnostic_candidates` | Planned diagnostic candidates |
| `blocked_instruments` | Instruments that must remain blocked |
| `not_evaluated_instruments` | Instruments not evaluated |
| `execution_prerequisites` | Prerequisites before execution |
| `estimand_scope` | Declared estimand scope |
| `uncertainty_scope` | Uncertainty semantics scope |
| `required_diagnostics` | Required diagnostic checks |
| `required_sensitivity_checks` | Required sensitivity checks |
| `claim_scope` | Planned claim scope (not authorization) |
| `reporting_caveats` | Caveats for reporting |
| `blocking_reasons` | Blocking reasons if plan blocked |
| `warnings` | Non-blocking warnings |
| `claim_boundary_report` | Authorization boundary flags |

---

## 16. Readiness gates

Future gate order (all must pass or explicit provisional policy applies):

1. `readout_method_governance_gate` — governance must not be blocked
2. `assignment_artifact_gate` — assignment artifact present and valid
3. `reproducibility_manifest_gate` — reproducibility manifest present
4. `eligible_restricted_instrument_gate` — at least one non-blocked instrument for planning path
5. `diagnostic_only_instrument_gate` — diagnostic-only path rules applied
6. `blocked_instrument_gate` — blocked instruments preserved
7. `estimand_scope_gate` — estimand scope declared and compatible
8. `uncertainty_semantics_gate` — uncertainty semantics declared and compatible
9. `diagnostics_requirement_gate` — required diagnostics listed or diagnostic plan required
10. `sensitivity_requirement_gate` — required sensitivity checks listed or sensitivity plan required
11. `execution_prerequisite_gate` — execution prerequisites enumerated
12. `claim_scope_boundary_gate` — claim scope bounded; no implicit authorization
13. `readout_plan_packet_gate` — packet complete for handoff

**Rules:**

- Readout governance blocked → readout plan blocked
- Assignment artifact missing/failed → readout plan blocked
- Reproducibility manifest missing → readout plan blocked
- All instruments blocked → readout plan blocked
- Only diagnostic-only instruments → no primary production candidate may be planned
- Estimand scope missing/incompatible → blocked or provisional
- Uncertainty semantics missing/incompatible → blocked or provisional
- Required diagnostics missing → `READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN`
- Required sensitivity checks missing → `READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN`

---

## 17. Primary/sensitivity/diagnostic stack treatment

- Future readout plan **may define** primary, sensitivity, and diagnostic **candidates**.
- Primary candidates must come from `PLANNING_ELIGIBLE_PRIMARY_CANDIDATE` or `PLANNING_RESTRICTED_REQUIRES_REVIEW` instruments.
- Diagnostic-only instruments may be planned **only** as diagnostic candidates.
- Blocked instruments must remain in `blocked_instruments`.
- Restricted instruments must carry restrictions, required diagnostics, and reporting caveats.
- **No candidate is executed by this contract.**
- **No method winner is selected by this contract.**
- **No production claim is authorized by this contract.**

---

## 18. Estimator/inference instrument treatment

Readout planning operates on governed **estimator/inference instruments**, not broad method labels alone.

| Example instrument | Planning notes |
|--------------------|----------------|
| DID + Bootstrap | May be primary candidate when eligible |
| SCM + Placebo | Often diagnostic candidate |
| SCM + UnitJackknife | Primary or sensitivity when eligible |
| TBR Ridge + BRB | Restricted; requires caveats and diagnostics |
| TBR Ridge + KFold | Restricted; leakage/split caveats |
| TBR Ridge + Placebo | Diagnostic or restricted sensitivity |
| AugSynth + Jackknife | Restricted/diagnostic per governance |
| MatchedPair + RandomizationInference | Requires matched-pair metadata |
| A/B + StandardInference | Individual-randomized designs only |

The plan must preserve instrument-level governance: governed, restricted, diagnostic-only, blocked, not evaluated.

---

## 19. Claim scope treatment

Readout plan may define **planned claim scope**, but it **cannot authorize claims**.

Claim scope must include:

- estimand
- population/unit scope
- time window
- metric/KPI
- assignment artifact reference
- planned instrument
- uncertainty semantics
- diagnostics prerequisites
- sensitivity prerequisites
- reporting caveats

**Rules:**

- ROI claims require additional governance and cannot be implied by lift plans.
- Diagnostic-only instruments cannot support production lift/ROI claims.
- Dosage contrast blocks standard incrementality claim scope unless explicitly scoped.
- Budget reallocation requires explicit source/destination estimand and blocks simple ROI claim scope.

---

## 20. Diagnostics and sensitivity treatment

Required diagnostics and sensitivity checks must be listed as **prerequisites**, not executed.

**Diagnostic examples:**

- pre-period fit
- placebo checks
- jackknife stability
- bootstrap stability
- parallel-trend diagnostics
- donor support
- outlier sensitivity
- assignment reproducibility
- spend support
- interference risk
- common-control conflict review

**Sensitivity examples:**

- donor pool sensitivity
- pre-period window sensitivity
- outlier exclusion sensitivity
- estimator specification sensitivity
- inference path sensitivity
- assignment algorithm caveat sensitivity

This contract does not execute diagnostics or sensitivity checks.

---

## 21. Examples

| # | Scenario | Expected outcome |
|---|----------|------------------|
| 1 | DID + Bootstrap eligible; SCM + Placebo diagnostic-only | DID+Bootstrap planned primary; SCM placebo planned diagnostic |
| 2 | Only diagnostic-only instruments available | No primary candidate allowed |
| 3 | All instruments blocked | `READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS` |
| 4 | Restricted TBR Ridge + BRB | Allowed only with caveats and required diagnostics |
| 5 | Dosage contrast estimand | Dosage-compatible plan; standard incrementality claim blocked |
| 6 | Budget reallocation estimand | Explicit source/destination scope; simple ROI claim blocked |
| 7 | Missing reproducibility manifest | Readout plan blocked |
| 8 | Missing uncertainty semantics | Blocked or provisional |
| 9 | Common-control unresolved conflict | Diagnostic/review plan required |
| 10 | Deterministic explicit-pool assignment | Assignment limitation preserved in caveats |

---

## 22. Claim boundaries

All authorization flags are **false** in this contract:

| Flag | Value |
|------|-------|
| `readout_plan_runtime_implemented` | false |
| `readout_plan_generated` | false |
| `primary_readout_stack_selected` | false |
| `sensitivity_stack_selected` | false |
| `diagnostic_stack_selected` | false |
| `method_winner_selected` | false |
| `estimator_execution_implemented` | false |
| `inference_execution_implemented` | false |
| `effect_estimate_computed` | false |
| `lift_computed` | false |
| `roi_computed` | false |
| `p_value_computed` | false |
| `confidence_interval_computed` | false |
| `uncertainty_computed` | false |
| `diagnostic_check_executed` | false |
| `sensitivity_check_executed` | false |
| `causal_claim_authorized` | false |
| `incremental_lift_claim_authorized` | false |
| `roi_claim_authorized` | false |
| `production_readout_authorized` | false |
| `production_authorization_granted` | false |
| `mmm_runtime_calls_implemented` | false |
| `mmm_calibration_authorized` | false |
| `llm_decisioning_authorized` | false |

Contract-level positives: `readout_plan_contract_defined`, `planned_readout_stack_contract_defined`, `primary_candidate_contract_defined`, `sensitivity_candidate_contract_defined`, `diagnostic_candidate_contract_defined`, `blocked_instrument_contract_defined`, `execution_prerequisite_contract_defined`, `claim_scope_contract_defined`, `reporting_caveat_contract_defined`, `claim_boundaries_defined` — all **true**.

---

## 23. Future implementation acceptance criteria

Future `READOUT_PLAN_RUNTIME_001` must:

- consume readout method governance packet
- consume assignment runtime artifact
- consume method suitability instrument matrix
- preserve governed/restricted/diagnostic-only/blocked instruments
- plan primary candidates only from eligible/restricted instruments
- plan diagnostic-only instruments only as diagnostics
- preserve blocked instruments
- require explicit estimand scope
- require uncertainty semantics
- require diagnostics prerequisites
- require sensitivity prerequisites
- emit planned stack packet
- emit claim scope and caveats
- **not** execute estimators
- **not** compute lift/ROI/p-values/CIs
- **not** authorize claims
- **not** authorize production

---

## 24. Future tests

Documented for `READOUT_PLAN_RUNTIME_001`:

- blocked readout governance blocks plan
- missing assignment artifact blocks plan
- missing reproducibility manifest blocks plan
- all instruments blocked blocks plan
- only diagnostic-only instruments prevents primary candidate
- restricted instrument carries caveats and diagnostics
- eligible instrument may become planned primary candidate
- diagnostic-only instrument only diagnostic candidate
- blocked instrument preserved
- dosage estimand prevents standard incrementality claim scope
- budget reallocation prevents simple ROI claim scope
- missing uncertainty semantics blocks/provisionalizes
- missing diagnostics requires diagnostic plan
- missing sensitivity requires sensitivity plan
- no estimator execution
- no inference execution
- no lift/ROI/p-values/CIs
- no claim authorization
- no production authorization
- no fixture-specific branching

---

## 25. Roadmap placement

Sits after `READOUT_METHOD_GOVERNANCE_CONTRACT_001` and before `READOUT_PLAN_RUNTIME_001` in the profiler/diagnostics → assignment → governance → **readout plan** sequencing lane.

---

## 26. Recommended next artifact

**Primary:** `READOUT_PLAN_RUNTIME_001`

**Alternative:** `READOUT_METHOD_GOVERNANCE_RUNTIME_001`

Neither is implemented in this artifact.

---

## 27. Completion confirmation

| Area | Confirmed |
|------|-----------|
| Readout plan boundary | Contract only; no runtime |
| Future contract concepts | 21 concepts defined |
| Readout plan statuses | 14 statuses defined |
| Stack roles | 6 roles defined |
| Instrument planning categories | 6 categories defined |
| Input dependencies | 21 dependencies defined |
| Output concepts | 11 concepts defined |
| Packet fields | 20 fields defined |
| Readiness gates | 13 gates in order |
| Primary/sensitivity/diagnostic treatment | Defined; no selection/execution |
| Estimator/inference instrument treatment | Instrument-level planning rules |
| Claim scope treatment | Scope defined; no authorization |
| Diagnostics/sensitivity treatment | Prerequisites listed; no execution |
| Examples | 10 examples documented |
| Future tests | 20 tests documented |

**Final verdict:** `readout_plan_contract_defined_no_estimator_execution_or_claim_authorization`
