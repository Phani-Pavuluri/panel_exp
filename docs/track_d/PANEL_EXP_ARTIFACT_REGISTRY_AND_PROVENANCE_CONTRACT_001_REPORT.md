# PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` |
| **Artifact type** | `panel_exp_artifact_registry_and_provenance_contract` |
| **Status** | `completed` |
| **Base commit** | `b811a2f` (Define panel exp agent run packet contract) |
| **Contract scope** | `artifact_registry_provenance_contract_no_runtime` |
| **Final verdict** | `panel_exp_artifact_registry_provenance_contract_defined_no_runtime_authorization` |

This artifact is a **contract/specification document only**. It defines durable artifact identity, metadata, provenance, validation/governance state, and downstream-use policy for future panel_exp planner reports, agent outputs, diagnostic outputs, validation reports, failure packets, and downstream-readable artifacts. **No runtime registry storage, agents, orchestration, profilers, planners, estimators, design algorithms, inference logic, p-values, confidence intervals, production recommendations, budget optimization, selector/router behavior, MMM ingestion, LLM decisioning, or downstream integrations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | Per-run execution envelopes and artifact reference hooks |
| `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Planning intent and intake routing |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data modes, input references, profiler reports |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Tool-first/agent-second framework |
| `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | Cross-cutting contract sequencing |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |

---

## 3. Reason for artifact registry/provenance contract

Future planner agents and deterministic diagnostics will produce many reports, summaries, failure packets, and validation outputs. Without a durable registry and provenance contract, artifacts may exist without stable identity, lose source workflow and input references, lose agent run linkage, lose validation and governance status, be reused beyond allowed scope, or be cited by LLMs without traceable evidence.

This contract defines how panel_exp identifies, tracks, validates, governs, and references artifacts **before** any runtime registry, profiler, or agent orchestration.

---

## 4. Registry-first provenance principle

**Core principles:**

- **Registry-first, provenance-always** — durable artifacts must be indexed with full lineage
- **No artifact id, no durable artifact claim** — unregistered files are not durable artifacts
- **No provenance, no downstream use** — routing requires typed provenance
- **No validation status, no validation claim** — validation claims require `PanelExpArtifactValidationState`
- **No governance status, no claim boundary** — claim ceilings require `PanelExpArtifactGovernanceState`
- **No `allowed_downstream_use`, no downstream routing** — routing requires `PanelExpArtifactDownstreamUsePolicy`
- **Diagnostic artifact does not imply production authorization**
- **Sample schema artifact does not imply final feasibility**
- **Ballpark artifact does not imply final feasibility**

---

## 5. Artifact lifecycle

```
source workflow + inputs
  → artifact generated (draft/generated)
  → registry entry created (PanelExpArtifactRegistryEntry)
  → provenance attached (PanelExpArtifactProvenance)
  → validation run (PanelExpArtifactValidationState)
  → governance evaluation (PanelExpArtifactGovernanceState)
  → downstream-use policy assigned (PanelExpArtifactDownstreamUsePolicy)
  → lifecycle transition (validated | validation_failed | blocked | superseded | expired | revoked | archived)
  → downstream consumers query registry (PanelExpArtifactRegistryQuery)
```

**Lifecycle rules:**

- Only **validated** artifacts may support deterministic downstream diagnostics
- **Blocked** artifacts may be referenced only to explain why claims are blocked
- **Superseded** artifacts must point to replacement artifact
- **Expired/revoked** artifacts cannot support new recommendations
- **Draft/generated** artifacts cannot support final claims

---

## 6. Artifact identity requirements

### `PanelExpArtifactIdentity`

| Field | Purpose |
|-------|---------|
| `artifact_id` | Stable unique identifier |
| `artifact_type` | Taxonomy type (see §14) |
| `schema_version` | Contract/schema version |
| `artifact_family` | Logical family (profiler, feasibility, agent, audit) |
| `artifact_name` | Human-readable name |
| `artifact_path_or_uri` | Storage location |
| `content_hash_or_version` | Integrity/version fingerprint |

No `artifact_id` → no durable artifact claim. Identity must be stable across registry lookups.

---

## 7. Artifact metadata requirements

### `PanelExpArtifactRegistryEntry`

| Field | Purpose |
|-------|---------|
| `artifact_id` | Stable unique identifier |
| `artifact_type` | Taxonomy type |
| `artifact_name` | Human-readable name |
| `artifact_path_or_uri` | Storage location |
| `created_at` | Creation timestamp |
| `created_by_workflow` | Producing workflow |
| `created_by_run_id` | Producing agent/diagnostic run |
| `source_input_references` | Typed input refs |
| `source_artifact_references` | Upstream artifact refs |
| `content_hash_or_version` | Integrity/version fingerprint |
| `lifecycle_state` | Current lifecycle state |
| `validation_state` | Validation snapshot |
| `governance_state` | Governance snapshot |
| `allowed_downstream_use` | Permitted downstream targets |
| `blocked_downstream_use` | Forbidden downstream targets |
| `claim_boundaries` | Claim ceiling definitions |
| `retention_policy` | Retention/archival policy |
| `notes` | Non-authoritative notes |

Every durable artifact must have a registry entry. Registry entries are the authoritative index for artifact existence and metadata.

---

## 8. Provenance link requirements

### `PanelExpArtifactProvenance`

| Field | Purpose |
|-------|---------|
| `source_workflow` | Workflow that produced artifact |
| `source_run_id` | Run identifier |
| `source_agent_name_or_tool` | Agent or deterministic tool |
| `source_input_references` | Input lineage |
| `source_artifact_references` | Upstream artifact lineage |
| `transformation_summary` | What changed from inputs |
| `created_at` | Provenance timestamp |
| `created_by` | Actor (agent, tool, harness) |

No provenance → no downstream use. Provenance must chain to `PanelExpAgentRunManifest` when produced by agents (per `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001`).

### `PanelExpArtifactVersionReference`

Links artifact versions and supersession chains. Superseded artifacts must reference replacement via version reference.

---

## 9. Source workflow and source run requirements

### `PanelExpArtifactSourceWorkflow`

| Field | Purpose |
|-------|---------|
| `workflow_id` | Stable workflow identifier |
| `workflow_name` | Human-readable workflow name |
| `workflow_version` | Workflow contract version |
| `workflow_stage` | Stage (intake, profiler, feasibility, design, inference) |
| `workflow_family` | Family (planner, diagnostic, validation, audit) |

### `PanelExpArtifactSourceRunReference`

| Field | Purpose |
|-------|---------|
| `run_id` | Run identifier |
| `packet_id` | Source input packet (if agent run) |
| `agent_name` | Agent identifier |
| `agent_role` | Agent role |
| `run_status` | completed, failed, blocked |
| `run_started_at` | Start timestamp |
| `run_completed_at` | End timestamp |

No `source_run_id` → artifact cannot claim agent/diagnostic execution. Agent runs must link to `PanelExpAgentRunManifest`.

---

## 10. Input data / fixture / payload reference requirements

### `PanelExpArtifactInputReference`

| Field | Purpose |
|-------|---------|
| `input_reference_id` | Stable input ref ID |
| `input_type` | upload, fixture, ballpark, sample_schema |
| `input_mode` | full_panel, sample_schema, ballpark |
| `input_path_or_uri` | Data location |
| `input_hash_or_version` | Integrity fingerprint |
| `time_window` | Temporal scope |
| `region_market` | Geographic scope |
| `geo_unit_type` | Unit granularity |
| `kpi` | KPI identifier |
| `spend_scope` | Spend channel scope |
| `data_contract_version` | Data contract version |

**Input mode rules:**

- `sample_schema` cannot support final design feasibility claims
- `ballpark` cannot support final design feasibility claims
- `full_panel` required for final feasibility evidence (subject to validation/governance)

Artifacts must not lose input references. Input mode must propagate to governance and downstream-use policy.

---

## 11. Validation status requirements

### `PanelExpArtifactValidationState`

| Field | Purpose |
|-------|---------|
| `validation_status` | pass, warn, block, not_run |
| `validation_report_id` | Linked validation report |
| `checks_run` | Check inventory |
| `checks_passed` | Passed checks |
| `checks_failed` | Failed checks |
| `warnings` | Non-blocking warnings |
| `blocking_errors` | Hard blockers |
| `validated_at` | Validation timestamp |

No validation status → no validation claim. Only `validation_status=pass` with `lifecycle_state=validated` supports deterministic downstream diagnostics.

---

## 12. Governance status requirements

### `PanelExpArtifactGovernanceState`

| Field | Purpose |
|-------|---------|
| `governance_status` | See §15 governance statuses |
| `authorization_flags` | Auth snapshot (all false unless release gate) |
| `claim_level` | diagnostic, provisional, internal_planning, review, approved |
| `review_required` | Human review gate |
| `approval_required` | Approval gate |
| `expires_at` | Expiration timestamp |
| `revocation_reason` | Reason if revoked |

**Governance rules:**

- `approved_for_specific_downstream_use` is **not** production authorization unless corresponding release-gate artifact authorizes it
- `diagnostic_only` cannot be upgraded by LLM explanation
- `provisional` cannot support final design feasibility
- `needs_more_data` cannot support p-values/CIs
- `blocked` cannot route downstream except as blocked evidence

No governance status → no claim boundary.

---

## 13. Allowed/blocked downstream use requirements

### `PanelExpArtifactDownstreamUsePolicy`

| Field | Purpose |
|-------|---------|
| `allowed_downstream_use` | Permitted downstream targets |
| `blocked_downstream_use` | Forbidden downstream targets |
| `allowed_audiences` | Permitted consumer audiences |
| `blocked_audiences` | Forbidden audiences |
| `allowed_claims` | Permitted claim types |
| `blocked_claims` | Forbidden claim types |
| `routing_constraints` | Additional routing rules |

**Downstream use targets:**

`internal_planning`, `diagnostic_explanation`, `portfolio_feasibility`, `design_generation`, `spend_feasibility`, `inference_planning`, `model_fallback_routing`, `mmm_prior_candidate`, `calibration_signal_candidate`, `trust_report_candidate`, `production_readout`, `production_p_value`, `production_confidence_interval`, `production_decisioning`, `budget_optimization`, `live_api`, `scheduler`

**Routing rules:**

- No artifact may route to `production_readout` / `production_p_value` / `production_confidence_interval` / `production_decisioning` unless explicit release-gate artifact authorizes it
- MMM/calibration/trust candidates remain candidates unless later contracts authorize ingestion
- Blocked artifacts may route only to `diagnostic_explanation` as blocked evidence
- Expired/revoked artifacts cannot support new recommendations

No `allowed_downstream_use` → no downstream routing.

### `PanelExpArtifactClaimBoundary`

Defines claim ceilings per artifact: supported claims, blocked claims, evidence requirements, release-gate dependencies.

---

## 14. Artifact type taxonomy

| Type | Description |
|------|-------------|
| `planning_intent` | User/planner stated goals |
| `data_profile_report` | KPI/spend data profile |
| `column_mapping_report` | Column mapping diagnostic |
| `geo_time_coverage_report` | Geo/time coverage diagnostic |
| `unit_eligibility_report` | Unit eligibility diagnostic |
| `geo_unit_feasibility_report` | Geo-unit feasibility |
| `portfolio_feasibility_report` | Portfolio-level feasibility |
| `tier_assignment_plan` | Test tier assignment |
| `spend_contrast_feasibility_report` | Spend contrast feasibility |
| `cell_spend_plan` | Cell spend allocation |
| `candidate_design_set` | Candidate designs |
| `design_feasibility_scores` | Design feasibility scores |
| `design_based_inference_plan` | Inference plan |
| `inference_validity_diagnostics` | Inference validity checks |
| `model_fallback_recommendation` | Model fallback suggestion |
| `agent_run_manifest` | Agent run manifest |
| `agent_validation_report` | Agent validation report |
| `agent_failure_packet` | Agent failure packet |
| `agent_resolution_plan` | Agent resolution plan |
| `claim_boundary_report` | Claim boundary report |
| `golden_path_result` | Golden-path test result |
| `audit_report` | Audit report |
| `governance_summary` | Governance summary |

---

## 15. Artifact state model

### Lifecycle states

`draft`, `generated`, `validated`, `validation_failed`, `blocked`, `superseded`, `expired`, `revoked`, `archived`

### Governance statuses

`diagnostic_only`, `provisional`, `needs_more_data`, `blocked`, `validated_for_internal_planning`, `eligible_for_review`, `approved_for_specific_downstream_use`, `revoked`, `expired`

### Registry query contracts

**`PanelExpArtifactRegistryQuery`** — query by `artifact_id`, `artifact_type`, `lifecycle_state`, `governance_status`, `source_run_id`, `input_reference_id`, `allowed_downstream_use`.

**`PanelExpArtifactRegistryLookupResult`** — returns matching `PanelExpArtifactRegistryEntry` records, lookup status, and claim-boundary summary. Lookup does not authorize runtime routing.

---

## 16. Retention/version/hash requirements

- Every artifact must record `content_hash_or_version` at creation and on material change
- Superseded artifacts must reference replacement via `PanelExpArtifactVersionReference`
- Retention policy must be explicit (`retention_policy` field)
- Hash/version mismatch between registry entry and stored content invalidates artifact for downstream use
- Version references must be immutable once archived

---

## 17. LLM answerability boundaries

| Claim | Required source |
|-------|-----------------|
| Artifact exists as durable | `PanelExpArtifactRegistryEntry` |
| Provenance / lineage | `PanelExpArtifactProvenance` |
| Validation passed | `PanelExpArtifactValidationState` |
| Allowed downstream use | `PanelExpArtifactDownstreamUsePolicy` |
| Blocked/revoked/expired status | Registry metadata |

**LLM may not:**

- Treat unregistered files as durable artifacts
- Claim provenance without `PanelExpArtifactProvenance`
- Claim validation passed without `PanelExpArtifactValidationState`
- Claim allowed downstream use without `PanelExpArtifactDownstreamUsePolicy`
- Upgrade diagnostic/provisional artifacts to production authorization
- Route artifacts downstream beyond `allowed_downstream_use`
- Treat sample-schema or ballpark artifacts as final feasibility evidence

---

## 18. Relation to agent run packet contract

`PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` defines per-run execution envelopes: input packets, run manifests, artifact references, validation/failure/resolution packets. This contract defines **durable artifact registry and provenance** after or alongside those runs.

Agent `PanelExpAgentArtifactReference` hooks become full `PanelExpArtifactRegistryEntry` records with provenance, validation, governance, and downstream-use policy. Run manifests supply `source_run_id`; artifact references supply initial identity hooks.

---

## 19. Relation to golden-path acceptance tests

`PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` will define deterministic end-to-end regression scenarios that rely on registered artifacts. Golden paths must assert: registry entry completeness, provenance chains, validation/governance state, lifecycle transitions, blocked/expired handling, and LLM grounding over registry-backed artifacts.

---

## 20. Relation to LLM grounding contract

`LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` will define user-facing explanation rules over registry-backed artifacts. This contract supplies the registry index and provenance metadata that grounding rules consume. LLM explanations must cite registry entries, not freeform file paths.

---

## 21. Fixture/scenario test requirements

Minimum 21 scenarios: registry entry fields, artifact identity fields, provenance fields, input reference fields, source workflow/run fields, validation/governance/downstream-use fields, lifecycle states, governance statuses, artifact type taxonomy, no-artifact-id/no-provenance principles, sample-schema/ballpark cannot final feasibility, diagnostic cannot production authorization, blocked/expired/revoked routing rules, LLM answerability boundaries, revised roadmap sequence.

---

## 22. Governance boundaries

All authorization flags remain **false**:

- Panel exp artifact registry, artifact registry, artifact provenance, artifact downstream routing runtime
- Agent orchestration, golden path, LLM report grounding, LLM artifact interpretation runtime
- Production design, readout, p-values, CIs, selector/router, downstream integrations
- MMM ingestion, calibration signal, trust report, budget optimization, live API, scheduler

This contract defines metadata contracts only. No runtime registry storage or routing was authorized.

---

## 23. Revised roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 9 | `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | ✅ |
| 10 | `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | ✅ This contract |
| 11 | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Next |
| 12+ | Profiler and planner implementation lanes | After cross-cutting contracts |

Also requires future: `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`.

---

## 24. Recommended next artifact

`PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` — deterministic end-to-end regression scenarios over registry-backed artifacts before profiler runtime.

---

## 25. Final verdict

**`panel_exp_artifact_registry_provenance_contract_defined_no_runtime_authorization`**

Registry-first/provenance-always principles, fourteen typed contracts, artifact type taxonomy, lifecycle and governance state models, downstream-use policy, retention/version/hash requirements, LLM answerability boundaries, and relations to agent run packet, golden-path, and LLM grounding contracts defined. All runtime authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001_summary.json` |
| Harness | `panel_exp/validation/panel_exp_artifact_registry_and_provenance_contract_001.py` |
