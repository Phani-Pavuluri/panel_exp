# METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001 Report

## 1. Purpose

This planning-only artifact defines execution decisions for method-family retire/replace paths across **12 method families** and **15 execution areas** (**180 execution rows**; `failed_scenarios: []`).

This plan decides which method-family paths remain active, which stay diagnostic/research-only, which require remediation, and which overclaim paths should be retired or replaced before implementation work continues. It is **not** code deletion or replacement implementation.

## 2. Why retire/replace execution is needed before implementation

Per `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`, `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, and `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`, multiple method families have unresolved overclaim paths (classic/aggregate TBR), diagnostic-only paths (TBRRidge), research-only paths (TROP, Bayesian TBR), and gated candidates (SCM, DID, Synthetic DID). Without explicit retire/replace execution metadata, implementation lanes risk routing unsafe claims to production eligibility.

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|---|---|
| `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` | Synthetic DID implementation-readiness candidate |
| `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | DID conditional candidate |
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | AugSynth remediation retention |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | SCM gated candidate retention |
| `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` | TBRRidge diagnostic/remediation |
| `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` | Bayesian TBR research boundary |
| `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001` | TROP research-only boundary |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` | Selection-gate routing |

Resolved audits are not re-implemented; unresolved retire/replace blockers are encoded as execution requirements.

## 4. Relationship to OPEN_INVESTIGATIONS_001

`INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001` is resolved by this artifact. Open investigations for selection-gate implementation, release gate, and SCM validation implementation remain **PLANNED**. Investigation resolution does **not** imply production readiness.

## 5. Relationship to PRODUCTION_READINESS_BACKLOG_LEDGER_001

Backlog rows for classic TBR retire/replace, TBRRidge remediation, TROP research-only, multicell blockers, and downstream integration pause map directly to execution rows in this plan.

## 6. Relationship to selection-gate requirements

Per `routing_retire_replace_execution`, the selection gate must route retired/replaced paths away from production eligibility. Retired overclaim paths must not appear in production-compatible routing tables.

## 7. Relationship to method-family promotion criteria

Per `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`, promotion status varies by family. This execution plan operationalizes those criteria into retain/retire/replace/block decisions without authorizing production inference.

## 8. Retire/replace semantics

Retire/replace means retiring **unsafe claims or overclaiming paths**, not necessarily deleting all code. Diagnostic code may remain if clearly labeled and prevented from production routing. Research code may remain if clearly labeled and prevented from production routing.

## 9. Execution decision definitions

| Decision | Meaning |
|---|---|
| `retain_candidate_gated` | Retain as gated production-candidate path |
| `retain_diagnostic_only` | Retain for diagnostic readout only |
| `retain_research_only` | Retain for research/scout only |
| `retain_with_remediation` | Retain pending remediation evidence |
| `retire_overclaim_path` | Retire unsafe causal-inference overclaim |
| `replace_with_candidate_path` | Route to replacement candidate family |
| `hard_block_until_validated` | Block until validation implementation exists |
| `defer_to_release_gate` | Defer authorization to release gate |

## 10. Status definitions

| Status | Meaning |
|---|---|
| `production_candidate_gated` | Gated candidate; point estimate not sufficient |
| `diagnostic_only` | Diagnostic readout only |
| `research_only` | Research/scout handling only |
| `remediation_required` | Remediation evidence required |
| `retire_replace_required` | Overclaim path must be retired/replaced |
| `blocked` | Path blocked |
| `release_gate_required` | Release gate required before authorization |

## 11. Execution area definitions

Execution areas cover: active candidate retention, diagnostic-only retention, research-only retention, remediation-required retention, retire/replace required, hard block required, overclaim prevention, replacement candidate mapping, code-path labeling, documentation labeling, test/governance labeling, selection-gate routing impact, open-investigation update, roadmap update, and release-gate dependency.

## 12. SCM execution decisions

SCM is **retained** as the strongest near-term production-candidate lane (`retain_candidate_gated`, `production_candidate_gated`). Point estimates do not authorize production inference.

## 13. AugSynth execution decisions

AugSynth CVXPY is **retained with remediation** (`retain_with_remediation`, `remediation_required`) per `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`.

## 14. DID execution decisions

DID is **retained as conditional candidate** (`retain_candidate_gated`) only under eligible designs per `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`.

## 15. Synthetic DID execution decisions

Synthetic DID is **retained as implementation-readiness candidate** (`retain_candidate_gated`) per `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`. Not implemented by this artifact.

## 16. TBRRidge execution decisions

TBRRidge is **retained diagnostic/remediation only** (`retain_diagnostic_only`) unless future evidence changes status.

## 17. Classic/Aggregate TBR retire/replace decisions

Classic/aggregate TBR causal-inference overclaim paths require **retire/replace** (`retire_overclaim_path`, `retire_replace_required`). Replacement candidate: SCM gated path.

## 18. Bayesian TBR boundary decisions

Bayesian TBR remains **posterior-diagnostic/research-only** (`retain_research_only`). Posterior intervals are **not** causal CIs.

## 19. TROP boundary decisions

TROP remains **research-only** (`retain_research_only`). Production recommendations, rankings, budget allocation, and decisioning remain **blocked**.

## 20. Multicell/shared-control boundary decisions

Multicell/shared-control overclaim paths remain **blocked** (`hard_block_until_validated`) until dependence/multiplicity validation implementation exists.

## 21. Selection-gate routing impact

Selection gate must route retired/replaced paths away from production eligibility. Overclaim paths must not receive production-compatible routing.

## 22. Required code-path labeling

All families require code-path labeling (`label_code_path`, `block_production_routing`). Retire/replace paths require `retire_overclaim_label` and production entrypoint guards.

## 23. Required documentation labeling

Roadmap, method inventory, and retire/replace semantics must be documented. Allowed/forbidden uses must be explicit per family.

## 24. Required test/governance labeling

Governance and routing tests must assert no production authorization for gated, diagnostic, research, retired, and blocked paths.

## 25. Allowed current uses

- Gated candidate research (SCM, DID, Synthetic DID)
- Diagnostic readout (TBRRidge, legacy TBR if labeled)
- Research/scout (TROP, Bayesian TBR, multicell)
- Remediation planning (AugSynth)
- Selection-gate and release-gate planning
- Retire/replace metadata execution (this artifact)

## 26. Forbidden current uses

- Code deletion mandated by this plan
- Replacement implementation
- Production p-values
- Causal confidence intervals
- TrustReport production authorization
- CalibrationSignal ingestion
- MMM ingestion
- LLM decisioning
- Live API production endpoints
- Scheduler production runs
- Budget optimization
- Production routing for retired/blocked paths

## 27. Required future artifacts

| Artifact | Role |
|---|---|
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | **Immediate next** — selection-gate implementation |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release gate before authorization |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001` | SCM validation implementation |

## 28. Updated roadmap sequence

✅ `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` → ✅ **`METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`** → **`DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001`**

## 29. Downstream boundary

This execution plan does not delete code.
This execution plan does not implement replacements.
This execution plan does not authorize production inference.
This execution plan does not authorize production p-values.
This execution plan does not authorize causal confidence intervals.
This execution plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.
Downstream work remains paused.

## 30. Validation

Harness: `panel_exp/validation/method_family_retire_replace_execution_plan_001.py`  
Summary: `docs/track_d/archives/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_summary.json`  
Tests: `tests/validation/test_method_family_retire_replace_execution_plan_001.py`

## 31. Verdict

**`method_family_retire_replace_execution_plan_defined_no_downstream_authorization`**

All authorization flags remain **false**. Recommended next artifact: **`DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001`**.
