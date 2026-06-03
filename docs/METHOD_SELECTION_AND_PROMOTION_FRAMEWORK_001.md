# METHOD-SELECTION-AND-PROMOTION-FRAMEWORK-001

**Document ID:** METHOD-SELECTION-AND-PROMOTION-FRAMEWORK-001  
**Type:** Method selection & promotion pipeline — **governance / research only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Governance is a **promotion pipeline**, not a freeze; **no method promoted in this artifact**  
**Decomposition input:** [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) (L1/L2/L3 complete)

**Related:** [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md) · [`TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md) · [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) (evidence work between lanes and promotion audit)

**Future gate (not authored here):** **METHOD-PROMOTION-AUDIT-TEMPLATE-001**

---

## 1. Executive summary

The platform is **decision-safe** today: F-INF, F-GEO, F-CAT, AUDIT-010, F-DECISION-001, and TrustReport `f_decision_context` prevent unsafe promotion. That work is **necessary but not sufficient** for a literature-aligned product hierarchy.

| Statement | Meaning |
|-----------|---------|
| **A26 (SCM + UnitJackKnife)** is the **current conservative governed null-monitor baseline** | Not the permanent winner |
| **L1/L2/L3 decomposition is complete** | See METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001 |
| **Promotion-ready count today** | **0** |
| **This artifact** | Defines **how** strong-but-restricted methods move toward stronger roles — **not** that any move today |

```text
L1 nominate estimator  +  L2 nominate inference  →  L3 must pass  →  benchmark vs A26  →  METHOD-PROMOTION-AUDIT-TEMPLATE-001  →  F-DECISION role change
```

**F-DECISION-001 remains authoritative baseline policy** until a tuple passes promotion gates and receives an explicit governance amendment.

---

## 2. Reframe existing governance (safety gates, not final hierarchy)

| Artifact | Role in pipeline | **Not** |
|----------|------------------|--------|
| **F-INF-001** | Interval semantics gate | Final say on “best method” |
| **F-GEO-001** | Geometry / adapter gate | Estimator ranking |
| **F-CAT-001** | Catalog / INV-015 gate | Promotion approval |
| **AUDIT-010** | Tuple disposition + MMM block | Method-selection winner |
| **TRACK-F checkpoint** | Pause impl/OC; contracts done | Permanent SCM lock-in |
| **F-DECISION-001** | **Baseline** role assignment today | Future roles without audit |
| **F-BACKLOG-002** | Investigation priority | Promotion list |
| **METHOD-READINESS matrix** | L1/L2/L3 decomposition | Auto-promotion |
| **TrustReport `f_decision_context`** | Visibility of baseline roles | Role upgrade |

**Principle:** Safety gates **block** bad states early. The **promotion pipeline** (this doc) defines **positive** evidence required to **replace or supplement** the baseline for a **specific data structure and role**.

---

## 3. Matrix consumption (L1 / L2 / L3 — given, not rediscovered)

From [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md):

### 3.1 L1 — estimator strength (nomination only)

| Strength | Estimators |
|----------|------------|
| **Strong** | SCM, AugSynthCVXPY |
| **Niche strong** | Class TBR (aggregate 1×1 only) |
| **Moderate** | TBRRidge, DID |
| **Blocked / R&D** | Supergeo, TrimmedMatch, TBR unit panel, TROP, BayesianTBR, base AugSynth |

### 3.2 L2 — inference strength (nomination only)

| Role | Inference |
|------|-----------|
| **Strong null-monitor** | UnitJackKnife (with SCM) |
| **Strong diagnostic** | Conformal, TimeSeriesKfold, Kfold |
| **Falsification** | Placebo |
| **Unverified** | JKP on TBRRidge pooled counterfactual |
| **Blocked / R&D** | Registry Bayesian; MCMC native |

### 3.3 L3 — combination status (compatibility gate)

| L3 classification | Examples |
|-------------------|----------|
| `ready_limited_governed_use` | **A26 only** |
| `characterized_restricted` | A05, A18, A19, A07, A10, A27 |
| `callable_unverified` | A16, A21 |
| `design_ADR_required` | Pooled multi-cell, supergeo, trim, DID CI, AugSynth+BRB |
| `research_to_production_candidate` | BayesianTBR, TROP |
| `keep_blocked` | A12, A20, A28, … |

**No method is promoted from L1 or L2 alone.**

---

## 4. Data-structure routing

For each **data structure**, the platform routes to a **current baseline**, **literature-aligned candidates**, and **promotion blockers**. Status reflects L3 + F-DECISION today.

| Data structure | Current governed baseline | Best literature-aligned estimator candidates | Eligible inference (by role) | L3 / F-DECISION status | Promotion blocker |
|----------------|---------------------------|---------------------------------------------|------------------------------|------------------------|-------------------|
| **Single treated, unit panel** | SCM + UnitJackKnife (A26) | AugSynthCVXPY; TBRRidge (diagnostic) | JK (primary); Conformal, TS-Kfold, Kfold (diag); Placebo (falsif.) | A26 `ready_limited`; A05/A18/A19 restricted | No beat-A26 OC; CS null_monitor_only |
| **Multi-treated, unit panel** | Per-unit: SCM+JK per cell | AugSynth; TBRRidge | Same per cell; Placebo **blocked** multi-treated (A28) | Per-cell A26 pattern; pooled **blocked** | Pooling rule; placebo geometry |
| **Aggregate 1×1 time series** | None as **primary**; SCM+JK on unit N/A | **Class TBR** (CausalImpact-style) | point, Kfold (diag); JKP (unverified A09) | A07/A10 restricted; A09 OC_required | Not unit primary; MMM blocked |
| **Multi-cell per-cell** | SCM+JK per cell (A26 per cell) | AugSynth per cell | JK per cell; diagnostics per cell | `OC_required` D5-MCELL | Pooled claims without F-MCELL-001 |
| **Pooled multi-cell** | **None** (blocked) | SCM+JK (invalid pooled) | — | `design_ADR_required` | F-MCELL-001 `pooling_rule_id` |
| **Supergeo markets** | **None** on flat panel | SCM+JK post **adapter** | JK after F-GEO-003 | `design_ADR_required` A29 | F-GEO-003 → RTP-003 |
| **Trimmed population** | **None** on 001e tensor | Trimmed native pair lift (diag only) | Pair CI (design) | `design_ADR_required` A30 | F-GEO-004 estimand bridge |
| **Sparse donor pool** | SCM+JK (caveats) | AugSynthCVXPY (literature: augmentation under weak donors) | JK + diagnostics | A26 caveats; A05 comparator | Donor stress OC; no primary swap without audit |
| **Weak SCM pretreatment fit** | SCM+JK (conservative) | **AugSynthCVXPY** (ASCM literature) | Conformal / JK comparators | A05 characterized | **First promotion lane candidate** — not promoted here |
| **Strong SCM pretreatment fit** | SCM+JK | AugSynth as **supplement** only | JK primary; diagnostics optional | A26 baseline sufficient | Must **beat** baseline to replace |
| **High volatility / outliers** | SCM+JK (001e battery) | TBRRidge, AugSynth (competitor practice) | Robust diagnostics (Conformal, Kfold) | Diagnostics only | Shock OC + conflict policy; no primary without audit |

---

## 5. Candidate-selection policy

### 5.1 Three-layer nomination rules

| Step | Layer | Action | May promote? |
|------|-------|--------|--------------|
| 1 | **L1** | Nominate estimator families strong for estimand/geometry | **No** |
| 2 | **L2** | Nominate inference layers strong for intended **role** | **No** |
| 3 | **L3** | Require valid **estimator × inference × geometry × estimand** (AUDIT-010 + F-GEO + F-INF) | **No** — enables **benchmark** only |
| 4 | **Benchmark** | Compare nominated L3 tuple vs **A26 baseline** on governed OC dimensions (§6) | **No** |
| 5 | **Promotion audit** | **METHOD-PROMOTION-AUDIT-TEMPLATE-001** (or equivalent) per tuple × role × data structure | **Only step that may authorize role change** |
| 6 | **Governance amendment** | Update F-DECISION allowlists, AUDIT-010 row, CS/MMM policy if applicable | After audit pass |

```text
IF L1 = strong AND L2 = strong BUT L3 ≠ characterized_restricted (or better)
THEN candidate = "benchmark queue" NOT "promotion queue"

IF L3 = characterized_restricted AND benchmark beats A26 on required dimensions
THEN eligible for METHOD-PROMOTION-AUDIT-TEMPLATE-001
ELSE remain diagnostic_comparator / excluded
```

### 5.2 Example nominations (not promotions)

| Candidate tuple | L1 | L2 | L3 today | Pipeline stage |
|-----------------|----|----|----------|------------------|
| AugSynth + Conformal (A05) | strong | strong diagnostic | characterized_restricted | Benchmark queue → weak-fit lane |
| TBR 1×1 + Kfold (A10) | niche strong | strong diagnostic | characterized_restricted | Aggregate lane |
| TBRRidge + Conformal (A18) | moderate | strong diagnostic | characterized_restricted | Comparator strengthen only |
| TBRRidge + JK (A16) | moderate | strong (SCM only) | callable_unverified | **Blocked** until L3 fixed |
| AugSynth + JK | strong | strong (on SCM est.) | not primary path | Use A05 Conformal lane first |

---

## 6. Benchmark policy

### 6.1 Baseline definition

| Field | Value |
|-------|--------|
| **Baseline tuple** | **A26** — SCM + UnitJackKnife on **unit panel** (single_cell / per-cell multi_cell) |
| **Baseline role** | `primary_null_monitor` (F-DECISION); CS `null_monitor_only` |
| **Baseline purpose** | Conservative **null-monitor** and direction reference — **not** lift detection, MMM lift, or platform MDE |
| **Replacement rule** | A candidate may **replace** baseline only if it **beats or materially improves** baseline on **required** dimensions **for the same data structure and role** |
| **Supplement rule** | A candidate may **supplement** baseline as `diagnostic_comparator` without audit if already L3 `characterized_restricted` |
| **Beside rule** | Multiple primaries for **different roles** (e.g. aggregate-only primary) require **separate** promotion audit per role |

### 6.2 Benchmark dimensions (governed OC evidence)

Evidence must come from **Track D–style batteries** (or successor OC), not literature alone.

| Dimension | Required for null-monitor promotion? | Required for diagnostic promotion? | Notes |
|-----------|--------------------------------------|-------------------------------------|-------|
| Effect recovery under known DGPs | **Yes** | Desirable | vs injected effect |
| Bias (point / path) | **Yes** | **Yes** | Scale-aligned comparisons |
| Null FPR (interval exclusion) | **Yes** | **Yes** | A16/A21 fail here today |
| Coverage / calibrated interval behavior | **Yes** | **Yes** | Conformal characterized |
| Power / MDE (where relevant) | Contextual | Contextual | Geo power ≠ instrument OC |
| Placebo / falsification behavior | **Yes** | N/A for non-falsification | SCM+Placebo A27 |
| Robustness: weak pretreatment fit | **Yes** for AugSynth lane | Desirable | Product differentiator |
| Robustness: donor sparsity | **Yes** | Desirable | Donor diagnostics |
| Robustness: shocks / outliers | Desirable | Desirable | May stay comparator |
| Conflict vs SCM + diagnostics | **Yes** | **Yes** | F-DECISION no silent averaging |

### 6.3 Beat / improve / beside criteria (draft)

| Outcome vs A26 | Interpretation | Pipeline effect |
|----------------|----------------|-----------------|
| **Beat** on null FPR + bias + recovery on battery | Eligible for **null-monitor promotion audit** | METHOD-PROMOTION-AUDIT-TEMPLATE-001 |
| **Improve** on weak-fit sub-battery only | Eligible for **supplement** or **conditional primary** audit | Narrower audit scope |
| **Beside** on aggregate geometry only | Eligible for **`aggregate_only_primary`** audit | Separate from unit panel |
| **Lose** on null FPR or conflict | Remain `diagnostic_comparator` or `excluded` | No audit |

---

## 7. Role-specific promotion (not global)

Promotion is always **(data structure × role × tuple)** — never “promote AugSynth globally.”

| Promotion role target | Current holder | First-wave candidates | Notes |
|----------------------|----------------|----------------------|-------|
| `primary_null_monitor` | A26 | AugSynth+JK or AugSynth+Conformal **only after audit** | **Do not declare AugSynth primary in this artifact** |
| `primary_effect_readout` | (product-defined; not separate today) | TBRRidge point (restricted) | Future product role |
| `diagnostic_comparator` | A05, A18, A19, A07, A10 | Maintain; strengthen evidence | Default safe expansion |
| `falsification_check` | A27 | Placebo taxonomy (F-P0-005) | Not promotion |
| `aggregate_only_primary` | *none* | TBR 1×1 + point/Kfold | Separate geometry |
| `per_cell_primary` | A26 per cell | Same as unit panel per cell | D5-MCELL OC |
| `research_only` | BayesianTBR, TROP | RTP charters | Not F-DECISION prod |
| `blocked` | A12, A20, A28, … | — | ADR first |

**F-DECISION-001 today:** Maps tuples to **baseline roles** above. **No tuple** receives upgraded role until §8 promotion audit passes.

---

## 8. First promotion lanes (recommended program order)

Using F-BACKLOG-002 rank + matrix L3 classifications. **Lanes authorize investigation and audit scoping — not promotion.**

| Lane ID | Scope | Rationale (matrix) | Preconditions | Deliverables before role change |
|---------|-------|-------------------|---------------|--------------------------------|
| **LANE-ASCM-001** | AugSynthCVXPY / ASCM on **unit-panel geo**, especially **weak SCM pretreatment fit** | L1 strong; A05 L3 restricted; industry ASCM | L3 `characterized_restricted`; benchmark vs A26 on weak-fit battery | METHOD-PROMOTION-AUDIT-TEMPLATE-001 (null-monitor or supplement); optional extra OC |
| **LANE-TBR-AGG-001** | **Class TBR** / CausalImpact-style **aggregate 1×1** | L1 niche strong; A07/A10 restricted; high product ask | TBR-001 maintained; geometry assert | Promotion audit for `aggregate_only_primary`; never unit panel |
| **LANE-MCELL-001** | **Multi-cell per-cell** + **pooling rule** | Product k=2 tests; per-cell A26 | F-MCELL-001 ADR for any pooled claim | D5-MCELL refresh; per-cell audits; pooling ADR before pooled primary |
| **LANE-SUPERGEO-001** | **Supergeo adapter** | L1 blocked until adapter; external imp 5 | F-GEO-003 ADR | RTP-003 charter; DES OC; then L3 rows |
| **LANE-TRIM-001** | **Trim estimand bridge** | Trim design; L1 blocked on SCM tensor | F-GEO-004 ADR | RTP-004; pair-lift diagnostic only first |
| **LANE-R&D-001** | **BayesianTBR**, **TROP** | research_only | RTP-001, RTP-002 | No F-DECISION prod role until charter exit |

**Explicitly not first lanes for primary null-monitor:** TBRRidge+JK/JKP (A16/A21) until L3 exits `callable_unverified`; registry Bayesian (INV-015); pooled multi-cell without ADR.

**Strengthening (downstream):** Concrete OC/ADR/audit work packages for each lane are defined in [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md). That artifact does **not** duplicate routing or promotion rules from this document.

---

## 9. Promotion evidence & METHOD-PROMOTION-AUDIT-TEMPLATE-001

### 9.1 Required future gate

**Any future role upgrade** (including `primary_null_monitor`, `aggregate_only_primary`, or CalibrationSignal policy change) requires:

1. A completed **METHOD-PROMOTION-AUDIT-TEMPLATE-001** (or governance-approved equivalent), and  
2. Explicit amendment to **F-DECISION-001** allowlists / **AUDIT-010** Appendix A row / **E5** CS policy as applicable.

**No current method receives promotion audit pass status in this artifact.**

### 9.2 METHOD-PROMOTION-AUDIT-TEMPLATE-001 (outline — to be authored)

| Section | Content |
|---------|---------|
| A. Tuple identity | Estimator × inference × geometry × estimand |
| B. Target role & data structure | From §7 |
| C. L1/L2/L3 snapshot | Cite matrix row |
| D. Benchmark vs A26 | §6 dimensions with OC artifact IDs |
| E. Conceptual validity | CV-001 / literature alignment |
| F. Conflict & F-DECISION impact | No silent averaging; TrustReport posture |
| G. CS / MMM / governed uncertainty | Explicit allowlist change proposal |
| H. Verdict | `promotion_denied` \| `promotion_approved_restricted` \| `promotion_approved_primary_for_structure` |
| I. Rollback conditions | What reverts role if later OC fails |

### 9.3 Evidence hierarchy

| Tier | Evidence type | Sufficient for promotion alone? |
|------|---------------|--------------------------------|
| T0 | Industry popularity | **No** |
| T1 | L1/L2 matrix strength | **No** |
| T2 | L3 `characterized_restricted` | **No** — enables benchmark |
| T3 | Governed OC beat/improve vs A26 | **Necessary** not sufficient |
| T4 | METHOD-PROMOTION-AUDIT-TEMPLATE-001 pass | **Required** for role change |
| T5 | Governance PR merged | **Required** for production |

---

## 10. F-DECISION-001 as baseline until gates pass

| Today | After promotion audit (future) |
|-------|----------------------------------|
| A26 → `primary_null_monitor` | May remain, share, or narrow by data structure |
| A05/A18/A19 → `diagnostic_comparator` | Unchanged unless audit upgrades **scoped** role |
| A16/A21 → `excluded` | Unchanged until L3 + benchmark + audit |
| CS export only for governed SCM+JK | Unchanged unless E5 amendment |
| MMM `exclude_from_mmm` | Unchanged until AUDIT-010 re-open |

**TrustReport `f_decision_context`:** Reflects **baseline** policy. Updates follow F-DECISION amendments — not this framework alone.

---

## 11. Non-goals (this artifact)

| Non-goal | Status |
|----------|--------|
| Promote any method today | ✅ None promoted |
| Declare AugSynth primary | ✅ Explicitly not |
| Assume SCM permanent primary | ✅ Baseline is conservative default only |
| L1 or L2 alone sufficient | ✅ Forbidden |
| Estimator / inference code | ✅ No code |
| OC execution | ✅ No OC run |
| CalibrationSignal expansion | ✅ No |
| MMM ingestion | ✅ No |
| TrustReport / F-DECISION behavior change | ✅ No |

---

## 12. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Governance reframed as pipeline not freeze | ✅ §2 |
| Data-structure routing | ✅ §4 |
| Candidate-selection uses L1/L2/L3 | ✅ §5 |
| Benchmark policy vs A26 | ✅ §6 |
| Role-specific promotion | ✅ §7 |
| First promotion lanes | ✅ §8 |
| METHOD-PROMOTION-AUDIT-TEMPLATE-001 named | ✅ §9 |
| F-DECISION baseline until audit | ✅ §10 |
| No promotion today | ✅ §11 |

---

*METHOD-SELECTION-AND-PROMOTION-FRAMEWORK-001 v1.0.0 — positive pipeline; 0 promotions authorized.*
