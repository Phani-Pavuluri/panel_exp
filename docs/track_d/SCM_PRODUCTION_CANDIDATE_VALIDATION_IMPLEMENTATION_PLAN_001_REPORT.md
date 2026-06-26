# SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001` |
| **Artifact type** | `scm_validation_implementation_plan_metadata_only` |
| **Status** | `completed` |
| **Base commit** | `b3ea093` (Plan production authorization release gate) |
| **Method family** | `SCM` — `production_candidate_gated` |
| **Plan rows** | **144** metadata rows (`failed_scenarios: []`) |
| **Final verdict** | `scm_production_candidate_validation_implementation_plan_defined_no_downstream_authorization` |

This artifact is an **SCM validation implementation plan only**. SCM remains a **gated production-candidate**. **No SCM validation runtime was implemented.** **No SCM production inference was authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | 63-row validation plan (21 areas) |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate domains and evidence prerequisites |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Selector shadow integration boundary |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | SCM `retain_candidate_gated` |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | SCM backlog items |
| `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001` | Adapter contract |
| `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001` | Agents deferred |

---

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|----------------|-----------------|
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | 21 validation areas → 31 implementation areas |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate dependency; no authorization granted |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Shadow selector integration (stage 8) |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | SCM gated candidate retention |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell SCM claims blocked |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | SCM backlog consult flags |

`prior_work_reconciled: true`. Resolved planning artifacts do **not** imply production readiness.

---

## 4. SCM candidate scope

SCM is the **strongest near-term gated production-candidate** method family:

- Point estimates may be produced under diagnostic/candidate conditions
- Production inference, production p-values, and causal CIs remain **unauthorized**
- Donor support, convex hull, pre-period fit/trend, assignment validity are **required** before promotion review
- Multicell/shared-control SCM claims remain **blocked**
- Release gate remains **mandatory** before any SCM production authorization

---

## 5. Explicit non-goals

- No SCM validation runtime or harness implementation (this plan only)
- No SCM production inference authorization
- No production p-values or causal confidence intervals
- No selector/router production use
- No TrustReport, CalibrationSignal, MMM, live API, scheduler, budget authorization
- No package-side agent authorization
- No multicell SCM production claims
- No SCM `production_safe` promotion
- No skipping release gate
- No automatic authorization from placebo/null or jackknife diagnostics

---

## 6. Implementation-plan scope

**144 plan rows** covering:

- **31** SCM validation implementation areas
- **19** `SCMValidationInput` contract fields
- **22** `SCMValidationEvidence` contract fields
- **10** staged implementation phases (× 6 aspects each)
- **12** explicit non-goals

---

## 7. Required SCM validation evidence

Future implementation must produce typed `SCMValidationEvidence` covering all 31 validation areas, with statuses from the allowed vocabulary. Evidence must be auditable, deterministic, and consumable by selector shadow mode and release-gate review — but evidence alone does not authorize production.

---

## 8. SCM input/data contract validation plan

`SCMValidationInput` fields: `panel_metadata`, `treated_units`, `donor_units`, `time_index`, `pre_period`, `post_period`, `outcome_metadata`, `kpi_metadata`, `estimand_metadata`, `assignment_metadata`, `design_diagnostics`, `observed_panel_diagnostics`, `donor_pool_metadata`, `method_governance_state`, `failure_registry_state`, `simulation_dgp_evidence_state`, `multicell_validation_state`, `release_gate_state`, `audit_context`.

Area: `scm_input_contract`, `panel_balance_and_time_index`.

---

## 9. Donor pool/support validation plan

Areas: `donor_pool_definition`, `donor_pool_size`, `donor_support_overlap`, `convex_hull_support`, `extrapolation_risk`, `donor_weight_stability`.

**Required before promotion review:** donor support, convex-hull support, extrapolation risk assessment. Extrapolation risk → `blocked` for promotion.

---

## 10. Treated/control geometry validation plan

Areas: `treated_unit_definition`, `donor_pool_definition`, `treated_set_sensitivity`.

Single-treated SCM is the primary candidate path. Multi-treated/treated-set paths → `research_only` until framework matures.

---

## 11. Pre-period fit validation plan

Areas: `pre_period_length`, `pre_period_fit_quality`, `post_period_window_definition`.

Per `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`: pre-period fit is a **required blocker**; insufficient pre-period → blocked.

---

## 12. Pre-period trend stability validation plan

Area: `pre_period_trend_stability`.

Trend instability blocks promotion review; diagnostic warnings may yield `eligible_after_warning` for point estimates only.

---

## 13. Placebo/null calibration validation plan

Areas: `placebo_unit_generation`, `placebo_distribution_quality`, `null_calibration`.

**Decision:** Placebo/null diagnostics are **diagnostic** or `candidate_after_validation` — they do **not** automatically authorize production p-values (`placebo_null_not_auto_p_value_authorization`).

---

## 14. Jackknife/unit-sensitivity validation plan

Area: `jackknife_unit_sensitivity`.

**Decision:** Jackknife diagnostics are **diagnostic_only** — they do **not** automatically authorize causal confidence intervals (`jackknife_not_auto_causal_ci_authorization`).

---

## 15. Assignment/design validity validation plan

Areas: `assignment_design_validity`, `randomization_compatibility`, `geographic_interference_risk`, `spillover_exclusion_or_flagging`.

Assignment/design validity must pass **before** SCM can be reviewed for production use. Per `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`.

---

## 16. Outcome/KPI compatibility validation plan

Areas: `outcome_scale_compatibility`, `kpi_estimand_compatibility`, `effect_scale_contract`.

Sparse/count/rate outcomes require scale checks. Estimand must be explicit and compatible with SCM estimand contract.

---

## 17. Statistic adapter validation plan

Area: `statistic_adapter_contract`.

Per `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`: adapter required for inference-family promotion hypotheses; adapter alone does not authorize production inference.

---

## 18. Uncertainty/inference boundary plan

Area: `uncertainty_boundary` — planned status **`blocked`**.

SCM point estimates do not imply causal uncertainty authorization. Production inference remains unauthorized until separate release-gate decisions on `inference_authorization` and `causal_uncertainty_authorization` domains.

---

## 19. Failure-registry integration plan

Area: `failure_registry_mapping`.

Unresolved `FM-*` modes block SCM promotion review. Per `METHOD_FAILURE_MODE_REGISTRY_001`.

---

## 20. DGP/simulation evidence integration plan

Area: `simulation_dgp_coverage`.

DGP evidence required for promotion hypotheses per `SIMULATION_DGP_COVERAGE_PLAN_001`; not sufficient alone.

---

## 21. Multicell/shared-control blocker handling

Area: `multicell_shared_control_blocker` — planned status **`blocked`**.

Multicell/shared-control SCM production claims remain blocked until `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` implementation exists. `multicell_production_claim_authorized: false`.

---

## 22. Selector/router integration boundary

Stage 8 (`selector_shadow_integration`): future `SCMValidationEvidence` may supply `ExperimentSelectionInput.method_governance_state` in **shadow/planned mode only**.

`selector_implementation_authorized: false`, `production_selection_router_authorized: false`. Selector may not route SCM to production eligibility without separate authorization.

---

## 23. Release-gate dependency

Area: `release_gate_dependency` — planned status **`release_gate_required`**.

Per `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001`: release gate mandatory before SCM production authorization. `production_authorization_granted: false`.

---

## 24. Package-side agent deferral boundary

Per `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001`: agents deferred. Agents cannot interpret SCM validation outputs as production approval. `package_side_agents_authorized: false`.

---

## 25. Staged implementation sequence

| Stage | Purpose | Authorization boundary |
|-------|---------|------------------------|
| `stage_0_contract_and_registry` | `SCMValidationInput`/`Evidence` schemas | All flags false |
| `stage_1_data_and_panel_diagnostics` | Panel balance, time index | All flags false |
| `stage_2_donor_support_and_geometry_diagnostics` | Donor pool, support, hull | All flags false |
| `stage_3_pre_period_fit_and_trend_diagnostics` | Fit and trend harness | All flags false |
| `stage_4_placebo_and_null_calibration_diagnostics` | Placebo/null (diagnostic) | No p-value authorization |
| `stage_5_jackknife_and_sensitivity_diagnostics` | Jackknife (diagnostic) | No causal CI authorization |
| `stage_6_assignment_outcome_and_estimand_compatibility` | Assignment/outcome gates | All flags false |
| `stage_7_failure_registry_and_dgp_integration` | FM registry, DGP | All flags false |
| `stage_8_selector_shadow_integration` | Shadow selector inputs | Shadow only |
| `stage_9_release_gate_candidate_review` | Release-gate review prep | Not authorization |

**This artifact plans these stages only; it does not implement them.**

---

## 26. Test strategy

- Metadata harness: `panel_exp/validation/scm_production_candidate_validation_implementation_plan_001.py`
- Harness tests: `tests/validation/test_scm_production_candidate_validation_implementation_plan_001.py`
- Future implementation: per-area unit tests, integration tests, governance tests
- No production inference execution in tests at this stage

---

## 27. Governance update strategy

- Resolve `INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001`
- Add `SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001` lane binding
- Update ROADMAP_V4, METHOD_SOUNDNESS, MIP_AUDIT_REGISTRY
- Set `next_artifact`: `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001`
- Keep all authorization flags **false**

---

## 28. Risks and ambiguities

| Item | Severity | Detail |
|------|----------|--------|
| Placebo → p-value conflation | High | Teams may treat null calibration pass as production p-value authorization |
| Jackknife → CI conflation | High | Unit jackknife may be mistaken for causal CI |
| Point estimate → inference | Medium | Gated candidate may be over-read as production-ready |
| Multicell SCM edge cases | Medium | Per-cell SCM diagnostics vs blocked production claims |
| Selector shadow leakage | Medium | Stage 8 must not enable production routing |

---

## 29. Recommended next artifact

**`SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001`** — actual SCM validation harness implementation (not authorization).

Deferred: selector/router runtime implementation; release-gate runtime.

---

## 30. Final verdict

**`scm_production_candidate_validation_implementation_plan_defined_no_downstream_authorization`**

144-row metadata implementation plan for future SCM production-candidate validation evidence. SCM remains a **gated production-candidate**. **No SCM validation runtime implemented.** **No SCM production inference authorized.** **No production p-values or causal CIs authorized.** **No selector/router production use authorized.** **Release gate remains required.** **Multicell/shared-control SCM claims remain blocked.** **All downstream integrations remain blocked.**

---

## Validation artifacts

| Artifact | Path |
|----------|------|
| Harness | `panel_exp/validation/scm_production_candidate_validation_implementation_plan_001.py` |
| Summary | `docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_summary.json` |
| Tests | `tests/validation/test_scm_production_candidate_validation_implementation_plan_001.py` |
