# PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` |
| **Artifact type** | `production_catalog_blocklist_enforcement` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `production_catalog_blocklist_enforced_no_claim_or_production_authorization` |
| **Base commit** | `0763fda` (Update roadmap for audit P0 hardening) |
| **Final verdict** | `production_catalog_blocklist_enforced_no_claim_or_production_authorization` |

This artifact enforces production-catalog blocklist policy across governed planning and execution paths. Implemented ≠ production-safe; characterized ≠ production-safe; governed runtime supported ≠ claim-authorized. Research-only methods remain callable in research contexts but are blocked from production-facing readout, causal claims, ROI claims, and trusted reports.

---

## 2. Source files inspected

- `docs/track_d/AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001.md`
- `docs/ROADMAP_V4.md`
- `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/estimator_inference_executor_adapters_002.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/estimator_inference_did_executor_003.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `panel_exp/validation/readout_did_diagnostics_002.py`
- `panel_exp/validation/claim_authorization_contract_001.py`
- `panel_exp/governance/downstream_readout_authorization_001.py`
- `panel_exp/method_metadata.py`
- Archive evidence: `D5_STAT_DID_BOOTSTRAP_001`, `D5_INST_TBRRIDGE_002`, `D5_AUGSYNTH_CONFORMAL`

---

## 3. Audit finding being addressed

Expanded adversarial audit identified missing enforced production blocklist: negative characterization, insufficient maturity, and unsafe inference/method combinations could still reach production-primary planning slots. `AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001` inserted P0 hardening before claim authorization runtime; this artifact is the first implementation in that lane.

---

## 4. Production blocklist purpose

Evaluate method/instrument combinations for production catalog eligibility without blocking global research use. Overlay production restrictions on method suitability, readout planning, executor adapter availability metadata, and execution-runtime blocking for production contexts.

---

## 5. Maturity policy

| Maturity | Production stance |
|----------|-------------------|
| `IMPLEMENTED_RESEARCH` | Not production-safe |
| `CHARACTERIZED` | Not production-safe |
| `GOVERNED_RUNTIME_SUPPORTED` | Not claim-authorized |
| `EXPERT_REVIEW` | Restricted expert review only |
| `RESEARCH_ONLY` | Blocked for production claims |
| `UNVALIDATED` | Blocked for production claims |
| `PRODUCTION_SAFE` | Required for default eligibility; still subject to claim/runtime gates |

No estimator in the current catalog is `PRODUCTION_SAFE`; reports reflect this honestly.

---

## 6. Default blocklist stance

Conservative defaults encoded from audit and roadmap:

- `DID_BOOTSTRAP` production claims blocked (bootstrap inference not implemented; governed executor point-estimate only)
- `TBR_RIDGE_KFOLD`, `TBR_RIDGE`+Conformal, `TBR_RIDGE`+Jackknife/JKP production claims blocked (negative/invalid interval evidence)
- `TBR_FAMILY` aggregate production paths blocked (unit-panel semantics unresolved)
- `AUGSYNTH`+Conformal production claims blocked until adapter + null calibration (config override available)
- `TROP`, `MTGP`, `BayesianTBR` production exposure blocked (research-only maturity)
- `RESEARCH_ONLY` / `UNVALIDATED` maturity blocked for production
- Missing claim authorization runtime blocks production claim types
- Missing statistical thresholds block default production eligibility

---

## 7. Status taxonomy

- `PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW`
- `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW`
- `PRODUCTION_CATALOG_DIAGNOSTIC_ONLY`
- `PRODUCTION_CATALOG_RESEARCH_ONLY`
- `PRODUCTION_CATALOG_BLOCKED`
- `PRODUCTION_CATALOG_NOT_EVALUATED`

---

## 8. Blocker taxonomy

`NEGATIVE_CHARACTERIZATION_EVIDENCE`, `MISSING_STATISTICAL_THRESHOLDS`, `MISSING_GOVERNED_RUNTIME`, `MISLEADING_INSTRUMENT_ID`, `INFERENCE_NOT_IMPLEMENTED`, `UNCALIBRATED_INFERENCE`, `INVALID_INTERVAL_EVIDENCE`, `UNSUPPORTED_PRODUCTION_CLAIM`, `RESEARCH_ONLY_METHOD`, `UNVALIDATED_METHOD`, `DIAGNOSTIC_ONLY_INSTRUMENT`, `AGGREGATE_UNIT_PANEL_MISMATCH`, `CLAIM_AUTHORIZATION_MISSING`, `PRODUCTION_GOVERNANCE_MISSING`.

---

## 9. Integration with method suitability

`method_suitability_runtime_001` attaches production overlay fields to each instrument matrix row when `enforce_production_catalog_blocklist=true`:

- `production_catalog_status`
- `is_production_blocked`
- `is_research_allowed`
- `production_blockers`
- `production_restrictions`
- `production_catalog_evidence`
- `production_catalog_trace`

Suitability classification semantics unchanged; a method may be method-suitable but production-blocked.

---

## 10. Integration with readout planning

`readout_plan_runtime_001` evaluates production catalog status per instrument and excludes production-blocked instruments from `planned_primary_candidates`. Preserves them in `blocked_instruments`, `research_only_instruments`, or `planned_diagnostic_candidates` without ranking.

---

## 11. Integration with executor adapters

`estimator_inference_executor_adapters_002` exposes `production_catalog_status`, `production_catalog_blocked`, `production_claim_blocked`, and `production_catalog_metadata` on `GovernedExecutorLookupResult`. Dry-run availability may remain true while production claims are blocked (e.g. `DID_BOOTSTRAP`).

---

## 12. Integration with execution runtime

`estimator_inference_execution_runtime_001` blocks production-context execution when catalog status is blocked (`production_catalog_blocklist_gate`). Config defaults:

- `enforce_production_catalog_blocklist = true`
- `block_production_context_when_catalog_blocked = true`
- `block_research_context_when_catalog_blocked = false`
- `allow_research_only_dry_run = true`

Non-production dry-run is not blocked when `allow_research_only_dry_run=true`.

---

## 13. Research-vs-production boundary

Research contexts and dry-run roles remain allowed for blocked instruments unless config disables research. Production contexts, production candidate roles, and production claim types trigger blocklist enforcement.

---

## 14. Claim / production authorization boundary

All claim and production authorization flags remain false. This artifact defines and enforces blocklist policy only; it does not implement claim authorization runtime, trusted readout, MMM, or LLM decisioning.

---

## 15. Tests added

`tests/validation/test_production_catalog_blocklist_001.py` plus integration assertions in method suitability, readout plan, executor adapter, and execution runtime test modules.

---

## 16. Validation results

Targeted pytest suites pass. Summary JSON validates. Safety grep confirms no forbidden authorization flags set true.

---

## 17. Known limitations

- Blocklist policy is conservative and catalog-driven; explicit per-study overrides are limited to config flags (e.g. `allow_augsynth_conformal_production`).
- No statistical threshold numeric enforcement (deferred to `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001`).
- Claim authorization runtime remains unimplemented.
- Library-direct bypass outside governed path is not closed by this artifact alone.

---

## 18. Recommended next artifact

**Primary:** `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`

**Alternative:** `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001`
