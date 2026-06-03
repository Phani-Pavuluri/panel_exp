# AUGSYNTH-ASCM-STRENGTHENING-001

**Document ID:** AUGSYNTH-ASCM-STRENGTHENING-001  
**Type:** Method-strengthening charter / audit plan — **governance & research only**  
**Status:** **complete** (charter); **OC executed** — [`D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)  
**Date:** 2026-06-03  
**Verdict:** First concrete lane to test whether AugSynth/ASCM should **challenge** A26 (SCM+UnitJackKnife) on unit-panel geo — **no promotion, no role change**  
**Framework lane:** LANE-ASCM-001 ([`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) §8)  
**Parent lane registry:** [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) §3.1

**Related:** [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) (`CV-EST-AUGSYNTH`) · [`track_d/D5_INST_AUGSYNTH_001_REPORT.md`](track_d/D5_INST_AUGSYNTH_001_REPORT.md) · [`track_d/D5_INST_AUGSYNTH_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_003_REPORT.md) · [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md) (future gate)

**Baseline (unchanged):** **A26** — SCM + UnitJackKnife, `primary_null_monitor`, `ready_limited_governed_use`, CalibrationSignal `null_monitor_only` only.

---

## 1. Problem statement

| Fact | Implication |
|------|-------------|
| **SCM** is transparent, well-characterized on 001e-style batteries, and **currently governed** as the conservative null-monitor path (A26). | SCM remains the **baseline for benchmark and F-DECISION** until a promotion audit passes. |
| SCM can be **biased or unstable** when pretreatment fit is poor, donors are sparse, or treated markets sit **outside the donor convex hull** (extrapolation). | Product and literature both motivate an **augmented** estimator when SCM weights are extreme or pre-period RMSE is high. |
| **AugSynthCVXPY** implements an ASCM-style path: inner SCM + outcome-model correction on residuals (Ben-Michael et al.), improving effect recovery in some competitor and Phase 14 settings. | AugSynth is the **strongest literature-aligned challenger** to SCM on **unit-panel geo**, not a replacement today. |
| Prior D5 work shows AugSynth is **feasible** and useful as a **diagnostic comparator** (point, JK, Kfold, Conformal) with **material scale/path disagreement** vs SCM+JK at null. | Strengthening must **quantify when** disagreement helps vs hurts — especially under **weak SCM fit**. |
| **This artifact does not promote AugSynth**, expand CalibrationSignal, ingest MMM, or change TrustReport / F-DECISION behavior. | Output is a **charter + audit checklist + OC specification** for follow-on execution. |

**Scientific question:** Under which unit-panel geo conditions should AugSynth/ASCM **challenge** SCM as the primary effect readout or null-monitor supplement — and with which inference layer?

---

## 2. Scope

### 2.1 In scope (phase 1)

| Geometry / design | Notes |
|-------------------|--------|
| **Single treated, unit panel** (`single_cell`, 001e windows) | Primary OC world set; aligns with D5-INST-AUGSYNTH-001/003/KFOLD. |
| **Multi-treated unit panel** | Include **only where** F-GEO and existing harness already support (per-unit paths; no pooled claim). |
| **Multi-cell k=2, per-cell** | **Future extension** within this charter — donor-floor failures documented (D5-INST-AUGSYNTH-001); no pooled AugSynth estimand. |

**Estimator surface:** `AugSynthCVXPY` only (registry / Track B `AugSynthCVXPY_Point`). Base `AugSynth` (non-CVXPY) remains **probe-only** per F-CAT-003 and D5-INST-AUGSYNTH-001.

**Data structures:** Unit-panel geo experiments per **F-GEO-001**; instruments per **F-CAT-001** / AUDIT-010 Appendix A rows **A01–A05**, **A26** (benchmark).

### 2.2 Explicit exclusions

| Excluded | Rationale |
|----------|-----------|
| Pooled multi-cell claims | F-MCELL-001 ADR required; separate MULTICELL strengthening lane. |
| Trim / supergeo | TRIM_SUPERGEO strengthening lane; flat SCM tensor blocked. |
| MMM ingress | AUDIT-010 `not_ready_continue_track_f`. |
| CalibrationSignal expansion | E5 policy: **A26 only** until explicit promotion audit. |
| Declaring AugSynth **primary** or demoting SCM | Role change only via METHOD-PROMOTION-AUDIT-TEMPLATE-001 + F-DECISION amendment. |
| `AugSynthCVXPY + BRB` (A04) | F-CAT-002 block ADR — out of phase 1. |

---

## 3. Literature / conceptual alignment checklist

**Deliverable type:** `literature_fidelity_audit` (can cite this section + [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) §5.2 `CV-EST-AUGSYNTH`).

| # | Topic | Required alignment | Pass / gap (current) |
|---|--------|-------------------|----------------------|
| L1 | **Target estimand** | Augmented SCM **ATT** on treated unit path (relative effect family aligned with SCM); document spillover sensitivity. | **Partial** — same path family as SCM; spillover DGP bias documented (~−0.034 vs 0.10 truth in Phase 14). |
| L2 | **SCM baseline assumptions** | Convex combination of donors, pre-period fit, no extrapolation without risk flag. | **Aligned** — inner `SyntheticControlCVXPY`; inherits `full_model` risk. |
| L3 | **ASCM improvement mechanism** | SCM leg + **ridge (or declared) outcome model** on residualized outcomes; bias correction when SCM underfits. | **Aligned with deviation** — restricted on contaminated geo DGPs. |
| L4 | **Outcome-model dependence** | Report ridge λ / model spec; sensitivity to outcome-model misspecification. | **Gap** — sensitivity suite not standardized in D5. |
| L5 | **Extrapolation / negative-weight risk** | Policy when weights outside [0,1] or outside donor hull; regularization interpretation. | **Gap** — needs explicit diagnostic thresholds (§5). |
| L6 | **Donor convex-hull diagnostics** | Distance of treated pre-treatment profile to donor hull; flag extrapolation. | **Gap** — not in archived D5 JSON. |
| L7 | **Weak pretreatment fit trigger** | Operational definition (e.g. SCM pre-RMSE percentile, max weight, LEEF imbalance) triggering “ASCM challenge mode.” | **Gap** — **primary strengthening deliverable** for OC stratification. |
| L8 | **GeoLift / industry practice** | Position vs GeoLift-style ASCM and competitor dashboards (F-BACKLOG-002 rank 3–7). | **Aligned** — investigation priority high; governance blocks auto-promotion. |

**Forbidden claims (reaffirm):** CalibrationSignal eligibility; JK as **lift detector**; Conformal as governed uncertainty; pooled multi-cell AugSynth; equivalence of AugSynth point scale to SCM+JK without bridge.

---

## 4. Implementation fidelity checklist

**Deliverable type:** `implementation_fidelity_audit` (code refs in `panel_exp/methods/scm.py`, `CV-EST-AUGSYNTH`).

| # | Component | Audit question | Evidence / note |
|---|-----------|----------------|-----------------|
| I1 | **Objective / loss** | Inner SCM CVXPY objective matches documented SCM leg; ridge loss on residuals documented. | Inner `SyntheticControlCVXPY`; probe matches CVXPY point (D5-INST-AUGSYNTH-001). |
| I2 | **Constraints** | Donor weights, `min_donors`, correlation filter — match catalog. | `min_donors=5` on batteries; thin-cell blocks recorded. |
| I3 | **Regularization** | Ridge (or stated) penalty on outcome model; defaults recorded. | Conceptual audit §5.2; **sensitivity grid not archived**. |
| I4 | **Donor weights** | Export weight vector / concentration metrics for OC JSON. | **Gap** for strengthening OC artifact. |
| I5 | **Outcome-model component** | Fit on residualized Y; post-period counterfactual path. | Implemented; **metadata emission incomplete** for TrustReport (no wiring change in this charter). |
| I6 | **Treated/control geometry** | Unit panel only; reject aggregate JK on AugSynth path. | F-GEO aligned; aggregate JK **invalid**. |
| I7 | **Point estimand** | `AugSynthCVXPY_Point` Track B alias; scale documented vs SCM. | 100% material point mismatch vs SCM+JK @ null on 001e battery (D5-AS-FIND-004). |
| I8 | **Metadata emitted** | Pre-fit RMSE, weights, augmentation flags, failure codes. | **Partial** — strengthen OC harness to archive. |
| I9 | **Unsupported modes** | `full_model=True`, registry Bayesian on AugSynth, BRB (A04), base AugSynth prod. | **Blocked** per F-CAT / AUDIT-010. |

**Verdict:** Implementation is **faithful enough for diagnostic OC** but **not audit-complete** for promotion — fidelity audit must close I4–I8 before promotion audit.

---

## 5. Diagnostics required before OC

Diagnostics below must be **defined, computed, and archived** in the strengthening OC JSON (`D5-INST-AUGSYNTH-ASCM-002` — §7) **before** interpreting effect-recovery winners.

| ID | Diagnostic | Definition (operational) | Used for |
|----|------------|--------------------------|----------|
| D1 | **SCM pretreatment fit quality** | Pre-period RMSE (or catalog metric) of SCM leg on treated unit. | Stratify **weak vs strong** SCM fit worlds. |
| D2 | **AugSynth pretreatment fit quality** | Same window on augmented path / residual fit. | Show augmentation value. |
| D3 | **Improvement over SCM** | Δ pre-fit RMSE or post-period path MSE vs SCM-only. | Trigger for “challenge SCM” hypothesis. |
| D4 | **Donor sparsity** | Count of donors ≥ `min_donors`; effective N. | Sparse vs rich pool worlds. |
| D5 | **Weight concentration** | Herfindahl / max weight on SCM leg. | Extrapolation risk. |
| D6 | **Hull / extrapolation flag** | Treated pre-profile distance to donor convex hull (or weight outside [0,1] policy). | Outside-hull world label. |
| D7 | **Negative / extrapolation weight policy** | Document whether negative weights allowed; if so, flag runs. | Governance ADR input (`estimand_ADR`). |
| D8 | **Outcome-model sensitivity** | ± ridge λ or alternate outcome spec (small grid). | Robustness of augmentation. |
| D9 | **Placebo / falsification** | SCM-space placebo where geometry allows (A27 pattern); not AugSynth-primary placebo. | Falsification slice only. |
| D10 | **Scale compatibility** | Explicit bridge: relative ATT vs level path; sign agreement rate vs A26. | Forbid silent lift compare (D5-AS-FIND-004). |
| D11 | **False confidence / over-extrapolation** | High point effect + poor pre-fit + hull flag. | Downgrade to diagnostic-only. |

---

## 6. Candidate inference pairings

**Do not select a primary inference in this charter.** Define evidence required to nominate a pairing for promotion audit.

| Tuple | AUDIT-010 / matrix | Current disposition | Evidence required to nominate |
|-------|-------------------|---------------------|------------------------------|
| **A26** (benchmark) | SCM + UnitJackKnife | `ready_limited_governed_use` | Maintain as benchmark; not re-litigated here. |
| **A05** | AugSynthCVXPY + Conformal | `characterized_restricted` | **P1** — POSTFIX callable; **100% null interval-exclusion FPR** and invalid band sign on 003 battery → **not governed uncertainty**. Need: weak-fit worlds where **bands are diagnostically useful** OR reject for primary role. |
| **A01–A03** | AugSynth + point / JK / Kfold | `diagnostic_comparator` / strengthen | **P2** — JK: 0% null FPR on 001e but **not SCM JK estimand**; Kfold: restricted diagnostic (KFOLD-001). Need: **estimand bridge ADR** before any null-monitor swap. |
| **AugSynth + UnitJackKnife** | Characterized in D5-001; not registry-primary | Diagnostic | JK LOO on **augmented** path — clarify uncertainty source vs donor LOO on SCM. |
| **AugSynth + Placebo** | A27 / combo audit | Placebo on **SCM** space; not AugSynth estimator | **Falsification only** — cannot support AugSynth primary. |
| **A04** AugSynth + BRB | `blocked` | F-CAT-002 | **Out of scope** phase 1. |
| **Registry Bayesian** | INV-015 blocked | — | **Unsupported**. |

**Inference pairing ADR** (`inference_semantics_ADR`) must answer:

1. What randomness does the interval represent (donor LOO, fold CV, conformal residual)?
2. Null behavior on **weak-fit** and **strong-fit** slices separately vs A26.
3. Whether pairing is **supplement band**, **diagnostic comparator**, or **candidate null-monitor** (promotion audit only).

---

## 7. Proposed OC battery

**Artifact ID:** `D5-INST-AUGSYNTH-ASCM-002`  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`  
**Results:** [`track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json)  
**Status:** **executed** (n_mc=4 per committed archive)

### 7.1 Design

| Field | Value |
|-------|--------|
| Reference baseline | **A26** (SCM + UnitJackKnife) on same geometry/windows |
| Estimator under test | **AugSynthCVXPY** (+ inference variants per §6 as **arms**, not winners) |
| Windows | train=28, test=8 (001e); optional sensitivity grid later |
| Design method | `greedy_match_markets` + **weak-fit / hull-stratified** DGP arms |
| `n_mc` | ≥ 14 per cell (match D5-INST-AUGSYNTH-001); higher for promotion evidence |
| Governance flags | `no_promotion`, `no_calibration_signal_ingress`, `no_mmm` |

### 7.2 Known-DGP worlds

| World ID | Description | Hypothesis under test |
|----------|-------------|------------------------|
| W1 | **Strong SCM fit**, treated inside donor hull | AugSynth should **not harm** null FPR; may match or slightly diverge on point recovery. |
| W2 | **Weak SCM fit**, inside hull | AugSynth should **improve** effect recovery vs SCM with acceptable null behavior on **approved** inference arm. |
| W3 | **Weak SCM fit**, **outside** donor hull / extrapolation | AugSynth may improve recovery but must trigger D6/D11 flags; high false-confidence rate is failure. |
| W4 | **Sparse donor pool** (at `min_donors`) | Feasibility + stability vs A26 caveats. |
| W5 | **Rich donor pool** | Diminishing augmentation benefit; disagreement should shrink. |
| W6 | **Null treatment** (effect = 0) | Null FPR, interval exclusion, sign conflict rate vs A26. |
| W7 | **Known positive effect** (e.g. 4%, 8% grid) | Bias, MAE/RMSE vs truth on **bridged** scale. |
| W8 | **Post-period shock** on donors or treated | Robustness; conflict policy stress. |
| W9 | **Noisy donors** | Weight stability; augmentation value. |
| W10 | **Outlier market** | Outlier down-weighting via ridge; failure modes. |
| W11 | **Multi-treated unit panel** (if feasible) | Per-unit readouts only; no pooled AugSynth. |

### 7.3 Metrics (archived per world × arm)

| Metric | Purpose |
|--------|---------|
| Effect recovery **bias** | Mean(point − truth) @ injected effect |
| **MAE / RMSE** vs known truth | Primary “beat SCM” evidence in W2–W3 |
| **Null interval-exclusion FPR** | Must not materially exceed A26 on approved arm |
| **Coverage** (where intervals valid) | Secondary; only for arms passing F-INF semantics |
| **Interval width** | Diagnostic; compare arms |
| **D1–D11 diagnostics** | Stratification and failure flags |
| **False confidence rate** | D11 positive |
| **Conflict behavior vs SCM** | Sign disagreement %, material mismatch rate, F-DECISION policy input |

### 7.4 Prior OC (inputs, not sufficient alone)

| Prior artifact | Relevance |
|----------------|-----------|
| [`D5_INST_AUGSYNTH_001`](track_d/D5_INST_AUGSYNTH_001_REPORT.md) | Feasibility, JK @ null, scale mismatch vs SCM+JK |
| [`D5_INST_AUGSYNTH_003`](track_d/D5_INST_AUGSYNTH_003_REPORT.md) | Conformal invalid bands @ null — blocks governed uncertainty |
| [`D5_INST_AUGSYNTH_KFOLD_001`](track_d/D5_INST_AUGSYNTH_KFOLD_001_REPORT.md) | Kfold restricted diagnostic |
| Phase 14 archive | Spillover bias context |

**Gap:** None of the above **stratify by weak SCM fit** or outside-hull conditions — **D5-INST-AUGSYNTH-ASCM-002** is the required strengthening battery.

---

## 8. Promotion-audit entry criteria

Opening [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md) requires **all** of the following (none met today):

| # | Criterion | Status |
|---|-----------|--------|
| P1 | AugSynth **improves effect recovery** (MAE/RMSE) vs A26 in **weak-fit worlds** (W2–W3) without unacceptable bias in W1. | ⚠️ **Partial** (1/2 weak-fit worlds @ 8% in D5-ASCM2) |
| P2 | Does **not materially worsen** null FPR vs A26 on the **nominated inference arm** (separate strong-fit slice). | ❌ Conformal fails; JK estimand unclear |
| P3 | **Clear failure diagnostics** (D1–D11) archived and wired to TrustReport **proposal** (not production). | ❌ Partial |
| P4 | **Approved inference pairing** via `inference_semantics_ADR` + F-INF classification. | ❌ Open |
| P5 | **TrustReport disagreement policy** documented (supplement vs challenge vs block); no silent averaging. | ❌ Proposal only |
| P6 | **No unresolved geometry/estimand mismatch** (F-GEO, F-CAT, Track B estimand IDs). | ⚠️ Scale bridge open (D5-AS-FIND-004) |
| P7 | **CalibrationSignal** unchanged unless separate E5 amendment explicitly scoped. | ✅ Unchanged |
| P8 | **Implementation fidelity** checklist (§4) closed. | ❌ I4–I8 open |
| P9 | **Literature fidelity** checklist (§3) signed with deviation bounds. | ⚠️ Spillover restricted |

**Target roles (audit scope only — not granted here):**

| Role | Preconditions |
|------|----------------|
| `primary_null_monitor` supplement or conditional swap | Beat A26 on W2 null FPR + recovery; inference ADR closed |
| `diagnostic_comparator` (maintain/enhance) | Default if P1 fails or P2 fails |
| `primary_effect_readout` (product-specific) | Separate product ADR; not Phase 1 |

---

## 9. Exit recommendations

| Exit code | When | Current recommendation |
|-----------|------|------------------------|
| **`proceed_to_OC`** | Charter complete; D5-INST-AUGSYNTH-ASCM-002 not run | ✅ **Done** — see D5-INST-AUGSYNTH-ASCM-002 |
| **`proceed_to_inference_pairing_ADR`** | OC shows partial weak-fit gain; Conformal unsafe | Optional — D5-ASCM2 exit `remain_diagnostic_comparator` |
| **`proceed_to_inference_pairing_ADR`** | After OC stratification; Conformal vs JK vs Kfold | ✅ **Parallel** after W1–W3 slice from OC |
| **`remain_diagnostic_comparator`** | OC does not beat A26 on null FPR or weak-fit recovery | **Default baseline** until OC proves otherwise |
| **`proceed_to_promotion_audit`** | §8 all criteria met | ❌ **Not authorized** |
| **`keep_restricted`** | Conformal / callable_unverified arms | ✅ **A05** stays `characterized_restricted` |

**Immediate program order:**

1. Close implementation fidelity gaps (§4 I4–I8) in OC harness design.  
2. Run **D5-INST-AUGSYNTH-ASCM-002** (§7).  
3. Draft **inference_semantics_ADR** for leading arm(s).  
4. If §8 passes → **promotion_charter** scoped to `(unit panel × role × tuple)` only.  
5. Else → **`remain_diagnostic_comparator`** and refresh Track E INST-004 cards.

---

## 10. Contract crosswalk

| Contract | Application |
|----------|-------------|
| **F-GEO-001** | Unit-panel eligibility; multi-treated per-unit; block pooled multi-cell |
| **F-INF-001** | Interval semantics per arm; governed uncertainty remains **empty** |
| **F-CAT-001** | AugSynthCVXPY catalog; BRB block; no registry Bayesian |
| **AUDIT-010 Appendix A** | Rows A01–A05, A26 dispositions |
| **F-DECISION-001** | Baseline roles; conflict compare — **no amendment** |
| **Track E E2** | INST-004 `diagnostic_only` until OC + audit |

---

## 11. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Why AugSynth should challenge SCM | ✅ §1 |
| Scope / exclusions | ✅ §2 |
| Literature + implementation checklists | ✅ §3–§4 |
| Pre-OC diagnostics | ✅ §5 |
| Inference pairing candidates + evidence bar | ✅ §6 |
| OC worlds + metrics specified | ✅ §7 |
| Promotion-audit entry criteria | ✅ §8 |
| Exit recommendations | ✅ §9 |
| No promotion / code / CS / TrustReport change | ✅ |

---

*AUGSYNTH-ASCM-STRENGTHENING-001 v1.1.0 — charter + D5-INST-AUGSYNTH-ASCM-002 OC (research lane; no promotion).*
