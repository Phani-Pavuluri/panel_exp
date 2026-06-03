# AUGSYNTH-ASCM-INFERENCE-PAIRING-ADR-001

**Document ID:** AUGSYNTH-ASCM-INFERENCE-PAIRING-ADR-001  
**Type:** Architecture / governance decision record — **inference pairing policy**  
**Status:** **accepted**  
**Date:** 2026-06-03  
**Verdict:** **No AugSynth/ASCM inference pairing is promoted today.** A26 (SCM+UnitJackKnife) remains the governed null-monitor baseline.  
**Upstream:** [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)  
**Matrix / policy:** [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md)

**Related OC:** [`D5_INST_AUGSYNTH_001_REPORT.md`](track_d/D5_INST_AUGSYNTH_001_REPORT.md) · [`D5_INST_AUGSYNTH_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_003_REPORT.md) · [`D5_INST_AUGSYNTH_KFOLD_001_REPORT.md`](track_d/D5_INST_AUGSYNTH_KFOLD_001_REPORT.md)

---

## 1. Decision summary

| Decision | Status |
|----------|--------|
| **Promote any AugSynth/ASCM inference pairing** | **No** — all pairings remain diagnostic, restricted, or falsification-only |
| **Change A26 / SCM+UnitJackKnife baseline** | **No** |
| **Declare AugSynth primary null-monitor or effect readout** | **No** |
| **Expand CalibrationSignal allowlist** | **No** — **A26 only** (E5) |
| **Add governed-uncertainty allowlist entries** | **No** — F-INF governed set remains **empty** for AugSynth arms |
| **Change TrustReport or F-DECISION production behavior** | **No** — this ADR records policy only |
| **Select a primary AugSynth inference layer** | **No** — no single pairing is nomination-ready |

**Net:** After D5-INST-AUGSYNTH-ASCM-002, AugSynth/ASCM stays a **diagnostic comparator family**. **AugSynth+UnitJackKnife** is the only pairing with a **credible future promotion-audit research track** (null FPR conservative; estimand bridge still open). **Conformal** is **restricted / not governed uncertainty**. **KFold** is **robustness diagnostic only**. **Placebo** applies to **SCM falsification**, not AugSynth-primary inference.

---

## 2. Pairing evaluation

Classification uses matrix rows **A01–A05**, benchmark **A26**, and F-DECISION roles. “Promotion-audit eligible” means **may enter scoping** for [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md) — **not** approved today.

### 2.1 AugSynthCVXPY point (A01)

| Field | Disposition |
|-------|-------------|
| **Matrix row** | A01 (point) |
| **Current status** | `diagnostic_comparator` — **`characterized_restricted`** / diagnostic strengthen |
| **Uncertainty source** | None (point-only) |
| **Geometry support** | Unit-panel single-cell (F-GEO-001); multi-treated per-unit where harness supports; no pooled multi-cell |
| **Interval semantics** | N/A |
| **Null FPR evidence** | N/A (no interval); material **point scale/path disagreement** vs A26 at null (D5-001, ASCM-002) |
| **Coverage / power** | Not applicable; directional recovery partial on weak-fit worlds (ASCM-002: **1/2** MAE beat @ 8%) |
| **Failure modes** | Scale bridge vs SCM+JK; over-extrapolation when outside donor hull (W3: **no** MAE beat) |
| **Additional OC required** | Outside-hull worlds with larger `n_mc`; estimand bridge ADR before any null-monitor swap |
| **TrustReport role** | **`diagnostic_comparator`** (existing F-DECISION comparator panel) — unchanged |
| **CalibrationSignal** | **Neither** — not eligible |
| **Promotion-audit eligible** | **No** — point-only cannot support null-monitor promotion without paired inference ADR |

### 2.2 AugSynthCVXPY + UnitJackKnife (A02 / A03 JK path)

| Field | Disposition |
|-------|-------------|
| **Matrix row** | A01–A03 (JK characterized) |
| **Current status** | `diagnostic_comparator` — **not** SCM JK estimand; conservative null-monitor **style** on batteries |
| **Uncertainty source** | Donor leave-one-out on **augmented** counterfactual path (not identical to A26 donor LOO on SCM leg) |
| **Geometry support** | Same as point; aggregate JK **invalid** |
| **Interval semantics** | F-INF: JK path CI on augmented readout — **`diagnostic_interval_only`**; not governed uncertainty |
| **Null FPR evidence** | D5-001 / KFOLD-003 context: **0%** on 001e-style battery; **ASCM-002 weak-fit worlds W2/W3: 0.0** for both A26 and AugSynth+JK |
| **Coverage / power** | Under-investigated on weak-fit **coverage**; null FPR conservative on available slices |
| **Failure modes** | Estimand mismatch vs A26 JK; treating as lift detector; spillover DGP bias (CV-EST-AUGSYNTH) |
| **Additional OC required** | **Yes (P1)** — targeted JK battery: outside-hull emphasis, `n_mc` ≥ 14, estimand bridge doc, weak-fit stratification |
| **TrustReport role** | **`diagnostic_comparator`** — optional visibility; no upgrade |
| **CalibrationSignal** | **Neither** |
| **Promotion-audit eligible** | **Research candidate only** — **not eligible today**; requires stable weak-fit recovery **and** closed estimand bridge **and** §5 rules |

### 2.3 AugSynthCVXPY + Conformal (A05)

| Field | Disposition |
|-------|-------------|
| **Matrix row** | A05 |
| **Current status** | `characterized_restricted` — **`callable_unverified_interval_semantics`** (D5-003; ASCM-002 confirms) |
| **Uncertainty source** | Pre-period absolute residual calibration vs treated-period residual (rank / conformal score) |
| **Geometry support** | Unit-panel single-cell; per-cell k=2 in D5-003 only |
| **Interval semantics** | `conformal_interval`; **invalid band sign** (negative half-width) on batteries; F-INF **blocks governed export** |
| **Null FPR evidence** | D5-003: **100%** null interval-exclusion FPR on feasible runs; ASCM-002: remains **unsafe** across worlds |
| **Coverage / power** | Not trustworthy for null monitoring; always excludes zero at null on characterized runs |
| **Failure modes** | Exchangeability failure; orientation/sign; disagreement ~100% vs JK/Kfold at null |
| **Additional OC required** | **Only if** band semantics fixed in code — otherwise **no further promotion-oriented OC** |
| **TrustReport role** | **`diagnostic_comparator`** band (if exported) — **not** null-monitor |
| **CalibrationSignal** | **Neither** — explicitly blocked |
| **Promotion-audit eligible** | **No** — **keep_restricted** / not governed uncertainty |

### 2.4 AugSynthCVXPY + KFold (A03 Kfold path)

| Field | Disposition |
|-------|-------------|
| **Matrix row** | A01–A03 |
| **Current status** | `characterized_restricted` — **`remain_restricted_diagnostic_comparator`** (D5-KFOLD-001) |
| **Uncertainty source** | Time-series / panel K-fold CV on augmented path |
| **Geometry support** | Unit-panel; not aggregate |
| **Interval semantics** | `confidence_interval` — **diagnostic only**; not governed |
| **Null FPR evidence** | D5-KFOLD-001 / D5-003 context: **0%** on 001e battery; ASCM-002: diagnostic arm, not primary |
| **Coverage / power** | Robustness / triangulation; not validated as null-monitor substitute |
| **Failure modes** | Fold policy sensitivity; scale mismatch vs A26 |
| **Additional OC required** | Optional fold-policy sensitivity — **low priority** vs JK outside-hull OC |
| **TrustReport role** | **`diagnostic_comparator`** — robustness panel |
| **CalibrationSignal** | **Neither** |
| **Promotion-audit eligible** | **No** |

### 2.5 AugSynthCVXPY + Placebo / falsification

| Field | Disposition |
|-------|-------------|
| **Matrix row** | A27 pattern (Placebo on **SCM** estimator space); combo audit lists probe — **explicit block** for AugSynth+Placebo as primary |
| **Current status** | **Falsification-only** — not an AugSynth inference pairing for promotion |
| **Uncertainty source** | Placebo reallocation on SCM donor space (A27) |
| **Geometry support** | Single-treated unit panel where placebo geometry valid; **multi-treated blocked** (A28) |
| **Interval semantics** | Falsification check — not lift evidence |
| **Null FPR evidence** | N/A for AugSynth-primary role |
| **Coverage / power** | N/A |
| **Failure modes** | Mis-labeling placebo as AugSynth uncertainty |
| **Additional OC required** | F-P0-005 placebo taxonomy — **orthogonal** to AugSynth promotion |
| **TrustReport role** | **`falsification_check`** (SCM placebo) — not AugSynth pairing |
| **CalibrationSignal** | **Neither** |
| **Promotion-audit eligible** | **No** |

### 2.6 Summary table

| Pairing | Tuple | Current status | Promotion-audit eligible today | Next step |
|---------|-------|----------------|----------------------------------|-----------|
| **Point** | A01 | diagnostic comparator | **No** | Maintain; outside-hull OC |
| **+ UnitJackKnife** | A02/A03 | diagnostic comparator | **Research candidate only** | **P1** follow-up OC + estimand ADR |
| **+ Conformal** | A05 | restricted / unverified semantics | **No** | **keep_restricted** |
| **+ KFold** | A03 | restricted diagnostic | **No** | Optional sensitivity OC |
| **+ Placebo** | — | falsification (SCM) | **No** | F-P0-005 only |
| **A26 baseline** | A26 | `primary_null_monitor` | N/A (baseline) | Maintain |

---

## 3. Interpretation of D5-INST-AUGSYNTH-ASCM-002

| ASCM-002 finding | Inference pairing implication |
|------------------|------------------------------|
| **Overall `remain_diagnostic_comparator`** | No pairing earns role upgrade |
| **Weak-fit recovery partial (1/2 @ 8% MAE)** | Point path alone **insufficient**; does not justify primary readout |
| **W2 inside hull: AugSynth MAE beats A26** | Supports **continued research** on JK + point under weak-fit **inside** hull |
| **W3 outside hull: AugSynth does not beat A26** | **Do not** promote AugSynth for extrapolation-heavy cases without new diagnostics + OC |
| **A26 & AugSynth+JK null FPR 0.0 on W2/W3** | JK pairing **safe on null FPR** in this battery — **necessary but not sufficient** for promotion |
| **Conformal unsafe (prior + ASCM-002 arms)** | **Disqualifies** Conformal from null-monitor or governed-uncertainty candidacy |
| **KFold 0% null FPR in prior batteries** | Remains **diagnostic robustness** only — not primary inference |
| **No primary inference chosen** | Correct — this ADR **does not** select a winner |

**Track E (INST-004):** Remains **`diagnostic_only`** for point and JK; Conformal/Kfold **restricted** comparators — consistent with this ADR.

---

## 4. Next OC needs (recommended follow-up)

**Artifact ID (proposed):** `D5-INST-AUGSYNTH-ASCM-003` — **not authorized in this ADR**; research lane only if product pulls.

| Priority | Battery extension | Rationale |
|----------|-------------------|-----------|
| **P1** | **Larger `n_mc`** (≥ 14) on W2–W3 weak-fit / hull worlds | ASCM-002 used `n_mc=4`; stabilize MAE and FPR estimates |
| **P1** | **Stronger outside-hull worlds** | W3 failed to beat A26 — need dedicated DGP stress, not only noise/correlation tweaks |
| **P1** | **JK-specific null coverage** | Report cell-level and mean coverage where intervals exist; separate from exclusion FPR |
| **P2** | **Regularization / outcome-model sensitivity grid** | Charter §4 I8; ridge λ sweep on weak-fit slices |
| **P2** | **Placebo / falsification slice** | SCM-space placebo alongside AugSynth point — conflict policy input, not AugSynth inference |
| **P3** | **Multi-treated / per-cell extension** | W11 feasibility only; no pooled claims |

**Not recommended:** Additional Conformal promotion OC until interval semantics are fixed in implementation (separate F-INF track — **out of scope** for this ADR).

---

## 5. Decision rules — promotion audit gate

Before **any** AugSynth pairing enters [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md):

| # | Requirement | ASCM-002 / ADR status |
|---|-------------|------------------------|
| R1 | **Stable effect recovery improvement** over A26 in **targeted** weak-fit worlds (not global) | ❌ Partial (1/2) |
| R2 | **No unsafe null FPR** on nominated inference arm vs A26 on same worlds | ✅ JK arms on W2/W3 (battery-limited) |
| R3 | **Clear interval semantics** (F-INF classification + orientation) | ❌ Conformal fails; JK diagnostic only |
| R4 | **Clear failure diagnostics** (hull, pre-RMSE, false-confidence flags) archived | ⚠️ Partial in ASCM-002 JSON |
| R5 | **TrustReport disagreement policy** documented (no silent averaging) | ⚠️ Proposal only — F-DECISION conflict compare exists for baseline |
| R6 | **No unresolved estimand / geometry mismatch** | ❌ Scale bridge vs A26 open (D5-AS-FIND-004) |
| R7 | **Explicit F-DECISION amendment path** + AUDIT-010 row + E5 if CS ever scoped | ❌ Not initiated |
| R8 | **Implementation fidelity** closed (charter §4) | ⚠️ Partial |

**Minimum bar for opening promotion audit (JK supplement hypothesis):** R1 **and** R6 closed on weak-fit **inside-hull** slice **and** R2 replicated at `n_mc` ≥ 14 **and** inference semantics ADR **accepted** (this document) **and** separate **estimand bridge ADR**.

---

## 6. Final disposition (accepted)

| Pairing | Disposition | F-DECISION / TrustReport (unchanged) |
|---------|-------------|--------------------------------------|
| **AugSynthCVXPY point** | **`diagnostic_comparator`** | Comparator panel; not primary |
| **AugSynthCVXPY + UnitJackKnife** | **`diagnostic_comparator`** — **candidate for more OC**, **not promoted** | No null-monitor upgrade |
| **AugSynthCVXPY + Conformal** | **`keep_restricted`** — **not governed uncertainty** | Diagnostic band only if exported |
| **AugSynthCVXPY + KFold** | **`diagnostic_comparator`** — robustness only | No promotion path |
| **AugSynthCVXPY + Placebo** | **Not supported** as AugSynth pairing — **SCM falsification only** | A27 pattern |
| **A26 SCM+UnitJackKnife** | **`primary_null_monitor`** — baseline maintained | **Not demoted** |

**Exit from strengthening lane (inference leg):** `remain_diagnostic_comparator` with optional **`proceed_to_OC`** (ASCM-003) for JK + outside-hull — **not** `proceed_to_promotion_audit`.

---

## 7. Consequences

| System | Change |
|--------|--------|
| Production estimator / inference code | **None** |
| F-DECISION-001 allowlists | **None** |
| TrustReport / `f_decision_context` | **None** |
| CalibrationSignal E5 | **None** |
| Governed uncertainty allowlist | **None** |
| METHOD-READINESS matrix | **No row upgrade** — cite this ADR in next matrix refresh |
| Promotion pipeline | JK pairing may receive **future** promotion **audit scoping** only after §5 satisfied |

---

## 8. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| No pairing promoted | ✅ §1 |
| Per-pairing evaluation | ✅ §2 |
| ASCM-002 interpreted | ✅ §3 |
| Next OC needs defined | ✅ §4 |
| Promotion audit rules | ✅ §5 |
| Final disposition | ✅ §6 |
| No production / CS / MMM / TrustReport / F-DECISION change | ✅ §7 |

---

*AUGSYNTH-ASCM-INFERENCE-PAIRING-ADR-001 v1.0.0 — accepted; research/governance only.*
