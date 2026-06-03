# Track D — Conceptual validity audit 001

**Document ID:** TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001  
**Type:** Research-lane audit / ADR (literature & method fidelity)  
**Status:** **complete (v1)** — findings are **not** production-promotion evidence  
**Date:** 2026-06-02  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ post `D5-INST-COMBO-AUDIT-001`  
**Lane:** Research / robustness per [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D  

**Structured artifact:** [`track_d/archives/TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001_results.json`](track_d/archives/TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001_results.json)  
**Harness (read-only generator):** `panel_exp/validation/track_d_conceptual_validity_audit_001.py`

---

## ADR decision record

| Field | Value |
|-------|--------|
| **Context** | D5 instrument batteries (PLACEBO, AUDIT, AUGSYNTH, COMBO, TBRRIDGE, etc.) establish **callability, geometry, and synthetic OC**. They do **not** establish that implementations match their research basis or support MMM-grade claims. AUDIT-010 (MMM readiness/gap) must run on a **conceptual** foundation, not inventory alone. |
| **Decision** | Document method-by-method conceptual validity: research basis, assumptions, implementation behavior, deviations, geometry, inference semantics, TrustReport vs CalibrationSignal boundaries, forbidden claims, and production blockers. **No** production code changes in this package. |
| **Consequences** | AUDIT-010 inputs are explicit; literature cross-check rows gain audit IDs; zero methods are promoted to production/MMM on this audit alone. |
| **Alternatives rejected** | Treating D5 synthetic pass as paper fidelity; treating class names (e.g. `TBR`, `Bayesian`) as proof of method family; expanding `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` from documentation. |

---

## 1. Executive summary

**Overall verdict (research lane):** `continue_with_restricted_diagnostics_only`

| Category | Methods | Conceptual stance |
|----------|---------|-------------------|
| **Faithful enough (with governed scope)** | SCM default pre-fit + UnitJackKnife | **Null-monitor** aligned with leave-one-donor diagnostic literature; **not** lift detection |
| **Faithful as diagnostic comparator** | AugSynthCVXPY point/JK; SCM Placebo (single-treated) | Runnable and characterized; spillover/estimand limits documented |
| **Faithful only on narrow geometry** | Class **TBR** (aggregate 1×1); **TBRRidge** (unit / geo-power agg2) | **Different research objects** — must not conflate |
| **Restricted / approximate** | TBRRidge Kfold/BRB; DID bootstrap; Kfold multi-treated aggregation | Usable for diagnostics; not CalibrationSignal |
| **Blocking deviations** | `full_model=True` SCM/AugSynth; registry `Bayesian` vs BayesianTBR MCMC; recovery_runner TBR→TBRRidge; DID relative ATT CI | Fix or block before MMM |
| **Research only** | BayesianTBR (native MCMC); TROP | No production instrument card |

**Production-ready count:** **0** — no estimator×inference path is cleared for MMM ingress by this audit alone.

**Calibration eligibility:** **Unchanged** — `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` for **null-monitor** role only ([`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md)).

**Critical rule:** A passing D5 battery proves **operating characteristics under a synthetic DGP**, not conceptual validity under the cited papers.

---

## 2. Scope and non-goals

### In scope

All estimator and inference families listed in [`D5_INST_AUDIT_001`](track_d/D5_INST_AUDIT_001_REPORT.md) and [`D5_INST_COMBO_AUDIT_001`](track_d/D5_INST_COMBO_AUDIT_001_REPORT.md), audited against:

- [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md)
- [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md)
- [`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md)
- Phase 14/15 characterization and D5-INST-* reports

### Out of scope (explicit)

- Production code, estimator, inference, TrustReport, Track B schema, or MMM ingestion changes  
- Promotion or CalibrationSignal expansion  
- Full Cartesian OC of all 192 matrix cells  
- AUDIT-010 execution (this audit is a **prerequisite**, not AUDIT-010)

---

## 3. Audit dimensions (template)

Each method record in the JSON artifact answers:

1. Research basis / intended method family  
2. Required assumptions  
3. Implementation behavior in this repo  
4. Deviations from research method  
5. Deviation verdict: **acceptable** | **restricted** | **blocking** | **research_only**  
6. Supported estimand (Track B where applicable)  
7. Supported data geometry (see §4 legend)  
8. Inference semantics  
9. TrustReport vs CalibrationSignal support  
10. Forbidden claims  
11. Required fixes before production readiness  

---

## 4. Geometry legend

| Token | Meaning |
|-------|---------|
| **supported** | Conceptually coherent for stated estimand when diagnostics pass |
| **restricted** | May run; estimand/geometry bridge required in cards |
| **blocked** | Implementation or theory blocks governed use |
| **invalid** | Wrong geometry for method family (e.g. JK on 2-row agg) |
| **research** | Research lane only |
| **not_estimator_scope** | Design layer (supergeo, trim) — not estimator claim |

---

## 5. Estimator family audits

### 5.1 SCM (`SyntheticControl` / `SyntheticControlCVXPY`) — `CV-EST-SCM`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Abadie–Diamond–Hainmueller synthetic control: convex donor weights on pre-treatment outcomes, counterfactual for treated unit(s). |
| 2 | **Assumptions** | Donors approximate treated pre-trends; no structural break at treatment; treated excluded from donors; spillover not modeled. |
| 3 | **Implementation** | Default `full_model=False`: pre-period fit via `split_control_test_units`; CVXPY/OSQP simplex; treated dropped from `control_series`. |
| 4 | **Deviations** | (a) `full_model=True` uses post-treatment columns in fit — **parallel to pre-D1 leakage at estimator layer** (D2 INV-D2-001). (b) Multi-treated panels run per-unit paths without pooled ATT theory bridge. |
| 5 | **Deviation verdict** | (a) **blocking** for production exports; (b) **restricted** for multi-treated/MCELL. |
| 6 | **Estimand** | `geo.relative_att_post.pooled_path.relative` — path effect \(y - \hat y\) on treated unit. |
| 7 | **Geometry** | single_treated: supported · multi_treated: restricted per-unit · multi_cell: restricted per-cell · aggregate 2-row: invalid for JK · supergeo/trim: design scope |
| 8 | **Inference** | Point via estimator; uncertainty via separate modes (JK, placebo, etc.). |
| 9 | **Trust / Calibration** | TrustReport: **diagnostic only** · CalibrationSignal: **neither** (JK path: null_monitor_only when instrument card passes) |
| 10 | **Forbidden claims** | Universal SCM validity; lift from point path alone; JK as MDE planner |
| 11 | **Production fixes** | Govern or block `full_model` in exports; MCELL per-cell discipline |

**Literature cross-check:** `aligned_with_deviation` (D0b EST-001/002).

---

### 5.2 AugSynth / AugSynthCVXPY — `CV-EST-AUGSYNTH`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Augmented SCM (Ben-Michael et al.): SCM leg + outcome model on residuals. |
| 2 | **Assumptions** | SCM pre-fit valid; ridge (or chosen) residual model adequate; `min_donors` / correlation filter appropriate. |
| 3 | **Implementation** | Inner `SyntheticControlCVXPY` + ridge on residualized outcomes; inherits `full_model` risk from inner SCM. |
| 4 | **Deviations** | Phase 14 spillover DGP bias (~−0.034 vs 0.10 truth) — interference not modeled. |
| 5 | **Deviation verdict** | **restricted** for contaminated geo DGPs |
| 6 | **Estimand** | Same relative ATT path family as SCM; JK mirrors SCM null conservatism |
| 7 | **Geometry** | Same as SCM; aggregate JK invalid |
| 8 | **Inference** | JK: diagnostic null-monitor only (D5-INST-AUGSYNTH-001) |
| 9 | **Trust / Calibration** | **diagnostic only** / **neither** CalibrationSignal |
| 10 | **Forbidden claims** | CalibrationSignal; JK as lift detector; generalizing default-battery recovery to spillover geo |
| 11 | **Production fixes** | Spillover on instrument card; Kfold combo unvalidated (COMBO: valid_candidate, needs OC) |

**Literature cross-check:** `aligned_with_deviation`.

---

### 5.3 TBR (class `TBR`, not TBRRidge) — `CV-EST-TBR`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Google geo experiments TBR: regression of **one** treated aggregate on **one** control aggregate using pre-period fit. |
| 2 | **Assumptions** | Exactly one treated and one control series; stable linear relationship pre/post. |
| 3 | **Implementation** | `tbr.py` asserts `len(treated_units)==1` and `num_control_units==1`. **Geo PowerAnalysis uses TBRRidge on 2-row agg**, not class TBR. |
| 4 | **Deviations** | `recovery_runner` may label TBR while factory uses TBRRidge — **audit trail conflation** (blocking for governed reporting). |
| 5 | **Deviation verdict** | **blocking** until harness/doc fix; geometry otherwise **aligned on aggregate only** |
| 6 | **Estimand** | Aggregate level shift — **not** unit SCM ATT |
| 7 | **Geometry** | **Only** `aggregate_test_control` (1 treated + 1 control row) |
| 8 | **Inference** | Registry JK/Kfold on 1×1 panel atypical vs paper; COMBO lists valid_candidate on aggregate |
| 9 | **Trust / Calibration** | **neither** until D5-INST-TBR-001 |
| 10 | **Forbidden claims** | Equating TBR with TBRRidge or SCM unit readout; unit-level multi-market TBR |
| 11 | **Production fixes** | **D5-INST-TBR-001**; fix recovery_runner factory |

---

### 5.4 TBRRidge — `CV-EST-TBRRIDGE`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | TBR family with ridge across **multiple** control unit series; geo product extension for panels and power MDE. |
| 2 | **Assumptions** | Comparable controls after normalization; ridge stabilizes high-dimensional control fit. |
| 3 | **Implementation** | Multi-control unit paths; also 2-row aggregate for geo power (001a/001c). |
| 4 | **Deviations** | Point scale and null behavior differ from SCM+JK (D5-TBRRIDGE); agg2 MDE is **optimistic_proxy** vs SCM detection MDE. |
| 5 | **Deviation verdict** | **restricted** — not interchangeable with SCM+JK |
| 6 | **Estimand** | Unit path effect **or** geo-power proxy — declare which |
| 7 | **Geometry** | single/multi treated: supported with caveats · agg2: geo power only · supergeo/trim: invalid |
| 8 | **Inference** | Kfold/BRB/JK each need separate validity row (D3/D5) |
| 9 | **Trust / Calibration** | diagnostic TrustReport only · **no** CalibrationSignal |
| 10 | **Forbidden claims** | Platform MDE from Kfold on agg2; null FPR match implies same estimand as SCM+JK |
| 11 | **Production fixes** | Estimand bridge doc; TBRRidge-002 for unconstrained combos |

---

### 5.5 BayesianTBR — `CV-EST-BAYESIANTBR`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Bayesian regression / horseshoe; MCMC (NUTS) posterior. |
| 2 | **Assumptions** | Priors, convergence, likelihood match DGP. |
| 3 | **Implementation** | `fit_model` runs NUTS; registry `Bayesian` mode uses JAX quantiles on `predict()` — **not** MCMC posterior (INV-015). |
| 4 | **Deviations** | Registry shortcut vs paper MCMC — **blocking** for “BayesianTBR” product claims |
| 5 | **Deviation verdict** | **research_only** / **blocking** for registry path |
| 6–11 | | No Track B governed estimand; **forbidden** TrustReport/CalibrationSignal; bridge or remove registry Bayesian |

---

### 5.6 DID — `CV-EST-DID`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | TWFE DID; cluster/block bootstrap (native, not registry). |
| 2 | **Assumptions** | Parallel trends; simultaneous adoption; correct FE spec. |
| 3 | **Implementation** | TWFE + moving block bootstrap; cumulative ATT intervals (DEF-003). |
| 4 | **Deviations** | Relative ATT post CI **unsupported** — estimand mismatch with SCM path CI |
| 5 | **Deviation verdict** | **blocking** for cross-method interval compare |
| 6 | **Estimand** | `cumulative_att` / mean post ATT — not SCM relative ATT |
| 7 | **Geometry** | Pooled single/multi treated; not aggregate 2-row SCM tensor |
| 8 | **Inference** | `bootstrap_approximation` (estimator-embedded INF-010) |
| 9 | **Trust / Calibration** | diagnostic only · **neither** CalibrationSignal |
| 10 | **Forbidden claims** | Relative ATT lift vs SCM+JK; CalibrationSignal without bridge |
| 11 | **Production fixes** | Pretrend contract in exports |

---

### 5.7 TROP — `CV-EST-TROP`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Triply robust panel estimators (low-rank + penalties). |
| 2 | **Implementation** | Research module; validation runner skipped; multi-treated display aggregation. |
| 3–5 | | **research_only** — **blocking** for production geo instrument |
| 6–11 | | Full D5 OC + Track B instrument if ever promoted |

---

## 6. Inference family audits

### 6.1 Point estimate — `CV-INF-POINT` (implicit)

| Item | Assessment |
|------|------------|
| **Semantics** | Estimator output only — no uncertainty layer |
| **Trust / Calibration** | Point may feed TrustReport **diagnostics**; never CalibrationSignal alone |
| **Forbidden** | Decision-grade lift without governed interval mode |

---

### 6.2 UnitJackKnife / JKP — `CV-INF-JK`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Leave-one-donor stability / permutation-style inference for SCM counterfactuals (Abadie et al. literature). |
| 2 | **Assumptions** | ≥2 donors; LOO refit stable; exchangeability for **diagnostic** null interpretation. |
| 3 | **Implementation** | LOO on controls; post INV-D3-001 correct LOO target; batteries show FPR≈0, power≈0 (conservative null monitor). |
| 4 | **Deviations** | Not a classical sampling CI for ATT — **acceptable** under null-monitor role |
| 5 | **Geometry** | single_treated supported; multi_treated/MCELL per-unit restricted; aggregate **invalid** |
| 6 | **Inference semantics** | `diagnostic_interval_only` |
| 7 | **Trust / Calibration** | TrustReport diagnostic · **CalibrationSignal: null_monitor_only for SCM_UnitJackKnife only** |
| 8 | **Forbidden** | Lift detection; MMM planning MDE |
| 9 | **Fixes** | Keep eligibility registry narrow |

---

### 6.3 Placebo — `CV-INF-PLACEBO`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Placebo-in-space: treatment on control units; null for test statistic. |
| 2 | **Assumptions** | **Single treated unit**; ≥5 donors (soft); ≥2 hard minimum. |
| 3 | **Implementation** | `placebo_band` typing; TBR class blocked in `impl.py`; inversion CI exists but governed as band not ATT CI (E-ESTIMAND-004). |
| 4 | **Deviations** | Inversion CI can be misread as ATT CI — **restricted** |
| 5 | **Geometry** | single_treated: supported · multi_treated/multi_cell: **blocked** (PLACEBO-001) |
| 6 | **Semantics** | `placebo_randomization_uncertainty` |
| 7 | **Trust / Calibration** | diagnostic only · **neither** CalibrationSignal |
| 8 | **Forbidden** | Lift evidence; CI comparable to JK |
| 9 | **OC note** | Synthetic OC ≠ paper fidelity; geometry block is conceptually correct |

---

### 6.4 KFold — `CV-INF-KFOLD`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | SC cross-validation / bias correction (Chernozhukov et al. family). |
| 2 | **Implementation** | Time-horizon folds; multi-treated residual aggregation in TBRRidge path — document geometry. |
| 3 | **Deviation verdict** | **restricted** for multi-treated and geo-power agg2 |
| 4 | **Semantics** | `sampling_uncertainty_approximation` (CI on path — check estimand per estimator) |
| 5 | **Trust / Calibration** | diagnostic · **neither** CalibrationSignal |
| 6 | **COMBO** | AugSynthCVXPY+Kfold: valid_candidate — **needs OC before promotion** |

---

### 6.5 BlockResidualBootstrap (BRB) — `CV-INF-BRB`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Block bootstrap for dependent time series. |
| 2 | **Implementation** | Cumulative effect emphasis for multi-unit; lower `n_bootstrap` default for SCM. |
| 3 | **Verdict** | **restricted** on TBRRidge geo paths (D5-TBRRIDGE) |
| 4 | **Semantics** | `bootstrap_approximation` |
| 5 | **Trust / Calibration** | diagnostic · **neither** CalibrationSignal |

---

### 6.6 Bootstrap (registry generic)

Registry `bootstrap` routes through mode implementations tied to estimators — treat as **estimator-dependent**. No standalone production card. Same governance as BRB/Kfold parent estimator.

---

### 6.7 Conformal — `CV-INF-CONFORMAL`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Research basis** | Distribution-free predictive intervals under exchangeability. |
| 2 | **Assumptions** | Exchangeable scores — **likely violated** in geo panels. |
| 3 | **Implementation** | Registry mode; grid null search — diagnostic tier. |
| 4 | **Verdict** | **needs_characterization** — not production-ready |
| 5 | **Semantics** | `conformal_interval` |
| 6 | **Trust / Calibration** | **neither** |
| 7 | **Forbidden** | Decision-grade geo lift |

---

### 6.8 Registry Bayesian (JAX) — `CV-INF-BAYESIAN-REG`

| # | Item | Assessment |
|---|------|------------|
| 1 | **Claimed basis** | MCMC posterior intervals |
| 3 | **Implementation** | Quantiles of `predict()` after single fit — **not** NUTS posterior |
| 4 | **Verdict** | **blocking** / `implementation_bug_for_claimed_family` (INV-015) |
| 5 | **Forbidden** | Any BayesianTBR paper claim via registry mode |

---

### 6.9 TimeSeriesKfold

Registry variant — same conceptual caveats as KFold; **needs_characterization** for geo production. Not calibration-eligible.

---

## 7. Cross-cutting findings

| ID | Finding |
|----|---------|
| **CV-FIND-001** | Synthetic OC pass does **not** establish paper fidelity — only code + geometry + estimand alignment audits do. |
| **CV-FIND-002** | **SCM+JK** is the only calibration-eligible config and is conceptually a **null monitor**, not lift detection. |
| **CV-FIND-003** | **Placebo** (`placebo_band`) and **JK** (`confidence_interval` diagnostic) answer different estimands — must not merge in TrustReport claims. |
| **CV-FIND-004** | **TBR** (aggregate 1×1) ≠ **TBRRidge** (unit / geo power) — critical for AUDIT-010 and D5-INST-TBR-001. |
| **CV-FIND-005** | **COMBO-AUDIT-001** `valid_candidate` means interface+geometry **plausible**, not conceptually validated for MMM. |
| **CV-FIND-006** | **Zero** paths are production/MMM-ready without AUDIT-010 gap closure and listed blocker fixes. |

---

## 8. Summary matrix (estimator × conceptual stance)

| Estimator | Fidelity | MMM / CalibrationSignal | AUDIT-010 gate |
|-----------|----------|-------------------------|----------------|
| SCM (default pre-fit) | aligned_with_deviation | null-monitor only (via JK) | full_model guard required |
| AugSynthCVXPY | aligned_with_deviation | blocked | diagnostic comparator OK |
| TBR (class) | aggregate-only | blocked | TBR-001 required |
| TBRRidge | aligned_with_deviation | blocked | restricted diagnostic |
| BayesianTBR | research_only | blocked | INV-015 |
| DID | aligned_with_deviation | blocked | DEF-003 interval policy |
| TROP | research_only | blocked | — |

---

## 9. AUDIT-010 inputs (MMM readiness/gap — not promotion)

**Faithful enough for TrustReport diagnostics (with cards):**

- SCM + UnitJackKnife null-monitor (single_treated / per-cell MCELL)
- SCM + Placebo (single_treated only)
- AugSynthCVXPY point + JK (diagnostic comparator)

**Blocked from MMM without fix/bridge:**

- Registry `Bayesian` as BayesianTBR posterior
- DID relative ATT interval vs SCM CI
- TBRRidge Kfold as platform MDE / CalibrationSignal
- TBR vs TBRRidge conflation in harness/docs
- `full_model=True` SCM/AugSynth production exports
- Placebo or JK on multi-treated default assignment
- Any method with only `valid_candidate` COMBO status and no D5 OC

**Required sequence before MMM:**

1. ~~D5-INST-COMBO-AUDIT-001~~ ✅  
2. **TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001** ✅ (this document)  
3. **D5-INST-TBR-001** (true aggregate TBR)  
4. **AUDIT-010** — readiness/gap audit (block invalid combos; document bridges)

---

## 10. Binding documents updated

| Document | Change |
|----------|--------|
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Conceptual validity checkpoint; AUDIT-010 prerequisite |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001 checkpoint |
| [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) | Conceptual validity column / next actions |
| [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) | Part C3 conceptual validity cross-links |

---

## 11. Stop condition (met)

The project has a **method-by-method conceptual validity audit** stating which implementations are **faithful within scope**, which are **approximate diagnostics**, which are **restricted**, and which require **fixes or bridges** before production/MMM readiness — without conflating synthetic batteries with research-paper fidelity.
