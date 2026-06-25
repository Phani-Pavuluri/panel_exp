# DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` |
| **Artifact type** | `implementation_plan_metadata_only` |
| **Status** | `completed` |
| **Base commit** | `71bc44e` (Audit roadmap state before selection gate plan) |
| **Plan rows** | **127** metadata rows (`failed_scenarios: []`) |
| **Final verdict** | `data_driven_selection_gate_implementation_plan_defined_no_downstream_authorization` |

This artifact is an **implementation plan only**. It defines how a future deterministic design × estimator × inference selector/router should be built. **No runtime selector/router was implemented.** **No package-side agents were implemented.** **No production authorization was granted.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `README.md` | Package maturity and documentation index |
| `docs/ROADMAP_V4.md` | Active method lane sequencing |
| `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` | Method-soundness active lane |
| `docs/MIP_AUDIT_REGISTRY.md` | Audit index and verdicts |
| `docs/governance/OPEN_INVESTIGATIONS_001.json` | Investigation and lane bindings |
| `docs/FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001.md` | Deferred package-side agents |
| `docs/track_d/ROADMAP_STATE_BEFORE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_REPORT.md` | Pre-artifact audit |
| `docs/track_d/PRODUCTION_READINESS_BACKLOG_LEDGER_001_REPORT.md` | 46-row backlog |
| `docs/track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_REPORT.md` | 96-row requirements (14 layers) |
| `docs/track_d/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_REPORT.md` | 180-row retire/replace execution |
| `docs/track_d/archives/*_summary.json` | Authorization flags and prior verdicts |

---

## 3. Prior-work reconciliation

| Prior artifact | Carried forward into this plan |
|----------------|-------------------------------|
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` | 14-layer rule ordering, route vocabulary, routing examples |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | All 46 backlog rows as router input consult flags |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | Per-family retain/retire/replace/block routing |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | SCM gated candidate; point estimate ≠ inference |
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | AugSynth diagnostic/remediation retention |
| `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | DID conditional designs only |
| `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` | Implementation-readiness only; not implemented |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell production claims blocked |
| `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001` | Agents deferred; manifest concepts staged only |
| `ROADMAP_STATE_BEFORE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Confirmed next-artifact boundaries |

`prior_work_reconciled: true`. Resolved planning artifacts do **not** imply production readiness.

---

## 4. Implementation-plan scope

This plan translates prior requirements, backlog, retire/replace decisions, method-governance boundaries, diagnostics, multicell constraints, package-side agent deferral, and release-gate rules into a **staged future implementation plan** for a deterministic selector/router that is:

- **Deterministic** — same inputs yield same outputs
- **Side-effect free** — no mutation of panel data or governance state
- **Auditable** — every decision cites prior artifacts and blocked reasons
- **Testable** — pure-function contract with harness and governance tests
- **Rules-first** — ordered 14-layer evaluation; no LLM decisioning
- **Non-authorizing** — unless release-gate state explicitly permits (none today)

**127 plan rows** cover: input contract (17 fields), output contract (18 fields), rule ordering (14 layers), staged implementation (7 stages × 6 aspects), method-family routing (9 families), integration contracts (15 areas), and explicit non-goals (12 items).

---

## 5. Explicit non-goals

- No runtime selector/router implementation
- No agent runtime, LLM calls, or package-side agent authorization
- No production inference, production p-values, or causal confidence intervals
- No TrustReport, CalibrationSignal, MMM, live API, scheduler, or budget integration
- No budget optimization or production decisioning
- No lift computation or power/MDE outside governed diagnostics
- No method promotion beyond existing gated/diagnostic/research/blocked labels
- No code deletion (retire/replace is claim/routing metadata)
- No skipping release-gate dependency
- No production authorization by this plan

---

## 6. Future input contract: `ExperimentSelectionInput`

| Field | Purpose |
|-------|---------|
| `panel_metadata` | Panel schema, units, time range, grain |
| `experiment_metadata` | Experiment ID, design type, scope |
| `assignment_metadata` | Assignment mechanism, support, stress state |
| `outcome_metadata` | Outcome variable definitions and transforms |
| `kpi_metadata` | KPI definitions, multiplicity scope |
| `cell_structure_metadata` | Treatment/control cell geometry |
| `design_diagnostics` | Design-layer validation outputs |
| `observed_panel_diagnostics` | Typed OPD diagnostic payloads |
| `method_governance_state` | Per-family promotion/retention status |
| `production_readiness_backlog_state` | Backlog row consult flags |
| `retire_replace_state` | Retire/replace execution row state |
| `multicell_validation_state` | Dependence/multiplicity validation state |
| `failure_registry_state` | Unresolved FM-* failure modes |
| `simulation_dgp_evidence_state` | DGP coverage evidence |
| `open_investigations_state` | Active INV-* investigations |
| `release_gate_state` | Release-gate checklist state |
| `audit_context` | Prior artifact IDs and summary references |

---

## 7. Future output decision contract: `ExperimentSelectionDecision`

| Field | Purpose |
|-------|---------|
| `design_status` | Design-layer route status |
| `estimator_status` | Estimator-layer route status |
| `inference_status` | Inference-layer route status |
| `design_estimator_pair_status` | Design × estimator pair status |
| `estimator_inference_pair_status` | Estimator × inference pair status |
| `full_tuple_status` | Full design × estimator × inference tuple |
| `method_family_status` | Per-family aggregated status |
| `route_status` | Overall route status |
| `blocked_reasons` | Typed blocked-reason codes |
| `warnings` | Non-blocking warnings |
| `required_diagnostics` | Diagnostics still required |
| `required_evidence` | Validation evidence still required |
| `allowed_current_use` | Explicit allowed uses at current maturity |
| `forbidden_current_use` | Explicit forbidden uses |
| `next_best_alternatives` | Governed fallback routes |
| `release_gate_required` | Whether release gate blocks authorization |
| `authorization_flags` | Per-role authorization (all false today) |
| `audit_references` | Cited artifact IDs and summary paths |

**Allowed status vocabulary:** `eligible`, `eligible_after_warning`, `candidate_after_validation`, `diagnostic_only`, `research_only`, `blocked`, `release_gate_required`, `not_applicable`.

---

## 8. Rule-ordering plan

Ordered evaluation (earlier hard-gate failure prevents later production eligibility):

| # | Layer | Decision focus |
|---|-------|----------------|
| 1 | `data_intake` | Panel schema and data contract validity |
| 2 | `experiment_metadata` | Experiment ID, cell structure declared |
| 3 | `assignment_mechanism` | Assignment mechanism declared and valid |
| 4 | `design_eligibility` | Design suitability separate from estimator |
| 5 | `estimator_eligibility` | Estimator allowed ≠ inference allowed |
| 6 | `inference_eligibility` | Inference family suitability |
| 7 | `outcome_kpi_compatibility` | Outcome scale and KPI compatibility |
| 8 | `observed_diagnostics` | OPD diagnostics feed eligibility |
| 9 | `simulation_dgp_coverage` | DGP evidence for promotion hypotheses |
| 10 | `failure_registry` | Unresolved failure modes block routing |
| 11 | `multicell_dependence_multiplicity` | Multicell/shared-control blockers |
| 12 | `method_family_promotion_status` | Family promotion/retire/replace state |
| 13 | `release_gate` | Release gate before authorization |
| 14 | `downstream_boundary` | TrustReport/CS/MMM/LLM/API/scheduler/budget blocked |

**Critical rule:** Failing an earlier **hard gate** prevents later layers from authorizing production use, even if a later layer would otherwise be `eligible`.

---

## 9. Blocked-reason schema plan

Typed `blocked_reason` codes on `ExperimentSelectionDecision.blocked_reasons`:

| Code family | Source | Example |
|-------------|--------|---------|
| `FM-*` | `METHOD_FAILURE_MODE_REGISTRY_001` | `FM-ES-001`, `FM-CP-003`, `FM-INF-009` |
| `INV-*` | `OPEN_INVESTIGATIONS_001` | Open investigation blocks production routing |
| `VAL-*` | Validation-plan blockers | Family-specific validation gaps |
| `RET-*` | Retire/replace execution | Retired overclaim path |
| `RG-*` | Release gate | `RG-NOT-AUTHORIZED` |

Selector must return blocked reasons (`selector_returns_blocked_reasons: true`).

---

## 10. Next-best-alternative schema plan

When primary route is blocked, `next_best_alternatives` returns governed fallback routes:

| Primary blocked | Allowed fallback | Forbidden fallback |
|-----------------|------------------|-------------------|
| SCM production inference | SCM point-estimate diagnostic | Production inference without adapter |
| Classic TBR overclaim | SCM gated candidate (if eligible) | Retired TBR causal path |
| Multicell production claim | Per-cell marginal diagnostic | Naive per-cell p-value |
| DID ineligible design | DID research exploration | Unconditional DID inference |

Retired overclaim paths must **not** appear as production-eligible alternatives.

---

## 11. Audit-reference contract

Every `ExperimentSelectionDecision` must include `audit_references` citing:

- Prior artifact report paths under `docs/track_d/`
- Summary JSON paths under `docs/track_d/archives/`
- Relevant investigation IDs from `OPEN_INVESTIGATIONS_001.json`
- `prior_work_reconciled: true` on plan completion

---

## 12. Method-family routing plan

| Family | Planned route status | Production inference |
|--------|---------------------|----------------------|
| **SCM** | `candidate_after_validation` | **Unauthorized** |
| **AugSynth CVXPY** | `diagnostic_only` | **Unauthorized** |
| **DID** | `candidate_after_validation` (conditional designs) | **Unauthorized** |
| **Synthetic DID** | `research_only` | **Unauthorized** |
| **TBRRidge** | `diagnostic_only` | **Unauthorized** |
| **Classic/Aggregate TBR** | `blocked` | **Unauthorized** |
| **Bayesian TBR** | `research_only` (posterior ≠ causal CI) | **Unauthorized** |
| **TROP** | `research_only` | **Unauthorized** |
| **Multicell/shared-control** | `blocked` | **Unauthorized** |

**Decisions enforced:**
1. Estimator eligibility does not imply inference eligibility
2. Point estimate eligibility does not imply causal uncertainty eligibility
3. Retired overclaim paths route to blocked/diagnostic/research, not production

---

## 13. Multicell/shared-control routing plan

Per `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`:

- Naive per-cell p-values: **blocked**
- Pooled/global overclaims without dependence handling: **blocked**
- Shared-control unresolved dependence: **blocked**
- Per-cell marginal diagnostic: **diagnostic_only**
- Multicell research exploration: **research_only**
- Production multicell claims: **blocked** until validation implementation exists

`multicell_production_claim_authorized: false`.

---

## 14. Outcome/KPI compatibility plan

At `outcome_kpi_compatibility` layer (layer 7):

- Sparse/count/rate outcomes require outcome-scale checks
- Multiple KPIs require multiplicity handling before inferential claims
- Incompatible outcome scale blocks estimator/inference pairing
- Warnings may yield `eligible_after_warning` but not production authorization

---

## 15. Observed-panel diagnostics ingestion plan

At `observed_diagnostics` layer (layer 8):

- Typed OPD diagnostics (`OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`) feed router inputs
- Donor support, pre-period fit, outcome scale, assignment validity gates
- Missing required diagnostics → `blocked` or `candidate_after_validation`
- Diagnostics are inputs, not outputs of the selector

---

## 16. DGP/simulation evidence integration plan

At `simulation_dgp_coverage` layer (layer 9):

- `simulation_dgp_evidence_state` consults `SIMULATION_DGP_COVERAGE_PLAN_001`
- DGP evidence required for promotion hypotheses; not sufficient alone
- Sparse outcome worlds without DGP coverage → research-only or blocked

---

## 17. Failure-registry integration plan

At `failure_registry` layer (layer 10):

- Unresolved `FM-*` modes block production routing
- Failure registry state is a hard gate
- Resolution of failure modes does not auto-authorize production (release gate still required)

---

## 18. Production-readiness backlog integration plan

All **46** backlog rows from `PRODUCTION_READINESS_BACKLOG_LEDGER_001` map to `production_readiness_backlog_state` consult flags. Unresolved backlog items prevent production eligibility at `method_family_promotion_status` or `downstream_boundary` layers.

---

## 19. Retire/replace integration plan

All **180** retire/replace execution rows inform `retire_replace_state`:

- `retire_overclaim_path` → route **blocked** or **diagnostic_only**
- `retain_candidate_gated` → route **candidate_after_validation**
- `hard_block_until_validated` → route **blocked**
- Classic TBR overclaim paths must not receive production-compatible routing

---

## 20. Release-gate integration plan

At `release_gate` layer (layer 13):

- `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` required before any authorization hypothesis
- `release_gate_state` must be explicitly authorized for production roles
- Until release gate plan exists and passes: all routes return `release_gate_required` for authorization requests

---

## 21. Package-side agent deferral boundary

Per `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001`:

- Package-side agents remain **deferred** (`package_side_agents_authorized: false`)
- This plan may stage `ExperimentRunManifest` / `ExperimentFailurePacket` concepts as future prerequisites in stage 1
- No agent runtime, LLM, or design-authority shift
- Near-term priority remains diagnostics-first deterministic work

---

## 22. Staged implementation sequence

| Stage | Purpose | Authorization boundary |
|-------|---------|------------------------|
| `stage_0_contract_only` | Define `ExperimentSelectionInput`/`Decision` schemas | All flags false |
| `stage_1_metadata_registry` | Metadata registry rows mirroring governance | All flags false |
| `stage_2_pure_function_router` | Pure deterministic side-effect-free router skeleton | Router unauthorized |
| `stage_3_diagnostics_integration` | Wire OPD and design diagnostics | All flags false |
| `stage_4_governance_integration` | Wire backlog, retire/replace, investigations | All flags false |
| `stage_5_shadow_mode` | Shadow evaluation; no production routing | All flags false |
| `stage_6_release_gate_candidate` | Release-gate-candidate evaluation only after release gate plan | Release gate required |

**This artifact only plans these stages; it does not implement them.**

---

## 23. Test strategy

- Metadata harness: `panel_exp/validation/data_driven_selection_gate_implementation_plan_001.py`
- Harness tests: `tests/validation/test_data_driven_selection_gate_implementation_plan_001.py`
- Governance lane tests: `tests/governance/` (on registry update)
- Scenario validation: all plan sections, families, layers, stages represented
- No production router execution in tests

---

## 24. Validation strategy

Tiered validation:

1. `python -m json.tool` on summary JSON
2. `git diff --check`
3. Safety grep: no authorization flags set to `true`
4. Targeted pytest on harness tests
5. Governance pytest if registry updated
6. Full-repo pytest only if schema changes justify it

---

## 25. Downstream boundary

This implementation plan does not implement the selector/router.
This implementation plan does not implement package-side agents.
This implementation plan does not authorize production inference.
This implementation plan does not authorize production p-values.
This implementation plan does not authorize causal confidence intervals.
This implementation plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.
Release gate remains required before any production authorization.
Resolved planning artifacts do not imply production readiness.
Downstream work remains paused.

All authorization flags remain **false** (see summary JSON).

---

## 26. Risks and ambiguities

| Item | Severity | Detail |
|------|----------|--------|
| Manifest vs router sequencing | Low | Agent roadmap lists manifests before implementation; plan stages manifests in stage 1 without changing agent deferral |
| Flag naming | Low | `selector_implementation_authorized` vs `data_driven_selection_gate_implementation_authorized` — semantically equivalent, both false |
| Shadow mode scope | Medium | Stage 5 must not leak into production routing without release gate |
| Actual router implementation timing | Info | Router implementation deferred until after release-gate plan |

---

## 27. Recommended next artifact

| Priority | Artifact | Role |
|----------|----------|------|
| **1 (immediate next)** | `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release gate before any authorization |
| **2 (deferred)** | `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001` | SCM validation implementation |
| **3 (later)** | Actual selector/router implementation (stages 0–6) | Only after release-gate plan |

---

## 28. Final verdict

**`data_driven_selection_gate_implementation_plan_defined_no_downstream_authorization`**

127-row metadata implementation plan for the future deterministic design × estimator × inference selector. Contracts, rule ordering, integration plans, and staged sequence defined. **No runtime selector/router implemented.** **No package-side agents implemented.** **No production authorization granted.** All authorization flags remain **false**. Recommended next artifact: **`PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001`**.

---

## Validation artifacts

| Artifact | Path |
|----------|------|
| Harness | `panel_exp/validation/data_driven_selection_gate_implementation_plan_001.py` |
| Summary | `docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_summary.json` |
| Tests | `tests/validation/test_data_driven_selection_gate_implementation_plan_001.py` |
