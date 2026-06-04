# METHOD-CODE-INVENTORY-001

**Document ID:** METHOD-CODE-INVENTORY-001  
**Type:** Layer 1 code-derived method inventory — **read-only discovery**  
**Status:** **complete** (docs + generator)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) Layer 1

**Machine-readable inventory:** [`track_d/archives/METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json) (44 items; regenerate via `python -m panel_exp.validation.method_code_inventory_001`)

**Generator:** [`panel_exp/validation/method_code_inventory_001.py`](../panel_exp/validation/method_code_inventory_001.py)

**Evidence input (not authority):** [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) · prior Track D / Track F inventory docs

**Guardrails:** No trust roles · no promotion/demotion · no behavior change · no OC in this artifact

---

## 1. Purpose

Discover **all implemented** design, estimator, inference, wrapper, orchestration, and registry components from **code** before literature alignment, implementation validation, statistical OC, or trust-framework work resumes.

This inventory answers: *what exists in the repo today?* — not *what should be primary/secondary/diagnostic in product*.

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Program layer | This artifact |
|---------------|---------------|
| **Layer 1 — Code inventory** | ✅ **This document** + JSON archive |
| Layer 2 — Literature alignment | ✅ [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) |
| Layer 3 — Implementation validation | ✅ [`METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md) |
| Layer 4 — Statistical validation protocol | ✅ [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| Layer 5 — Combination matrix | ✅ [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) |
| Suitability framework | **Next** — `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001` |
| Suitability / trust framework | **Paused** per validation program §8 |

[`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) remains a useful **evidence map** but is **superseded for sequencing**; combination rows there are hypotheses until Layer 5.

---

## 3. Inventory method

| Step | Source | Rule |
|------|--------|------|
| 1 | `get_design_registry()` | All registered `DesignSpec` rows + manual `rerandomization_wrapper` |
| 2 | `estimator_catalog()` | `_ESTIMATOR_CATALOG` in `method_metadata.py` |
| 3 | `inference_mode_catalog()` + `InferenceRegistry` | Registered modes + **DID native bootstrap** (embedded, not registry) |
| 4 | Code inspection | Orchestration (`GeoExperimentDesign`, `ImpactAnalyzer`, `PowerAnalysis`), registries, alias collisions |
| 5 | Docs/tests (supplement) | Cross-link prior audits; **not** primary discovery |

**Regenerate JSON after registry/catalog changes:**

```bash
python -m panel_exp.validation.method_code_inventory_001
```

---

## 4. Scope

### In scope

- `panel_exp/design/` · `panel_exp/methods/` · `panel_exp/inference/` · `panel_exp/impact.py`
- Design / inference **registries** and **maturity catalogs**
- Production geo orchestration (`GeoExperimentDesign`, `Rerandomization` wrapper)
- Research estimators present in catalog (TROP, MTGP, BayesianTBR, SyntheticDID, legacy `synthetic_control` function)

### Out of scope

- Trust roles (primary/secondary/directional/diagnostic)
- Final combination suitability or promotion
- Running OC or changing estimator/inference behavior
- Exhaustive test-file grep (representative references only)

---

## 5. Design methods discovered

**Registry source:** `panel_exp/design/modes/__init__.py` → `register_builtin_designs`.

| canonical_name | class / handler | geo_run_supported | inventory_status | notes |
|----------------|-----------------|-------------------|------------------|-------|
| **greedy_match_markets** | `greedy_match_markets` | yes | implemented | Production default base; D5-POW-001c/e baseline |
| **completerandomization** | `CompleteRandomization` | yes | implemented | Tier-1 geo |
| **balancedrandomization** | `BalancedRandomization` | yes | implemented | Tier-1 geo |
| **stratifiedrandomization** | `StratifiedRandomization` | yes | implemented | Tier-1 geo |
| **thinningdesign** | `ThinningDesign` | yes | implemented | Tier-1 geo |
| **trimmedmatch** | `TrimmedMatchDesign` | no | partial | Tp/Te pairs; D5-DES-TRIM-001 |
| **supergeos** | `SupergeoModel` | no | partial | Separate geometry; D5-DES-SUPERGEO-001 |
| **quickblock** | `QuickBlock` | no | partial | Legacy API; not geo-run |
| **matchedpair** | `MatchedPair` | no | partial | Legacy API; not geo-run |
| **rerandomization_wrapper** | `Rerandomization` | yes (via wrapper) | implemented | **Not** separate registry name; `GeoExperimentDesign` wraps tier-1 bases |

**Multi-cell:** Not a separate design class — `n_test_grps > 1` on geo-supported designs (assignment dict `test_0..test_{K-1}`).

**Count:** 9 registry designs + 1 wrapper row (see JSON).

---

## 6. Estimators discovered

**Catalog source:** `panel_exp/method_metadata.py` → `_ESTIMATOR_CATALOG` (13 entries) + legacy function.

| canonical_name | class | module | inventory_status | inference_support (declared) |
|----------------|-------|--------|------------------|------------------------------|
| **SCM** | `SyntheticControl` | `methods/scm.py` | implemented | JK, JKP, BRB, Conformal, Kfold, Placebo, TS-Kfold, Bayesian |
| **SyntheticControlCVXPY** | `SyntheticControlCVXPY` | `methods/scm.py` | implemented | point, Kfold, Conformal, BRB |
| **AugSynthCVXPY** | `AugSynthCVXPY` | `methods/scm.py` | implemented | point, Kfold, Conformal |
| **AugSynth** | `AugSynth` | `methods/scm.py` | partial | point, Kfold, Conformal — UNVALIDATED maturity |
| **TBR** | `TBR` | `methods/tbr.py` | implemented | point, JK, JKP, Kfold — **1 treated + 1 control row only** |
| **TBRRidge** | `TBRRidge` | `methods/tbr.py` | implemented | full inference menu (see catalog) |
| **TBRAutoSARIMAX** | `TBRAutoSARIMAX` | `methods/tbr.py` | partial | point only; pmdarima optional |
| **DID** | `DID` | `methods/DID.py` | implemented | point + **native bootstrap in estimator** |
| **SyntheticDID** | `SyntheticDID` | `methods/synthetic_did.py` | research_only | point |
| **TROP** | `TROP` | `methods/triply_robust_est.py` | research_only | point |
| **MTGP** | `MTGP` | `methods/mtgp.py` | research_only | Bayesian |
| **BayesianTBR** | `BayesianTBR` | `methods/bayesian_regression.py` | research_only | Bayesian (JAX) |
| **BayesianTBRHorseShoe** | `BayesianTBRHorseShoe` | `methods/bayesian_regression.py` | research_only | Bayesian (JAX) |
| **synthetic_control_function** | `synthetic_control()` | `methods/synthetic_control.py` | legacy | Not in catalog — scipy helper |

**ASCM:** Not a separate class — **AugSynthCVXPY** implements augmented SCM (ridge outcome leg + CVXPY SCM leg).

---

## 7. Inference methods discovered

**Registry source:** `panel_exp/inference/modes/__init__.py` → `register_builtin_inference_modes` (9 modes).

| canonical_name | implementation | intervals | inventory_status |
|----------------|----------------|-----------|------------------|
| **point_estimate** | `impl.run_point_estimate` | none | implemented |
| **UnitJackKnife** | `unit_jackknife` / `impl` | CI | implemented |
| **JKP** | `jkp` / `impl` | CI | implemented |
| **Kfold** | `k_fold.kfold` | CI | implemented |
| **TimeSeriesKfold** | `k_fold` TS path | CI | implemented |
| **BlockResidualBootstrap** | `block_residual_bootstrap` | CI | implemented |
| **Conformal** | `conformal` / `impl` | conformal | implemented |
| **Placebo** | `placebo` / `impl` | placebo band | implemented |
| **Bayesian** | `impl.run_bayesian` | credible | research_only (handler) |
| **DID_native_bootstrap** | `DID.run_analysis` | cumulative ATT | partial — **not** in inference registry |

**Bootstrap:** No standalone registry mode named `Bootstrap`; BRB is **BlockResidualBootstrap**. DID uses **estimator-embedded** bootstrap.

---

## 8. Wrappers / orchestration paths discovered

| canonical_name | type | module | role |
|----------------|------|--------|------|
| **Rerandomization** | wrapper | `design/assign.py` | Wraps tier-1 randomizers; imbalance minimization |
| **GeoExperimentDesign** | orchestration | `design/geo_experiment_design.py` | Geo design + power/MDE + evidence |
| **run_geo_experiment_design** | orchestration | `design/geo_runner.py` | Registry dispatch for geo designs |
| **ImpactAnalyzer** | orchestration | `impact.py` | Estimator + inference dispatch |
| **PowerAnalysis** | orchestration | `design/power.py` | Simulation MDE; often TBRRidge agg2 path |
| **recovery_runner** | orchestration | `validation/recovery_runner.py` | Synthetic recovery batteries |
| **track_d_d5_* harnesses** | orchestration | `validation/track_d_d5_*.py` | OC archives (evidence, not catalog) |

---

## 9. Research / archived / legacy components

| Component | status | notes |
|-----------|--------|-------|
| TROP, MTGP, SyntheticDID | research_only | Skipped or limited in validation runner |
| BayesianTBR, BayesianTBRHorseShoe | research_only | JAX optional stack |
| AugSynth (non-CVXPY) | partial | UNVALIDATED maturity |
| synthetic_control() function | legacy | Pre–ImpactAnalyzer scipy path |
| quickblock, matchedpair | partial | Registered; not geo-run |
| supergeos, trimmedmatch | partial | Require geometry bridges before SCM/AugSynth readout |

---

## 10. Alias and naming collision table

| canonical_name | aliases / collision | risk |
|----------------|---------------------|------|
| greedy_match_markets | gmm, greedymatchmarkets | low |
| trimmedmatch | trimmed_match | low |
| supergeos | supergeo, supergeo_model | medium — “supergeo” overloaded in docs |
| **SCM** | SyntheticControl, SyntheticControlCVXPY | **high** — three names, two production legs |
| **TBR vs TBRRidge** | both in `tbr.py` | **high** — product conflation (GAP-TBR-TBRR-001) |
| **AugSynth vs AugSynthCVXPY** | ASCM colloquial | medium — charter uses CVXPY path |
| **rerandomization_wrapper** | Rerandomization class | medium — not in `list_names()` |
| **Kfold vs TimeSeriesKfold** | panel vs temporal blocking | medium — distinct semantics |
| **Placebo** | forbidden as **estimator** catalog name | governance — inference only |

---

## 11. Docs / tests coverage table

| Category | n_items | docs anchor | tests (representative) | validation archives |
|----------|---------|-------------|------------------------|---------------------|
| Design (geo) | 5 | TRACK_D_DESIGN_METHOD_INVENTORY | test_design_inventory_001 | D5-POW-001e, D5-DES-001a |
| Design (non-geo) | 4 | D5-DES-SUPERGEO/TRIM | partial | D5-DES-SUPERGEO-001, D5-DES-TRIM-001 |
| Estimators (production path) | 4 core | METHOD_SOUNDNESS §2.A | test_scm.py, track_d AugSynth/TBR | ASCM-003, TBR-001, TBRRIDGE-* |
| Estimators (research) | 4 | D2 inventory | trop_test, synthetic_did_test | sparse |
| Inference modes | 9 | D3, F-INF-001 | governance f_inf tests | D5-INF-*, POSTFIX |
| Orchestration | 5+ | D4, geo docs | track_d, recovery tests | POW-001* |

**Gap:** Not every cataloged estimator has dedicated OC archive; research paths are **test_only** or **unclear_requires_review**.

---

## 12. Known gaps carried forward from prior audits

| gap_id | component | source |
|--------|-----------|--------|
| INV-D1-001 | greedy_match_markets | Caller must pass `pre_treatment_period` or matching uses full panel |
| G4 / G7 / G8 | AugSynthCVXPY | Fidelity audit — SCM leg mismatch, level vs relative, hull proxy |
| IMPL-JK-001 | AugSynth+UnitJackKnife | W8 unsafe stratum (JK calibration-001) |
| IMPL-CONF-001 | AugSynth+Conformal | Blocked pending new interval design |
| F-GEO-003/004 | supergeos, trimmedmatch | No unit-panel bridge |
| POW-EST-001 | PowerAnalysis vs SCM+JK | TBRRidge agg2 planning vs unit readout |
| D2 full_model | SCM paths | Post-period weight leakage risk |
| F-INF / INV-015 | Bayesian registry on TBRRidge | Not full BayesianTBR MCMC |

---

## 13. Items requiring literature alignment (Layer 2)

All **implemented** estimators and inference modes except `point_estimate` require literature rows in **`METHOD_LITERATURE_ALIGNMENT_001`**.

**Priority families (from evidence density, not role assignment):**

1. SCM / synthetic control / jackknife / placebo  
2. Augmented SCM (AugSynthCVXPY)  
3. Conformal + panel/time-series uncertainty  
4. TBR / TBRRidge / ridge geo lift  
5. DID / SDID  
6. Multi-cell geo designs + shared control  
7. Supergeo / trimmed matching designs  
8. Rerandomization-based designs  

---

## 14. Items requiring implementation validation (Layer 3)

| Item | trigger |
|------|---------|
| AugSynthCVXPY | G1–G8 fidelity caveats |
| SCM / SyntheticControlCVXPY | full_model, donor rules |
| UnitJackKnife, JKP | target matrix, pooled-CF on TBRRidge |
| Conformal, TimeSeriesKfold | F-INF-003 orientation; band semantics |
| TBR | aggregate-only asserts |
| DID | native bootstrap vs registry dispatch |
| GeoExperimentDesign | period slicing into matching |
| supergeos, trimmedmatch | output type ≠ assignment dict |

---

## 15. Items to quarantine / deprecate (candidate list)

| Item | candidate reason | action |
|------|------------------|--------|
| **synthetic_control()** function | legacy scipy; superseded by classes | quarantine candidate — document only |
| **AugSynth** (non-CVXPY) | UNVALIDATED maturity | research/quarantine until fidelity |
| **Bayesian** inference handler without JAX pins | optional-deps fragility | research_only path |
| **quickblock / matchedpair** | not geo-run | legacy — no new product wiring |
| **TROP / MTGP** | no production metadata path | research_only |

*Final quarantine decisions belong in Layer 3/5 — this list is inventory-only.*

---

## 16. Next artifact

**`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`** — post-Layer-5 suitability map (no automatic trust roles).

**Inputs from this inventory:** JSON `items[]` · Layers 2–5 registers · executed D5-STAT-* archives when present.

---

## 17. Guardrails

- **No** trust-role labels (primary/secondary/directional)  
- **No** promotion or eligibility change  
- **No** estimator, inference, or design behavior change  
- **No** OC execution in this PR  
- **No** TrustReport / F-DECISION / CalibrationSignal / MMM / LLM change  
- **Inventory status** describes code presence/maturity — **not** product permission  

---

## 18. Stop condition

| Criterion | Status |
|-----------|--------|
| Code-first discovery documented | ✅ |
| Machine-readable JSON (44 items) | ✅ |
| Regenerator script (read-only) | ✅ |
| Sufficient structure for literature alignment | ✅ |
| Roadmap/registry updated | ✅ (companion edits) |

---

*METHOD-CODE-INVENTORY-001 v1.0.0 — Layer 1 complete; authority for sequencing remains METHOD-VALIDATION-PROGRAM-001.*
