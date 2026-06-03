# INV-D1-001 — Pre-period matching leakage (design layer)

**Investigation ID:** INV-D1-001  
**Track:** D (research / robustness)  
**Status:** **fix applied** (`61a174f`) — D5-DES-001a re-run **passed** (Jaccard 1.0)  
**Opened:** 2026-05-28  
**Source finding:** [D1-FIND-001](../TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) §8  
**Characterization:** [D5_DES_001a_results.json](../track_d/archives/D5_DES_001a_results.json)  
**Code (read-only):** `panel_exp/validation/track_d_d5_des_001a.py` · `tests/track_d/test_d5_des_001a_pre_period_matching.py`

**Lane:** Research only — **no** production assignment, estimator, TrustReport, eligibility, maturity, or release-gate changes in this investigation.

---

## 1. Problem statement

The default GeoX design pipeline may allow **look-ahead** in market matching: `run_geo_experiment_design` invokes `assign(..., treatment_period=None, pre_treatment_period=None)`, while `greedy_match_markets` balances test/control using **all columns** in `panel_data.wide_data` (`sales_df = wide.T`). If `wide_data` includes post-treatment periods, matching optimizes correlation on outcomes that would not be observable at design time.

**Causal/statistical risk:** Assignment correlates with post-treatment noise or effects → biased simple contrasts, inflated post-hoc balance, and invalid design–analysis timing even when Track B adapter export is `complete`.

---

## 2. Affected pathways

| Layer | Location | Role |
|-------|----------|------|
| Geo orchestrator | `panel_exp/design/geo_runner.py` | Passes null periods to `assign` |
| Design API | `panel_exp/design/geo_experiment_design.py` | `create_design()` → `Rerandomization` → base randomizer |
| Matching | `panel_exp/design/assign.py` | `greedy_match_markets.assign` uses full `wide` |
| Spec contract | `spec_from_geo_design` | Records `pre_period` / `experiment_period` but does not slice matching input |
| Validation | `panel_exp/design/validation.py` | DG-007 does **not** verify pre-period-only matching |

**Out of scope for this INV:** SCM donor pools (MAT-004/005) → D2.

---

## 3. Hypotheses

| ID | Hypothesis | D5-DES-001a result |
|----|------------|-------------------|
| H1 | Full-panel matching assigns different test sets than pre-only | **Supported** — mean Jaccard **0.27** (n=120) |
| H2 | Full-panel matching increases \|corr(test, post mean)\| | **Weak** — mean abs diff **0.018** |
| H3 | Full-panel matching inflates post-period balance | **Not observed** — post balance corr similar |
| H4 | Null DGP yields high spurious post correlation | **Partial** — 14% replicates with \|ρ\|>0.3 (full panel, no post shift) |

---

## 4. D5-DES-001a characterization summary

**Artifact:** [`docs/track_d/archives/D5_DES_001a_results.json`](../track_d/archives/D5_DES_001a_results.json)  
**Config:** 24 units · 50 pre + 20 post periods · 120 MC replicates · post unit shift SD=12 (stress) · `greedy_match_markets` corr objective

| Metric | Full panel | Pre-period only | Interpretation |
|--------|------------|-----------------|----------------|
| Test-set Jaccard vs paired run | — | mean **0.27** | Assignments **materially differ** |
| \|corr(test, unit post mean)\| | mean 0.18 | mean 0.17 | Small gap; not primary signal |
| Post-period balance corr | 0.99 | 0.99 | Both high; not discriminative |
| Pre SMD (mean) | 0.47 | 0.36 | Full panel slightly worse pre balance |
| Null \|ρ\|>0.3 rate | 14% | — | Non-trivial spurious association |

**Post-fix D5-DES-001a (commit `61a174f`+):** `test_set_jaccard_fixed_vs_pre_only` mean **1.00** · recommendation **`accepted_deviation`**

**Pre-fix recommendation:** `restrict` (baseline full-panel vs pre-only Jaccard 0.27)

**Disposition for D1-FIND-001:** `characterization_required` (fix verified; promotion still forbidden)

---

## 5. Governance disposition

| Field | Value |
|-------|--------|
| **Current disposition** | `characterization_required` (fix in `61a174f`; D5 re-run confirms pre-period boundary) |
| **TrustReport** | Unchanged — do not infer design validity from export alone |
| **Promotion** | **Forbidden** until fix + re-run OC |
| **MMM / planning** | **No feed** |

### Decision tree (post D5-DES-001a)

| Outcome | Condition | Action |
|---------|-----------|--------|
| **restrict** ✅ | Jaccard < 0.75 | Document boundary; propose geo runner pre-period slice **separately** |
| fix | Leakage signal + assignment change | Code change + migration notes |
| accepted_deviation | Jaccard > 0.92 and small ρ gap | Document contract only |
| continue_investigation | Ambiguous | More DGPs / production panels |

---

## 6. Fix implemented (`61a174f`)

1. **`geo_runner`:** passes `pre_treatment_period=TimePeriod(0, train_length)` when `train_length > 0`.
2. **`greedy_match_markets`:** slices `wide` via `slice_wide_to_time_period` when `pre_treatment_period` is set.
3. **`Rerandomization`:** imbalance evaluation uses pre-period panel; `_eval_period_clipped` maps period labels to sliced columns.
4. **Shared helper:** `panel_exp/design/period_slice.py`.

**D5-DES-001a post-fix:** mean Jaccard (fixed vs pre-only) **1.00** — see updated [`D5_DES_001a_results.json`](../track_d/archives/D5_DES_001a_results.json).

**Migration (research):** Historical runs that used full-panel matching before this fix may differ; flag in study metadata when replaying old evidence.

---

## 7. Required follow-up

| Priority | Item | Owner |
|----------|------|-------|
| P0 | ADR / fix PR for geo runner pre-period boundary | Engineering (post-approval) |
| P1 | Re-run D5-DES-001a after fix | Track D |
| P1 | Update D0b DES-001 literature record with deviation or alignment | Track D |
| P2 | Production-like panel replay (real KPI shapes) | Track D |
| P3 | Start D2 estimator audit | After fix or explicit accept |

---

## 8. Evidence index

| Artifact | Path |
|----------|------|
| D1 audit | [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](../TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) |
| D5 results | [`track_d/archives/D5_DES_001a_results.json`](../track_d/archives/D5_DES_001a_results.json) |
| Simulation module | `panel_exp/validation/track_d_d5_des_001a.py` |
| Tests | `tests/track_d/test_d5_des_001a_pre_period_matching.py` |

---

*INV-D1-001 v1.0.0 — research lane — 2026-05-28*
