# SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001` |
| **Artifact type** | `scm_null_calibration_implementation_plan_metadata_only` |
| **Status** | `completed` |
| **Base commit** | `81e2044` (Implement SCM validation metadata evidence) |
| **Method family** | `SCM` — `production_candidate_gated` |
| **Plan rows** | **147** metadata rows (`failed_scenarios: []`) |
| **Final verdict** | `scm_production_candidate_null_calibration_implementation_plan_defined_no_downstream_authorization` |

This artifact is an **SCM null calibration implementation plan only**. SCM remains a **gated production-candidate**. **No null calibration runtime was implemented.** **No SCM production inference was authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001` | SCM validation metadata scaffolding |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001` | Prior validation implementation plan |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | 63-row validation plan |
| `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001` | Prior placebo/null calibration research |
| `SCM_TREATED_SET_PLACEBO_INTEGRATION_001` | Placebo unit generation integration |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate dependency |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP simulation requirements |
| `METHOD_FAILURE_MODE_REGISTRY_001` | Failure mode registry |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Selector shadow boundary |

---

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|----------------|-----------------|
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001` | `SCMValidationEvidence` as precondition for null calibration |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001` | Stage 4 placebo/null diagnostics scope |
| `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001` | Placebo distribution and null calibration research |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate dependency; no authorization granted |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell/multiple-testing blockers |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP evidence for Type I / FPR assessment |

`prior_work_reconciled: true`. Resolved artifacts do **not** imply production readiness.

---

## 4. SCM null calibration scope

Future SCM null calibration will provide **diagnostic and candidate evidence** for placebo-based inference under gated production-candidate conditions:

- Placebo unit generation and time-window contracts
- Placebo and treated statistic adapter alignment
- Placebo distribution size, quality, and tail resolution
- Type I error and false-positive rate assessment (simulation-conditioned)
- P-value calibration diagnostics (not authorization)
- Null coverage diagnostics (not causal CI authorization)
- Integration with `SCMValidationEvidence`, failure registry, and DGP evidence
- Selector shadow consumption only until separately authorized

---

## 5. Explicit non-goals

- No null calibration runtime or harness implementation (this plan only)
- No placebo statistic computation or p-value generation
- No Type I error, FPR, or coverage computation at runtime
- No SCM production inference authorization
- No production p-values or causal confidence intervals
- No selector/router production use
- No TrustReport, CalibrationSignal, MMM, live API, scheduler, or budget authorization
- No package-side agent authorization
- No multicell SCM production claims
- No automatic p-value authorization from null calibration evidence

---

## 6. Implementation-plan scope

**147 plan rows** covering:

- **30** SCM null calibration areas
- **22** `SCMNullCalibrationInput` contract fields
- **23** `SCMNullCalibrationEvidence` contract fields
- **10** staged implementation phases (× 6 aspects each)
- **12** explicit non-goals

---

## 7. Required null calibration evidence

Future implementation must produce typed `SCMNullCalibrationEvidence` covering all 30 calibration areas, with statuses from the allowed vocabulary. Evidence must be auditable, deterministic, and consumable by selector shadow mode and release-gate review — but evidence alone does not authorize production p-values or causal CIs.

---

## 8. Placebo generation contract plan

**Area:** `placebo_unit_generation_contract`, `placebo_time_window_contract`

Future contracts must define:

- Placebo unit selection rules (donor-pool compatible, non-treated)
- Placebo time-window alignment with pre/post periods
- Conditioning on `SCMValidationEvidence` donor support and geometry status
- Explicit non-authorization of placebo generation as p-value approval

---

## 9. Null statistic contract plan

**Area:** `placebo_statistic_contract`, `treated_statistic_contract`

Future contracts must define:

- Placebo effect statistic via statistic adapter
- Treated effect statistic via same adapter family
- Effect scale alignment between placebo and treated paths
- Estimand compatibility gates before statistic evaluation

---

## 10. Placebo distribution quality diagnostics plan

**Areas:** `placebo_distribution_size`, `placebo_distribution_quality`, `placebo_rank_stability`, `tail_resolution`

Future diagnostics must assess:

- Minimum placebo draw count thresholds
- Distribution shape and outlier sensitivity
- Rank stability under donor perturbation (research tier)
- Tail resolution for extreme placebo statistics
- All outputs remain `diagnostic_only` or `research_only`

---

## 11. Type I error / false-positive calibration plan

**Areas:** `type_i_error_control`, `false_positive_rate_assessment`

Future implementation must:

- Assess Type I error under simulation DGP nulls
- Report false-positive rate diagnostics
- Condition on DGP coverage evidence from `SIMULATION_DGP_COVERAGE_PLAN_001`
- **Not** authorize production p-values from Type I / FPR diagnostics alone

---

## 12. Calibration threshold and acceptance policy plan

Future acceptance policy must define:

- Diagnostic thresholds for placebo distribution quality
- Candidate thresholds for Type I / FPR under DGP coverage
- Explicit separation between diagnostic pass and production authorization
- Release-gate review required before any threshold implies authorization

---

## 13. Coverage / interval calibration boundary plan

**Area:** `null_coverage_diagnostic`

**Decision:** Null coverage diagnostics assess interval behavior under null DGPs but do **not** authorize causal confidence intervals. Jackknife and uncertainty boundaries remain separate (`SCMValidationEvidence.jackknife_sensitivity_status`).

---

## 14. P-value authorization boundary plan

**Area:** `p_value_calibration_diagnostic`, `production_authorization_boundary`

**Decision:** SCM null calibration evidence is **necessary but not sufficient** for production p-value authorization. `scm_production_p_value_authorized` and `production_p_value_authorized` remain false until release-gate approval with separate authorization artifact.

---

## 15. Jackknife / causal CI boundary plan

**Decision:** SCM null calibration evidence is **necessary but not sufficient** for causal CI authorization. Null coverage diagnostics do not substitute for jackknife sensitivity validation. `scm_causal_confidence_interval_authorized` remains false.

---

## 16. DGP/simulation evidence integration plan

**Area:** `simulation_dgp_coverage`

Future implementation must:

- Consume `simulation_dgp_evidence_state` from input contract
- Require DGP coverage for Type I / FPR assessment stages
- Map unresolved DGP gaps to blocked reasons and required followups

---

## 17. Failure-registry integration plan

**Area:** `failure_registry_mapping`, `blocked_reason_mapping`, `required_followup_mapping`

Future implementation must:

- Map calibration failures to `METHOD_FAILURE_MODE_REGISTRY_001` modes
- Emit blocked-reason codes consistent with `SCMValidationEvidence` patterns
- Emit required-followup codes for incomplete calibration evidence

---

## 18. SCMValidationEvidence integration plan

**Area:** `null_calibration_input_contract`, `pre_period_fit_conditioning`, `donor_support_conditioning`

Future `SCMNullCalibrationInput.scm_validation_evidence` must be consumed as precondition:

- Donor support and pre-period fit must pass validation gates
- Assignment/design validity must be satisfied
- Unresolved validation blocked reasons propagate to null calibration evidence
- Null calibration cannot override validation failures

---

## 19. Selector/router shadow integration boundary

**Area:** `selector_shadow_input_contract`

**Decision:** Selector/router may consume future null calibration evidence only as **non-authorizing shadow evidence** until separately authorized. `selector_implementation_authorized` and `production_selection_router_authorized` remain false.

---

## 20. Multicell/shared-control calibration boundary

**Areas:** `multicell_shared_control_boundary`, `multiple_testing_boundary`

**Decision:** Multicell/shared-control SCM null calibration claims remain **blocked** unless separately validated per `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`. Multiple-testing corrections are a separate blocker from single-cell null calibration.

---

## 21. Release-gate dependency

**Area:** `release_gate_dependency`

**Decision:** Release gate remains **mandatory** before any SCM production p-value, causal CI, or inference authorization. Null calibration completion does not bypass release gate.

---

## 22. Package-side agent deferral boundary

**Decision:** Package-side agents remain **deferred** and cannot interpret null calibration evidence as production approval. `package_side_agents_authorized` remains false.

---

## 23. Staged implementation sequence

| Stage | Purpose |
|-------|---------|
| `stage_0_contract_and_registry` | Define `SCMNullCalibrationInput`/`Evidence` schemas and 30-area registry |
| `stage_1_placebo_generation_contracts` | Placebo unit and time-window generation contracts |
| `stage_2_null_statistic_contracts` | Placebo and treated statistic adapter contracts |
| `stage_3_distribution_quality_diagnostics` | Distribution size, quality, rank stability |
| `stage_4_type_i_error_and_false_positive_diagnostics` | Type I error and FPR assessment |
| `stage_5_p_value_calibration_diagnostics` | P-value and null coverage diagnostics |
| `stage_6_dgp_and_failure_registry_integration` | DGP and failure registry integration |
| `stage_7_scm_validation_evidence_integration` | Consume `SCMValidationEvidence` as precondition |
| `stage_8_selector_shadow_integration` | Selector shadow evidence supply |
| `stage_9_release_gate_candidate_review` | Release-gate candidate review only |

Each stage defines purpose, inputs, outputs, acceptance criteria, non-goals, and authorization boundary. **This artifact plans these stages only.**

---

## 24. Future test strategy

Future `SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001` tests should verify:

1. All 30 calibration areas present in registry
2. `SCMNullCalibrationInput` and `SCMNullCalibrationEvidence` field contracts
3. Status vocabulary completeness
4. Deterministic evidence builder behavior
5. SCM validation evidence precondition enforcement
6. Donor support and pre-period fit conditioning
7. Null calibration incomplete does not authorize p-values
8. Null coverage incomplete does not authorize causal CIs
9. Multicell unvalidated state produces blocked status
10. Release gate not granted produces `release_gate_required`
11. All authorization flags remain false
12. Summary JSON and report generation

---

## 25. Governance update strategy

- Add `INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001` investigation (RESOLVED)
- Add `SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001` lane (complete)
- Set `next_artifact`: `SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001`
- Update `ROADMAP_V4.md`, `METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`, `MIP_AUDIT_REGISTRY.md`
- Do not mark SCM null calibration as implemented or authorized

---

## 26. Risks and ambiguities

- Placebo null calibration under small donor pools may have insufficient tail resolution
- Type I / FPR assessment depends on DGP coverage not yet fully implemented
- Multicell null calibration paths require separate validation lane
- P-value calibration diagnostic thresholds require future empirical calibration artifacts
- Selector shadow integration timing depends on selection-gate implementation sequencing

---

## 27. Recommended next artifact

**`SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001`** — actual SCM null calibration metadata harness implementation (not authorization).

---

## 28. Final verdict

**`scm_production_candidate_null_calibration_implementation_plan_defined_no_downstream_authorization`**

SCM null calibration implementation plan is defined. SCM remains gated production-candidate. No null calibration runtime, placebo computation, p-values, causal CIs, selector production use, downstream integrations, or package-side agents are authorized. Release gate remains required.

---

| Summary | `docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001_summary.json` |
| Module | `panel_exp/validation/scm_production_candidate_null_calibration_implementation_plan_001.py` |
| Tests | `tests/validation/test_scm_production_candidate_null_calibration_implementation_plan_001.py` |
