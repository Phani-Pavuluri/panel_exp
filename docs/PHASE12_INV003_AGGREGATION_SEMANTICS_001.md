# Phase 12 INV-003 — aggregation and estimand semantics characterization 001

**Investigation:** INV-003 — multi-treated aggregation semantics  
**Status:** evidence archive (semantic / governance tier)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  

**Related:** [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md)

**Raw JSON (local, not committed):** `.phase12_inv003_aggregation.json`

This document archives **estimand and aggregation semantics** only. No estimator, inference, recovery scoring, threshold, or eligibility registry changes were made.

---

## 1. Executive summary

### Which estimands align

| Pair | Homogeneous multi-treated | Heterogeneous multi-treated | Single-treated |
|------|---------------------------|----------------------------|----------------|
| **A (canonical cell relative)** ↔ **truth scalar** | **Identical** | **Identical** | **Identical** |
| **B (pooled-path relative)** ↔ **A** | **Identical** (machine precision) | **Small divergence** (≤ ~0.07% of lift in this matrix) | **Identical** |
| **C (aggregate pooled relative)** ↔ **B** | **Identical** | **Identical** | **Identical** |
| **D (cumulative absolute)** / **E (mean absolute)** ↔ **A/B/C** | **Not comparable** (different scale) | **Not comparable** | **Not comparable** |

### Which diverge

- **B vs A** diverges when **heterogeneous relative effects** combine with **multi-treated pooling** — because aggregation order differs (time-first geo-mean of levels → relative **vs** cell-wise relative → mean).
- **Recovery predicted path (B)** vs **absolute truth scalar** diverges catastrophically on **`effect_type="absolute"`** DGPs while recovery still applies `_path_relative_att` scoring.
- **D / E / DID cumulative** quantities are **diagnostic or family-specific** — not interchangeable with relative ATT recovery scores.

### Safest operational estimands (today)

| Role | Estimand | Rationale |
|------|----------|-----------|
| **Primary validation truth** | **A — canonical cell relative ATT** | Matches `world.truth["true_effect"]` on relative DGPs |
| **Primary recovery prediction** | **B — pooled-path relative ATT** | What `_path_relative_att` and interval extraction implement |
| **Calibration interval target** | **`relative_att_post` aligned to B** | `recovery_intervals.py` contract |
| **Diagnostic only** | D, E, per-geo effects | Different scales / aggregation |
| **Unsafe comparison** | Relative recovery score vs absolute truth; cumulative vs relative without transform | Documented scale mismatch |

**Headline:** Under default **homogeneous relative** recovery DGP, operational stack is **coherent**. Under **heterogeneity** or **absolute DGP**, semantic ambiguity is **material** and must be governed explicitly before Phase 13 decisions or Track C contracts.

---

## 2. Current operational semantics

### Recovery scoring (operational)

| Field | Value | Source |
|-------|--------|--------|
| **Scored target estimand** | `relative_att_post` | `recovery_runner.SCORED_TARGET_ESTIMAND` |
| **Predicted effect function** | `_path_relative_att` | `recovery_runner.PREDICTED_EFFECT_SCORING` |
| **Truth scalar** | `world.truth["true_effect"]` | Canonical **cell relative ATT (A)** on relative DGPs |
| **Recovery success** | \|predicted − truth\| within tolerance | Compares **B-like prediction** to **A-like truth** |
| **Aggregation mode metadata** | `relative_att_post_path_mean` | `synthetic_world.RECOVERY_AGGREGATION_MODE` |

### Interval semantics (operational)

| Field | Value |
|-------|--------|
| **Interval estimand (when aligned)** | `relative_att_post` |
| **Interval scale** | `path_period_relative_mean` |
| **Construction** | Path level `y`, `y_hat`, `y_lower`, `y_upper` → pool treated units per period like `_path_relative_att` → scalar CI |
| **Significance (TBRRidge BRB/Kfold)** | CI exclusion of zero on aligned relative scale |

### Canonical truth (validation)

| Quantity | Definition |
|----------|------------|
| **A — canonical cell relative** | Mean of `(Y − Y(0)) / Y(0)` over all **treated × post** cells |
| **Scalar truth on relative DGP** | Equals **A** (`_scalar_truth_effect`) |
| **Configured effect** | Scenario parameter; equals realized lift only under homogeneous relative |

### Documented mismatches (still open)

| Mismatch | Severity |
|----------|----------|
| **B vs A under heterogeneous multi-treated** | Low numeric drift in synthetic matrix; **conceptual** non-equivalence |
| **Relative prediction vs absolute truth** | **Severe** on absolute DGP (bias O(100+) in spot check) |
| **Cross-estimator ATT comparison** | `OPEN_INVESTIGATIONS` — estimand not enforced across SCM/TBR/DID |
| **DID cumulative bootstrap** | `did_relative_att_interval_unsupported` — different scale from recovery |

---

## 3. Aggregation comparison matrix

**Estimand definitions used in this archive:**

| ID | Name | Definition |
|----|------|------------|
| **A** | Canonical treated-cell relative ATT | `canonical_relative_att_post` |
| **B** | Pooled-path relative ATT | `_path_relative_att` with TBRRidge-shaped `(time × treated)` exports |
| **C** | Aggregate-relative ATT | `canonical_pooled_relative_att_post` (sum geos per period → relative) |
| **D** | Cumulative absolute ATT | `canonical_cumulative_att` (sum of increments) |
| **E** | Mean post-period absolute ATT | `canonical_absolute_att_post` |

**Method:** Perfect counterfactual exports (`y_hat = Y(0)`) to isolate **aggregation semantics** from estimator error. **15 seeds** per scenario (10 for noise variants). Branch `phase12-run002-brb-oc`, commit `10274b7`.

### Matrix summary

| Scenario | n_treated | A (truth) | B − A (max abs) | C − A (max abs) | B vs C | Operational note |
|----------|-----------|-----------|-----------------|-----------------|--------|------------------|
| `hom_multi_default` | 4 | 0.10 | **0** | **0** | equal | Default recovery DGP — **aligned** |
| `hom_multi_null` | 4 | 0.00 | **0** | **0** | equal | Null reference |
| `het_multi` | 4 | ~0.098 | **0.00072** | **0.00072** | equal | Heterogeneous U(0.5,1.5) multipliers |
| `hom_single` | 1 | 0.10 | **0** | **0** | equal | KFold-viable geometry |
| `het_single` | 1 | varies | **0** | **0** | equal | Single-unit heterogeneity degenerate |
| `hom_two_treated` | 2 | 0.10 | **0** | **0** | equal | KFold failure boundary |
| `hom_multi_high_noise` | 4 | 0.10 | **0** | **0** | equal | Noise does not break alignment |
| `hom_multi_low_corr` | 4 | 0.10 | **0** | **0** | equal | Donor corr does not break alignment |

### Example row — heterogeneous multi-treated (seed 0)

| Estimand | Value |
|----------|-------|
| A (truth scalar) | 0.10224 |
| B (path) | 0.10200 |
| C (pooled aggregate) | 0.10200 |
| D (cumulative abs) | 612.69 |
| E (mean abs) | 10.21 |
| B − A | −0.00024 (~−0.24% of lift) |

### Example row — homogeneous multi-treated (seed 0)

| Estimand | Value |
|----------|-------|
| A = B = C | 0.1000000000000001 |
| D | 600.69 |
| E | 10.01 |

**Finding:** **B and C are operationally identical** for TBRRidge-shaped path exports in all cells. Divergence from **A** appears only under **multi-treated heterogeneity**.

---

## 4. Heterogeneous-effect behavior

### When pooled paths hide geo-level heterogeneity

- DGP assigns treated unit \(g\) a multiplier \(m_g \sim U(0.5, 1.5)\) on configured relative effect.
- **A** averages relative lifts over **every treated geo × post period**.
- **B** averages **across geos first at each time**, then computes relative lift on pooled series, then averages post periods.

These are **different estimands** when \(m_g\) varies — even with perfect counterfactuals.

### When averaging order changes interpretation

| Order | Estimand | Interpretation |
|-------|----------|----------------|
| Cell-first (A) | Equal weight per geo-period | Standard **ATT-style** cell average |
| Time-first geo-mean (B) | Equal weight per period | **Synthetic pooled treated series** — closer to aggregate market lift path |

Under homogeneous relative effects, orders commute (verified to machine precision).

### When relative transforms become unstable

- Near-zero counterfactual levels amplify relative lifts (general DGP caution).
- **Absolute effect DGP** with relative path scoring: truth scalar ≈ **249** (absolute), **B ≈ 2.48** (relative) — **not a small drift; wrong scale entirely**.
- Recovery spot check on absolute DGP: bias ≈ **−246** (`TBRRidge` point, n=5) — scoring contract broken for absolute scenarios.

---

## 5. Multi-treated implications

### Interaction with INV-007 (KFold geometry)

| Layer | Interaction |
|-------|-------------|
| **Geometry** | Kfold fails for n_treated ≥ 2 due to `(n_pre, n_treated)` broadcast — **before** aggregation semantics matter |
| **Semantics** | Operational **B** pools across treated units in `_path_relative_att` — same pooling family Kfold legacy paths assume incorrectly at multi-treated |
| **Single-treated** | Geometry viable **and** B = A under homogeneous relative |

### Pooled treated paths and operational metrics

- Default recovery DGP (~4 treated, homogeneous): **truth, path score, and intervals share one relative estimand** (approximately **A = B**).
- Heterogeneous multi-treated: recovery **grades against A** while predicting **B** — introduces **structured residual** even with perfect estimation.
- Run 002 / Phase 11 positive under-coverage: intervals use **same pooling as B**; width behavior is **not independent** of aggregation choice.

### Future TrustReport implications

| Trust signal | Implication |
|--------------|-------------|
| `incompatible_estimand` | Relative recovery score vs absolute business question |
| `inconclusive` | Heterogeneous multi-geo panel without declared aggregation contract |
| `supported_*` | Requires declared **primary estimand** = operational B **and** truth alignment documented |

---

## 6. Future experimentation implications

| Platform area | INV-003 implication |
|---------------|---------------------|
| **GeoX** | Declare whether report is **cell ATT (A)** or **pooled path lift (B)** on multi-geo tests |
| **Conversion lift / A/B (Track C)** | User/session estimands must map to registry — not silent `_path_relative_att` |
| **MMM calibration** | Calibrated contribution requires **explicit transform** from experiment estimand — raw relative path ≠ MMM increment without contract (INV-023) |
| **ExperimentEvidence** | Must store **declared estimand**, **scored estimand**, **interval estimand**, **aggregation mode** |
| **Unified estimand contracts (INV-020)** | Primary output of this investigation — formalize table in §7 |
| **DID family** | Cumulative / pooled DID exports remain **separate branch** — not recovery-comparable without waiver |

---

## 7. Recommendations

### Primary operational estimands (relative geo recovery — current scope)

| Estimand | Classification |
|----------|----------------|
| **A — canonical cell relative** | **Validation truth** for relative DGPs |
| **B — pooled-path relative** | **Operational prediction + interval target** (current code truth) |
| **Homogeneous multi-treated default DGP** | **Safe to treat A ≈ B** for scoring (documented) |

### Diagnostic-only estimands

| Estimand | Use |
|----------|-----|
| **D — cumulative absolute** | DID-style diagnostics; scale checks |
| **E — mean absolute post** | Absolute-effect DGP truth; not relative recovery |
| **Per-unit `effect_by_unit`** | Heterogeneity review |
| **C — aggregate pooled relative** | Collapses to B for TBRRidge path exports; useful for DID cross-check |

### Unsafe / misleading comparisons (without explicit transform)

| Comparison | Why unsafe |
|------------|------------|
| Recovery relative score vs **absolute** business lift | Scale mismatch |
| SCM/TBR/DID point exports vs each other as “the ATT” | Cross-family estimand gap |
| Cumulative vs relative coverage metrics | DID policy already blocks |
| Calibration pass on null only → positive lift claims | Phase 11 / Run 002 lesson |

### Future investigation areas (Phase 13 / Track C inputs)

1. **Formal estimand registry entry** mapping A vs B and when they may diverge.  
2. **Heterogeneous DGP scenario catalog** for recovery — score against A or B explicitly.  
3. **Single-treated calibration scenario** documentation (pairs with INV-007).  
4. **Absolute-effect scenarios** — exclude from relative recovery battery or add alternate scoring path.  
5. **TrustReport rules** for multi-treated heterogeneous panels (`inconclusive` vs `incompatible_estimand`).

---

## 8. Non-goals

This investigation **does not**:

- Redefine official estimands or change `SCORED_TARGET_ESTIMAND`
- Modify `_path_relative_att`, `recovery_intervals.py`, or `synthetic_world` truth
- Change `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` or maturity labels
- Promote any estimator or claim production-safe status
- Replace Phase 13 governance decision — it **informs** it

This investigation **does**:

- Document operational vs canonical alignment on default recovery DGP
- Quantify heterogeneous multi-treated divergence (small but non-zero)
- Flag absolute-vs-relative scoring as a **hard incompatibility**
- Connect aggregation semantics to KFold geometry and TrustReport design

---

## Appendix A — Investigation execution

| Field | Value |
|-------|--------|
| Branch | `phase12-run002-brb-oc` |
| Commit | `10274b7` |
| Simulations | 10–15 per scenario × 3 estimand families |
| Perfect CF probe | `y_hat = counterfactual` with TBRRidge `(time × treated)` export shape |
| Estimator error isolated | Yes (semantic layer only) |

---

## Appendix B — Phase 12 evidence integration

| Config | Governance status (after INV-003 lens) |
|--------|--------------------------------------|
| **SCM_UnitJackKnife** | Null monitor; intervals use jackknife pooling — same **B-family** path semantics |
| **TBRRidge_BRB** | Bounds fixed; positive under-coverage; intervals aligned to **B** |
| **TBRRidge_Kfold** | Single-treated geometry only; semantics align with **B** when runs succeed |

**Phase 13 readiness:** Semantic blocker **characterized** — not eliminated. Decision can proceed with explicit **A vs B** and **geometry** contracts.

---

*Evidence archive INV-003-001. Registry and scoring unchanged.*
