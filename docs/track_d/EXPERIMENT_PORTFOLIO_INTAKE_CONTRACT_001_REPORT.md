# EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` |
| **Artifact type** | `experiment_portfolio_intake_contract` |
| **Status** | `completed` |
| **Base commit** | `d022dec` (Define geo KPI spend data contract and profiler spec) |
| **Contract scope** | `adaptive_intake_contract_no_runtime` |
| **Final verdict** | `experiment_portfolio_intake_contract_defined_no_runtime_authorization` |

This artifact is a **contract/specification document only**. It defines adaptive intake behavior and typed planning-intent outputs. **No runtime intake agents, profilers, planners, estimators, or production recommendations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data modes and profiler contracts |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Intake agent tooling framework |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | Planner architecture |
| `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | Contract sequencing |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |

---

## 3. Reason for intake contract

Downstream deterministic diagnostics require a typed planning-intent packet before geo/KPI/spend profiling, feasibility checks, or design generation. Without an explicit intake contract, Cursor/agents may use long static questionnaires, ask irrelevant portfolio questions for single tests, recommend design before data diagnostics, or claim feasibility from intake answers alone.

---

## 4. Adaptive intake principle

**Core principle:** The intake layer should minimize questions, ask only adaptive high-level questions, request sample/full KPI-spend data as early as possible, and produce a typed planning intent packet for deterministic diagnostics.

**The intake layer does not:**

- decide feasibility
- authorize design
- authorize p-values/CIs
- select estimators

---

## 5. Non-questionnaire UX principle

The LLM must **not** use a static long questionnaire. Questions are conditional on prior answers. Irrelevant branches are skipped. One test → no multi-test portfolio priority questions unless necessary.

---

## 6. Supported intake branches

| Branch | Description |
|--------|-------------|
| `single_test_full_data_available` | One test; full panel ready |
| `single_test_sample_schema_only` | One test; sample for schema inference |
| `single_test_ballpark_only` | One test; ballpark inputs only |
| `multi_test_full_data_available` | Multiple tests; full panel |
| `multi_test_sample_schema_only` | Multiple tests; sample schema |
| `multi_test_ballpark_only` | Multiple tests; ballpark only |
| `unknown_test_count` | Test count unclear |
| `data_unavailable` | No data and no ballpark yet |
| `insufficient_high_level_context` | Missing region/KPI/goal |

---

## 7. Minimal high-level questions

**Core questions (smallest useful set):**

1. What are you trying to test?
2. Which region/market?
3. Which KPI matters most?
4. How many tests in this planning window?
5. Decision-grade p-values/CIs, directional evidence, or prior-building?
6. Can you provide weekly/daily geo-level KPI and spend data (sample first)?

---

## 8. Branch-specific follow-up rules

| Branch | Follow-up |
|--------|-----------|
| Single test | Region, KPI, window, claim level, data availability only |
| Multi-test | Which Tier 1 must-win; which Tier 2 directional; which Tier 3 prior-building |
| No data | Ballpark: geo count, duration, KPI volume, spend, manipulation type |
| Unknown count | Ask count; default one-test with caveat if unanswered |

---

## 9. Data request strategy

Request data in order:

1. Full geo-unit × date/week × KPI × spend panel
2. Sample schema if full data not ready
3. Ballpark planning inputs if no data available

References `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` for field semantics and claim ceilings per mode.

---

## 10. Sample schema mode routing

Route to `request_sample_schema` → `route_to_geo_kpi_spend_profiler` when sample available. **No final design feasibility claims.** Outputs labeled provisional. `DataAvailabilityIntent = sample_schema_available`.

---

## 11. Full panel mode routing

Route to `request_full_panel_data` → `route_to_geo_kpi_spend_profiler` when full panel available. Supports downstream feasibility diagnostics when profiler quality gates pass. `DataAvailabilityIntent = full_panel_available`.

---

## 12. Ballpark mode routing

Route to `request_ballpark_inputs` → `route_to_ballpark_feasibility_mode` when no data. **Provisional only.** Full contract in `BALLPARK_FEASIBILITY_MODE_CONTRACT_001`. No final design, p-values, or CIs. `DataAvailabilityIntent = ballpark_only`.

---

## 13. Single-test intake behavior

- Ask only region, KPI, planning window, claim level, data availability
- Do not ask full multi-test priority questions
- Route to profiler if data available; ballpark if not
- Default to maximum-sensitivity design **intent** (not authorization)
- Note full market capacity may be consumed for planning window

---

## 14. Multi-test portfolio intake behavior

- Ask Tier 1 must-win vs Tier 2 directional vs Tier 3 prior-building
- Request geo KPI/spend data
- Route to portfolio feasibility diagnostics
- **Do not claim** requested portfolio is feasible from intake alone

---

## 15. Tier 1 / Tier 2 / Tier 3 claim-intent intake

| Tier | `ReadoutClaimIntent` value | Intake captures |
|------|---------------------------|-----------------|
| Tier 1 | `decision_grade_p_value_ci` or `decision_grade_point_estimate_only` | Must-win decision-grade |
| Tier 2 | `directional_diagnostic` | Directional evidence |
| Tier 3 | `prior_building` | MMM/MTA/Bayesian prior-building |

Intake captures intent only; does not authorize claims.

---

## 16. KPI selection intake

Capture `KpiIntent`: primary KPI name, optional secondary/guardrail KPIs, unit semantics if known. Do not infer KPI from spend columns. Reference `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` for profiler validation.

---

## 17. Region and geo-unit intake

Capture `RegionMarketIntent` and `GeoUnitPreferenceOrUnknown`. User may specify region without geo-unit type; profiler infers later. Country/region aggregate alone is insufficient for randomized testing unless decomposed.

---

## 18. Planning-window intake

Capture `PlanningWindowIntent`: `history_start`, `history_end`, `planning_window_start`, `planning_window_end`. Pre-period vs planning-window must be separable for downstream diagnostics.

---

## 19. Spend/budget-intent intake

Capture `SpendBudgetIntent`: available spend or unknown, planning-window budget if known, business tolerance for go-dark. **Do not infer** spend constraints without data or explicit ballpark inputs.

---

## 20. Manipulation-type intake: go-dark, heavy-up, go-live

Capture `ManipulationIntent` per test: `go_dark`, `heavy_up`, `go_live`, or `unknown`. Intake records user-stated preference; spend contrast diagnostics validate later.

---

## 21. Missing-input handling

Emit `MissingCriticalInputReport` listing required fields not yet provided. Route to `ask_minimal_missing_high_level_questions` or `block_until_required_context_available`. Never fill gaps with invented values.

---

## 22. Typed intake output contracts

| Contract | Purpose |
|----------|---------|
| `ExperimentPortfolioPlanningIntent` | Top-level planning packet |
| `ExperimentGoalSummary` | Stated test goals |
| `PlanningWindowIntent` | Time windows |
| `RegionMarketIntent` | Region/market scope |
| `GeoUnitPreferenceOrUnknown` | Unit type preference |
| `KpiIntent` | KPI selection |
| `RequestedTestPortfolio` | Per-test requests |
| `ReadoutClaimIntent` | Claim level per test |
| `SpendBudgetIntent` | Spend/budget context |
| `ManipulationIntent` | Go-dark/heavy-up/go-live |
| `DataAvailabilityIntent` | Data mode state |
| `MissingCriticalInputReport` | Missing fields |
| `RecommendedDataRequest` | What to upload next |
| `IntakeRoutingDecision` | Next routing step |
| `IntakeClaimBoundaryReport` | Allowed claim ceiling |

### `ExperimentPortfolioPlanningIntent` required fields

`intent_id`, `created_at`, `intake_mode`, `planning_scope`, `region_market`, `planning_window`, `primary_kpi`, `requested_test_count`, `test_requests`, `readout_claim_requirements`, `data_availability_state`, `recommended_next_step`, `claim_boundaries`.

### `RequestedTestPortfolio` per-test fields

`test_id`, `channel_or_campaign`, `business_priority`, `requested_tier`, `required_claim_level`, `manipulation_type`, `available_spend_or_unknown`, `can_be_shadow_or_prior_building`.

---

## 23. Downstream routing contracts

`IntakeRoutingDecision` routes to one of:

- `request_full_panel_data`
- `request_sample_schema`
- `request_ballpark_inputs`
- `route_to_geo_kpi_spend_profiler`
- `route_to_ballpark_feasibility_mode`
- `ask_minimal_missing_high_level_questions`
- `block_until_required_context_available`

Downstream consumers: `GEO_KPI_SPEND_DATA_PROFILER_001`, `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`, `PORTFOLIO_TEST_TIERING_ENGINE_001`.

---

## 24. LLM answerability boundaries

**LLM may:** summarize user goals; ask minimal adaptive follow-ups; request full panel/sample/ballpark inputs; explain why data is required; produce intake routing decision.

**LLM may not:**

- claim design feasibility from intake alone
- claim spend sufficiency from intake alone
- claim enough geo units from intake alone
- claim p-values/CIs from intake
- select final estimator from intake
- authorize production readout claims

---

## 25. New cross-cutting contract roadmap additions

Three contracts added after MIP audit pattern:

| Contract | Why needed |
|----------|------------|
| `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | Prevents agents from inventing what they did, evidence used, or failures |
| `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | Preserves source workflow, input data, governance status, downstream use |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Deterministic regression for agents, UI, API, notebooks, demos, LLM explanations |

These precede profiler runtime and demo agents.

---

## 26. Revised roadmap sequence

| # | Artifact |
|---|----------|
| 1–7 | Portfolio checkpoint through geo KPI/spend data contract (✅) |
| 8 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` (✅ this contract) |
| 9 | `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` |
| 10 | `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` |
| 11 | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` |
| 12–23 | Profiler through model fallback router |
| 24 | `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` |

---

## 27. Governance boundaries

All authorization flags remain **false**:

- Intake, profiler, agent run packet, artifact registry, golden path runtime
- LLM intake interpretation, design recommendation
- Production p-values, CIs, selector/router, downstream integrations

`design_feasibility_authorized_from_intake: false`  
`p_values_or_cis_authorized_from_intake: false`

---

## 28. Fixture/scenario test requirements

Minimum 16 scenarios: single-test avoids multi-test questionnaire; multi-test tier essentials; unknown count fallback; full panel/sample/ballpark routing; data unavailable blocking; decision-grade intent captured not authorized; directional/prior-building intents; go-dark/heavy-up/go-live intents; LLM cannot claim design feasibility or p-values/CIs from intake; roadmap includes cross-cutting contracts.

---

## 29. Recommended next artifact

`PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` — stable run packets before profiler runtime or demo agents.

Profiler implementation (`GEO_KPI_SPEND_DATA_PROFILER_001`) follows agent packet, provenance, and golden-path contracts.

---

## 30. Final verdict

**`experiment_portfolio_intake_contract_defined_no_runtime_authorization`**

Adaptive minimal intake, nine supported branches, fifteen typed output contracts, three-step data request order, LLM boundaries, and three cross-cutting roadmap contracts documented. All runtime authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001_summary.json` |
| Harness | `panel_exp/validation/experiment_portfolio_intake_contract_001.py` |
