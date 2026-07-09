# TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` |
| **Artifact type** | `tbrridge_promotion_evidence_packet_assembly_contract` |
| **Lane** | **Lane A — Method / instrument promotion** |
| **Status** | `completed` |
| **Scope** | `evidence_packet_assembly_contract_defined_no_runtime_no_promotion` |
| **Instrument identity** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Final verdict** | `tbrridge_promotion_evidence_packet_assembly_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` |

**Depends on:**

- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`
- `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001`
- `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001`
- `ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001`
- `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `TRACK_B_ESTIMAND_REGISTRY_001`
- `INFERENCE_READOUT_SEMANTICS_001`

---

## 2. Why this contract exists

TBRRidge × KFold is the only current pursue-now / restricted-review TBRRidge lane. `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` established what this exact instrument may and may not claim: diagnostic/restricted-review evidence surfaces only — not CI, p-value, significance, causal/business lift, ROI, decision recommendation, production readout, catalog unblock, method promotion, or production compatibility.

Before method promotion review can evaluate the instrument, evidence must be assembled into a governed packet with traceable source artifacts, explicit statuses, blockers, and non-authorization. **Packet assembly is not promotion.** This contract defines the packet object, required evidence categories, readiness statuses, and eligibility rules — without implementing runtime or authorizing any claim.

---

## 3. Exact instrument identity

**Full identity:** `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `tbrridge` |
| `inference_family` | `kfold` |
| `geometry` | `single_cell` |
| `point_estimand` | `delta_mu` |
| `interval_semantics` | `diagnostic_interval` |
| `surface` | `restricted_review` |

**Promotion scope constraints:**

- No cross-inference-family promotion (e.g. cannot promote TBRRidge × Jackknife from this packet)
- No cross-geometry promotion (e.g. cannot promote multi-cell from single-cell evidence)
- No estimator-family-level promotion (TBRRidge family-wide)
- No production/global TBRRidge promotion

---

## 4. Allowed and prohibited surfaces

Reuses `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` claim surfaces.

### Allowed packet surfaces

- `DIAGNOSTIC_STATUS_SUMMARY`
- `EVIDENCE_COMPLETENESS_SUMMARY`
- `BLOCKER_SUMMARY`
- `RESTRICTED_REVIEW_READINESS_SUMMARY`
- `METHOD_PROMOTION_REVIEW_INPUT_DESCRIPTION`
- `FUTURE_EVIDENCE_PACKET_INPUT_DESCRIPTION`

### Prohibited packet surfaces

- `CONFIDENCE_INTERVAL_CLAIM`
- `P_VALUE_CLAIM`
- `STATISTICAL_SIGNIFICANCE_CLAIM`
- `STATISTICAL_POWER_CLAIM`
- `CAUSAL_LIFT_CLAIM`
- `BUSINESS_LIFT_CLAIM`
- `ROI_CLAIM`
- `DECISION_RECOMMENDATION`
- `PRODUCTION_READOUT`
- `CATALOG_UNBLOCK_NOTICE`
- `METHOD_PROMOTION_NOTICE`
- `PRODUCTION_COMPATIBILITY_NOTICE`
- `UNCERTAINTY_APPROVAL_NOTICE`

---

## 5. Evidence packet object

Conceptual object: **`TBRRidgePromotionEvidencePacket`**

| Field | Description |
|-------|-------------|
| `packet_id` | Unique packet identifier |
| `instrument_identity` | Exact identity string (§3) |
| `estimator_family` | `tbrridge` |
| `inference_family` | `kfold` |
| `geometry` | `single_cell` |
| `estimand` | `delta_mu` |
| `interval_semantics` | `diagnostic_interval` |
| `allowed_surfaces` | Tuple from §4 allowed list |
| `prohibited_surfaces` | Tuple from §4 prohibited list |
| `claim_authorization_boundary_report_ref` | Reference to boundary audit / report |
| `metric_estimand_alignment_evidence` | Metric/estimand alignment artifact refs |
| `null_control_false_positive_evidence` | Null-control false-positive evidence refs |
| `directional_error_evidence` | Directional-error evidence refs |
| `positive_control_recovery_evidence` | Positive-control recovery evidence refs |
| `sensitivity_evidence` | Sensitivity evidence refs |
| `readout_compatibility_evidence` | Restricted-review readout compatibility refs |
| `trusted_readout_compatibility_evidence` | Trusted readout packet compatibility refs |
| `classification_policy_ref` | `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` |
| `catalog_triage_ref` | `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` |
| `pairing_coverage_ref` | `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` |
| `pairing_value_ref` | `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` |
| `blockers` | Active blocker codes |
| `missing_evidence` | Missing required category codes |
| `warnings` | Advisory flags |
| `packet_readiness_status` | Status from §7 |
| `promotion_review_eligibility_status` | Status from §8 |
| `lineage` | Provenance manifest |
| `created_from_artifacts` | Source artifact IDs used to assemble packet |

---

## 6. Required evidence categories

| Evidence category | Required? | Minimum contents | Source owner / artifact | Missing status |
|-------------------|----------:|------------------|-------------------------|----------------|
| Instrument identity | yes | Exact identity fields (§3) | `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · catalog triage | `BLOCKED_MISSING_INSTRUMENT_IDENTITY` |
| Claim boundary | yes | Allowed/prohibited surfaces, boundary report | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | `BLOCKED_MISSING_CLAIM_BOUNDARY` |
| Metric/estimand alignment | yes | `delta_mu`/KPI compatibility, interval semantics | `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` · `TRACK_B_ESTIMAND_REGISTRY_001` · `INFERENCE_READOUT_SEMANTICS_001` | `BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT` |
| Null-control false-positive evidence | yes | Null/control false-positive behavior | `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` · validation sources | `BLOCKED_MISSING_NULL_CONTROL_EVIDENCE` |
| Directional-error evidence | yes | Sign/direction error behavior | `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` · validation sources | `BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE` |
| Positive-control recovery evidence | yes | Recovery under known injected effect | `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` · validation sources | `BLOCKED_MISSING_POSITIVE_CONTROL_EVIDENCE` |
| Sensitivity evidence | yes | Sensitivity to design/window/noise/spec | `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` · `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` | `BLOCKED_MISSING_SENSITIVITY_EVIDENCE` |
| Readout compatibility | yes | Can emit restricted-review diagnostic packet | `TRUSTED_READOUT_REPORT_*` · claim boundary | `BLOCKED_MISSING_READOUT_COMPATIBILITY` |
| Production compatibility | no | Future only | `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_*` | `NOT_REQUIRED_FOR_RESTRICTED_REVIEW_PACKET` |

---

## 7. Packet readiness statuses

| Status | Meaning |
|--------|---------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | All required evidence categories present with source refs |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | Some diagnostic evidence present; packet incomplete for review input |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | One or more required categories missing |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | Claim boundary report absent or invalid |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | Packet identity does not match exact instrument |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | Requested surface not in allowed list |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | Evidence references wrong inference family |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | Evidence references wrong geometry |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | Production compatibility incorrectly required for restricted-review packet |
| `PACKET_NOT_REQUESTED` | No packet assembly requested |

**Canonical missing-evidence status:** `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE`

---

## 8. Promotion review eligibility

| Status | Meaning |
|--------|---------|
| `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | Packet ready as method promotion review input (restricted-review only) |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | Required evidence categories incomplete |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | Instrument identity mismatch |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | Claim boundary not established |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | Restricted-review packet cannot enter production review |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | Packet does not authorize catalog unblock |

**Rule:** Eligibility as promotion-review input does **not** mean promotion approval, catalog unblock, or claim authorization.

---

## 9. Evidence completeness rules

1. Required evidence must have explicit source artifact references — no silent pass.
2. Missing evidence must produce a blocker in `blockers` / `missing_evidence`, not implicit approval.
3. Diagnostic-only evidence cannot authorize production surfaces.
4. Null-control evidence cannot substitute for positive-control evidence.
5. Positive-control evidence cannot substitute for false-positive evidence.
6. Readout compatibility cannot substitute for method validity evidence.
7. Lane B spend/ROI readiness cannot authorize method promotion.
8. Lane B final readout readiness is **orthogonal** to Lane A method promotion.

---

## 10. Relationship to Lane B

Lane B completed the minimum semantic chain: post-test spend evidence derivation, trusted readout spend integration, and efficiency metric readiness mapping contract.

Lane B artifacts may support **readout compatibility** evidence in this packet. They do **not** authorize TBRRidge promotion, catalog unblock, or ROI/ROAS claims. Lane B efficiency metric runtime is **not** required for this restricted-review packet. Spend/ROI readiness is not method-validity evidence.

---

## 11. Future runtime plan

**Recommended future artifact:** `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Collect evidence references from completed audits | Runtime |
| Validate required categories (§6) | Runtime |
| Assemble `TBRRidgePromotionEvidencePacket` | Runtime |
| Emit blockers and missing evidence | Runtime |
| Pass packet to method promotion review runtime | Runtime |
| Approve promotion | **No** |
| Authorize claims | **No** |
| Unblock catalog | **No** |

---

## 12. Non-goals

- No runtime implemented
- No method promotion
- No instrument promotion
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical claim authorization (CI, p-value, significance)
- No causal/business lift claim authorization
- No ROI/ROAS claim authorization
- No decision recommendation
- No estimator/inference implementation
- No new validation experiments run
- No Lane B runtime changes

---

## 13. Validation results

- Governance tests: `tests/governance/test_tbrridge_promotion_evidence_packet_assembly_contract_001.py`
- Summary JSON: `docs/track_d/archives/TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001_summary.json`
- Safety grep: forbidden capability flags must remain `false`
- Capability grep: contract completion flags must be `true`
