# D5 Trust DID Bootstrap Remediation 001 — Report

**Artifact ID:** D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001  
**Verdict:** `did_bootstrap_remediation_failed`  
**Summary:** [`archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json`](archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json)  
**Threshold label:** `provisional_for_remediation_characterization_only`

## 1. Executive summary

Diagnoses DCM-004 DID+bootstrap ~0% positive-effect interval coverage. Under **corrected assignment geometry** (`test_0` treated only), point estimates recover injected cumulative level effects with good sign accuracy, but **embedded bootstrap CIs are miscentered** relative to the reported `cumulative_att` point. Null-world coverage is high because wide CIs centered near zero contain null truth; positive-world coverage remains ~0%. **Not a truth-scale mismatch** (unlike SCM-JK). D5-STAT harness also has an assignment defect (`groups.values()` → all units treated, zero controls). **No TrustReport authorization.**

## 2. Prior eligibility finding

DCM-004 classified `INSUFFICIENT_EVIDENCE` with positive coverage ~0% in `D5_STAT_DID_BOOTSTRAP_001_results.json`.

## 3. Scope

DID point/interval diagnostics, 18 worlds, effect-size sweep, timing regimes, bootstrap policy comparisons, harness defect probe.

## 4. DID estimator path

`panel_exp/methods/DID.py` pooled TWFE with path-based `cumulative_att` reporting.

## 5. Bootstrap implementation

Embedded moving-block **time-period** resampling (`_block_bootstrap_inference`); whole cross-sections preserved per sampled period.

## 6. DID estimand

Cumulative treated-minus-synthetic-control ATT over post periods (level units).

## 7. Identification assumptions

Parallel trends required for causal interpretation; pretrend contract recorded per run.

## 8. Worlds

8 diagnostic worlds with deterministic paired seeds.

## 9. Effect-size sweep

Effects: 0.0, 0.08.

## 10. Timing regimes

Common simultaneous adoption supported; staggered cohort geometry blocked for pooled DID.

## 11. Bootstrap policies

Policies A–H evaluated; cluster bootstrap not implemented.

## 12. Metrics

Separate null/positive/negative coverage, bias, RMSE, interval center error, bootstrap center vs point, oracle recentering (diagnostic).

## 13. Run counts/runtime

Total runs: 22; failures: 22.

## 14. Point-estimate bias

Sign accuracy (positive): None; mean bias: None.

## 15. Interval centering

Mean interval center error: None; miscentering dominant: False.

## 16. Variance calibration

Point-in-bootstrap-CI rate: None.

## 17. Null coverage

At 0% effect: None.

## 18. Positive coverage

At 8% effect: None.

## 19. Negative coverage

At −5% effect: None.

## 20. Parallel-trends findings

{'coverage_by_parallel_trends_regime': {}, 'clean_vs_severe_positive_coverage': {'clean_parallel_trends': None, 'severe_pretrend_violation': None}}

## 21. Serial-correlation findings

Serial-correlation world positive coverage: None.

## 22. Timing findings

Staggered blocked runs: 0.

## 23. Worst-world behavior

Positive coverage remains low across clean and stress worlds when bootstrap miscentering present.

## 24. Failure analysis

{'total_runs': 22, 'failed_runs': 22, 'timing_blocked_runs': 0, 'overall_failure_rate': 1.0, 'harness_defect_probe_failures': 2}

## 25. Policy comparisons

Oracle recentering improves coverage diagnostically; production policy H blocks causal interval.

## 26. Root cause

Driver: `bootstrap_interval_miscentering_plus_harness_geometry_defect`; harness defect: True.

## 27. Algorithm changes

None in this artifact. Production bootstrap/point alignment requires separate fix with regression tests.

## 28. TrustReport eligibility implications

DCM-004 remains `INSUFFICIENT_EVIDENCE`; causal-interval candidacy unsupported.

## 29. Authorization status

**Blocked** — `trust_report_authorized_count = 0`.

## 30. Remaining limitations

- Synthetic worlds only; cumulative level truth matches DID cumulative_att scale.
- Oracle recentering is diagnostic only.
- Does not modify D5-STAT-DID-BOOTSTRAP-001 committed archive.
- Cluster/unit bootstrap not available in DID embedded path.
- Production acceptance thresholds not defined.

## 31. Governance verdict

**`did_bootstrap_remediation_failed`**

