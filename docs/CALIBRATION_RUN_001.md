# Calibration run 001 — production nominal calibration evidence

**Run ID:** CALIBRATION_RUN_001  
**Generated:** 2026-05-20  
**Harness:** `panel_exp.validation.production_nominal_calibration.run_production_nominal_calibration`  
**Wall time:** ~416 s (~6.9 min)  
**Raw JSON (local, not committed):** `.calibration_run_001.json` at repo root during generation

This document archives **operating-characteristic evidence** only. No estimator, inference, or recovery scoring changes were made for this run.

---

## 1. Run metadata

| Field | Value |
|-------|--------|
| **Package version** | 0.2.1 |
| **Branch** | `estimator-maturity-metadata` |
| **Commit** | `6ff3f4f62987066394f14a7820c2acdec39a3880` |
| **α (nominal)** | 0.05 |
| **n_simulations** | 100 per config × scenario × seed |
| **random_seeds** | 0, 1, 2 |
| **Scenarios** | `recovery_null_effect`, `recovery_positive_effect` |
| **Eligible configs** | `SCM_UnitJackKnife`, `TBRRidge_Kfold`, `TBRRidge_BlockResidualBootstrap` |
| **Excluded** | `DID_Bootstrap` (not in eligible set; relative-ATT interval unsupported) |
| **DGP** | Standard recovery calibration scenarios; `missingness_policy=none` on null/positive scenarios |

---

## 2. Results by estimator × scenario

Aggregates are **mean / std / min / max** across three seeds. Per-seed runs used `RecoveryRunner` with aligned-interval eligibility enforced by `production_nominal_calibration`.

### SCM_UnitJackKnife — `recovery_null_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| False positive rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Power | — | — | — | — (not requested on null) |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Interval estimand:** `relative_att_post` (aligned)  
- **Warnings (all seeds):** stale harness text *"CI smoke is not production calibration…"* (n=100; advisory only)

### SCM_UnitJackKnife — `recovery_positive_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| False positive rate | — | — | — | — (not requested on positive) |
| Power | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Warnings:** harness smoke note; **Power below target (0.000 < 0.8)** on every seed

### TBRRidge_BlockResidualBootstrap — `recovery_null_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 0.000 | 0.000 | 0.000 | 0.000 |
| False positive rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Power | — | — | — | — |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none (runs complete; intervals/significance miscalibrated)  
- **Interval estimand:** `relative_att_post` (aligned)  
- **Warnings:** FPR exceeds threshold (1.000 > 0.1); coverage below null range (0.000 < 0.9)

### TBRRidge_BlockResidualBootstrap — `recovery_positive_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 0.000 | 0.000 | 0.000 | 0.000 |
| False positive rate | — | — | — | — |
| Power | 1.000 | 0.000 | 1.000 | 1.000 |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Note:** Power = 1.0 with coverage = 0.0 on positive scenario indicates **significance-based power without interval coverage** on this DGP/inference pairing—not nominal interval calibration.

### TBRRidge_Kfold — both scenarios

**Not eligible for aggregation** — all six per-seed runs marked `eligible_for_nominal_calibration=False`.

| Per-seed (all seeds 0–2) | Value |
|--------------------------|--------|
| `interval_estimand` | `unavailable` |
| `interval_aligned` | false |
| `ineligible_reason` | `interval_not_aligned` |
| Coverage / FPR | NaN (unavailable) |
| **Failure rate** | **1.000** (100% failed replications) |
| Recovery success rate | NaN |

Every replication failed before aligned intervals were available (consistent with CI smoke behavior on multi-geo `recovery_*` panels).

---

## 3. Threshold assessment

Thresholds (from Phase 5 / `ROADMAP_V3` §6.1): **coverage ≥ 0.90**, **FPR ≤ 0.10**, **failure_rate < 0.05** on null scenarios.

### Null scenario (`recovery_null_effect`)

| Config | Coverage | FPR | Failure rate | Overall |
|--------|----------|-----|--------------|---------|
| SCM_UnitJackKnife | **pass** (1.00) | **pass** (0.00) | **pass** (0.00) | **pass** |
| TBRRidge_BlockResidualBootstrap | **fail** (0.00) | **fail** (1.00) | **pass** (0.00) | **fail** |
| TBRRidge_Kfold | **unavailable** | **unavailable** | **fail** (1.00) | **fail** |

### Positive scenario (`recovery_positive_effect`)

| Config | Power (informative) | Failure rate | Notes |
|--------|-------------------|--------------|-------|
| SCM_UnitJackKnife | **fail** (0.00; target ≥ 0.80) | **pass** (0.00) | Intervals cover but do not reject null on positive DGP |
| TBRRidge_BlockResidualBootstrap | **pass** (1.00) | **pass** (0.00) | Significance always true; coverage still 0.0 |
| TBRRidge_Kfold | **unavailable** | **fail** (1.00) | No eligible runs |

**Harness status labels (aggregates):** SCM null → coverage/fpr **pass**; SCM positive → power **fail**; BRB null → coverage/fpr **fail**; BRB positive → power **pass**, coverage **fail**; Kfold → all **unavailable** at aggregate level.

---

## 4. Stability across seeds

| Config × scenario | Material change across seeds? |
|-------------------|-------------------------------|
| SCM_UnitJackKnife × null | **No** — identical metrics (std = 0) |
| SCM_UnitJackKnife × positive | **No** — identical metrics (std = 0) |
| TBRRidge_BlockResidualBootstrap × null | **No** — identical (coverage 0, FPR 1.0 every seed) |
| TBRRidge_BlockResidualBootstrap × positive | **No** — identical (coverage 0, power 1.0 every seed) |
| TBRRidge_Kfold × both | **No** — 100% failure rate every seed |

**Interpretation:** Metrics are **stable** across seeds but that stability reflects **degenerate** outcomes (perfect SCM null calibration; complete BRB miscalibration; total Kfold failure)—not healthy sampling variation.

---

## 5. Conclusions

### Is nominal calibration demonstrated?

**Partially — only for SCM_UnitJackKnife on the null scenario.**

- **Demonstrated (null, n=100):** SCM unit jackknife meets coverage ≥ 0.90 and FPR ≤ 0.10 with zero failures.
- **Not demonstrated:** TBRRidge_BlockResidualBootstrap (null FPR = 1.0, coverage = 0.0).
- **Not assessable:** TBRRidge_Kfold (100% replication failure; intervals never aligned).

Package-level claim *“aligned inference configs are nominally calibrated”* is **not supported** for 2 of 3 eligible configs.

### Which configs appear reliable?

| Config | Verdict |
|--------|---------|
| **SCM_UnitJackKnife** | **Reliable on null calibration metrics** at n=100; suspiciously perfect coverage (1.0) warrants follow-up (interval width / test strength), not promotion without review |
| **TBRRidge_BlockResidualBootstrap** | **Unreliable** for nominal null calibration on default recovery panels |
| **TBRRidge_Kfold** | **Non-functional** for production calibration on default `recovery_*` scenarios (total failure rate) |

### Which configs remain weak?

1. **TBRRidge_Kfold** — cannot produce aligned intervals on standard recovery DGP (failure_rate = 1.0).  
2. **TBRRidge_BlockResidualBootstrap** — aligned intervals export but **anti-calibrated** on null (always significant / never covers).  
3. **SCM_UnitJackKnife (positive scenario)** — power = 0.0 despite point recovery success; not useful for lift detection via current significance path.

### Is expert-review positioning unchanged?

**Yes, with sharper evidence.**

- **Unchanged:** No `production_safe` promotion; DID still excluded; expert-review with human checks remains the appropriate posture (`docs/PHASE8_ALGORITHM_AUDIT.md`).
- **Updated:** Phase 8 blocker *“no n≥100 artifact”* is **closed for this run** — evidence now exists and shows **mixed** results, not blanket readiness.
- **Recommendation:** Wider expert-review use of **SCM + unit jackknife** on similar panels may be reasonable **with caveats** (null calibration pass, positive power fail). **TBRRidge inference configs should not be cited as calibrated** until root-caused (document failures; do not tune scenarios or thresholds in this run).

---

*Evidence-only archive. Fixes, scenario changes, and estimator/inference work are explicitly out of scope for run 001.*
