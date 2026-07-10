# METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001` |
| **Artifact type** | `method_promotion_generic_runtime_contract` |
| **Lane** | Lane A — Method / instrument promotion framework generic runtime contract |
| **Status** | `completed` |
| **Scope** | `generic_runtime_contract_docs_only_no_runtime_no_promotion` |
| **Final verdict** | `generic_runtime_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_RUNTIME_001` |

**Depends on:**

- `METHOD_PROMOTION_GENERIC_CONTRACTS_001`
- `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

---

## 2. Why this artifact exists

`METHOD_PROMOTION_GENERIC_CONTRACTS_001` defined shared vocabulary for instrument identity, evidence packets, review decisions, boundary statuses, and allowed/prohibited actions. The next step is to define how a **future generic runtime** would adapt instrument-specific packet and decision outputs into generic summaries for dashboards, audits, governance views, and MIP-facing rollups.

Without this contract, dashboards, MIP registry views, and governance summaries would depend on TBRRidge-specific or SCM-specific class names and status labels. That creates coupling and copy-paste drift as new instruments are added.

The future generic runtime is an **adapter/summarizer only**. Instrument-specific packet and decision runtimes remain the source of truth. This artifact defines contract only; no runtime, no dataclasses, no modification of existing TBRRidge or SCM runtimes.

---

## 3. Runtime design principle

**Instrument-specific packet and decision runtimes remain the source of truth.**

The generic runtime **may:**

- Summarize instrument-specific outputs
- Normalize names to generic vocabulary
- Map instrument-specific statuses to generic statuses (preserving source status)
- Preserve blockers, missing evidence, warnings, and lineage
- Produce audit/dashboard/MIP-facing summaries

The generic runtime **must not:**

- Recompute packet readiness
- Recompute review decisions
- Override instrument-specific blockers
- Inspect raw evidence quality
- Run estimators or inference
- Promote methods or instruments
- Authorize claims
- Unblock catalog
- Approve production compatibility
- Bypass MIP, TrustReport, or claim authorization

---

## 4. Future generic runtime entry points

Conceptual future API only (no implementation):

```python
adapt_method_promotion_packet_to_generic_summary(
    packet: instrument_specific_packet | dict,
    profile: MethodPromotionInstrumentAdapterProfile,
    *,
    lineage: dict | None = None,
) -> MethodPromotionEvidencePacketSummary

adapt_method_promotion_decision_to_generic_summary(
    decision: instrument_specific_decision | dict,
    profile: MethodPromotionInstrumentAdapterProfile,
    *,
    lineage: dict | None = None,
) -> MethodPromotionReviewDecisionSummary

build_method_promotion_governance_summary(
    packet_summary: MethodPromotionEvidencePacketSummary | None,
    decision_summary: MethodPromotionReviewDecisionSummary | None,
    profile: MethodPromotionInstrumentAdapterProfile,
    *,
    lineage: dict | None = None,
) -> MethodPromotionGovernanceSummary
```

**Input:** instrument-specific packet/decision object or dict, adapter profile, lineage/context.

**Output:** `MethodPromotionEvidencePacketSummary`, `MethodPromotionReviewDecisionSummary`, `MethodPromotionGovernanceSummary`.

---

## 5. Generic output: MethodPromotionEvidencePacketSummary

| Field | Description |
|-------|-------------|
| `summary_id` | Stable summary identifier |
| `source_packet_ref` | Source packet ID |
| `source_artifact_id` | Instrument-specific packet artifact |
| `source_runtime_id` | Instrument-specific packet runtime |
| `instrument_identity` | Canonical identity |
| `aliases` | Preserved aliases |
| `generic_packet_readiness_status` | Mapped generic readiness |
| `instrument_specific_packet_readiness_status` | Original readiness (preserved) |
| `generic_review_eligibility_status` | Mapped generic eligibility |
| `instrument_specific_review_eligibility_status` | Original eligibility (preserved) |
| `required_evidence_categories` | Required categories |
| `optional_evidence_categories` | Optional categories |
| `evidence_category_count` | Count of categories present |
| `missing_evidence` | Preserved missing categories |
| `blockers` | Preserved blockers (+ adapter blockers if any) |
| `warnings` | Preserved warnings |
| `allowed_surfaces` | Allowed surfaces |
| `prohibited_surfaces` | Prohibited surfaces |
| `boundary_statuses` | Boundary status dict |
| `lineage` | Merged lineage |
| `created_from_artifacts` | Contributing artifacts |

**Rules:**

- Generic status is mapped from instrument-specific status; source status must be preserved
- Missing evidence and blockers must not be dropped
- Alias cannot replace canonical identity
- No evidence quality scoring

---

## 6. Generic output: MethodPromotionReviewDecisionSummary

| Field | Description |
|-------|-------------|
| `summary_id` | Stable summary identifier |
| `source_decision_ref` | Source decision ID |
| `source_artifact_id` | Instrument-specific decision artifact |
| `source_runtime_id` | Instrument-specific decision runtime |
| `instrument_identity` | Canonical identity |
| `aliases` | Preserved aliases |
| `generic_decision_status` | Mapped generic decision status |
| `instrument_specific_decision_status` | Original decision status (preserved) |
| `decision_scope` | Scope label (e.g. `restricted_review`, `null_monitor`) |
| `decision_surface` | Requested surface |
| `evidence_summary` | Non-scoring evidence metadata |
| `missing_evidence` | Preserved from source |
| `blockers` | Preserved from source |
| `required_followups` | Required followups |
| `allowed_next_actions` | Allowed actions |
| `prohibited_next_actions` | Prohibited actions (preserved or expanded) |
| `boundary_statuses` | Boundary status dict |
| `warnings` | Preserved warnings |
| `lineage` | Merged lineage |
| `created_from_artifacts` | Contributing artifacts |

**Rules:**

- Positive instrument-specific decision maps to generic `APPROVE_REVIEW_CONTINUATION` only with explicit `decision_scope`
- Generic approval never means promotion, claims, catalog unblock, or production authorization
- All fixed non-authorization boundary statuses must be preserved
- Prohibited actions must be preserved or expanded, never weakened

---

## 7. Generic output: MethodPromotionGovernanceSummary

| Field | Description |
|-------|-------------|
| `governance_summary_id` | Stable governance rollup ID |
| `instrument_identity` | Canonical identity |
| `aliases` | Preserved aliases |
| `packet_summary_ref` | Reference to packet summary |
| `decision_summary_ref` | Reference to decision summary |
| `current_framework_stage` | Stage in promotion framework chain |
| `current_review_state` | Mapped generic review state |
| `next_allowed_actions` | Allowed actions from decision summary |
| `blocked_actions` | Prohibited actions |
| `claim_authorization_status` | From boundary statuses |
| `catalog_status` | From boundary statuses |
| `production_compatibility_status` | From boundary statuses |
| `method_promotion_status` | From boundary statuses |
| `instrument_promotion_status` | From boundary statuses |
| `mip_decisioning_status` | Not authorized by adapter |
| `trust_report_bypass_status` | Not bypassed |
| `unresolved_blockers` | Union of packet/decision/adapter blockers |
| `unresolved_missing_evidence` | Preserved missing evidence |
| `lineage` | Merged lineage |
| `created_from_artifacts` | Contributing artifacts |

**Purpose:** Provide a governance/audit/MIP-facing rollup without changing source-of-truth decisions.

---

## 8. Adapter profile contract

**Conceptual object:** `MethodPromotionInstrumentAdapterProfile`

| Field | Description |
|-------|-------------|
| `profile_id` | Stable profile identifier |
| `instrument_identity` | Canonical identity this profile serves |
| `aliases` | Known aliases |
| `source_packet_type` | Instrument-specific packet type name |
| `source_decision_type` | Instrument-specific decision type name |
| `packet_status_mapping` | Instrument → generic packet readiness map |
| `eligibility_status_mapping` | Instrument → generic eligibility map |
| `decision_status_mapping` | Instrument → generic decision status map |
| `boundary_status_mapping` | Field name normalization map |
| `required_field_mapping` | Required source field → generic field map |
| `allowed_surface_mapping` | Surface normalization |
| `prohibited_action_mapping` | Action name normalization |
| `source_of_truth_runtime_ids` | Authoritative runtime artifact IDs |
| `notes` | Profile notes |

**Rules:**

- Adapter profile maps names only; cannot change decision semantics
- Adapter profile cannot authorize missing fields
- Missing required source fields must generate adapter blockers

---

## 9. Required adapter blockers

Stable blocker names:

- `GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET`
- `GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_DECISION`
- `GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY`
- `GENERIC_ADAPTER_BLOCKED_UNMAPPED_PACKET_STATUS`
- `GENERIC_ADAPTER_BLOCKED_UNMAPPED_ELIGIBILITY_STATUS`
- `GENERIC_ADAPTER_BLOCKED_UNMAPPED_DECISION_STATUS`
- `GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS`
- `GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`
- `GENERIC_ADAPTER_BLOCKED_PROHIBITED_ACTION_WEAKENED`
- `GENERIC_ADAPTER_BLOCKED_SOURCE_OF_TRUTH_MISMATCH`

---

## 10. Generic status mapping requirements

**TBRRidge packet:**

| Instrument-specific | Generic |
|---------------------|---------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |

**SCM packet:**

| Instrument-specific | Generic |
|---------------------|---------|
| `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | `PACKET_BLOCKED_CROSS_ESTIMAND` |

**TBRRidge decision:**

| Instrument-specific | Generic |
|---------------------|---------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` with `decision_scope=restricted_review` |

**SCM decision:**

| Instrument-specific | Generic |
|---------------------|---------|
| `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` with `decision_scope=null_monitor` |

---

## 11. Boundary preservation requirements

Future generic runtime must preserve:

- `claim_authorization_status`
- `catalog_status`
- `production_compatibility_status`
- `method_promotion_status`
- `instrument_promotion_status`
- `scope_status` / `null_monitor_scope_status` / restricted-review scope when available
- Prohibited actions list

If any boundary field is missing from source:

- `boundary_status_incomplete = true`
- Adapter blocker: `GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS`

---

## 12. Source-of-truth rules

- Instrument-specific runtime output is authoritative for readiness and decision
- Generic adapter cannot repair failed decisions
- Generic adapter cannot convert `REQUEST_ADDITIONAL_EVIDENCE` into approval
- Generic adapter cannot convert null-monitor approval into restricted-review approval
- Generic adapter cannot convert restricted-review approval into production approval
- Generic adapter cannot use Lane B spend/ROI to satisfy method evidence

---

## 13. MIP-facing summary boundary

Generic summaries may be useful for MIP display, registry, and routing, but:

- MIP DecisionSurface remains separate
- TrustReport remains separate
- RecommendationContract remains separate
- Generic promotion summary cannot authorize business actions
- Generic promotion summary cannot serve as ROI/readout readiness

---

## 14. Future runtime validation requirements

A future `METHOD_PROMOTION_GENERIC_RUNTIME_001` must test:

- TBRRidge packet adaptation
- TBRRidge decision adaptation
- SCM packet adaptation
- SCM decision adaptation
- Canonical identity preserved
- Alias not substituted
- Unmapped status blocks
- Missing boundary status blocks
- Prohibited actions not weakened
- Missing evidence/blockers preserved
- No raw evidence scoring
- No claim/catalog/production authorization

---

## 15. Recommended next step

**`METHOD_PROMOTION_GENERIC_RUNTIME_001`** — only after this contract is accepted.

The runtime should be a thin adapter using hard-coded profiles for the two completed applications first:

- TBRRidge restricted-review
- SCM null-monitor

Do not support AugSynth/DID until their instrument-specific packet/decision chains exist.

---

## 16. Alternative next artifacts

| Alternative | Why not now |
|-------------|-------------|
| `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` | Defer until generic runtime adapter exists |
| `DID_BOOTSTRAP_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` | Defer; assumptions/claim-boundary burden |
| Catalog unblock lane | Premature |
| Production compatibility lane | Premature |

---

## 17. Non-goals

This artifact does **not**:

- Implement runtime, generic runtime, generic dataclasses, or adapter profiles
- Promote any method, instrument, TBRRidge, SCM, AugSynth, or DID
- Unblock catalog or authorize production compatibility
- Change claim authorization or authorize statistical/causal/business/ROI claims
- Authorize decision recommendations or production readout
- Implement estimator/inference behavior
- Run new validation experiments or score raw evidence quality
- Modify Lane B runtime, implement MIP decisioning, or bypass TrustReport

---

## 18. Validation results

- Contract doc: `docs/track_d/METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001.md`
- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_generic_runtime_contract_001.py`

Capability flags (all true): `generic_runtime_contract_defined`, `future_runtime_entry_points_defined`, `packet_summary_contract_defined`, `decision_summary_contract_defined`, `adapter_profile_contract_defined`, `source_of_truth_rules_defined`, `mip_facing_summary_boundary_defined`.
