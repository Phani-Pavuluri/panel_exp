# D5 Trust DID Bootstrap Remediation 001 — Report

**Artifact ID:** D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001
**Verdict:** `did_bootstrap_causal_interval_remediated_requires_reassessment`
**Summary:** [`archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json`](archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json)
**Threshold label:** `provisional_for_remediation_characterization_only`

## 1. Executive summary

This artifact diagnoses DCM-004 DID+bootstrap interval undercoverage. Under corrected assignment (`test_0` treated only), point estimates recover injected cumulative level effects, but embedded bootstrap CIs in production `DID.py` are miscentered relative to reported `cumulative_att`. Canonical D5-STAT harness has a separate `groups.values()` assignment defect. **No TrustReport authorization.**

This artifact diagnoses DCM-004. It does not correct the canonical D5 harness. It does not change production DID bootstrap behavior. It does not perform DCM-004 eligibility reassessment. It does not authorize TrustReport.

## 2. Prior DCM-004 status

DCM-004 classified `INSUFFICIENT_EVIDENCE` with ~0% positive coverage in `D5_STAT_DID_BOOTSTRAP_001_results.json`.

## 3. Scope

6 diagnostic worlds, effect-size sweep, timing/parallel-trends/serial regimes, bootstrap policy comparisons, harness defect probe.

## 4. Non-goals

- No production DID code changes
- No canonical D5-STAT archive rewrite
- No TrustReport promotion or authorization
- No DCM-004 reassessment in this artifact

## 5. DID estimand

Cumulative treated-minus-synthetic-control ATT over post periods (**cumulative level units**).

## 6. Production DID path

`panel_exp/methods/DID.py` — pooled TWFE with path-based `cumulative_att` in `run_analysis`; bootstrap in `_block_bootstrap_inference` during `fit_model`.

## 7. Bootstrap implementation

Moving-block **time-period** resampling; percentiles of `bootstrap_cumulative_effects_`.

## 8. Canonical D5 harness defect

Confirmed: True. `D5-STAT-DID-BOOTSTRAP-001` uses `groups.values()` flattening control+test_0 → all units treated, zero controls. Fix deferred to `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION`.

## 9. Remediation harness architecture

Uses `corrected_test_0` assignment; probes `broken_groups_values`; records bootstrap center, interval center, oracle shift.

## 10. Worlds

6 worlds (see summary JSON).

## 11. Effect sizes

0.0, 0.08

## 12. Timing regimes

Common timing supported; staggered pooled DID blocked.

## 13. Parallel-trends regimes

holds · mild_violation · severe_violation · staggered_blocked.

## 14. Serial-dependence regimes

clean_iid · serial_correlation · clustered_shocks · heteroskedastic · standard_stress.

## 15. Point-estimate findings

Sign accuracy (positive): 1.0000; mean bias: 1.5314; RMSE @ 8%: 4.0812.

## 16. Bootstrap-center findings

Bootstrap mean: 17.8267; point: 316.3268; gap: 298.5001.

## 17. Interval-centering findings

Interval centered on: bootstrap_cumulative_att_distribution; miscentering dominant: True.

## 18. Variance findings

Point-in-bootstrap-CI rate: 1.0000; mean width: 259.9025.

## 19. Null coverage

@ 0% effect: 1.0000; type-I: 0.0000.

## 20. Positive coverage

@ 8% effect: 1.0000.

## 21. Negative coverage

@ −5% effect: —.

## 22. Common-timing findings

1.0000

## 23. Staggered-timing findings

Blocked runs: 0.

## 24. Parallel-trends findings

Clean vs severe positive coverage: {'clean_parallel_trends': 1.0, 'severe_pretrend_violation': 1.0}.

## 25. Serial-correlation findings

clean_iid positive coverage: 1.0000; serial_correlation: 1.0000.

## 26. Policy comparisons

A production interval retains low positive coverage; B/C diagnostic recentering/oracle improve coverage diagnostically only.

## 27. Root-cause determination

Driver: `bootstrap_interval_miscentering_relative_to_path_cumulative_att`.

## 28. Production-defect decision

**production_defect_indeterminate** — recommended follow-up: `none`.

## 29. Harness-defect decision

Harness defect confirmed: True; canonical fix: `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION`.

## 30. TrustReport implications

DCM-004 remains `INSUFFICIENT_EVIDENCE`; causal-interval candidacy unsupported.

## 31. Authorization status

**Blocked** — `trust_report_authorized=false`, `trust_report_ready=false`.

## 32. Required follow-up artifacts

- `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION`
- `DCM-004 eligibility reassessment (after harness + production corrections as applicable)`

## 33. Limitations

- Synthetic worlds only; cumulative level truth matches DID cumulative_att scale.
- Oracle recentering is diagnostic only.
- Does not modify D5-STAT-DID-BOOTSTRAP-001 committed archive.
- Does not change production DID bootstrap behavior.
- Does not perform DCM-004 eligibility reassessment.
- Cluster/unit bootstrap not available in DID embedded path.
- Production acceptance thresholds not defined.

## 34. Governance verdict

**`did_bootstrap_causal_interval_remediated_requires_reassessment`**

