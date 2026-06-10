# DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001

**Document ID:** DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001  
**Type:** Post-foundation suitability policy framework — **no production wiring**  
**Status:** **complete** (register + generator; no OC execution)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) — post Layer 5

**Machine-readable register:** [`track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json`](track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json) (30 rows; regenerate: `python -m panel_exp.validation.design_estimator_inference_suitability_framework_001`)

**Generator:** [`panel_exp/validation/design_estimator_inference_suitability_framework_001.py`](../panel_exp/validation/design_estimator_inference_suitability_framework_001.py)

**Primary input:** [`METHOD_COMBINATION_VALIDATION_MATRIX_001`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) · Layers 1–4 as supporting context

**Guardrails:** No promotion · no TrustReport/F-DECISION wiring · no CalibrationSignal/MMM/LLM · no primary/secondary/directional labels

---

## 1. Purpose

Define **how** design × estimator × inference × geometry × estimand combinations will eventually be classified for product use — **without** assigning suitability, trust roles, or production integration today.

| Question | This framework answers |
|----------|------------------------|
| What evidence before diagnostic use? | `minimum_evidence_before_diagnostic_use` per row |
| What evidence before a suitability claim? | `minimum_evidence_before_suitability_claim` — requires **completed** D5-STAT archives |
| What before role assignment later? | `minimum_evidence_before_role_assignment` — requires future `TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001` |
| What is allowed today? | `current_allowed_use` — typically `oc_execution_only` or `planning_only` |
| What is forbidden today? | `current_forbidden_use` — TrustReport roles, CalibrationSignal, MMM, LLM product rec |

**Not answered here:** “This method is primary/secondary/directional” · “feeds TrustReport today” · “production-ready” · “promoted.”

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Layer / step | Status |
|--------------|--------|
| Layers 1–5 | ✅ Complete |
| **Suitability framework** | ✅ **This artifact** — policy only |
| D5-STAT smoke (Level A) | ✅ [`D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) |
| D5-STAT SCM+JK Level B | ✅ [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) |
| D5-STAT AugSynth point Level B | ✅ [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) |
| D5-STAT TBR aggregate Level B | ✅ [`D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md) |
| D5-STAT DID bootstrap Level B | ✅ [`D5_STAT_DID_BOOTSTRAP_001_REPORT.md`](track_d/D5_STAT_DID_BOOTSTRAP_001_REPORT.md) |
| D5-STAT MCELL per-cell Level B | ✅ [`D5_STAT_MCELL_PERCELL_001_REPORT.md`](track_d/D5_STAT_MCELL_PERCELL_001_REPORT.md) |
| D5-STAT OC execution | ✅ Complete through TBRRidge INF |
| Post-D5 readout semantics | ✅ [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) (**Accepted**) |
| Post-D5 geometry bridge | ✅ [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) (**Accepted**) |
| Post-D5 design output contract | ✅ [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) (**Accepted**) |
| Post-D5 design code inventory | ✅ [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) (**Accepted**) |
| Post-D5 design literature alignment | ✅ [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) (**Accepted**) |
| Post-D5 design implementation validation | ✅ [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) (**Accepted**) |
| Post-D5 design statistical validation protocol | ✅ [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) (**Accepted**) |
| Design combination matrix | ✅ [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) |
| Design guardrails | ✅ [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) |
| **Design-side suitability** | ✅ [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) — **distinct layer** (see §2.1) |
| Next enhancement | **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`** |
| Post-Level-B enhancement synthesis | ✅ [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) |
| Trust role assignment | **Blocked** — `TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001` after OC evidence |
| Design audit program | ✅ [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) (**Accepted**) |

### 2.1 Distinction from design-side suitability framework

| Artifact | Scope | Question answered |
|----------|-------|-------------------|
| **This artifact** (`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`) | Design × **estimator × inference × geometry** suitability surface | Is this **readout method path** suitable for a reference design geometry? |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | **Design-side** structural suitability | Is this **design method's evidence** contract-complete, adapter-ready, bridge-ready, and validation-ready? |

**Do not collapse** these artifacts. Final product suitability requires **both** plus guardrails PASS and executed validation. This estimator/inference framework rows use reference designs; design-side suitability governs actual design evidence emission.

**Suitability v2 dependency:** Requires readout semantics + geometry bridge + **design output contract** + **design code inventory** + **design literature alignment** + **design implementation validation** + **design statistical validation protocol** + **design combination matrix** + **design guardrails** + **design-side suitability framework** (all ✅ Accepted), **executed design statistical validation** (`D5-DES-STAT-*` archives) before suitability rows may advance. **Suitability remains blocked until guardrails are satisfied** per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) — 0 downstream PASS at authoring. **Suitability remains blocked until actual design statistical validation is executed** per [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) — protocol definition alone does not authorize suitability. **Implementation validation alone does not authorize suitability.** **Design names in suitability rows must match inventory IDs in [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) (DES-001–DES-031).** **Current framework is incomplete without design audit parity.**

---

## 3. Inputs from Layers 1–5

| Layer | Role in suitability framework |
|-------|------------------------------|
| 1 — Code inventory | Canonical modules and names; **design-side:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) |
| 2 — Literature alignment | Estimand and literature scope |
| 3 — Implementation validation | Gaps → `required_implementation_fixes` |
| 4 — Statistical protocol | D5-STAT artifact names and batteries |
| 5 — Combination matrix | `validation_matrix_status` → `suitability_class` |

**Coverage:** Every Layer 5 matrix row (30) maps to exactly one suitability-framework row.

---

## 4. Difference between OC-ready, suitable, trusted, and promoted

| Term | Meaning in this program |
|------|-------------------------|
| **OC-ready** (Layer 5) | Protocol exists; combination may run D5-STAT — **not** suitable |
| **Suitable** (future) | Completed D5-STAT evidence meets protocol acceptance — **not** defined here |
| **Trusted** (future) | Explicit trust-framework charter + role rules — **not** this artifact |
| **Promoted** (future) | Product eligibility after layers 1–5 + OC + suitability + roles — **always false** in JSON |

**Rule:** OC-ready ⊄ suitable ⊄ trusted ⊄ promoted.

---

## 5. Suitability taxonomy

| `suitability_class` | Meaning |
|---------------------|---------|
| `not_yet_assessed` | Reserved — unmapped edge cases |
| `oc_ready_not_suitable_yet` | May run smoke/OC; no suitability claim |
| `diagnostic_candidate_pending_oc` | May become diagnostic evidence **after** OC |
| `suitability_candidate_pending_oc` | May become suitability evidence **after** stronger OC |
| `blocked_before_suitability` | No suitability path until blockers cleared |
| `bridge_required_before_suitability` | ADR + bridge validation required |
| `implementation_fix_required` | Close Layer 3 gaps before OC/suitability |
| `research_only` | RTP/research charter only |
| `quarantine_or_deprecate` | No product path |

**Forbidden class labels:** primary · secondary · directional · trusted · promoted · production-ready · calibration_signal_eligible · governed_uncertainty

---

## 6. Evidence requirements

| Stage | Requirement |
|-------|-------------|
| Diagnostic use | Completed Level B D5-STAT characterization for that combo + geometry scope |
| Suitability claim | Completed Level C calibration + interval semantics where applicable |
| Role assignment | `TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001` + suitability evidence + explicit charter |

Protocol registers (Layers 4–5) **do not** satisfy suitability evidence.

---

## 7. Geometry scoping rules

1. Unit-panel OC does **not** transfer to aggregate 2-row, supergeo, trim, or pooled multi-cell.  
2. Per-cell multi-cell OC does **not** authorize pooled causal lift.  
3. TBR aggregate evidence applies **only** to `aggregate_two_row` combinations.  
4. Supergeo/trim require bridge ADR + dedicated D5-STAT-*-BRIDGE archives.

---

## 8. Estimand and effect-scale scoping rules

1. ATT counterfactual gap (SCM) ≠ ridge penalized gap (TBRRidge) ≠ DiD panel estimand.  
2. Level vs relative export (G7) must match claimed effect scale in evidence.  
3. Placebo rows are **falsification** — not suitability for ATT claims.  
4. Pooled multi-cell causal lift blocked until pooling ADR defines estimand.

---

## 9. Inference semantics requirements

1. Point-only paths require bias/recovery OC — not interval suitability.  
2. Interval suitability requires orientation, degeneracy, and coverage/FPR evidence.  
3. Jackknife on AugSynth blocked (IMPL-JK-001) until strata fixed + OC.  
4. Conformal on AugSynth blocked (IMPL-CONF-001) until redesign + OC.  
5. Registry Bayesian handler ≠ BayesianTBR MCMC (INV-015).

---

## 10. Suitability candidate register

| combination_id | Class | Pending artifact |
|----------------|-------|------------------|
| SCM-JK | `suitability_candidate_pending_oc` | D5-STAT-SCM-JK-001 |
| TBR-AGG-POINT | `suitability_candidate_pending_oc` | D5-STAT-TBR-AGG-001 ✅ Level B |
| DID-BOOTSTRAP | `suitability_candidate_pending_oc` | D5-STAT-DID-BOOTSTRAP-001 ✅ Level B |
| MCELL-PERCELL-SCM-JK | `suitability_candidate_pending_oc` | D5-STAT-MCELL-PERCELL-001 ✅ Level B |

---

## 11. Diagnostic candidate register

| combination_id | Class | Notes |
|----------------|-------|-------|
| AUGSYNTH-POINT | `diagnostic_candidate_pending_oc` | G1–G8 acknowledged; not suitable yet |
| SCM-PLACEBO | `diagnostic_candidate_pending_oc` | Falsification only |
| AUGSYNTH-KFOLD | `diagnostic_candidate_pending_oc` | Diagnostic band |
| TBR-AGG-KFOLD | `diagnostic_candidate_pending_oc` | Aggregate only |
| TBRRIDGE-KFOLD / TSKFOLD / BRB / CONFORMAL | `diagnostic_candidate_pending_oc` | Identity separation + OC |

---

## 12. Blocked-before-suitability register

| combination_id | Class |
|----------------|-------|
| AUGSYNTH-CONFORMAL | `blocked_before_suitability` |
| TBR-UNIT-JK | `blocked_before_suitability` |
| TBRRIDGE-BAYESIAN-REG | `blocked_before_suitability` |
| TBRRIDGE-PLACEBO | `blocked_before_suitability` |

---

## 13. Bridge-required register

| combination_id | Bridge |
|----------------|--------|
| SUPERGEO-SCM-JK · SUPERGEO-AUGSYNTH-POINT | F-GEO-003 |
| TRIM-SCM-JK · TRIM-AUGSYNTH-POINT | F-GEO-004 |
| MCELL-POOLED-AUGSYNTH · MCELL-POOLED-SCM-JK | multicell causal pooling ADR |

---

## 14. Research-only register

| combination_id | Class |
|----------------|-------|
| TROP-RESEARCH | `research_only` — no advancement until TROP audit ladder complete ([`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md)) |
| MTGP-RESEARCH | `research_only` |
| BAYESIANTBR-MCMC | `research_only` |
| SDID-POINT | `research_only` |

---

## 15. Quarantine / deprecation register

Family-level quarantine (quickblock, matchedpair, legacy SCM) remains in Layer 3 — no combination-level product declaration in v1.

---

## 16. Required D5-STAT evidence queue

**Smoke callable artifact:** ✅ **`D5-STAT-SMOKE-CALLABLE-001`** — [`D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md).

**SCM+JK Level B:** ✅ **`D5-STAT-SCM-JK-001`** — [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md).

**AugSynth point Level B:** ✅ **`D5-STAT-AUGSYNTH-POINT-001`**.

**TBR aggregate point Level B:** ✅ **`D5-STAT-TBR-AGG-001`**.

**DID bootstrap Level B:** ✅ **`D5-STAT-DID-BOOTSTRAP-001`**.

**MCELL per-cell Level B:** ✅ **`D5-STAT-MCELL-PERCELL-001`**.

**Immediate next concrete artifact:** **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** (design-side).

Then (from Layer 5 matrix queue):

1. D5-STAT-SCM-JK-001 ✅  
2. D5-STAT-AUGSYNTH-POINT-001 ✅  
3. D5-STAT-TBR-AGG-001 ✅  
4. D5-STAT-DID-BOOTSTRAP-001 ✅  
5. D5-STAT-MCELL-PERCELL-001 ✅  
6. D5-STAT-TBRRIDGE-INF-001 ✅  
7. INFERENCE_READOUT_SEMANTICS_001 ✅  
8. GEOMETRY_BRIDGE_REQUIREMENTS_001 ✅  
9. DESIGN_OUTPUT_CONTRACT_001 ✅  
10. DESIGN_CODE_INVENTORY_001 ✅  
11. DESIGN_LITERATURE_ALIGNMENT_001 ✅  
12. DESIGN_IMPLEMENTATION_VALIDATION_001 ✅
13. DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 ✅
14. DESIGN_COMBINATION_VALIDATION_MATRIX_001 **(next)**

Blocked queue unchanged from Layer 5 (`d5_stat_blocked_queue` in JSON).

---

## 17. Future role-assignment prerequisites

Before any primary/secondary/directional label:

1. Layers 1–5 ✅  
2. Executed D5-STAT archives per combination scope  
3. Suitability claims supported by evidence  
4. **`TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001`** (not authored in this PR)  
5. Explicit program charter to resume TrustReport / F-DECISION integration  

---

## 18. What this artifact does not authorize

- TrustReport / F-DECISION role assignment  
- CalibrationSignal or MMM export  
- LLM product recommendations  
- Production promotion or eligibility changes  
- Claim that OC-ready = suitable  
- Claim that suitability candidate = suitable  

---

## 19. JSON schema

Each `rows[]` entry: `combination_id` · `source_matrix_status` · design/estimator/inference/geometry/estimand/effect_scale/interval_semantics · `suitability_class` · evidence minimums · `current_allowed_use` · `current_forbidden_use` · `next_action` · forbidden flags (all **false**).

Regenerate: `python -m panel_exp.validation.design_estimator_inference_suitability_framework_001`

---

## 20. Next artifact recommendation

**Do not** wire TrustReport or F-DECISION from this framework.

**Next concrete work:** execute **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** (statistical protocol defined — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md); suitability blocked until `D5-DES-STAT-*` execution).

**After OC evidence accumulates:** author **`TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001`** or targeted F-DECISION/TrustReport amendments — not before.

---

## 21. Guardrails

- No estimator/design/inference code changes  
- No OC execution in this PR  
- No promotion; all `promotion_allowed: false`  
- No TrustReport/F-DECISION **runtime** changes  
- No CalibrationSignal/MMM/LLM changes  
- No primary/secondary/directional labels  

---

## Stop condition

| Criterion | Status |
|-----------|--------|
| Layer 5 row coverage | ✅ 30/30 |
| Non-promotional classes only | ✅ |
| Forbidden flags false | ✅ |
| Smoke artifact D5-STAT-SMOKE-CALLABLE-001 | ✅ |
| Level B SCM+JK D5-STAT-SCM-JK-001 | ✅ |
| Level B AugSynth point D5-STAT-AUGSYNTH-POINT-001 | ✅ |
| Level B TBR aggregate D5-STAT-TBR-AGG-001 | ✅ |
| Level B DID bootstrap D5-STAT-DID-BOOTSTRAP-001 | ✅ |
| Level B MCELL per-cell D5-STAT-MCELL-PERCELL-001 | ✅ |
| Readout semantics controller | ✅ [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) |
| Geometry bridge controller | ✅ [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) |
| Design output contract = DESIGN_OUTPUT_CONTRACT_001 | ✅ |
| Design code inventory = DESIGN_CODE_INVENTORY_001 | ✅ |
| Design literature alignment = DESIGN_LITERATURE_ALIGNMENT_001 | ✅ |
| Design implementation validation = DESIGN_IMPLEMENTATION_VALIDATION_001 | ✅ |
| Design statistical validation protocol = DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 | ✅ |
| Design-side suitability = DESIGN_SUITABILITY_FRAMEWORK_001 | ✅ |
| Next artifact = DESIGN_CONTRACT_ENFORCEMENT_PLAN_001 | ✅ |
| JSON + tests | ✅ |

---

*DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001 v1.1.0 — Design-side suitability framework cross-linked; distinct layers; next = DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.*
