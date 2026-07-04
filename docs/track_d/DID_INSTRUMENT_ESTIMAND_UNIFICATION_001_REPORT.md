# DID_INSTRUMENT_ESTIMAND_UNIFICATION_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` |
| **Artifact type** | `instrument_estimand_unification` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `did_instrument_estimand_unified_no_bootstrap_or_claim_authorization` |
| **Base commit** | `bcfcdc0` (Enforce production catalog blocklist) |
| **Final verdict** | `did_instrument_estimand_unified_no_bootstrap_or_claim_authorization` |

This artifact removes ambiguity between `DID_BOOTSTRAP`, governed 2×2 point-estimate execution, library TWFE DID, and bootstrap inference. One instrument ID maps to one estimand, estimator behavior, inference contract, and production eligibility policy.

---

## 2. Source files inspected

- `panel_exp/validation/production_catalog_blocklist_001.py`
- `panel_exp/validation/estimator_inference_did_executor_003.py`
- `panel_exp/validation/estimator_inference_executor_adapters_002.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/readout_did_diagnostics_002.py`
- `panel_exp/methods/DID.py` (library TWFE research implementation)
- Audit and governance docs

---

## 3. Audit finding being addressed

Expanded adversarial audit identified `DID_BOOTSTRAP` naming vs governed 2×2 point-estimate executor split. The governed executor computed point estimates only while the instrument ID implied bootstrap inference. This artifact enforces explicit separation before assignment-panel integrity and statistical threshold enforcement.

---

## 4. Problem statement

| Concept | Prior ambiguity | Unified meaning |
|---------|-----------------|-----------------|
| `DID_BOOTSTRAP` | Sometimes routed to point-estimate executor | Bootstrap inference alias only; production-blocked |
| Governed executor | Accepted `DID_BOOTSTRAP` | Accepts `DID_2X2_POINT_ESTIMATE` only (legacy alias opt-in) |
| Library `DID.py` TWFE | Implicit overlap with governed path | `DID_TWFE_LIBRARY_RESEARCH` research-only |

---

## 5. Conceptual model

- **DID_2X2_POINT_ESTIMATE:** governed 2×2 means DID point estimate; no uncertainty/bootstrap/claims
- **DID_BOOTSTRAP_INFERENCE** (`DID_BOOTSTRAP` alias): bootstrap inference contract; not implemented in governed runtime
- **DID_TWFE_LIBRARY_RESEARCH:** library TWFE in `panel_exp/methods/DID.py`; no governed runtime

---

## 6. Canonical DID instruments and alias policy

| Canonical ID | Aliases | Governed runtime |
|--------------|---------|------------------|
| `DID_2X2_POINT_ESTIMATE` | `DID_GOVERNED_POINT_ESTIMATE`, `DID_POINT_ESTIMATE` | Point estimate when config enabled |
| `DID_BOOTSTRAP_INFERENCE` | `DID_BOOTSTRAP` | Not implemented |
| `DID_TWFE_LIBRARY_RESEARCH` | `DID_TWFE`, `TWFE` | Research library only |

`allow_legacy_did_bootstrap_for_point_estimate` defaults to `false`.

---

## 7. Runtime/executor behavior

`execute_did_point_estimate` accepts canonical point-estimate IDs. `DID_BOOTSTRAP` is rejected by default with failure packet blockers: `MISLEADING_INSTRUMENT_ID`, `INFERENCE_NOT_IMPLEMENTED`, `USE_DID_2X2_POINT_ESTIMATE_FOR_POINT_ONLY_EXECUTION`.

---

## 8. Adapter behavior

Registry distinguishes `DID_2X2_POINT_ESTIMATE` (governed execution under config) from `DID_BOOTSTRAP` / `DID_BOOTSTRAP_INFERENCE` (dry-run only, inference not implemented) and `DID_TWFE_LIBRARY_RESEARCH` (research-only).

---

## 9. Production catalog behavior

Uses DID instrument registry resolution. `DID_BOOTSTRAP` blocked for production claims. `DID_2X2_POINT_ESTIMATE` restricted for production claims but allowed for review/dry-run planning contexts.

---

## 10. Method suitability / readout plan behavior

- Governed point path uses `DID_2X2_POINT_ESTIMATE`
- `DID_BOOTSTRAP` classified as blocked inference alias
- Readout plan production overlay uses review context for planning eligibility

---

## 11. Research-vs-production boundary

Research and point-estimate review preserved for canonical point-estimate instrument. Bootstrap inference and TWFE library remain research/remediation paths. Production causal/incremental/ROI claims blocked.

---

## 12. Claim / production authorization boundary

No claim authorization runtime, bootstrap inference, TWFE executor, uncertainty, p-values, CIs, MMM, or LLM decisioning added. Existing governed point estimate computation unchanged.

---

## 13. Tests added

`tests/validation/test_did_instrument_estimand_registry_001.py` plus updates to executor, adapter, execution runtime, production catalog, method suitability, readout plan, and DID diagnostic tests.

---

## 14. Validation results

Targeted pytest suites pass. Summary JSON validates. Safety grep confirms no forbidden authorization flags set true.

---

## 15. Known limitations

- Legacy `DID_BOOTSTRAP` point-estimate alias available only via explicit transition config
- DID diagnostics and sensitivity artifacts may still reference `DID_BOOTSTRAP` in historical docs
- Bootstrap inference runtime remains deferred

---

## 16. Recommended next artifact

**Primary:** `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001`

**Alternative:** `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001`
