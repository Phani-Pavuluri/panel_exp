# Artifact Redundancy / Reuse / Coherence Audit — Preflight Template

**Template ID:** `ARTIFACT_REDUNDANCY_REUSE_AUDIT_TEMPLATE_001`  
**Checkpoint:** `LANE_C_REDUNDANCY_REUSE_PREFLIGHT_TEMPLATE_CHECKPOINT_001` — Lane C hygiene documentation  
**Note:** Docs-only checkpoint; no code/runtime/governance changes. Future cross-cutting artifacts should use this preflight before implementation.  
**Purpose:** Required preflight before creating any new contract, runtime, schema, adapter, audit, or ADR in GeoX / `panel_exp`.  
**Rule:** Force a reuse verdict before building. Do not create new owners when existing owners exist.

---

## When to run this audit

Run before any proposed artifact involving:

- reporting, trust, claim authorization
- data ingestion, spend, ROI/ROAS
- MIP handoff, user prompting, data-source resolution
- cross-cutting platform contracts or runtimes

---

## Known lanes (classify every proposal)

### Lane A — Method / instrument promotion

**Purpose:** Validate exact method instruments (especially TBRRidge × KFold restricted-review).

**Known artifacts:** `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` · `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` · `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` · `ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001` · `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` · parked next: `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001`

### Lane B — Final trusted readout / spend / ROI readiness

**Purpose:** Final test readouts report increment, lift, cost-per, ROI/ROAS readiness, and claim status without duplicating report or claim owners.

**Known artifacts:** `FINAL_TEST_RESULTS_EXISTING_ARTIFACT_REUSE_AUDIT_001` · `GEOX_READOUT_DATAFLOW_AND_SPEND_EXTRACTION_PROCESS_AUDIT_001` · `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` · next: `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`

**Known owners to reuse:**

- `TRUSTED_READOUT_REPORT_CONTRACT_001` / `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`
- `estimator_readout_adapter_001.py`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `GEO_KPI_SPEND_DATA_PROFILER_001`
- `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`
- `TRACK_B_ESTIMAND_REGISTRY_001`
- `INFERENCE_READOUT_SEMANTICS_001`

### Lane C — Architecture reuse / redundancy governance

**Purpose:** Prevent duplicate contracts, runtimes, claim logic, schemas; clarify package vs MIP ownership; block over-engineering.

---

## Ownership principles (encode in every audit)

| Principle | Rule |
|-----------|------|
| **Reuse before create** | Search for existing owner; extend or adapt before new artifact |
| **Package vs MIP** | MIP: user input, prompting, data-source resolution, explanation. panel_exp: deterministic validation, extraction, claim/report assembly |
| **Contract vs runtime vs adapter** | Contract defines semantics; runtime implements; adapter bridges existing modules — never skip contract when dataflow unclear |
| **Claim delegation** | `CLAIM_AUTHORIZATION_RUNTIME_001` owns claim status; never duplicate |
| **Report delegation** | `TRUSTED_READOUT_REPORT_*` owns final report assembly; never create parallel final-results module |
| **Lane check** | Every artifact must map to Lane A, B, C, cross-lane, MIP-level, or blocked |

---

## Cursor prompt (copy and fill)

```
You are working in the GeoX / panel_exp package.

Task: run a lightweight redundancy / reuse / coherence audit before creating any new artifact.

Artifact name:
<PROPOSED_ARTIFACT_NAME>_REDUNDANCY_REUSE_AUDIT

Proposed new artifact / task:
<PASTE THE PROPOSED ARTIFACT OR TASK HERE>

Do not implement anything.
Do not create a production module.
Do not create a new owner unless the audit proves no owner exists.
Do not modify roadmap/governance files.
Do not git pull/push/commit.

Create only:
docs/track_d/<PROPOSED_ARTIFACT_NAME>_REDUNDANCY_REUSE_AUDIT.md

Search broadly with project-specific KEY_TERM_1/2/3 plus:
contract|schema|runtime|adapter|readout|trust|claim|governance|summary.json

Required sections: 1–13 per ARTIFACT_REDUNDANCY_REUSE_AUDIT_TEMPLATE_001.md
```

---

## Required audit sections (checklist)

1. Proposed artifact (name, problem, type, consumers, inputs, outputs)
2. Lane classification (exactly one primary lane + rationale)
3. Search terms used
4. Existing related artifacts table
5. Existing owner check (package vs MIP, partial owners)
6. Ownership map (responsibilities × owners × conflicts)
7. Duplicate-risk scan (classified risks)
8. Coherence scan (roadmap, registry, lanes, claim/trust boundaries)
9. Reuse decision (exactly one allowed verdict)
10. Recommended next step (exactly one action)
11. If proceeding, required follow-up changes
12. Explicit non-goals
13. Final verdict block (verdict, lane, rationale, next action, safe to proceed)

---

## Allowed reuse verdicts

- `REUSE_EXISTING_ARTIFACT`
- `EXTEND_EXISTING_ARTIFACT`
- `ADD_THIN_ADAPTER_ONLY`
- `ADD_NEW_ARTIFACT_BECAUSE_NO_OWNER_EXISTS`
- `RENAME_OR_MERGE_WITH_EXISTING_ARTIFACT`
- `BLOCKED_PENDING_OWNER_DECISION`
- `DO_NOT_BUILD`
- `SPLIT_INTO_LANES_FIRST`
- `MOVE_TO_MIP_LAYER`
- `MOVE_TO_PANEL_EXP_LAYER`

---

## Allowed safe-to-proceed answers

- `YES`
- `NO`
- `YES_WITH_REUSE_ONLY`
- `BLOCKED_PENDING_OWNER_DECISION`
- `SPLIT_FIRST`

---

## Example filled audits

- `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001_REDUNDANCY_REUSE_AUDIT.md` — Lane B contract preflight (retrospective validation)
