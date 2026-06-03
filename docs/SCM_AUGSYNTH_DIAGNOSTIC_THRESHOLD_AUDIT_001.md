# SCM-AUGSYNTH-DIAGNOSTIC-THRESHOLD-AUDIT-001

**Document ID:** SCM-AUGSYNTH-DIAGNOSTIC-THRESHOLD-AUDIT-001  
**Type:** Diagnostic threshold audit — **governance / research planning only**  
**Status:** **complete** (provisional thresholds; calibration OC not executed)  
**Date:** 2026-06-03  
**Verdict:** Define **provisional operational labels** for SCM/A26 and AugSynth/ASCM failure modes before any LLM-layer synthesis; **no promotion**, **no production behavior change**  
**Foundation lane:** P1 ([`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) §4)

**Primary inputs:** [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md) (validation PR) · [`track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json) (validation PR) · [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md)

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) · [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) §3.1

**Guardrails (reaffirmed):** Docs/research only. No estimator code, inference code, OC execution, promotion, CalibrationSignal expansion, MMM ingestion, TrustReport behavior change, F-DECISION behavior change, or LLM integration. Do not declare AugSynth primary. Do not demote SCM/A26.

---

## 1. Problem statement

SCM/A26 and AugSynth/ASCM produce **point effects**, **intervals**, and **comparator disagreement** that are already consumed by F-DECISION and optionally surfaced in TrustReport. An LLM decision layer would **summarize** these objects — it must not **infer validity** from a favorable point estimate alone.

| Failure mode | Why unlabeled summaries are unsafe |
|--------------|-------------------------------------|
| **Weak SCM pretreatment fit** | High pre-period RMSE does not automatically invalidate A26, but it **does** mean AugSynth may diverge materially; without a label, an LLM may treat SCM as “fine.” |
| **Donor hull / extrapolation** | ASCM-002 W3 shows AugSynth **did not** beat A26 MAE when outside hull — augmentation can **hurt** under extrapolation. |
| **Donor sparsity / weight concentration** | Sparse pools and Herfindahl spikes correlate with instability; ASCM-002 blocks some worlds at `min_donors=5`. |
| **Scale / path mismatch** | D5-AS-FIND-004 and ASCM-002 conflict metrics show **100% material point mismatch** vs A26 at null — comparing lifts without bridge is misleading. |
| **False confidence** | Large post-period lift with poor pre-fit and hull stress is a **governance downgrade**, not a success story. |
| **Method disagreement** | F-DECISION already defines `diagnostic_disagreement`; facet labels must exist **before** LLM smoothing. |
| **Interval contradiction** | Narrow JK/Conformal bands with poor pre-fit (or Conformal invalid sign) must not read as “precise truth.” |

**Net:** SCM/A26 and AugSynth/ASCM **cannot be safely summarized by an LLM** unless failure modes are **explicitly labeled** with stable vocabulary and threshold **categories** (block / caution / diagnostic-only / research-only / insufficient-evidence). This audit defines those labels **provisionally**; numeric cutoffs require **ASCM-003 calibration** (§7).

---

## 2. Diagnostics to threshold

Each diagnostic maps to a **measure**, **label candidate(s)**, and **threshold type** (§4). Numeric values in the **provisional** column are **hypothesis cutoffs** for calibration — **not product constants**.

### 2.1 SCM pretreatment RMSE / normalized prefit error

| Field | Definition |
|-------|------------|
| **Measure** | `scm_pre_rmse` — pre-period RMSE of SCM leg on treated unit (charter D1). Optional normalization: RMSE / pre-period treated outcome std (not yet archived). |
| **Provisional cutoffs** | `fit_good`: RMSE ≤ p25 of W1 strong-fit archive; `fit_weak`: between p25(W1) and p75(W3); `fit_failed`: ≥ p75(W3) **or** blocked SCM leg. |
| **Threshold type** | `fit_failed` → **hard block** for “SCM fit supports causal readout” narrative; `fit_weak` → **caution**; `fit_good` → **diagnostic-only** positive label (does not promote). |
| **ASCM-002 note** | W2 (weak, inside hull) median `scm_pre_rmse` **0.51** < W1 strong **0.81** — world labels **do not monotonically track RMSE** at n_mc=4. Thresholds **must not** be set from world IDs alone. |

### 2.2 AugSynth pretreatment RMSE

| Field | Definition |
|-------|------------|
| **Measure** | `augsynth_pre_rmse` — pre-period fit on augmented/residual path (D2). |
| **Provisional cutoffs** | Same band structure as SCM, evaluated **independently**; additionally flag when `augsynth_pre_rmse > scm_pre_rmse` after augmentation (augmentation **worsened** pre-fit). |
| **Threshold type** | Worsening → **caution** (`fit_weak` on AugSynth path); extreme values → **diagnostic-only** for AugSynth point claims. |

### 2.3 Fit improvement over SCM

| Field | Definition |
|-------|------------|
| **Measure** | `fit_improvement_rmse` = (SCM pre-RMSE − AugSynth pre-RMSE) / SCM pre-RMSE (D3); negative = augmentation hurt pre-fit. |
| **Provisional cutoffs** | `fit_improvement_material`: ≥ 0.15 relative improvement; `fit_improvement_marginal`: (0.05, 0.15); below 0.05 → **insufficient-evidence** for “AugSynth helps fit.” |
| **Threshold type** | Material improvement → **diagnostic-only** label enabling “challenge hypothesis” text, **not** promotion; negative → **caution** on AugSynth superiority claims. |
| **ASCM-002 note** | W2 median improvement **0.18**; W3 **0.43** but AugSynth **lost** MAE @ 8% — improvement alone **does not** predict effect recovery outside hull. |

### 2.4 Donor hull / extrapolation risk

| Field | Definition |
|-------|------------|
| **Measure** | `hull_min_donor_z_distance` — min z-scaled distance from treated pre-profile to donor profiles (D6). Lower distance → more hull-supported. |
| **Provisional cutoffs** | `donor_hull_supported`: distance ≤ p50(W1); `donor_hull_stressed`: between p50(W1) and p50(W3); `extrapolation_risk_high`: > p75(W3) **or** world tag `weak_fit_outside_hull`. |
| **Threshold type** | `extrapolation_risk_high` → **caution** + **`diagnostic_only_do_not_promote`** for AugSynth superiority; not a hard block on A26 null-monitor. |
| **ASCM-002 note** | W3 median distance **7.46** vs W2 **3.65** — directionally aligned with hull stress, but W1 **4.58** overlaps W2; distance alone is **noisy** at n_mc=4. |

### 2.5 Donor sparsity

| Field | Definition |
|-------|------------|
| **Measure** | `donor_sparsity_n_control` — count of donors meeting `min_donors` policy (D4). |
| **Provisional cutoffs** | `donor_pool_sparse`: n_control ≤ 6; `donor_pool_rich`: n_control ≥ 10; between → unlabeled or **insufficient-evidence**. |
| **Threshold type** | At `min_donors` floor with `blocked_reason=insufficient_donors_need_5` → **hard block** on comparator arms for that run; sparse but feasible → **caution**. |
| **ASCM-002 note** | W4/W8/W10 show partial blocks and NaN diagnostics — sparsity labels must attach **`insufficient_evidence`** when `diagnostics_feasible=0`. |

### 2.6 Weight concentration

| Field | Definition |
|-------|------------|
| **Measure** | `weight_herfindahl`, `max_weight` on SCM leg (D5); `n_negative_weights` (D7). |
| **Provisional cutoffs** | `weight_concentration_high`: Herfindahl ≥ 0.12 **or** max_weight ≥ 0.18; `negative_weights_present`: n_negative > 0. |
| **Threshold type** | High concentration → **caution**; negative weights → **caution** + **`extrapolation_risk_high`** (research label until estimand ADR). |

### 2.7 Treated / control scale mismatch

| Field | Definition |
|-------|------------|
| **Measure** | Ratio of treated vs donor-weighted control pre-period level std, or post-period path scale ratio (D10 partial — **not fully archived** in ASCM-002). |
| **Provisional cutoffs** | `scale_mismatch_material`: ratio outside [0.67, 1.5] on bridged scale. |
| **Threshold type** | **caution** on cross-method point compare; pairs with `method_disagreement_material`. |
| **ASCM-002 note** | **Missing** as standalone field; inferred only via `conflict_vs_a26.null_material_point_mismatch` (100% on sample). |

### 2.8 Outside-hull stress

| Field | Definition |
|-------|------------|
| **Measure** | Composite: `extrapolation_risk_high` **and** (`fit_weak` on SCM **or** `fit_improvement_material`). |
| **Provisional cutoffs** | Trigger **`diagnostic_only_do_not_promote`** on AugSynth-challenge narratives; A26 remains runnable. |
| **Threshold type** | **caution** + diagnostic-only; ASCM-002 W3 is canonical stress case. |

### 2.9 Null false-confidence flags

| Field | Definition |
|-------|------------|
| **Measure** | Charter D11: high \|point effect\| at null with `fit_weak` and/or hull stress. Field **`false_confidence_flag`** specified in charter — **not emitted** in ASCM-002 JSON. |
| **Provisional rule** | At null effect world: flag if \|point\| > null-materiality threshold **and** (`fit_weak` **or** `extrapolation_risk_high`). |
| **Threshold type** | **`false_confidence_risk`** → **caution**; must surface in TrustReport/LLM as **warning**, not hidden. |

### 2.10 Material disagreement between SCM and AugSynth

| Field | Definition |
|-------|------------|
| **Measure** | `conflict_vs_a26`: `null_sign_disagreement`, `null_material_point_mismatch`, effect-world sign mismatch (F-DECISION input). |
| **Provisional cutoffs** | `method_disagreement_material`: sign mismatch **or** material point mismatch rate > 0.5 on comparable runs. |
| **Threshold type** | **caution**; triggers F-DECISION `diagnostic_disagreement` posture when primary vs diagnostic — **no averaging**. |
| **ASCM-002 note** | Null sign disagreement **0%**; material point mismatch **100%** — scale bridge required before lift comparison labels. |

### 2.11 Interval contradiction / narrow interval with poor fit

| Field | Definition |
|-------|------------|
| **Measure** | JK/Conformal interval width vs `scm_pre_rmse` / hull labels; Conformal band sign validity (F-INF). |
| **Provisional cutoffs** | `interval_contradiction`: valid-looking narrow interval (width < effect magnitude proxy) **and** (`fit_weak` **or** `extrapolation_risk_high`); Conformal invalid sign → **`diagnostic_only_do_not_promote`**. |
| **Threshold type** | Conformal invalid → **hard block** on governed uncertainty (already F-INF); JK narrow + poor fit → **caution** (`false_confidence_risk`). |
| **ASCM-002 note** | Conformal remains unsafe (ADR-001); JK null FPR 0.0 on W2/W3 but **does not** prove fit quality. |

---

## 3. Evidence from ASCM-002

Source: [`D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json) on branch `validation/d5-inst-augsynth-ascm-002` (n_mc=4, 48 replicates, 12 worlds). Report: [`D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md).

### 3.1 Diagnostics available in archive

| Charter ID | JSON field | Status | Notes |
|------------|------------|--------|-------|
| D1 | `scm_pre_rmse` | **Available** | Feasible on most worlds; NaN when blocked |
| D2 | `augsynth_pre_rmse` | **Available** | Same caveats |
| D3 | `fit_improvement_rmse` | **Available** | Does not predict W3 MAE outcome |
| D4 | `donor_sparsity_n_control` | **Available** | Aligns with sparse-world design |
| D5 | `weight_herfindahl`, `max_weight` | **Available** | Partial NaN on blocked runs |
| D6 | `hull_min_donor_z_distance` | **Available** | Directionally useful; overlaps across worlds |
| D7 | `n_negative_weights` | **Available** | All 0 in sample — no stress test |
| D8 | Outcome-model sensitivity | **Missing** | Not in JSON |
| D9 | Placebo slice | **Missing** | Not in ASCM-002 harness |
| D10 | Scale bridge metrics | **Partial** | Only via `conflict_vs_a26` aggregate |
| D11 | `false_confidence_flag` | **Missing** | Charter required; harness gap |
| — | `diagnostics_feasible`, `blocked_reason` | **Available** | Required for insufficient-evidence labels |
| — | `conflict_vs_a26` | **Available** | Material mismatch 100% at null |
| — | Interval width / coverage | **Partial** | Arms present; Conformal unsafe per ADR |

### 3.2 Diagnostic reliability assessment

| Finding | Implication for thresholds |
|---------|---------------------------|
| Weak-fit world **W2** has **lower** SCM RMSE than strong-fit **W1** in sample | Pretreatment RMSE thresholds **cannot** be calibrated from DGP labels alone |
| W3 outside hull: high `fit_improvement_rmse` but AugSynth **does not** beat A26 MAE | Improvement thresholds must **not** auto-elevate AugSynth |
| W4/W8/W10: `insufficient_donors_need_5` blocks | Sparsity thresholds must gate **`insufficient_evidence`** |
| Null JK FPR 0.0 for A26 and AugSynth+JK on W2/W3 | Null FPR **does not** substitute for fit/hull labels |
| Conformal remains 100% null exclusion on characterized runs | Keep **hard block** on governed Conformal claims (ADR-001) |

### 3.3 Verdict on ASCM-002 sufficiency

ASCM-002 **validates that diagnostics can be archived** and **invalidates naive promotion heuristics** (fit improvement ≠ effect win outside hull). It is **insufficient** to set production numeric cutoffs: n_mc=4, missing D8/D9/D11, no normalized RMSE, no interval-contradiction field, no scale-bridge scalar.

---

## 4. Threshold types

| Type | Meaning | Platform behavior (future) | Examples in this audit |
|------|---------|----------------------------|------------------------|
| **Hard block threshold** | Label prevents a **decision-grade claim** for that facet | F-DECISION / TrustReport must not emit proceed posture on blocked facet | Conformal governed export; run blocked at donor floor; `fit_failed` for “SCM fit supports readout” |
| **Caution threshold** | Label forces **warning posture**; methods may still run | TrustReport `diagnostic_disagreement` / caveat strings; LLM must use cautionary language | `fit_weak`, `extrapolation_risk_high`, `method_disagreement_material`, `false_confidence_risk` |
| **Diagnostic-only label** | Informational facet for comparator panel | Visible; **no role upgrade** | `fit_good`, `donor_hull_supported`, material fit improvement |
| **Research-only label** | OC / charter context only | Must not appear as product decision text | Negative-weight extrapolation policy pending ADR |
| **Insufficient-evidence label** | Metric missing, blocked, or n too small | Suppress threshold conclusion; surface “not computed” | NaN diagnostics, D8/D11 absent, n_mc=4 calibration |

**Composition rule:** Multiple labels may apply. **Hard block** on one facet does not demote A26 globally. **Caution** labels **accumulate**; LLM must not net them into a single “confidence score.”

---

## 5. Label vocabulary

Stable labels for Track B metadata, future TrustReport facets, and LLM contracts:

| Label | Definition | Typical threshold type |
|-------|------------|------------------------|
| `fit_good` | SCM pre-RMSE in strong-fit band (provisional) | diagnostic-only |
| `fit_weak` | SCM pre-RMSE in weak band or augmentation worsened pre-fit | caution |
| `fit_failed` | SCM pre-RMSE extreme or SCM leg blocked | hard block (narrative facet) |
| `donor_hull_supported` | Hull distance in supported band | diagnostic-only |
| `donor_hull_stressed` | Hull distance intermediate | caution |
| `extrapolation_risk_high` | Hull distance high or outside-hull world stress | caution |
| `donor_pool_sparse` | n_control at or near min_donors | caution |
| `weight_concentration_high` | Herfindahl or max_weight elevated | caution |
| `scale_mismatch_material` | Treated/control scale ratio out of band (when computed) | caution |
| `method_disagreement_material` | Sign or material point mismatch vs A26 | caution |
| `false_confidence_risk` | Large effect with weak fit / hull stress (D11 rule) | caution |
| `interval_contradiction` | Narrow interval with poor fit or invalid Conformal | caution / hard block (Conformal) |
| `diagnostic_only_do_not_promote` | Composite downgrade for AugSynth-challenge claims under stress | caution |
| `insufficient_evidence` | Diagnostic missing, blocked, or uncalibrated cutoff | insufficient-evidence |
| `research_only` | Pending estimand ADR (e.g. negative weights) | research-only |

**Label emission (future):** One primary **fit** label, one **hull** label, zero or more **caution** flags, optional **`insufficient_evidence`** per missing diagnostic.

---

## 6. TrustReport / LLM implications

**No behavior change in this audit.** When labels are wired (post AS CM-003 + implementation ADR):

| Rule | Requirement |
|------|-------------|
| **LLM may summarize labels** | Text may restate `fit_weak`, `extrapolation_risk_high`, etc., from structured facets |
| **LLM may not infer validity from point estimates** | A positive AugSynth point with `fit_weak` + `extrapolation_risk_high` must **not** be narrated as “AugSynth confirms lift” |
| **Weak-fit evidence is cautionary** | `fit_weak` / `fit_failed` require explicit caveat even when A26 null-monitor runs |
| **Disagreement must be surfaced** | `method_disagreement_material` → cite both readouts; **no averaging** (aligns with F-DECISION § evidence comparison) |
| **A26 baseline unchanged** | Labels do not demote `primary_null_monitor`; AugSynth remains `diagnostic_comparator` |
| **Conformal / Kfold roles** | Per ADR-001: Conformal not governed; Kfold diagnostic-only — labels must not upgrade inference role |
| **CalibrationSignal** | Unaffected — **A26 only** |

**TrustReport `f_decision_context`:** May eventually include a **`diagnostic_labels`** array mirroring this vocabulary — **separate PR**, blocked until ASCM-003 calibration and implementation charter.

---

## 7. Next OC needs — ASCM-003

**Recommendation:** **Yes — ASCM-003 is needed** to calibrate provisional cutoffs before product-stable thresholds or LLM contracts.

| ASCM-003 design element | Purpose |
|-------------------------|---------|
| **Larger n_mc** | ≥ 14 per world (charter §7.1); target 24+ for percentile stability |
| **Grid over weak-fit severity** | Continuous SCM RMSE stress, not binary world IDs |
| **Inside vs outside hull** | Joint distribution of RMSE, hull distance, and MAE @ 8% |
| **Sparse vs rich donor pool** | Calibrate `donor_pool_sparse` / block rates at min_donors |
| **Outlier / noise / shock variants** | W8–W10 had NaN/block rates — need clean feasibility accounting |
| **Null / effect worlds** | Calibrate D11 `false_confidence_flag`; interval contradiction rates |
| **Emit missing diagnostics** | D8 sensitivity, D10 scale ratio, D11 boolean, interval width fields |
| **Label calibration table** | Map cutoffs → label precision/recall vs OC ground-truth failure modes |

**Stop condition for ASCM-003:** Published threshold calibration table with confidence bands; revision of §2 provisional cutoffs; gap closure for GAP-SCM-DIAG-001 / GAP-ASCM-HULL-001 in foundation doc.

**Guardrails unchanged:** Research OC only; no promotion; no F-DECISION/TrustReport code change in same PR as OC.

---

## 8. Final disposition

| Item | Disposition |
|------|-------------|
| **Thresholds** | **Provisional** — §2 cutoffs are hypotheses for ASCM-003, not product constants |
| **Method promotion** | **None** — AugSynth remains diagnostic comparator; A26 unchanged |
| **F-DECISION change** | **None** — existing disagreement policy applies; labels are future inputs |
| **TrustReport behavior** | **None** — §6 is forward-looking only |
| **CalibrationSignal** | **No expansion** |
| **LLM layer** | **Still paused** — L3 criterion in METHOD-FOUNDATION-HARDENING §6 partially addressed by vocabulary; numeric calibration still open |
| **ASCM-003** | **Likely required** before stable cutoffs (§7) |
| **Gap closure** | GAP-SCM-DIAG-001, GAP-ASCM-HULL-001, GAP-HULL-001 → **documented, calibration pending** |

**Stop condition (this audit):** Repo contains provisional SCM/AugSynth failure-mode labels, threshold categories, ASCM-002 evidence table, and ASCM-003 calibration charter — **met**.

---

*SCM-AUGSYNTH-DIAGNOSTIC-THRESHOLD-AUDIT-001 v1.0.0 — planning only; numeric calibration via D5-INST-AUGSYNTH-ASCM-003 (future).*
