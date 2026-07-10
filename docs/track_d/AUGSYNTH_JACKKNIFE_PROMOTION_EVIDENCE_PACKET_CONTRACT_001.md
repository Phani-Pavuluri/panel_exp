# AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` |
| **Artifact type** | `augsynth_jackknife_promotion_evidence_packet_contract` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | `completed` |
| **Scope** | `evidence_packet_contract_docs_only_no_runtime_no_promotion` |
| **Instrument identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Final verdict** | `augsynth_jackknife_evidence_packet_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` |

**Depends on:**

- `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001`
- `METHOD_PROMOTION_GENERIC_RUNTIME_001`
- `METHOD_PROMOTION_GENERIC_CONTRACTS_001`
- `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001`
- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

**Framework references (precedent only, no evidence substitution):** TBRRidge restricted-review pilot · SCM Jackknife null-monitor application

---

## 2. Why this contract exists

`METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001` approved only a **narrowed restricted-review path** (`PROCEED_WITH_NARROWED_AUGSYNTH_SCOPE`) for AugSynth Jackknife. The audit found enough framework precedent to define an evidence packet contract, but **not** enough evidence to promote AugSynth, unblock catalog, authorize production compatibility, or authorize claims.

This contract defines the **evidence packet shape**, required evidence categories, readiness/eligibility statuses, blockers, warnings, and fixed non-authorization boundaries for:

`geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**This contract is packet-only.** It does not implement packet assembly runtime, review decision contract/runtime, generic adapter profile, method promotion, instrument promotion, or claim authorization. It does **not** add AugSynth to `METHOD_PROMOTION_GENERIC_RUNTIME_001`. It prepares the next artifact (`AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`) to assemble evidence references only.

AugSynth receives **stricter boundaries** than TBRRidge because diagnostic interval semantics, augmentation components, and SCM-bridge evidence are easier to overstate as production uncertainty or causal validity.

---

## 3. Exact instrument identity

**Canonical identity:** `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `augsynth` |
| `inference_family` | `jackknife` |
| `geometry` | `single_cell` |
| `point_estimand` | `delta_mu` |
| `interval_semantics` | `diagnostic_interval` |
| `surface` | `restricted_review` |

**Alias-related / non-substitutable identity:** `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` — registered in `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` as RANK_1 `RESEARCH_SANDBOX`. Related but **not equivalent**.

**Identity rules (non-negotiable):**

- Canonical identity is **required** on every packet input and output
- Alias/research identity may be recorded in `aliases` or `lineage` only
- Alias **cannot** satisfy canonical identity
- `research_only` surface **cannot** substitute `restricted_review`
- `research_interval` interval semantics **cannot** substitute `diagnostic_interval`
- No cross-inference-family promotion (e.g. cannot promote AugSynth × Conformal from this packet)
- No cross-geometry promotion
- No cross-estimand promotion
- No estimator-family-level AugSynth promotion
- SCM evidence cannot satisfy AugSynth required categories
- TBRRidge evidence cannot satisfy AugSynth required categories
- Lane B spend/ROI evidence cannot satisfy method-validity categories

---

## 4. Packet purpose

**`AugSynthJackknifePromotionEvidencePacket`** is a restricted-review packet input/output contract.

### May support

- Review readiness assessment for restricted-review surface only
- Diagnostic evidence organization by category
- Missing evidence tracking
- Blocker tracking
- Lineage preservation
- Future review-decision input (separate artifact)

### Does not support

- Method promotion
- Instrument promotion
- Catalog unblock
- Production compatibility authorization
- Claim authorization (statistical, causal, business, ROI, recommendation)
- Production readout
- Business decision recommendation
- MIP DecisionSurface approval
- TrustReport bypass

---

## 5. Evidence reference object

Conceptual object: **`AugSynthJackknifeEvidenceReference`**

| Field | Description |
|-------|-------------|
| `evidence_id` | Stable reference identifier within packet |
| `evidence_category` | Required category key (§7) |
| `artifact_ref` | Path or URI to source artifact (non-empty to satisfy category) |
| `instrument_identity` | Must match canonical identity when category is `instrument_identity` |
| `evidence_surface` | Surface the evidence supports (must be restricted-review scoped) |
| `source_family` | e.g. `augsynth`, `scm_bridge`, `diagnostic` |
| `source_lane` | e.g. `lane_a_method_promotion`, `track_d_validation` |
| `source_artifact_type` | e.g. `audit`, `validation_report`, `diagnostic_runtime` |
| `notes` | Human-readable context |
| `metadata` | Opaque key-value; no quality scoring |

**Rules:**

- `artifact_ref` must be non-empty to count toward category satisfaction
- Evidence category must match a required or declared optional category
- Evidence reference **does not certify** evidence quality or method validity
- SCM/TBRRidge artifacts may appear only as `related-pattern support` in notes — **not** as satisfying AugSynth required categories
- Lane B spend/ROI/trusted-readout spend evidence cannot satisfy method-validity categories
- References to `D5_INST_AUGSYNTH_*`, `D5_DIAG_SCM_AUGSYNTH_*`, fidelity audits are acceptable **AugSynth-family** sources when category-aligned

---

## 6. Packet input/output contract

### Input: `AugSynthJackknifePromotionEvidencePacketInput`

| Field | Description |
|-------|-------------|
| `packet_id` | Unique packet identifier |
| `instrument_identity` | Exact canonical identity (§3) |
| `requested_surface` | Default `restricted_review` |
| `evidence_references` | List of `AugSynthJackknifeEvidenceReference` |
| `required_evidence_categories` | Override only to subset of §7 core+AugSynth required; cannot omit required categories |
| `optional_evidence_categories` | Subset of §7 optional categories |
| `lineage` | Provenance manifest |
| `warnings` | Input-side advisory flags |
| `created_from_artifacts` | Source artifact IDs |

### Output: `AugSynthJackknifePromotionEvidencePacket`

| Field | Description |
|-------|-------------|
| `packet_id` | From input |
| `instrument_identity` | Canonical identity (forced if valid input) |
| `aliases` | Related non-canonical identities from lineage only |
| `evidence_by_category` | Map category → list of reference dicts |
| `missing_evidence` | Required categories without valid refs |
| `blockers` | Active blocker codes (§12) |
| `warnings` | Advisory flags (§13) |
| `packet_readiness_status` | From §9 |
| `promotion_review_eligibility_status` | From §10 |
| `allowed_surfaces` | From §11 |
| `prohibited_surfaces` | From §11 |
| `boundary_statuses` | Fixed non-authorization statuses (§14) |
| `lineage` | Merged provenance |
| `created_from_artifacts` | Source + contract artifact ID |

---

## 7. Required evidence categories

### Core required (framework-shared)

| Category | Required |
|----------|----------|
| `instrument_identity` | yes |
| `claim_boundary` | yes |
| `metric_estimand_alignment` | yes |
| `null_control_false_positive` | yes |
| `directional_error` | yes |
| `positive_control_recovery` | yes |
| `sensitivity` | yes |
| `readout_compatibility` | yes |

### AugSynth-specific required

| Category | Required |
|----------|----------|
| `donor_pool_diagnostics` | yes |
| `pre_period_fit_diagnostics` | yes |
| `augmentation_component_diagnostics` | yes |
| `synthetic_weight_diagnostics` | yes |
| `regularization_or_model_component_diagnostics` | yes |
| `jackknife_stability` | yes |
| `method_disagreement_or_scm_bridge` | yes |
| `support_overlap_or_donor_hull_stress` | yes |

### Optional / future (not required for packet-ready)

- `placebo_evidence`
- `conformal_evidence`
- `bootstrap_evidence`
- `production_compatibility`
- `catalog_governance`
- `external_method_review`

---

## 8. Evidence category semantics

| Category | Purpose | Acceptable reference type | Does not authorize |
|----------|---------|---------------------------|-------------------|
| `instrument_identity` | Exact canonical identity validation | Classification policy, catalog triage, identity audit refs | Catalog tier upgrade |
| `claim_boundary` | Restricted-review allowed/prohibited surfaces | Future AugSynth claim-boundary audit; catalog research-only boundaries | Any claim type |
| `metric_estimand_alignment` | `delta_mu` compatibility for AugSynth JK path | Estimand alignment audit, readout compatibility refs | Causal lift |
| `null_control_false_positive` | Null-control behavior under no effect | D5 validation, ASCM OC refs | Significance / FPR approval |
| `directional_error` | Sign behavior under diagnostic scenarios | Validation evidence refs | Directional claim |
| `positive_control_recovery` | Weak-fit / injection recovery diagnostics | ASCM-002/003 OC refs | Method promotion |
| `sensitivity` | Specification / donor / window sensitivity | Sensitivity plans, diagnostic grids | Robustness approval |
| `readout_compatibility` | Restricted-review diagnostic packet compatibility only | Trusted readout contract refs (surface-scoped) | Production readout |
| `donor_pool_diagnostics` | Donor availability/support | D5-DIAG-SCM-AUGSYNTH, hull diagnostics | Causal validity |
| `pre_period_fit_diagnostics` | Pre-period fit evidence | SCM-bridge fit diagnostics (AugSynth-owned refs) | Production CI |
| `augmentation_component_diagnostics` | Augmented component sanity | ASCM fidelity, component diagnostic refs | Model promotion |
| `synthetic_weight_diagnostics` | Weight concentration / effective donors | D4/D5 weight metadata refs | Catalog unblock |
| `regularization_or_model_component_diagnostics` | Ridge/CVXPY component stability | Fidelity audit, outcome-model sensitivity | Claim authorization |
| `jackknife_stability` | Diagnostic interval stability | JK calibration refs (diagnostic only) | Production uncertainty |
| `method_disagreement_or_scm_bridge` | AugSynth vs SCM disagreement/bridge | ASCM-002 disagreement, scale bridge refs | SCM evidence substitution |
| `support_overlap_or_donor_hull_stress` | Extrapolation / outside-hull risk | Hull stress, outside-hull W3 refs | Approval under extrapolation |

---

## 9. Packet readiness statuses

**`AugSynthJackknifePacketReadinessStatus`:**

| Status | Meaning |
|--------|---------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | All required categories present with valid refs |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | Some diagnostic evidence; incomplete for review input |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | One or more required categories missing |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | Claim boundary category absent |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | Identity does not match canonical |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | Surface not in allowed list |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | Wrong inference family evidence |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | Wrong geometry evidence |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | Wrong estimand evidence |
| `PACKET_BLOCKED_SCOPE_VIOLATION` | Packet requests promotion/production/claim surfaces |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | Production compatibility incorrectly required |
| `PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT` | Alias used as canonical identity |
| `PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT` | Research-only identity/surface substituted |
| `PACKET_NOT_REQUESTED` | No packet assembly requested |

### Generic status mapping (`METHOD_PROMOTION_GENERIC_CONTRACTS_001`)

| AugSynth status | Generic `MethodPromotionPacketReadinessStatus` |
|-----------------|-----------------------------------------------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | `PACKET_PARTIAL_DIAGNOSTIC_ONLY` |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `PACKET_BLOCKED_UNSUPPORTED_SURFACE` |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | `PACKET_BLOCKED_CROSS_GEOMETRY` |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | `PACKET_BLOCKED_CROSS_ESTIMAND` |
| `PACKET_BLOCKED_SCOPE_VIOLATION` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` |
| `PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |
| `PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_NOT_REQUESTED` | `PACKET_NOT_REQUESTED` |

---

## 10. Promotion review eligibility statuses

**`AugSynthJackknifePromotionReviewEligibilityStatus`:**

| Status | Meaning |
|--------|---------|
| `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | Packet ready as restricted-review input only |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | Required categories incomplete |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | Canonical identity mismatch |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | Claim boundary not established |
| `NOT_ELIGIBLE_SCOPE_VIOLATION` | Exceeds restricted-review scope |
| `NOT_ELIGIBLE_ALIAS_SUBSTITUTION` | Alias substitution detected |
| `NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION` | Research-only substitution detected |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | Cannot enter production review |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | Does not authorize catalog unblock |
| `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` | Cannot enter causal/statistical claim review |

### Generic eligibility mapping

| AugSynth status | Generic `MethodPromotionReviewEligibilityStatus` |
|-----------------|--------------------------------------------------|
| `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | `NOT_ELIGIBLE_MISSING_EVIDENCE` |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `NOT_ELIGIBLE_IDENTITY_MISMATCH` |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` |
| `NOT_ELIGIBLE_SCOPE_VIOLATION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_ALIAS_SUBSTITUTION` | `NOT_ELIGIBLE_IDENTITY_MISMATCH` |
| `NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` |
| `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` | `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` |

**Rule:** Eligibility as restricted-review input does **not** mean AugSynth promotion, catalog unblock, production compatibility, or claim authorization.

---

## 11. Allowed surfaces

### Allowed

- `restricted_review`
- `diagnostic_restricted_review`
- `augsynth_restricted_review`
- `DIAGNOSTIC_STATUS_SUMMARY`
- `EVIDENCE_COMPLETENESS_SUMMARY`
- `BLOCKER_SUMMARY`
- `RESTRICTED_REVIEW_READINESS_SUMMARY`
- `METHOD_PROMOTION_REVIEW_INPUT_DESCRIPTION`
- `FUTURE_EVIDENCE_PACKET_INPUT_DESCRIPTION`

### Blocked / deferred

- `production`
- `production_readout`
- `production_compatibility`
- `catalog`
- `catalog_unblock`
- `catalog_promotion`
- `claim_authorization`
- `business_recommendation`
- `mip_decision_surface`
- `research_only_as_promotion_substitute`
- `CONFIDENCE_INTERVAL_CLAIM`
- `P_VALUE_CLAIM`
- `STATISTICAL_SIGNIFICANCE_CLAIM`
- `CAUSAL_LIFT_CLAIM`
- `BUSINESS_LIFT_CLAIM`
- `ROI_CLAIM` / `ROAS_CLAIM`
- `DECISION_RECOMMENDATION`
- `METHOD_PROMOTION_NOTICE`
- `PRODUCTION_COMPATIBILITY_NOTICE`

---

## 12. Blockers

Stable blocker names:

- `AUGSYNTH_PACKET_BLOCKED_MISSING_CANONICAL_IDENTITY`
- `AUGSYNTH_PACKET_BLOCKED_MISSING_CLAIM_BOUNDARY`
- `AUGSYNTH_PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE`
- `AUGSYNTH_PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`
- `AUGSYNTH_PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT`
- `AUGSYNTH_PACKET_BLOCKED_UNSUPPORTED_SURFACE`
- `AUGSYNTH_PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED`
- `AUGSYNTH_PACKET_BLOCKED_CATALOG_GOVERNANCE_REQUIRED`
- `AUGSYNTH_PACKET_BLOCKED_CLAIM_AUTHORIZATION_ATTEMPT`
- `AUGSYNTH_PACKET_BLOCKED_RAW_EVIDENCE_QUALITY_SCORING_ATTEMPT`
- `AUGSYNTH_PACKET_BLOCKED_GENERIC_ADAPTER_AS_SOURCE_OF_TRUTH`
- `AUGSYNTH_PACKET_BLOCKED_SCM_EVIDENCE_SUBSTITUTION`
- `AUGSYNTH_PACKET_BLOCKED_TBRRIDGE_EVIDENCE_SUBSTITUTION`
- `AUGSYNTH_PACKET_BLOCKED_LANE_B_EVIDENCE_SUBSTITUTION`

Category-level missing blockers (runtime may emit): `BLOCKED_MISSING_INSTRUMENT_IDENTITY`, `BLOCKED_MISSING_CLAIM_BOUNDARY`, `BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT`, `BLOCKED_MISSING_NULL_CONTROL_EVIDENCE`, `BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE`, `BLOCKED_MISSING_POSITIVE_CONTROL_EVIDENCE`, `BLOCKED_MISSING_SENSITIVITY_EVIDENCE`, `BLOCKED_MISSING_READOUT_COMPATIBILITY`, `BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS`, `BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS`, `BLOCKED_MISSING_AUGMENTATION_COMPONENT_DIAGNOSTICS`, `BLOCKED_MISSING_SYNTHETIC_WEIGHT_DIAGNOSTICS`, `BLOCKED_MISSING_REGULARIZATION_DIAGNOSTICS`, `BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE`, `BLOCKED_MISSING_METHOD_DISAGREEMENT_EVIDENCE`, `BLOCKED_MISSING_SUPPORT_OVERLAP_DIAGNOSTICS`

---

## 13. Warnings

- `AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI`
- `AUGSYNTH_WARNING_RESTRICTED_REVIEW_NOT_PROMOTION`
- `AUGSYNTH_WARNING_SCM_BRIDGE_NOT_SUBSTITUTION`
- `AUGSYNTH_WARNING_TBRRIDGE_PATTERN_NOT_EVIDENCE`
- `AUGSYNTH_WARNING_OUTSIDE_HULL_EXTRAPOLATION_RISK`
- `AUGSYNTH_WARNING_AUGMENTATION_COMPONENT_NEEDS_DIAGNOSTIC_SUPPORT`
- `AUGSYNTH_WARNING_GENERIC_ADAPTER_PROFILE_NOT_AVAILABLE_YET`

---

## 14. Fixed non-authorization boundary statuses

Every packet output must include:

| Field | Fixed value |
|-------|-------------|
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_THIS_PACKET` |
| `catalog_status` | `NOT_UNBLOCKED_BY_THIS_PACKET` |
| `production_compatibility_status` | `NOT_AUTHORIZED_BY_THIS_PACKET` |
| `method_promotion_status` | `NOT_PROMOTED_BY_THIS_PACKET` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_THIS_PACKET` |
| `generic_adapter_status` | `NOT_REGISTERED_BY_THIS_PACKET` |
| `mip_decisioning_status` | `NOT_AUTHORIZED_BY_THIS_PACKET` |
| `trust_report_bypass_status` | `NOT_BYPASSED_BY_THIS_PACKET` |

---

## 15. Generic framework compatibility

| Contract object | Generic abstraction (`METHOD_PROMOTION_GENERIC_CONTRACTS_001`) |
|-----------------|----------------------------------------------------------------|
| Canonical identity | `MethodPromotionInstrumentIdentity` |
| `AugSynthJackknifeEvidenceReference` | `MethodPromotionEvidenceReference` |
| `AugSynthJackknifePromotionEvidencePacket` | `MethodPromotionEvidencePacket` |
| `AugSynthJackknifePacketReadinessStatus` | `MethodPromotionPacketReadinessStatus` (via §9 mapping) |
| `AugSynthJackknifePromotionReviewEligibilityStatus` | `MethodPromotionReviewEligibilityStatus` (via §10 mapping) |

**Rules:**

- AugSynth must **not** be added to `METHOD_PROMOTION_GENERIC_RUNTIME_001` until packet runtime **and** review decision runtime exist
- Generic runtime remains adapter/summarizer only; instrument-specific packet runtime is source of truth
- Future generic adapter profile requires completed AugSynth packet + decision chain

---

## 16. Relationships and boundaries

| Related artifact | Relationship |
|------------------|--------------|
| **TBRRidge** | Framework precedent for restricted-review packet pattern; TBRRidge evidence **cannot substitute** AugSynth categories |
| **SCM** | Related synthetic-control family; bridge/disagreement category only; SCM evidence **cannot substitute** AugSynth categories |
| **Generic runtime** | Not source-of-truth for AugSynth; no profile yet |
| **Claim authorization runtime** | Unchanged; packet does not grant claims |
| **Catalog governance** | Separate future lane; RANK_1 research sandbox unchanged |
| **Production compatibility** | Separate future lane; blocked for AugSynth |
| **Lane B spend/ROI** | Orthogonal; cannot satisfy method-validity evidence |
| **MIP** | Cannot authorize DecisionSurface or TrustReport bypass |

---

## 17. Recommended next artifact

**`AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`**

Scope:

- Implement packet assembly runtime per this contract
- Consume evidence references only
- Validate identity, category, surface, reference presence
- No raw evidence quality scoring
- No promotion or claim authorization
- No generic adapter profile yet

---

## 18. Non-goals

This contract explicitly does **not**:

- Implement runtime (packet or decision)
- Modify generic runtime or add AugSynth adapter profile
- Promote any method or instrument
- Unblock catalog or authorize production compatibility
- Change claim authorization or authorize statistical/causal/business/ROI claims
- Authorize production readout or decision recommendations
- Implement estimator/inference behavior
- Run new validation experiments
- Score raw evidence quality
- Modify Lane B runtime
- Implement MIP decisioning
- Bypass TrustReport or claim authorization

---

## 19. Validation results

- Summary JSON: `docs/track_d/archives/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001_summary.json`
- Governance tests: `tests/governance/test_augsynth_jackknife_promotion_evidence_packet_contract_001.py`
- Safety grep: no forbidden `true` flags in contract doc or summary
- Capability grep: contract definition flags `true`
