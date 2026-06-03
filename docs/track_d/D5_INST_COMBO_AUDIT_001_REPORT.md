# D5-INST-COMBO-AUDIT-001 — Estimator × inference × geometry compatibility audit

**Artifact:** [`archives/D5_INST_COMBO_AUDIT_001_results.json`](archives/D5_INST_COMBO_AUDIT_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_combo_audit_001.py`  
**Lane:** Research — audit only; curated combinations (not full Cartesian product)

**Prior:** [`D5_INST_AUDIT_001_REPORT.md`](D5_INST_AUDIT_001_REPORT.md) · [`D5_INST_AUGSYNTH_001_REPORT.md`](D5_INST_AUGSYNTH_001_REPORT.md)

---

## Summary

**30 curated** estimator × inference × geometry tuples audited via **static code rules** + **targeted probes** on `scm_low_signal` panels (train=20, test=6).

**Overall verdict:** `compatibility_audited_curated_combinations_only`

| Status | Count |
|--------|------:|
| already_characterized | 9 |
| valid_candidate | 6 |
| invalid_by_interface | 5 |
| implemented_but_unvalidated | 5 |
| invalid_by_geometry | 3 |
| research_only | 2 |

---

## Required examples (headline)

| Combo | Status | Notes |
|-------|--------|-------|
| **AugSynthCVXPY + point** | already_characterized | D5-INST-AUGSYNTH-001 |
| **AugSynthCVXPY + JK** | already_characterized | D5-INST-AUGSYNTH-001 |
| **AugSynthCVXPY + Kfold** | **valid_candidate** | Probe success; OC battery before use |
| **AugSynthCVXPY + BRB** | invalid_by_interface | Not in `inference_support` catalog (BRB treats AS family in impl) |
| **AugSynthCVXPY + Placebo** | invalid_by_interface | Placebo not in catalog `inference_support` |
| **TBR + point / JK / JKP / Kfold** | valid_candidate (agg2) | **aggregate_two_series only** |
| **TBR + Placebo** | invalid_by_interface | `run_placebo` blocks `TBR` class |
| **TBR + unit panel** | invalid_by_geometry | 1×1 treated+control assert |
| **TBRRidge + Kfold/BRB** | already_characterized | D5-INST-TBRRIDGE-001 |
| **TBRRidge + JK/Conformal/JKP/Bayesian** | implemented_but_unvalidated | Wired; not D5 OC'd |
| **TBRRidge + Placebo** | invalid_by_interface | Probe failed (donor count / geometry) |
| **BayesianTBR + Bayesian** | research_only | Registry JAX path ≠ NUTS MCMC |
| **TROP + point** | research_only | No registry inference |
| **DID + native bootstrap** | already_characterized | Not registry `bootstrap` |
| **SCM + JK / Placebo** | already_characterized | 001e / PLACEBO-001 |

---

## Core rules (code-grounded)

1. **No blind Cartesian product** — only tuples with coherent interface + geometry + estimand.
2. **TBR ≠ TBRRidge** — TBR requires **aggregate 1×1**; TBRRidge is unit/agg restricted path (already characterized).
3. **Placebo** — single-treated only; blocks `TBR` class; ≥5 donors; `placebo()` single-unit assert.
4. **JK** — unit donor LOO; invalid on 2-row aggregate for SCM/AugSynth.
5. **DID** — `run_analysis` native bootstrap only; cumulative ATT (DEF-003).
6. **CalibrationSignal** — no combo audit entry is MMM-eligible except existing SCM JK policy.

---

## Valid OC candidates (do test)

- `TBR+point_estimate+aggregate_two_series`
- `TBR+UnitJackKnife+aggregate_two_series`
- `TBR+JKP+aggregate_two_series`
- `TBR+Kfold+aggregate_two_series`
- `AugSynthCVXPY+Kfold+single_cell_unit_level` (after dedicated battery)
- `TBRRidge+UnitJackKnife+single_cell_unit_level` (TBRRidge-002)

## Do not OC (blocked / invalid)

- Any **TBR** on **unit** multi-control panel
- **Placebo** on multi-treated natural assignment
- **Pooled multi-cell** instruments
- **supergeo / trim** as estimator readout (design-only)
- **BayesianTBR** for governed Track B / MMM

---

## Prioritized OC roadmap

| Priority | Battery | Combos |
|----------|---------|--------|
| **P1** | ~~D5-INST-TBR-001~~ ✅ | [`D5_INST_TBR_001_REPORT.md`](D5_INST_TBR_001_REPORT.md) — aggregate 1×1; JK blocked |
| **P0 after P1** | **AUDIT-010** | MMM readiness/gap — block invalid tuples from intake |

---

## Findings

1. **D5-COMBO-FIND-001:** TBR geometry gate is strict (1 treated + 1 control).
2. **D5-COMBO-FIND-002:** AugSynthCVXPY+Kfold is a valid candidate; BRB/Placebo need catalog/runtime clarity before OC.
3. **D5-COMBO-FIND-003:** TBRRidge+Placebo is not the same as SCM placebo (donor/thin-cell failures).
4. **D5-COMBO-FIND-004:** Registry `Bayesian` on BayesianTBR is research-only and not NUTS MCMC.

**Next:** ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010**.
