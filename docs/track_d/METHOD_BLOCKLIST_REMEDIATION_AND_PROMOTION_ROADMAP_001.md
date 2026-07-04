# METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001` |
| **Artifact type** | `roadmap_control_artifact` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `blocked_method_remediation_and_promotion_roadmap_documented_no_unblock_or_runtime_changes` |
| **Base commit** | `fd8b02a` (Unify DID instrument estimand semantics across governed runtime) |
| **Final verdict** | `blocked_method_remediation_and_promotion_roadmap_documented_no_unblock_or_runtime_changes` |

**Depends on:** `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` · `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` · `AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001` · `CLAIM_AUTHORIZATION_CONTRACT_001`

**Related prior roadmaps:** [`METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`](METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md) · [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001`](../METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) · [`METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_REPORT.md`](METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_REPORT.md)

---

## 2. Purpose

This artifact documents the **full remediation, revisit, and promotion pathway** for methods that are production-blocked, restricted, or research-only under `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001`.

**Core message:**

- **Blocked** means blocked from production-facing claims, trusted readout, ROI claims, causal approval, and production authorization.
- **Blocked does not mean deleted, forgotten, or permanently abandoned.**
- Blocked or research-only methods may remain available for research, diagnostics, characterization, and expert review, but can only be promoted through governed remediation, re-characterization, threshold enforcement, and promotion review.

This is **docs/governance only**. No method is unblocked in code. Production blocklist behavior is not loosened. No estimators, inference, diagnostics, claim authorization, or trusted reporting are implemented by this artifact.

---

## 3. Current blocklist state

Production catalog blocklist is **enforced and active** via `panel_exp/validation/production_catalog_blocklist_001.py` across:

- method suitability overlay (`method_suitability_runtime_001`)
- readout planning exclusion (`readout_plan_runtime_001`)
- executor adapter restriction metadata (`estimator_inference_executor_adapters_002`)
- execution-runtime production-context blocking (`estimator_inference_execution_runtime_001`)

**Status taxonomy:** `PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW` · `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW` · `PRODUCTION_CATALOG_DIAGNOSTIC_ONLY` · `PRODUCTION_CATALOG_RESEARCH_ONLY` · `PRODUCTION_CATALOG_BLOCKED` · `PRODUCTION_CATALOG_NOT_EVALUATED`

**Default conservative stance (from blocklist enforcement):**

| Family / combo | Production stance |
|----------------|-------------------|
| `DID_2X2_POINT_ESTIMATE` | Review/dry-run only; production claims blocked |
| `DID_BOOTSTRAP` / `DID_BOOTSTRAP_INFERENCE` | Blocked (inference not implemented in governed runtime) |
| `DID_TWFE_LIBRARY_RESEARCH` | Research-only |
| `TBR_RIDGE` + Kfold / Conformal / Jackknife / JKP | Blocked (negative/invalid interval evidence) |
| `TBR_FAMILY` aggregate | Blocked (unit-panel semantics unresolved) |
| `AUGSYNTH` + Conformal | Blocked until adapter + null calibration |
| `TROP`, `MTGP`, `BayesianTBR` | Research-only maturity |
| `RESEARCH_ONLY` / `UNVALIDATED` maturity | Blocked for production |
| Missing claim authorization runtime | Blocks production claim types |
| Missing statistical thresholds | Blocks default production eligibility |

No estimator in the current catalog is `PRODUCTION_SAFE`. See [`PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001_REPORT.md`](PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001_REPORT.md).

---

## 4. Method maturity ladder

```
DISCOVERED
  → IMPLEMENTED_RESEARCH
  → CHARACTERIZED
  → DIAGNOSTIC_ONLY
  → RESTRICTED_EXPERT_REVIEW
  → GOVERNED_RUNTIME_SUPPORTED
  → PRODUCTION_CANDIDATE
  → PRODUCTION_SAFE
```

**Clarifications (non-negotiable):**

| Maturity | Production-safe? | Claim-authorized? |
|----------|------------------|-------------------|
| `IMPLEMENTED_RESEARCH` | **No** | No |
| `CHARACTERIZED` | **No** | No |
| `DIAGNOSTIC_ONLY` | **No** | No |
| `RESTRICTED_EXPERT_REVIEW` | **No** | No |
| `GOVERNED_RUNTIME_SUPPORTED` | **No** | No — not claim-authorized |
| `PRODUCTION_CANDIDATE` | **No** — not automatically authorized | Requires promotion review + gates |
| `PRODUCTION_SAFE` | Required baseline | Still requires claim authorization and trusted readout gates |

Implemented ≠ production-safe. Characterized ≠ production-safe. Governed runtime supported ≠ claim-authorized. `PRODUCTION_SAFE` still requires claim authorization runtime and trusted readout compatibility before any production-facing claim.

---

## 5. Blocked-method revisit policy

Blocked methods are revisited **only after** all of the following gates pass:

1. **Instrument / estimand semantics are unambiguous** — canonical IDs, alias policy, and estimand mapping documented and enforced (see `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`).
2. **Assignment-panel integrity gates exist** — assignment compatibility and panel integrity validated at runtime (`ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` planned).
3. **Statistical promotion thresholds are numeric and enforced** — FPR, coverage, RMSE recovery, and related gates (`STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` planned).
4. **Method-specific recovery / calibration evidence passes** — OC batteries, null calibration, interval sanity, bias recovery per family.
5. **Required diagnostics and sensitivity checks exist** — governed readout diagnostics and sensitivity contract satisfied.
6. **Governed runtime support exists for the intended role** — executor/adapters, dry-run vs execution policy, production overlay.
7. **Production catalog status is updated through governance** — explicit catalog delta, not silent unblock.
8. **Claim authorization runtime consumes the required evidence before any claim** — `CLAIM_AUTHORIZATION_RUNTIME_001` planned.

**Explicit non-policies:**

- No method is unblocked for production merely because it **exists**.
- No method is unblocked for production merely because **tests pass**.
- No method is unblocked for production merely because it is **mathematically sophisticated**.
- No method is unblocked for production merely because it is **useful in research**.

---

## 6. Production unblock criteria

For any method/instrument to move toward production eligibility, the following evidence classes must be satisfied as applicable:

| Evidence class | Requirement |
|--------------|-------------|
| Estimand mapping | Canonical estimand documented; no ID/estimand mismatch |
| Instrument identity | Canonical instrument ID; alias policy enforced |
| Assignment compatibility | Design/assignment type compatible with method assumptions |
| Panel integrity | Unit/time panel structure validated; no aggregate/unit mismatch |
| Governed runtime support | Executor/adapters for intended role; dry-run vs execution policy |
| Diagnostic requirements | Required diagnostics emitted and threshold-gated |
| Sensitivity requirements | Required sensitivity checks available and consumed |
| Bias / RMSE recovery | Recovery evidence within numeric promotion thresholds |
| Coverage calibration | Interval coverage within declared bands on null/stress worlds |
| Type I error / false positive calibration | Null FPR within thresholds on supported worlds |
| Directional false signal control | Directional error rates characterized where applicable |
| Interval sanity | No negative widths, inverted bounds, or invalid interval evidence |
| Small-sample behavior | Characterized under declared minimum-N regimes |
| Null / A/A calibration | A/A and placebo null behavior within thresholds |
| Outlier / shock robustness | Stress-world behavior documented; failures gated |
| Production catalog status update | Explicit governance update to catalog status |
| Claim authorization compatibility | Claim types mapped to allowed evidence gates |
| Trusted readout compatibility | Trusted report handoff fields satisfied |

Not all rows apply to every method; promotion review must document which are required vs N/A for the requested maturity.

---

## 7. Required promotion evidence

Promotion from one maturity rung to the next requires a **promotion request packet** (future: `METHOD_PROMOTION_REVIEW_CONTRACT_001`) containing:

- method/instrument identity and canonical estimand
- current maturity and requested maturity
- characterization archive references (D5 OC JSON, audit reports)
- statistical threshold results (pass/fail with numeric values)
- diagnostic and sensitivity evidence
- governed runtime support evidence
- production catalog delta proposal
- remediation artifacts completed for known blockers
- approval / rejection / remediation-needed outcome with immutable decision record

**Future enforcement runtime:** `METHOD_PROMOTION_REVIEW_RUNTIME_001` will enforce: no promotion without required evidence; no promotion with failed thresholds; no promotion with missing diagnostics; no promotion with missing runtime support; no `PRODUCTION_SAFE` status without claim/report compatibility; **no silent unblock**.

**Umbrella remediation artifact (planned):** `METHOD_SPECIFIC_REMEDIATION_AND_RECHARACTERIZATION_001` — template and checklist for per-method remediation packets.

---

## 8. Method-family remediation lanes

| Planned artifact | Status | Cross-reference / notes |
|------------------|--------|---------------------------|
| `DID_BOOTSTRAP_REMEDIATION_AND_RECHARACTERIZATION_001` | Planned lane | Prior evidence: [`D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001`](D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md); governed bootstrap inference still not implemented |
| `TBRRIDGE_INFERENCE_REMEDIATION_AND_RECHARACTERIZATION_001` | Planned lane | Prior audit: [`TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`](TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_REPORT.md); D5-INST-TBRRIDGE-002 negative interval evidence |
| `SCM_JK_PLACEBO_PROMOTION_REVIEW_001` | Planned lane | SCM production-candidate chain: `SCM_PRODUCTION_CANDIDATE_VALIDATION_*` · null calibration · jackknife sensitivity · release gate review |
| `AUGSYNTH_ASCM_REMEDIATION_AND_PROMOTION_REVIEW_001` | Deferred | Cross-ref: `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` · [`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`](AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md); deferred until P0 validity hardening closes |
| `SDID_RESEARCH_CHARACTERIZATION_001` | Research lane | Cross-ref: [`SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`](SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_REPORT.md) |
| `BAYESIAN_TBR_RESEARCH_CHARACTERIZATION_001` | Research lane | Cross-ref: `INV-BAYESIAN-TBR-CALIBRATION-REPLAY-RESEARCH-PLAN-001`; JAX optional-deps path |
| `TROP_MTGP_RESEARCH_CHARACTERIZATION_001` | Research lane | Cross-ref: [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001`](../TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md); MTGP evidence_missing |

---

## 9. Promotion review artifacts to add later

| Artifact | Purpose |
|----------|---------|
| `METHOD_PROMOTION_REVIEW_CONTRACT_001` | Defines promotion request packet schema, evidence checklist, decision outcomes, immutable promotion decision record |
| `METHOD_PROMOTION_REVIEW_RUNTIME_001` | Enforces promotion gates at runtime; blocks silent unblock |
| `METHOD_SPECIFIC_REMEDIATION_AND_RECHARACTERIZATION_001` | Umbrella template for per-method remediation and re-characterization packets |

### METHOD_PROMOTION_REVIEW_CONTRACT_001 (planned contents)

- promotion request packet schema
- method/instrument identity fields
- current maturity / requested maturity
- required evidence checklist
- statistical threshold results attachment
- diagnostic evidence attachment
- sensitivity evidence attachment
- governed runtime support attestation
- production catalog delta specification
- approval / rejection / remediation-needed outcome enum
- immutable promotion decision record format

### METHOD_PROMOTION_REVIEW_RUNTIME_001 (planned enforcement)

- no promotion without required evidence
- no promotion with failed thresholds
- no promotion with missing diagnostics
- no promotion with missing runtime support
- no `PRODUCTION_SAFE` status without claim/report compatibility
- no silent unblock

---

## 10. Relationship to current P0 hardening lane

This roadmap **does not change** the active P0 execution sequence. Production blocklist remains enforced.

**P0 hardening lane (active):**

```
PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001 ✅
  → DID_INSTRUMENT_ESTIMAND_UNIFICATION_001 ✅
  → METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001 ✅ (this artifact — docs only)
  → ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001 (immediate next implementation)
  → STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001
  → GOVERNED_RANDOMIZATION_RUNTIME_001
  → SRM_BALANCE_READOUT_DIAGNOSTIC_001
  → CLAIM_AUTHORIZATION_RUNTIME_001
  → TRUSTED_READOUT_REPORT_CONTRACT_001
  → TRUSTED_READOUT_REPORT_RUNTIME_001
```

This artifact sits **after blocklist enforcement and DID unification** as governance documentation clarifying that blocked methods have explicit remediation paths. It does **not** authorize implementation skips or production exposure.

**Alternative next artifact:** `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001`

---

## 11. What remains blocked

Production-blocked combinations (production claims, trusted readout, ROI, causal approval):

- `DID_BOOTSTRAP` / `DID_BOOTSTRAP_INFERENCE` — inference not implemented; misleading if used for point-only execution
- `DID_2X2_POINT_ESTIMATE` — production causal/incremental/ROI claims (review/dry-run allowed)
- `TBR_RIDGE` + Kfold, Conformal, Jackknife, JKP — invalid/negative interval evidence
- `TBR_FAMILY` aggregate production paths — unit-panel semantics unresolved
- `AUGSYNTH` + Conformal — adapter + null calibration incomplete
- All `RESEARCH_ONLY` / `UNVALIDATED` maturity estimators for production claims
- Any method missing claim authorization runtime for requested claim type
- Any method failing statistical promotion thresholds (once enforced)

---

## 12. What remains research-only

| Method / family | Rationale |
|-----------------|-----------|
| `DID_TWFE_LIBRARY_RESEARCH` | Library TWFE in `panel_exp/methods/DID.py`; no governed runtime; separate from governed 2×2 point path |
| `SyntheticDID` / SDID | Implementation-readiness plan only; broad recovery evidence missing |
| `TROP` | Triply robust estimator; expert tuning; RTP-002 research charter |
| `MTGP` | GP prior fidelity and MCMC runtime uncharacterized |
| `BayesianTBR` / `BayesianTBRHorseShoe` | JAX optional-deps; registry ≠ NUTS MCMC production path |
| `TBRAutoSARIMAX` | Unclear fidelity; needs audit before OC |
| AugSynth non-CVXPY path | UNVALIDATED maturity; probe-only |

Research-only methods remain callable in research contexts subject to blocklist overlay (`is_research_allowed` where configured).

---

## 13. What can become diagnostic-only or restricted expert-review

| Method / combo | Path | Prerequisites |
|----------------|------|---------------|
| `DID_2X2_POINT_ESTIMATE` | Governed point-estimate review / diagnostic | Assignment-panel integrity; diagnostics emitted |
| SCM + UnitJackknife | Null monitor / diagnostic | Null calibration; D5-INF evidence; governed runtime integration |
| SCM + Placebo (studentized) | Restricted expert-review candidate | Placebo null calibration; diagnostic gates |
| TBRRidge + Kfold / BRB | Restricted diagnostic band | Already characterized as restricted diagnostic in D5 |
| Kfold (general) | Diagnostic band | Not null-monitor substitute; threshold labels |
| Matched-pair / randomization inference | Diagnostic / design validation | Governed randomization runtime |

SCM + unit jackknife / placebo may be among the **first** candidates for restricted expert-review or production-candidate review, but only after null calibration, diagnostic gates, and governed runtime integration are complete.

---

## 14. What can eventually become production-candidate

**None are production-candidates today.** Hypothesized eventual candidates (subject to full promotion review):

| Method / combo | Earliest realistic target | Blockers to clear |
|----------------|---------------------------|-------------------|
| SCM + UnitJackknife (+ optional placebo) | `RESTRICTED_EXPERT_REVIEW` → `PRODUCTION_CANDIDATE` | SCM production-candidate validation chain; claim runtime; thresholds |
| `DID_2X2_POINT_ESTIMATE` + governed inference (future) | `PRODUCTION_CANDIDATE` (conditional) | Bootstrap inference implemented, calibrated, threshold-enforced; DID conditional validation plan |
| A/B standard inference (matched randomization) | `PRODUCTION_CANDIDATE` | Governed randomization runtime; SRM/balance diagnostics |
| TBRRidge + Kfold/BRB (diagnostic role only) | `DIAGNOSTIC_ONLY` ceiling unless estimand resolved | Aggregate/unit geometry; not primary causal claim path |

Promotion to `PRODUCTION_CANDIDATE` requires `METHOD_PROMOTION_REVIEW_CONTRACT_001` packet approval. `PRODUCTION_SAFE` requires additional broad validation and claim authorization.

---

## 15. What should not be built yet

Per P0 hardening and audit verdict — **do not build yet:**

- Production TrustReport operations (API, scheduler, platform ops)
- LLM/MMM downstream decisioning authorization
- Estimator-shopping UI or automatic ensemble selection
- Adaptive experimentation / bandits in production path
- Bootstrap inference runtime before DID remediation and threshold enforcement (`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE` deferred)
- AugSynth/ASCM production remediation before P0 validity closure (`AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` paused)
- Advanced estimator production (SDID, TROP, MTGP, BayesianTBR) before research characterization lanes complete
- Silent production catalog unblocks or config-only "allow production" overrides without promotion review
- Claim authorization runtime before P0 hardening acceptance criteria pass

---

## 16. Acceptance criteria

| Criterion | Status |
|-----------|--------|
| Blocked-method revisit policy documented (8 gates) | ✅ |
| Method maturity ladder documented with non-safe clarifications | ✅ |
| Method-specific remediation lanes documented with cross-references | ✅ |
| Promotion review future artifacts defined | ✅ |
| Method-family remediation table complete | ✅ |
| Production blocklist remains enforced (no code loosening) | ✅ |
| No methods unblocked | ✅ |
| No runtime behavior changed | ✅ |
| No claim or production authorization added | ✅ |
| DID canonical names used (`DID_2X2_POINT_ESTIMATE`, `DID_BOOTSTRAP_INFERENCE`, `DID_TWFE_LIBRARY_RESEARCH`) | ✅ |
| Governance docs and investigation registry updated | ✅ |

---

## 17. Recommended next artifact

**Recommended:** `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` — assignment-panel mismatch blocks governed execution; prerequisite for meaningful method promotion.

**Alternative:** `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` — numeric FPR/coverage/recovery gates required before any production-candidate promotion review.

**Method-family next steps (after P0 hardening, not immediate):**

- `DID_BOOTSTRAP_REMEDIATION_AND_RECHARACTERIZATION_001`
- `SCM_JK_PLACEBO_PROMOTION_REVIEW_001`
- `METHOD_PROMOTION_REVIEW_CONTRACT_001`

---

## Appendix A — Method-family remediation table

| Method / instrument family | Current status | Why blocked/restricted | Research use allowed? | Diagnostic/expert-review path | Production unblock requirements | Required artifacts | Earliest promotion target | Notes |
|----------------------------|----------------|------------------------|----------------------|--------------------------------|--------------------------------|-------------------|---------------------------|-------|
| **DID_2X2_POINT_ESTIMATE** | `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW` / blocked for production claims | Point estimate only; no governed inference; claim auth missing | Yes (review/dry-run) | Governed point-estimate review; structural DID diagnostic | Estimand mapping; assignment compatibility; panel integrity; diagnostics; claim auth; catalog update | `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001`; `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | `RESTRICTED_EXPERT_REVIEW` | Canonical ID post `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` |
| **DID_BOOTSTRAP / DID_BOOTSTRAP_INFERENCE** | `PRODUCTION_CATALOG_BLOCKED` | Inference not implemented; negative bootstrap characterization; alias confusion resolved | Yes (research/library) | None for production | Bootstrap implementation; calibration; threshold pass; interval sanity; null FPR; claim auth | `DID_BOOTSTRAP_REMEDIATION_AND_RECHARACTERIZATION_001`; cross-ref `D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001` | `CHARACTERIZED` → remediation | Remains production-blocked until bootstrap inference implemented, corrected, calibrated, threshold-enforced |
| **DID_TWFE_LIBRARY_RESEARCH** | `PRODUCTION_CATALOG_RESEARCH_ONLY` | Library TWFE; no governed runtime; separate estimand | Yes | Expert review only with explicit TWFE estimand disclosure | Governed runtime support; diagnostics; TWFE-specific OC; catalog update | `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` ✅ | `IMPLEMENTED_RESEARCH` → `CHARACTERIZED` | Not interchangeable with governed 2×2 point path |
| **TBR / TBR aggregate** | `PRODUCTION_CATALOG_BLOCKED` | Aggregate estimand ≠ unit SCM; unresolved geometry | Yes (aggregate OC) | Aggregate diagnostic only | Unit/aggregate geometry resolution; assignment compatibility; recovery evidence | `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`; D5-INST-TBR-001 | `DIAGNOSTIC_ONLY` (aggregate) | `blocked_by_unresolved_geometry` on unit panel |
| **TBR_RIDGE_KFOLD** | `PRODUCTION_CATALOG_BLOCKED` | Negative/invalid interval evidence in D5-INST-TBRRIDGE-002 | Yes | Restricted diagnostic band (non-production) | Interval sanity; recovery calibration; re-characterization; thresholds | `TBRRIDGE_INFERENCE_REMEDIATION_AND_RECHARACTERIZATION_001` | `DIAGNOSTIC_ONLY` | Kfold diagnostic role may survive; production claims blocked |
| **TBR_RIDGE_CONFORMAL** | `PRODUCTION_CATALOG_BLOCKED` | Invalid interval evidence | Yes | Expert review after remediation | Interface/shape fixes; coverage calibration; null FPR | `TBRRIDGE_INFERENCE_REMEDIATION_AND_RECHARACTERIZATION_001` | `CHARACTERIZED` (post-remediation) | Production-blocked until re-characterization passes |
| **TBR_RIDGE_JACKKNIFE / TBR_RIDGE_JKP** | `PRODUCTION_CATALOG_BLOCKED` | ~79% null FPR (JK); ~29% (JKP); pooled-CF semantics | Yes | Restricted diagnostic with warnings | Pooled-CF pivot fix or retire; null calibration; threshold pass | `TBRRIDGE_INFERENCE_REMEDIATION_AND_RECHARACTERIZATION_001`; D5-TBRRIDGE-003 | Remediation or retire | May be retired rather than promoted |
| **SCM_UNIT_JACKKNIFE** | `PRODUCTION_CATALOG_DIAGNOSTIC_ONLY` / expert-review candidate | Null monitor framing; not primary causal claim | Yes | DCM-001 TrustReport reassessment path (restrictions) | Null calibration; diagnostic gates; governed runtime; thresholds; claim auth | `SCM_JK_PLACEBO_PROMOTION_REVIEW_001`; SCM production-candidate chain | `RESTRICTED_EXPERT_REVIEW` → `PRODUCTION_CANDIDATE` | Among first promotion-review candidates |
| **SCM_PLACEBO / SCM studentized placebo** | `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW` | Requires null calibration and diagnostic gates | Yes | Expert-review placebo path | Null/A/A calibration; placebo threshold gates; runtime integration | `SCM_JK_PLACEBO_PROMOTION_REVIEW_001` | `RESTRICTED_EXPERT_REVIEW` | Paired with SCM JK lane |
| **AUGSYNTH / ASCM** | `PRODUCTION_CATALOG_RESEARCH_ONLY` / blocked for production claims | UNVALIDATED/non-CVXPY; scale/path issues; P0 deferred | Yes (CVXPY research) | Diagnostic/restricted research | P0 validity closure; null calibration; D5 remediation; adapter | `AUGSYNTH_ASCM_REMEDIATION_AND_PROMOTION_REVIEW_001`; deferred `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` | `CHARACTERIZED` (post-P0) | Must not jump ahead of blocklist, DID unification, assignment integrity, thresholds |
| **AUGSYNTH_CONFORMAL** | `PRODUCTION_CATALOG_BLOCKED` | Adapter + null calibration incomplete | Yes | None for production | Conformal adapter; null calibration; interval sanity | `AUGSYNTH_ASCM_REMEDIATION_AND_PROMOTION_REVIEW_001`; D5-AUGSYNTH-CONFORMAL | Post-remediation review | Config override exists but default blocked |
| **SDID** | `PRODUCTION_CATALOG_RESEARCH_ONLY` | evidence_missing; unit/time-weight contracts | Yes | Research characterization | Broad recovery; diagnostics; runtime support; thresholds | `SDID_RESEARCH_CHARACTERIZATION_001`; `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` | `IMPLEMENTED_RESEARCH` → `CHARACTERIZED` | No production exposure in current phase |
| **BayesianTBR / Horseshoe TBR** | `PRODUCTION_CATALOG_RESEARCH_ONLY` | JAX optional; registry ≠ MCMC production path | Yes (optional deps) | Research only | Calibration replay; coverage; runtime support | `BAYESIAN_TBR_RESEARCH_CHARACTERIZATION_001` | `CHARACTERIZED` (research) | No production exposure in current phase |
| **TROP** | `PRODUCTION_CATALOG_RESEARCH_ONLY` | research_only maturity; expert tuning | Yes | Research audit path | Broad recovery; diagnostics; RTP-002 ladder | `TROP_MTGP_RESEARCH_CHARACTERIZATION_001`; TRIPLY_ROBUST audit program | `CHARACTERIZED` (research) | Parked not rejected |
| **MTGP** | `PRODUCTION_CATALOG_RESEARCH_ONLY` | evidence_missing; GP fidelity | Yes | Research only | MCMC runtime characterization; recovery evidence | `TROP_MTGP_RESEARCH_CHARACTERIZATION_001` | `IMPLEMENTED_RESEARCH` | future lane only — limited repo evidence |
| **Matched-pair / randomization inference** | Not fully governed in runtime | Missing governed randomization runtime | Yes (design layer) | Design validation / diagnostic | `GOVERNED_RANDOMIZATION_RUNTIME_001`; SRM/balance diagnostics | `GOVERNED_RANDOMIZATION_RUNTIME_001`; `SRM_BALANCE_READOUT_DIAGNOSTIC_001` | `GOVERNED_RUNTIME_SUPPORTED` | not evidenced as production instrument in current repo |
| **A/B standard inference** | Partially characterized | Claim auth missing; threshold enforcement missing | Yes | Standard inference diagnostic | Governed randomization; thresholds; claim auth; trusted readout | P0 hardening chain | `PRODUCTION_CANDIDATE` (conditional) | future lane only for production promotion |

---

## Appendix B — DID policy (canonical names)

Post `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`, use canonical IDs:

| Canonical ID | Policy |
|--------------|--------|
| `DID_2X2_POINT_ESTIMATE` | May support governed point-estimate review only; production claims blocked |
| `DID_BOOTSTRAP_INFERENCE` (`DID_BOOTSTRAP` alias) | Remains production-blocked until bootstrap inference is implemented, corrected, calibrated, and threshold-enforced |
| `DID_TWFE_LIBRARY_RESEARCH` | Remains research/expert-review unless governed runtime support and diagnostics are added |

Legacy `DID_BOOTSTRAP` point-estimate routing blocked by default (`allow_legacy_did_bootstrap_for_point_estimate=false`).

---

## Appendix C — TBR / TBRRidge policy

TBRRidge inference combos with invalid/negative interval evidence remain **production-blocked**. They require remediation, interface/shape fixes, interval sanity gates, recovery calibration, and re-characterization before promotion review. See `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`.

---

## Appendix D — SCM / AugSynth / SDID / Bayesian / TROP / MTGP policy summaries

- **SCM:** SCM + unit jackknife / placebo may be first candidates for restricted expert-review or production-candidate review, but only after null calibration, diagnostic gates, and governed runtime integration are complete.
- **AugSynth/ASCM:** Remediation deferred until P0 validity hardening closes. Must not jump ahead of blocklist, DID unification, assignment integrity, and statistical thresholds.
- **SDID / Bayesian / TROP / MTGP:** Remain research-only until broad recovery evidence, diagnostics, runtime support, and threshold gates exist. No production exposure in current roadmap phase.
