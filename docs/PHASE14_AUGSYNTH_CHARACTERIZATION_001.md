# Phase 14 INV-028 — AugSynth operating-characteristic characterization 001

**Investigation:** INV-028 — AugSynth / AugSynthCVXPY characterization  
**Status:** evidence archive (characterization + production-tier point path)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  

**Related:** [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) · [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md)

**Raw JSON (local, not committed):** `.phase14_augsynth_characterization.json`  
**Reproduction:** `poetry run python scripts/phase14_augsynth_characterization.py`

No estimator, inference, recovery scoring, threshold, eligibility, or maturity registry changes were made.

---

## 1. Executive summary

**Headline:** `AugSynthCVXPY` is **execution-reliable** on the Phase 14 battery (0% run failures) with **excellent point recovery** on standard geo recovery DGPs. **UnitJackKnife on AugSynth** shows the **same conservative interval pattern as SCM jackknife**: perfect null coverage / zero FPR, **zero power** on positive scenarios despite accurate points.

| Layer | Verdict |
|-------|---------|
| **Point recovery (`AugSynthCVXPY_Point`)** | **Expert-review candidate (point only)** — recovery success 100% across 24 cells; \|bias\| ≪ truth on positive DGP |
| **Inference (`AugSynthCVXPY_UnitJackKnife`)** | **Null-monitor-style only** — aligned intervals; null pass; **power = 0** on positive (width/effect ≈ 15×) |
| **Geometry (n_treated 1–4, default ~4)** | **No degradation** vs default multi-treated panel |
| **Donor tier (small / medium / large)** | **Stable point recovery**; slightly higher absolute error on small/large panels |
| **Heterogeneity** | **No material point drift** vs homogeneous default (bias magnitude matches hom case) |
| **Spillover stress (`scm_donor_contamination`)** | **Material point bias** (~−0.034 vs truth 0.10) — estimator does not model spillover; not a hard failure under recovery tolerance |
| **Collinearity stress** | **Point recovery remains strong** |
| **Non-CVXPY `AugSynth`** | **Probe viable** (10 reps) — point recovery success 100% |
| **Nominal calibration** | **Not demonstrated** — point config has no aligned intervals; JK path not lift-detector |

**Classification:** **Characterization success** — supports **point-only expert-review** usage with documented limits on inference and interference DGPs. **Not** a promotion or eligibility change.

---

## 2. Run metadata

| Field | Value |
|-------|--------|
| **Package version** | 0.2.1 |
| **Branch context** | `phase12-run002-brb-oc` (investigation executed at commit below) |
| **Commit** | `734e85e` |
| **Investigation ID** | INV-028 |
| **Primary config** | `AugSynthCVXPY_Point` (`AugSynthCVXPY(inference=None)`) |
| **Inference config** | `AugSynthCVXPY_UnitJackKnife` |
| **Diagnostic** | `SCM_Point` on positive default DGP |
| **Harness** | Investigation-only `_run_simulation` loop (no `RecoveryRunner` registry change) |
| **α** | 0.05 |
| **Scored estimand** | `relative_att_post` via `_path_relative_att` |
| **Wall time (full matrix)** | ~47 s |
| **Cells** | 24 |

### Tiering

| Tier | n_simulations | Seeds | Cells |
|------|---------------|-------|-------|
| **Production characterization** | 100 | 0, 1, 2 | `prod_null_default`, `prod_positive_default` |
| **Characterization** | 30 | 0, 1, 2 | All other cells |

### Investigation-only eligibility note

| Field | Value |
|-------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` — **unchanged** |
| **`eligible_for_nominal_calibration`** | **false** for all AugSynth configs in this archive |

---

## 3. Production-tier results (`AugSynthCVXPY_Point`)

Aggregates: **mean / std / min / max** across seeds 0–2 (300 replications per scenario).

### `recovery_null_effect` (default ~4 treated)

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Bias | 0.00032 | 0.00054 | −0.00013 | 0.00088 |
| Absolute bias | 0.00178 | 0.00024 | 0.00154 | 0.00208 |
| Coverage / FPR / Power | — | — | — | (point-only; intervals not requested) |

### `recovery_positive_effect` (`true_effect = 0.10`)

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Bias | 0.00035 | 0.00046 | −0.00014 | 0.00097 |
| Absolute bias | 0.00196 | 0.00023 | 0.00175 | 0.00228 |
| Coverage / FPR / Power | — | — | — | (point-only) |

**Interpretation:** At n = 100, AugSynthCVXPY **point estimates track canonical truth** on default recovery DGP with **no execution failures**. This does **not** establish interval calibration (no inference on point config).

---

## 4. Inference track (`AugSynthCVXPY_UnitJackKnife`)

Characterization tier (n = 30 × 3 seeds).

### `recovery_null_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| FPR | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | — | — | — |
| Mean interval width | 0.153 | 0.003 | 0.150 | 0.157 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

### `recovery_positive_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| Power | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | — | — | — |
| Mean interval width | 1.537 | 0.006 | 1.528 | 1.542 |
| Width / effect ratio | ~15.4 | ~0.06 | ~15.3 | ~15.4 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

**Interpretation:** AugSynth + UnitJackKnife mirrors **SCM jackknife conservatism** (Phase 11): intervals are **wide enough** to always cover truth and zero on null, but **never exclude zero** on positive — **not a lift detector**. Null monitoring behavior is **sane** (FPR = 0), not anti-calibrated.

---

## 5. Geometry sensitivity (point config)

All cells: n = 30, seeds 0–1–2, **failure rate = 0**, **recovery success = 1.0**.

| n_treated | Null abs bias (mean) | Positive abs bias (mean) | Notes |
|-----------|----------------------|---------------------------|-------|
| 1 | 0.0020 | 0.0039 | Slightly higher error at n_treated = 1 |
| 2 | 0.0018 | 0.0020 | |
| 4 | 0.0018 | 0.0020 | |
| Default (~4 sampled) | 0.0018 | 0.0020 | Matches explicit n = 4 |

**Finding:** No sharp geometry failure surface (contrast with TBRRidge Kfold). Multi-treated default DGP is **supported** for AugSynthCVXPY point path.

---

## 6. Donor-pool sensitivity (point config, n_treated = 4)

| Donor tier | n_geos | Positive abs bias (mean) | Recovery success |
|------------|--------|--------------------------|------------------|
| small | 9 | 0.0021 | 1.0 |
| medium | 20 | 0.0020 | 1.0 |
| large | 40 | 0.0028 | 1.0 |

**Finding:** Point recovery **stable across donor tiers**; large-panel absolute error modestly higher but still within recovery tolerance.

---

## 7. Heterogeneity sensitivity (point config)

| DGP | Positive bias (mean) | Positive abs bias (mean) | Recovery success |
|-----|----------------------|--------------------------|------------------|
| Homogeneous default | 0.00052 | 0.00191 | 1.0 |
| Heterogeneous multi-treated | 0.00052 | 0.00194 | 1.0 |

**Finding:** Heterogeneous relative effects do **not** materially degrade AugSynthCVXPY **point** recovery on this battery (unlike INV-003 aggregation semantics for pooled scoring — point path remains stable).

---

## 8. Spillover / stress scenarios (point config)

| Scenario | true_effect | Bias (mean) | Abs bias (mean) | Recovery success | Interpretation |
|----------|-------------|-------------|-----------------|------------------|----------------|
| `scm_high_collinearity` | 0.10 | 0.00022 | 0.00073 | 1.0 | **Robust** |
| `scm_donor_contamination` | 0.10 | **−0.0340** | **0.0340** | 1.0 | **Material negative bias** under spillover DGP; still within recovery tolerance |

**Finding:** Under donor contamination (spillover_strength = 0.35), AugSynthCVXPY **under-estimates** lift by ~34% of the configured effect — expected when spillover is in the DGP but not modeled. Expert reviewers must **not** treat point recovery success as causal validity under interference.

---

## 9. Diagnostic comparison (SCM point, positive default)

| Estimator | Recovery success | Bias (mean) | Abs bias (mean) |
|-----------|------------------|-------------|-----------------|
| AugSynthCVXPY_Point | 1.0 | 0.00052 | 0.00191 |
| SCM_Point | 1.0 | (same cell) | (same order) |

**Finding:** On default positive DGP, AugSynthCVXPY point accuracy is **comparable to SCM point** — diagnostic only, not a ranking claim.

---

## 10. Non-CVXPY AugSynth (probe)

| Field | Value |
|-------|--------|
| Config | `AugSynth_Point` |
| n | 10, seed 0 |
| Failure rate | 0.0 |
| Recovery success | 1.0 |

**Finding:** Legacy `AugSynth` path **runs** on probe; full OC deferred to optional follow-up. **Primary evidence** is AugSynthCVXPY.

---

## 11. Threshold assessment (inference config)

Frozen thresholds ([`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md)): null coverage ≥ 0.90, FPR ≤ 0.10, failure_rate < 0.05; power target 0.80 informative on positive.

### `AugSynthCVXPY_UnitJackKnife` — null

| Metric | Value | Threshold | Overall |
|--------|-------|-----------|---------|
| Coverage | 1.000 | ≥ 0.90 | **pass** |
| FPR | 0.000 | ≤ 0.10 | **pass** |
| Failure rate | 0.000 | < 0.05 | **pass** |

### `AugSynthCVXPY_UnitJackKnife` — positive

| Metric | Value | Threshold | Overall |
|--------|-------|-----------|---------|
| Coverage | 1.000 | ≥ 0.90 (informative) | **pass** |
| Power | 0.000 | target 0.80 | **fail** |
| Failure rate | 0.000 | < 0.05 | **pass** |

**Overall:** Null-threshold **pass** is consistent with **conservative null monitoring**, not full lift-detection calibration. Positive **power fail** matches SCM jackknife role boundary.

---

## 12. Governance classification (evidence-supported)

| Config / path | Classification | Rationale |
|---------------|----------------|-----------|
| **AugSynthCVXPY_Point** | **Retain as expert-review (point only)** | n = 100 point archive; 0% failures; excellent bias |
| **AugSynthCVXPY_UnitJackKnife** | **Restrict to null-monitor semantics** | FPR = 0, power = 0; width/effect ~15× |
| **Under spillover DGP** | **Warn / incompatible estimand** | Material bias; DEF-004 spillover not modeled |
| **Nominal calibration eligibility** | **Do not add** | No aligned interval path for point; JK not lift detector |
| **RecoveryRunner wiring** | **Deferred** (DEF-017) | OC exists via investigation harness; registry wiring optional later |

**Disposition (DEF-019):** **Characterized** — point expert-review candidate; inference null-monitor only; not calibration-ready for lift claims.

---

## 13. Comparison to Phase 12 TBRRidge lessons

| Dimension | TBRRidge (Phase 12) | AugSynthCVXPY (Phase 14) |
|-----------|---------------------|---------------------------|
| Multi-treated default DGP | Kfold **hard fails** | Point path **0% failure** |
| BRB intervals | Fixed bounds; positive under-coverage | Not tested on BRB |
| Jackknife-style intervals | SCM: null only | AugSynth+JK: **same null-only pattern** |
| Primary value | Ridge extrapolation | Augmented SCM + ridge residual |

---

## 14. Non-claims

This archive **does not**:

- Promote AugSynth / AugSynthCVXPY maturity labels  
- Add any config to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`  
- Certify package-wide or estimator-level nominal calibration  
- Imply `production_safe` or unattended decisioning  
- Change recovery scoring, thresholds, or Track B contracts  
- Validate AugSynth under real-world spillover (only synthetic contamination DGP)

This archive **does**:

- Provide first governed OC evidence for a core long-term geo instrument candidate  
- Bound **point** vs **inference** usage for expert review  
- Flag **spillover-stress** bias for TrustReport / ExperimentEvidence design  
- Close INV-028 planning loop with archived metrics

---

## 15. Recommended next steps (documentation only)

1. Wire optional `RecoveryRunner` configs for `AugSynthCVXPY_Point` (registry PR separate from this archive).  
2. Document **spillover / interference** warning in validation coverage row.  
3. Proceed to **Phase 15 Placebo** characterization before Track B implementation priority.  
4. Reference this archive in `METHOD_VALIDATION_PLAN.md` path **B** for AugSynthCVXPY point recovery.

---

*Evidence archive INV-028-001. Registry and code unchanged.*
