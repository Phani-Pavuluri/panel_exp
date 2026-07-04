# CLAIM_AUTHORIZATION_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `CLAIM_AUTHORIZATION_RUNTIME_001` |
| **Artifact type** | `claim_authorization_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `claim_authorization_runtime_implemented_no_trusted_report_or_production_authorization` |
| **Base commit** | `08f1312` (Add SRM balance readout diagnostic) |
| **Final verdict** | `claim_authorization_runtime_implemented_no_trusted_report_or_production_authorization` |

---

## 2. Source files inspected

- `panel_exp/validation/claim_authorization_contract_001.py`
- `panel_exp/validation/production_catalog_blocklist_001.py`
- `panel_exp/validation/did_instrument_estimand_registry_001.py`
- `panel_exp/validation/assignment_panel_integrity_runtime_001.py`
- `panel_exp/validation/statistical_promotion_thresholds_001.py`
- `panel_exp/validation/governed_randomization_runtime_001.py`
- `panel_exp/validation/srm_balance_readout_diagnostic_001.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- Audit and governance docs

---

## 3. Audit finding being addressed

P0 pre-claim hardening inserted governed evidence gates before claim authorization runtime. A numeric result, diagnostic pass, or execution completion does not constitute claim authorization. Claims must be classified against typed evidence from production catalog, assignment-panel integrity, SRM/balance, diagnostics/sensitivity, statistical promotion, execution, and uncertainty artifacts.

---

## 4. Problem statement

Numeric result does not equal claim authorization. Without a governed claim authorization runtime, downstream review could treat point estimates, diagnostic passes, or partial evidence as causal lift, ROI, production readout, or statistical significance claims.

---

## 5. Runtime purpose

`authorize_readout_claims` classifies requested readout claims as authorized, authorized with restrictions, insufficient evidence, blocked, or not evaluated based on consumed evidence reports. It emits structured caveat codes, blockers, and allowed/disallowed surfaces — not polished report text.

---

## 6. Input contract

Accepts dict, dataclass-like, or list input (multiple requests, no ranking).

Supported fields: `claim_requests`, `claim_type`, `claim_scope`, `production_context`, `instrument_id`, `execution_result`, `effect_estimate_report`, `uncertainty_report`, `assignment_panel_integrity_report`, `srm_balance_diagnostic_report`, `governed_randomization_report`, `diagnostics_sensitivity_report`, `statistical_promotion_report`, `production_catalog_report`, `instrument_execution_results`, and related evidence sources.

---

## 7. Claim taxonomy

Canonical claim types include descriptive/metadata claims (`ASSIGNMENT_INTEGRITY_DESCRIPTION`, `RANDOMIZATION_ARTIFACT_DESCRIPTION`, `SRM_BALANCE_DIAGNOSTIC_DESCRIPTION`, `DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION`), restricted execution claims (`POINT_ESTIMATE_DESCRIPTION`, `DIRECTIONAL_RESULT_DESCRIPTION`), and blocked strong claims (`CAUSAL_LIFT_CLAIM`, `INCREMENTAL_CONVERSIONS_CLAIM`, `INCREMENTAL_REVENUE_CLAIM`, `ROI_CLAIM`, `STATISTICAL_SIGNIFICANCE_CLAIM`, `CONFIDENCE_INTERVAL_CLAIM`, `PRODUCTION_READOUT_CLAIM`, `TRUSTED_BUSINESS_RECOMMENDATION`).

Contract aliases mapped: `POINT_ESTIMATE_CLAIM` → `POINT_ESTIMATE_DESCRIPTION`, `INCREMENTAL_LIFT_CLAIM` → `INCREMENTAL_CONVERSIONS_CLAIM`, etc.

---

## 8. Authorization status taxonomy

Per-claim: `CLAIM_AUTHORIZED`, `CLAIM_AUTHORIZED_WITH_RESTRICTIONS`, `CLAIM_INSUFFICIENT_EVIDENCE`, `CLAIM_BLOCKED`, `CLAIM_NOT_EVALUATED`.

Overall report: `CLAIM_AUTHORIZATION_COMPLETED`, `CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS`, `CLAIM_AUTHORIZATION_BLOCKED`, `CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE`, `CLAIM_AUTHORIZATION_NOT_EVALUATED`.

---

## 9. Evidence requirements by claim type

- **Descriptive claims:** corresponding diagnostic/integrity/randomization report passed
- **Point estimate description:** governed execution completed, effect estimate computed, integrity passed when panel present, production catalog not blocking, DID 2×2 point-estimate instrument only
- **Directional description:** point estimate + integrity + SRM/balance + promotion gates
- **Causal/incremental/ROI/production/trusted:** full evidence chain including uncertainty/inference — blocked in current repo state
- **Statistical significance / CI:** governed inference and uncertainty required — blocked

---

## 10. Blocker taxonomy

`PRODUCTION_CATALOG_BLOCKED`, `METHOD_NOT_PRODUCTION_SAFE`, `STATISTICAL_PROMOTION_FAILED`, `STATISTICAL_PROMOTION_MISSING`, `ASSIGNMENT_PANEL_INTEGRITY_FAILED`, `ASSIGNMENT_PANEL_INTEGRITY_MISSING`, `SRM_BALANCE_DIAGNOSTIC_FAILED`, `SRM_BALANCE_DIAGNOSTIC_MISSING`, `REQUIRED_DIAGNOSTIC_FAILED`, `REQUIRED_DIAGNOSTIC_MISSING`, `UNCERTAINTY_MISSING`, `INFERENCE_NOT_IMPLEMENTED`, `CONFIDENCE_INTERVAL_MISSING`, `P_VALUE_MISSING`, `EFFECT_ESTIMATE_MISSING`, `TRUSTED_REPORT_RUNTIME_MISSING`, `CLAIM_SCOPE_MISSING`, `ESTIMAND_MISMATCH`, `INSTRUMENT_CLAIM_MISMATCH`, `PRODUCTION_CONTEXT_NOT_AUTHORIZED`.

---

## 11. Caveat taxonomy

`DESCRIPTIVE_ONLY`, `POINT_ESTIMATE_ONLY`, `NO_UNCERTAINTY`, `NO_STATISTICAL_SIGNIFICANCE`, `NO_CONFIDENCE_INTERVAL`, `NO_CAUSAL_CLAIM`, `NO_INCREMENTAL_CLAIM`, `NO_ROI_CLAIM`, `NO_PRODUCTION_AUTHORIZATION`, `RESEARCH_OR_REVIEW_ONLY`, `DIAGNOSTIC_ONLY`, `METHOD_BLOCKED_FOR_PRODUCTION`.

---

## 12. Retry/remediation taxonomy

`ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE`, `ADD_SRM_BALANCE_DIAGNOSTIC`, `ADD_REQUIRED_DIAGNOSTICS`, `ADD_GOVERNED_UNCERTAINTY`, `ADD_STATISTICAL_PROMOTION_EVIDENCE`, `FIX_PRODUCTION_CATALOG_BLOCKER`, `IMPLEMENT_TRUSTED_REPORT_RUNTIME`, `REQUEST_WEAKER_DESCRIPTIVE_CLAIM`, `KEEP_RESEARCH_ONLY`, `BLOCK_CLAIM`.

---

## 13. Integration

- **Production catalog:** consumed via `production_catalog_report` or inline evaluation; never loosened
- **DID semantics:** `DID_2X2_POINT_ESTIMATE` supports restricted point-estimate description; `DID_BOOTSTRAP` blocked for point-estimate claims
- **Assignment-panel integrity / SRM balance / statistical promotion / diagnostics:** consumed as upstream evidence gates
- **Execution runtime:** attaches `claim_authorization_report` to execution packet when `claim_requests` supplied
- **Readout plan:** adds `claim_authorization_required` execution prerequisite when enabled

---

## 14. Research-vs-production boundary

Production context applies stricter catalog and promotion requirements. Restricted descriptive claims remain research/review-only with explicit caveats.

---

## 15. Trusted report boundary

`PRODUCTION_READOUT_CLAIM` and `TRUSTED_BUSINESS_RECOMMENDATION` remain blocked because trusted readout report runtime is not implemented.

---

## 16. Claim / production authorization boundary

No production authorization, production readout authorization, trusted readout handoff, authorized claim text, causal/incremental/ROI/significance/CI claim authorization, method unblocking, or new effect/inference computation. `CLAIM_AUTHORIZED_WITH_RESTRICTIONS` applies only to narrow descriptive claims.

---

## 17. Tests added

`tests/validation/test_claim_authorization_runtime_001.py` covers public API, descriptive/restricted claims, blocking for causal/ROI/significance/CI/production/trusted claims, catalog/integrity/SRM/promotion failures, DID 2×2 vs bootstrap, list/dataclass input, deterministic trace, execution and readout plan integration, and authorization boundary flags.

---

## 18. Validation results

Targeted pytest suites pass. Summary JSON validates. Safety grep confirms no unauthorized capability flags.

---

## 19. Known limitations

- No governed uncertainty/inference path — causal and significance claims remain blocked
- No trusted readout report runtime — production/trusted claims blocked
- No natural-language claim text generation
- Does not execute estimators, diagnostics, or inference

---

## 20. Recommended next artifact

**Primary:** `TRUSTED_READOUT_REPORT_CONTRACT_001`

**Alternative:** `TRUSTED_READOUT_REPORT_RUNTIME_001`
