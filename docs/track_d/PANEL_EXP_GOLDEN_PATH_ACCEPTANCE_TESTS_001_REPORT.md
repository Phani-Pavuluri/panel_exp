# PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` |
| **Artifact type** | `panel_exp_golden_path_acceptance_tests_contract` |
| **Status** | `completed` |
| **Base commit** | `ee62ddb` (Define panel exp artifact registry provenance contract) |
| **Contract scope** | `golden_path_acceptance_contract_no_runtime` |
| **Final verdict** | `panel_exp_golden_path_acceptance_tests_defined_no_runtime_authorization` |

This artifact is a **contract/specification document only**. It defines deterministic golden-path and blocked-path acceptance scenarios for future panel_exp planner workflows. **No runtime golden-path tests, agents, registry storage, data profilers, planners, estimators, design algorithms, inference logic, p-values, confidence intervals, production recommendations, budget optimization, selector/router behavior, MMM ingestion, LLM decisioning, notebooks, demos, or downstream integrations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | Artifact registry, provenance, downstream-use policy |
| `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | Agent run packets, manifests, failure packets |
| `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Adaptive intake and planning intent |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data modes, profiler reports, input references |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Tool-first/agent-second framework |
| `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | Cross-cutting contract sequencing |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |

---

## 3. Reason for golden-path acceptance contract

Future profiler, planner, agent, and LLM workflows will span intake, data profiling, feasibility diagnostics, spend contrast, design generation, inference routing, and artifact registry. Without deterministic golden-path and blocked-path scenarios, implementations may ship with only happy-path coverage, missing provisional/blocked cases, allowing sample-schema or ballpark overclaims, shared-control independence fiction, weak spend contrast silent passes, LLM overclaiming diagnostics, or unregistered artifacts appearing usable.

This contract defines the regression spine **before** any profiler runtime, planner implementation, notebook, or demo.

---

## 4. Deterministic regression spine principle

**Core principles:**

- **Golden paths before demos** — no notebook/demo/API example until golden paths are stable
- **Blocked paths before production claims** — every happy path has paired failure/provisional paths
- **Every happy path must have a paired failure/provisional path**
- **Fixtures test behavior; fixtures do not define product branches**
- **Reports summarize deterministic outputs; reports do not perform hidden inference**
- **LLM consumes typed reports; LLM does not infer from raw fixtures/data**
- **No golden path may authorize** production readout, p-values, CIs, selector/router, MMM ingestion, LLM decisioning, live API, scheduler, or budget optimization
- Golden paths test deterministic workflows and claim boundaries, **not** runtime production readiness

---

## 5. Critical implementation anti-patterns

### 1. No fixture-specific product logic

Fixtures are test cases, not product branches. Future profiler/planner logic must be schema/category/contract based, not `fixture_id` based.

- **Bad:** `if fixture_id == "GP-001", treat as feasible DMA panel`
- **Good:** `if required columns exist + geo_unit_type=DMA + time_grain=weekly + coverage checks pass, then emit eligible internal-planning diagnostic`

### 2. No demo-specific workflow logic promoted to product paths

Demo sample files, golden-path fixtures, notebook examples, and real uploaded user data must remain separate modes until an explicit bridge contract exists.

### 3. Report builders must not become hidden inference engines

Report builders summarize deterministic workflow outputs. They must **not** calculate lift, ROI, power, MDE, budget allocation, p-values, confidence intervals, matched markets, treatment/control assignment, or method recommendations.

- **Bad:** report builder computes MDE or p-value
- **Good:** report builder renders MDE/p-value only if produced by an authorized deterministic diagnostic and allowed by claim boundary

### 4. LLM explanations must consume typed deterministic reports, not raw fixture JSON or raw uploaded data

LLMs may explain registered typed reports and claim boundaries. They may not directly infer feasibility, spend sufficiency, p-values, CIs, design approval, or estimator choice from raw data.

- **Bad:** LLM reads raw fixture JSON and says "this design is feasible"
- **Good:** LLM cites registered `GeoKpiSpendDataProfileReport`, `UnitEligibilityReport`, `SpendContrastFeasibilityReport`, and `ClaimBoundaryReport`

### 5. No notebooks, demos, landing-page examples, API examples, or agent demos before golden paths are stable

Notebook/demo work must wait until golden-path and blocked-path contracts are defined and future implementation has deterministic regression targets.

### 6. Do not create a generic readiness report before readiness concepts are separately defined

Data readiness, unit eligibility readiness, spend contrast readiness, portfolio feasibility readiness, inference eligibility readiness, and downstream-use readiness must remain distinct until explicit contracts safely unify them.

---

## 6. Golden-path vs blocked-path taxonomy

| Category | Prefix | Purpose |
|----------|--------|---------|
| Golden path | `GP-` | Successful or internal-planning scenarios with expected artifacts and claim boundaries |
| Blocked/provisional | `BP-` | Blocking conditions, overclaim attempts, anti-pattern violations |

Each scenario is a `PanelExpGoldenPathScenario` with typed expected artifacts, claims, blocks, and acceptance dimensions.

---

## 7. Required fixture/input categories

| Category | Input mode | Use |
|----------|------------|-----|
| Full-panel geo-week KPI/spend | `full_panel` | GP-001, GP-002, GP-005–GP-008 |
| Sample schema only | `sample_schema` | GP-003, BP-008 |
| Ballpark estimates | `ballpark` | GP-004, BP-007 |
| Missing/invalid columns | any | BP-001, BP-002 |
| Mixed grain | any | BP-003 |
| Duplicate geo-date rows | any | BP-004 |
| Insufficient units | `full_panel` | BP-005 |
| Weak spend contrast | `full_panel` | BP-006 |

Fixtures are `PanelExpGoldenPathFixture` records: test inputs only, never product branches.

---

## 8. Fixture-mode versus product-mode boundary

`PanelExpFixtureModeBoundary` defines:

- **Fixture mode:** test harness inputs; `fixture_id`/`sample_key` for regression only
- **Product mode:** `full_panel`, `sample_schema`, `ballpark` per data contract
- Fixture ids must not branch product logic
- Product logic must be schema/category/contract based

BP-013 and BP-014 enforce this boundary.

---

## 9. Demo/notebook boundary

`PanelExpNotebookDemoBoundary` defines:

- Demo paths, notebook examples, landing-page examples, API examples remain separate from product modes
- No demo path may silently merge with production paths
- Notebooks/demos blocked until golden paths stable (BP-017)
- Explicit bridge contract required before demo-to-product promotion

---

## 10. Report-builder non-inference boundary

`PanelExpReportBuilderBoundary` defines:

- Report builders **render** existing deterministic outputs only
- Must **not** calculate: lift, ROI, power, MDE, budget allocation, p-values, CIs, treatment/control assignment, method recommendations
- Must preserve validation state, governance state, lifecycle state, allowed/blocked downstream use
- Must surface blocking reasons, not hide them
- `ReportBuilderBoundaryResult` records compliance per scenario

BP-015 enforces this boundary.

---

## 11. LLM typed-report consumption boundary

LLM explanations must:

- Reference typed reports/artifacts from registry
- Preserve claim boundaries
- State missing data/blocking reasons when applicable
- **Not** upgrade provisional/diagnostic outputs
- **Not** infer from raw fixture JSON or raw uploaded data
- **Not** claim p-values/CIs unless authorized by future release gate

BP-016 enforces raw-data inference blocking.

---

## 12. Readiness-generalization boundary

Distinct readiness concepts (until explicit unification contract):

- Data readiness
- Unit eligibility readiness
- Spend contrast readiness
- Portfolio feasibility readiness
- Inference eligibility readiness
- Downstream-use readiness

BP-018 blocks generic readiness overgeneralization.

---

## 13. Required output artifact categories

Golden paths must expect these output categories where applicable:

`PlanningIntentReport`, `GeoKpiSpendDataProfileReport`, `UnitEligibilityReport`, `PortfolioFeasibilityReport`, `SpendContrastFeasibilityReport`, `CandidateDesignSet`, `DesignBasedInferencePlan`, `ModelFallbackRecommendation`, `PanelExpAgentRunManifest`, `PanelExpAgentArtifactReference`, `PanelExpAgentValidationReport`, `PanelExpAgentFailurePacket`, `PanelExpArtifactRegistryEntry`, `ClaimBoundaryReport`, `PanelExpGoldenPathAcceptanceResult`, `ReportBuilderBoundaryResult`, `FixtureModeBoundaryResult`, `NotebookDemoBoundaryResult`

---

## 14. Required acceptance dimensions

Each `PanelExpGoldenPathScenario` must define:

`scenario_id`, `scenario_name`, `scenario_type`, `input_mode`, `fixture_requirements`, `fixture_mode_or_product_mode`, `intake_expected`, `data_profile_expected`, `agent_packet_expected`, `artifact_registry_expected`, `diagnostic_expected`, `design_expected`, `spend_expected`, `inference_expected`, `model_fallback_expected`, `report_builder_expected`, `llm_explanation_expected`, `claim_boundary_expected`, `authorization_flags_expected`, `expected_final_status`, `expected_blocking_reasons`

---

## 15. Required golden-path scenarios

### GP-001: Single-test full-panel feasible planning

User requests one US DMA-level test with full geo-week KPI/spend panel.

**Expected:** adaptive intake, profiler-ready data, sufficient units, feasible maximum-sensitivity design candidate, registered artifacts, no production authorization.

### GP-002: Multi-test portfolio tiering

User requests five tests with 2 Tier 1, 2 Tier 2, 1 Tier 3.

**Expected:** portfolio planner evaluates requested mix, returns feasible or downgraded tiering alternative, explains tradeoffs, no p-value/CI authorization.

### GP-003: Sample schema mode

User provides sample schema only.

**Expected:** schema/data contract feedback and required-field checklist; no final feasibility, design, p-value, or CI claim.

### GP-004: Ballpark provisional mode

User has no data and provides rough unit count, KPI volume, spend, duration.

**Expected:** provisional feasibility range only; no final design, p-value, or CI claim.

### GP-005: Shared-control multi-arm planning

User requests multiple treatment arms with shared control.

**Expected:** shared-control dependency warning, covariance/multiplicity requirement, restricted claims, no independent-test fiction.

### GP-006: Go-live new channel planning

User wants to launch a new channel in selected geos.

**Expected:** go-live manipulation captured, ramp-up/platform-learning caveats, spend contrast requirement, no production claim.

### GP-007: Design-based inference eligible planning

Full-panel randomized/blocked design diagnostics pass for internal planning.

**Expected:** design-based inference fast path marked eligible-for-review only; p-values/CIs remain unauthorized until release gate.

### GP-008: Model fallback routing

Design-based path weak or insufficient.

**Expected:** model fallback candidates surfaced with claim boundaries, not production authorization.

---

## 16. Required blocked/provisional-path scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| BP-001 | Missing KPI column | Profiler blocking; no feasibility claim |
| BP-002 | Missing spend column when spend feasibility requested | Spend feasibility blocked |
| BP-003 | Mixed grain without mapping | Data contract block until grain mapping supplied |
| BP-004 | Duplicate geo-date rows without aggregation rule | Aggregation readiness blocked |
| BP-005 | Too few eligible units | Multi-cell design blocked/downgraded; no p-value/CI |
| BP-006 | Weak heavy-up spend contrast | Spend gap surfaced; recommend fewer cells, longer duration, higher spend, or downgrade tier |
| BP-007 | Ballpark mode overclaim attempt | LLM/report blocked from final feasibility, p-values, CIs |
| BP-008 | Sample schema overclaim attempt | LLM/report blocked from final design feasibility |
| BP-009 | Shared-control independent-test overclaim | Blocked unless joint covariance/multiplicity contract satisfied |
| BP-010 | Unregistered artifact referenced downstream | Downstream reference blocked until registry entry exists |
| BP-011 | Hidden agent failure | Blocked; failure packet required |
| BP-012 | Expired/revoked artifact used for new recommendation | Blocked by registry/provenance policy |
| BP-013 | Fixture-specific product logic | Blocked; no `fixture_id` product branching |
| BP-014 | Demo-specific workflow promoted to product path | Blocked; demo/notebook paths separate until bridge contract |
| BP-015 | Report builder hidden inference | Blocked; no lift/ROI/power/MDE/p-value/CI/assignment/method calc |
| BP-016 | LLM raw fixture/data inference | Blocked; no feasibility/causal claims from raw data |
| BP-017 | Notebook/demo before golden paths stable | Blocked; notebooks/demos wait for regression targets |
| BP-018 | Generic readiness overgeneralization | Blocked; distinct readiness concepts must not blur |

---

## 17. Agent packet/manifest acceptance

Every agent-involved scenario must assert:

- `PanelExpAgentInputPacket` present before run
- `PanelExpAgentRunManifest` records tools executed/blocked
- `PanelExpAgentArtifactReference` for every output
- `PanelExpAgentValidationReport` when validation claimed
- `PanelExpAgentFailurePacket` on failure (BP-011)
- No hidden failures; manifest completeness required

---

## 18. Artifact registry/provenance acceptance

Every scenario producing durable artifacts must assert:

- `PanelExpArtifactRegistryEntry` created with provenance
- Validation and governance state recorded
- Allowed/blocked downstream use explicit
- Unregistered artifacts blocked downstream (BP-010)
- Expired/revoked artifacts blocked for new recommendations (BP-012)

---

## 19. LLM explanation acceptance

Each scenario requires:

- LLM references typed reports/artifacts
- Claim boundaries preserved
- Missing data/blocking reasons stated when applicable
- No upgrade of provisional/diagnostic outputs
- No inference from raw fixture JSON or raw uploaded data
- No p-value/CI claims unless release gate authorizes

---

## 20. Claim boundary acceptance

Each scenario requires `ClaimBoundaryReport` or equivalent claim ceiling:

- Supported claims match governance status and input mode
- Blocked claims explicit
- Sample schema and ballpark cannot support final feasibility
- Diagnostic artifacts cannot imply production authorization
- All per-scenario authorization flags remain false

---

## 21. Data profiler acceptance

Profiler scenarios (GP-001, BP-001–BP-004) must assert:

- `GeoKpiSpendDataProfileReport` with contract compliance
- Column mapping, grain, coverage diagnostics
- Blocking conditions surfaced, not hidden
- No feasibility claim when profiler blocks

---

## 22. Portfolio planner acceptance

Portfolio scenarios (GP-002, GP-005, GP-006) must assert:

- `PortfolioFeasibilityReport` with tier assignment
- Tradeoff explanations for downgraded tiering
- Shared-control warnings (GP-005)
- Go-live caveats (GP-006)
- No p-value/CI authorization

---

## 23. Spend feasibility acceptance

Spend scenarios (GP-001, GP-006, BP-002, BP-006) must assert:

- `SpendContrastFeasibilityReport` when spend feasibility requested
- Weak contrast surfaced with remediation options (BP-006)
- Missing spend column blocks spend sufficiency claim (BP-002)

---

## 24. Shared-control/multicell acceptance

Shared-control scenarios (GP-005, BP-009) must assert:

- Dependency warning and covariance/multiplicity requirement
- No independent-test fiction
- Restricted claims until joint contract satisfied
- `multicell_production_claim_authorized` remains false

---

## 25. Design-based inference acceptance

Inference scenarios (GP-007, GP-008) must assert:

- `DesignBasedInferencePlan` when eligible-for-review
- P-values/CIs remain unauthorized
- `design_based_inference_production_authorized` remains false
- Model fallback surfaced with claim boundaries when design path weak (GP-008)

---

## 26. Model fallback acceptance

GP-008 and related blocked paths must assert:

- `ModelFallbackRecommendation` with claim boundaries
- Candidates surfaced, not production authorization
- `model_based_fallback_router_authorized` remains false

---

## 27. Scenario naming/versioning requirements

- Golden paths: `GP-NNN_<snake_case_description>`
- Blocked paths: `BP-NNN_<snake_case_description>`
- Scenarios versioned in `PanelExpGoldenPathRegressionSuite`
- Suite version tied to contract artifact version
- Scenario additions require contract revision, not silent fixture branching

---

## 28. Fixture/scenario test requirements

Minimum 21 scenario-spec tests: GP-001–GP-008, BP-001–BP-018, critical anti-patterns, acceptance dimensions, output artifact categories, authorization flags false per scenario, LLM/report-builder/fixture/demo boundaries, agent packet/manifest, registry/provenance, claim boundary, sample-schema/ballpark no-final-claim, shared-control, unregistered artifact, hidden failure, expired/revoked, generic readiness, revised roadmap sequence.

---

## 29. Governance boundaries

All authorization flags remain **false**:

- Golden path runtime, regression suite runtime, fixture-specific product logic, demo-specific product logic
- Report builder inference, notebook/demo runtime, generic readiness runtime
- Agent orchestration, artifact registry, LLM report grounding runtime
- Geo KPI spend profiler, geo unit feasibility, spend feasibility, portfolio planner, candidate design generator runtime
- Design-based inference production, model-based fallback router
- Production design, readout, p-values, CIs, selector/router, downstream integrations

---

## 30. Revised roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 10 | `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | ✅ |
| 11 | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | ✅ This contract |
| 12 | `GEO_KPI_SPEND_DATA_PROFILER_001` | Next |
| 13+ | Feasibility, design, inference implementation lanes | After golden paths |

This contract must guide: `GEO_KPI_SPEND_DATA_PROFILER_001`, `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`, `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001`, `PORTFOLIO_TEST_TIERING_ENGINE_001`, `CANDIDATE_DESIGN_GENERATOR_001`, `DESIGN_BASED_INFERENCE_FAST_PATH_001`, `MODEL_BASED_FALLBACK_ROUTER_001`, `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`.

---

## 31. Recommended next artifact

`GEO_KPI_SPEND_DATA_PROFILER_001` — first profiler implementation lane with golden-path regression targets.

---

## 32. Final verdict

**`panel_exp_golden_path_acceptance_tests_defined_no_runtime_authorization`**

Golden paths before demos, blocked paths before production claims, eight golden-path scenarios (GP-001–GP-008), eighteen blocked/provisional scenarios (BP-001–BP-018), critical implementation anti-patterns, eleven typed contracts, acceptance dimensions, output artifact categories, LLM/report-builder/fixture/demo boundaries, and per-scenario authorization boundaries defined. All runtime authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001_summary.json` |
| Harness | `panel_exp/validation/panel_exp_golden_path_acceptance_tests_001.py` |
