# DCM-005 TrustReport Eligibility Reassessment — Report

**Artifact ID:** DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001
**Verdict:** `dcm005_mixed_path_specific_restrictions_no_authorization`
**Aggregate status:** `MIXED_WITH_TERMINAL_PATH_DECISIONS`

> This reassessment issues path-specific decisions for DCM-005.
> It does not authorize TrustReport.
> It does not promote any TBRRidge inference path.
> It does not reinterpret diagnostic intervals as causal uncertainty.

## 1. Executive summary

DCM-005 TBRRidge BRB, KFold, and Placebo paths reassessed from committed trust characterization evidence. BRB centering corrected but variance calibration failed; deferred for remediation. KFold diagnostic-only. Placebo null-monitor-only. **No TrustReport authorization.**

## 2. Why DCM-005 reassessment was required

Prior harness marked INSUFFICIENT_EVIDENCE / INELIGIBLE without path-specific trust evidence.

## 3. Prior DCM-005 status

{'DCM-005-BRB': 'INSUFFICIENT_EVIDENCE', 'DCM-005-KFOLD': 'INSUFFICIENT_EVIDENCE', 'DCM-005-PLACEBO': 'INELIGIBLE'}

## 4. Evidence chain

D5-TRUST-TBRRIDGE-BRB-001 → TBRRIDGE-BRB-INTERVAL-CORRECTION-001 → D5-TRUST-TBRRIDGE-KFOLD-001 → D5-TRUST-TBRRIDGE-PLACEBO-001 → this reassessment.

## 5. Scope

DCM-005 BRB, KFold, Placebo paths only.

## 6. Non-goals

No production changes; no full-matrix reassessment; no TrustReport promotion.

## 7. DCM-005 identity

TBRRidge estimator with BRB, KFold, or Placebo inference on unit-panel single-cell geometry.

## 8. Path-specific decision framework

Each path receives independent statistical, semantic, and eligibility decisions.

## 9. BRB evidence summary

Centering gap ~−292.6 → ~0.006; null coverage ~40.5%; type-I ~59.5%; variance ratio ~11.

## 10. BRB statistical decision

`DEFERRED_FOR_REMEDIATION` — variance calibration unacceptable for causal interval.

## 11. BRB semantic decision

`restricted_causal_interval_blocked` — causal interval blocked.

## 12. BRB investigation disposition

`REMEDIATE` — INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 → DEFERRED_WITH_TRIGGER → TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001.

## 13. KFold evidence summary

CV stability band; sign accuracy ~1.7% positive; no temporal leakage; not causal ATT interval.

## 14. KFold statistical decision

`INELIGIBLE_FOR_CAUSAL_INTERVAL`

## 15. KFold semantic decision

`DIAGNOSTIC_ONLY` — dispersion band is diagnostic only.

## 16. KFold investigation disposition

`DIAGNOSTIC_ONLY` — INV-TBRRIDGE-KFOLD-NULL-FPR-001 RESOLVED.

## 17. Placebo evidence summary

Single-treated only; ≥5 controls; null type-I 0%; null-reference / falsification semantics.

## 18. Placebo statistical decision

`NULL_MONITOR_ACCEPTABLE` for governed null-monitor role.

## 19. Placebo semantic decision

`NULL_MONITOR_ONLY` — not causal ATT uncertainty.

## 20. Placebo investigation disposition

`NULL_MONITOR_ONLY` — INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001 RESOLVED.

## 21. Aggregate DCM-005 status

`MIXED_WITH_TERMINAL_PATH_DECISIONS`

## 22. Supported roles by path

BRB: (); KFold: ('directional_diagnostic', 'model_selection_diagnostic'); Placebo: ('null_monitor', 'falsification_diagnostic')

## 23. Blocked roles by path

BRB: ('trust_report', 'calibration_signal', 'production', 'causal_interval'); KFold: ('trust_report', 'calibration_signal', 'production', 'causal_interval'); Placebo: ('trust_report', 'calibration_signal', 'production', 'causal_interval')

## 24. Promotion-candidate status

`eligible_for_promotion: false` for all paths.

## 25. TrustReport authorization

**Blocked** — `trust_report_authorized_count: 0`.

## 26. Other DCM rows unchanged

DCM-001–004, 006–008 preserved with `unchanged_due_to_no_new_evidence`.

## 27. Remaining limitations

BRB variance remediation pending; FULL reassessment not performed.

## 28. Governance updates

OPEN_INVESTIGATIONS_001 consumed for KFold and Placebo; BRB deferred with remediation trigger.

## 29. Final verdict

**`dcm005_mixed_path_specific_restrictions_no_authorization`**

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-TBRRIDGE-KFOLD-NULL-FPR-001
- INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001

**New investigations opened:** none

**Existing investigations updated:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 → DEFERRED_WITH_TRIGGER; REMEDIATE → TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001
- INV-TBRRIDGE-KFOLD-NULL-FPR-001 → RESOLVED; DIAGNOSTIC_ONLY
- INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001 → RESOLVED; NULL_MONITOR_ONLY

**Deferred issues:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**Explicit exclusions:**
- FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT

**Revisit trigger:** After BRB variance remediation or remediation closeout decision

**Required decision checkpoint:** FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT

**Next artifact:** D5-TRUST-MULTICELL-PERCELL-INFERENCE-001

