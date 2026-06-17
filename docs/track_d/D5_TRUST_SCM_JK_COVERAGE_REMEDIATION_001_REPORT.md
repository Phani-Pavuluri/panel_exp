# D5 Trust SCM+JK Coverage Remediation 001 — Report

**Artifact ID:** D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001  
**Verdict:** `scm_jk_eligible_as_null_monitor_only`  
**Summary:** [`archives/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_summary.json`](archives/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_summary.json)  
**Harness:** `panel_exp/validation/track_d_d5_trust_scm_jk_coverage_remediation_001.py`  
**Threshold label:** `provisional_for_remediation_characterization_only`

## 1. Executive summary

Diagnoses the apparent SCM+UnitJackknife coverage split (null ≈93%, positive-effect ≈7% in TRUSTREPORT-ELIGIBILITY-VALIDATION-001) by decomposing estimator bias, interval centering, variance calibration, donor support, and **semantic scale mismatch**. With correct assignment geometry and level-scaled truth comparison, **level-scale positive-effect coverage is high** (100% at 8% injection in the effect sweep; aggregate ~94% across positive runs). **Percent-scale comparison reproduces the prior ~7–9% undercoverage**, confirming the eligibility finding was dominated by **metric misuse**, not catastrophic JK failure. **Causal-interval TrustReport remains unsupported.** Null-monitor and diagnostic readout classes are the evidence-backed ceiling. **No TrustReport authorization.**

## 2. Prior eligibility finding

TRUSTREPORT-ELIGIBILITY-VALIDATION-001 classified DCM-001 (SCM+UnitJackKnife) as `ELIGIBLE_WITH_RESTRICTIONS` with:

- Null-world coverage ~93% (acceptable under provisional thresholds)
- Positive-scenario coverage ~6.7% (far below provisional 50% minimum for causal-interval candidacy)
- Bias ratio on positive scenarios ~107× effect scale (percent truth vs level point estimate)

Source archive: `D5_STAT_SCM_JK_001_results.json` via `D5-STAT-SCM-JK-001` harness, which compares **level-unit** SCM effect intervals to **fractional percent** `true_effect` (0.08).

## 3. Scope

In scope: SCM point diagnostics, UnitJackknife interval diagnostics, 18 synthetic worlds, effect-size and donor-regime sweeps, interval centering and variance decomposition, policy comparisons A–G (evaluation only), compact summary and this report.

Out of scope: TrustReport authorization, production SCM/JK algorithm changes, DID/TBRRidge remediation, pooled multi-cell, downstream gateway changes.

## 4. SCM estimator path

`SyntheticControlCVXPY` with `inference="UnitJackKnife"` on unit-panel geometry. Greedy `test_0` assignment (not control pool), percent effect injected as **level delta** = `percent × mean(treated pre-period level)`. Post-window effect = `y − y_hat`; point estimate = mean post effect.

## 5. UnitJackknife implementation

`panel_exp/inference/unit_jackknife.py` (`unit_jk`) and `run_unit_jackknife` in inference modes. Intervals transformed to effect scale via `effect_lo = y − y_hi`, `effect_hi = y − y_lo` (production-consistent orientation per D5-POW-001b).

## 6. Statistical question

Can UnitJackknife support (a) causal confidence intervals, (b) null-monitor intervals only, (c) diagnostic use only, or (d) no defensible TrustReport class—given observed null vs positive coverage split?

## 7. Worlds

18 diagnostic worlds: clean balanced, weak donor pool, poor pre-fit, latent-factor mismatch, high heterogeneity, serial correlation, heteroskedasticity, outlier donor, donor contamination, trend mismatch, level shift, delayed effect, carryover, effect heterogeneity, small donor pool, unstable pre-period, geographic correlation, placebo null. Deterministic paired seeds with up to 6 assignment retries per replicate.

## 8. Effect-size sweep

Effects: 0.00, 0.03, 0.08, 0.12, −0.05 (fractional percent of treated mean). Six replicates each on `effect_sweep` world.

| Effect | Coverage (level) | Coverage (percent scale) |
|--------|------------------|--------------------------|
| 0.00 | 1.00 | 1.00 |
| 0.03 | 1.00 | 0.50 |
| 0.08 | 1.00 | 0.00 |
| 0.12 | 0.83 | 0.00 |
| −0.05 | 1.00 | 0.17 |

## 9. Donor-strength sweep

Five regimes: strong (16 geos), moderate (14), weak (12), contaminated scenario, small pool (10). Level-scale coverage at 8% effect: 1.00 for all regimes in this battery. JK-to-empirical variance ratio ranges ~6.9–12.0 across regimes.

## 10. Metrics

Per run: point estimate, level and percent truth, estimation errors, interval bounds/center/width, contains-truth (level and percent), contains-zero, JK half-width, LOO empirical half-width, pre-fit RMSE, donor weights, failure status. Aggregate: separate null/positive/negative coverage, bias decomposition, variance decomposition, policy comparisons.

## 11. Run counts/runtime

168 total runs, 0 failures, ~33s full harness (`n_replicates=6`). Full run records: `/tmp/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_results.json` (local only).

## 12. Point-estimate bias

Mean bias on positive effects (level): −0.26; RMSE at 8% effect: 1.26. Mean bias on **percent scale** for 8% injection: +8.07 (dominated by unit mismatch—point is in level units, truth labeled as 0.08 fraction). SCM recovers injected level effects adequately for null-monitor purposes; percent-labeled comparison inflates apparent bias ~100×.

## 13. Interval centering

Intervals are centered on the SCM point estimate on the **level effect scale**. `interval_center_error` ≈ 0 (oracle-centered diagnostic coverage matches current JK coverage). Recentering diagnostically does not materially change coverage—**miscentering is not the driver** of prior undercoverage.

## 14. Variance calibration

Mean JK half-width: 4.27; mean LOO empirical half-width: 0.44; mean JK/empirical ratio: **~10.9**. Jackknife is **conservative (wider)** relative to LOO donor-delete spread in this battery—not variance underestimation. Wide intervals contribute to level-scale coverage despite ratio asymmetry.

## 15. Null-world coverage

Effect-sweep null (0.0): level 1.00, percent 1.00. Across all null-labeled world runs (trend mismatch, level shift, placebo): aggregate null contains-zero rate **~95.8%** (`policy_comparisons.A_current_unit_jackknife.null_coverage_level`).

## 16. Positive-effect coverage

Effect 0.08: **level 1.00**, **percent 0.00** (reproduces eligibility ~7% when pooled with other positive runs: aggregate percent-scale **~8.7%**, level-scale **~94.2%**).

## 17. Negative-effect coverage

Effect −0.05: level 1.00, percent 0.17.

## 18. Pre-fit relationship

Poor pre-fit world (`scm_trend_mismatch`): level coverage 0.67 (worst among positive-effect worlds). Outlier-donor world: level coverage 0.83 with very high pre-fit RMSE (~39). Coverage generally remains high at moderate pre-fit RMSE (~2–3); degrades under trend mismatch and extreme outlier donors.

## 19. Donor-support relationship

Weak and small-pool regimes still achieve level coverage 1.00 at 8% in this sweep. Donor count ~9–11 controls after `test_0` assignment. Weight concentration not a primary failure mode in feasible runs.

## 20. Worst-world behavior

Worst positive-effect level coverage: `poor_prefit` 0.67, `clean_balanced` 0.83, `geographic_correlation` 0.83. Percent-scale coverage 0.00 for most positive worlds except partial recovery in heteroskedasticity/outlier cases where level and percent scales accidentally align.

## 21. Failure analysis

Initial harness runs failed 100% due to **remediation harness defects** (assignment pooled control+treated units; multi-treated inject type error)—fixed within this artifact only. Production SCM/JK unchanged. Zero failures in final 168-run battery.

## 22. Policy comparisons

| Policy | Finding |
|--------|---------|
| A — current UnitJackknife | Null level ~96%; positive level ~94%; positive percent ~9% |
| B — null-monitor only | Supported when percent-scale causal claims excluded |
| Oracle-centered diagnostic | Matches A (centering not the bug) |
| Empirical LOO diagnostic | Much narrower than JK (characterization only) |
| G — causal interval not supported | Percent-scale eligibility metrics invalid for level readout |

## 23. Causal-interval interpretation

**Not supported** for TrustReport. Level-scale intervals can cover injected level truth, but estimand labeling in D5-STAT-SCM-JK-001 and eligibility evaluator compares to fractional percent—invalid causal-interval claim. Large percent-scale bias ratios are **semantic artifacts**.

## 24. Null-monitor interpretation

**Supported with restrictions.** Null-world zero-coverage ~96%. Interval-excludes-zero is a defensible null-monitor primitive when readout semantics explicitly disallow causal level-to-percent promotion without estimand bridge.

## 25. TrustReport eligibility implications

DCM-001 should remain `ELIGIBLE_WITH_RESTRICTIONS` with **null-monitor / diagnostic_only** classes only. Prior positive coverage deficiency is **explained**; does not authorize promotion. Requires `TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` before any class upgrade. `eligible_for_promotion: false`.

## 26. Algorithm changes

**None to production SCM or UnitJackknife.** Harness-only fixes: `test_0`-only assignment, per-unit baseline vector for multi-treated inject, seed retry loop, separate level vs percent coverage keys.

## 27. Remaining limitations

Six replicates per cell (modest MC). Synthetic worlds only. LOO empirical intervals diagnostic only. Does not repair `D5-STAT-SCM-JK-001` committed archive drift. JK conservatism vs LOO not fully characterized theoretically. Multi-treated aggregation semantics still merit INV-003 follow-up.

## 28. Required reassessment

1. Update eligibility evaluator to use **level-consistent** coverage for SCM+JK positive scenarios (or explicit estimand bridge).  
2. Re-run TRUSTREPORT-ELIGIBILITY-VALIDATION-001 or targeted reassessment artifact.  
3. Fix D5-STAT-SCM-JK-001 harness assignment + truth scale in a separate artifact (do not silently regenerate archive).

## 29. Authorization status

`authorization_summary.trust_report_authorized = false`  
`trust_report_authorized_count = 0`  
No downstream role authorized.

## 30. Governance verdict

**`scm_jk_eligible_as_null_monitor_only`** — evidence shows prior positive undercoverage was primarily **semantic percent-vs-level mismatch** in validation metrics, not interval centering or variance collapse under effect. Causal-interval TrustReport promotion remains blocked. Null-monitor and diagnostic readouts are the narrowly supported eligibility classes pending formal reassessment.
