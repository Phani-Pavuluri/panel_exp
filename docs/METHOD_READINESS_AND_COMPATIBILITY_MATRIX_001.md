# METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001

**Document ID:** METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001  
**Type:** Layered readiness / compatibility matrix — **governance only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Estimator strength, inference strength, and combination validity are **separate**; **0** combinations are promotion-ready for MMM  
**Primary input:** [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md)

**Related:** [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md) · [`TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md)

---

## 1. Executive summary

F-BACKLOG-002 ranked **investigation priority** (external × internal × product). This matrix decomposes that into three **non-interchangeable** layers:

| Layer | Question | Authority |
|-------|----------|-----------|
| **L1 — Estimator** | Is the **estimator family** conceptually right for an estimand/geometry class? | CV-001 · D2 · Track E design cards |
| **L2 — Inference** | Is the **uncertainty/falsification mechanism** right for its role (null monitor vs band vs falsification)? | D3 · F-INF-001 · OC null FPR |
| **L3 — Combination** | Is **estimator × inference × geometry × estimand** valid, characterized, and policy-safe? | AUDIT-010 Appendix A · F-GEO · F-DECISION |

```text
L1 estimator strength  ≠  L2 inference trustworthiness  ≠  L3 combination readiness
Industry standard at L1 does NOT upgrade L3 without OC + AUDIT amendment.
```

| Global gate | Status |
|-------------|--------|
| MMM ingress | `not_ready_continue_track_f` (AUDIT-010) |
| Governed uncertainty allowlist | ∅ |
| CalibrationSignal | **A26 only** (`null_monitor_only`) |
| Promotion candidates | **0** |
| F-DECISION / TrustReport | Decision-safe; optional `f_decision_context` |

---

## 2. Layer separation rules

1. **Estimator row** scores **method family** only — not “SCM+JK is strong” (that is L3).
2. **Inference row** scores **uncertainty layer** only — Placebo is falsification, not an estimator.
3. **Combination row** is the only place for AUDIT-010 buckets, F-DECISION roles, CS/MMM policy.
4. **F-BACKLOG-002 rank** informs **strengthening priority** — not automatic reclassification.
5. **External importance** may justify ADR / OC / charter — **not** promotion without gates in §1.

**Strength scale (L1/L2):** `strong` · `moderate` · `weak` · `blocked` · `research_only`  
**Fidelity scale:** `high` · `partial` · `low` · `none` · `n/a`

---

## 3. Layer 1 — Estimator readiness

Independent of inference mode. “Strong estimator” means coherent estimand + geometry **when paired with a valid inference layer**.

| Estimator family | Target estimand | Supported geometry | Data structure | Literature / industry | Impl fidelity | Known failure modes | Track F / E status | TrustReport role (typical) | Product relevance | Promotion blockers |
|------------------|-----------------|-------------------|----------------|----------------------|---------------|---------------------|----------------------|---------------------------|-------------------|-------------------|
| **SCM / SyntheticControl** | Unit-level ATT (fixed window) | Unit panel; single/multi-cell **per cell** | Treated units × time; donor pool | Abadie et al.; GeoLift narrative (partial) | **high** (001e path) | Donor stress; multi-treated geometry; `full_model` misuse | **Characterized** null-monitor path | `primary_null_monitor` (with JK) | **high** | Not lift/MDE; supergeo/trim without adapter; pooled multi-cell |
| **AugSynthCVXPY** | Augmented SC ATT | Unit panel | Same as SCM + augmentation | Ben-Michael et al. ASCM | **partial** | Spillover; scale vs SCM+JK | Diagnostic comparator | `diagnostic_comparator` | **high** | Not CS/MMM; non-CVXPY path deprioritized |
| **Class TBR** | Aggregate treated vs control series | **Aggregate 1×1 only** | 2 series × time | CausalImpact / BSTS analog | **partial** on 1×1 | **Invalid on unit panel**; ≠ TBRRidge | Restricted aggregate diagnostic | `diagnostic_comparator` (1×1) | **high** (aggregate campaigns) | Unit panel permanent block; not MMM |
| **TBRRidge** | Ridge-regularized panel ATT | Unit panel; agg2 **power path** | Panel (n_time × n_units) | Marketing science ridge | **partial** | Scale ≠ SCM+JK; pooled-CF semantics | Restricted diagnostics | `diagnostic_comparator` / `excluded` | **medium** | JK/JKP on pooled CF unverified; not primary |
| **BayesianTBR** | BSTS-style aggregate | Unit (research) | Panel | CausalImpact MCMC | **low** (registry split) | Registry `Bayesian` ≠ NUTS | **research_only** | `research_only` | **low** | RTP-001; INV-015 separate |
| **TROP** | Transport regularized panel | Unit (research) | Panel | Arkhangelsky et al. | **low** | No registry inference surface | **research_only** | `research_only` | **low** | RTP-002 |
| **DID** | Relative ATT (panel) | Unit panel | Panel DiD | Standard DiD | **partial** | Relative CI semantics deferred (DEF-003) | Restricted diagnostic | `diagnostic_comparator` (ADR-gated) | **medium** | Bootstrap CI policy; not CS |
| **TrimmedMatch** | Pair-trimmed population lift | **Trimmed population** | Pairs Tp/Te | Trimmed design literature | **low** (design) | Population shift; no SCM tensor | **Blocked** readout | `blocked` | **medium** | F-GEO-004 bridge; RTP-004 |
| **Supergeo** (design + adapter) | Market/cluster ATT | **Supergeo unit** | MILP clusters | GeoLift / market designs | **none** (estimator on flat panel) | Flat SCM+JK invalid | **Blocked** without adapter | `blocked` | **high** | F-GEO-003; RTP-003 |
| **Base AugSynth** (non-CVXPY) | ASCM (claimed) | Unit | Panel | ASCM | **low** | CVXPY path sufficient | Deprioritized | `excluded` | **low** | F-CAT-003 not_worth_fixing_now |

### 3.1 Top estimator families worth strengthening

| Priority | Estimator | Why (L1) | Do **not** conflate with |
|----------|-----------|----------|---------------------------|
| **E1** | SCM | Only **strong** null-monitor family on 001e | GeoLift market designs (need supergeo) |
| **E2** | AugSynthCVXPY | Strong **diagnostic** alternative estimand | Primary or CS path |
| **E3** | Class TBR | High product ask on **aggregate** campaigns | TBRRidge or unit SCM |
| **E4** | TBRRidge | Common competitor panel model | SCM+JK primary |
| **E5** | Supergeo adapter | High industry; **blocked** until ADR | SCM on flat markets |

---

## 4. Layer 2 — Inference readiness

Independent of estimator. Role = how uncertainty is used in governance.

| Inference family | Uncertainty represented | Design alignment | Construction policy | Interval semantics | Null FPR / coverage evidence | Power evidence | Failure modes | Governance role | Promotion blockers |
|------------------|----------------------|------------------|---------------------|-------------------|------------------------------|----------------|---------------|-----------------|-------------------|
| **UnitJackKnife** | Donor LOO null variability | Fixed-window geo | Leave-one-donor | Path CI; JK semantics | **001e characterized** (SCM) | 001e reference | Multi-treated pooled-CF misuse on TBRRidge | **Causal null monitor** | Only with SCM primary; not governed export alone |
| **JKP** | Jackknife+ pivot intervals | Same | Pivot from JK | Path intervals | **Mixed** (SCM ok; TBRRidge ~29% null FPR) | Limited | Pooled CF pivot semantics | **Causal uncertainty** (restricted) | TBRRidge A21 unverified |
| **Kfold** | Time/block cross-validation | Assignment-aware folds | Panel Kfold | Effect intervals | **0% null FPR** on many batteries | Geo-power path (agg2) | Multi-treated aggregation | **Diagnostic band** | Not CS; not primary |
| **TimeSeriesKfold** | Time-series CV cumulative | Pre/post split | TS Kfold | Effect intervals | **POSTFIX characterized** (A19) | Limited vs JK | Orientation fixed F-INF-003 | **Diagnostic band** | Scale ≠ SCM+JK |
| **Conformal** | Distribution-free bands | Exchangeability caveats | Residual conformal | Conformal intervals | **POSTFIX characterized** (A05, A18) | Limited | Label/orientation (fixed) | **Diagnostic band** | Not governed uncertainty |
| **BRB** | Block residual bootstrap | Block structure | BRB blocks | Bootstrap CI | TBRRidge **characterized** | Limited | Not in AugSynth catalog (A04) | **Diagnostic band** | F-CAT-002 block for AugSynth+BRB |
| **Placebo** | Pre-treatment null | Single-treated only | Placebo time draw | Placebo band | **PLACEBO-001** | N/A (falsification) | Multi-treated invalid | **Falsification** | Not estimator; A28 blocked multi-treated |
| **Bayesian posterior** | Posterior predictive | BSTS model | Registry vs MCMC | Posterior intervals | **Not production** | R&D | INV-015 registry misuse | **Blocked / research** | INV-015; RTP-001 |
| **Bootstrap** (DID native) | Unit bootstrap | Panel DiD | Native bootstrap | Relative ATT CI | Partial | DEF-003 gap | Relative CI semantics | **Diagnostic** (ADR) | F-P0-004 |
| **point_estimate** | None (point only) | N/A | N/A | None | N/A | Ratio checks (TBR-001) | No interval governance | **Point diagnostic** | Never primary monitor |

### 4.1 Top inference methods worth strengthening

| Priority | Inference | Why (L2) | Valid roles | Invalid roles |
|----------|-----------|----------|-------------|---------------|
| **I1** | UnitJackKnife | Only **strong** null-monitor uncertainty | SCM primary | TBRRidge primary (A16) |
| **I2** | Placebo | Standard falsification | SCM single-treated | Estimator substitute |
| **I3** | Conformal | Industry-friendly diagnostic bands | Comparator (characterized) | Governed export |
| **I4** | TimeSeriesKfold | Common panel CV readout | Comparator | Primary |
| **I5** | JKP | Used in industry tooling | SCM restricted; TBR A09 OC optional | TBRRidge default comparator |

---

## 5. Layer 3 — Combination readiness (compatibility / promotion)

**Authoritative tuple source:** AUDIT-010 Appendix A + F-BACKLOG-002 focus rows.  
**Classification** applies to the **combination** — not inherited from L1/L2 alone.

### 5.1 Legend

| Classification | Meaning |
|----------------|---------|
| `ready_limited_governed_use` | Only **A26** — CS null_monitor_only; not MMM lift |
| `characterized_restricted` | OC complete; diagnostic comparator; F-DECISION safe |
| `diagnostic_strengthen` | Worth UX/docs/TrustReport visibility; no promotion |
| `callable_unverified` | Feasible; interval/null semantics not trusted |
| `research_to_production_candidate` | RTP charter; not prod |
| `design_ADR_required` | No code until ADR |
| `OC_required` | ADR satisfied or N/A; needs battery |
| `keep_restricted` | Stay diagnostic; intentional cap |
| `keep_blocked` | Policy or geometry block |
| `not_worth_prioritizing` | Low investigation return |

### 5.2 Combination matrix (focus + F-BACKLOG-002 surfaced)

| ID | Estimator | Inference | Geometry | Estimand | Interval semantics | Null FPR (001e) | Power | Conflict handling | CS policy | TrustReport / F-DECISION | Promotion audit | **Classification** | **Next artifact** |
|----|-----------|-----------|----------|----------|-------------------|-----------------|-------|-------------------|-----------|------------------------|-----------------|------------------|---------------------|
| **A26** | SCM | UnitJackKnife | unit panel | unit ATT pooled path | JK path CI | characterized (~caveats) | 001e reference | F-DECISION primary vs diagnostic | **null_monitor_only** | `primary_null_monitor` | **not MMM lift** | **ready_limited_governed_use** | Maintain 001e; no promotion PR |
| **A27** | SCM | Placebo | single-treated | falsification | placebo band | diagnostic | N/A | Falsification failure blocks | neither | `falsification_check` | blocked MMM | **characterized_restricted** | F-P0-005 taxonomy doc |
| **A05** | AugSynthCVXPY | Conformal | unit panel | aug ATT | conformal | 0% post-POSTFIX | limited | diagnostic_disagreement | neither | `diagnostic_comparator` | blocked | **characterized_restricted** | TrustReport comparator panel (done) |
| **A18** | TBRRidge | Conformal | unit panel | ridge ATT | conformal | 0% post-TBRRIDGE-003 | limited | sign compare only | neither | `diagnostic_comparator` | blocked | **characterized_restricted** | Optional comparator docs |
| **A19** | TBRRidge | TimeSeriesKfold | unit panel | ridge ATT | TS kfold | 0% post-POSTFIX | limited | scale caveat | neither | `diagnostic_comparator` | blocked | **characterized_restricted** | — |
| **A16** | TBRRidge | UnitJackKnife | unit panel | pooled CF JK | JK (pooled CF) | **~79%** | limited | **excluded** default | neither | `excluded` | blocked | **callable_unverified** | Behavioral OC or F-DECISION-002 sensitivity |
| **A21** | TBRRidge | JKP | unit panel | pooled CF JKP | JKP | **~29%** | limited | excluded default | neither | `excluded` | blocked | **callable_unverified** | parked_watch |
| **A07** | TBR class | point_estimate | agg 1×1 | aggregate ATT | none | ratio ~0.99 @8% | limited | diagnostic only | neither | `diagnostic_comparator` | blocked | **characterized_restricted** | TBR-001 maintained |
| **A10** | TBR class | Kfold | agg 1×1 | aggregate ATT | kfold | 0% | limited | restricted | neither | `diagnostic_comparator` | blocked | **characterized_restricted** | — |
| **A09** | TBR class | JKP | agg 1×1 | aggregate ATT | JKP unverified | callable | limited | excluded | neither | `excluded` | blocked | **OC_required** | F-INF-004 + spot OC (optional) |
| **A12** | TBR class | * | unit panel | — | — | — | — | blocked | neither | `blocked` | blocked | **keep_blocked** | Permanent (geometry) |
| **A01–A03** | AugSynthCVXPY | point/JK/Kfold | unit | aug ATT | varies | JK 0% | limited | diagnostic | neither | `diagnostic_comparator` | blocked | **diagnostic_strengthen** / restricted | — |
| **A13–A15** | TBRRidge | Kfold/BRB | unit/agg2 | ridge | restricted | 0% / char | agg2 power | diagnostic | neither | `diagnostic_comparator` | blocked | **keep_restricted** | — |
| **A25** | DID | bootstrap | unit | relative ATT | bootstrap | partial | limited | ADR-gated | neither | diagnostic (ADR) | blocked | **design_ADR_required** | F-P0-004 / DEF-003 |
| **A28** | SCM | Placebo | multi-treated | — | — | blocked | — | blocked | neither | `blocked` | blocked | **keep_blocked** | Multi-treated placebo |
| **A29** | SCM | UnitJackKnife | supergeo | — | — | blocked | — | blocked | neither | `blocked` | blocked | **design_ADR_required** | F-GEO-003 → RTP-003 |
| **A30** | SCM | UnitJackKnife | trimmed | — | — | blocked | — | blocked | neither | `blocked` | blocked | **design_ADR_required** | F-GEO-004 → RTP-004 |
| **A20** | TBRRidge | Bayesian registry | unit | — | — | blocked | — | INV-015 | neither | `blocked` | blocked | **keep_blocked** | Permanent prod |
| **A22–A23** | BayesianTBR | Bayesian/MCMC | unit | BSTS | research | R&D | — | research | neither | `research_only` | blocked | **research_to_production_candidate** | RTP-001 |
| **A24** | TROP | point | unit | transport | none | research | — | research | neither | `research_only` | blocked | **research_to_production_candidate** | RTP-002 |
| **A04** | AugSynthCVXPY | BRB | unit | — | n/a | not OC'd | — | blocked | neither | `blocked` | blocked | **design_ADR_required** | F-CAT-002 |
| **—** | * | * | pooled multi-cell | pooled | — | — | — | blocked w/o rule | neither | `blocked` | blocked | **design_ADR_required** | F-MCELL-001 |
| **—** | * | * | multi-cell per-cell | per-cell | per A26 row | per cell | D5-MCELL | per cell | neither | per-cell diagnostic | blocked pooled | **OC_required** (per cell) | D5-MCELL refresh |

### 5.3 Top combinations worth strengthening

| Priority | Combination | L1+L2 gist | Classification today | Strengthen toward |
|----------|-------------|------------|----------------------|-------------------|
| **C1** | SCM + JK (A26) | Strong + strong on unit panel | `ready_limited_governed_use` | Maintain; clarify caveats in Track E only |
| **C2** | AugSynth + Conformal (A05) | Strong diag est + strong diag inf | `characterized_restricted` | TrustReport visibility (done) |
| **C3** | TBRRidge + Conformal/Kfold (A18/A19) | Moderate + strong diag inf | `characterized_restricted` | Comparator docs; no promotion |
| **C4** | SCM + Placebo (A27) | Strong + falsification | `characterized_restricted` | F-P0-005 placebo taxonomy |
| **C5** | TBR 1×1 + point/Kfold (A07/A10) | Strong niche + diag inf | `characterized_restricted` | Product aggregate playbook |
| **C6** | Per-cell multi-cell + SCM+JK | Strong per cell | per-cell `ready_limited` | OC per cell only (D5-MCELL) |

---

## 6. Blocked despite external importance (F-BACKLOG-002)

| Item | Ext imp | Why still blocked | Layer responsible |
|------|---------|-------------------|-----------------|
| GeoLift / supergeo SCM+JK | 5 | Wrong geometry/estimand without adapter | L1+L3 |
| Trimmed match SCM+JK | 4 | Population bridge missing | L1+L3 |
| Pooled multi-cell | 4 | No `pooling_rule_id` | L3 policy |
| Class TBR unit panel | 3 | Invalid geometry | L3 |
| TBRRidge + JK/JKP (A16/A21) | 2 | Null FPR / semantics | L2+L3 |
| Registry Bayesian | 2 | INV-015 | L2 |
| MMM all tuples | — | AUDIT-010 | Program |

**Rule:** High **external** rank → ADR/charter/OC — **not** L3 reclassification without evidence.

---

## 7. F-BACKLOG-002 → matrix mapping

| F-BACKLOG-002 lane | Matrix layer | Typical classification |
|--------------------|--------------|------------------------|
| decision_layer_candidate | L3 | `characterized_restricted` or `ready_limited_governed_use` |
| diagnostic_only | L3 | `characterized_restricted` / `diagnostic_strengthen` |
| parked_watch | L2+L3 | `callable_unverified` |
| design_ADR | L1 or L3 precondition | `design_ADR_required` |
| research_to_production_charter | L1 | `research_to_production_candidate` |
| OC_priority | L3 | `OC_required` |
| keep_blocked | L1/L2/L3 | `keep_blocked` |

---

## 8. Recommended next artifact (high-priority items)

| Item | Classification | Next artifact | Owner lane |
|------|----------------|---------------|------------|
| A26 SCM+JK | ready_limited_governed_use | Track E caveat doc refresh only | E |
| A05/A18/A19 diagnostics | characterized_restricted | — (sufficient) | — |
| A27 placebo | characterized_restricted | **F-P0-005** placebo taxonomy | F-P0 |
| A09 TBR+JKP | OC_required | **F-INF-004** + optional spot OC | F-INF |
| A16/A21 TBRRidge JK/JKP | callable_unverified | Behavioral study memo or **F-DECISION-002** | Research |
| Pooled multi-cell | design_ADR_required | **F-MCELL-001** ADR | Design |
| Supergeo | design_ADR_required | **F-GEO-003** → RTP-003 | Design → R&D |
| Trim | design_ADR_required | **F-GEO-004** → RTP-004 | Design → R&D |
| DID bootstrap | design_ADR_required | **F-P0-004** / DEF-003 | F-P0 |
| BayesianTBR | research_to_production_candidate | **RTP-001** charter | R&D |
| TROP | research_to_production_candidate | **RTP-002** charter | R&D |
| AugSynth+BRB | design_ADR_required | **F-CAT-002** (prefer block) | F-CAT |
| Per-cell k=2 | OC_required | **D5-MCELL** refresh | Track D |

**Not listed:** Promotion audit (none authorized). See [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) for **METHOD-PROMOTION-AUDIT-TEMPLATE-001** (future gate).

---

## 9. Promotion pipeline (downstream)

L1/L2/L3 in this matrix are **inputs** to [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md):

- **Routing** by data structure (§4 of framework)
- **Candidate selection** (L1+L2 nominate; L3 gates benchmark)
- **Benchmark** vs A26 baseline
- **Role-specific promotion** only after METHOD-PROMOTION-AUDIT-TEMPLATE-001

This matrix does **not** authorize promotion.

---

## 10. Crosswalk: contracts and decision layer

| Contract | Layer enforced |
|----------|----------------|
| **F-GEO-001** | L3 geometry before intervals |
| **F-INF-001** | L2 interval semantics; governed ∅ |
| **F-CAT-001** | L2 catalog; INV-015 |
| **F-DECISION-001** | L3 roles; no promotion |
| **TrustReport `f_decision_context`** | L3 visibility only ([`TRUSTREPORT_F_DECISION_INTEGRATION_001.md`](TRUSTREPORT_F_DECISION_INTEGRATION_001.md), [`TRUSTREPORT_DECISION_INPUTS_WIRING_001.md`](TRUSTREPORT_DECISION_INPUTS_WIRING_001.md)) |
| **E5 CalibrationSignal** | L3: A26 only |
| **AUDIT-010** | L3 authoritative buckets |

---

## 11. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Estimator table (L1) | ✅ §3 |
| Inference table (L2) | ✅ §4 |
| Combination / promotion table (L3) | ✅ §5 |
| Top strengthen lists | ✅ §3.1, §4.1, §5.3 |
| Blocked despite external importance | ✅ §6 |
| Next artifact per priority | ✅ §8 |
| Layers kept separate | ✅ §2 |
| No promotion / CS / MMM expansion | ✅ §1 |

---

*METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001 v1.0.0 — ranking input F-BACKLOG-002; does not authorize promotion or code.*
