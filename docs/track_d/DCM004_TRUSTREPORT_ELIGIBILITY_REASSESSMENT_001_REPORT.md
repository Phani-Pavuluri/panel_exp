# DCM-004 TrustReport Eligibility Reassessment — Report

**Artifact ID:** DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001
**Verdict:** `dcm004_eligible_with_restrictions_no_authorization`
**Reassessed status:** `ELIGIBLE_WITH_RESTRICTIONS`

> Reassesses DCM-004 (DID + bootstrap) only. **No TrustReport authorization.**

## 1. Executive summary

DCM-004 reassessed using corrected harness geometry, production bootstrap readout fix, and post-fix canonical replay. Positive coverage improved materially; aggregate null type-I rose to ~32% but supported-world type-I remains ~13% with stress-world concentration. **Status: `ELIGIBLE_WITH_RESTRICTIONS`** with promotion blocked.

## 2. Why reassessment was required

Prior INSUFFICIENT_EVIDENCE reflected harness defect and production bootstrap miscentering.

## 3. Prior DCM-004 status

`INSUFFICIENT_EVIDENCE` — missing/invalid positive coverage evidence.

## 4. Evidence chain

D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 → D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION → DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001 → this reassessment.

## 5. Corrected production behavior

Centered-deviation percentile bootstrap intervals anchored to cumulative_att.

## 6. Scope

DCM-004 only.

## 7. Non-goals

No production changes; no promotion; no full-matrix reassessment.

## 8. DCM-004 identity

DID + embedded bootstrap; single-cell unit panel; causal_interval readout.

## 9. DID estimand

Cumulative level ATT (`cumulative_att_level`).

## 10. Bootstrap interval semantics

`centered_deviation_percentile` on block-resampled cumulative path replicates.

## 11. Geometry gate

`pass` — explicit test_0/control, n_treated>0, n_control≥4.

## 12. Scale gate

`pass` — cumulative level truth/point/interval aligned.

## 13. Timing gate

`pass` — common simultaneous adoption only.

## 14. Parallel-trends gate

`warning_required` — pretrend diagnostic required; violation worlds excluded.

## 15. Dependence gate

`warning_required` — serial/heteroskedastic caveats on noisy worlds.

## 16. Overall null calibration

Null coverage 0.6833333333333333; type-I 0.31666666666666665.

## 17. Supported-world null calibration

Null coverage 0.8666666666666667; type-I 0.13333333333333333.

## 18. Unsupported-world null calibration

Null coverage 0.5; type-I 0.5.

## 19. Positive-effect coverage

Overall 0.9333333333333332; clean parallel 1.0.

## 20. Negative-effect coverage

Not characterized in canonical D5 battery.

## 21. Type-I decomposition

Overall 0.31666666666666665; supported 0.13333333333333333; unsupported 0.5; post_shock 1.0.

## 22. Interval-width findings

Finite widths; point-in-interval ~100% post-correction.

## 23. Worst-world behavior

post_shock_null drives unsupported null failure (type-I 100%).

## 24. Supported contract

Common timing, parallel-trends gate, cumulative level estimand, stress worlds excluded.

## 25. Semantic restrictions

`restricted_causal_interval` — no population ATE, no staggered pooled DID.

## 26. Reassessed eligibility status

`ELIGIBLE_WITH_RESTRICTIONS`

## 27. Promotion-candidate status

`eligible_for_promotion: false`

## 28. Other DCM rows unchanged

DCM-001–003, 005–008 preserved with `unchanged_due_to_no_new_evidence`.

## 29. TrustReport authorization

**Blocked** — `trust_report_authorized_count: 0`.

## 30. Remaining limitations

Stress-world null behavior; noisy-world 80% positive coverage; provisional gates only.

## 31. Required next validation

DCM-005 TBRRidge paths; DCM-006 multi-cell; DCM-008 stratified; FULL reassessment later.

## 32. Governance verdict

**`dcm004_eligible_with_restrictions_no_authorization`**

