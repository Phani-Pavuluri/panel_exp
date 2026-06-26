# EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` |
| **Artifact type** | `experiment_portfolio_planner_agent_tooling_contract` |
| **Status** | `completed` |
| **Base commit** | `88f1b15` (Define experiment portfolio planner agent roadmap) |
| **Final verdict** | `experiment_portfolio_planner_agent_tooling_contract_defined_no_runtime_authorization` |

This artifact is a **roadmap/governance/tooling-contract document only**. It defines readiness contracts for planner agent modules. **No runtime agents, estimators, inference engines, design assignment algorithms, budget optimization, production recommendations, or downstream integrations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | Nine-module planner architecture |
| `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` | Portfolio prioritization; design before estimator |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Design/estimator/inference separation |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Shared-control/multiplicity boundaries |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |
| `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001` | Deferred package-side agent boundaries |
| `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001` | SCM governance context |

---

## 3. Reason for tooling contract

`EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` defined **what** the planner architecture should do. This artifact defines **how we know each agent has the right tools** before it can generate reports or help the LLM answer user questions.

Without typed contracts, deterministic diagnostics, explicit failure modes, and claim boundaries, an LLM could invent feasibility, power, spend requirements, or design suitability. This contract prevents that.

---

## 4. Tool-first, agent-second principle

**Core principle:** `tool_first_agent_second`

Agents assemble reports from deterministic modules. They do not invent diagnostics. Each agent is a thin orchestration layer over typed tools that produce auditable evidence reports.

---

## 5. No-tool-no-claim rule

**Core rule:** No deterministic diagnostic → no LLM claim.

| Missing diagnostic | Blocked claim |
|--------------------|---------------|
| Matchability diagnostic | Matched pairs are feasible |
| Spend contrast diagnostic | Budget is sufficient |
| Randomization inference diagnostic | Valid p-values |
| CI validation diagnostic | Valid confidence intervals |
| Portfolio feasibility report | Multiple tests are feasible |

The LLM may explain results and ask adaptive high-level questions, but **cannot invent** feasibility, power, spend, p-values, CIs, match quality, or design suitability.

---

## 6. Planned agent/tool architecture

Nine agents from the planner roadmap, each with required contracts/modules, output reports, and claim boundaries:

```
Intake → Data Profiler → Geo Feasibility → Portfolio Planner
    → Spend/Budget → Design Generator → [Design Inference | Model Fallback]
    → LLM Explanation (grounded in typed reports only)
```

---

## 7. Typed input contract requirements

Every agent/tool module must declare:

- input schema (field names, types, required/optional)
- validation rules (range checks, enum constraints)
- upstream report dependencies
- ballpark-mode vs full-data-mode variants
- version identifier for contract evolution

Example intake contracts: `ExperimentPlanningIntent`, `ExperimentGoal`, `ReadoutTierRequest`, `PlanningWindow`, `KPISelection`, `DataAvailabilityState`, `MissingCriticalFieldReport`.

---

## 8. Deterministic diagnostic module requirements

Every diagnostic module must:

- produce the same output for the same input (no LLM, no randomness without seed)
- declare assumptions and preconditions
- emit structured warnings/errors with codes
- record input hash and module version in output metadata
- fail closed when preconditions are not met

---

## 9. Typed output report requirements

20 required report types (minimum):

`PlanningIntentReport`, `DataProfileReport`, `ColumnMappingReport`, `GeoTimeCoverageReport`, `UsablePanelSummary`, `GeoUnitFeasibilityReport`, `MatchabilityReport`, `MarketConcentrationReport`, `PortfolioFeasibilityReport`, `TierAssignmentPlan`, `SpendContrastFeasibilityReport`, `CellSpendPlan`, `EffectSizeSensitivityTable`, `CandidateDesignSet`, `DesignFeasibilityScores`, `DesignBasedInferencePlan`, `InferenceValidityDiagnostics`, `ModelFallbackRecommendation`, `EstimatorEligibilityReport`, `ClaimBoundaryReport`.

Each report must include: report ID, agent/module source, timestamp, input references, claim level allowed, and explicit uncertainty/limitations.

---

## 10. Failure mode requirements

Each module must document:

- **hard blockers** — agent cannot proceed; report status `blocked`
- **warnings** — agent proceeds with degraded claims; report status `warning`
- **missing-input fallbacks** — ballpark mode or request-more-data path
- **upstream dependency failures** — propagate with clear attribution

No silent degradation. Missing upstream report → downstream agent must not emit claims requiring that report.

---

## 11. Claim boundary requirements

Each agent has explicit allowed and forbidden claims (see §13). A `ClaimBoundaryReport` aggregates per-session claim ceilings based on available diagnostics and release-gate state.

Production point estimates, p-values, CIs, selector/router use, and downstream decisioning require **separate authorization** — none granted by this contract.

---

## 12. LLM answerability rules

The LLM explanation layer:

**May:** summarize typed reports; ask adaptive follow-up questions; explain tradeoffs and feasible alternatives; state when evidence is missing.

**May not:** invent diagnostics, feasibility, p-values, CIs, spend requirements, match quality, design suitability, or method authorization.

**Required inputs before explanation:** `PlanningIntentReport`, `DataProfileReport`, `GeoUnitFeasibilityReport`, `PortfolioFeasibilityReport`, `SpendContrastFeasibilityReport`, `CandidateDesignSet`, `DesignBasedInferencePlan`, `ModelFallbackRecommendation`, `ClaimBoundaryReport`.

No freeform LLM-generated report is authoritative without typed diagnostic backing.

---

## 13. Agent-by-agent tooling requirements

### 13.1 Intake / Goal Clarifier Agent

**Contracts:** `ExperimentPlanningIntent`, `ExperimentGoal`, `ReadoutTierRequest`, `PlanningWindow`, `KPISelection`, `DataAvailabilityState`, `MissingCriticalFieldReport`

**Output reports:** `PlanningIntentReport`, `MissingInputReport`, `RecommendedDataRequest`

**Allowed:** summarize stated goals; identify missing context; request sample/full KPI+spend data.

**Forbidden:** recommend design, p-values, CIs, spend levels, or estimator.

### 13.2 Data Profiler / Cleaner Agent

**Modules:** `schema_detector`, `column_mapper`, `time_grain_detector`, `geo_unit_detector`, `duplicate_detector`, `missingness_profiler`, `coverage_profiler`, `outlier_detector`, `low_volume_unit_detector`, `spend_kpi_summary_profiler`, `channel_campaign_availability_detector`

**Output reports:** `DataProfileReport`, `ColumnMappingReport`, `GeoTimeCoverageReport`, `DataQualityWarningReport`, `UsablePanelSummary`

**Allowed:** report detected geo/time/KPI/spend structure; data quality issues; usable unit count.

**Forbidden:** recommend design feasibility alone; claim p-values/CIs.

### 13.3 Geo Unit and Market Feasibility Agent

**Modules:** `eligible_unit_filter`, `geo_size_concentration_diagnostic`, `pre_period_kpi_variation_diagnostic`, `pair_block_matchability_diagnostic`, `trend_similarity_diagnostic`, `interference_spillover_risk_checklist`, `minimum_cell_size_diagnostic`, `unit_count_sufficiency_diagnostic`, `dma_gma_state_province_custom_unit_mapper`

**Output reports:** `GeoUnitFeasibilityReport`, `MatchabilityReport`, `MarketConcentrationReport`, `DesignUnitInventory`, `FeasibilityStatusReport`

**Allowed:** unit sufficiency for candidate design classes; too-few-unit risks; DMA/GMA/state/province/custom constraints.

**Forbidden:** final design feasibility without spend and portfolio diagnostics.

### 13.4 Portfolio Planner Agent

**Modules:** `test_request_parser`, `priority_scorer`, `tier_assignment_feasibility_checker`, `multi_test_capacity_checker`, `claim_level_feasibility_checker`, `portfolio_alternative_generator`

**Output reports:** `PortfolioFeasibilityReport`, `TierAssignmentPlan`, `PortfolioDesignAlternatives`, `BlockedRequestedTests`, `DowngradeRecommendations`

**Allowed:** test count/tier mix feasibility; Tier 1/2/3 alternatives.

**Forbidden:** spend feasibility without `SpendContrastFeasibilityReport`; valid p-values/CIs without inference diagnostics.

### 13.5 Spend Contrast / Budget Reallocation Agent

**Modules:** `spend_baseline_profiler`, `cell_level_spend_simulator`, `go_dark_contrast_calculator`, `heavy_up_contrast_calculator`, `go_live_contrast_calculator`, `budget_sufficiency_checker`, `effect_size_mde_sensitivity_calculator`, `budget_reallocation_searcher`, `business_cost_summary_generator`

**Output reports:** `SpendContrastFeasibilityReport`, `CellSpendPlan`, `EffectSizeSensitivityTable`, `BudgetGapReport`, `SpendReallocationRecommendations`

**Allowed:** spend contrast feasibility; go-dark/heavy-up/go-live comparison; spend shifting, duration, tier downgrade, fewer cells.

**Forbidden:** budget optimization execution; production design or budget authorization.

### 13.6 Candidate Design Generator

**Modules:** `single_test_design_generator`, `dedicated_control_design_generator`, `shared_control_multi_arm_generator`, `mutually_exclusive_multi_arm_generator`, `blocked_matched_design_generator`, `prioritized_full_power_plus_shadow_generator`, `factorial_fractional_factorial_generator`, `rotating_staggered_restricted_generator`, `design_scoring_function`, `design_feasibility_comparator`

**Output reports:** `CandidateDesignSet`, `DesignFeasibilityScores`, `RecommendedDesignCandidate`, `RejectedDesignsWithReasons`, `DesignAssumptionReport`

**Allowed:** candidate design classes when diagnostics support; reject designs with insufficient units/spend/match; mark rotating/staggered restricted.

**Forbidden:** authorize final production design; claim p-values/CIs without inference diagnostics.

### 13.7 Design-Based Inference Fast Path

**Modules:** `blocked_difference_estimator`, `matched_pair_estimator`, `cuped_ancova_adjusted_estimator`, `randomization_permutation_inference`, `shared_control_covariance_handler`, `multiplicity_correction`, `small_sample_warning_system`, `ci_construction_diagnostics`

**Output reports:** `DesignBasedInferencePlan`, `AllowedClaimLevel`, `InferenceValidityDiagnostics`, `PValueAuthorizationRecommendation`, `CIValidityRecommendation`

**Allowed:** recommend design-based inference when supported; say p-values/CIs eligible for review when diagnostics pass.

**Forbidden:** authorize production p-values/CIs without release gate.

### 13.8 Model-Based Fallback Router

**Modules:** `tbrridge_eligibility_checker`, `synthetic_did_eligibility_checker`, `augsynth_ascm_eligibility_checker`, `bayesian_tbr_eligibility_checker`, `method_claim_boundary_checker`, `method_specific_diagnostics_availability_checker`

**Output reports:** `ModelFallbackRecommendation`, `EstimatorEligibilityReport`, `AllowedClaimsByEstimator`, `RequiredValidationBeforeProduction`

**Allowed:** recommend model-based fallback; explain restriction/diagnostic-only status.

**Forbidden:** authorize model-based p-values/CIs without method-specific validation and release gate.

### 13.9 LLM Explanation Layer

**Required inputs:** all typed reports listed in §12.

**Allowed:** summarize/explain typed reports; adaptive questions; tradeoffs; state missing evidence.

**Forbidden:** invent any diagnostic, feasibility, p-value, CI, spend, or authorization claim.

---

## 14. Report generation architecture

```
raw/sampled user data
  → data profiler
  → typed data quality reports
  → geo/unit feasibility diagnostics
  → portfolio/tier feasibility diagnostics
  → spend contrast diagnostics
  → candidate design generation
  → inference/model routing
  → typed evidence packet
  → report generator
  → LLM explanation grounded in report
```

No freeform LLM-generated report is authoritative without typed diagnostic backing.

---

## 15. Tool-readiness gates

Each agent/tool is **not available** until it has:

| Gate | Requirement |
|------|-------------|
| `typed_input_contract` | Schema defined and versioned |
| `typed_output_report` | Output report type registered |
| `deterministic_implementation` | Same input → same output |
| `failure_mode_behavior` | Blockers/warnings documented and tested |
| `unit_tests` | Module-level tests pass |
| `scenario_tests` | End-to-end scenario coverage |
| `fixture_coverage` | Representative data fixtures |
| `claim_boundary_tests` | Forbidden claims blocked |
| `summary_json_report_generation_tests` | Report JSON schema validated |

---

## 16. Scenario/evaluation harness requirements

Required scenario tests (minimum 16):

| Scenario | Expected behavior |
|----------|-------------------|
| Single test, enough units/spend | Tier 1 feasible path |
| Single test, too few units | Blocked with unit-count reason |
| Five-test portfolio, insufficient units | Downgrade recommendations |
| Five tests: 2 Tier 1, 2 Tier 2, 1 Tier 3 | Feasibility assessment |
| Shared-control feasible, correlated contrasts | Warning required |
| Mutually exclusive multi-arm, too few cells | Rejected with reason |
| Heavy-up contrast too weak | Spend gap report |
| Go-dark business-cost warning | Business cost surfaced |
| Go-live ramp-up warning | Ramp-up risk surfaced |
| Rotating/staggered restricted | Carryover risk block |
| Missing KPI column | Hard blocker |
| Missing spend column | Degraded to ballpark or blocker |
| Daily data detected | Time grain reported |
| Weekly data detected | Time grain reported |
| Province/state unit count too small | Unit sufficiency blocked |
| DMA/GMA/custom mapping needed | Mapping request emitted |

---

## 17. User-facing answerability matrix

| User question | Required report |
|---------------|-----------------|
| Can I run 5 tests? | `PortfolioFeasibilityReport` |
| How many should be Tier 1? | `TierAssignmentPlan` |
| Do I have enough geos? | `GeoUnitFeasibilityReport` |
| Should I use shared control? | `CandidateDesignReport` plus shared-control diagnostics |
| How much spend do I need? | `SpendContrastFeasibilityReport` |
| Can I get valid p-values? | `InferenceValidityDiagnostics` plus release-gate state |
| Can I get valid CIs? | `CIValidityRecommendation` plus release-gate state |
| Should I use AugSynth? | `ModelFallbackRecommendation` plus method eligibility diagnostics |
| Can this feed MMM? | `ClaimBoundaryReport` or CalibrationSignal readiness |

---

## 18. Revised roadmap sequence

| # | Artifact | Status |
|---|----------|--------|
| 1 | `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` | ✅ Complete |
| 2 | `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001` | ✅ Complete |
| 3 | `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` | Active SCM lane |
| 4 | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | ✅ Complete |
| 5 | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | ✅ This artifact |
| 6 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Next planner implementation lane |
| 7–13 | Profiler → … → Model fallback router | Planned |
| 14 | `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | Post-planner method lane |

---

## 19. Governance boundaries

All authorization flags remain **false**:

- Planner runtime and per-agent runtime flags
- `planner_agent_tooling_contract_runtime_authorized`
- Design-based inference production
- Model-based fallback router
- LLM explanation layer production
- Production design recommendation
- Production p-values, causal CIs, selector/router
- Downstream: TrustReport, CalibrationSignal, MMM, LLM decisioning, live API, scheduler, budget optimization, package-side agents

SCM state unchanged: `production_candidate_gated`; no production inference, p-values, or causal CIs.

---

## 20. Risks and ambiguities

1. **Contract proliferation** — many report types may overlap; registry discipline required.
2. **Ballpark mode claim creep** — coarse inputs must cap claim levels strictly.
3. **LLM grounding enforcement** — runtime must reject explanations without report references.
4. **Shared-control diagnostics gap** — joint covariance tooling may lag design generator.
5. **Implementation order** — intake contract vs profiler may need parallel scaffolding.
6. **Release-gate coupling** — p-value/CI answerability depends on external gate state.

---

## 21. Recommended next artifact

`EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` — first planner implementation lane defining `ExperimentPlanningIntent` and related intake contracts.

---

## 22. Final verdict

**`experiment_portfolio_planner_agent_tooling_contract_defined_no_runtime_authorization`**

Tool-first/agent-second principle, no-tool-no-claim rule, typed reports, readiness gates, scenario tests, and LLM answerability matrix are defined. All runtime and production authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001_summary.json` |
| Harness | `panel_exp/validation/experiment_portfolio_planner_agent_tooling_contract_001.py` |
