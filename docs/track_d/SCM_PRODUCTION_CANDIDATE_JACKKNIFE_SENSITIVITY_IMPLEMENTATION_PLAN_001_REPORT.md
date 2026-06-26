# SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001` |
| **Artifact type** | `scm_jackknife_sensitivity_implementation_plan_metadata_only` |
| **Status** | `completed` |
| **Base commit** | `3839d94` (Implement SCM null calibration metadata evidence) |
| **Method family** | `SCM` — `production_candidate_gated` |
| **Plan rows** | **159** metadata rows (`failed_scenarios: []`) |
| **Final verdict** | `scm_production_candidate_jackknife_sensitivity_implementation_plan_defined_no_downstream_authorization` |

This artifact is an **SCM jackknife sensitivity implementation plan only**. SCM remains a **gated production-candidate**. **No jackknife sensitivity runtime was implemented.** **No SCM production inference was authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001` | Null calibration metadata precondition |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001` | SCM validation evidence precondition |
| `SCM_JACKKNIFE_CHARACTERIZATION_001` | Prior jackknife OC research |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate dependency |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP simulation requirements |
| `METHOD_FAILURE_MODE_REGISTRY_001` | Failure mode registry |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Selector shadow boundary |

---

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|----------------|-----------------|
| `SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001` | `scm_null_calibration_evidence` as precondition |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001` | `scm_validation_evidence` as precondition |
| `SCM_JACKKNIFE_CHARACTERIZATION_001` | Unit-deletion and instability research context |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release-gate dependency; no authorization granted |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell/multiple-testing blockers |

`prior_work_reconciled: true`. Resolved artifacts do **not** imply production readiness.

---

## 4. SCM jackknife sensitivity scope

Future SCM jackknife/unit-sensitivity evidence will provide **diagnostic and sensitivity** readouts under gated production-candidate conditions:

- Unit, donor, and treated-unit deletion contracts
- Donor-weight stability and concentration diagnostics
- Treated-unit influence and high-leverage detection
- Effect sign and magnitude instability diagnostics
- Sensitivity threshold and escalation policies (not authorization)
- Integration with `SCMValidationEvidence`, `SCMNullCalibrationEvidence`, failure registry, and DGP evidence
- Selector shadow consumption only until separately authorized

**Jackknife sensitivity is not a causal confidence interval by itself.**

---

## 5. Explicit non-goals

- No jackknife sensitivity runtime or harness implementation (this plan only)
- No jackknife estimate, uncertainty interval, or causal CI computation
- No production p-values or Type I error computation
- No SCM production inference authorization
- No selector/router production use
- No TrustReport, CalibrationSignal, MMM, live API, scheduler, or budget authorization
- No package-side agent authorization
- No multicell SCM production claims
- No automatic causal CI authorization from jackknife sensitivity

---

## 6. Implementation-plan scope

**159 plan rows** covering:

- **37** SCM jackknife sensitivity areas
- **23** `SCMJackknifeSensitivityInput` contract fields
- **27** `SCMJackknifeSensitivityEvidence` contract fields
- **10** staged implementation phases (× 6 aspects each)
- **12** explicit non-goals

---

## 7. Required jackknife sensitivity evidence

Future implementation must produce typed `SCMJackknifeSensitivityEvidence` covering all 37 sensitivity areas, with statuses from the allowed vocabulary. Evidence must be auditable, deterministic, and consumable by selector shadow mode and release-gate review — but evidence alone does not authorize causal CIs or production inference.

---

## 8. Unit-deletion contract plan

**Areas:** `unit_deletion_contract`, `donor_deletion_contract`, `treated_unit_deletion_contract`

Future contracts must define:

- Which units may be deleted in jackknife sensitivity passes
- Donor vs treated deletion semantics
- Conditioning on donor support and pre-period fit
- Explicit non-authorization of deletion diagnostics as causal CIs

---

## 9. Donor-deletion contract plan

**Area:** `donor_deletion_contract`

Future contracts must define donor-pool-compatible deletion rules, weight re-normalization metadata, and instability flags when donor removal materially changes effect estimates.

---

## 10. Treated-set sensitivity contract plan

**Area:** `treated_set_sensitivity_contract`

Future contracts must define treated-set perturbation rules for multi-treated geometries. Status remains `research_only` until separately validated.

---

## 11. Donor-weight stability diagnostics plan

**Areas:** `donor_weight_stability_contract`, `donor_weight_concentration`

Future diagnostics must assess donor weight stability under unit deletion and flag concentration risk. High concentration produces warnings or blockers before promotion review.

---

## 12. Treated-unit influence diagnostics plan

**Areas:** `treated_unit_influence`, `influence_diagnostic`, `high_leverage_unit_detection`

Future diagnostics must identify treated units with disproportionate influence on effect estimates. High-leverage units produce warnings, blockers, or required followups.

---

## 13. Effect instability diagnostics plan

**Areas:** `effect_instability_contract`, `effect_sign_stability`, `effect_magnitude_stability`, `jackknife_distribution_quality`

Future diagnostics must assess sign flips and magnitude swings under unit deletion. All outputs remain `diagnostic_only` unless separately authorized.

---

## 14. Sensitivity threshold and escalation policy plan

**Areas:** `sensitivity_threshold_policy`, `sensitivity_escalation_policy`

Future policy must define diagnostic thresholds for instability, leverage, and weight concentration, plus escalation rules (warning → blocker → followup). Threshold pass does **not** imply causal CI authorization.

---

## 15. Causal CI authorization boundary plan

**Area:** `causal_ci_boundary`

**Decision:** Jackknife sensitivity evidence is **necessary but not sufficient** for causal CI authorization. `scm_causal_confidence_interval_authorized` and `causal_confidence_interval_authorized` remain false until release-gate approval with separate authorization artifact.

---

## 16. P-value authorization boundary plan

**Area:** `p_value_boundary`

**Decision:** Jackknife sensitivity does **not** authorize production p-values. P-value authorization remains tied to null calibration and release-gate review, not jackknife stability.

---

## 17. Null calibration dependency plan

**Areas:** `null_calibration_dependency`, `placebo_calibration_dependency`

Future jackknife sensitivity must consume `scm_null_calibration_evidence` as precondition. Jackknife cannot override incomplete null calibration evidence.

---

## 18. SCMValidationEvidence integration plan

Future `SCMJackknifeSensitivityInput.scm_validation_evidence` must be consumed as precondition:

- Donor support, pre-period fit, assignment validity must pass validation gates
- Unresolved validation blocked reasons propagate to jackknife evidence

---

## 19. SCMNullCalibrationEvidence integration plan

Future `SCMJackknifeSensitivityInput.scm_null_calibration_evidence` must be consumed as precondition:

- Null calibration metadata must be present before jackknife sensitivity review
- Jackknife cannot substitute for null calibration evidence

---

## 20. DGP/simulation evidence integration plan

**Area:** `simulation_dgp_coverage`

Future implementation must consume `simulation_dgp_evidence_state` for sensitivity calibration under simulation DGPs.

---

## 21. Failure-registry integration plan

**Areas:** `failure_registry_mapping`, `blocked_reason_mapping`, `required_followup_mapping`

Future implementation must map jackknife sensitivity failures to `METHOD_FAILURE_MODE_REGISTRY_001` modes and emit consistent blocked-reason/followup codes.

---

## 22. Selector/router shadow integration boundary

**Area:** `selector_shadow_input_contract`

**Decision:** Selector/router may consume future jackknife evidence only as **non-authorizing shadow evidence** until separately authorized.

---

## 23. Multicell/shared-control sensitivity boundary

**Areas:** `multicell_shared_control_boundary`, `multiple_testing_boundary`

**Decision:** Multicell/shared-control SCM jackknife claims remain **blocked** unless separately validated. Multiple-testing corrections are a separate blocker.

---

## 24. Release-gate dependency

**Area:** `release_gate_dependency`

**Decision:** Release gate remains **mandatory** before any SCM causal CI or inference authorization. Jackknife sensitivity completion does not bypass release gate.

---

## 25. Package-side agent deferral boundary

**Decision:** Package-side agents remain **deferred** and cannot interpret jackknife stability as production approval.

---

## 26. Staged implementation sequence

| Stage | Purpose |
|-------|---------|
| `stage_0_contract_and_registry` | Define `SCMJackknifeSensitivityInput`/`Evidence` schemas and 37-area registry |
| `stage_1_unit_deletion_contracts` | Unit, donor, treated-unit deletion contracts |
| `stage_2_donor_and_treated_set_sensitivity_contracts` | Donor and treated-set sensitivity |
| `stage_3_donor_weight_and_influence_diagnostics` | Weight stability and influence diagnostics |
| `stage_4_effect_instability_diagnostics` | Sign/magnitude instability diagnostics |
| `stage_5_threshold_and_escalation_policy` | Threshold and escalation policy |
| `stage_6_null_calibration_and_validation_evidence_integration` | Consume validation and null calibration evidence |
| `stage_7_dgp_and_failure_registry_integration` | DGP and failure registry integration |
| `stage_8_selector_shadow_integration` | Selector shadow evidence supply |
| `stage_9_release_gate_candidate_review` | Release-gate candidate review only |

Each stage defines purpose, inputs, outputs, acceptance criteria, non-goals, and authorization boundary. **This artifact plans these stages only.**

---

## 27. Future test strategy

Future `SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001` tests should verify:

1. All 37 sensitivity areas present in registry
2. Input and evidence field contracts
3. Validation and null calibration evidence preconditions
4. Deletion contract enforcement
5. Instability/leverage warnings and blockers
6. Causal CI and p-value authorization remain false
7. Multicell unvalidated → blocked
8. Release gate not granted → `release_gate_required`
9. All authorization flags remain false

---

## 28. Governance update strategy

- Add `INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001` investigation (RESOLVED)
- Add `SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001` lane (complete)
- Set `next_artifact`: `SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001`
- Update roadmaps and MIP registry
- Do not mark jackknife sensitivity as implemented or authorized

---

## 29. Risks and ambiguities

- Jackknife sensitivity under small donor pools may have insufficient deletion diversity
- High-leverage detection thresholds require future empirical calibration
- Multi-treated jackknife paths require separate validation lane
- Jackknife OC from Phase 11 does not automatically transfer to production-candidate authorization

---

## 30. Recommended next artifact

**`SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001`** — actual SCM jackknife sensitivity metadata harness implementation (not authorization).

---

## 31. Final verdict

**`scm_production_candidate_jackknife_sensitivity_implementation_plan_defined_no_downstream_authorization`**

SCM jackknife sensitivity implementation plan is defined. SCM remains gated production-candidate. No jackknife runtime, causal CIs, p-values, selector production use, downstream integrations, or package-side agents are authorized. Release gate remains required.

---

| Summary | `docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001_summary.json` |
| Module | `panel_exp/validation/scm_production_candidate_jackknife_sensitivity_implementation_plan_001.py` |
| Tests | `tests/validation/test_scm_production_candidate_jackknife_sensitivity_implementation_plan_001.py` |
