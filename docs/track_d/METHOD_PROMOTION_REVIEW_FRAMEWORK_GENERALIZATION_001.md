# METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` |
| **Artifact type** | `method_promotion_review_framework_generalization` |
| **Lane** | **Lane A — Method / instrument promotion framework** |
| **Status** | `completed` |
| **Scope** | `framework_generalization_docs_only_no_runtime_no_promotion` |
| **Pilot instrument** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Final verdict** | `method_promotion_review_framework_generalized_docs_only_no_runtime_no_promotion` |
| **Recommended next** | `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001` |

**Depends on:**

- `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001`
- `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

---

## 2. Why this generalization exists

The TBRRidge × KFold restricted-review lane (`geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`) was a **pilot**. It produced a complete governed chain: evidence packet contract/runtime, review decision contract/runtime, claim boundary audit, and fixed non-authorization semantics.

**The work should not keep deepening one TBRRidge config.** The pilot has done its job. The value is the **reusable governance pattern** — instrument identity, evidence categories, packet readiness, review decisions, blockers, and claim/catalog/production boundaries.

Future instruments should reuse this promotion framework instead of duplicating bespoke TBRRidge-only artifacts for every estimator × inference × geometry combination. Generalization prevents accidental estimator-family promotion, cross-inference inheritance, and conflation of restricted-review continuation with method promotion or catalog unblock.

---

## 3. Pilot pattern extracted

Reusable promotion review pattern (does **not** imply promotion):

```
Instrument identity
  → Claim boundary
  → Required evidence categories
  → Evidence packet contract
  → Evidence packet runtime
  → Review decision contract
  → Review decision runtime
  → Future catalog/production lanes (if separately authorized)
```

**TBRRidge pilot mapping:**

| Stage | Pilot artifact |
|-------|----------------|
| Claim boundary | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` |
| Evidence packet contract | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` |
| Evidence packet runtime | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` |
| Review decision contract | `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001` |
| Review decision runtime | `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001` |

Each future instrument instantiates this pattern with instrument-specific identity, evidence sources, claim boundary, and thresholds — not by copying TBRRidge module names.

---

## 4. Generic instrument identity schema

**Canonical identity fields:**

| Field | Description |
|-------|-------------|
| `modality` | Domain/modality (e.g. `geo`) |
| `estimator_family` | Estimator family (e.g. `tbrridge`) |
| `inference_family` | Inference family (e.g. `kfold`) |
| `geometry` | Unit/aggregation geometry (e.g. `single_cell`) |
| `point_estimand` | Point estimand (e.g. `delta_mu`) |
| `interval_semantics` | Interval semantics (e.g. `diagnostic_interval`) |
| `surface` | Review/readout surface (e.g. `restricted_review`) |

**Optional future fields:** `metric_family`, `aggregation_level`, `design_family`, `assignment_family`, `readout_surface`, `catalog_tier`, `production_compatibility_class`

**Identity rule:** Promotion is **exact-instrument scoped** unless an explicit family-level promotion review exists. No cross-inference, cross-geometry, cross-estimand, or cross-surface inheritance.

**Pilot example:** `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

---

## 5. Generic evidence category registry

### Core categories (required unless framework revision)

| Category | Purpose |
|----------|---------|
| `instrument_identity` | Exact instrument identity and classification alignment |
| `claim_boundary` | Claim authorization boundary audit/report |
| `metric_estimand_alignment` | Metric ↔ estimand alignment evidence |
| `null_control_false_positive` | Null-control false-positive evidence |
| `directional_error` | Directional-error evidence |
| `positive_control_recovery` | Positive-control recovery evidence |
| `sensitivity` | Sensitivity/regime evidence bundle |
| `readout_compatibility` | Restricted-review readout compatibility |
| `catalog_classification` | Catalog triage/classification alignment |
| `production_compatibility` | Optional/future; not required for restricted-review packet |

### Optional / extension categories

`coverage_evidence`, `method_pairing_value`, `calibration_alignment`, `robustness_to_window_choice`, `robustness_to_geo_set`, `placebo_or_null_distribution`, `uncertainty_semantics_review`, `operational_runtime_compatibility`, `MIP_handoff_compatibility`

**Rule:** Extension categories **cannot replace** required core categories unless a future framework revision explicitly allows it. Lane B spend/ROI readiness cannot substitute for method-validity core categories.

---

## 6. Generic packet readiness statuses

| Status | Meaning |
|--------|---------|
| `PACKET_READY_FOR_REVIEW_INPUT` | Sufficient evidence for review input |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | Partial evidence; diagnostic only |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | Missing required categories |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | Claim boundary missing |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | Wrong instrument identity |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | Unsupported surface requested |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | Cross-inference promotion attempted |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | Cross-geometry promotion attempted |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | Cross-estimand promotion attempted |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | Production compatibility required but absent |
| `PACKET_NOT_REQUESTED` | No packet assembly requested |

**TBRRidge pilot alias:** `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` ≡ `PACKET_READY_FOR_REVIEW_INPUT` for restricted-review scope.

---

## 7. Generic review decision statuses

| Status | Meaning |
|--------|---------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | Restricted-review lane may continue only |
| `REQUEST_ADDITIONAL_EVIDENCE` | Evidence packet incomplete |
| `REJECT_FOR_METHOD_VALIDITY` | Method-validity evidence insufficient |
| `REJECT_FOR_IDENTITY_MISMATCH` | Wrong instrument/scope |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Claim boundary missing/violated |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | Surface outside restricted-review |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Not exact inference family |
| `REJECT_FOR_CROSS_GEOMETRY` | Not exact geometry |
| `REJECT_FOR_CROSS_ESTIMAND` | Not exact estimand |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Production lane required |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Catalog governance lane required |
| `NO_DECISION_PACKET_NOT_READY` | Assemble valid packet first |

**Important:** `APPROVE_RESTRICTED_REVIEW_CONTINUATION` is **not** method promotion, instrument promotion, catalog unblock, production compatibility, or claim authorization.

---

## 8. Decision mapping framework

| Packet / request state | Decision status | Authorized next action |
|------------------------|-----------------|----------------------|
| Ready + eligible + `restricted_review` | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | Continue restricted-review governance only |
| Missing required evidence | `REQUEST_ADDITIONAL_EVIDENCE` | Collect missing evidence refs |
| Identity mismatch | `REJECT_FOR_IDENTITY_MISMATCH` | Rebuild packet with exact identity |
| Claim boundary missing/violated | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Repair claim boundary evidence |
| Unsupported surface | `REJECT_FOR_UNSUPPORTED_SURFACE` | Restrict scope or separate review |
| Cross-inference family | `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Create separate instrument lane |
| Cross-geometry | `REJECT_FOR_CROSS_GEOMETRY` | Create separate instrument lane |
| Cross-estimand | `REJECT_FOR_CROSS_ESTIMAND` | Create separate instrument lane |
| Production request | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Open production compatibility lane |
| Catalog unblock request | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Open catalog governance lane |
| Packet not ready | `NO_DECISION_PACKET_NOT_READY` | Assemble valid evidence packet first |

**Precedence:** production/catalog defer → identity mismatch → cross-family/geometry/estimand → claim boundary → method validity → missing evidence → unsupported surface → approval.

---

## 9. Claim / catalog / production boundaries

- **`CLAIM_AUTHORIZATION_RUNTIME_001`** remains sole package-level claim owner
- Promotion review does **not** authorize claims
- Catalog unblock requires separate catalog governance artifact
- Production compatibility requires separate production compatibility artifact
- MIP DecisionSurface / TrustReport / RecommendationContract cannot be bypassed
- Readout compatibility does **not** imply method validity
- Lane B spend/ROI readiness does **not** imply method promotion

**Fixed non-authorization statuses (all instruments):**

- `claim_authorization_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `catalog_status = NOT_UNBLOCKED_BY_THIS_DECISION`
- `production_compatibility_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `method_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`
- `instrument_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`

---

## 10. What is reusable vs instrument-specific

### Reusable

- Identity schema and exact-scope rules
- Evidence packet shape (`MethodPromotionEvidencePacket` future)
- Readiness status families
- Review decision status families
- Blocker semantics and missing-evidence rules
- Allowed/prohibited surface pattern
- Non-authorization status fields
- Lineage/warnings preservation
- Contract → runtime artifact pairing pattern

### Instrument-specific

- Exact identity string
- Required evidence thresholds and source artifacts
- Method-specific diagnostics (leakage, placebo, coverage, etc.)
- Instrument-specific claim boundary audit
- Production compatibility requirements
- Catalog tiering decision
- Method validity thresholds and blocker naming

---

## 11. Candidate next instruments

Listed for future lanes only — **no implementation commitment:**

| Candidate identity | Notes |
|--------------------|-------|
| `geo.tbrridge.brb.single_cell.delta_mu.diagnostic_interval.restricted_review` | BRB variance path; separate evidence packet required |
| `geo.tbrridge.placebo.single_cell.delta_mu.diagnostic_interval.restricted_review` | Placebo inference family; own lane |
| `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` | AugSynth JK; governed-but-not-promoted pairing |
| `geo.scm.jackknife.single_cell.delta_mu.null_monitor` | SCM unit jackknife null monitor |
| `geo.did.bootstrap.single_cell.delta_mu.diagnostic_interval.restricted_review` | DID bootstrap; blocked until remediation |

Each requires its own evidence packet and decision review unless a future **family-level** promotion is explicitly authorized.

---

## 12. Future generic runtime plan

**Recommended future artifact:** `METHOD_PROMOTION_REVIEW_FRAMEWORK_RUNTIME_CONTRACT_001`

Define generic typed contracts (not implemented now):

- `MethodPromotionInstrumentIdentity`
- `MethodPromotionEvidenceReference`
- `MethodPromotionEvidencePacket`
- `MethodPromotionReviewDecision`
- `MethodPromotionReadinessStatus`
- `MethodPromotionDecisionStatus`

TBRRidge pilot runtimes remain the reference implementation; a generic runtime would parameterize identity, category registry, and mapping rules — not replace pilot artifacts retroactively.

---

## 13. Recommended next step

**Recommended next artifact:** `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`

**Purpose:** Choose the next instrument to run through the generalized framework based on evidence availability, risk, value, and roadmap priority — not by gut feeling.

Do not immediately deepen TBRRidge KFold or duplicate pilot artifacts for another instrument without this selection audit.

---

## 14. Non-goals

- No runtime implemented
- No generic runtime implemented
- No method or instrument promoted
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical/CI/p-value/significance claim authorization
- No causal/business lift or ROI/ROAS claim authorization
- No decision recommendation authorization
- No estimator/inference implementation
- No new validation experiments
- No Lane B runtime changes
- No MIP decisioning
- No TrustReport bypass
- No modification of TBRRidge pilot runtimes

---

## 15. Validation results

- Framework doc: `docs/track_d/METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001.md`
- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_review_framework_generalization_001.py`

Capability flags (all true): `framework_generalization_completed`, `pilot_pattern_extracted`, `generic_instrument_identity_schema_defined`, `generic_evidence_category_registry_defined`, `generic_packet_readiness_statuses_defined`, `generic_review_decision_statuses_defined`, `reusable_vs_instrument_specific_split_defined`.

Forbidden flags (all false): runtime/generic_runtime implemented, promotion, catalog unblock, claim authorization changes, statistical claims, estimator/inference implementation, Lane B changes, MIP decisioning, TrustReport bypass.
