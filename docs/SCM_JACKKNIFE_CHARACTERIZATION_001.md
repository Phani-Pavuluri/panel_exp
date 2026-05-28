# SCM UnitJackKnife characterization 001

**Date:** 2026-05-26  
**Phase:** 11  
**Config:** `SCM_UnitJackKnife`  
**Inputs:** Run 001 findings, existing `RecoveryRunner` / `SyntheticWorld` infrastructure, no estimator or inference code changes  
**Constraint:** Characterization only. No estimator math, jackknife implementation, thresholds, scoring, eligibility registry, or scenario tuning changed.

---

## 1. Objective

Determine whether the Phase 10 / Run 001 SCM UnitJackKnife pattern—null coverage = 1.0, FPR = 0.0, positive-scenario power = 0.0 with accurate point estimates—is expected conservatism or evidence of a defect.

---

## 2. Experimental design

- **Matrix size:** 144 cells = 4 treated counts × 3 donor tiers × 3 noise levels × 4 effect sizes (`0.00`, `0.05`, `0.10`, `0.20`).
- **Replications per cell:** 25 synthetic simulations.
- **Seed-stability check:** 3 additional runs for one representative geometry (`n_treated=4`, donor tier = `medium`, noise = `medium`, effect = `0.10`) at base seeds 0 / 100 / 200.
- **Outcome metrics recorded per cell:** coverage, FPR, power, average interval width, width/effect ratio, significance rate, recovery success rate, failure rate.
- **Donor-tier definition used in this characterization:**
  - `small`: `n_geos = n_treated + 5` → always 5 donors
  - `medium`: `n_geos = 20` → donors vary with treated count (`19, 18, 16, 12`)
  - `large`: `n_geos = 40` → donors vary with treated count (`39, 38, 36, 32`)
- **Noise scale:** `low = 0.4`, `medium = 0.8`, `high = 1.6`.

This means the matrix cleanly varies treated count, but donor tier also changes total panel geometry. Therefore, any donor-tier effect should be interpreted as a geometry effect rather than a pure donor-count causal attribution.

---

## 3. Headline findings

1. **No execution failures occurred.** Failure rate was `0.0` in all 144 cells.
2. **Null over-coverage was perfectly persistent.** Every null cell had coverage = `1.0` and FPR = `0.0`.
3. **Power was `0.0` in every positive-effect cell**, including single-treated, low-noise, large-effect settings.
4. **Point recovery remained excellent.** Recovery success rate was `1.0` in every cell; mean point estimates tracked truth closely.
5. **Interval width did not inflate with treated count.** If anything, mean width fell slightly as treated count increased.
6. **The strongest driver was panel geometry / donor tier, not noise.** Larger donor-tier panels produced much wider intervals; changing noise had almost no effect on average width.
7. **Width scaled almost linearly with effect size.** The width/effect ratio stayed roughly constant within a geometry, so larger effects did not improve power.
8. **Behavior was stable across seeds.** The representative seed-stability subset reproduced the same pattern: coverage = `1.0`, power = `0.0`, width/effect ratio ≈ `15`.

---

## 4. Aggregate results

### 4.1 By treated count (positive-effect cells only)

| Treated count | Mean interval width | Mean width/effect ratio | Mean power | Mean coverage |
|---:|---:|---:|---:|---:|
| 1 | 1.899 | 16.29 | 0.000 | 1.000 |
| 2 | 1.861 | 15.93 | 0.000 | 1.000 |
| 4 | 1.793 | 15.31 | 0.000 | 1.000 |
| 8 | 1.683 | 14.41 | 0.000 | 1.000 |

**Interpretation:** There is no evidence that interval width inflation is driven primarily by treated-count growth. Under this matrix, width is slightly smaller at higher treated counts. The Run 001 zero-power result is therefore not a multi-treated-only collapse.

### 4.2 By donor tier / panel geometry (positive-effect cells only)

| Donor tier | Mean interval width | Mean width/effect ratio | Mean power |
|---|---:|---:|---:|
| small | 0.953 | 8.18 | 0.000 |
| medium | 1.781 | 15.26 | 0.000 |
| large | 2.693 | 23.03 | 0.000 |

**Interpretation:** The dominant empirical pattern is geometry sensitivity: larger donor-tier panels produced much wider intervals, with width/effect ratios rising from about `8×` (`small`) to `23×` (`large`). Because donor tier also changes `n_geos`, this is best described as a panel-geometry limitation.

### 4.3 By noise level (positive-effect cells only)

| Noise tier | Mean interval width | Mean width/effect ratio | Mean power |
|---|---:|---:|---:|
| low | 1.811 | 15.50 | 0.000 |
| medium | 1.809 | 15.48 | 0.000 |
| high | 1.807 | 15.47 | 0.000 |

**Interpretation:** Noise had almost no measurable effect on interval width or power in this matrix. That strongly suggests the dominant driver is the jackknife interval construction under the chosen panel geometry, not outcome noise alone.

### 4.4 By effect size (positive-effect cells only)

| Effect size | Mean interval width | Mean width/effect ratio | Mean power |
|---:|---:|---:|---:|
| 0.05 | 0.772 | 15.44 | 0.000 |
| 0.10 | 1.548 | 15.48 | 0.000 |
| 0.20 | 3.108 | 15.54 | 0.000 |

**Interpretation:** Width grows nearly proportionally with signal size, leaving the width/effect ratio essentially unchanged. Larger effects therefore did not rescue significance.

### 4.5 Null behavior

| Metric | Mean | Min | Max |
|---|---:|---:|---:|
| Coverage | 1.000 | 1.000 | 1.000 |
| FPR | 0.000 | 0.000 | 0.000 |

**Interpretation:** Over-coverage is not an isolated Run 001 artifact. It persisted in every null configuration in this characterization matrix.

---

## 5. Representative cells

| Geometry | Effect | Mean interval width | Width/effect ratio | Power | Mean predicted effect |
|---|---:|---:|---:|---:|---:|
| t=1, donor=small, noise=low | 0.05 | 0.416 | 8.32 | 0.000 | 0.052 |
| t=1, donor=small, noise=low | 0.10 | 0.816 | 8.16 | 0.000 | 0.102 |
| t=1, donor=small, noise=low | 0.20 | 1.617 | 8.09 | 0.000 | 0.202 |
| t=4, donor=medium, noise=medium | 0.05 | 0.750 | 15.00 | 0.000 | 0.049 |
| t=4, donor=medium, noise=medium | 0.10 | 1.512 | 15.12 | 0.000 | 0.099 |
| t=4, donor=medium, noise=medium | 0.20 | 3.038 | 15.19 | 0.000 | 0.199 |
| t=8, donor=large, noise=high | 0.05 | 1.088 | 21.77 | 0.000 | 0.049 |
| t=8, donor=large, noise=high | 0.10 | 2.177 | 21.77 | 0.000 | 0.099 |
| t=8, donor=large, noise=high | 0.20 | 4.365 | 21.83 | 0.000 | 0.199 |

The middle row (`n_treated=4`, donor tier `medium`, noise `medium`, effect `0.10`) is the closest analog to Run 001 geometry. It produced mean width ≈ `1.512`, width/effect ratio ≈ `15.12`, power = `0.0`, and mean predicted effect ≈ `0.099`, matching the original Run 001 diagnosis closely.

---

## 6. Required analysis

### 6.1 Does interval width scale with treated count?

**No.** Across positive-effect cells, mean width moved from `1.899` at 1 treated unit to `1.683` at 8 treated units. Within donor tiers, width was roughly flat or slightly lower at higher treated counts. This characterization does not support the claim that width inflation is caused primarily by treated-count growth.

### 6.2 Does power improve with larger effects?

**No.** Mean power was `0.0` at effects `0.05`, `0.10`, and `0.20`. Larger effects increased point estimates, but interval width increased almost proportionally, leaving significance unchanged.

### 6.3 Does power collapse only in multi-treated settings?

**No.** Power was `0.0` even in the easiest single-treated cells (`n_treated=1`, `small` donor tier, `low` noise, effect `0.20`). Multi-treated pooling is therefore not the sole explanation.

### 6.4 Is null over-coverage persistent?

**Yes.** Null coverage remained `1.0` and null FPR remained `0.0` in every null cell. This is persistent over-conservatism, not a one-off seed artifact.

### 6.5 Is behavior consistent across seeds?

**Yes.** In the representative seed-stability subset (`n_treated=4`, donor tier `medium`, noise `medium`, effect `0.10`):

| Base seed | Coverage | Power | Mean interval width | Width/effect ratio | Mean abs error |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.000 | 0.000 | 1.512 | 15.12 | 0.0025 |
| 100 | 1.000 | 0.000 | 1.535 | 15.35 | 0.0022 |
| 200 | 1.000 | 0.000 | 1.544 | 15.44 | 0.0023 |

The seed variation was negligible relative to the overall interval scale.

### 6.6 Is this expected conservatism, estimator limitation, geometry limitation, or inference defect?

**Best evidence-based classification:**

- **Not a point-estimator defect.** Point estimates consistently tracked truth and recovery success stayed at `1.0`.
- **Not an execution defect.** Failure rate was `0.0`, intervals were aligned, and behavior was stable across seeds.
- **Yes: strong conservatism in the UnitJackKnife inference path.** The interval construction is so wide that it eliminates significance even at large effects.
- **Yes: geometry limitation.** Panel geometry / donor-tier changes were the strongest empirical driver of width.
- **No direct evidence of a broken implementation analogous to the BRB bound inversion.** The pattern is internally consistent, not pathological or erratic.

So the safest conclusion is: **SCM_UnitJackKnife is behaving like an extremely conservative inference procedure under these panel geometries, not like a numerically broken method.** That is still a serious limitation for decision use.

---

## 7. Recommendation

| Option | Recommendation | Rationale |
|---|---|---|
| Keep current behavior | **Yes, for now** | No defect evidence justifies an implementation change in this characterization phase. |
| Document limitation | **Yes** | The method appears suitable for conservative null monitoring but not for lift detection under the tested geometries. |
| Open / keep investigation | **Yes** | Keep INV-004 open; this characterization narrows the diagnosis but does not close the issue. |
| Future inference redesign | **Yes, if promotion is desired** | Any promotion beyond conservative monitoring likely requires a less conservative SCM interval strategy or a geometry-specific policy. |

**Phase 11 conclusion:** The evidence supports expected conservatism plus geometry limitation, not a clear inference defect. However, the conservatism is strong enough that `SCM_UnitJackKnife` should not be treated as a generally useful positive-effect detector under the tested recovery geometries.

---

## 8. Appendix A — Full matrix results (`n_treated = 1`)

| Donor tier | Donors | Geos | Noise | Effect | Coverage | FPR | Power | Avg width | Width/effect | Sig rate | Recovery success | Failure rate | Mean point | MAE |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small | 5 | 6 | low | 0.00 | 1.000 | 0.000 | NA | 0.071 | NA | 0.000 | 1.000 | 0.000 | 0.002 | 0.0047 |
| small | 5 | 6 | low | 0.05 | 1.000 | NA | 0.000 | 0.416 | 8.32 | 0.000 | 1.000 | 0.000 | 0.052 | 0.0049 |
| small | 5 | 6 | low | 0.10 | 1.000 | NA | 0.000 | 0.816 | 8.16 | 0.000 | 1.000 | 0.000 | 0.102 | 0.0052 |
| small | 5 | 6 | low | 0.20 | 1.000 | NA | 0.000 | 1.617 | 8.09 | 0.000 | 1.000 | 0.000 | 0.202 | 0.0056 |
| small | 5 | 6 | medium | 0.00 | 1.000 | 0.000 | NA | 0.100 | NA | 0.000 | 1.000 | 0.000 | 0.001 | 0.0056 |
| small | 5 | 6 | medium | 0.05 | 1.000 | NA | 0.000 | 0.412 | 8.25 | 0.000 | 1.000 | 0.000 | 0.051 | 0.0059 |
| small | 5 | 6 | medium | 0.10 | 1.000 | NA | 0.000 | 0.812 | 8.12 | 0.000 | 1.000 | 0.000 | 0.101 | 0.0062 |
| small | 5 | 6 | medium | 0.20 | 1.000 | NA | 0.000 | 1.613 | 8.06 | 0.000 | 1.000 | 0.000 | 0.202 | 0.0067 |
| small | 5 | 6 | high | 0.00 | 1.000 | 0.000 | NA | 0.167 | NA | 0.000 | 1.000 | 0.000 | 0.001 | 0.0077 |
| small | 5 | 6 | high | 0.05 | 1.000 | NA | 0.000 | 0.413 | 8.25 | 0.000 | 1.000 | 0.000 | 0.051 | 0.0080 |
| small | 5 | 6 | high | 0.10 | 1.000 | NA | 0.000 | 0.808 | 8.08 | 0.000 | 1.000 | 0.000 | 0.101 | 0.0084 |
| small | 5 | 6 | high | 0.20 | 1.000 | NA | 0.000 | 1.607 | 8.04 | 0.000 | 1.000 | 0.000 | 0.201 | 0.0092 |
| medium | 19 | 20 | low | 0.00 | 1.000 | 0.000 | NA | 0.071 | NA | 0.000 | 1.000 | 0.000 | 0.000 | 0.0013 |
| medium | 19 | 20 | low | 0.05 | 1.000 | NA | 0.000 | 0.837 | 16.74 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0013 |
| medium | 19 | 20 | low | 0.10 | 1.000 | NA | 0.000 | 1.670 | 16.70 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0014 |
| medium | 19 | 20 | low | 0.20 | 1.000 | NA | 0.000 | 3.336 | 16.68 | 0.000 | 1.000 | 0.000 | 0.200 | 0.0015 |
| medium | 19 | 20 | medium | 0.00 | 1.000 | 0.000 | NA | 0.137 | NA | 0.000 | 1.000 | 0.000 | 0.000 | 0.0025 |
| medium | 19 | 20 | medium | 0.05 | 1.000 | NA | 0.000 | 0.839 | 16.78 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0026 |
| medium | 19 | 20 | medium | 0.10 | 1.000 | NA | 0.000 | 1.672 | 16.72 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0028 |
| medium | 19 | 20 | medium | 0.20 | 1.000 | NA | 0.000 | 3.337 | 16.69 | 0.000 | 1.000 | 0.000 | 0.200 | 0.0030 |
| medium | 19 | 20 | high | 0.00 | 1.000 | 0.000 | NA | 0.274 | NA | 0.000 | 1.000 | 0.000 | 0.000 | 0.0049 |
| medium | 19 | 20 | high | 0.05 | 1.000 | NA | 0.000 | 0.844 | 16.88 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0051 |
| medium | 19 | 20 | high | 0.10 | 1.000 | NA | 0.000 | 1.670 | 16.70 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0054 |
| medium | 19 | 20 | high | 0.20 | 1.000 | NA | 0.000 | 3.336 | 16.68 | 0.000 | 1.000 | 0.000 | 0.200 | 0.0059 |
| large | 39 | 40 | low | 0.00 | 1.000 | 0.000 | NA | 0.097 | NA | 0.000 | 1.000 | 0.000 | -0.000 | 0.0013 |
| large | 39 | 40 | low | 0.05 | 1.000 | NA | 0.000 | 1.201 | 24.01 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0014 |
| large | 39 | 40 | low | 0.10 | 1.000 | NA | 0.000 | 2.409 | 24.09 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0015 |
| large | 39 | 40 | low | 0.20 | 1.000 | NA | 0.000 | 4.825 | 24.13 | 0.000 | 1.000 | 0.000 | 0.200 | 0.0016 |
| large | 39 | 40 | medium | 0.00 | 1.000 | 0.000 | NA | 0.195 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0028 |
| large | 39 | 40 | medium | 0.05 | 1.000 | NA | 0.000 | 1.194 | 23.88 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0029 |
| large | 39 | 40 | medium | 0.10 | 1.000 | NA | 0.000 | 2.402 | 24.02 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0031 |
| large | 39 | 40 | medium | 0.20 | 1.000 | NA | 0.000 | 4.818 | 24.09 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0034 |
| large | 39 | 40 | high | 0.00 | 1.000 | 0.000 | NA | 0.391 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0059 |
| large | 39 | 40 | high | 0.05 | 1.000 | NA | 0.000 | 1.185 | 23.70 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0062 |
| large | 39 | 40 | high | 0.10 | 1.000 | NA | 0.000 | 2.390 | 23.90 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0065 |
| large | 39 | 40 | high | 0.20 | 1.000 | NA | 0.000 | 4.805 | 24.02 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0071 |

## 9. Appendix B — Full matrix results (`n_treated = 2`)

| Donor tier | Donors | Geos | Noise | Effect | Coverage | FPR | Power | Avg width | Width/effect | Sig rate | Recovery success | Failure rate | Mean point | MAE |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small | 5 | 7 | low | 0.00 | 1.000 | 0.000 | NA | 0.076 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0042 |
| small | 5 | 7 | low | 0.05 | 1.000 | NA | 0.000 | 0.407 | 8.13 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0044 |
| small | 5 | 7 | low | 0.10 | 1.000 | NA | 0.000 | 0.806 | 8.06 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0046 |
| small | 5 | 7 | low | 0.20 | 1.000 | NA | 0.000 | 1.617 | 8.08 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0051 |
| small | 5 | 7 | medium | 0.00 | 1.000 | 0.000 | NA | 0.106 | NA | 0.000 | 1.000 | 0.000 | -0.002 | 0.0051 |
| small | 5 | 7 | medium | 0.05 | 1.000 | NA | 0.000 | 0.402 | 8.04 | 0.000 | 1.000 | 0.000 | 0.048 | 0.0053 |
| small | 5 | 7 | medium | 0.10 | 1.000 | NA | 0.000 | 0.801 | 8.01 | 0.000 | 1.000 | 0.000 | 0.098 | 0.0056 |
| small | 5 | 7 | medium | 0.20 | 1.000 | NA | 0.000 | 1.610 | 8.05 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0061 |
| small | 5 | 7 | high | 0.00 | 1.000 | 0.000 | NA | 0.173 | NA | 0.000 | 1.000 | 0.000 | -0.003 | 0.0072 |
| small | 5 | 7 | high | 0.05 | 1.000 | NA | 0.000 | 0.401 | 8.02 | 0.000 | 1.000 | 0.000 | 0.047 | 0.0076 |
| small | 5 | 7 | high | 0.10 | 1.000 | NA | 0.000 | 0.793 | 7.93 | 0.000 | 1.000 | 0.000 | 0.097 | 0.0080 |
| small | 5 | 7 | high | 0.20 | 1.000 | NA | 0.000 | 1.601 | 8.01 | 0.000 | 1.000 | 0.000 | 0.197 | 0.0087 |
| medium | 18 | 20 | low | 0.00 | 1.000 | 0.000 | NA | 0.078 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0013 |
| medium | 18 | 20 | low | 0.05 | 1.000 | NA | 0.000 | 0.801 | 16.02 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0014 |
| medium | 18 | 20 | low | 0.10 | 1.000 | NA | 0.000 | 1.611 | 16.11 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0014 |
| medium | 18 | 20 | low | 0.20 | 1.000 | NA | 0.000 | 3.230 | 16.15 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0016 |
| medium | 18 | 20 | medium | 0.00 | 1.000 | 0.000 | NA | 0.140 | NA | 0.000 | 1.000 | 0.000 | -0.000 | 0.0019 |
| medium | 18 | 20 | medium | 0.05 | 1.000 | NA | 0.000 | 0.804 | 16.08 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0020 |
| medium | 18 | 20 | medium | 0.10 | 1.000 | NA | 0.000 | 1.613 | 16.13 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0021 |
| medium | 18 | 20 | medium | 0.20 | 1.000 | NA | 0.000 | 3.233 | 16.17 | 0.000 | 1.000 | 0.000 | 0.200 | 0.0023 |
| medium | 18 | 20 | high | 0.00 | 1.000 | 0.000 | NA | 0.272 | NA | 0.000 | 1.000 | 0.000 | -0.000 | 0.0033 |
| medium | 18 | 20 | high | 0.05 | 1.000 | NA | 0.000 | 0.811 | 16.22 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0035 |
| medium | 18 | 20 | high | 0.10 | 1.000 | NA | 0.000 | 1.613 | 16.13 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0037 |
| medium | 18 | 20 | high | 0.20 | 1.000 | NA | 0.000 | 3.233 | 16.16 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0040 |
| large | 38 | 40 | low | 0.00 | 1.000 | 0.000 | NA | 0.109 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0015 |
| large | 38 | 40 | low | 0.05 | 1.000 | NA | 0.000 | 1.176 | 23.53 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0016 |
| large | 38 | 40 | low | 0.10 | 1.000 | NA | 0.000 | 2.369 | 23.69 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0017 |
| large | 38 | 40 | low | 0.20 | 1.000 | NA | 0.000 | 4.753 | 23.77 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0019 |
| large | 38 | 40 | medium | 0.00 | 1.000 | 0.000 | NA | 0.204 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0026 |
| large | 38 | 40 | medium | 0.05 | 1.000 | NA | 0.000 | 1.174 | 23.49 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0027 |
| large | 38 | 40 | medium | 0.10 | 1.000 | NA | 0.000 | 2.366 | 23.66 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0028 |
| large | 38 | 40 | medium | 0.20 | 1.000 | NA | 0.000 | 4.750 | 23.75 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0031 |
| large | 38 | 40 | high | 0.00 | 1.000 | 0.000 | NA | 0.397 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0048 |
| large | 38 | 40 | high | 0.05 | 1.000 | NA | 0.000 | 1.175 | 23.49 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0050 |
| large | 38 | 40 | high | 0.10 | 1.000 | NA | 0.000 | 2.359 | 23.59 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0053 |
| large | 38 | 40 | high | 0.20 | 1.000 | NA | 0.000 | 4.743 | 23.71 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0057 |

## 10. Appendix C — Full matrix results (`n_treated = 4`)

| Donor tier | Donors | Geos | Noise | Effect | Coverage | FPR | Power | Avg width | Width/effect | Sig rate | Recovery success | Failure rate | Mean point | MAE |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small | 5 | 9 | low | 0.00 | 1.000 | 0.000 | NA | 0.097 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0065 |
| small | 5 | 9 | low | 0.05 | 1.000 | NA | 0.000 | 0.402 | 8.04 | 0.000 | 1.000 | 0.000 | 0.048 | 0.0069 |
| small | 5 | 9 | low | 0.10 | 1.000 | NA | 0.000 | 0.810 | 8.10 | 0.000 | 1.000 | 0.000 | 0.098 | 0.0072 |
| small | 5 | 9 | low | 0.20 | 1.000 | NA | 0.000 | 1.635 | 8.17 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0078 |
| small | 5 | 9 | medium | 0.00 | 1.000 | 0.000 | NA | 0.126 | NA | 0.000 | 1.000 | 0.000 | -0.002 | 0.0071 |
| small | 5 | 9 | medium | 0.05 | 1.000 | NA | 0.000 | 0.403 | 8.05 | 0.000 | 1.000 | 0.000 | 0.048 | 0.0074 |
| small | 5 | 9 | medium | 0.10 | 1.000 | NA | 0.000 | 0.809 | 8.09 | 0.000 | 1.000 | 0.000 | 0.098 | 0.0078 |
| small | 5 | 9 | medium | 0.20 | 1.000 | NA | 0.000 | 1.633 | 8.17 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0085 |
| small | 5 | 9 | high | 0.00 | 1.000 | 0.000 | NA | 0.193 | NA | 0.000 | 1.000 | 0.000 | -0.002 | 0.0084 |
| small | 5 | 9 | high | 0.05 | 1.000 | NA | 0.000 | 0.410 | 8.20 | 0.000 | 1.000 | 0.000 | 0.048 | 0.0089 |
| small | 5 | 9 | high | 0.10 | 1.000 | NA | 0.000 | 0.807 | 8.07 | 0.000 | 1.000 | 0.000 | 0.098 | 0.0093 |
| small | 5 | 9 | high | 0.20 | 1.000 | NA | 0.000 | 1.630 | 8.15 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0101 |
| medium | 16 | 20 | low | 0.00 | 1.000 | 0.000 | NA | 0.085 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0018 |
| medium | 16 | 20 | low | 0.05 | 1.000 | NA | 0.000 | 0.747 | 14.94 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0019 |
| medium | 16 | 20 | low | 0.10 | 1.000 | NA | 0.000 | 1.510 | 15.10 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0020 |
| medium | 16 | 20 | low | 0.20 | 1.000 | NA | 0.000 | 3.036 | 15.18 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0022 |
| medium | 16 | 20 | medium | 0.00 | 1.000 | 0.000 | NA | 0.144 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0023 |
| medium | 16 | 20 | medium | 0.05 | 1.000 | NA | 0.000 | 0.750 | 15.00 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0024 |
| medium | 16 | 20 | medium | 0.10 | 1.000 | NA | 0.000 | 1.512 | 15.12 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0025 |
| medium | 16 | 20 | medium | 0.20 | 1.000 | NA | 0.000 | 3.038 | 15.19 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0027 |
| medium | 16 | 20 | high | 0.00 | 1.000 | 0.000 | NA | 0.267 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0032 |
| medium | 16 | 20 | high | 0.05 | 1.000 | NA | 0.000 | 0.758 | 15.16 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0034 |
| medium | 16 | 20 | high | 0.10 | 1.000 | NA | 0.000 | 1.511 | 15.11 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0035 |
| medium | 16 | 20 | high | 0.20 | 1.000 | NA | 0.000 | 3.038 | 15.19 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0038 |
| large | 36 | 40 | low | 0.00 | 1.000 | 0.000 | NA | 0.108 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0015 |
| large | 36 | 40 | low | 0.05 | 1.000 | NA | 0.000 | 1.131 | 22.62 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0016 |
| large | 36 | 40 | low | 0.10 | 1.000 | NA | 0.000 | 2.291 | 22.91 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0017 |
| large | 36 | 40 | low | 0.20 | 1.000 | NA | 0.000 | 4.610 | 23.05 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0019 |
| large | 36 | 40 | medium | 0.00 | 1.000 | 0.000 | NA | 0.198 | NA | 0.000 | 1.000 | 0.000 | -0.002 | 0.0023 |
| large | 36 | 40 | medium | 0.05 | 1.000 | NA | 0.000 | 1.121 | 22.43 | 0.000 | 1.000 | 0.000 | 0.048 | 0.0024 |
| large | 36 | 40 | medium | 0.10 | 1.000 | NA | 0.000 | 2.280 | 22.80 | 0.000 | 1.000 | 0.000 | 0.098 | 0.0025 |
| large | 36 | 40 | medium | 0.20 | 1.000 | NA | 0.000 | 4.599 | 22.99 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0028 |
| large | 36 | 40 | high | 0.00 | 1.000 | 0.000 | NA | 0.380 | NA | 0.000 | 1.000 | 0.000 | -0.003 | 0.0039 |
| large | 36 | 40 | high | 0.05 | 1.000 | NA | 0.000 | 1.108 | 22.16 | 0.000 | 1.000 | 0.000 | 0.047 | 0.0041 |
| large | 36 | 40 | high | 0.10 | 1.000 | NA | 0.000 | 2.258 | 22.58 | 0.000 | 1.000 | 0.000 | 0.097 | 0.0043 |
| large | 36 | 40 | high | 0.20 | 1.000 | NA | 0.000 | 4.574 | 22.87 | 0.000 | 1.000 | 0.000 | 0.197 | 0.0047 |

## 11. Appendix D — Full matrix results (`n_treated = 8`)

| Donor tier | Donors | Geos | Noise | Effect | Coverage | FPR | Power | Avg width | Width/effect | Sig rate | Recovery success | Failure rate | Mean point | MAE |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small | 5 | 13 | low | 0.00 | 1.000 | 0.000 | NA | 0.085 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0038 |
| small | 5 | 13 | low | 0.05 | 1.000 | NA | 0.000 | 0.416 | 8.33 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0040 |
| small | 5 | 13 | low | 0.10 | 1.000 | NA | 0.000 | 0.835 | 8.35 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0042 |
| small | 5 | 13 | low | 0.20 | 1.000 | NA | 0.000 | 1.676 | 8.38 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0046 |
| small | 5 | 13 | medium | 0.00 | 1.000 | 0.000 | NA | 0.113 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0041 |
| small | 5 | 13 | medium | 0.05 | 1.000 | NA | 0.000 | 0.420 | 8.39 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0043 |
| small | 5 | 13 | medium | 0.10 | 1.000 | NA | 0.000 | 0.836 | 8.36 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0045 |
| small | 5 | 13 | medium | 0.20 | 1.000 | NA | 0.000 | 1.677 | 8.38 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0049 |
| small | 5 | 13 | high | 0.00 | 1.000 | 0.000 | NA | 0.179 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0055 |
| small | 5 | 13 | high | 0.05 | 1.000 | NA | 0.000 | 0.432 | 8.63 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0058 |
| small | 5 | 13 | high | 0.10 | 1.000 | NA | 0.000 | 0.839 | 8.39 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0060 |
| small | 5 | 13 | high | 0.20 | 1.000 | NA | 0.000 | 1.679 | 8.40 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0066 |
| medium | 12 | 20 | low | 0.00 | 1.000 | 0.000 | NA | 0.081 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0021 |
| medium | 12 | 20 | low | 0.05 | 1.000 | NA | 0.000 | 0.644 | 12.89 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0022 |
| medium | 12 | 20 | low | 0.10 | 1.000 | NA | 0.000 | 1.305 | 13.05 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0024 |
| medium | 12 | 20 | low | 0.20 | 1.000 | NA | 0.000 | 2.627 | 13.13 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0026 |
| medium | 12 | 20 | medium | 0.00 | 1.000 | 0.000 | NA | 0.132 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0027 |
| medium | 12 | 20 | medium | 0.05 | 1.000 | NA | 0.000 | 0.646 | 12.91 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0028 |
| medium | 12 | 20 | medium | 0.10 | 1.000 | NA | 0.000 | 1.305 | 13.05 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0029 |
| medium | 12 | 20 | medium | 0.20 | 1.000 | NA | 0.000 | 2.627 | 13.13 | 0.000 | 1.000 | 0.000 | 0.198 | 0.0032 |
| medium | 12 | 20 | high | 0.00 | 1.000 | 0.000 | NA | 0.239 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0038 |
| medium | 12 | 20 | high | 0.05 | 1.000 | NA | 0.000 | 0.655 | 13.10 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0040 |
| medium | 12 | 20 | high | 0.10 | 1.000 | NA | 0.000 | 1.307 | 13.07 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0042 |
| medium | 12 | 20 | high | 0.20 | 1.000 | NA | 0.000 | 2.628 | 13.14 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0046 |
| large | 32 | 40 | low | 0.00 | 1.000 | 0.000 | NA | 0.096 | NA | 0.000 | 1.000 | 0.000 | -0.000 | 0.0009 |
| large | 32 | 40 | low | 0.05 | 1.000 | NA | 0.000 | 1.085 | 21.70 | 0.000 | 1.000 | 0.000 | 0.050 | 0.0009 |
| large | 32 | 40 | low | 0.10 | 1.000 | NA | 0.000 | 2.179 | 21.79 | 0.000 | 1.000 | 0.000 | 0.100 | 0.0010 |
| large | 32 | 40 | low | 0.20 | 1.000 | NA | 0.000 | 4.368 | 21.84 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0011 |
| large | 32 | 40 | medium | 0.00 | 1.000 | 0.000 | NA | 0.182 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0013 |
| large | 32 | 40 | medium | 0.05 | 1.000 | NA | 0.000 | 1.084 | 21.68 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0014 |
| large | 32 | 40 | medium | 0.10 | 1.000 | NA | 0.000 | 2.178 | 21.78 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0014 |
| large | 32 | 40 | medium | 0.20 | 1.000 | NA | 0.000 | 4.366 | 21.83 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0015 |
| large | 32 | 40 | high | 0.00 | 1.000 | 0.000 | NA | 0.355 | NA | 0.000 | 1.000 | 0.000 | -0.001 | 0.0021 |
| large | 32 | 40 | high | 0.05 | 1.000 | NA | 0.000 | 1.088 | 21.77 | 0.000 | 1.000 | 0.000 | 0.049 | 0.0022 |
| large | 32 | 40 | high | 0.10 | 1.000 | NA | 0.000 | 2.177 | 21.77 | 0.000 | 1.000 | 0.000 | 0.099 | 0.0023 |
| large | 32 | 40 | high | 0.20 | 1.000 | NA | 0.000 | 4.365 | 21.83 | 0.000 | 1.000 | 0.000 | 0.199 | 0.0025 |
