# METHOD-STATISTICAL-VALIDATION-PROTOCOL-001

**Document ID:** METHOD-STATISTICAL-VALIDATION-PROTOCOL-001  
**Type:** Layer 4 statistical validation / OC protocol — **read-only plan**  
**Status:** **complete** (register + generator; no heavy OC execution)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) Layer 4

**Machine-readable register:** [`track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json`](track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json) (51 rows; regenerate: `python -m panel_exp.validation.method_statistical_validation_protocol_001`)

**Generator:** [`panel_exp/validation/method_statistical_validation_protocol_001.py`](../panel_exp/validation/method_statistical_validation_protocol_001.py)

**Primary inputs:** Layer 1–3 artifacts · prior D5 / Track D / Track F OC reports (**evidence only**)

**Guardrails:** No trust roles · no promotion · no eligibility changes · no heavy OC in this PR · no CalibrationSignal/MMM/LLM/TrustReport changes

---

## 1. Purpose

Answer **“What statistical evidence is required before a method family or design × estimator × inference combination may be considered validated?”**

Layer 4 defines **synthetic worlds**, **metrics**, **acceptance criteria classes**, **battery levels**, and **expected D5-STAT-* artifacts**. It does **not** execute full OC batteries, declare methods production-ready, or assign primary/secondary/directional evidence roles.

| Question | Layer 4 answers |
|----------|-----------------|
| Is a path eligible for OC? | `eligibility_status` from Layer 3 gates |
| Which DGP worlds apply? | `required_worlds` per row |
| Which metrics must be recorded? | `required_metrics` + metric catalog |
| What thresholds apply? | Acceptance **classes** (proposed until OC supports) |
| What runs first? | Recommended execution order §15 |

**Not answered here:** trust roles · promotion · suitability matrix (Layer 5).

**Design methods:** Estimator/inference protocol rows do **not** substitute for design-method statistical validation. Future **`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`** must assert **DesignOutputContract** completeness per [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) in every design simulation world.

**Wording:** Use **ready for protocol**, **blocked**, or **research-only** — never “validated,” “trusted,” or “eligible for promotion.”

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Program layer | Status |
|---------------|--------|
| Layer 1 — Code inventory | ✅ |
| Layer 2 — Literature alignment | ✅ |
| Layer 3 — Implementation validation | ✅ |
| **Layer 4 — Statistical validation protocol** | ✅ **This artifact** |
| Layer 5 — Combination matrix | ✅ [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) |
| Suitability framework | ✅ |
| D5-STAT smoke + SCM+JK Level B | ✅ [`D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) · [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) |
| Suitability / trust framework | **Paused** per program §8 |

---

## 3. Inputs from Layers 1–3

| Layer | Artifact | Layer 4 use |
|-------|----------|-------------|
| 1 | [`METHOD_CODE_INVENTORY_001`](METHOD_CODE_INVENTORY_001.md) | Canonical names, modules, geometry hints |
| 2 | [`METHOD_LITERATURE_ALIGNMENT_001`](METHOD_LITERATURE_ALIGNMENT_001.md) | `statistical_validation_needed` lists per family |
| 3 | [`METHOD_IMPLEMENTATION_VALIDATION_001`](METHOD_IMPLEMENTATION_VALIDATION_001.md) | `implementation_validation_status` → eligibility mapping |

**Coverage:** Every Layer 3 row (29) maps to ≥1 protocol row; 22 combination protocol cards extend design × estimator × inference planning.

---

## 4. Statistical validation philosophy

1. **Protocol before proof** — This artifact is the validation *plan*; D5-STAT-* archives are the *evidence*.  
2. **Layer 3 gates Layer 4** — `implementation_gap`, `architecture_gap`, and unsupported geometry block confirmatory OC until fixed or bridged.  
3. **Characterization before calibration** — Level B records behavior under null/injected worlds without promotion authority.  
4. **Governed uncertainty is stricter** — Interval methods targeting nominal FPR/coverage require Level C+ with proposed hard gates on interval semantics.  
5. **Prior OC is evidence only** — D5-POW-001e, ASCM-003, JK calibration, Conformal POSTFIX inform protocol rows; they do not auto-pass Layer 4.  
6. **No silent unsupported geometry** — Level A smoke must confirm block or explicit abstention on invalid combos.

---

## 5. Battery levels A–E

| Level | Name | Scope | Promotion authority |
|-------|------|-------|---------------------|
| **A** | Smoke validation | Callable path, schema, interval orientation, geometry guards | None |
| **B** | Characterization | Moderate MC; null + injected worlds | None |
| **C** | Calibration | Larger MC; FPR, coverage, interval semantics | None (protocol only) |
| **D** | Stress / robustness | Shocks, donor stress, hull, multi-cell, trim/supergeo | None |
| **E** | Promotion-candidate | Full battery after Layers 1–5 + gap closure | **Not authorized by this artifact** |

---

## 6. DGP world catalog

| World ID | Intent |
|----------|--------|
| `clean_linear_additive` | Recovery slope / bias baseline |
| `weak_signal` | Power-adjacent characterization |
| `noisy_low_signal` | High variance null/injected |
| `correlated_controls_collinearity` | Donor weight instability |
| `treated_outside_donor_hull` | Extrapolation stress |
| `post_period_shock` | Post-treatment outlier sensitivity |
| `pre_period_trend_mismatch` | Design balance / pretrend stress |
| `sparse_geo_low_donor_count` | Donor-count sensitivity |
| `multi_treated_multi_cell` | Per-cell vs pooled geometry |
| `aggregate_two_row` | TBR / aggregate readout only |
| `supergeo_geometry` | Cluster geometry (bridge required) |
| `trimmed_pair_geometry` | Pair geometry (bridge required) |
| `null_no_effect` | FPR / placebo null |
| `positive_injected_lift` | Bias, MAE, recovery slope |
| `negative_injected_lift` | Sign error / symmetric recovery |
| `heterogeneous_treatment_effects` | Multi-unit heterogeneity |
| `delayed_ramp_effect` | Dynamic treatment paths |

Full list: JSON `dgp_world_catalog`.

---

## 7. Metric catalog

| Metric | Typical use |
|--------|-------------|
| `null_false_positive_rate` | Governed uncertainty / null monitor |
| `empirical_coverage` | Interval methods |
| `bias`, `mae`, `rmse` | Point estimators |
| `interval_width` | Efficiency vs nominal |
| `interval_orientation_validity` | POSTFIX / export checks |
| `lower_le_upper_rate`, `negative_half_width_rate`, `degenerate_interval_rate` | **Hard gates** (proposed 1.0 / 0.0 / bounded) |
| `point_recovery_slope`, `point_injected_ratio` | Injected-world recovery |
| `donor_stability`, `treated_control_prefit_quality` | SCM / design paths |
| `placebo_distribution_sanity` | Placebo falsification |
| `fold_stability` | K-fold diagnostic |
| `shock_sensitivity`, `donor_count_sensitivity`, `outside_hull_sensitivity` | Robustness |
| `uncertainty_band_calibration` | Conformal / BRB |
| `sign_error_rate` | Directional characterization only |
| `abstention_blocked_rate` | Geometry / combo guards |

Full list: JSON `metric_catalog`.

---

## 8. Acceptance criteria taxonomy

| Class | Meaning |
|-------|---------|
| `hard_gate` | Must pass before any governed uncertainty claim (e.g. lower ≤ upper always) |
| `soft_gate` | Target band; proposed until OC calibrates (e.g. recovery slope ≈ 1) |
| `diagnostic_threshold` | Records behavior; no pass/fail for product |
| `research_characterization_only` | TROP / MTGP / BayesianTBR paths |
| `not_thresholded_yet` | Nominal FPR/coverage — **proposed** α/level until Level C evidence |

**Examples (proposed, not final):**

- Null FPR ≈ nominal α for governed candidates (Level C)  
- Coverage ≈ nominal level for interval methods (Level C)  
- `lower_le_upper_rate` = 1.0 (**hard_gate**)  
- `negative_half_width_rate` = 0.0 (**hard_gate**)  
- Degenerate interval rate bounded (**soft_gate** pending OC)  
- Point recovery slope ≈ 1.0 in clean injected worlds (**soft_gate**)  

---

## 9. Design protocol cards

| Implementation | Layer 3 → Layer 4 eligibility | Battery | Key worlds | Expected output |
|----------------|--------------------------------|---------|------------|-----------------|
| greedy_match_markets | `ready_with_caveats` | B→C | null, injected, pretrend, sparse geo | D5-STAT-DES-GMM-001 |
| rerandomization_wrapper | `ready_with_caveats` | B | + rerand vs bare sensitivity | D5-STAT-DES-RERAND-001 |
| tier-1 randomizers | `ready_with_caveats` | B | per-mode 001e SCM+JK reference | D5-STAT-DES-TIER1-001 |
| supergeos | `blocked_by_geometry` | A smoke only | supergeo_geometry | D5-STAT-SUPERGEO-BRIDGE-001 (after bridge) |
| trimmedmatch | `blocked_by_geometry` | A smoke only | trimmed_pair_geometry | D5-STAT-TRIM-BRIDGE-001 (after bridge) |
| quickblock / matchedpair | `deprecated_or_quarantine` | A | n/a | No OC until revival charter |

---

## 10. Estimator protocol cards

| Implementation | Eligibility | Blocker (if any) | Battery | Notes |
|----------------|-------------|------------------|---------|-------|
| SyntheticControlCVXPY | `ready_with_caveats` | G4, INV-D2-001 | B→C | SCM+JK characterization continuation |
| SyntheticControl (scipy) | `blocked_by_implementation_gap` | parity vs CVXPY | B after L3 gap | |
| AugSynthCVXPY | `blocked_by_implementation_gap` | G1–G8 | B characterization after gaps acknowledged | Point/JK/Conformal combos gated |
| AugSynth (non-CVXPY) | `research_only_protocol` | G1–G8 | B | Not default product path |
| TBR | `ready_with_caveats` | aggregate geometry only | B | **Blocked** on unit panel (TBR-UNIT-JK) |
| TBRRidge | `blocked_by_implementation_gap` | JK/JKP FPR | B→C | Identity vs TBR naming |
| DID | `ready_with_caveats` | embedded bootstrap ≠ registry BRB | B | D5-STAT-DID-BOOTSTRAP-001 |
| SyntheticDID | `research_only_protocol` | runner skip | B | |
| BayesianTBR / TROP / MTGP | `research_only_protocol` | RTP charter | B | Characterization only |

---

## 11. Inference protocol cards

| Mode | Eligibility | Battery | Key metrics |
|------|-------------|---------|-------------|
| point_estimate | `ready_for_protocol` | A | bias, MAE (diagnostic) |
| UnitJackKnife | `blocked_by_implementation_gap` (global) | C when paired | FPR, coverage, orientation |
| JKP | `blocked_by_implementation_gap` | C | pooled-CF caveat on TBRRidge |
| Kfold / TimeSeriesKfold | `ready_with_caveats` | B | fold_stability; diagnostic bands |
| BlockResidualBootstrap | `ready_with_caveats` | C | DEF-002 ordering; calibration |
| Conformal | `blocked_by_implementation_gap` | B restricted | IMPL-CONF-001; AugSynth blocked |
| Placebo | `ready_with_caveats` | B | falsification_only — not CI |
| DID_native_bootstrap | `ready_with_caveats` | B | relative CI policy open |
| Bayesian (registry) | `blocked_by_architecture_gap` | A | INV-015 ≠ MCMC |

---

## 12. Combination protocol cards

Minimum combination set (JSON `combination_id`):

| Combination | Geometry | Eligibility | Confirmatory? | Artifact |
|-------------|----------|-------------|---------------|----------|
| SCM + UnitJackKnife | single_cell_unit | `ready_with_caveats` | characterization | D5-STAT-SCM-JK-001 |
| SCM + Placebo | single_treated | `ready_with_caveats` | falsification_only | D5-STAT-SCM-PLACEBO-001 |
| AugSynthCVXPY point | single_cell_unit | `ready_with_caveats` | characterization | D5-STAT-AUGSYNTH-POINT-001 |
| AugSynthCVXPY + JK | single_cell_unit | **blocked** | blocked | D5-STAT-AUGSYNTH-JK-001 |
| AugSynthCVXPY + Conformal | single_cell_unit | **blocked** | blocked | D5-STAT-AUGSYNTH-CONFORMAL-001 |
| AugSynthCVXPY + KFold | single_cell_unit | `ready_with_caveats` | characterization | D5-STAT-AUGSYNTH-KFOLD-001 |
| TBR aggregate point | aggregate_two_row | `ready_with_caveats` | characterization | D5-STAT-TBR-AGG-001 ✅ |
| TBR + JK unit panel | single_cell_unit | **blocked** | blocked | D5-STAT-TBR-UNIT-JK-001 |
| TBRRidge + KFold / TSKFold / BRB / Conformal | single_cell_unit | mixed | characterization | D5-STAT-TBRRIDGE-* |
| TBRRidge + JK | single_cell_unit | **blocked** (impl gap) | characterization after pivot fix | D5-STAT-TBRRIDGE-JK-001 |
| TBRRidge + registry Bayesian | single_cell_unit | **blocked** (arch) | blocked | D5-STAT-TBRRIDGE-BAYESIAN-001 |
| DID + embedded bootstrap | single_cell_unit | `ready_with_caveats` | characterization | D5-STAT-DID-BOOTSTRAP-001 ✅ |
| multi-cell per-cell SCM+JK | multi_cell_per_cell | `ready_with_caveats` | characterization | D5-STAT-MCELL-PERCELL-001 ✅ |
| pooled multi-cell AugSynth | pooled_multi_cell | **blocked** | blocked | D5-STAT-MCELL-POOLED-001 |
| supergeo / trim + SCM+JK | bridge geometry | **blocked** | blocked | D5-STAT-*-BRIDGE-001 |

Per-row worlds, metrics, MC replicates: JSON `rows[]`.

---

## 13. Blocked-before-OC register

| Blocker | Combinations / families |
|---------|-------------------------|
| G1–G8 AugSynth fidelity | AugSynthCVXPY paths; JK/Conformal combos |
| IMPL-CONF-001 | AugSynth + Conformal |
| IMPL-JK-001 | AugSynth + UnitJackKnife |
| F-GEO-003 / A29 | supergeo flat SCM+JK |
| F-GEO-004 / A30 | trimmedmatch flat SCM+JK |
| INV-015 | TBRRidge + registry Bayesian |
| TBR geometry | TBR on unit panel + JK |
| Pooled multi-cell causal ADR | MCELL-POOLED-AUGSYNTH |
| TBRRidge JK/JKP calibration | TBRRidge + JK (high null FPR evidence) |

JSON: `known_blocked_combos`.

---

## 14. Research-only protocol register

| Path | Protocol mode |
|------|---------------|
| AugSynth (non-CVXPY) | Level B characterization only |
| SyntheticDID | Level B — runner skip |
| TROP, MTGP | Level B research_characterization_only |
| BayesianTBR MCMC | Level B — not registry Bayesian handler |
| synthetic_control legacy | deprecated — no OC |

---

## 15. Recommended execution order

1. **Level A smoke** — schema, orientation, callable paths for all non-quarantine rows  
2. **Geometry guards** — confirm blocked combos abstain or error (supergeo, trim, TBR unit, pooled multi-cell)  
3. **SCM + JK characterization** — continue D5-POW-001e / MAT-004 aligned strata (Level B→C)  
4. **AugSynth point** — after G1–G8 acknowledged; JK/Conformal remain blocked  
5. **TBR aggregate** — aggregate_two_row only  
6. **TBRRidge inference** — KFold/TSKFold/BRB before JK pivot calibration  
7. **Conformal** — restricted failure-redesign protocol unless new design lands  
8. **Supergeo / trim** — only after bridge ADR + D5-STAT-*-BRIDGE smoke  
9. **Multi-cell** — per-cell only; pooled causal protocol blocked  

---

## 16. Artifact naming convention

Pattern: **`D5-STAT-<DOMAIN>-<COMPONENT>-<NNN>`**

Examples:

- `D5-STAT-SCM-JK-001`  
- `D5-STAT-AUGSYNTH-POINT-001`  
- `D5-STAT-AUGSYNTH-JK-001` (blocked until IMPL-JK-001 closed)  
- `D5-STAT-AUGSYNTH-CONFORMAL-001` (blocked until IMPL-CONF-001)  
- `D5-STAT-TBR-AGG-001`  
- `D5-STAT-TBRRIDGE-KFOLD-001`  
- `D5-STAT-DID-BOOTSTRAP-001`  
- `D5-STAT-MCELL-PERCELL-001`  
- `D5-STAT-SUPERGEO-BRIDGE-001` · `D5-STAT-TRIM-BRIDGE-001`  

Each archive must cite Layer 4 `protocol_id` and record worlds, metrics, and acceptance classes used — **without** assigning trust roles.

---

## 17. JSON schema

Each `rows[]` entry includes:

| Field | Description |
|-------|-------------|
| `protocol_id` | Unique plan ID |
| `method_family` | Layer 2/3 family or `COMBINATION` |
| `combination_id` | Empty for family rows; e.g. `SCM-JK` |
| `method_type` | design \| estimator \| inference \| combination \| orchestration |
| `eligible_for_layer4` | Boolean — plan eligibility only |
| `eligibility_status` | ready_for_protocol \| ready_with_caveats \| blocked_* \| research_only \| deprecated |
| `blocked_by` | Gap IDs / geometry notes |
| `required_worlds` | Subset of DGP catalog |
| `required_metrics` | Subset of metric catalog |
| `acceptance_criteria` | `{metric, class, proposed_threshold}` |
| `battery_level` | A–E |
| `minimum_mc_replicates` | Recommended MC count |
| `confirmatory_or_characterization` | characterization \| confirmatory \| falsification_only \| blocked |
| `layer3_dependencies` | Layer 3 keys or combo deps |
| `expected_outputs` | D5-STAT-* artifact names |
| `promotion_allowed` | always **false** |
| `trust_role_allowed` | always **false** |
| `calibration_signal_allowed` | always **false** |
| `mmm_allowed` | always **false** |

Regenerate: `python -m panel_exp.validation.method_statistical_validation_protocol_001`

---

## 18. Executed D5-STAT evidence (characterization)

| Artifact | Status |
|----------|--------|
| `D5-STAT-SMOKE-CALLABLE-001` | ✅ smoke callable |
| `D5-STAT-SCM-JK-001` | ✅ Level B — `characterization_mixed_requires_followup` |
| `D5-STAT-AUGSYNTH-POINT-001` | ✅ Level B point — `characterization_mixed_requires_followup` |
| `D5-STAT-TBR-AGG-001` | ✅ Level B aggregate point — `characterization_mixed_requires_followup` |
| `D5-STAT-DID-BOOTSTRAP-001` | ✅ Level B DID bootstrap — `characterization_mixed_requires_followup` |
| `D5-STAT-MCELL-PERCELL-001` | ✅ Level B per-cell execution — `characterization_pass_with_caveats` |

**Next execution:** `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` (design-side).

**Design validation worlds:** Must be scoped to **implementation-validated behavior** from [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) and methods in [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) with **literature-aligned failure modes** from [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) — not intended-only behavior or ad hoc shortlists. `adapter_required` and `implementation_behavior_ambiguous` designs remain blocked or separately scoped.

**Geometry bridge:** ✅ [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) (**Accepted**) — canonical geometry IDs, bridge/blocked transitions, required metadata.

**Protocol v2 dependency:** Readout + geometry declarations per enhancement roadmap. **TROP:** requires **`TRIPLY_ROBUST_STATISTICAL_VALIDATION_PROTOCOL_001`** with nuisance-model correctness worlds — not covered by current Layer 4 protocol rows alone.

**Still blocked:** Trust framework auto-expansion · primary/secondary/directional roles · promotion.

---

## 19. Guardrails

- **No** primary / secondary / directional labels  
- **No** promotion (`promotion_allowed: false` on every row)  
- **No** CalibrationSignal / MMM expansion  
- **No** TrustReport / F-DECISION behavior change  
- **No** estimator, inference, or design code change in this PR  
- **No** heavy OC execution (Level A smoke only if explicitly scoped elsewhere)  
- Prior audits inform **protocol**, not automatic pass/fail without new OC  

---

## Stop condition

| Criterion | Status |
|-----------|--------|
| Layer 3 row coverage | ✅ 29/29 mapped |
| Combination protocol cards | ✅ 22 combos |
| DGP + metric catalogs | ✅ |
| Battery A–E defined | ✅ |
| Blocked / research registers | ✅ |
| JSON + tests | ✅ |
| Roadmap updates | ✅ |

---

*METHOD-STATISTICAL-VALIDATION-PROTOCOL-001 v1.0.0 — Layer 4 protocol complete; post-Layer-5 suitability framework is next.*
