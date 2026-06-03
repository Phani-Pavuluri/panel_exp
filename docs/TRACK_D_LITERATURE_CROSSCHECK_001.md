# Track D — literature cross-check 001

**Document ID:** TRACK-D-LITERATURE-CROSSCHECK-001  
**Status:** architecture design — D0b deliverable  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1 (current implementation)  

**Related:** [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) · [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) · [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md)

This document defines **literature grounding requirements** for Track D. It converts canonical research into **audit checklists** — not paper summaries. **No method promotion** from literature alone; OC and implementation audits required.

---

## 1. Purpose

For each method in [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md), maintain a **literature cross-check record** answering:

> Does our **implemented variant** match what the literature claims — and what Track B says we measure?

### Decision outcomes (per method)

| Decision | Meaning |
|----------|---------|
| **aligned** | Implementation matches literature within stated assumptions |
| **aligned_with_deviation** | Documented, governed deviation |
| **implementation_bug** | Code contradicts literature and intent |
| **unsupported_claim** | Product claim exceeds literature + OC |
| **needs_characterization** | Literature OK in theory; our OC missing |
| **restricted** | Usable with explicit boundary |
| **deprecated** | Do not use |

### Non-goals

- No blind copying from papers  
- No promotion because a paper exists  
- No assuming paper-valid inference transfers to geo/media settings  
- No calibration eligibility changes without OC (Track A/B governance)

---

## 2. Record template

```yaml
method_id: EST-001                    # inventory row ID
method_name: SCM
implemented_variant: SyntheticControl + UnitJackKnife
canonical_papers:
  - "Abadie, Diamond, Hainmueller (2015) — comparative politics / SCM"
  - "Abadie (2021) — Using Synthetic Controls"
assumptions:
  - donor pool excludes treated units
  - convex weights sum to one (CVXPY path)
  - pre-period used for fit; post for effect
estimand_literature: ATT on treated unit / aggregate
design_setting: case study / comparative
required_diagnostics:
  - pre-period fit
  - donor weight concentration
  - placebo or permutation where claimed
inference_semantics_literature: permutation / placebo — not always classical CI
known_limitations:
  - few treated units
  - extrapolation risk
implementation_checklist:
  - item: treated excluded from donors
    status: pass | fail | unknown
  - item: post-period not in weight fitting
    status: pass | fail | unknown
gap_vs_literature: ""
decision: needs_characterization
track_b_mapping:
  measurement_instrument_id: geo.synthetic_control.unit_jackknife...
  estimand_id: geo.relative_att_post.pooled_path.relative
  interval_semantics: confidence_interval
def_refs: [DEF-013, DEF-015]
next_action: D2 estimator math audit
```

---

## 3. Canonical paper families and audit checks

### 3.1 Synthetic control (SCM)

**Papers:** Abadie, Diamond, Hainmueller; Abadie synthetic control guidance; Abadie & Gardeazabal.

| Audit check | Pass criterion |
|-------------|----------------|
| Donor-only controls | Treated units not in donor pool |
| Weight constraints | Non-negative + sum-to-one where required |
| Pre-period fit | Reported; post excluded from fitting |
| Post-period inference | Effect vs counterfactual clearly separated |
| Placebo inference | Not labeled as standard CI (Track B F3) |
| Multi-treated | Explicit estimand if multiple treated |

**Platform mapping:** EST-001, EST-002, INF-002, INF-006, GOLD-001, GOLD-005.

---

### 3.2 Augmented SCM (AugSynth / ASCM)

**Papers:** Ben-Michael, Feller, Rothstein augmented SC.

| Audit check | Pass criterion |
|-------------|----------------|
| Augmentation role | Bias correction vs ridge mislabel |
| SCM vs outcome model | Components separated |
| Poor pre-fit handling | Documented failure modes |
| Spillover | DEF-004 sensitivity |
| Uncertainty | Point-only vs JK claims bounded |

**Platform mapping:** EST-003, EST-004, INF-002, Phase 14 archive.

---

### 3.3 TBR / matched markets

**Papers:** Google TBR / matched-market experiment references.

| Audit check | Pass criterion |
|-------------|----------------|
| Design–analysis alignment | Markets paired before outcomes |
| Cumulative vs relative | Estimand explicit (INV-003) |
| Regression assumptions | Residual / variance review |
| Geographic grouping | Correct indexing |

**Platform mapping:** EST-005, EST-006, DES-001, MAT-001.

---

### 3.4 Generalized SCM / ridge balancing

**Papers:** Doudchenko & Imbens.

| Audit check | Pass criterion |
|-------------|----------------|
| Intercept handling | Documented |
| Negative weights | Only where allowed |
| Regularization | TBRRidge path matches intent |
| DID / regression / SCM relationship | Not conflated |

**Platform mapping:** EST-006, INF-004, INF-005.

---

### 3.5 Synthetic DID (SDID)

**Papers:** Arkhangelsky, Athey, Hirshberg, Imbens, Wager.

| Audit check | Pass criterion |
|-------------|----------------|
| Unit + time weights | Both identified |
| Treatment timing | Staggered handling if claimed |
| ATT vs cumulative vs relative | Registry IDs distinct |
| Inference | Matches SDID assumptions |

**Platform mapping:** EST-011, DEF-005.

---

### 3.6 Bayesian structural time series (CausalImpact-style)

**Papers:** Brodersen et al.

| Audit check | Pass criterion |
|-------------|----------------|
| State-space form | Matches implementation |
| Covariate restrictions | Documented |
| Posterior intervals | `credible_interval` semantics |
| Counterfactual prediction | Pre/post separation |

**Platform mapping:** EST-008, INF-008 (registry Bayesian ≠ full MCMC).

---

### 3.7 DID / panel TWFE

**Papers:** Standard DID; caution on TWFE staggered (literature debate).

| Audit check | Pass criterion |
|-------------|----------------|
| Parallel trends | Pretrend diagnostic |
| Relative ATT intervals | **Not** supported (DEF-003) |
| Cumulative intervals | Separate estimand ID |

**Platform mapping:** EST-010, INF-010, GOLD-008.

---

### 3.8 Additional families (expand in D0b execution)

| Family | Topics | Track D package |
|--------|--------|-----------------|
| Conformal | Exchangeability, splits | D3 |
| Randomization / rerandomization | Design validity | D1 |
| Geo experiment design | Cluster interference | D1, D6 |
| Power / MDE | Frequentist vs simulation | D4 |
| MMM calibration | Transform + holdout | DEF-012, Track C |

---

## 4. Cross-check index (initial — to be filled in D1–D3)

| Inventory ID | Literature family | Decision (initial) | Owner |
|--------------|-------------------|--------------------|-------|
| EST-001 | SCM | needs_characterization | D2 |
| EST-004 | AugSynth | needs_characterization | D2 |
| EST-006 | TBR/ridge | needs_characterization | D2 |
| EST-010 | DID | aligned_with_deviation | D2 (DEF-003) |
| EST-011 | SDID | needs_characterization | D2 |
| INF-002 | Jackknife | aligned_with_deviation | **D3** ✅ (null monitor; INV-D3-001 LOO target) |
| INF-004 | K-fold (TBR) | needs_characterization | **D3** ✅ restricted |
| INF-005 | Block bootstrap | needs_characterization | **D3** ✅ restricted |
| INF-006 | Placebo | aligned_with_deviation | **D3** ✅ (Phase 15; diagnostic) |
| INF-010 | DID bootstrap | aligned_with_deviation | **D3** ✅ (DEF-003 cumulative interval) |
| DES-001 | Matched markets | needs_characterization | D1 ✅ → D0b YAML + D5 OC |
| DES-010 | Rerandomization | needs_characterization | D1 ✅ → D5-DES-010a |
| DES-011 | Constraints | aligned (pending D0b record) | D1 |
| DES-013 | Design validation | aligned_with_deviation | D1 |
| MAT-001 | Greedy market match | needs_characterization | D1 (alias DES-001) |

---

## 5. Relationship to Track B

| Literature finding | Track B update |
|--------------------|----------------|
| New estimand discovered | Estimand Registry entry |
| New instrument variant | Measurement Instrument Catalog |
| OC completes | CalibrationSignal version |
| Claim boundary | TrustReport `usage_boundary` |
| Testable rule | B5 golden fixture |

---

## 6. Success criterion (D0b)

**D0b succeeds when:**

1. Every **priority** inventory row (governed + restricted instruments) has a literature record stub.  
2. Audit checklists exist for **six canonical families** (§3.1–3.7).  
3. **Decision taxonomy** is defined and linked to inventory status.  
4. No paper is cited as justification for **decision_eligible** without D5 OC.

---

*Planning artifact TRACK-D-LITERATURE-CROSSCHECK-001. D0b template complete. Per-method records filled during D1–D3 audits.*
