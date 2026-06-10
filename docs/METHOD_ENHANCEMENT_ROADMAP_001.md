# Method Enhancement Roadmap 001

**Document ID:** METHOD-ENHANCEMENT-ROADMAP-001  
**Title:** Method Enhancement Roadmap 001  
**Status:** Planning / post-Level-B synthesis  
**Scope:** GeoX / `panel_exp` repository only  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Guardrails:** Documentation only · no promotion · no TrustReport/F-DECISION wiring · no CalibrationSignal/MMM/LLM changes · no suitability claims · no primary/secondary/directional evidence labels

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Method Enhancement Roadmap 001 |
| Status | **Planning / post-Level-B synthesis** |
| Scope | GeoX / `panel_exp` only |
| Authority | Synthesis and prioritization — **not** production authorization |

This document converts completed D5-STAT Level B characterization into a **targeted enhancement plan**. It does not modify estimators, designs, or inference code.

---

## 2. Purpose

The D5-STAT queue established **what the codebase does today** under controlled synthetic worlds. This roadmap explains **what to improve next** and **why**, across:

- **Designs** — assignment contracts, balance metadata, leakage guards
- **Estimators** — SCM, AugSynth, TBR, DID, TBRRidge, SARIMAX operators
- **Inference** — JK, bootstrap, KFold, BRB, Conformal, Bayesian posteriors
- **Geometry bridges** — unit-panel, aggregate 2-row, per-cell multi-cell, pooled multi-cell, supergeo, trim
- **Readout semantics** — level vs fractional vs cumulative scale; interval and coverage targets
- **Bayesian methods** — prior/likelihood/posterior contracts (deferred, not rejected)
- **TBRRidge / time-series operators** — split policy, leakage, diagnostic bands
- **TBR-SARIMAX and Auto-SARIMAX** — aggregate counterfactual operators with explicit model-selection policy
- **Triply robust / TROP** — nuisance-model audit ladder (parked; not rejected)
- **Design methods** — design-side audit ladder ([`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md)); estimator/inference parity incomplete until complete

---

## 3. Completed evidence base

| Artifact | Type | Verdict | Report |
|----------|------|---------|--------|
| **D5-STAT-SMOKE-CALLABLE-001** | Level A smoke | `smoke_pass_with_caveats` | [`D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) |
| **D5-STAT-SCM-JK-001** | Level B unit-panel | `characterization_mixed_requires_followup` | [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) |
| **D5-STAT-AUGSYNTH-POINT-001** | Level B unit-panel point | `characterization_mixed_requires_followup` | [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) |
| **D5-STAT-TBR-AGG-001** | Level B aggregate 2-row point | `characterization_mixed_requires_followup` | [`D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md) |
| **D5-STAT-DID-BOOTSTRAP-001** | Level B DID embedded bootstrap | `characterization_mixed_requires_followup` | [`D5_STAT_DID_BOOTSTRAP_001_REPORT.md`](track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md) |
| **D5-STAT-MCELL-PERCELL-001** | Level B per-cell execution | `characterization_pass_with_caveats` | [`D5_STAT_MCELL_PERCELL_001_REPORT.md`](track_d/D5_STAT_MCELL_PERCELL_001_REPORT.md) |

**Queue status:** D5 Level B complete. Design audit ladder through **contract schema** ✅ Accepted. Next enhancement artifact: **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** (Phase 2 emission).

---

## 4. Key findings from completed D5 artifacts

### SCM-JK (`D5-STAT-SCM-JK-001`)

- **Structurally clean intervals:** zero orientation failures, zero negative half-widths on feasible runs.
- **Mixed stress-null behavior:** elevated null FPR on `weak_signal_null` (~23%) and `post_shock_null` (~33%); `clean_null` modest (~7%).
- **Readout/coverage caveats:** injected-world coverage low on level readout vs fractional injection truth; sign recovery strong.

### AugSynth point (`D5-STAT-AUGSYNTH-POINT-001`)

- **Clean injected lift recovery:** directionally correct on injected worlds; ratios near 1.0 on clean/noisy lift.
- **No uncertainty claim:** point-only path; intervals explicitly not applicable.
- **Stress null directional caveats:** high directional false signal on weak-signal and donor-stress worlds.

### TBR aggregate (`D5-STAT-TBR-AGG-001`)

- **Excellent injected recovery:** ~1.0 recovery ratios on clean/noisy/short-post injected worlds; 0% sign errors.
- **High null directional FPR:** 0.87–1.0 on null/trend/shock worlds under fixed threshold — point mass without calibrated null decision rule.
- **Callable/finite stable:** 105/105 feasible; aggregate geometry guard held.

### DID bootstrap (`D5-STAT-DID-BOOTSTRAP-001`)

- **Interval orientation clean:** no orientation failures or negative half-widths.
- **0% injected cumulative coverage:** bootstrap CIs on cumulative scale do not cover injected cumulative truth in this battery.
- **Readout mismatch:** directional point recovery reasonable; interval target vs scored truth misaligned (cumulative ATT vs injected cumulative level).

### MCELL per-cell (`D5-STAT-MCELL-PERCELL-001`)

- **Cell/method identity preserved:** 1.0 across all worlds; 264 per-cell results, 0 missing cells.
- **No pooling:** `pooled_effect_emitted` and `pooled_interval_emitted` false everywhere.
- **Caveat under one-cell post-shock:** `post_shock_one_cell` elevated sign-error (~0.63) while structural guardrails hold.

### General conclusion

Major gaps are **readout semantics**, **inference target alignment**, **geometry compatibility contracts**, and **suitability policy prerequisites** — not merely whether code is callable. Enhancement must be evidence-led, not speculative refactors.

---

## 5. Why method enhancement starts after this synthesis

1. **Baseline first:** D5-STAT measured behavior without changing production estimators/inference during characterization.
2. **Evidence baseline exists:** Six archives + Layer 1–5 registers provide reproducible starting points.
3. **Targeted enhancement:** Improvements should cite specific D5 findings (e.g., DID cumulative coverage, TBR null FPR).
4. **No promotion by enhancement:** Any code change requires **rerun validation**; enhancement ≠ suitability ≠ TrustReport eligibility.

---

## 6. Deferred families and rationale

| Family | Why deferred |
|--------|----------------|
| **Bayesian methods** | Require prior/likelihood/posterior estimand contracts, convergence diagnostics, calibration semantics (INV-015 registry vs MCMC separation). |
| **TBRRidge / time-series estimators** | Require split policy, leakage checks, KFold/TSKFold/BRB/Conformal semantics before governed uncertainty claims. |
| **TBR-SARIMAX** | Aggregate counterfactual operator — needs frequency, seasonality, differencing, residual diagnostics, forecast-vs-causal interval separation. |
| **TBR-Auto-SARIMAX** | Auto model selection without post-period leakage policy is unsafe; needs audit trail and fallback rules. |
| **Supergeo / trim designs** | Geometry bridges undefined (F-GEO-003/004); flat readout vs unit-panel mismatch. |
| **Pooled multi-cell** | Causal pooling ADR unset; per-cell evidence explicitly does not authorize portfolio lift. |
| **Inference wrappers** (KFold, TSKFold, BRB, Conformal, bootstrap variants) | Each needs interval target, coverage definition, null rule — blocked until `INFERENCE_READOUT_SEMANTICS_001`. |
| **AugSynth JK / Conformal** | IMPL-JK-001, IMPL-CONF-001, G1–G8 fidelity gaps. |

Deferred ≠ rejected. Each family moves through **contract artifact → targeted fix → rerun D5/Level C**.

---

## 7. Enhancement lanes (planned artifacts)

### A. INFERENCE_READOUT_SEMANTICS_001 ✅

**Status:** **Complete (Accepted)** — [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

Standardizes:

- Level vs fractional vs cumulative effect scale
- Interval estimand target
- Coverage target and nominal calibration scope
- Null decision rule vs directional signal rule
- Cumulative vs average post-period readout

**Feeds:** SCM-JK, DID bootstrap, TBRRidge, suitability v2, protocol v2.

### B. GEOMETRY_BRIDGE_REQUIREMENTS_001 ✅

**Status:** **Complete (Accepted)** — [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)

Define bridge requirements and blocked transitions for:

- Unit-panel · aggregate 2-row · multi-cell per-cell · pooled multi-cell · supergeo · trim

**Feeds:** TBR aggregate generalization guardrails, MCELL pooling ADR, TrustReport geometry gates.

### C. DESIGN_OUTPUT_CONTRACT_001 ✅

**Status:** **Complete (Accepted)** — [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

Governed **DesignOutputContract** schema for all designs: identity, unit universe, assignment, multi-cell, geometry, trim/supergeo, balance, power/MDE, compatibility hints, forbidden claims, PASS/WARN/BLOCK policy.

**Feeds:** ✅ `DESIGN_CODE_INVENTORY_001` → ✅ `DESIGN_LITERATURE_ALIGNMENT_001` → ✅ `DESIGN_IMPLEMENTATION_VALIDATION_001` → ✅ `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` → combination matrix v2 → suitability v2.

### D. SCM_JK_STRESS_NULL_CALIBRATION_001

Address elevated stress-null FPR; clarify JK interval target; diagnostics and blocking conditions for poor pre-fit / shock worlds.

**Evidence input:** [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md).

### E. AUGSYNTH_INFERENCE_BRIDGE_001

AugSynth **point** characterized; inference paths (JK, placebo, conformal, KFold) remain blocked. Define appropriate uncertainty path post G1–G8.

**Evidence input:** [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md).

### F. TBR_READOUT_SEMANTICS_001

Address high null directional FPR; separate point recovery from rejection/decision rules; define aggregate causal readout without unit-panel generalization.

**Evidence input:** [`D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md).

### G. DID_BOOTSTRAP_CUMULATIVE_READOUT_FIX_001

Fix cumulative injected truth vs bootstrap interval mismatch; clarify whether interval targets cumulative, average, or period-level ATT.

**Evidence input:** [`D5_STAT_DID_BOOTSTRAP_001_REPORT.md`](track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md).

### H. MCELL_PERCELL_GUARD_HARDENING_001

Preserve cell identity; prohibit pooled claims; cell-level failure policy; strengthen shared-control exclusion rules.

**Evidence input:** [`D5_STAT_MCELL_PERCELL_001_REPORT.md`](track_d/D5_STAT_MCELL_PERCELL_001_REPORT.md).

### I. TBRRIDGE_OPERATOR_CONTRACT_001

TBRRidge estimand · time split policy · KFold/TSKFold/BRB/Conformal semantics · leakage checks · diagnostics.

**Precedes / pairs with:** `D5-STAT-TBRRIDGE-INF-001` characterization.

### J. TBR_SARIMAX_OPERATOR_CONTRACT_001

SARIMAX as **aggregate 2-row time-series counterfactual operator**:

- Outcome: treated aggregate series
- Exogenous: control aggregate series
- Forecast: untreated treated counterfactual
- Readout: observed post treated minus forecast counterfactual
- Specify frequency, seasonality, minimum pre-period, stationarity/differencing, residual diagnostics

### K. TBR_AUTO_SARIMAX_MODEL_SELECTION_POLICY_001

Safe auto-selection: candidate grid · AIC/BIC policy · no post-period leakage · convergence handling · fallback · model-selection audit trail · uncertainty caveat for selection

### L. BAYESIAN_METHOD_SPECIFICATION_001

Bayesian model families · priors · likelihoods · posterior estimands · convergence · PPC · sensitivity · calibration semantics

### M. TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001 ✅

**Status:** **Proposed (parked)** — [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md)

Triply robust / TROP requires the **same audit rigor** as characterized estimator families. **No implementation** in this artifact. Future sequence:

1. `TRIPLY_ROBUST_LITERATURE_ALIGNMENT_001`  
2. `TRIPLY_ROBUST_IMPLEMENTATION_GAP_ANALYSIS_001`  
3. `TRIPLY_ROBUST_STATISTICAL_VALIDATION_PROTOCOL_001`  
4. `TRIPLY_ROBUST_COMBINATION_MATRIX_001`  
5. `TRIPLY_ROBUST_SUITABILITY_EXTENSION_001`  
6. Future D5-style characterization **only if** implementation exists under separate plan  

**Immediate program priority:** `DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001` (design-side) — TROP audit steps follow design/readout/geometry/guardrail/suitability/schema contracts, not implementation.

### N. DESIGN_AUDIT_PROGRAM_001 ✅

**Status:** **Accepted** — [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md)

Design methods require the **same audit rigor** as estimator/inference families. Estimator/inference audit parity is **not complete** until the design ladder completes. **No implementation** in this artifact. Future sequence:

1. `DESIGN_OUTPUT_CONTRACT_001` ✅ **Accepted** — [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)  
2. `DESIGN_CODE_INVENTORY_001` ✅ **Accepted** — [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md)  
3. `DESIGN_LITERATURE_ALIGNMENT_001` ✅ **Accepted** — [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md)  
4. `DESIGN_IMPLEMENTATION_VALIDATION_001` ✅ **Accepted** — [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md)
5. `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` ✅ **Accepted** — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md)
6. `DESIGN_COMBINATION_VALIDATION_MATRIX_001` ✅ **Accepted** — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md)  
7. `DESIGN_GUARDRAILS_001` ✅ **Accepted** — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md)  
8. `DESIGN_SUITABILITY_FRAMEWORK_001` ✅ **Accepted** — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)  
9. `DESIGN_CONTRACT_ENFORCEMENT_PLAN_001` ✅ **Accepted** — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md)  
10. `DESIGN_CONTRACT_SCHEMA_001` ✅ **Accepted** — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md)  
11. `DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001` *(next)*  
11. Method-specific design audits as needed (supergeo, trim, QuickBlock integration)

---

## 8. TBR-SARIMAX and Auto-SARIMAX positioning

- **Not a drop-in replacement** for simple class TBR aggregate point readout.
- **Enhanced operator** for aggregate time-series counterfactual settings with explicit time-series structure.
- **Governed separately** from `TBR-AGG-POINT` D5 evidence — no generalization from aggregate 2-row TBR characterization.
- **Auto-SARIMAX prohibited** without `TBR_AUTO_SARIMAX_MODEL_SELECTION_POLICY_001`.
- **Forecast intervals ≠ causal intervals** — must not flow into TrustReport or CalibrationSignal without validation.

---

## 9. Bayesian positioning

- **Deferred, not rejected** — may matter for hierarchical geo effects and MMM calibration paths.
- Requires **separate** prior/likelihood/posterior semantics (`BAYESIAN_METHOD_SPECIFICATION_001`).
- **No shortcut** into TrustReport or CalibrationSignal without validation archives and governance gates.
- Registry Bayesian handler ≠ BayesianTBR MCMC (INV-015) — enhancement must preserve identity separation.

---

## 10. Immediate next queue

| Step | Artifact | Mode |
|------|----------|------|
| **D5-STAT-TBRRIDGE-INF-001** | ✅ **Complete** — `characterization_mixed_requires_followup`; see [`D5_STAT_TBRRIDGE_INF_001_REPORT.md`](track_d/D5_STAT_TBRRIDGE_INF_001_REPORT.md) |
| **INFERENCE_READOUT_SEMANTICS_001** | ✅ **Complete (Accepted)** — [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) |
| **GEOMETRY_BRIDGE_REQUIREMENTS_001** | ✅ **Complete (Accepted)** — [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) |
| **DESIGN_OUTPUT_CONTRACT_001** | ✅ **Complete (Accepted)** — [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) |
| **DESIGN_CODE_INVENTORY_001** | ✅ **Complete (Accepted)** — [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) |
| **DESIGN_LITERATURE_ALIGNMENT_001** | ✅ **Complete (Accepted)** — [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) |
| **DESIGN_IMPLEMENTATION_VALIDATION_001** | ✅ **Complete (Accepted)** — [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) |
| **DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001** | ✅ **Complete (Accepted)** — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| **DESIGN_COMBINATION_VALIDATION_MATRIX_001** | ✅ **Complete (Accepted)** — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) |
| **DESIGN_GUARDRAILS_001** | ✅ **Complete (Accepted)** — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) |
| **DESIGN_SUITABILITY_FRAMEWORK_001** | ✅ **Complete (Accepted)** — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) |
| **DESIGN_CONTRACT_ENFORCEMENT_PLAN_001** | ✅ **Complete (Accepted)** — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) |
| **DESIGN_CONTRACT_SCHEMA_001** | ✅ **Complete (Accepted)** — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) |
| **Next enhancement** | **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** |
| Constraint | No governed uncertainty claim until readout semantics proven |
| Feeds | `TBRRIDGE_OPERATOR_CONTRACT_001` · `INFERENCE_READOUT_SEMANTICS_001` |

Do not skip TBRRidge characterization to begin code enhancement — it completes the D5 queue before contract-heavy refactors.

---

## 11. Post-D5 enhancement order

Recommended sequence:

1. Execute **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** (design-side)
2. Targeted method-family fixes (TBR readout, DID cumulative fix, SCM stress-null, TBRRidge operator contract, …)
4. **`TBR_READOUT_SEMANTICS_001`**
5. **`TBRRIDGE_OPERATOR_CONTRACT_001`**
6. **`TBR_SARIMAX_OPERATOR_CONTRACT_001`**
7. **`TBR_AUTO_SARIMAX_MODEL_SELECTION_POLICY_001`**
8. **`BAYESIAN_METHOD_SPECIFICATION_001`**
9. Targeted method upgrades (D, E, F, G, H lanes as prioritized by contracts)
10. **Suitability framework v2**
11. TrustReport / CalibrationSignal / MMM / LLM role assignment — **only after explicit gates** (§12)

---

## 12. Governance gates

No enhanced method may be promoted unless **all** hold:

| Gate | Requirement |
|------|-------------|
| Method contract | Operator/spec artifact exists (lanes A–L as applicable) |
| Geometry bridge | `GEOMETRY_BRIDGE_REQUIREMENTS_001` row satisfied |
| Readout semantics | `INFERENCE_READOUT_SEMANTICS_001` defines estimand/interval/coverage |
| Validation evidence | D5 or Level C archive with characterization verdict |
| Suitability update | Framework v2 row revised with evidence citations |
| TrustReport role | Explicit approval via future role framework |
| CalibrationSignal | Explicit eligibility approval |
| MMM / LLM downstream | Explicit approval |

---

## 13. Non-goals

This roadmap does **not**:

- Promote any method or combination
- Claim production readiness or statistical validation
- Wire TrustReport / F-DECISION
- Change CalibrationSignal / MMM / LLM behavior
- Authorize pooled multi-cell causal or portfolio effects
- Permit Auto-SARIMAX without model-selection policy
- Provide a Bayesian shortcut to product roles
- Assign primary / secondary / directional evidence labels

---

## 14. Required roadmap/audit updates checked

| Document | Inspected | Updated |
|----------|-----------|---------|
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | ✅ | ✅ — post-Level-B synthesis link |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | ✅ | ✅ — enhancement roadmap section |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | ✅ | ✅ — register entry |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | ✅ | ✅ — controlling enhancement plan cross-link |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | ✅ | ✅ — suitability v2 dependency note |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | ✅ | ✅ — deferred → enhancement note |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | ✅ | ✅ — protocol v2 consumption note |

**D5 reports inspected (evidence citations):**

- [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md)
- [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md)
- [`D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md)
- [`D5_STAT_DID_BOOTSTRAP_001_REPORT.md`](track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md)
- [`D5_STAT_MCELL_PERCELL_001_REPORT.md`](track_d/D5_STAT_MCELL_PERCELL_001_REPORT.md)

---

*METHOD-ENHANCEMENT-ROADMAP-001 v1.1.6 — DESIGN_CONTRACT_SCHEMA_001 accepted; next = DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.*
