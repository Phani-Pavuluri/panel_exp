# METHOD-LITERATURE-ALIGNMENT-001

**Document ID:** METHOD-LITERATURE-ALIGNMENT-001  
**Type:** Layer 2 literature alignment register — **docs-only**  
**Status:** **complete** (human register + JSON generator)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) Layer 2

**Machine-readable register:** [`track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json`](track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json) (24 families; regenerate via `python -m panel_exp.validation.method_literature_alignment_001`)

**Generator:** [`panel_exp/validation/method_literature_alignment_001.py`](../panel_exp/validation/method_literature_alignment_001.py)

**Primary inputs:** [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) · [`track_d/archives/METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json)

**Evidence inputs (not final authority):** [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) · Track D D1–D3 audits · [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · AugSynth fidelity / JK / Conformal reports

**Guardrails:** No trust roles · no promotion/demotion · no behavior change · no OC in this artifact

---

## 1. Purpose

Define **what correctness means** for each **code-derived method family** before implementation validation (Layer 3) and statistical OC (Layer 4).

This register compares **implemented** components from [`METHOD_CODE_INVENTORY_001`](METHOD_CODE_INVENTORY_001.md) to **canonical literature identities** — estimands, geometries, assumptions, valid inference companions, diagnostics, and known failure modes.

**This artifact does not:**

- Prove final implementation or statistical correctness  
- Assign primary / secondary / directional evidence roles  
- Promote or demote methods  
- Replace Layer 3–5 evidence  

**This artifact does:**

- State literature-prescribed targets per family  
- Label repo variants and alignment posture (`repo_alignment_status`)  
- Carry **implementation_questions_to_resolve** → Layer 3  
- Carry **statistical_validation_needed** → Layer 4  

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Program layer | This artifact |
|---------------|---------------|
| Layer 1 — Code inventory | ✅ Complete — defines method **universe** |
| **Layer 2 — Literature alignment** | ✅ **This document** + JSON |
| Layer 3 — Implementation validation | ✅ [`METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md) |
| Layer 4 — Statistical validation protocol | ✅ [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| Layer 5 — Combination matrix | ✅ [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) |
| Suitability framework | **Next** — `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001` |
| Trust / suitability framework | **Paused** per validation program §8 |

[`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) and combo matrices remain **hypotheses** until Layer 5.

---

## 3. Inputs from METHOD_CODE_INVENTORY_001

**Inventory counts (Layer 1):** 44 items — 10 design (+ wrapper), 14 estimators, 10 inference, 10 orchestration/alias rows.

**Alignment rule:** Every family below maps to one or more `canonical_name` entries in [`METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json). Orchestration rows (`GeoExperimentDesign`, `ImpactAnalyzer`, etc.) are **not** separate literature families; they appear under implementation questions where they affect design→analysis alignment.

**Status vocabulary (`repo_alignment_status`):**

| Status | Meaning |
|--------|---------|
| `aligned_pending_validation` | Literature identity matches intent; Layer 3–4 proof still required |
| `partially_aligned` | Known deviations or open fidelity questions |
| `literature_mismatch` | Geometry or estimand incompatible with flat production readout |
| `unclear_requires_review` | Literature or implementation mapping incomplete |
| `not_literature_backed` | Research / legacy without product literature claim |
| `implementation_specific_extension` | Deliberate product extension (e.g. diagnostic Kfold bands) |

---

## 4. Literature review method

| Step | Action |
|------|--------|
| 1 | Enumerate families from Layer 1 inventory (no hand-picked shortlist) |
| 2 | Assign **literature_identity** and **canonical_reference_or_reference_family** (primary sources preferred; industry/geo practice cited where academic SCM/DID papers do not cover geo lift) |
| 3 | State **canonical_estimand** and **required_data_geometry** in literature terms |
| 4 | List **assumptions**, **recommended_or_valid_inference_methods**, **diagnostics_expected_by_literature**, **known_failure_modes** |
| 5 | Map **repo_implementation_variants** and **repo_alignment_status** |
| 6 | Emit Layer 3 / Layer 4 question lists — **without** treating prior audit labels as proof |
| 7 | Serialize to JSON for diffable updates |

**Citation policy:** References are **families of work**, not claims that the repo implements every estimator in a paper. Where the repo is product-specific (supergeo, TBRRidge power path, registry `Bayesian` handler), status is `implementation_specific_extension` or `literature_mismatch` as appropriate.

**Canonical reference index (families used in this register):**

| Topic | References |
|-------|------------|
| SCM | Abadie & Gardeazabal (2003); Abadie, Diamond, Hainmueller (2015); Abadie (2021) [JEL — https://doi.org/10.1257/jel.20191450](https://doi.org/10.1257/jel.20191450) |
| Augmented SCM | Ben-Michael, Feller, Rothstein (2021) [arXiv:1811.08779](https://arxiv.org/abs/1811.08779) |
| Ridge / generalized SC | Doudchenko & Imbens (2017) |
| SDID | Arkhangelsky et al. (2021) [RESTUD — https://doi.org/10.1093/restud/rdz044](https://doi.org/10.1093/restud/rdz044) |
| DID | Angrist & Pischke (2009); Callaway & Sant'Anna (2021) for staggered settings |
| BSTS / geo series | Brodersen et al. (2015) [AOAS — https://doi.org/10.1214/14-AOAS788](https://doi.org/10.1214/14-AOAS788) |
| Conformal | Vovk, Gammerman, Shafer (2005); conformal prediction surveys |
| Block bootstrap | Politis & Romano (1994) |
| Rerandomization | Morgan & Rubin (2012) |
| Jackknife+ | Jackknife+ / conformal predictive interval literature (Barber et al. family) |
| Placebo (SCM) | Abadie, Diamond, Hainmueller (2015) placebo exercises |
| Geo / matched markets | Industry geo experiment + matched-market practice (see Track D D1); align with TBR materials |

---

## 5. Design method alignment

### 5.1 Summary table

| family_id | Inventory names | literature_identity (short) | repo_alignment_status | next_layer_3_action |
|-----------|-----------------|------------------------------|------------------------|---------------------|
| DES-GMM-001 | greedy_match_markets | Matched-market greedy geo pairing | partially_aligned | GeoExperimentDesign pre-period audit |
| DES-RERAND-001 | rerandomization_wrapper | Rerandomization wrapper on base designs | aligned_pending_validation | Wrapper vs bare greedy dispatch |
| DES-TIER1-RAND-001 | complete / balanced / stratified / thinning | Standard geo randomization arms | aligned_pending_validation | Per-mode constraint behavior |
| DES-SUPERGEO-001 | supergeos | Cluster/supergeo pair geometry | literature_mismatch | F-GEO-003 geometry bridge |
| DES-TRIM-001 | trimmedmatch | Trimmed pair markets (Tp/Te) | literature_mismatch | F-GEO-004 geometry bridge |
| DES-LEGACY-BLOCK-001 | quickblock, matchedpair | Legacy blocking APIs | unclear_requires_review | Quarantine vs research-only |

### 5.2 DES-GMM-001 — greedy_match_markets

| Field | Content |
|-------|---------|
| **literature_identity** | Matched-market / greedy geo market pairing before treatment |
| **canonical_estimand** | Valid randomization assignment — **not** ATT (analysis estimand is separate) |
| **required_data_geometry** | Unit-level panel; `control` + `test_*` assignment dict |
| **assumptions** | Pre-treatment-only matching; sufficient controls; stable units |
| **valid inference (design stage)** | N/A — pairing with TBR/SCM at analysis requires design–analysis alignment |
| **diagnostics** | Pre-period balance; constraint satisfaction; KPI-mass treatment shares |
| **failure modes** | Post-period leakage in matching (INV-D1-001); donor pool ≠ design pool |
| **repo variants** | `greedy_match_markets`; geo_runner / GeoExperimentDesign |
| **Layer 3** | Confirm `pre_treatment_period` plumbing end-to-end |
| **Layer 4** | 001e balance + null-monitor sensitivity when `wide` includes post periods |

### 5.3 DES-RERAND-001 — rerandomization_wrapper

| Field | Content |
|-------|---------|
| **literature_identity** | Morgan–Rubin rerandomization for covariate balance |
| **canonical_estimand** | Assignment subject to balance acceptance |
| **repo variants** | `Rerandomization` class; not a separate registry name |
| **failure modes** | Production path differs from bare greedy; inference not automatic |
| **Layer 3** | Imbalance metric ↔ literature balance definition |
| **Layer 4** | Rerandomization vs bare tier-1 OC sensitivity |

### 5.4 DES-TIER1-RAND-001 — tier-1 randomizers

**Inventory:** completerandomization · balancedrandomization · stratifiedrandomization · thinningdesign

| Field | Content |
|-------|---------|
| **literature_identity** | Classical randomization / stratification / thinning designs |
| **canonical_estimand** | Known assignment probabilities to arms |
| **failure modes** | Design–readout mismatch when analysis assumes matched markets |
| **Layer 3** | Strata + KPI share semantics per class |
| **Layer 4** | D5-POW-001e tier-1 with SCM+JK reference path |

### 5.5 DES-SUPERGEO-001 / DES-TRIM-001

| Field | supergeos | trimmedmatch |
|-------|-----------|--------------|
| **geometry** | MILP/cluster pairs | Tp/Te trimmed pairs |
| **repo_alignment_status** | literature_mismatch | literature_mismatch |
| **failure modes** | Flat SCM+JK invalid (A29) | Flat SCM+JK invalid (A30) |
| **Layer 3** | F-GEO-003 bridge | F-GEO-004 bridge |
| **Layer 4** | D5-DES-SUPERGEO-001 | D5-DES-TRIM-001 |

### 5.6 DES-LEGACY-BLOCK-001

**quickblock · matchedpair** — not geo-run; `unclear_requires_review`. Candidate **quarantine** unless revived with literature + Layer 3 proof.

---

## 6. Estimator alignment

### 6.1 Summary table

| family_id | Inventory names | canonical_estimand (short) | repo_alignment_status |
|-----------|-----------------|----------------------------|------------------------|
| EST-SCM-001 | SCM, SyntheticControlCVXPY, synthetic_control() | Treated-unit gap vs donor-weighted SC | partially_aligned |
| EST-AUGSYNTH-001 | AugSynthCVXPY, AugSynth | Augmented SC bias-corrected ATT | partially_aligned |
| EST-TBR-001 | TBR | Aggregate geo lift (1×1 series) | aligned_pending_validation |
| EST-TBRRIDGE-001 | TBRRidge | Ridge-regularized counterfactual / lift | partially_aligned |
| EST-DID-001 | DID | Panel ATT / cumulative ATT | partially_aligned |
| EST-SDID-001 | SyntheticDID | SDID ATT | unclear_requires_review |
| EST-RESEARCH-BAYES-001 | BayesianTBR*, TBRAutoSARIMAX | Posterior / state-space lift | unclear_requires_review |
| EST-RESEARCH-OTHER-001 | TROP, MTGP | Research-only | not_literature_backed |

### 6.2 EST-SCM-001 — synthetic control family

**References:** Abadie et al. (2015); Abadie (2021).

| Field | Content |
|-------|---------|
| **canonical_estimand** | Treated-unit treatment effect vs weighted donor counterfactual |
| **required_data_geometry** | Donor pool + treated units; explicit pre/post windows |
| **assumptions** | Donor exclusion; convex weights; informative pre-fit; spillover limits |
| **valid inference (literature)** | Permutation / placebo / jackknife variants — **not** all classical CI |
| **repo inference wired** | UnitJackKnife, JKP, Kfold, BRB, Conformal, Placebo, TimeSeriesKfold, Bayesian (compatibility varies) |
| **diagnostics** | Pre RMSPE; weight concentration; placebo distribution |
| **failure modes** | `full_model` leakage; outside hull; aggregate vs unit confusion |
| **Layer 3** | D2 donor rules; level vs relative; SCM alias routing |
| **Layer 4** | SCM+JK null FPR; Placebo scope |

### 6.3 EST-AUGSYNTH-001 — augmented SCM

**Reference:** Ben-Michael, Feller, Rothstein (2021).

| Field | Content |
|-------|---------|
| **canonical_estimand** | Augmented treated-unit gap (ridge + SCM leg) |
| **treatment structure** | Per-cell multi-cell; **no pooled causal lift** (ADR semantic guardrail) |
| **failure modes** | SCM leg mismatch (G4/G7/G8); JK unsafe strata; Conformal blocked; pooling invalid |
| **Layer 3** | Fidelity G1–G8; per-cell metadata |
| **Layer 4** | ASCM-003; JK calibration; Conformal POSTFIX (non-promotion) |

### 6.4 EST-TBR-001 / EST-TBRRIDGE-001

| | TBR | TBRRidge |
|---|-----|----------|
| **literature** | Geo TBR / matched-market industry practice | Doudchenko & Imbens ridge balancing + product extension |
| **geometry** | 1 treated + 1 control aggregate row | Unit panel + agg2 power path |
| **failure modes** | Unit-panel misuse | JK/JKP high null FPR; Bayesian registry ≠ MCMC |
| **Layer 3** | INV-003 estimand | JK pivot / pooled-CF |
| **Layer 4** | D5-INST-TBR-001 | D5-INST-TBRRIDGE-* |

### 6.5 EST-DID-001 / EST-SDID-001

**DID:** Angrist & Pischke; Callaway & Sant'Anna when staggered timing claimed. Embedded bootstrap — `partially_aligned`. Layer 3: registry vs native bootstrap. Layer 4: A25 + pretrend.

**SyntheticDID:** Arkhangelsky et al. (2021). `unclear_requires_review` — research_only until fidelity spike.

### 6.6 Research estimators

**BayesianTBR / Horseshoe / TBRAutoSARIMAX:** BSTS literature; `unclear_requires_review` — JAX optional; registry Bayesian handler mismatch (INV-015).

**TROP / MTGP:** `not_literature_backed` for product — quarantine unless charter renewed.

---

## 7. Inference method alignment

### 7.1 Summary table

| family_id | Inventory names | literature role | repo_alignment_status |
|-----------|-----------------|-----------------|------------------------|
| INF-POINT-001 | point_estimate | Point diagnostic only | aligned_pending_validation |
| INF-JK-001 | UnitJackKnife | Jackknife / SCM uncertainty cousin | partially_aligned |
| INF-JKP-001 | JKP | Jackknife+ predictive intervals | partially_aligned |
| INF-KFOLD-001 | Kfold | CV diagnostic bands | implementation_specific_extension |
| INF-TSKFOLD-001 | TimeSeriesKfold | Temporal blocked CV | partially_aligned |
| INF-BRB-001 | BlockResidualBootstrap | Block bootstrap CI | aligned_pending_validation |
| INF-CONFORMAL-001 | Conformal | Conformal predictive intervals | partially_aligned |
| INF-PLACEBO-001 | Placebo | SCM falsification | aligned_pending_validation |
| INF-BAYES-REG-001 | Bayesian | Credible intervals (if full Bayes) | literature_mismatch |
| INF-DID-BOOT-001 | DID_native_bootstrap | DID bootstrap | partially_aligned |

### 7.2 Per-family notes (concise)

**UnitJackKnife:** Literature jackknife + SCM permutation context; repo uses as **null monitor** for SCM in characterized strata — not automatic confirmatory CI for all estimators. Invalid on 2-row aggregate geometry. TBRRidge null FPR failure documented in evidence — Layer 4 calibration required.

**JKP:** Jackknife+ literature; pooled-CF semantics on TBRRidge must match pivot definition (Layer 3).

**Kfold / TimeSeriesKfold:** Diagnostic resampling extensions — must not be marketed as literature-primary SCM inference.

**BlockResidualBootstrap:** Politis–Romano block bootstrap; primary OC path TBRRidge; mis-pairing with AugSynth is invalid combo.

**Conformal:** Exchangeability required; panel dependence problematic; F-INF-003 orientation; AugSynth+Conformal blocked pending new interval design.

**Placebo:** Falsification only (Abadie et al. placebo); not CI; multi-treated scope limited.

**Bayesian (registry):** Credible intervals only if posterior sampling matches Brodersen et al. — current TBRRidge registry path **literature_mismatch**.

**DID_native_bootstrap:** Estimator-embedded; cumulative ATT framing (DEF-003); relative CI policy open.

---

## 8. Design × estimator × inference implications

Literature **does not** authorize arbitrary crossing of design geometry with estimators. High-risk pairings from evidence (not proof):

| Design family | Estimator | Inference | Literature implication | Repo posture |
|---------------|-----------|-----------|----------------------|--------------|
| DES-GMM-001 | EST-SCM-001 | INF-JK-001 | Matched markets + SC + jackknife — common geo **practice**; design donors ≠ SCM donors | **Partially aligned** — bridge MAT-004 |
| DES-TIER1-RAND-001 | EST-SCM-001 | INF-JK-001 | Randomized geo + SC — requires explicit design-based justification for SC analysis | **Aligned pending** — 001e reference |
| DES-SUPERGEO-001 | EST-SCM-001 | INF-JK-001 | **Mismatch** without geometry bridge | **Blocked** (A29) |
| DES-TRIM-001 | EST-SCM-001 | INF-JK-001 | **Mismatch** without pair bridge | **Blocked** (A30) |
| DES-GMM-001 | EST-TBR-001 | point | Matched markets + aggregate TBR — design–analysis alignment literature | **Aligned pending** |
| DES-* | EST-AUGSYNTH-001 | INF-JK-001 | JK not literature-default for ASCM; unsafe strata in repo evidence | **Diagnostic-only / blocked** |
| DES-* | EST-AUGSYNTH-001 | INF-CONFORMAL-001 | Conformal under exchangeability debate for panels | **Blocked** pending design |
| DES-* | EST-TBRRIDGE-001 | INF-JK-001 / INF-JKP-001 | Requires calibrated pivots | **Needs calibration** |
| Any | EST-DID-001 | INF-DID-BOOT-001 | DID bootstrap separate from registry BRB | **Partial** — dispatch clarity |

**Multi-cell:** Literature default is **per-cell** estimands for SC/ASCM; pooled lift is **not** literature-backed for causal claims (pooling ADR = semantic guardrail only).

---

## 9. Known literature gaps and ambiguities

| Gap | Description | Handling |
|-----|-------------|----------|
| Geo lift vs academic SCM | Industry geo experiments combine matching + regression + SC variants not always co-described in one paper | Label industry + academic references separately; `partially_aligned` |
| JK as null monitor | Repo characterized SCM+JK null FPR — literature for SCM inference is often permutation-based | `implementation_specific_extension` for monitor role until Layer 4 documents |
| TBRRidge + JK/JKP | Ridge balancing literature ≠ product pivot semantics | Layer 3 pivot audit required |
| Conformal on panels | Exchangeability questionable with temporal dependence | `partially_aligned`; coverage OC not promotion |
| Staggered DID | Debate on TWFE vs modern estimators | DID class must declare timing model before promotion |
| Supergeo / trim | Product geometry without single canonical paper in repo | `literature_mismatch` until bridge ADR |
| Registry Bayesian | Name implies MCMC; implementation may not | `literature_mismatch` on prod path |

---

## 10. Implementation questions carried into Layer 3

Consolidated from JSON `implementation_questions_to_resolve` (priority order):

1. **Pre-period design leakage** — greedy_match_markets / GeoExperimentDesign / geo_runner (`INV-D1-001`)  
2. **SCM fidelity** — donors, `full_model`, level vs relative, CVXPY vs scipy paths  
3. **AugSynthCVXPY fidelity** — G1–G8 SCM leg vs outcome leg; per-cell metadata  
4. **Geometry bridges** — supergeos, trimmedmatch → unit-panel estimators  
5. **TBR/TBRRidge estimand registry** — cumulative vs relative; aggregate vs unit  
6. **Inference plumbing** — JK target matrices; JKP pooled-CF; Conformal scores/orientation; DID bootstrap dispatch  
7. **Registry disambiguation** — SCM aliases; Bayesian handler vs BayesianTBR class  
8. **Rerandomization wrapper** — dispatch and metric definitions  

**Deliverable:** `METHOD_IMPLEMENTATION_VALIDATION_001` with per-family pass/fail/`implementation_gap`.

---

## 11. Statistical validation questions carried into Layer 4

| Family | Batteries / metrics (examples) |
|--------|--------------------------------|
| DES-GMM + tier-1 | Balance; 001e null FPR for paired SCM+JK |
| EST-SCM | Donor stress; Placebo distribution; JK null FPR |
| EST-AUGSYNTH | ASCM-003 strata; outside-hull; JK unsafe strata exclusion |
| EST-TBR | Aggregate ratio stability (TBR-001) |
| EST-TBRRidge | TBRRIDGE-001/003; JK/JKP null FPR and coverage |
| INF-CONFORMAL | POSTFIX orientation; width; null exclude rate |
| EST-DID | A25 bootstrap; pretrend worlds |
| DES-SUPERGEO / TRIM | DES audits; combo blocked until bridge |

**Deliverable:** `METHOD_STATISTICAL_VALIDATION_PROTOCOL_001` — synthetic worlds per family; archives required before Layer 5 combos.

---

## 12. Items to quarantine or deprecate unless literature support is found

| Item | Reason | Layer 2 status |
|------|--------|----------------|
| synthetic_control() legacy function | Superseded by classes | not_literature_backed / quarantine candidate |
| AugSynth (non-CVXPY) | UNVALIDATED maturity | unclear_requires_review |
| quickblock, matchedpair | Not geo-run | unclear_requires_review |
| TROP, MTGP | No product literature path | not_literature_backed |
| Registry Bayesian on TBRRidge | ≠ BSTS MCMC | literature_mismatch |
| Pooled multi-cell AugSynth lift | Not canonical ASCM estimand | literature_mismatch (ADR blocks semantics) |
| Ad-hoc combos (A04, A06, …) | Invalid interface per COMBO audit | remain blocked in Layer 5 |

*Final quarantine decisions require Layer 3 confirmation.*

---

## 13. Next artifact: DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001

**Layers 3–5** complete — see implementation validation, statistical protocol, and combination matrix artifacts.

**Post-Layer-5** suitability framework uses matrix rows + D5-STAT evidence; does not auto-assign trust roles.

**Inputs:** Layer 5 JSON `rows[]` · §11 statistical_validation_needed lists · prior D5 archives (evidence only).

---

## 14. Guardrails

- **No** primary / secondary / directional / diagnostic evidence labels  
- **No** promotion, demotion, or eligibility change  
- **No** estimator, inference, or design behavior change  
- **No** OC execution in this PR  
- **No** TrustReport / F-DECISION / CalibrationSignal / MMM / LLM change  
- **Prior audit verdicts** are citations for **questions**, not final proof  
- **`repo_alignment_status`** describes literature fit — **not** product permission  

---

## 15. Stop condition

| Criterion | Status |
|-----------|--------|
| All Layer 1 inventory families covered (design, estimator, inference) | ✅ (24 literature families → 44 inventory items) |
| Citations / reference families recorded | ✅ §4 |
| Layer 3 questions enumerated | ✅ §10 |
| Layer 4 questions enumerated | ✅ §11 |
| Design × estimator × inference implications table | ✅ §8 |
| JSON register + generator + test | ✅ |
| Roadmap/registry updated | ✅ (companion edits) |

---

*METHOD-LITERATURE-ALIGNMENT-001 v1.0.0 — Layer 2 complete; Layer 3 implementation validation is next.*
