# Phase 15 INV-029 — Placebo operating-characteristic characterization 001

**Investigation:** INV-029 — Placebo inference characterization  
**Status:** evidence archive (production-tier single-treated + characterization matrix)  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  

**Related:** [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) · [`tests/test_inference_result_semantics.py`](../tests/test_inference_result_semantics.py)

**Raw JSON (local, not committed):** `.phase15_placebo_characterization.json`  
**Reproduction:** `poetry run python scripts/phase15_placebo_characterization.py`

No placebo implementation, threshold, eligibility, maturity, or recovery scoring changes were made.

---

## 1. Executive summary

**Headline:** SCM Placebo is **viable on single-treated panels** with **100% `placebo_band` path semantics** and **aligned recovery interval extraction** (`relative_att_post`). **Multi-treated panels fail systematically** (`NotImplementedError`: single-treated-only implementation). **TBR Placebo fails** (`AssertionError` / aggregated-control exclusion). **TBRRidge Placebo** mirrors SCM on single-treated geometry.

| Layer | Verdict |
|-------|---------|
| **Single-treated SCM Placebo (production n=100)** | **Runs complete**; null FPR = 0, coverage = 1; positive **power = 0**, significance = 0; intervals **include zero** on positive |
| **Multi-treated (n≥2, default ~4)** | **100% failure** — not a calibration surface today |
| **Placebo-band semantics** | **100%** of successful runs export `path_interval_type = placebo_band`; inversion CI present |
| **Recovery calibration metrics** | **Meaningful when aligned** on single-treated cells; **unavailable** on failed cells |
| **Nominal calibration** | **Not demonstrated for lift detection**; **not** added to eligibility registry |

**Classification:** **Expert-review null-reference / diagnostic inference** on **single-treated-only** geometry — not a lift detector; not default-DGP multi-geo ready.

---

## 2. Run metadata

| Field | Value |
|-------|--------|
| **Package version** | 0.2.1 |
| **Commit** | at execution branch tip |
| **Investigation ID** | INV-029 |
| **Primary config** | `SCM_Placebo` (`SyntheticControl(inference="Placebo", alpha=0.05)`) |
| **Secondary configs** | `TBRRidge_Placebo`, `TBR_Placebo` |
| **Harness** | Investigation-only loop (`scripts/phase15_placebo_characterization.py`) |
| **α** | 0.05 |
| **Scored estimand** | `relative_att_post` (unchanged) |
| **Wall time** | ~216 s |
| **Cells** | 22 |

### Tiering

| Tier | n_simulations | Seeds | Cells |
|------|---------------|-------|-------|
| **Production characterization** | 100 | 0, 1, 2 | `prod_null_single_treated`, `prod_positive_single_treated` |
| **Characterization** | 30 | 0, 1, 2 | All other cells |

### Investigation-only eligibility note

| Field | Value |
|-------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` — **unchanged** |
| **Placebo configs** | **Not eligible** |

---

## 3. Production-tier results (single-treated, n=100)

Aggregates: **mean across seeds 0–2** (300 replications per cell).

### `recovery_null_effect` — `prod_null_single_treated`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| FPR | 0.000 | 0.000 | 0.000 | 0.000 |
| Mean interval width | 0.068 | 0.000 | 0.068 | 0.068 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Placebo band rate | 1.000 | — | — | — |
| Inversion CI rate | 1.000 | — | — | — |

### `recovery_positive_effect` — `prod_positive_single_treated`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| Power | 0.000 | 0.000 | 0.000 | 0.000 |
| Mean interval width | 0.228 | 0.001 | 0.227 | 0.229 |
| Width / effect | ~2.28 | — | — | — |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Placebo band rate | 1.000 | — | — | — |

**Interpretation:** On single-treated panels, placebo-derived recovery intervals **cover the true effect** on positive scenarios (coverage = 1) but **never exclude zero** (power = 0, significance = 0). This differs from UnitJackKnife positive cells where coverage was 0 in Phase 11/14 — placebo intervals here are **wide enough to include both zero and the true lift**. Still **not a lift detector**.

---

## 4. Null behavior, FPR, and coverage

### Single-treated successful cells (SCM)

| Cell | Null coverage | Null FPR | Positive coverage | Positive power |
|------|---------------|----------|-------------------|----------------|
| prod_null / prod_positive (n=100) | 1.0 | 0.0 | 1.0 | 0.0 |
| geom_n1 null / positive | 1.0 | 0.0 | 1.0 | 0.0 |
| donor small / medium / large null | 1.0 | 0.0 | — | — |
| donor small / medium / large positive | — | — | 1.0 | 0.0 |

**Null monitoring:** FPR = 0 across all successful null cells — **sane**, not anti-calibrated.

**Positive scenario:** coverage = 1 reflects **intervals bracketing true effect**, not detection; power = 0 because intervals **always include zero**.

---

## 5. Placebo-band semantics and interval alignment

On every **successful** replication:

| Field | Value |
|-------|--------|
| **`path_interval_type`** | `placebo_band` (via `InferenceResult`) |
| **`interval_estimand` (recovery extraction)** | `relative_att_post` when aligned |
| **`interval_scale`** | `path_period_relative_mean` |
| **`ci_via_inversion`** | `true` — cumulative-effect inversion CI mapped to path bands |
| **`interval_aligned`** | `true` on single-treated successful runs |

**Critical semantic note:** Path bounds are **placebo null envelopes**; recovery scoring converts them to scalar `relative_att_post` intervals for OC metrics. This is **documented alignment**, not claim that placebo bands are jackknife/bootstrap CIs. Track B must preserve **`placebo_band` vs `confidence_interval`** distinction ([`IntervalType`](panel_exp/inference_result.py)).

**Misalignment policy:** Failed cells (multi-treated) report `interval_estimand=unavailable` — metrics correctly unavailable, not silently scored.

---

## 6. Geometry sensitivity (treated count)

| n_treated | Failure rate | Interval aligned | Notes |
|-----------|--------------|------------------|-------|
| **1** | 0% | 100% | Full OC available |
| **2** | **100%** | 0% | `NotImplementedError`: single-treated-only |
| **4** | **100%** | 0% | Same |
| **Default (~4)** | **100%** | 0% | Default recovery DGP **not supported** |

**Finding:** Sharp **single-treated-only** execution boundary — analogous in severity to pre-fix KFold multi-treated failures, but here is an **explicit implementation constraint**, not a broadcasting bug.

---

## 7. Donor-count sensitivity (single-treated)

| Donor tier | n_geos | n_control | Null width (mean) | Positive width (mean) | Positive width/effect |
|------------|--------|-----------|-------------------|----------------------|------------------------|
| small | 6 | 5 | 0.075 | 0.297 | ~3.0× |
| medium | 20 | 19 | 0.068 | 0.232 | ~2.3× |
| large | 40 | 39 | 0.027 | 0.055 | ~0.55× |

**Finding:** Width varies with donor pool size but remains **lift-detection-inadequate** (power = 0). Small-tier **n_treated=4** cell fails (multi-treated), not donor gate.

**Control gate:** Panels with ≥5 controls and **single treated** pass; no `placebo_unsupported` control-count failures observed on successful cells.

---

## 8. Multi-treated and cross-estimator behavior

### Default multi-treated DGP

| Cell | Failure rate | Top failure |
|------|--------------|-------------|
| default_multi_null / positive | 1.000 | `NotImplementedError` (90/90 per seed aggregate) |

### TBRRidge Placebo (single-treated)

| Cell | Failure rate | Null FPR | Positive power | Width/effect (positive) |
|------|--------------|----------|----------------|-------------------------|
| tbrridge_single_null | 0% | 0.0 | — | — |
| tbrridge_single_positive | 0% | — | 0.0 | ~1.7× |

**Finding:** TBRRidge + Placebo **matches SCM pattern** on single-treated geometry with **somewhat narrower** positive intervals — still power = 0.

### TBR Placebo (single-treated)

| Cell | Failure rate | Top failure |
|------|--------------|-------------|
| tbr_single_null / positive | **100%** | `AssertionError` |

**Finding:** TBR aggregated-control path **excluded** from placebo-in-space (`placebo_unsupported` policy) — documented failure surface, not OC matrix.

### Heterogeneous effects (single-treated positive)

| Metric | Value |
|--------|-------|
| Failure rate | 0% |
| Coverage | 1.0 |
| Power | 0.0 |
| Width | ~0.229 |

**Finding:** No material degradation vs homogeneous single-treated positive on this battery.

---

## 9. Acceptable-outcome mapping (plan §4)

| Planned outcome | Evidence |
|-----------------|----------|
| **Trustworthy null monitor** | **Partial** — single-treated null FPR = 0, stable across seeds |
| **Expert-review inference (strict export)** | **Supported** — `placebo_band` semantics 100% on success path |
| **Null monitor only** | **Supported** — positive power = 0 |
| **Research-only** | **Default multi-treated DGP** — 100% failure |
| **Geometry restricted** | **Required:** single-treated-only for any OC claims |
| **Policy closed on relative-ATT calibration for lift** | **Supported** — power = 0; not lift detector |

---

## 10. Eligibility and governance implications

| Field | Decision |
|-------|----------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | **Unchanged** |
| **Placebo promotion** | **Not warranted** from this archive |
| **Recommended governed role** | **Expert-review null reference / diagnostic** on **single-treated** panels with mandatory **`placebo_band` labeling** |
| **Default recovery DGP** | **Not supported** until multi-treated placebo implemented |
| **DEF-020** | Ready for disposition update in Phase 15 governance decision |

**Principle:** Placebo OC is **archived**; trust role requires **Phase 15 governance decision** — not automatic from this document alone.

---

## 11. Non-claims

This archive **does not**:

- Modify placebo implementation or `placebo_strict` defaults  
- Add Placebo to nominal calibration eligibility  
- Promote Placebo as lift detector  
- Claim default multi-geo recovery DGP support  
- Conflate placebo bands with jackknife/bootstrap CIs  
- Change maturity labels or release gates  

This archive **does**:

- Characterize null/positive OC on single-treated geometry  
- Document multi-treated failure surface  
- Confirm `placebo_band` export semantics on success path  
- Inform Phase 15 governance decision and Track B trust vocabulary  

---

*Evidence archive INV-029-001 / Phase 15. Registry unchanged. Next: [`PHASE15_GOVERNANCE_DECISION_001.md`](PHASE15_GOVERNANCE_DECISION_001.md) (planned).*
