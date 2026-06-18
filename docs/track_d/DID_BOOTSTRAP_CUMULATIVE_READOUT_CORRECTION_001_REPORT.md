# DID Bootstrap Cumulative Readout Correction — Report

**Artifact ID:** DID-BOOTSTRAP-CUMULATIVE-READOUT-CORRECTION-001  
**Verdict:** `did_bootstrap_cumulative_readout_corrected_requires_reassessment`  
**Summary:** [`archives/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json`](archives/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json)  
**Production change:** `panel_exp/methods/DID.py`

> This artifact corrects production DID bootstrap interval construction. It does **not** authorize TrustReport or complete DCM-004 reassessment.

## 1. Executive summary

Production `DID.py` embedded moving-block bootstrap intervals were miscentered: percentile CIs used raw bootstrap cumulative ATT replicates whose distribution centered near zero while the reported plug-in `cumulative_att` was large and positive. The fix applies a **centered-deviation percentile interval** anchored to the plug-in cumulative path ATT. Positive coverage improves from ~4% to ~93%; clean parallel worlds calibrate reasonably; stress null worlds show elevated type-I. **DCM-004 reassessment is the recommended next step.**

## 2. Prior evidence

- `D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001`: production miscentering confirmed (`did_bootstrap_production_miscentering_confirmed`).
- `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION`: canonical harness geometry and truth scale corrected; pre-fix archive retained.

## 3. Original production defect

Raw percentile interval `[Q_{α/2}(θ*), Q_{1-α/2}(θ*)]` used bootstrap replicates θ* whose mean was near zero while plug-in θ̂ (`cumulative_att`) was O(10²–10³). Intervals were therefore not centered on the reported point estimand and excluded injected cumulative truth.

## 4. DID point estimand

**θ̂** = cumulative path ATT on the original panel:

\[
\hat\theta = \sum_{t \in \text{post}} \bigl(\bar Y^{\text{treated}}_t - \widehat{Y(0)}^{\text{agg}}_t\bigr)
\]

computed in `run_analysis` / `_path_effect_from_df(self.data)`.

## 5. Bootstrap replicate estimand

Each bootstrap replicate **θ*_b** uses the same functional:

\[
\theta^*_b = \sum_{t \in \text{post}} \text{effect}_t\bigl(\text{block-resampled panel}_b\bigr)
\]

via `_path_effect_from_df` on a moving-block resampled panel (`_build_bootstrap_df`).

## 6. Mathematical diagnosis

1. **Plug-in cumulative ATT** sums post-period treated-minus-synthetic-control effects on the original timeline.
2. **Bootstrap replicates** apply the same estimator on panels where time periods are block-resampled and relabeled onto the fixed calendar post window.
3. Block resampling destroys alignment between injected treatment effects and the fixed post mask, so **E[θ* | data] ≈ 0** even when **θ̂** is large.
4. Raw percentile CI therefore estimates uncertainty around the bootstrap-null center, not around θ̂.
5. Diagnostic oracle shift `θ̂ - mean(θ*)` in remediation artifacts restored coverage, confirming a **centering/readout defect**, not a truth-scale mismatch.

## 7. Candidate constructions evaluated

| ID | Construction | Result |
|----|--------------|--------|
| A | Raw percentile of θ* | Fails positive coverage (~0%) |
| B | Plug-in pivot `θ̂ + Q(θ* − θ̂)` | Algebraically equals A when θ̂ is fixed |
| C | Basic bootstrap `2θ̂ − Q(θ*)` | Fails coverage on test panels |
| **D** | **Centered deviation `θ̂ + Q(θ* − mean(θ*))`** | **Selected** — restores point-in-interval and positive coverage |

## 8. Chosen interval construction

**Method:** `centered_deviation_percentile`

\[
\text{CI} = \hat\theta + \left[ Q_{\alpha/2}(\theta^*_b - \bar\theta^*),\; Q_{1-\alpha/2}(\theta^*_b - \bar\theta^*) \right]
\]

where \(\bar\theta^* = \text{mean}(\theta^*_b)\).

**Interpretation:** bootstrap replicates encode dependence-aware *relative* uncertainty around their own center; the interval re-anchors that shape on the plug-in cumulative ATT without truth-dependent adjustment.

## 9. Resampling behavior (unchanged)

| Property | Value |
|----------|-------|
| Resampling unit | Time period (moving block) |
| Block length | `bootstrap_block_size` (default 8) |
| Treated/control structure | Preserved within each period slice |
| Time dependence | Preserved via block resampling |
| Replicate count | `n_bootstrap` (default 50) |
| Seed | `bootstrap_seed` |

## 10. Production metadata fields

Added to `results` / export: `bootstrap_interval_method`, `bootstrap_center`, `bootstrap_replicate_estimand`, `bootstrap_standard_error`, `bootstrap_replicate_count`, `point_estimate`, `interval_lower`, `interval_upper`. Existing keys (`cumulative_att`, `treatment_ci`, etc.) retained.

## 11. Backward compatibility

`treatment_ci`, `cumulative_att`, `results` schema preserved; new fields are additive. No staggered-timing support added.

## 12. Before/after centering

| Metric | Before | After |
|--------|--------|-------|
| Mean point − bootstrap center | −40.5 | large gap remains (replicate center unchanged) |
| Point-in-interval rate | ~41% | ~100% |
| Max \|point − bootstrap center\| | ~2391 | unchanged (expected) |

Interval centering fixed; bootstrap replicate mean remains a block-bootstrap artifact.

## 13. Null coverage

Aggregate null coverage: **100% → 68%** (stress worlds degrade). Clean parallel null: **100% → 87%**.

## 14. Positive coverage

Aggregate: **4.4% → 93%**. Clean parallel positive lift: **0% → 100%**.

## 15. Negative coverage

Not separately characterized in canonical 7-world battery; focused production tests cover negative injection with interval covering truth.

## 16. Type-I error

Aggregate empirical null rejection: **0% → 32%** (stress-driven). Clean parallel null: **0% → 13%**.

## 17. Bias / RMSE

Point bias unchanged (estimand unchanged); RMSE driven by same path point estimator.

## 18. Interval width

Mean width increases modestly because intervals are anchored on θ̂ rather than near-zero bootstrap mass.

## 19. Variance comparison

Bootstrap replicate variance unchanged; interval width reflects centered deviation spread around θ̂.

## 20. Serial-dependence findings

Noisy/serial worlds remain feasible; positive coverage improves under `scm_low_signal` stress.

## 21. Failure summary

0 callable failures in post-fix canonical replay (105 runs).

## 22. TrustReport implications

TrustReport remains **blocked**. DCM-004 requires separate eligibility reassessment.

## 23. Archive policy

Pre-production-fix canonical archive `D5_STAT_DID_BOOTSTRAP_001_results.json` **not overwritten**. Comparison captured in `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json`.

## 24. Tests

`tests/methods/test_did_bootstrap_cumulative_readout_correction_001.py` — production paths, worlds, seeds, coverage, backward compatibility.

## 25. Governance verdict

**`did_bootstrap_cumulative_readout_corrected_requires_reassessment`**

## 26. Recommended next artifact

**DCM-004 eligibility reassessment** (not in scope here).
