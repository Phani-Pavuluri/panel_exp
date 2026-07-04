# STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` |
| **Artifact type** | `statistical_promotion_threshold_enforcement` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `statistical_promotion_thresholds_enforced_no_method_unblock_or_claim_authorization` |
| **Base commit** | `3edb276` (Add assignment panel integrity runtime) |
| **Final verdict** | `statistical_promotion_thresholds_enforced_no_method_unblock_or_claim_authorization` |

---

## 2. Source files inspected

- `panel_exp/validation/production_catalog_blocklist_001.py`
- `panel_exp/validation/did_instrument_estimand_registry_001.py`
- `panel_exp/validation/assignment_panel_integrity_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/estimator_inference_executor_adapters_002.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `docs/track_d/PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001_REPORT.md`
- `docs/track_d/DID_INSTRUMENT_ESTIMAND_UNIFICATION_001_REPORT.md`
- `docs/track_d/ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001_REPORT.md`
- `docs/track_d/METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001.md`
- `docs/track_d/AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001.md`
- D5 archive summaries (coverage, calibration, recovery, promotion eligibility)

---

## 3. Audit finding being addressed

P0 governed runtime hardening (`AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001`) identified that statistical promotion thresholds were documented in promotion protocol and D5 archives but not enforced at runtime. Methods could appear eligible for production review based on existence, tests, or documentation without passing numeric characterization gates.

---

## 4. Problem statement

Tests, docs, and subjective judgment are not sufficient for production promotion. A method/instrument must not move toward production-candidate or production-safe status until observed statistical evidence passes explicit numeric policy gates.

---

## 5. Runtime purpose

`evaluate_statistical_promotion_thresholds` evaluates supplied characterization evidence against governed numeric threshold policy for a requested maturity state. It returns pass/fail/inconclusive/blocked promotion status, metric-level results, blockers, and remediation guidance. It does not read archive files at runtime, compute new statistics, or authorize claims.

---

## 6. Threshold policy

Conservative governed defaults (config-overridable):

| Gate | Restricted expert review | Production candidate | Production safe |
|------|-------------------------|---------------------|-----------------|
| Coverage min | 0.80 (optional) | 0.90 (required if inference) | 0.90 (required) |
| Type I / FPR max | 0.15 (optional) | 0.10 (required if inference) | 0.05 (required) |
| Directional false signal max | — | 0.10 (optional) | 0.10 (required) |
| Negative interval width rate max | 0.0 | 0.0 | 0.0 |
| Invalid interval rate max | 0.0 | 0.0 | 0.0 |
| Power min | — | 0.80 (optional) | — |
| Bias abs / RMSE | required metric only if threshold supplied | same | required with threshold |

Policy thresholds are governance gates, not statistical universal truths.

---

## 7. Maturity promotion gates

- **RESTRICTED_EXPERT_REVIEW:** known estimand, method identity, minimum recovery evidence, no invalid interval behavior, no negative characterization blocker, diagnostic requirements documented.
- **PRODUCTION_CANDIDATE:** all restricted gates plus numeric thresholds, coverage/Type I/FPR/directional/interval gates as applicable, assignment compatibility, assignment-panel integrity compatibility, governed runtime support, production catalog not blocked.
- **PRODUCTION_SAFE:** all production-candidate gates plus stronger thresholds, diagnostic/sensitivity evidence, null/A/A calibration, claim authorization compatibility, trusted readout compatibility, no open P0 blockers. Unreachable by default without every gate and explicit authorization path.

---

## 8. Metric taxonomy

Metric results include: `metric_name`, `observed_value`, `threshold_operator`, `threshold_value`, `threshold_status`, `evidence_source`, `required_for_requested_maturity`, `failure_category`.

Metric statuses: `THRESHOLD_MET`, `THRESHOLD_FAILED`, `THRESHOLD_MISSING`, `THRESHOLD_NOT_APPLICABLE`, `THRESHOLD_NOT_DEFINED`.

---

## 9. Failure / remediation taxonomy

Failure categories include missing evidence, missing numeric threshold, bias/RMSE/coverage/Type I/FPR/directional/interval/power/calibration failures, negative characterization evidence, requested promotion not allowed, production catalog blocked, claim authorization missing.

Remediation categories include add recovery/coverage/null-AA calibration evidence, fix interval construction, fix method implementation, define numeric thresholds, recharacterize method, keep research/diagnostic only, block production catalog.

---

## 10. Known-negative policy evidence

Policy-encoded blockers (not computed evidence):

- **DID_BOOTSTRAP / DID_BOOTSTRAP_INFERENCE:** production promotion blocked until bootstrap remediation and characterization pass.
- **TBR_RIDGE + KFOLD:** blocked when invalid/negative interval evidence remains.
- **TBR_RIDGE + CONFORMAL:** blocked until interval validity/calibration evidence passes.
- **TBR_RIDGE + JACKKNIFE/JK:** blocked until interval sanity and calibration pass.
- **AUGSYNTH + CONFORMAL:** blocked until adapter and null calibration pass.
- **TROP / MTGP / BayesianTBR:** research-only until recovery/calibration and governed runtime support exist.
- **DID_2X2_POINT_ESTIMATE:** not production-candidate/production-safe without uncertainty and claim gates.

---

## 11. Production catalog integration

When `production_context` is production-oriented and enforcement is enabled, `evaluate_production_catalog_status` invokes statistical threshold evaluation. Failed/inconclusive promotion adds blockers: `MISSING_STATISTICAL_THRESHOLDS`, `MISSING_REQUIRED_EVIDENCE`, `STATISTICAL_PROMOTION_THRESHOLD_FAILED`. Threshold pass is necessary but not sufficient; existing catalog blocklist rules remain authoritative.

---

## 12. Method suitability integration

Instrument matrix rows attach threshold overlay fields: `statistical_promotion_status`, `statistical_threshold_failures`, `statistical_threshold_evidence`, `statistical_promotion_trace`, `is_statistically_promotable`, `is_statistically_promotion_blocked`. A method can be method-suitable but statistically promotion-blocked.

---

## 13. Readout plan integration

Readout planning preserves threshold status on instrument rows. Instruments with `STATISTICAL_PROMOTION_FAILED` or `STATISTICAL_PROMOTION_BLOCKED` are excluded from production primary candidates. Review-context planning uses restricted-expert-review maturity for overlay evaluation.

---

## 14. Research vs production boundary

Supplied evidence is evaluated; no method is unblocked by default. Research-only families remain research-only. Production-safe promotion remains unreachable without full gate pass and claim/trusted-readout authorization paths (not implemented).

---

## 15. Claim / production authorization boundary

All authorization flags remain false: no methods unblocked, no production catalog loosened, no production-safe promotion, no claim authorization runtime, no authorized claim text, no trusted readout handoff, no production readout authorization, no causal/incremental-lift/ROI claim authorization, no production authorization, no estimator/inference/bootstrap implementation, no p-values/CIs/uncertainty computation, no MMM runtime calls, no MMM calibration, no LLM decisioning.

Positive capability flags: `statistical_promotion_thresholds_defined`, `statistical_promotion_thresholds_evaluated`, `statistical_promotion_failures_block_production_promotion`.

---

## 16. Tests added

`tests/validation/test_statistical_promotion_thresholds_001.py` — public API, missing evidence, missing thresholds, coverage/Type I/FPR/directional/interval failures, known-negative blockers, config override, list/dataclass input, production catalog/method suitability/readout plan integration, authorization boundary flags.

---

## 17. Validation results

Targeted pytest for new module and integration regressions pass. Summary JSON validates. Safety grep confirms no false authorization flags.

---

## 18. Known limitations

- Evaluates supplied evidence only; does not load D5 archive files at runtime.
- Bias/RMSE gates require explicit threshold configuration to fail/pass numerically.
- Production-safe remains blocked by claim authorization and trusted readout prerequisites.
- Readout overlay uses restricted-expert-review maturity in review context; hard blocking applies only to FAILED/BLOCKED promotion statuses.

---

## 19. Recommended next artifact

**Recommended:** `GOVERNED_RANDOMIZATION_RUNTIME_001`

**Alternative:** `SRM_BALANCE_READOUT_DIAGNOSTIC_001`
