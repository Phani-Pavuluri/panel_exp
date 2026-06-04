# METHOD-COMBINATION-VALIDATION-MATRIX-001

**Document ID:** METHOD-COMBINATION-VALIDATION-MATRIX-001  
**Type:** Layer 5 design × estimator × inference combination matrix — **pre-suitability**  
**Status:** **complete** (register + generator; no OC execution)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) Layer 5

**Machine-readable register:** [`track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json`](track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json) (30 rows; regenerate: `python -m panel_exp.validation.method_combination_validation_matrix_001`)

**Generator:** [`panel_exp/validation/method_combination_validation_matrix_001.py`](../panel_exp/validation/method_combination_validation_matrix_001.py)

**Primary inputs:** Layers 1–4 artifacts · prior D5 / COMBO audits (**evidence only**)

**Guardrails:** No trust roles · no promotion · no suitability claims · no TrustReport/CalibrationSignal/MMM/LLM changes

---

## 1. Purpose

Answer **“Which design × estimator × inference × geometry combinations are valid candidates for future statistical OC — and which are blocked, bridge-required, research-only, or quarantined?”**

Layer 5 is the **final pre-suitability layer**. It converts Layers 1–4 into a structured matrix with `validation_matrix_status` and `allowed_next_action` per combination.

| Question | Layer 5 answers |
|----------|-----------------|
| Valid OC candidate? | `ready_for_oc_execution` / `ready_for_oc_with_caveats` |
| Blocked before OC? | `blocked_before_oc` / `blocked_needs_bridge` |
| Research / quarantine? | `research_only_oc` / `quarantine_or_deprecate` |
| What runs next? | D5-STAT execution queue §12 |

**Not answered here:** primary/secondary/directional roles · TrustReport eligibility · production readiness.

**Critical wording:** **Ready for OC execution** means literature identity is defined, implementation is understood, geometry is not silently unsupported, Layer 4 protocol exists, and a D5-STAT-* run is the next allowed action. It does **not** mean statistically validated, trusted, or suitable.

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Program layer | Status |
|---------------|--------|
| Layer 1 — Code inventory | ✅ |
| Layer 2 — Literature alignment | ✅ |
| Layer 3 — Implementation validation | ✅ |
| Layer 4 — Statistical validation protocol | ✅ |
| **Layer 5 — Combination matrix** | ✅ **This artifact** |
| Suitability framework | ✅ [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) |
| D5-STAT smoke (Level A) | ✅ [`D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) |
| SCM+JK Level B | ✅ [`D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) |
| AugSynth point Level B | ✅ [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) |
| TBR aggregate point Level B | ✅ [`D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md) |
| Next concrete work | **`D5-STAT-DID-BOOTSTRAP-001`** |

---

## 3. Inputs from Layers 1–4

| Layer | Use in matrix |
|-------|----------------|
| 1 | Canonical names, modules, geometry hints |
| 2 | `supported_by_literature`, estimand references |
| 3 | `implementation_status`, gap IDs → `blocked_by` |
| 4 | Protocol eligibility, worlds, metrics, D5-STAT artifact names |

**Coverage:** Every Layer 4 `combination_id` (22) maps to ≥1 matrix row; 8 extended rows add tier-1 SCM+JK, pooled SCM+JK, supergeo/trim AugSynth point, TBR+KFold aggregate, TBRRidge+Placebo, SDID, etc.

---

## 4. Matrix construction method

| Step | Action |
|------|--------|
| 1 | Load [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json`](track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json) |
| 2 | For each `combination_id` row, map `eligibility_status` → `validation_matrix_status` |
| 3 | Attach combination dimensions from `COMBO_DIMENSIONS` catalog |
| 4 | Derive `allowed_next_action` from status + battery level |
| 5 | Append extended combinations required by program spec |
| 6 | Emit JSON; all forbidden flags **false** |

---

## 5. Status taxonomy

| `validation_matrix_status` | Meaning |
|---------------------------|---------|
| `ready_for_oc_execution` | Layer 4 ready_for_protocol; smoke/characterization may proceed |
| `ready_for_oc_with_caveats` | Callable with documented gaps (INV-D1, G7, etc.) |
| `blocked_before_oc` | Implementation or architecture gap — fix before OC |
| `blocked_needs_bridge` | Geometry / pooling / flat-readout bridge ADR required |
| `research_only_oc` | TROP, MTGP, BayesianTBR MCMC, SDID skip paths |
| `quarantine_or_deprecate` | Legacy paths — no OC until charter |
| `not_applicable` | Reserved — unused in v1 register |

| `allowed_next_action` | Meaning |
|----------------------|---------|
| `run_smoke_protocol` | Level A D5-STAT-SMOKE-* |
| `run_characterization_protocol` | Level B D5-STAT-* |
| `run_calibration_protocol` | Level C D5-STAT-* |
| `write_bridge_adr` | F-GEO-003/004, pooling ADR |
| `fix_implementation_gap` | G1–G8, IMPL-JK-001, TBRRidge JK calibration |
| `research_only` | Characterization without product claims |
| `quarantine_or_deprecate` | No OC |
| `no_action` | Blocked with no scheduled run |

---

## 6. Combination dimensions

Each matrix row includes:

`combination_id` · `design_family` · `estimator_family` · `inference_family` · `geometry` · `treatment_structure` · `estimand` · `effect_scale` · `interval_semantics` · `data_level` · `supported_by_literature` · `implementation_status` · `statistical_protocol_status` · `validation_matrix_status` · `blocked_by` · `required_bridge` · `required_d5_stat_artifact` · `minimum_battery_level` · `required_metrics` · `known_failure_modes` · `allowed_next_action`

---

## 7. Core ready-for-OC candidates

| combination_id | Status | D5-STAT artifact | Caveats |
|----------------|--------|------------------|---------|
| SCM-JK | `ready_for_oc_with_caveats` | D5-STAT-SCM-JK-001 | MAT-004, INV-D1-001 |
| SCM-PLACEBO | `ready_for_oc_with_caveats` | D5-STAT-SCM-PLACEBO-001 | single-treated scope |
| AUGSYNTH-POINT | `ready_for_oc_with_caveats` | D5-STAT-AUGSYNTH-POINT-001 | G1–G8 open on estimator |
| TBR-AGG-POINT | `ready_for_oc_with_caveats` | D5-STAT-TBR-AGG-001 ✅ | aggregate 2-row only; mixed null/shock |
| DID-BOOTSTRAP | `ready_for_oc_with_caveats` | D5-STAT-DID-BOOTSTRAP-001 | relative CI policy open |
| MCELL-PERCELL-SCM-JK | `ready_for_oc_with_caveats` | D5-STAT-MCELL-PERCELL-001 | per-cell only |
| TBRRIDGE-KFOLD / TSKFOLD / BRB / CONFORMAL | `ready_for_oc_with_caveats` | D5-STAT-TBRRIDGE-* | diagnostic / calibration paths |

---

## 8. Blocked-before-OC combinations

| combination_id | Blocker |
|----------------|---------|
| AUGSYNTH-JK | IMPL-JK-001 unsafe strata |
| AUGSYNTH-CONFORMAL | IMPL-CONF-001 interval redesign |
| TBRRIDGE-JK | High null FPR — pivot calibration |
| TBRRIDGE-BAYESIAN-REG | INV-015 registry ≠ MCMC |
| TBRRIDGE-PLACEBO | Placebo not wired for TBRRidge |

---

## 9. Bridge-required combinations

| combination_id | Bridge |
|----------------|--------|
| SUPERGEO-SCM-JK | F-GEO-003 |
| TRIM-SCM-JK | F-GEO-004 |
| SUPERGEO-AUGSYNTH-POINT | F-GEO-003 |
| TRIM-AUGSYNTH-POINT | F-GEO-004 |
| MCELL-POOLED-AUGSYNTH | multicell causal pooling ADR |
| MCELL-POOLED-SCM-JK | multicell causal pooling ADR |
| TBR-UNIT-JK | TBR aggregate-only geometry |

---

## 10. Research-only combinations

| combination_id | Mode |
|----------------|------|
| TROP-RESEARCH | Level B characterization only |
| MTGP-RESEARCH | Level B Bayesian research |
| BAYESIANTBR-MCMC | MCMC path ≠ registry handler |
| SDID-POINT | Runner skip / research |

---

## 11. Quarantine / deprecation candidates

No combination rows use `quarantine_or_deprecate` in v1 — legacy design paths (quickblock, matchedpair) remain **not_applicable** at combination level until a product combo is declared. Family-level quarantine is documented in Layer 3.

---

## 12. Required D5-STAT execution queue

Recommended order (not authorization to promote):

1. **D5-STAT-SMOKE-CALLABLE-001** — schema, callable paths, orientation, geometry guards  
2. **D5-STAT-SCM-JK-001** — SCM+JK unit-panel null/injected characterization  
3. **D5-STAT-AUGSYNTH-POINT-001** — AugSynth point recovery diagnostics  
4. **D5-STAT-AUGSYNTH-JK-001** — blocked until IMPL-JK-001; protocol exists for future run  
5. **D5-STAT-TBR-AGG-001** — aggregate 2-row only ✅  
6. **D5-STAT-DID-BOOTSTRAP-001** — embedded bootstrap characterization **(next)**  
7. **D5-STAT-TBRRIDGE-INF-001** — TBRRidge KFold/TSKFold/BRB family  
8. **D5-STAT-MCELL-PERCELL-001** — per-cell multi-cell only  

JSON: `d5_stat_execution_queue` · `d5_stat_blocked_queue`.

---

## 13. Required bridge ADR queue

- F-GEO-003 supergeo unit-panel bridge  
- F-GEO-004 trimmedmatch flat readout bridge  
- multicell causal pooling ADR (pooled lift semantics)  

---

## 14. Implementation-fix queue

- G1–G8 AugSynthCVXPY fidelity  
- IMPL-JK-001 AugSynth strata  
- IMPL-CONF-001 Conformal redesign  
- TBRRidge JK/JKP pivot calibration  
- INV-015 registry Bayesian vs MCMC  
- SyntheticControl scipy parity vs CVXPY  

---

## 15. Matrix JSON schema

See JSON `rows[]` — forbidden flags always false:

`promotion_allowed` · `trust_role_allowed` · `calibration_signal_allowed` · `mmm_allowed`

Regenerate: `python -m panel_exp.validation.method_combination_validation_matrix_001`

---

## 16. What this matrix does not authorize

- Primary / secondary / directional evidence roles  
- TrustReport or F-DECISION export eligibility  
- CalibrationSignal or MMM integration  
- Production readiness or method promotion  
- Statistical validation (requires executed D5-STAT-* archives)  
- Suitability matrix cells (Layer 6 framework)  

---

## 17. Next concrete work: D5-STAT-DID-BOOTSTRAP-001

**TBR aggregate point Level B** complete — see [`track_d/D5_STAT_TBR_AGG_001_REPORT.md`](track_d/D5_STAT_TBR_AGG_001_REPORT.md) (`characterization_mixed_requires_followup`).

**Next:** DID bootstrap characterization — **not** TrustReport wiring until OC archives exist.

---

## 18. Guardrails

- **No** estimator, design, or inference code changes in this PR  
- **No** OC execution  
- **No** promotion or eligibility changes  
- **No** TrustReport / F-DECISION / CalibrationSignal / MMM / LLM changes  
- **No** primary/secondary/directional labels  
- Ready-for-OC ≠ validated ≠ trusted  

---

## Stop condition

| Criterion | Status |
|-----------|--------|
| Layer 4 combo coverage | ✅ 22/22 |
| Extended coverage rows | ✅ 30 total |
| D5-STAT queues | ✅ |
| Blocked / ready registers | ✅ |
| JSON + tests | ✅ |
| Roadmap updates | ✅ |

---

*METHOD-COMBINATION-VALIDATION-MATRIX-001 v1.0.0 — Layer 5 complete; D5-STAT-DID-BOOTSTRAP-001 is next.*
