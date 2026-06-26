# EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` |
| **Artifact type** | `experiment_portfolio_planner_agent_roadmap` |
| **Status** | `completed` |
| **Base commit** | `0984d85` (Log method portfolio prioritization checkpoint) |
| **Final verdict** | `experiment_portfolio_planner_agent_roadmap_defined_no_runtime_authorization` |

This artifact is a **roadmap/governance document only**. It defines the agreed experiment portfolio planner agent architecture direction. **No runtime agents, estimators, inference engines, production authorization, selector/router, MMM ingestion, LLM decisioning, or budget optimization was implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` | Strategic portfolio shift; SCM reference baseline |
| `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001` | SCM evidence packet |
| `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001` | Defer/closeout/handoff direction |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Design/estimator/inference separation |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Shared-control/multiplicity boundaries |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | Method portfolio context |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |
| `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001` | Deferred package-side agent boundaries |
| `AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001` | Post-planner method lane context |

---

## 3. Reason for roadmap

Prior roadmap momentum risked jumping from SCM closeout directly into AugSynth/ASCM estimator remediation without first answering the upstream product question: **what experiment designs can this region, geo portfolio, KPI/spend data, and business constraints actually support?**

Method selection (SCM, AugSynth, TBRRidge, Bayesian TBR) is premature when design feasibility, portfolio tiering, spend contrast, and unit availability are unknown. This roadmap records the agreed correction: add a **portfolio-planning lane** before estimator remediation.

---

## 4. Product principle

**Core principle:** The agent should minimize questions, maximize inference from uploaded KPI/spend data, and return feasible design alternatives with claim levels, spend requirements, and tradeoffs.

**Ordering principle:**

1. **Design selection comes before estimator selection.**
2. **Design feasibility diagnostics come before p-value/CI claims.**
3. **Production point estimates, p-values, CIs, selector/router use, and downstream decisioning require separate authorization.**

The platform should not begin by picking SCM/AugSynth/TBR. It should begin by understanding experiment planning context, available units, KPI/spend data, test portfolio, business priority, required claim level, and budget constraints.

---

## 5. User-experience principle

The LLM must **not** use a static long questionnaire.

It should ask **high-level adaptive questions only:**

| Question | Purpose |
|----------|---------|
| What are you trying to test? | Goal clarification |
| Which region/market? | Geo scope |
| How many tests in this planning window? | Portfolio sizing |
| Which KPI matters? | Outcome definition |
| Which tests need decision-grade p-values/CIs vs directional/prior-building evidence? | Tier assignment |
| Can you provide weekly or daily geo-level KPI and spend data (sample first)? | Data-first planning |

**Adaptive rules:**

- One test → do not ask multi-test portfolio priority unless needed.
- Five tests → ask which are must-win decision-grade vs directional/prior-building.
- No data → accept ballpark total-market weekly/daily KPI and spend numbers.

---

## 6. Adaptive intake strategy

The **Intake / Goal Clarifier Agent** collects minimal context, then defers granular feasibility to deterministic diagnostics on uploaded or ballpark data. Questions are conditional on prior answers. Irrelevant branches are skipped.

---

## 7. Data-first planning strategy

Uploaded geo/KPI/spend data is the primary source of:

- geo unit identification
- time grain
- spend availability and contrast potential
- unit volume/stability
- coverage gaps and outliers

Manual questions are fallback only when data is unavailable. Ballpark mode accepts aggregate weekly/daily KPI and spend totals for coarse feasibility screening.

---

## 8. Planner-agent architecture

Nine planned modules form a pipeline from intake through design recommendation, with estimator routing last:

```
Intake → Data Profiler → Geo Feasibility → Portfolio Planner
    → Spend/Budget → Design Generator → [Design Inference | Model Fallback]
    → LLM Explanation
```

All modules are **planned contracts only** in this artifact. No runtime implementation.

---

## 9. Agent responsibilities

| Module | Responsibilities |
|--------|------------------|
| **Intake / Goal Clarifier** | Minimal adaptive questions; region/window/KPI/test count/tier needs; request data; ballpark fallback |
| **Data Profiler / Cleaner** | Detect geo unit, time grain, KPI/spend/channel columns; missingness, duplicates, coverage gaps, outliers, low-volume units; data quality report |
| **Geo Unit and Market Feasibility** | Randomization units (DMA, GMA, province/state, city/metro, postal cluster, territory, custom); eligible unit counts; concentration; pair/block match quality; variation; spillover risk; multi-cell feasibility |
| **Portfolio Planner** | Test count feasibility; Tier 1/2/3 assignment; alternatives when infeasible; business-language tradeoffs |
| **Spend Contrast and Budget Reallocation** | Infer spend from data; go-dark/heavy-up/go-live feasibility; MDE/spend requirements; reallocation recommendations |
| **Candidate Design Generator** | Feasible design candidates across taxonomy (see §15) |
| **Design-Based Inference Fast Path** | Blocked/paired estimators, CUPED/ANCOVA, randomization/permutation, multiplicity, joint covariance for shared-control |
| **Model-Based Fallback Router** | Route to TBRRidge, Synthetic DiD, AugSynth/ASCM, Bayesian TBR only when design-based path is weak; preserve limited claims |
| **LLM Explanation Layer** | Explain design choice, infeasibility, tiering, spend, allowed claims, unsupported p-values/CIs |

---

## 10. Region and randomization-unit discovery

Supported unit types: DMA, GMA-like units, province/state, city/metro, postal cluster, sales territory, custom clusters.

Diagnostics: eligible unit count after exclusions, concentration, pair/block match quality, cross-unit variation, spillover/interference risk, and whether the region has too few units for multi-cell designs.

---

## 11. KPI/spend data requirements

Preferred input: weekly or daily geo-level panel with KPI outcome columns, spend columns (by channel/campaign where available), geo identifier, and date.

Minimum for coarse planning: ballpark total-market weekly/daily KPI and spend totals plus region scope.

---

## 12. Ballpark-input fallback mode

When full geo panel is unavailable, accept aggregate KPI/spend estimates for screening. Outputs carry wider uncertainty bands and lower tier ceilings. Ballpark mode cannot support Tier 1 decision-grade claims without later data upload and diagnostic pass.

---

## 13. Portfolio test tiering model

| Tier | Readout level | Claims |
|------|---------------|--------|
| **Tier 1** | Production-grade causal readout | Valid point estimate if diagnostics pass; p-value/CI only if design/inference supports; pre-specified estimand; strongest allocation; full diagnostics; highest spend/design priority |
| **Tier 2** | Directional causal / diagnostic readout | Point or directional estimate; diagnostic uncertainty unless inference diagnostics pass; limited claims; informs prioritization |
| **Tier 3** | Evidence collection / prior-building | Feed MMM/MTA/Bayesian prior library/calibration signals; **no** production incrementality claim; **no** production p-value/CI claim |

---

## 14. Spend contrast and budget feasibility model

Three manipulation types:

| Type | Description | Feasibility drivers |
|------|-------------|---------------------|
| **Go-dark** | Remove/reduce spend in designated geos | Business tolerance, baseline spend, lost volume, contrast strength |
| **Heavy-up** | Increase treatment spend vs control | Incremental spend delta vs KPI noise |
| **Go-live** | Launch new channel/campaign in treatment geos | Launch spend, ramp-up, platform learning, clean control exposure |

Spend constraints should be **inferred from uploaded data** where possible; manual input only when unavailable.

---

## 15. Design option taxonomy

| Design | Notes |
|--------|-------|
| Single full-power test | Default when units/spend support one Tier 1 test |
| Dedicated control design | Separate control pool per test |
| Shared-control multi-arm | Multiple treatments share control (see §16) |
| Mutually exclusive multi-arm | Each geo in exactly one arm (see §16) |
| Blocked/matched multi-arm | Pair/block structure for balance |
| Factorial/fractional factorial | When operations allow |
| Prioritized full-power + shadow | One Tier 1 plus lower-tier shadows |
| Rotating/staggered | **Restricted/risky only** (see §17) |

---

## 16. Shared-control vs mutually exclusive multi-arm distinction

**Mutually exclusive multi-arm:** Each geo belongs to exactly one arm (Control, Treatment A, B, C). Cleaner but more unit-hungry. Pairwise comparisons only when cell sizes and multiplicity policy support them.

**Shared-control multi-arm:** Multiple treatment arms reuse the same control group. More unit-efficient but statistically fragile. Treatment-vs-control contrasts are correlated. Requires joint covariance accounting, multiplicity correction, pre-specified contrasts, and **no independent-test fiction** (`MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`).

---

## 17. Rotating/staggered design restrictions

Rotating/staggered designs are **risky and restricted**, not default.

**Risks:** cool-off uncertainty, carryover, delayed conversion, adstock, brand memory, market contamination, seasonality across waves, competitive changes, budget pacing changes, platform learning resets.

**Allowed only if:** carryover window defined, adequate cool-off, KPI lag understood, short-lived campaign effects, seasonality controlled, wave comparability diagnostics pass.

---

## 18. Design-based inference fast path

When randomization/assignment supports it, prefer:

- blocked difference estimator
- paired estimator
- CUPED/ANCOVA adjustment
- randomization/permutation inference
- multiplicity correction
- joint covariance for shared-control designs

**Not production-authorized** until separate validation and release gates pass.

---

## 19. Model-based fallback path

Route to TBRRidge, Synthetic DiD, AugSynth/ASCM, or Bayesian TBR **only when** design-based inference is weak or insufficient.

Preserve limited claims unless method-specific inference validation exists. Model selection is **last**, not first.

---

## 20. Revised roadmap sequence

| # | Artifact | Status |
|---|----------|--------|
| 1 | `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` | ✅ Complete |
| 2 | `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001` | ✅ Complete |
| 3 | `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` | Active SCM lane |
| 4 | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | ✅ This artifact |
| 5 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | First planner implementation lane |
| 6 | `GEO_KPI_SPEND_DATA_PROFILER_001` | Planned |
| 7 | `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Planned |
| 8 | `PORTFOLIO_TEST_TIERING_ENGINE_001` | Planned |
| 9 | `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` | Planned |
| 10 | `CANDIDATE_DESIGN_GENERATOR_001` | Planned |
| 11 | `DESIGN_BASED_INFERENCE_FAST_PATH_001` | Planned |
| 12 | `MODEL_BASED_FALLBACK_ROUTER_001` | Planned |
| 13 | `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | Post-planner method lane |

Portfolio planning lanes (5–12) precede AugSynth/ASCM remediation. SCM closeout (3) remains immediate.

---

## 21. Future artifacts

| Artifact | Purpose |
|----------|---------|
| `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Intake/goal clarifier contracts |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler contracts |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Unit feasibility diagnostics |
| `PORTFOLIO_TEST_TIERING_ENGINE_001` | Tier assignment engine |
| `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` | Spend/budget diagnostics |
| `CANDIDATE_DESIGN_GENERATOR_001` | Design candidate generation |
| `DESIGN_BASED_INFERENCE_FAST_PATH_001` | Design-based inference contracts |
| `MODEL_BASED_FALLBACK_ROUTER_001` | Model fallback routing contracts |

---

## 22. Governance boundaries

All authorization flags remain **false**:

- Planner runtime modules (intake, profiler, feasibility, tiering, spend, design generator)
- Design-based inference production
- Model-based fallback router
- LLM design recommendation
- Production design recommendation
- Production p-values, causal CIs, selector/router
- Downstream: TrustReport, CalibrationSignal, MMM, LLM decisioning, live API, scheduler, budget optimization, package-side agents

Package-side/LLM agents remain **non-authorized** for production decisioning until later release gates (`FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001`).

SCM state unchanged: `production_candidate_gated`; no production inference, p-values, or causal CIs.

---

## 23. Risks and ambiguities

1. **Ballpark mode overconfidence** — coarse inputs may overstate Tier 1 feasibility.
2. **Shared-control multiplicity** — joint covariance and contrast pre-specification remain hard governance problems.
3. **Rotating/staggered temptation** — operations may prefer wave designs despite carryover risk.
4. **LLM scope creep** — explanation layer must not become design authority.
5. **Estimator pull-forward** — pressure to skip planner lanes and jump to AugSynth/SCM must be resisted.
6. **Data quality variance** — profiler outputs depend on upload quality; contracts must surface uncertainty.

---

## 24. Recommended next artifact

**Immediate:** `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` (SCM closeout lane).

**First planner implementation lane:** `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001`.

---

## 25. Final verdict

**`experiment_portfolio_planner_agent_roadmap_defined_no_runtime_authorization`**

The experiment portfolio planner agent architecture is defined as a roadmap direction. Design selection precedes estimator selection. Adaptive intake and data-first diagnostics precede method routing. All runtime, inference, production, and downstream authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001_summary.json` |
| Harness | `panel_exp/validation/experiment_portfolio_planner_agent_roadmap_001.py` |
