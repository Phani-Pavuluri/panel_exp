# INV-D1-001 — Pre-period matching leakage (design layer)

**Investigation ID:** INV-D1-001  
**Track:** D (research / robustness)  
**Status:** **investigating** → characterization complete; **restrict** recommended  
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

**Automated recommendation:** `restrict`  
**Disposition for D1-FIND-001:** `restricted` (research lane — not production code change yet)

---

## 5. Governance disposition

| Field | Value |
|-------|--------|
| **Current disposition** | `restricted` (inventory: DES-001 / MAT-001 remain `characterization_required`) |
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

## 6. Proposed fix path (not implemented)

**Separate change proposal** after governance review:

1. In `run_geo_experiment_design`, pass `pre_treatment_period=TimePeriod(0, train_length-1)` **or** slice `panel_data` to pre columns before `assign` when `train_length` is defined on geo orchestrator.
2. Extend `greedy_match_markets` to honor `pre_treatment_period` by slicing `wide` before `sales_df` (defense in depth).
3. Add DG-007 check: warn/fail if matching window includes experiment-period columns when spec declares pre-period end.
4. Re-run D5-DES-001a — target mean Jaccard > 0.95 vs explicit pre-only reference.

**Migration:** Existing studies that ran full-panel matching should be flagged in evidence metadata (research note only until product consumer exists).

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
