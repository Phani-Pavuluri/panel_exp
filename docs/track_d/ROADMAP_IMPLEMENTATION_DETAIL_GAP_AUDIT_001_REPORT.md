# ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` |
| **Artifact type** | `roadmap_implementation_detail_gap_audit` |
| **Status** | `completed` |
| **Base commit** | `55f7ae5` (Define experiment portfolio planner agent tooling contract) |
| **Audit result** | `implementation_detail_contracts_required_before_planner_runtime_work` |
| **Final verdict** | `roadmap_implementation_detail_gap_audit_logged_contracts_required_no_runtime_authorization` |

This artifact is an **audit/planning document only**. It identifies roadmap implementation-detail gaps. **No runtime agents, estimators, design algorithms, inference logic, production recommendations, or downstream integrations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | Nine-module planner architecture |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Tool-first/agent-second tooling contract (✅ complete) |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Design/estimator/inference separation |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Shared-control/multiplicity boundaries |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | Method portfolio context |
| SCM release-gate lane (validation/null/jackknife/packet/decision plan) | Dedicated SCM method-specific lane |

---

## 3. Audit motivation

Recent planner roadmap artifacts name high-level lanes (`GEO_KPI_SPEND_DATA_PROFILER_001`, `DESIGN_BASED_INFERENCE_FAST_PATH_001`, etc.) without sufficient implementation-detail contracts for Cursor/agents to implement safely.

Without typed data contracts, tool modules, failure modes, claim boundaries, and validation requirements, agents may build plausible but unsafe scaffolding, invent diagnostics, or overclaim feasibility and inference validity.

---

## 4. Implementation-detail gap pattern

**Pattern observed:** Roadmap artifact names imply implementation readiness, but missing layers include:

- typed input/output schemas
- deterministic module specifications
- explicit failure modes and degraded modes
- claim ceilings per diagnostic state
- scenario/fixture test requirements
- LLM grounding rules

**Safe implementation rule:** No contract artifact → no runtime implementation lane.

---

## 5. Current safe areas

| Area | Why safe |
|------|----------|
| SCM validation/release-gate lane | Dedicated method-specific artifacts with metadata scaffolding and explicit defer/closeout |
| Method portfolio prioritization checkpoint | Strategic governance only; no runtime claims |
| Planner agent roadmap | Architecture definition only |
| Planner agent tooling contract | Tool-first/agent-second; no-tool-no-claim; readiness gates defined |
| Selection gate implementation plan | Contracts defined; runtime explicitly deferred |
| Multicell dependence validation plan | Multiplicity/dependence requirements documented |

---

## 6. High-risk underspecified areas

| Gap area | Risk |
|----------|------|
| Agents without per-domain tool contracts | Hallucinated agent behavior |
| Design-based inference without tooling contract | Invalid p-value/CI claims |
| Spend feasibility without optimization boundary | Fake budget optimization |
| Geo KPI/spend without schema contract | Weak data handling |
| Shared-control/multicell without covariance contract | Independent-test fiction |
| Ballpark mode without claim boundaries | Overprecise provisional claims |
| LLM explanation without grounding rules | Ungrounded user-facing answers |

---

## 7. Agents/tooling gap assessment

`EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` addresses the cross-agent tooling framework (✅ complete). **Remaining gap:** domain-specific contracts for data profiling, spend contrast, design inference, ballpark mode, and LLM grounding must precede their respective implementation lanes.

Without these, Cursor may implement agent shells that emit plausible JSON without deterministic backing.

---

## 8. Design-based inference gap assessment

`DESIGN_BASED_INFERENCE_FAST_PATH_001` is named in the roadmap but lacks `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001` specifying:

- blocked/paired/CUPED estimator module contracts
- randomization/permutation inference preconditions
- shared-control covariance handling
- multiplicity correction requirements
- small-sample warning thresholds
- p-value/CI eligibility vs release-gate coupling

**Required before runtime:** `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001`.

---

## 9. Spend contrast / budget feasibility gap assessment

`SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` lacks `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` specifying:

- go-dark/heavy-up/go-live calculator contracts
- budget sufficiency vs budget **optimization** boundary (diagnostics only)
- MDE/sensitivity table schemas
- business-cost warning thresholds
- reallocation recommendation limits (suggest, not execute)

**Risk if skipped:** spend feasibility blurred with budget optimization; fake optimizer behavior.

---

## 10. Geo KPI/spend data contract gap assessment

`GEO_KPI_SPEND_DATA_PROFILER_001` lacks `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` specifying:

- panel schema semantics (geo ID, date, KPI, spend, channel)
- time-grain detection rules
- column mapping and missingness contracts
- usable-panel summary claim boundaries
- profiler module I/O types

**Required next contract artifact:** `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001`.

---

## 11. Shared-control/multicell inference gap assessment

`MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` exists at plan level but planner runtime needs `SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001` specifying:

- joint covariance requirements for shared-control contrasts
- pre-specified contrast lists
- multiplicity correction policy
- prohibition of independent per-arm test fiction
- correlated-contrast warning requirements

**Risk if skipped:** shared-control readouts treated as independent tests.

---

## 12. Ballpark feasibility mode gap assessment

Planner roadmap references ballpark fallback but lacks `BALLPARK_FEASIBILITY_MODE_CONTRACT_001` specifying:

- acceptable ballpark input types
- provisional claim ceilings (no Tier 1 decision-grade)
- uncertainty widening rules
- upgrade path when full data uploaded
- explicit "not precise" labeling

**Risk if skipped:** ballpark mode treated as precise feasibility.

---

## 13. LLM report grounding / claim boundary gap assessment

Tooling contract defines answerability matrix at framework level. Missing `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` specifying:

- required report references per claim type
- rejection rules for ungrounded explanations
- adaptive question boundaries
- session-level `ClaimBoundaryReport` aggregation
- audit trail for LLM outputs

**Risk if skipped:** LLM explanations not grounded in evidence packets.

---

## 14. Estimator claim-authorization assessment

**SCM:** Already has dedicated method-specific validation/release-gate lane (validation/null-calibration/jackknife metadata → review packet → decision plan → closeout). **No generic estimator-claim matrix detour is warranted now.**

**Future method lanes** (AugSynth/ASCM, TBRRidge, Synthetic DiD, Bayesian TBR, TROP) must preserve **separate authorization** for:

- point estimates
- p-values
- causal CIs
- selector/router use
- MMM ingestion
- downstream decisioning

Each method family retains its own release-boundary artifacts per existing audits (`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`, `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`, etc.).

---

## 15. Required implementation-detail contracts

| Contract artifact | Status | Domain |
|-------------------|--------|--------|
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | ✅ Complete | Cross-agent tooling framework |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Pending | Data schema and profiler |
| `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` | Pending | Spend/budget diagnostics |
| `SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001` | Pending | Multicell inference |
| `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001` | Pending | Design-based inference |
| `BALLPARK_FEASIBILITY_MODE_CONTRACT_001` | Pending | Ballpark fallback mode |
| `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` | Pending | LLM grounding |

**All seven must exist before respective planner runtime lanes proceed.**

---

## 16. Revised roadmap sequence

| # | Artifact | Status |
|---|----------|--------|
| 1 | `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` | ✅ |
| 2 | `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001` | ✅ |
| 3 | `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` | Active SCM |
| 4 | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | ✅ |
| 5 | `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | ✅ |
| 6 | `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | ✅ This audit |
| 7 | `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Next contract |
| 8 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Planned |
| 9 | `GEO_KPI_SPEND_DATA_PROFILER_001` | Planned |
| 10 | `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Planned |
| 11 | `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` | Planned |
| 12 | `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` | Planned |
| 13 | `PORTFOLIO_TEST_TIERING_ENGINE_001` | Planned |
| 14 | `CANDIDATE_DESIGN_GENERATOR_001` | Planned |
| 15 | `SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001` | Planned |
| 16 | `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001` | Planned |
| 17 | `DESIGN_BASED_INFERENCE_FAST_PATH_001` | Planned |
| 18 | `BALLPARK_FEASIBILITY_MODE_CONTRACT_001` | Planned |
| 19 | `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` | Planned |
| 20 | `MODEL_BASED_FALLBACK_ROUTER_001` | Planned |
| 21 | `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | Post-planner method |

Contract artifacts are inserted **before** their corresponding implementation lanes.

---

## 17. Governance boundaries

All authorization flags remain **false**:

- `roadmap_gap_audit_runtime_authorized`
- Planner/runtime module flags
- Design-based inference production
- Spend/budget reallocation runtime
- Geo KPI/spend profiler runtime
- Shared-control/multicell inference
- Ballpark feasibility production
- LLM report grounding runtime
- Production design recommendation, p-values, causal CIs, selector/router
- Downstream: TrustReport, CalibrationSignal, MMM, LLM decisioning, live API, scheduler, budget optimization, package-side agents

---

## 18. Risks if skipped

Without required contracts, Cursor/agents may:

1. Build plausible but unsafe scaffolding
2. Treat roadmap names as implementation detail
3. Invent diagnostic outputs
4. Overclaim design feasibility
5. Overclaim p-values/CIs
6. Blur spend feasibility with budget optimization
7. Treat ballpark mode as precise
8. Treat shared-control readouts as independent
9. Generate LLM explanations not grounded in evidence packets

---

## 19. Recommended next artifact

`GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` — first pending implementation-detail contract in revised sequence.

---

## 20. Final verdict

**`roadmap_implementation_detail_gap_audit_logged_contracts_required_no_runtime_authorization`**

The audit confirms seven implementation-detail contracts are required before planner runtime work. One (`EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001`) is complete; six remain. SCM retains its dedicated method-specific lane; no generic estimator-claim detour was added.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001_summary.json` |
| Harness | `panel_exp/validation/roadmap_implementation_detail_gap_audit_001.py` |
