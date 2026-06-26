# PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` |
| **Artifact type** | `panel_exp_agent_run_packet_contract` |
| **Status** | `completed` |
| **Base commit** | `f42322d` (Define experiment portfolio intake contract) |
| **Contract scope** | `agent_run_packet_contract_no_runtime` |
| **Final verdict** | `panel_exp_agent_run_packet_contract_defined_no_runtime_authorization` |

This artifact is a **contract/specification document only**. It defines typed agent run packets for future panel_exp planner agents. **No runtime agents, orchestration, profilers, planners, estimators, or production recommendations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Planning intent and intake routing |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data modes and profiler reports |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Tool-first/agent-second framework |
| `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | Cross-cutting contract sequencing |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |

---

## 3. Reason for agent run packet contract

Future planner agents will coordinate multi-step diagnostics and LLM explanations. Without typed run packets, agents may invent inputs, lose evidence references, claim diagnostics ran when they did not, hide failures, or recommend production design/p-values/CIs without release-gate evidence.

This contract defines the execution envelope before any agent runtime or demo.

---

## 4. Tool-first / packet-first principle

**Core principles:**

- **Packet-first, agent-second** — no `PanelExpAgentInputPacket`, no agent run
- **Tool-first, explanation-second** — diagnostics before LLM summaries
- **No run manifest, no claim that an agent executed**
- **No artifact reference, no claim that a report was produced**
- **No validation report, no claim that outputs passed checks**
- **No failure packet, no hidden failure**
- **No release-gate evidence, no production recommendation**

---

## 5. Agent packet lifecycle

```
user/planner request
  → PanelExpAgentInputPacket
  → allowed/blocked action evaluation
  → tool/report execution (if authorized)
  → PanelExpAgentRunManifest
  → PanelExpAgentArtifactReference (every output)
  → PanelExpAgentValidationReport
  → PanelExpAgentFailurePacket (if needed)
  → PanelExpAgentResolutionPlan (if recoverable)
  → LLM explanation grounded in packet/manifest/report references
```

---

## 6. Typed input packet requirements

### `PanelExpAgentInputPacket`

| Field | Purpose |
|-------|---------|
| `packet_id` | Unique packet identifier |
| `created_at` | Timestamp |
| `request_source` | UI, API, notebook, CLI |
| `user_intent_reference` | Link to user-stated goal |
| `planning_intent_reference` | `ExperimentPortfolioPlanningIntent` ref |
| `input_data_reference` | Data upload or ballpark ref |
| `input_mode` | full_panel, sample_schema, ballpark |
| `requested_workflow` | intake, profiler, feasibility, etc. |
| `requested_claim_level` | Tier/claim intent |
| `allowed_actions` | Pre-evaluated allowed set |
| `blocked_actions` | Pre-evaluated blocked set |
| `governance_context` | Release-gate and auth state |
| `prior_artifact_references` | Upstream artifact refs |
| `missing_required_inputs` | Gaps before execution |

---

## 7. Run manifest requirements

### `PanelExpAgentRunManifest`

| Field | Purpose |
|-------|---------|
| `run_id` | Unique run identifier |
| `packet_id` | Source input packet |
| `agent_name` | Agent identifier |
| `agent_role` | intake, profiler, feasibility, etc. |
| `started_at` / `completed_at` | Timestamps |
| `status` | running, completed, failed, blocked |
| `tools_requested` | Tools asked to run |
| `tools_executed` | Tools actually run |
| `tools_blocked` | Tools blocked with reason |
| `input_artifacts` | Input artifact refs |
| `output_artifacts` | Output artifact refs |
| `validation_reports` | Validation report refs |
| `failure_packets` | Failure packet refs |
| `claim_boundaries` | Claim ceiling for this run |
| `next_recommended_action` | Safe next step |
| `governance_status` | Auth/gate state |

---

## 8. Artifact reference requirements

### `PanelExpAgentArtifactReference`

| Field | Purpose |
|-------|---------|
| `artifact_id` | Artifact identifier |
| `artifact_type` | Report, contract, summary JSON |
| `artifact_path_or_uri` | Location |
| `source_workflow` | Workflow that produced it |
| `source_run_id` | Producing run |
| `input_reference` | Input artifact ref |
| `created_at` | Timestamp |
| `content_hash_or_version` | Integrity check |
| `governance_status` | Auth state |
| `allowed_downstream_use` | Permitted uses |
| `blocked_downstream_use` | Forbidden uses |

Every agent output must have an artifact reference. No reference → no claim the report exists.

---

## 9. Validation report requirements

### `PanelExpAgentValidationReport`

| Field | Purpose |
|-------|---------|
| `validation_id` | Unique validation ID |
| `run_id` | Source run |
| `artifact_id` | Validated artifact |
| `checks_run` | Check inventory |
| `checks_passed` | Passed checks |
| `checks_failed` | Failed checks |
| `warnings` | Non-blocking warnings |
| `blocking_errors` | Hard blockers |
| `authorization_flags` | Auth state snapshot |
| `claim_boundary_status` | Claim ceiling result |
| `final_validation_status` | pass, warn, block |

No validation report → no claim validation passed.

---

## 10. Failure packet requirements

### `PanelExpAgentFailurePacket`

| Field | Purpose |
|-------|---------|
| `failure_id` | Unique failure ID |
| `run_id` | Source run |
| `failed_step` | Step that failed |
| `failure_type` | input, tool, validation, governance |
| `failure_reason` | Human-readable reason |
| `blocking` | Whether run is blocked |
| `recoverable` | Whether retry possible |
| `safe_retry_allowed` | Safe retry flag |
| `unsafe_retry_reasons` | Why retry is unsafe |
| `required_user_or_system_action` | What is needed |
| `affected_claims` | Claims invalidated |

Failures must not be hidden. No failure packet → treated as incomplete run.

---

## 11. Resolution plan requirements

### `PanelExpAgentResolutionPlan`

| Field | Purpose |
|-------|---------|
| `resolution_plan_id` | Unique plan ID |
| `failure_id` | Source failure |
| `recommended_resolution` | Suggested fix |
| `required_inputs` | Inputs needed to retry |
| `allowed_retry_scope` | What may be retried |
| `blocked_retry_scope` | What must not be retried |
| `requires_human_review` | Human gate flag |
| `next_safe_action` | Safe next step |

LLM retry suggestions must cite resolution plan, not invent recovery paths.

---

## 12. Allowed action / blocked action requirements

### `PanelExpAllowedAction` (examples)

`read_artifact`, `summarize_report`, `request_missing_input`, `run_diagnostic`, `generate_candidate_report`, `write_metadata_artifact`, `update_governance_doc`, `recommend_provisional_next_step`

### `PanelExpBlockedAction` (examples)

`authorize_production_design`, `authorize_p_value`, `authorize_confidence_interval`, `override_blocked_status`, `modify_source_data`, `execute_budget_optimization`, `send_to_mmm`, `execute_live_api`, `schedule_experiment`, `select_final_estimator_without_diagnostics`

Actions evaluated before execution. Blocked actions must not run silently.

---

## 13. Evidence reference requirements

### `PanelExpEvidenceReference`

Links agent runs to typed diagnostic reports (`DataProfileReport`, `PortfolioFeasibilityReport`, etc.). Must include report type, artifact ref, claim level supported, and release-gate dependency. Evidence refs are required before any claim about diagnostic results.

---

## 14. Provenance hooks

Each packet/manifest/artifact reference must include:

- `source_run_id` chain
- `content_hash_or_version`
- `governance_status`
- `allowed_downstream_use` / `blocked_downstream_use`

Full durable provenance indexing deferred to `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001`. This contract defines per-run hooks only.

---

## 15. LLM answerability boundaries

| Claim | Required source |
|-------|-----------------|
| Agent ran | `PanelExpAgentRunManifest` |
| Report exists | `PanelExpAgentArtifactReference` |
| Validation passed | `PanelExpAgentValidationReport` |
| Failure occurred | `PanelExpAgentFailurePacket` |
| Retry suggested | `PanelExpAgentResolutionPlan` |

**LLM may not:** claim agent ran without manifest; claim report exists without artifact ref; hide failures; convert provisional outputs to production recommendations; override blocked actions.

---

## 16. Agent action boundaries

Agents may coordinate diagnostics and produce candidate reports within allowed actions. Agents may not authorize production design, p-values, CIs, budget optimization, MMM ingestion, live API, scheduling, or final estimator selection without diagnostics and release gates.

---

## 17. Failure and retry boundaries

Recoverable failures may produce resolution plans with explicit `allowed_retry_scope`. Unsafe retries (e.g., retry after data corruption, override blocked status) are forbidden. `requires_human_review` gates ambiguous recoveries.

---

## 18. Downstream routing boundaries

Run manifests may recommend `next_recommended_action` (e.g., route to profiler, request ballpark inputs). Routing is provisional. Downstream agents must consume typed packets, not freeform LLM state.

---

## 19. Relation to artifact registry/provenance contract

This contract defines **per-run execution envelopes**. `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` will define durable artifact indexing, lineage, and governance-status persistence across runs.

---

## 20. Relation to golden-path acceptance tests

`PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` will define deterministic E2E scenarios verifying packet lifecycle, manifest completeness, failure visibility, and LLM grounding. This contract defines what golden paths must assert.

---

## 21. Fixture/scenario test requirements

Minimum 21 scenarios: input packet fields, run manifest fields, artifact reference fields, validation/failure/resolution fields, allowed/blocked actions, packet-first principles, no-manifest/no-artifact-ref/no-validation claims, hidden failure blocking, production/p-value/CI/budget/MMM/live-API blocking, LLM boundaries, revised roadmap sequence.

---

## 22. Governance boundaries

All authorization flags remain **false**:

- Agent run packet, orchestration, manifest, artifact reference, validation, failure, resolution runtime
- Artifact registry, golden path, LLM report grounding runtime
- Production design, p-values, CIs, selector/router, downstream integrations

---

## 23. Revised roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 8 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | ✅ |
| 9 | `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | ✅ This contract |
| 10 | `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | Next |
| 11 | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Planned |
| 12+ | Profiler and planner implementation lanes | After cross-cutting contracts |

Also requires future: `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`.

---

## 24. Recommended next artifact

`PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` — durable artifact indexing and lineage before profiler runtime.

---

## 25. Final verdict

**`panel_exp_agent_run_packet_contract_defined_no_runtime_authorization`**

Packet-first/agent-second principles, eleven typed contracts, allowed/blocked actions, lifecycle, LLM boundaries, and provenance hooks defined. All runtime authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001_summary.json` |
| Harness | `panel_exp/validation/panel_exp_agent_run_packet_contract_001.py` |
