# SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` |
| **Artifact type** | `scm_jackknife_null_monitor_promotion_evidence_packet_contract` |
| **Lane** | **Lane A — Method / instrument promotion framework application** |
| **Status** | `completed` |
| **Scope** | `evidence_packet_contract_defined_no_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` |
| **Final verdict** | `scm_jackknife_null_monitor_evidence_packet_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` |

**Depends on:**

- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`
- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`
- `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001`
- `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `TRUSTED_READOUT_REPORT_CONTRACT_001`
- `TRUSTED_READOUT_REPORT_RUNTIME_001`

**Pilot reference (complete, do not inherit evidence):** `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

---

## 2. Why this contract exists

`METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001` selected **`geo.scm.jackknife.single_cell.delta_mu.null_monitor`** as the primary next instrument for the generalized method promotion framework (score 32/40). This is the **first non-TBRRidge application** of the framework pattern established by the TBRRidge restricted-review pilot and generalized in `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`.

Null-monitor semantics make this the lowest claim/governance-risk second application: diagnostic/null behavior monitoring only — not causal lift, business lift, CI, p-value, significance, production readout, catalog unblock, or method promotion.

**This contract defines the evidence packet only.** It does not promote SCM, SCM+Jackknife, any instrument, or authorize any claim. It does not implement packet assembly runtime.

---

## 3. Exact instrument identity

**Canonical identity:** `geo.scm.jackknife.single_cell.delta_mu.null_monitor`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `scm` |
| `inference_family` | `jackknife` |
| `geometry` | `single_cell` |
| `point_estimand` | `delta_mu` |
| `surface` | `null_monitor` |
| `interval_semantics` | `not_applicable_for_null_monitor` |

**Catalog alias (must reconcile, not substitute):** `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` — registered in `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` as `SCM_UnitJackKnife`, RANK_3, RESTRICTED_REVIEW. The alias uses `null_monitor` as geometry token and `delete_one_diagnostic` as inference semantics; the canonical identity uses `single_cell` geometry and `null_monitor` surface. Packet assembly must enforce exact canonical identity; alias mapping is documentation-only until a geometry taxonomy artifact reconciles strings.

**Identity rules (non-negotiable):**

- No cross-inference-family promotion (e.g. cannot promote SCM × Placebo from this packet)
- No cross-geometry promotion (e.g. cannot promote multi-treated or aggregate-pooled from single-cell evidence)
- No estimator-family-level SCM promotion
- No SCM placebo promotion (`geo.scm.placebo.*` is a separate instrument)
- No SCM production-readout promotion
- No causal-lift claim inheritance from SCM point-estimator readout behavior
- TBRRidge pilot evidence cannot satisfy SCM evidence categories

---

## 4. Null-monitor scope

### Definition

Null-monitor here means:

- Diagnostic/null behavior monitoring under restricted/non-production review
- False-positive / null-control behavior evidence surface
- Delete-one jackknife stability characterization for SCM unit jackknife path
- Evidence completeness and blocker surfacing for future promotion review input

Null-monitor is not a causal lift readout, business decision surface, confidence interval claim, or production compatibility review.

Null-monitor is **not**:

- A causal lift readout
- A business decision surface
- A confidence interval or significance claim surface
- Production compatibility review
- Catalog unblock authorization

### Allowed null-monitor outputs

- `NULL_MONITOR_STATUS_SUMMARY`
- `EVIDENCE_COMPLETENESS_SUMMARY`
- `MISSING_EVIDENCE_BLOCKER_SUMMARY`
- `FALSE_POSITIVE_DIAGNOSTIC_SUMMARY`
- `IDENTITY_SCOPE_CONSISTENCY_SUMMARY`
- `METHOD_PROMOTION_REVIEW_INPUT_DESCRIPTION` (null-monitor scoped)
- `FUTURE_EVIDENCE_PACKET_INPUT_DESCRIPTION`

### Prohibited outputs

- `CAUSAL_LIFT_CLAIM`
- `BUSINESS_LIFT_CLAIM`
- `CONFIDENCE_INTERVAL_CLAIM`
- `P_VALUE_CLAIM`
- `STATISTICAL_SIGNIFICANCE_CLAIM`
- `STATISTICAL_POWER_CLAIM`
- `ROI_CLAIM` / `ROAS_CLAIM`
- `DECISION_RECOMMENDATION`
- `PRODUCTION_READOUT`
- `CATALOG_UNBLOCK_NOTICE`
- `METHOD_PROMOTION_NOTICE`
- `PRODUCTION_COMPATIBILITY_NOTICE`
- `UNCERTAINTY_APPROVAL_NOTICE`

---

## 5. Evidence packet object

Conceptual object: **`SCMJackknifeNullMonitorPromotionEvidencePacket`**

| Field | Description |
|-------|-------------|
| `packet_id` | Unique packet identifier |
| `instrument_identity` | Exact canonical identity (§3) |
| `estimator_family` | `scm` |
| `inference_family` | `jackknife` |
| `geometry` | `single_cell` |
| `estimand` | `delta_mu` |
| `surface` | `null_monitor` |
| `interval_semantics_or_null_monitor_semantics` | `not_applicable_for_null_monitor` |
| `allowed_surfaces` | Tuple from §4 allowed list |
| `prohibited_surfaces` | Tuple from §4 prohibited list |
| `claim_authorization_boundary_ref` | Claim boundary refs (§11); no SCM-specific boundary audit yet — packet blocked until defined |
| `instrument_identity_evidence` | Identity field validation refs |
| `metric_estimand_alignment_evidence` | `delta_mu`/KPI compatibility refs |
| `null_control_false_positive_evidence` | Null-control / no-effect false-positive refs |
| `jackknife_stability_evidence` | Delete-one / leverage stability refs |
| `directional_error_evidence` | Sign/direction behavior under diagnostic scenarios |
| `donor_pool_diagnostics_evidence` | Donor pool adequacy, exclusion, support diagnostics |
| `pre_period_fit_diagnostics_evidence` | Pre-period fit, balance, residual diagnostics |
| `sensitivity_evidence` | Donor set, window, treated unit, specification sensitivity |
| `readout_compatibility_evidence` | Null-monitor diagnostic packet compatibility only |
| `catalog_classification_ref` | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` |
| `framework_generalization_ref` | `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` |
| `blockers` | Active blocker codes |
| `missing_evidence` | Missing required category codes |
| `warnings` | Advisory flags (e.g. catalog alias mismatch) |
| `packet_readiness_status` | Status from §7 |
| `promotion_review_eligibility_status` | Status from §8 |
| `lineage` | Provenance manifest |
| `created_from_artifacts` | Source artifact IDs used to assemble packet |

---

## 6. Required evidence categories

| Evidence category | Required? | Minimum contents | Source owner / artifact | Missing status |
|-------------------|----------:|------------------|-------------------------|----------------|
| instrument_identity | yes | Exact identity fields (§3); canonical vs catalog alias reconciliation | `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` | `BLOCKED_MISSING_INSTRUMENT_IDENTITY` |
| claim_boundary | yes | Allowed/prohibited null-monitor surfaces; no causal/CI/significance inheritance | `CLAIM_AUTHORIZATION_RUNTIME_001` · catalog null-monitor boundaries · future SCM null-monitor claim-boundary audit | `BLOCKED_MISSING_CLAIM_BOUNDARY` |
| metric_estimand_alignment | yes | `delta_mu` and KPI compatibility for SCM single-cell path | `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` · estimand/readout semantics | `BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT` |
| null_control_false_positive | yes | Null-control behavior under no effect | `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` (when complete) · SCM null-calibration validation refs | `BLOCKED_MISSING_NULL_CONTROL_EVIDENCE` |
| jackknife_stability | yes | Delete-one / leverage stability under null-monitor scenarios | SCM jackknife diagnostics · `SCM_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001` chain | `BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE` |
| directional_error | yes | Sign/direction behavior under diagnostic scenarios | Validation evidence refs · `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` | `BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE` |
| donor_pool_diagnostics | yes | Donor pool adequacy, donor exclusion, support diagnostics | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` (SCM JK gaps) · SCM diagnostics refs | `BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS` |
| pre_period_fit_diagnostics | yes | Pre-period fit, balance, residual diagnostics | SCM diagnostics refs | `BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS` |
| sensitivity | yes | Sensitivity to donor set, window, treated unit, specification | SCM sensitivity plans · validation evidence refs | `BLOCKED_MISSING_SENSITIVITY_EVIDENCE` |
| readout_compatibility | yes | Can emit null-monitor diagnostic packet only | `TRUSTED_READOUT_REPORT_CONTRACT_001` · `TRUSTED_READOUT_REPORT_RUNTIME_001` · framework refs | `BLOCKED_MISSING_READOUT_COMPATIBILITY` |
| production_compatibility | no | Future only | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_*` | `NOT_REQUIRED_FOR_NULL_MONITOR_PACKET` |

**SCM-specific categories (beyond TBRRidge pilot):** `jackknife_stability`, `donor_pool_diagnostics`, `pre_period_fit_diagnostics`, null-monitor scope violation checks.

---

## 7. Packet readiness statuses

| Status | Meaning |
|--------|---------|
| `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` | All required evidence categories present with source refs |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | Some diagnostic evidence present; packet incomplete for review input |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | One or more required categories missing |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | Null-monitor claim boundary not established |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | Packet identity does not match exact instrument |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | Requested surface not in allowed null-monitor list |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | Evidence references wrong inference family (e.g. placebo, bootstrap) |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | Evidence references wrong geometry |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | Evidence references wrong point estimand |
| `PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION` | Packet requests causal lift, CI, significance, production, or promotion surfaces |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | Production compatibility incorrectly required for null-monitor packet |
| `PACKET_NOT_REQUESTED` | No packet assembly requested |

**Canonical missing-evidence status:** `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE`

---

## 8. Promotion review eligibility

| Status | Meaning |
|--------|---------|
| `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT` | Packet ready as null-monitor promotion review input only |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | Required evidence categories incomplete |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | Instrument identity mismatch |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | Null-monitor claim boundary not established |
| `NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION` | Packet exceeds null-monitor scope |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | Null-monitor packet cannot enter production review |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | Packet does not authorize catalog unblock |
| `NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW` | Null-monitor packet cannot enter causal-lift claim review |

**Rule:** Eligibility as null-monitor review input does **not** mean SCM promotion, SCM+Jackknife promotion, catalog unblock, production compatibility, or claim authorization.

---

## 9. Evidence completeness rules

1. Required evidence must have explicit source artifact references — no silent pass.
2. Missing evidence must produce a blocker in `blockers` / `missing_evidence`, not implicit approval.
3. Null-control evidence cannot substitute for donor-pool diagnostics.
4. Donor-pool diagnostics cannot substitute for pre-period fit diagnostics.
5. Pre-period fit diagnostics cannot substitute for false-positive evidence.
6. Jackknife stability cannot substitute for directional-error evidence.
7. Readout compatibility cannot substitute for method validity evidence.
8. Lane B spend/ROI readiness cannot satisfy SCM method validity.
9. TBRRidge pilot evidence cannot satisfy SCM evidence categories.
10. `SCM_PLACEBO_GOVERNED_SEMANTICS_001` cannot automatically authorize SCM jackknife null-monitor unless explicitly referenced for this exact instrument identity.
11. Diagnostic-only evidence cannot authorize production surfaces.
12. Catalog alias presence does not substitute for canonical identity validation.

---

## 10. Relationship to generalized framework

This artifact applies `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` to a **second instrument family** (SCM × Jackknife), proving the framework is not TBRRidge-specific.

**Reuses from generalized framework:**

- Exact instrument identity schema
- Evidence packet shape and field families
- Readiness / eligibility status semantics
- Non-authorization boundaries
- Claim / catalog / production separation
- Contract → runtime artifact pairing pattern

**Extends framework with SCM / null-monitor-specific evidence categories:**

- Donor pool diagnostics
- Pre-period fit diagnostics
- Jackknife stability (delete-one / leverage)
- Null-monitor scope violation detection

TBRRidge pilot runtimes remain the reference implementation; this contract does not retroactively genericize them.

---

## 11. Relationship to claim authorization

- `CLAIM_AUTHORIZATION_RUNTIME_001` remains the sole package-level claim owner.
- This contract does **not** modify claim authorization.
- Null-monitor eligibility does **not** authorize causal lift, business lift, CI, p-value, significance, statistical power, ROI/ROAS, or decision claims.
- SCM placebo governed semantics (`SCM_PLACEBO_GOVERNED_SEMANTICS_001`) govern placebo inference only; they do not extend to jackknife null-monitor without instrument-specific boundary evidence.

---

## 12. Relationship to catalog and production

- Catalog remains blocked/restricted per `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` unless a separate catalog governance artifact changes tier.
- SCM UnitJackKnife is RESTRICTED_REVIEW (RANK_3), null-monitor only — not promotion-candidate for lift/production.
- Production compatibility is out of scope for this packet.
- Null-monitor review is **not** production review.

---

## 13. Relationship to Lane B and MIP

- Lane B spend/ROI readiness (`GEOX_*` chain) is **orthogonal** to SCM method validity.
- Lane B artifacts may inform readout compatibility only; they cannot substitute for SCM null-monitor evidence categories.
- MIP DecisionSurface / RecommendationContract / TrustReport cannot be bypassed.
- No MIP decisioning is implemented by this contract.
- Readout compatibility may inform packet assembly but cannot replace method evidence.

---

## 14. Future runtime plan

**Recommended future artifact:** `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Consume explicit evidence refs | Runtime |
| Enforce exact canonical identity | Runtime |
| Validate required SCM null-monitor evidence categories (§6) | Runtime |
| Emit blockers and missing evidence | Runtime |
| Assemble `SCMJackknifeNullMonitorPromotionEvidencePacket` | Runtime |
| Detect null-monitor scope violations | Runtime |
| Pass packet to future SCM promotion review decision runtime | Runtime |
| Promote SCM / SCM+Jackknife | **No** |
| Authorize claims | **No** |
| Unblock catalog | **No** |

**Downstream (not this artifact):** `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_REVIEW_DECISION_CONTRACT_001` · `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_REVIEW_DECISION_RUNTIME_001`

---

## 15. Non-goals

- No runtime implemented
- No SCM promotion
- No SCM+Jackknife promotion
- No method or instrument promotion
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical claim authorization
- No confidence interval claim authorization
- No p-value / significance / statistical power claim authorization
- No causal/business lift claim authorization
- No ROI/ROAS claim authorization
- No decision recommendation authorization
- No estimator/inference implementation
- No new validation experiments run
- No Lane B runtime changes
- No MIP decisioning
- No TrustReport bypass

---

## 16. Validation results

- Governance tests: `tests/governance/test_scm_jackknife_null_monitor_promotion_evidence_packet_contract_001.py`
- Summary JSON: `docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001_summary.json`
- Safety grep: forbidden capability flags must remain `false`
- Capability grep: contract completion flags must be `true`
