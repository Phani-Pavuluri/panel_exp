# METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001` |
| **Artifact type** | `method_portfolio_prioritization_checkpoint` |
| **Status** | `completed` |
| **Base commit** | `341d52c` (Plan SCM release gate decision) |
| **Strategic decision** | `shift_primary_method_focus_from_scm_to_augsynth_ascm_after_scm_closeout` |
| **Final verdict** | `method_portfolio_prioritization_checkpoint_logged_no_production_authorization` |

This artifact is a **roadmap/governance checkpoint only**. It records strategic method-portfolio prioritization. **No production authorization was granted.** **No runtime behavior changed.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001` | Assembled SCM evidence packet |
| `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001` | Defer/handoff decision plan |
| SCM evidence stack (validation/null/jackknife) | Metadata scaffolding |
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | Next primary method lane plan |
| `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` | TBRRidge boundary |
| `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` | Bayesian TBR boundary |
| `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001` | TROP deferred boundary |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | Portfolio retire/replace context |

---

## 3. Reason for checkpoint

SCM momentum risked monopolizing method development despite metadata-only evidence and explicit defer/handoff direction. This checkpoint records a strategic correction: SCM remains valuable as governance reference; primary implementation focus shifts to AugSynth/ASCM after SCM closeout.

---

## 4. Prior SCM work reconciliation

| Artifact | Outcome |
|----------|---------|
| Validation/null-calibration/jackknife implementations | Metadata scaffolding (31+30+37 areas) |
| Release-gate review plan/packet | Packet `assembled_for_review` |
| Release-gate decision plan | `defer_pending_empirical_validation`; handoff planned |

SCM produced governed contracts, registry patterns, and release-gate review infrastructure. **None of this authorizes production inference.**

---

## 5. SCM role going forward

**`governed_reference_candidate_and_validation_baseline`**

SCM closeout preserves evidence packet, governance patterns, and audit references. SCM is **not** the primary production-candidate implementation focus.

---

## 6. Why SCM should not remain the primary implementation focus

1. Evidence is metadata-only — no empirical validation, placebo calibration, or jackknife refits
2. Decision plan recommends defer pending empirical validation
3. Donor convex-combination limitations; AugSynth residual correction may be stronger where SCM is insufficient
4. Portfolio has multiple candidates requiring validation; SCM should not block them
5. Pursuing SCM production approval from metadata alone would violate release-gate boundaries

---

## 7. Method portfolio prioritization decision

**Priority order:**

| Priority | Lane |
|----------|------|
| 0 | Complete SCM decision-plan and closeout/handoff **without production approval** |
| 1 | AugSynth/ASCM point-estimate production-candidate validation |
| 2 | TBRRidge point-estimate validation |
| 3 | Shared inference validation framework for p-values/CIs |
| 4 | Bayesian TBR governed prior/posterior lane |
| 5 | TROP deferred until decisioning governance matures |

---

## 8. AugSynth/ASCM next-lane rationale

**Next primary method lane.** Residual correction can improve over plain SCM where donor convex combinations are insufficient. Requires residual-model governance, overfit controls, simulation coverage, null calibration, and uncertainty validation (`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`). **Not production-approved.**

**First post-SCM method lane:** `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001`

---

## 9. TBRRidge later-lane rationale

**Later practical point-estimate candidate.** Strong fit for noisy geo time-series counterfactuals and operational workflows. Ridge inference, p-values, and CIs remain unapproved until bootstrap/placebo/conformal or other inference validation (`TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`). **Not production-approved.**

---

## 10. Bayesian TBR governed-prior lane rationale

**Governed-prior research/calibration lane.** Useful when compatible priors exist. Posterior intervals are **not** automatically causal CIs. Prior scale/freshness/conflict governance and simulation-based calibration required (`BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`). **Not production-approved.**

---

## 11. TROP deferred/research rationale

**Deferred/research.** Optimization/decisioning introduces higher governance burden. No production decisioning until objective, constraints, action space, regret/sensitivity, policy guardrails, and human override governance are mature (`TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`). **Not production-approved.**

---

## 12. Separated authorization model: estimates vs p-values vs CIs vs decisioning

| Separation | Rule |
|------------|------|
| Point estimates → p-values | Production point-estimate authorization does **not** imply p-value authorization |
| P-values → causal CIs | P-value authorization does **not** imply causal CI authorization |
| Causal CIs → selector/router | Causal CI authorization does **not** imply selector/router authorization |
| Selector/router → downstream | Selector/router authorization does **not** imply downstream decisioning or budget optimization |

Each method and each claim type requires a **separate release gate**.

---

## 13. Near-term roadmap update

1. **SCM:** `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` (decision plan complete)
2. **Portfolio:** Shift primary focus to AugSynth/ASCM remediation implementation
3. **TBRRidge/Bayesian TBR/TROP:** Remain separate later lanes with existing boundary audits
4. **Shared inference:** Framework for p-values/CIs after point-estimate candidates advance

---

## 14. Blocked production authorization domains

All methods remain unauthorized for production inference, p-values, causal CIs, selector/router production use, multicell claims, and downstream integrations. SCM production approval is explicitly **not recommended**.

---

## 15. Required future validation work by method

| Method | Required before any approval |
|--------|------------------------------|
| SCM | Empirical validation, placebo calibration, jackknife results, human governance review |
| AugSynth/ASCM | Residual governance, overfit controls, DGP coverage, null calibration, uncertainty validation |
| TBRRidge | Inference validation (bootstrap/placebo/conformal), production-boundary audit closure |
| Bayesian TBR | Prior governance, simulation calibration, posterior≠causal CI boundary |
| TROP | Decisioning governance maturity (objective, constraints, guardrails, human override) |

---

## 16. Governance boundaries

- Checkpoint is logging only — no estimator implementation, no runtime change
- SCM remains `production_candidate_gated` as reference candidate
- No method marked production-approved
- Package-side agents remain deferred
- Downstream integrations remain paused

---

## 17. Risks and ambiguities

- Checkpoint may be read as abandoning SCM — it is a **focus shift**, not abandonment
- AugSynth remediation implementation artifact not yet defined in full detail
- Portfolio handoff sequencing must not collide with SCM closeout artifact
- Shared inference framework timing depends on point-estimate candidate progress

---

## 18. Recommended next artifacts

| Artifact | Role |
|----------|------|
| `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` | SCM closeout + formal handoff |
| `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | First post-SCM primary method lane |

---

## 19. Final verdict

**`method_portfolio_prioritization_checkpoint_logged_no_production_authorization`**

Method portfolio prioritization checkpoint logged. SCM is no longer the primary production-candidate focus; it remains a governed reference candidate and validation baseline. AugSynth/ASCM becomes the next primary method lane after SCM closeout. No production authorization granted for any method.

---

| Summary | `docs/track_d/archives/METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001_summary.json` |
| Module | `panel_exp/validation/method_portfolio_prioritization_checkpoint_001.py` |
| Tests | `tests/validation/test_method_portfolio_prioritization_checkpoint_001.py` |
