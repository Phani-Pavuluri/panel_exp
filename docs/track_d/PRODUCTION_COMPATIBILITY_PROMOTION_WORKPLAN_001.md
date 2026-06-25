# PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001

## 1. Purpose

This docs-only execution workplan turns `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` into an ordered production-compatibility roadmap. It defines which method families get validation plans first, which require remediation before validation, which remain diagnostic/research-only, which need retire/replace execution, and which artifacts must complete before any production authorization.

This workplan is a control artifact only. It is **not** a production inference implementation.

## 2. Why this workplan exists

After consolidating promotion criteria across nine method families, the platform needs an explicit execution sequence. Without this workplan, families could be advanced out of order (e.g., multicell production claims before dependence validation, AugSynth production validation before adapter remediation, or classic TBR overclaim paths left unretired). This artifact sequences the next implementation and validation artifacts.

## 3. Evidence base

Evidence consumed from:

- `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
- `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

## 4. Production-compatible candidate definition

A **production-compatible candidate** is a method family that has passed observed diagnostics, DGP coverage, failure-registry review, assignment-stress compatibility, and family-specific gate audits — but remains **gated** until a family validation plan and platform release-gate plan authorize downstream use. **No family is production-authorized by this workplan.**

## 5. Remediation lane definition

Remediation lanes address known blockers (adapter gaps, inference remediation, aggregate geometry mismatch, dependence/multiplicity handling) before production-candidate validation may begin.

## 6. Research-only lane definition

Research-only lanes preserve scout/exploration paths without production claims. Advancement requires future simulation and/or calibration/replay evidence.

## 7. Diagnostic-only lane definition

Diagnostic-only lanes permit readout and comparison research but block production inference, p-values, and causal CIs.

## 8. Retire/replace lane definition

Retire/replace lanes execute exit criteria for overclaim paths (classic/aggregate TBR aggregate geometry, production decisioning overclaims) before any promotion hypothesis.

## 9. Execution sequencing

Ordered next artifacts:

1. `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
2. `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`
3. `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`
4. `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
5. `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`
6. `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`
7. `BAYESIAN_TBR_CALIBRATION_REPLAY_RESEARCH_PLAN_001`
8. `TBRRIDGE_DIAGNOSTIC_REMEDIATION_DECISION_PLAN_001`
9. `TROP_EVIDENCE_SCOUT_PLAN_001`
10. `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001`

Not all lanes become production-ready. Some are validation, remediation, research, or retirement lanes.

---

## Lane 1 — SCM production-candidate validation plan

| Field | Value |
|---|---|
| **Current status** | `production_candidate_gated` |
| **Why in this lane** | SCM is the strongest near-term production-compatible candidate per promotion criteria matrix |
| **Predecessor artifacts** | `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`, `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` |
| **Implementation artifact** | `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` |
| **Required validation evidence** | Observed diagnostics, DGP coverage, null calibration, donor support, pre-period fit |
| **Promotion blockers** | Incomplete null calibration, donor-support gaps, multicell unvalidated dependence |
| **Retire/replace criteria** | N/A — candidate lane |
| **Allowed current use** | Diagnostic readout, gated candidate planning |
| **Forbidden current use** | Production inference, p-values, causal CIs, TrustReport |
| **Authorization boundary** | Paused — gated candidate only |
| **Sequence rank** | 1 |

---

## Lane 2 — AugSynth remediation and diagnostic validation plan

| Field | Value |
|---|---|
| **Current status** | `remediation_required` |
| **Why in this lane** | AugSynth needs adapter, null calibration, donor-support diagnostics, and DGP coverage before production-candidate validation |
| **Predecessor artifacts** | `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` |
| **Implementation artifact** | `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` |
| **Required validation evidence** | Inference adapter contract, null calibration, donor diagnostics |
| **Promotion blockers** | Missing adapter, null calibration incomplete, diagnostic-only default |
| **Retire/replace criteria** | Replace with SCM where causal claims required and AugSynth gates fail |
| **Allowed current use** | Diagnostic readout, remediation planning |
| **Forbidden current use** | Production inference without adapter/null calibration |
| **Authorization boundary** | Paused — remediation before validation |
| **Sequence rank** | 3 |

---

## Lane 3 — DID conditional production-candidate validation plan

| Field | Value |
|---|---|
| **Current status** | `conditional_candidate` |
| **Why in this lane** | DID is conditional only under strong design/trend/cluster/outcome conditions |
| **Predecessor artifacts** | `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` |
| **Implementation artifact** | `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` |
| **Required validation evidence** | Design validity, cluster/outcome compatibility, bootstrap suitability |
| **Promotion blockers** | Weak design, trend violations, ineligible cluster structure |
| **Retire/replace criteria** | Block DID production path when design ineligible |
| **Allowed current use** | Conditional diagnostic in eligible designs |
| **Forbidden current use** | Production inference in ineligible designs |
| **Authorization boundary** | Paused — conditional designs only |
| **Sequence rank** | 4 |

---

## Lane 4 — Synthetic DID implementation readiness plan

| Field | Value |
|---|---|
| **Current status** | `research_scout_candidate` |
| **Why in this lane** | Synthetic DID needs implementation readiness before validation per scout audit |
| **Predecessor artifacts** | `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` |
| **Implementation artifact** | `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` |
| **Required validation evidence** | Simulation DGP coverage, suitability scout conclusions |
| **Promotion blockers** | Implementation gap, scout-only status |
| **Retire/replace criteria** | Defer production path until implementation readiness |
| **Allowed current use** | Scout/research exploration |
| **Forbidden current use** | Production inference before implementation readiness |
| **Authorization boundary** | Paused — implementation readiness required |
| **Sequence rank** | 5 |

---

## Lane 5 — TBRRidge diagnostic/remediation decision plan

| Field | Value |
|---|---|
| **Current status** | `diagnostic_only` |
| **Why in this lane** | TBRRidge remains diagnostic unless remediation proves otherwise |
| **Predecessor artifacts** | `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` |
| **Implementation artifact** | `TBRRIDGE_DIAGNOSTIC_REMEDIATION_DECISION_PLAN_001` |
| **Required validation evidence** | BRB interval correction, variance calibration, null FPR |
| **Promotion blockers** | Unremediated inference paths, estimand mismatch |
| **Retire/replace criteria** | Retire production inference path if remediation fails |
| **Allowed current use** | Diagnostic readout, remediation research |
| **Forbidden current use** | Production inference unless later remediation authorizes |
| **Authorization boundary** | Paused — diagnostic unless remediated |
| **Sequence rank** | 8 |

---

## Lane 6 — Classic TBR retire/replace execution plan

| Field | Value |
|---|---|
| **Current status** | `retire_or_replace` |
| **Why in this lane** | Classic/aggregate TBR overclaim paths are blocked or retire/replace priority |
| **Predecessor artifacts** | `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` |
| **Implementation artifact** | `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` |
| **Required validation evidence** | Aggregate geometry audit, overclaim failure modes |
| **Promotion blockers** | Aggregate overclaim (`FM-ES-007`), global causal overclaim |
| **Retire/replace criteria** | Retire aggregate/global production paths; replace with SCM/DID where appropriate |
| **Allowed current use** | Diagnostic point readout only |
| **Forbidden current use** | Production aggregate inference, production p-values |
| **Authorization boundary** | Blocked for overclaim paths |
| **Sequence rank** | 6 |

---

## Lane 7 — Bayesian TBR calibration/replay research plan

| Field | Value |
|---|---|
| **Current status** | `posterior_diagnostic_only` |
| **Why in this lane** | Bayesian TBR needs calibration/replay evidence before any causal uncertainty claim |
| **Predecessor artifacts** | `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` |
| **Implementation artifact** | `BAYESIAN_TBR_CALIBRATION_REPLAY_RESEARCH_PLAN_001` |
| **Required validation evidence** | Posterior coverage replay, null FPR, prior sensitivity |
| **Promotion blockers** | Posterior intervals ≠ causal CIs, no calibration replay |
| **Retire/replace criteria** | Block credible-as-causal-CI paths |
| **Allowed current use** | Posterior diagnostic research |
| **Forbidden current use** | Production inference, causal CI from posterior |
| **Authorization boundary** | Paused — calibration/replay required |
| **Sequence rank** | 7 |

---

## Lane 8 — TROP research-only evidence plan

| Field | Value |
|---|---|
| **Current status** | `research_only` |
| **Why in this lane** | TROP remains research-only unless future simulation and calibration/replay evidence |
| **Predecessor artifacts** | `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001` |
| **Implementation artifact** | `TROP_EVIDENCE_SCOUT_PLAN_001` |
| **Required validation evidence** | Simulation stress, calibration/replay, method comparisons |
| **Promotion blockers** | No triply-robust validation, production decisioning unauthorized |
| **Retire/replace criteria** | Retire production recommendation/decisioning paths |
| **Allowed current use** | Research scout, simulation planning |
| **Forbidden current use** | Production inference, recommendations, budget allocation |
| **Authorization boundary** | Paused — research-only |
| **Sequence rank** | 9 |

---

## Lane 9 — Multicell/shared-control dependence/multiplicity validation plan

| Field | Value |
|---|---|
| **Current status** | `cross_family_blocker` |
| **Why in this lane** | Multicell validation must precede any multicell production claim across all families |
| **Predecessor artifacts** | `MULTICELL_MAX_T_RESEARCH_SCOUT_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` |
| **Implementation artifact** | `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` |
| **Required validation evidence** | Dependence handling, multiplicity calibration, shared-control stress |
| **Promotion blockers** | Unhandled dependence, uncalibrated multiplicity |
| **Retire/replace criteria** | Block multicell production claims until validated |
| **Allowed current use** | Multicell research exploration |
| **Forbidden current use** | Multicell production inference without dependence handling |
| **Authorization boundary** | Cross-family blocker |
| **Sequence rank** | 2 |

---

## Lane 10 — Platform authorization boundary and release gate plan

| Field | Value |
|---|---|
| **Current status** | `blocked` |
| **Why in this lane** | No method is production-authorized until explicit release-gate plan completes |
| **Predecessor artifacts** | All family lanes 1–9, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` |
| **Implementation artifact** | `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` |
| **Required validation evidence** | Per-family validation completion, authorization boundary audit |
| **Promotion blockers** | Incomplete family lanes, open investigations |
| **Retire/replace criteria** | Maintain block until all gates pass |
| **Allowed current use** | Release-gate planning only |
| **Forbidden current use** | Any production authorization by this workplan |
| **Authorization boundary** | All downstream authorization paused |
| **Sequence rank** | 10 |

---

## 10. Allowed current uses

- Per-family diagnostic readouts where criteria matrix permits
- Gated SCM candidate validation planning
- Remediation and research lane execution
- Retire/replace execution for classic TBR overclaim paths
- Multicell dependence research
- Release-gate planning (not authorization)

## 11. Forbidden current uses

- Production inference for any family
- Production p-values and causal confidence intervals
- TrustReport, CalibrationSignal, MMM, LLM decisioning
- Live API, scheduler, budget optimization
- Multicell production claims before Lane 9 validation
- AugSynth production validation before Lane 2 remediation

## 12. Updated roadmap sequence

1. ✅ `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
2. ✅ `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001` (this workplan)
3. **`SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`** (immediate next)

## 13. Downstream boundary

This workplan does not authorize production inference.
This workplan does not authorize production p-values.
This workplan does not authorize causal confidence intervals.
This workplan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 14. Validation

Tests: `tests/governance/test_production_compatibility_promotion_workplan_001.py`
Summary: `docs/track_d/archives/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001_summary.json`

## 15. Verdict

`production_compatibility_promotion_workplan_defined_no_downstream_authorization`

**Next:** `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`

## Summary JSON location

[`docs/track_d/archives/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001_summary.json`](archives/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001_summary.json)
