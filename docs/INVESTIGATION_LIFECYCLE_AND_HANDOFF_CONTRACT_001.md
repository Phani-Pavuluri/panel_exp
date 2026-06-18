# Investigation Lifecycle and Handoff Contract 001

**Artifact ID:** INVESTIGATION-LIFECYCLE-AND-HANDOFF-CONTRACT-001  
**Status:** Accepted  
**Authoritative registry:** [`docs/governance/OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json)

## Purpose

No unresolved finding may exist only inside a report. Every residual defect must either:

1. become a **tracked investigation** with revisit trigger and decision checkpoint, or  
2. receive an **explicit terminal disposition** recorded in the registry and artifact handoff.

Roadmap prose (`ROADMAP_V4.md`, `MIP_AUDIT_REGISTRY.md`) **references** the registry; it is not the primary source of truth.

## Status vocabulary

| Status | Meaning |
|--------|---------|
| `OPEN` | Active defect; blocks promotion paths per `blocking_policy` |
| `PLANNED` | Scheduled characterization/remediation artifact exists |
| `IN_PROGRESS` | Target artifact executing |
| `BLOCKED` | Cannot proceed without external decision |
| `DEFERRED_WITH_TRIGGER` | Explicitly deferred until concrete event |
| `RESOLVED` | Closed with `resolution_artifact` |
| `WONT_FIX` | Terminal accept/limit |
| `SUPERSEDED` | Replaced by another investigation |

`DEFERRED_WITH_TRIGGER` must name a concrete event (not “fix later”).

## Artifact handoff schema

Every validation, audit, remediation, or correction **summary JSON** must include:

```json
"investigation_handoff": {
  "follow_up_issues": ["INV-..."],
  "resolved_issues": ["INV-..."],
  "terminal_dispositions": [],
  "next_artifact": "ARTIFACT-ID"
}
```

Closure is invalid if `follow_up_issues` is non-empty and `next_artifact` is null.

## Report closure template

Every governed report must end with **Residual Issues and Handoff** containing:

- Resolved in this artifact  
- New investigations opened (or `none`)  
- Existing investigations updated  
- Deferred issues  
- Explicit exclusions  
- Revisit trigger  
- Required decision checkpoint  
- Next artifact  

## Milestone reconciliation

Before DCM reassessment, full TrustReport reassessment, promotion, major roadmap checkpoint, or release, produce a reconciliation table (see `reconciliation_rows()` in `panel_exp/governance/investigation_lifecycle_contract.py`).

The checkpoint cannot finish until every relevant open investigation for the DCM row has a disposition or explicit deferral with trigger.

## TBRRidge BRB lifecycle (reference)

```
D5-TRUST-TBRRIDGE-BRB-001
  → opened INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001
TBRRIDGE-BRB-INTERVAL-CORRECTION-001
  → resolved estimand alignment
  → opened INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001
D5-TRUST-TBRRIDGE-KFOLD-001
D5-TRUST-TBRRIDGE-PLACEBO-001
DCM-005 reassessment
  → must consume INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001
  → terminal: REMEDIATE | RESTRICT | DIAGNOSTIC_ONLY | PERMANENTLY_BLOCK
```

## CI enforcement

| Test module | Enforces |
|-------------|----------|
| `tests/governance/test_open_investigation_registry_001.py` | Registry schema, active-field completeness, lane bindings |
| `tests/governance/test_artifact_handoff_completeness_001.py` | Summary handoff blocks; report handoff sections |
| `tests/governance/test_roadmap_open_issue_alignment_001.py` | Complete lanes vs open blocking issues |

## Migration

Seeded investigations (2026-06-18):

- `INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001` (RESOLVED)  
- `INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001` (OPEN)  
- `INV-TBRRIDGE-KFOLD-NULL-FPR-001` (PLANNED)  
- `INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001` (DEFERRED_WITH_TRIGGER)  
- `INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001` (OPEN)  
- `INV-MULTICELL-PERCELL-INFERENCE-001` (RESOLVED — `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`)
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001` (DEFERRED_WITH_TRIGGER)
- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001` (DEFERRED_WITH_TRIGGER)

Legacy markdown ledger [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) remains for Phase 12 historical context; new Track D trust-lane defects use the JSON registry.
