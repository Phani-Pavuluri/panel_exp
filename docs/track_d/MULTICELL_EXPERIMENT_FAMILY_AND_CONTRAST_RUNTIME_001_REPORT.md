# MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001` |
| **Artifact type** | `multicell_experiment_family_contrast_runtime` |
| **Status** | `completed` |
| **Scope** | `multicell_experiment_family_and_contrast_runtime_implemented_no_multiplicity_or_inference_computation` |
| **Base commit** | `91dece1` (Fix governance test module name collision for multicell contract) |
| **Final verdict** | `multicell_experiment_family_and_contrast_runtime_implemented_no_multiplicity_or_inference_computation` |

**Depends on:** `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

---

## 2. Source files inspected

- `panel_exp/validation/multicell_experiment_family_contrast_contract_001.py`
- `tests/validation/test_multicell_experiment_family_contrast_contract_001.py`
- `docs/track_d/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_REPORT.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `panel_exp/validation/claim_authorization_runtime_001.py`
- `panel_exp/validation/method_promotion_review_runtime_001.py`

---

## 3. Runtime purpose

Narrow gate runtime that:

1. **Classifies** experiment family from identity signals (or explicit override).
2. **Maps** input evidence fields to contract evidence keys.
3. **Evaluates** requested readout surface eligibility via contract `evaluate_readout_surface`.
4. **Emits** a deterministic surface eligibility packet.

Does **not** compute multiplicity corrections, covariance, p-values, CIs, uncertainty, effects, lift, ROI, winner claims, budget recommendations, production authorization, method promotion, or catalog changes.

---

## 4. Public API

- `generate_multicell_experiment_family_contrast_review(input_data, config=None)`
- `evaluate_multicell_readout_surface(...)` (alias)
- `build_multicell_contrast_eligibility_packet(...)` (alias)

Supports dict, dataclass-like, and **list** input (multiple independent packets, no ranking).

---

## 5. Input / output packet

**Input:** family identity fields, evidence artifacts, `requested_surface`, optional `contrast_type`.

**Output packet fields:** `request_id`, `review_id`, `experiment_family`, `requested_surface`, `surface_status`, `allowed_surface`, `blocked_surface`, `required_evidence`, `missing_evidence`, `blockers`, `required_caveats`, contrast/multiplicity/covariance flags, `family_classification_reason`, `lineage_manifest`, `provenance_hash`, `policy_version`, `failure_packet`, `authorization_boundary_report`.

`review_id` and `provenance_hash` are deterministic (SHA-256 of canonical payload); no wall-clock dependency.

---

## 6. Family classification behavior

Classification order (unless `experiment_family` explicitly provided):

1. Pooling/global requested → `POOLED_AGGREGATE_FAMILY`
2. Dose semantics/contrast → `DOSE_RESPONSE_FAMILY`
3. Decision family spanning experiments/platforms → `PORTFOLIO_DECISION_FAMILY`
4. Shared control / overlapping units → `SHARED_CONTROL_MULTI_ARM`
5. Planned cross-arm comparisons → `RELATED_PARALLEL_ARMS`
6. Multiple experiments/platforms without shared family → `INDEPENDENT_EXPERIMENTS`
7. Multiple arms same context → `RELATED_PARALLEL_ARMS`
8. Single standalone experiment → `INDEPENDENT_EXPERIMENTS`
9. Otherwise → `UNKNOWN_FAMILY_REQUIRES_REVIEW`

---

## 7. Independent-experiment exemption behavior

`INDEPENDENT_EXPERIMENTS` allow `STANDALONE_ARM_READOUT` without `multiplicity_required` or shared covariance. Cross-platform winner, global, pooled, and portfolio comparative surfaces remain blocked unless reclassified with required evidence.

---

## 8. Contrast / multiplicity / covariance gate behavior

- **Related parallel arms:** `ARM_COMPARISON` requires contrast definitions and multiplicity policy.
- **Shared-control multi-arm:** additionally requires shared-control covariance semantics.
- **Dose-response:** `DOSE_RESPONSE_SUMMARY` requires dose ordering/units/policy.
- **Winner / scale-budget / production recommendation:** always blocked in this artifact.

---

## 9. Pooled / global gate behavior

`POOLED_EFFECT_SUMMARY` and `GLOBAL_EFFECT_SUMMARY` require pooling weights, heterogeneity diagnostics, covariance/variance semantics, and estimand alignment within `POOLED_AGGREGATE_FAMILY` or `SHARED_CONTROL_MULTI_ARM`.

---

## 10. Failure packet semantics

Propagates contract failure packets with codes: `UNKNOWN_EXPERIMENT_FAMILY`, `MISSING_CONTRAST_DEFINITION`, `MISSING_MULTIPLICITY_POLICY`, `MISSING_SHARED_CONTROL_COVARIANCE_SEMANTICS`, `MISSING_DOSE_RESPONSE_SEMANTICS`, `MISSING_POOLING_WEIGHTS`, `WINNER_CLAIM_BLOCKED`, `BUDGET_SCALE_CLAIM_BLOCKED`, etc.

---

## 11. Authorization boundary

| Flag | Value |
|------|-------|
| `runtime_implemented` | true |
| `multiplicity_correction_computed` | false |
| `covariance_computed` | false |
| `winner_claim_authorized` | false |
| `production_recommendation_authorized` | false |
| `method_promoted` | false |

---

## 12. Tests added

`tests/validation/test_multicell_experiment_family_contrast_runtime_001.py` — 20 scenarios covering API, classification, gates, determinism, forbidden flags.

---

## 13. Validation results

- Runtime tests pass
- Contract tests unchanged and pass
- Governance suite pass
- Safety grep: no forbidden `true` flags

---

## 14. Known limitations

- Classification heuristics are conservative; ambiguous inputs fail closed to `UNKNOWN_FAMILY_REQUIRES_REVIEW`.
- Not yet integrated into readout plan or claim authorization chain.
- Does not compute or apply multiplicity corrections.

---

## 15. Recommended next artifact

**`TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`**

**Alternative:** `MULTICELL_CONTRAST_MULTIPLICITY_RUNTIME_INTEGRATION_001`
