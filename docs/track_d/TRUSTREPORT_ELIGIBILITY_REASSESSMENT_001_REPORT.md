# TrustReport Eligibility Reassessment 001 — Report

**Artifact ID:** TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001
**Verdict:** `trustreport_dcm001_eligible_with_restrictions_no_authorization`
**DCM-001 reassessed status:** `ELIGIBLE_WITH_RESTRICTIONS`

## 1. Executive summary

Reassesses DCM-001 (SCM + UnitJackknife) using corrected canonical D5-STAT-SCM-JK-001 evidence after harness correction. Historical ~7% positive coverage interpretation is superseded. **No TrustReport authorization.**

## 2. Why reassessment was required

Harness correction fixed assignment geometry and level-consistent coverage metrics.

## 3. Prior eligibility status

`ELIGIBLE_WITH_RESTRICTIONS` with positive coverage ~7% on invalid percent scale.

## 4. Historical evidence defect

Invalid `groups.values()` assignment and level-vs-fractional-percent truth mismatch.

## 5. Corrected evidence source

`D5_STAT_SCM_JK_001_results.json` (harness correction supersession metadata required).

## 6. Scope

DCM-001 only.

## 7. Non-goals

No TrustReport authorization; no SCM/JK algorithm changes; no unrelated DCM upgrades.

## 8. DCM-001 identity

SCM + UnitJackknife, unit-panel single-cell, treated-unit level effect.

## 9. Geometry reassessment

n_treated_mean=4.933333333333334, n_control_mean=11.066666666666666, donor_count_mean=11.066666666666666.

## 10. Effect-scale reassessment

Canonical `level_effect`; fractional-percent coverage excluded from eligibility.

## 11. Null coverage

Level-scale null coverage: **0.8933333333333333**

## 12. Positive-effect coverage

Level-scale positive coverage: **0.9** (clean=1.0, noisy=0.8).

## 13. Negative-effect coverage

Not evaluated in D5-STAT-SCM-JK-001 battery.

## 14. Type-I error

Empirical type-I error: **0.10666666666666666**

## 15. Bias and RMSE

bias_level=0.3873021792040174, rmse_level=1.0995670895727094 (level scale).

## 16. Pre-fit sensitivity

prefit_gate_status=warning_required

## 17. Donor-support sensitivity

donor_gate_status=pass

## 18. Worst-world behavior

Worst positive-world level coverage: **0.8**

## 19. Support gates

`{"support_gate_status": "support_gated", "prefit_gate_status": "warning_required", "donor_gate_status": "pass", "label": "provisional_for_trustreport_reassessment_only"}`

## 20. Semantic restrictions

Treated-unit effect only; level-scale; support-gated; no population ATE.

## 21. Reassessed status

`ELIGIBLE_WITH_RESTRICTIONS`

## 22. Promotion-candidate status

eligible_for_promotion=False

## 23. Unchanged DCM rows

9 combinations unchanged (no new evidence).

## 24. TrustReport authorization status

`trust_report_authorized=false`, `trust_report_authorized_count=0`.

## 25. Remaining limitations

- Reassessment applies to DCM-001 only; other combinations unchanged.
- Provisional gates labeled provisional_for_trustreport_reassessment_only.
- Does not authorize TrustReport or downstream roles.
- Historical percent-scale coverage excluded from reassessment metrics.
- Stratified DCM-008 and multi-cell paths require separate artifacts.

## 26. Required next validation

✅ `D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001` (production miscentering confirmed) → `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION` → `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` → ✅ `DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001` → ✅ D5-TRUST TBRRidge lanes (BRB, KFold, Placebo characterized) → ✅ **`DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001`** → ✅ **`D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`** (DCM-006) → **`D5-TRUST-STRATIFIED-SCM-JK-001`** → **`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT`**.

## 27. Governance verdict

`trustreport_dcm001_eligible_with_restrictions_no_authorization`

