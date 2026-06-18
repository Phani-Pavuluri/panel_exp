# TrustReport Eligibility Validation 001 — Report

**Artifact ID:** TRUSTREPORT-ELIGIBILITY-VALIDATION-001  
**Verdict:** `trustreport_eligibility_mixed_with_restrictions_no_authorization`

## 1. Executive summary

Defines and empirically validates provisional TrustReport **promotion candidacy** requirements for governed readouts. Evaluates DCM-001–008 using committed D5 statistical archives. **No TrustReport output is authorized.** Downstream authorization gateway remains BLOCKED for `trust_report`.

## 2. Why eligibility validation was required

The downstream authorization gateway answers whether a consumer role may proceed. It does not answer whether a combination has sufficient statistical, semantic, geometric, and governance evidence to become a TrustReport promotion candidate.

## 3. Difference between eligibility and authorization

| Layer | Question | This artifact |
|-------|----------|---------------|
| Eligibility | Is there enough evidence to consider promotion? | `evaluate_trustreport_eligibility()` |
| Authorization | May TrustReport consume the readout? | Still BLOCKED via gateway |

`trust_report_promotion_candidate` may be true only for `ELIGIBLE_CANDIDATE`. `trust_report_ready` remains false.

## 4. Scope

- TrustReport eligibility contract and reason codes
- DCM-specific classification rules
- Empirical harness over committed D5 archives
- Track B integration (`trustreport_eligibility` on decision inputs)
- Fixtures and tests

## 5. Non-goals

- TrustReport authorization or production export
- Estimator/inference/design algorithm changes
- Live operator approval workflows

## 6. Governed evidence requirements

Governed `ReadoutEvidence`, valid marker, inference-boundary result, combination resolution, explicit estimand and interval semantics.

## 7–11. Statistical, semantic, geometry, provenance, freshness

Provisional thresholds labeled `provisional_for_trustreport_eligibility_only`. Null-world coverage, type-I error, failure rate, bias on positive scenarios, worst-world status, provenance completeness, and freshness evaluated separately.

## 12. Provisional thresholds

Aligned with `PROVISIONAL_THRESHOLDS` in design-combination execution and D5 Level-B harness conventions (null FPR ≤0.10 clean null, positive coverage ≥0.50 for causal interval candidacy, failure rate ≤0.10).

## 13. Candidate combinations

Lane A evaluated: SCM+JK, stratified+SCM/JK, DID+bootstrap, multi-cell per-cell, TBRRidge paths.

## 14. DCM-001 findings

**ELIGIBLE_WITH_RESTRICTIONS** (eligibility validation, 2026-06-17). Null-world coverage ~93%; positive-scenario coverage ~7% on **pre-correction fractional-percent metrics**. Causal interval TrustReport not supported at validation time; null-monitor / research CI only.

**Remediation (2026-06-17):** [`D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_REPORT.md`](D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_REPORT.md) diagnosed percent-vs-level mismatch.

**Harness correction (2026-06-17):** [`D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md`](D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md) regenerated canonical archive with level-consistent coverage (positive ~90%). Historical archive retained.

**Eligibility reassessment (2026-06-18):** [`TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md`](TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) — DCM-001 remains `ELIGIBLE_WITH_RESTRICTIONS` on corrected evidence; no authorization.

## 15. DCM-002 findings

**ELIGIBLE_WITH_RESTRICTIONS** for descriptive point-only. **INELIGIBLE** for interval-bearing TrustReport.

## 16. DCM-003 findings

**INELIGIBLE.** Aggregate TBR on unit-panel geometry mismatch.

## 17. DCM-004 findings

**INSUFFICIENT_EVIDENCE.** Null FPR controlled; positive-scenario coverage 0%; identification diagnostics incomplete. **Update (2026-06-03):** ✅ [`D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md`](D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md) diagnoses production bootstrap miscentering + canonical harness `groups.values()` defect; eligibility status unchanged pending harness correction and `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001`.

## 18. DCM-005 findings

**INSUFFICIENT_EVIDENCE** (harness) / **INELIGIBLE** when inference boundary BLOCKED. TBRRidge BRB, KFold, Placebo evaluated separately; causal interval semantics not validated.

## 19. DCM-006 findings

**ELIGIBLE_WITH_RESTRICTIONS.** Per-cell identity preserved; shared-control dependence and multiplicity limitations documented.

## 20. DCM-007 findings

**INELIGIBLE.** Pooled multi-cell claims permanently excluded.

## 21. DCM-008 findings

**ELIGIBLE_WITH_RESTRICTIONS.** Design feasibility demonstrated; dedicated D5-STAT stratified artifact missing.

## 22. Known ineligible controls

AugSynth interval claim, TBR geometry mismatch, pooled multi-cell, null-monitor-as-causal — all **INELIGIBLE**.

## 23. Insufficient-evidence cases

DID+bootstrap, TBRRidge paths, missing coverage/type-I/provenance — **INSUFFICIENT_EVIDENCE** or **INELIGIBLE**.

## 24. Worst-world behavior

SCM-JK post-shock null elevated FPR; DID parallel worlds show callable failures; TBRRidge scale mismatch documented.

## 25. Failure analysis

Positive-scenario under-coverage is primary blocker for causal-interval candidacy across SCM-JK and DID-bootstrap.

## 26. Promotion-candidate results

**Zero** `ELIGIBLE_CANDIDATE` combinations. No `trust_report_promotion_candidate=true` in this artifact.

## 27. TrustReport authorization status

`authorization_summary.trust_report_authorized_count = 0` for all combinations.

## 28. Remaining limitations

Provisional thresholds only; D5 archives mark `trust_role_allowed=false`; TBRRidge causal paths unvalidated.

## 29. Required promotion evidence

Future `TRUSTREPORT_DOWNSTREAM_PROMOTION_001` must supply role-specific approved evidence per DCM row, positive-scenario coverage, and Battery C+ statistical validation.

## 30. Recommended next work

See [`TRUSTREPORT_ELIGIBILITY_REMEDIATION_PLAN_001.md`](../TRUSTREPORT_ELIGIBILITY_REMEDIATION_PLAN_001.md) for prioritized `D5-TRUST-*` remediation artifacts. Sequence: remediation → `TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001` → `TRUSTREPORT_DOWNSTREAM_PROMOTION_001`.

## 31. Governance verdict

`trustreport_eligibility_mixed_with_restrictions_no_authorization`
