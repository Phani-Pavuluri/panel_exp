# SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001` |
| **Artifact type** | `spend_requirement_and_manipulation_feasibility_contract` |
| **Status** | `completed` |
| **Scope** | `contract_amendment_no_runtime_diagnostics` |
| **Amends/supersedes** | `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` |
| **Base commit** | `638dde7` (Align spend contrast contract with control-plane boundary spec) |
| **Final verdict** | `spend_requirement_and_manipulation_feasibility_contract_defined_no_runtime_diagnostics_or_production_authorization` |

This artifact is a **contract/specification amendment only**. It expands the spend module scope beyond spend-direction/contrast checking. **No runtime spend diagnostics, response curve computation, MMM runtime integration, power/MDE computation, design generation, lift/ROI, budget optimization, or production authorization was implemented or authorized.**

---

## 2. Source-of-truth files inspected

| File | Role |
|------|------|
| `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` | Prior narrow spend contrast contract (amended) |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Spend coverage and data semantics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo unit/market readiness gate |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Zero vs missing spend rules |

---

## 3. Reason this contract amendment is needed

`SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` framed the spend module mainly as spend-direction/contrast checking. The intended module is broader:

1. Validate spend data at the design-required grain.
2. Derive baseline and historical spend inventory from uploaded data.
3. Translate KPI/MDE targets into spend requirements only when an explicit response bridge is supplied.
4. Compare required spend contrast against feasible manipulations.

Without this amendment, implementation would under-scope baseline inventory, response bridging, dosage/difference-in-policy options, historical support checks, and control contamination warnings.

---

## 4. Core goal statement

The spend module validates spend data at the design-required grain, derives baseline and historical spend summaries by geo/cell/channel/time, optionally bridges KPI MDE into spend requirements using advisory response evidence, and emits feasible/provisional/blocked manipulation options for go-dark, heavy-up, go-live, budget reallocation, and dosage/difference-in-policy experiments. It does not compute MDE, estimate lift/ROI, choose final designs, optimize budget, select estimators, or authorize production decisions.

---

## 5. Relationship to profiler and geo unit/market feasibility diagnostics

| Upstream | Role |
|----------|------|
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Spend column mapping, coverage, missingness, zero vs missing |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo units and time coverage ready for downstream planning |

Future spend module implementation consumes profiler and geo feasibility outputs. It must not upgrade blocked, sample-schema, or ballpark upstream reports.

---

## 6. Relationship to earlier spend contrast contract

This artifact **supersedes or amends** `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001`.

The earlier contract remains useful for spend coverage/contrast/status taxonomy (`SpendCoverageStatus`, `SpendContrastStatus`, `SpendContrastQuality`, claim boundaries). This artifact expands scope to:

- Required spend (statistical vs business-response)
- Response bridge (MMM, proxy, back-of-napkin)
- Baseline spend inventory derivation
- Dosage contrast / difference-in-policy as first-class options
- Historical support checks
- Control contamination and estimand shift flags
- Manipulation feasibility planning (candidate options, not final design)

**Recommended next implementation:** `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` (expanded scope; supersedes `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` naming).

---

## 7. Module architecture — five subreports

| Subreport | Purpose |
|-----------|---------|
| `SpendDataReadinessReport` | Validate spend data at design-required grain |
| `BaselineSpendInventoryReport` | Derive baseline/historical spend from uploaded data |
| `ResponseBridgeReport` | Optional KPI MDE → required spend delta bridge |
| `ManipulationFeasibilityReport` | Compare required spend vs feasible manipulations |
| `PlanningBoundaryReport` | State allowed/blocked claims |

Top-level future contract: `SpendRequirementAndManipulationFeasibilityReport` composing the five subreports.

---

## 8. SpendDataReadinessReport

**Purpose:** Validate that spend data exists at the level needed for test design.

**Must cover:**

- Geo/time/channel/campaign grain
- Cell assignment availability when design cells exist
- Missing spend
- Zero vs missing spend
- Negative spend without correction/credit flag
- Duplicate spend rows
- Mixed planned vs observed spend
- Currency mismatch
- Missing baseline window
- Missing test/planning window
- Spend source/channel mapping
- Sample-schema and ballpark boundaries

**Status reuse:** May inherit `SpendCoverageStatus` from prior contract (`AVAILABLE`, `PARTIAL`, `MISSING`, `NOT_REQUESTED`).

---

## 9. BaselineSpendInventoryReport

**Purpose:** Derive baseline and historical spend from uploaded data when structure is sufficient.

The module can derive baseline spend from uploaded panel data if the baseline window and grain are known.

**Required summary fields:**

| Field | Definition |
|-------|------------|
| `baseline_mean_weekly_spend` | Mean weekly spend over pre-period window |
| `baseline_median_weekly_spend` | Median weekly spend over pre-period |
| `baseline_total_spend` | Total spend over pre-period |
| `baseline_p10_weekly_spend` | 10th percentile weekly spend |
| `baseline_p90_weekly_spend` | 90th percentile weekly spend |
| `historical_p95_spend` | 95th percentile historical weekly spend |
| `historical_max_spend` | Maximum observed weekly spend |
| `nonzero_weeks` | Count of weeks with observed nonzero spend |
| `missing_weeks` | Count of weeks with missing spend (not zero) |
| `max_reducible_spend` | Maximum spend available to reduce for go-dark |

**Support levels:** geo, cell, channel, campaign/platform (if available), time window, cell × channel, geo × channel.

**Rules:**

- Baseline spend = average or total spend over declared/derived pre-period window
- Max reducible spend for go-dark cannot exceed observed/planned baseline spend
- Missing spend must not be treated as zero

---

## 10. ResponseBridgeReport

**Purpose:** Represent the optional bridge from KPI MDE / business target into required spend delta.

**Important:** KPI may be total conversions/ARR/etc. while spend is channel-level. The experiment estimand is the effect of changing channel spend policy on total KPI. The spend module must not pretend to observe channel-attributed KPI unless such data is explicitly supplied.

**Supported response bridge sources:**

| Source | Description |
|--------|-------------|
| `NONE` | No bridge; required spend delta unknown |
| `USER_PROVIDED_REQUIRED_SPEND_DELTA` | User supplies required spend delta directly |
| `POWER_LAYER_REQUIRED_SPEND_DELTA` | Required delta from design/power/sensitivity layer |
| `MMM_RESPONSE_CURVE` | MMM response curve (advisory) |
| `MMM_ROMS` | MMM return on marginal spend (advisory) |
| `PRIOR_EXPERIMENT` | Prior experiment lift/spend evidence |
| `PROXY_RESPONSE_CURVE` | Proxy curve from related level |
| `BACK_OF_NAPKIN_USER_ASSUMPTION` | User assumption (e.g. conversions per dollar) |

**Two required spend concepts:**

| Concept | Definition |
|---------|------------|
| **Statistical required spend contrast** | Spend delta supplied by design/power/sensitivity logic or user assumption |
| **Business-response required spend** | Spend delta estimated from MMM, prior experiment, proxy curve, or user assumption to reach KPI MDE/business target |

**Required flags:**

`MMM_ADVISORY_SIGNAL_USED`, `MMM_OUT_OF_SUPPORT`, `OUT_OF_MMM_SUPPORT`, `MMM_CALIBRATION_WEAK`, `PROXY_RESPONSE_USED`, `PROXY_LEVEL_MISMATCH`, `BACK_OF_NAPKIN_ASSUMPTION_USED`, `BUSINESS_RESPONSE_RISK`, `REQUIRED_SPEND_DELTA_UNKNOWN`, `REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY`, `REQUIRED_SPEND_DELTA_SUPPLIED`

**Proxy-level handling:** When test level differs from MMM modeled level, curves/ROMS may be used only as proxy/advisory evidence with explicit mismatch flags. Preserve modeled level, requested test level, and proxy mapping.

**The module must not use MMM as proof of ROI or causal truth.**

---

## 11. ManipulationFeasibilityReport

**Purpose:** Compare required spend delta against feasible spend manipulation options.

**Supported manipulation options:**

| Option | Definition |
|--------|------------|
| `GO_DARK` | Reduce spend in treatment/test cell relative to business-as-usual control |
| `HEAVY_UP` | Increase spend in treatment/test cell relative to business-as-usual control |
| `GO_LIVE` | Move from near-zero/no baseline spend to active spend |
| `BUDGET_REALLOCATION` | Decrease source spend and increase destination spend with explicit mapping |
| `DOSAGE_CONTRAST` | Compare two or more intentionally manipulated spend policies (low vs high) |
| `DIFFERENCE_IN_POLICY` | Explicit policy contrast when controls may also be manipulated |
| `UNKNOWN` | Manipulation type not declared; provisional only |

**Required calculations (future implementation):**

| Calculation | Formula |
|-------------|---------|
| `go_dark_max_delta` | Baseline spend available to reduce, floored at zero |
| `required_heavy_up_spend` | `baseline_spend + required_spend_delta` |
| `required_heavy_up_multiplier` | `required_heavy_up_spend / baseline_spend` |
| `dosage_delta` | `high_spend_policy - low_spend_policy` |
| `budget_gap` | `required_incremental_budget - available_test_budget` |

**Feasibility outputs:**

`GO_DARK_FEASIBLE`, `GO_DARK_INSUFFICIENT_BASELINE_SPEND`, `HEAVY_UP_FEASIBLE`, `HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT`, `HEAVY_UP_MULTIPLIER_HIGH`, `GO_LIVE_FEASIBLE`, `GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND`, `BUDGET_REALLOCATION_FEASIBLE`, `BUDGET_REALLOCATION_MAPPING_INCOMPLETE`, `DOSAGE_CONTRAST_FEASIBLE`, `DOSAGE_CONTRAST_ESTIMAND_REQUIRED`, `INSUFFICIENT_CONTRAST`, `BLOCKED_MISSING_SPEND`, `PROVISIONAL_REQUIRED_SPEND_UNKNOWN`

**Historical support checks:**

`within_historical_support`, `near_upper_historical_support`, `above_historical_support`, `far_above_historical_support`, `unknown_historical_support`

**Control contamination flags:**

`CONTROL_CELL_MANIPULATED`, `CONTROL_CONTAMINATION_RISK`, `BUSINESS_AS_USUAL_CONTROL_NOT_PRESERVED`, `ESTIMAND_SHIFT_REQUIRED`, `STANDARD_GO_DARK_INTERPRETATION_NOT_ALLOWED`

**Clarification:** Heavying up a control cell and going dark in a test cell can create a valid difference-in-policy or dosage contrast only if the estimand is explicitly changed. It should not be interpreted as a standard go-dark versus business-as-usual control test.

---

## 12. PlanningBoundaryReport

**Purpose:** State what can and cannot be claimed.

**Required fields:**

| Field | Default |
|-------|---------|
| `standard_go_dark_interpretation_allowed` | Per manipulation/control context |
| `dosage_contrast_estimand_required` | When controls manipulated |
| `method_suitability_review_required` | When estimand shifts |
| `business_as_usual_control_preserved` | Per cell manipulation context |
| `mmm_advisory_used` | When MMM bridge used |
| `proxy_response_used` | When proxy bridge used |
| `production_authorization_granted` | `false` |
| `roi_authorized` | `false` |
| `lift_authorized` | `false` |
| `design_authorized` | `false` |
| `estimator_inference_authorized` | `false` |
| `budget_optimization_authorized` | `false` |

The spend module may emit **candidate manipulation options**, not final design recommendations.

---

## 13. Dosage / difference-in-policy experiments

Dosage contrast is **not conceptually invalid**. It is valid only when the design explicitly estimates a low-spend vs high-spend policy contrast.

| Point | Rule |
|-------|------|
| Estimand | Not the same as standard go-dark against business-as-usual control |
| Control manipulation | If controls are also manipulated, standard untreated-control assumptions may not hold |
| Method layer | SCM/TBR/matched-market estimators relying on untreated controls may have conceptual issues unless method layer supports dosage estimand |
| Spend module role | Flag estimand shift; require method-suitability review |
| Boundary | Must not decide final estimator/inference validity |

---

## 14. KPI MDE to spend translation

When KPI is total conversions/ARR/sales and spend is channel-level, the module does not observe channel-attributed KPI unless explicitly supplied. The experimental estimand is the effect of changing channel spend policy on total KPI. To translate KPI MDE into spend, the module needs a response bridge.

**Allowed bridge examples:** MMM response curve, MMM ROMS, prior experiment, CLS, user-provided conversion-per-dollar assumption, planner-provided required spend delta, back-of-napkin assumption, proxy curve from related level.

**Formula examples:**

- Linear marginal response: `required_spend_delta = KPI_MDE / expected_KPI_per_dollar`
- Nonlinear curve: find ΔSpend such that `f(baseline_spend + ΔSpend) - f(baseline_spend) >= KPI_MDE`
- Go-dark: find reduction r such that `f(baseline_spend) - f(baseline_spend - r) >= KPI_MDE`
- Dosage contrast: find low/high policies such that `f(high_spend) - f(low_spend) >= KPI_MDE`

**Example narrative:**

> MDE is 500 conversions per cell. MMM advisory curve suggests a $100K/week spend delta is expected to produce only ~180 incremental conversions, below the 500-conversion MDE. Business-response risk: high.

**Required warnings:**

- MMM/ROMS translation is advisory, not experimental proof
- Proxy-level use must be flagged
- Out-of-curve-support use must be flagged
- Business-response risk when spend delta likely cannot produce KPI MDE

---

## 15. Allowed diagnostic scope

Future implementation **may:**

- Validate spend data readiness at design grain
- Derive baseline/historical spend inventory
- Accept optional response bridge inputs
- Show KPI MDE in actual units when supplied
- Translate KPI MDE to advisory required spend when bridge exists
- Compare required spend vs feasible manipulations
- Emit candidate manipulation options with feasibility status
- Flag MMM/proxy/back-of-napkin use as advisory
- Flag control contamination and estimand shift

---

## 16. Disallowed / non-goal scope

Always disallow:

- Runtime implementation (this artifact)
- Power/MDE computation
- MMM runtime calls
- MMM calibration
- Causal lift estimation
- ROI estimation
- Budget optimization
- Candidate design finalization
- Treatment/control assignment
- Estimator/inference selection
- Production authorization
- LLM decisioning

---

## 17. Claim boundaries

**Always false:**

`final_experiment_feasibility_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `power_authorized`, `mde_authorized`, `p_value_authorized`, `confidence_interval_authorized`, `lift_authorized`, `roi_authorized`, `method_recommendation_authorized`, `portfolio_tiering_authorized`, `budget_optimization_authorized`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`, `final_design_recommendation_authorized`, `estimator_inference_authorized`

**Allowed future positive claim:** candidate manipulation options with feasibility status; readiness to feed power/design layers when contrast and inventory are sufficient (diagnostic only).

---

## 18. LLM/control-plane boundary

Package-side deterministic contract work. LLM/control-plane may later route users to spend diagnostics, ask for missing inputs, and explain typed reports. It must not infer spend requirements from raw data without typed reports or upgrade advisory bridges into ROI/causal/production claims.

---

## 19. Report-builder boundary

Report builders may render typed spend module outputs. They must not compute diagnostics, power, MDE, design feasibility, lift, ROI, budget recommendations, or production claims.

---

## 20. Future implementation acceptance criteria

Future `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` should:

- Derive baseline spend from uploaded data when grain/window sufficient
- Emit blocked/provisional when grain/window insufficient
- Preserve missing vs zero spend and planned vs observed labels
- Compute max go-dark reducible spend
- Compute required heavy-up spend and multiplier when `required_spend_delta` exists
- Compare proposed spend to historical p90/p95/max
- Flag high multiplier and out-of-support spend
- Support dosage/difference-in-policy as first-class option
- Flag control contamination and estimand shift
- Support budget reallocation source/destination mapping
- Accept optional response bridge inputs
- Show KPI MDE in actual units when supplied
- Translate KPI MDE to advisory required spend only when bridge supplied
- Flag MMM/proxy/back-of-napkin as advisory
- Emit candidate manipulation options, not final design recommendation
- Never compute power/MDE, lift, ROI, budget optimization, estimator validity, or production authorization

Suggested API: `evaluate_spend_requirement_and_manipulation_feasibility(profile_report, geo_feasibility_report, config=None) -> SpendRequirementAndManipulationFeasibilityReport`

---

## 21. Future tests expected

1. Baseline spend derived from pre-period data
2. Baseline blocked when pre-period missing
3. Zero spend not treated as missing
4. Missing spend not treated as zero
5. Required heavy-up multiplier computed
6. Go-dark blocked when max reducible below required delta
7. Heavy-up feasible within historical support
8. Heavy-up warning above p95
9. Heavy-up blocked/warned far above historical max per config
10. Control heavy-up + test go-dark flags control contamination
11. Control heavy-up + test go-dark requires dosage/difference-in-policy estimand
12. Standard go-dark interpretation blocked when control manipulated
13. Dosage contrast feasible when policy delta meets required spend
14. Budget reallocation requires source/destination mapping
15. KPI MDE shown in actual units
16. MMM response bridge translates KPI MDE to advisory spend
17. MMM out-of-support flagged
18. Proxy-level mismatch flagged
19. Back-of-napkin assumption flagged
20. Business-response risk when expected response below KPI MDE
21. No ROI/lift/power/design/estimator/production authorization
22. No fixture-specific branching

---

## 22. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001 ✅
→ GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 ✅
→ SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001 ✅ (amended by this artifact)
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001 ✅ (this artifact)
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 (next implementation)
```

---

## 23. Recommended next artifact

**`SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`** — deterministic runtime implementation per this expanded contract.

---

## 24. Final verdict

**`spend_requirement_and_manipulation_feasibility_contract_defined_no_runtime_diagnostics_or_production_authorization`**

Spend requirement and manipulation feasibility contract defined. Five subreports, dosage/difference-in-policy as first-class options, KPI MDE to spend advisory bridge, MMM/proxy/back-of-napkin advisory flags, baseline inventory, historical support, control contamination, and estimand shift documented. No runtime diagnostics, power/MDE, MMM runtime, lift/ROI, design, or production authorization granted.
