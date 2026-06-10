# Design Guardrails 001

**Document ID:** DESIGN-GUARDRAILS-001  
**Title:** Design Guardrails 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design-layer PASS/WARN/BLOCK governance policy  
**Artifact type:** Documentation / governance / guardrails — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Inputs:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) · [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No runtime enforcement · no code changes · no statistical validation execution · no design/estimator/inference promotion · no suitability approval · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Guardrails 001 |
| Status | **Accepted** |
| Scope | Design-layer PASS/WARN/BLOCK policy |
| Artifact type | Documentation / governance / guardrails |

Sixth concrete design audit artifact. Converts the design audit ladder, output contract, implementation blockers, statistical validation protocol, and combination matrix into **enforceable governance rules** for downstream systems.

**This artifact defines policy only. No design or combination is production-ready, suitability-approved, TrustReport-eligible, CalibrationSignal-eligible, MMM-ready, or LLM-ready.**

---

## 2. Purpose

This artifact turns prior design audit findings into operational **guardrail decisions**:

| Input artifact | Guardrail conversion |
|----------------|---------------------|
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Required fields → BLOCK if missing |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | IV-DES-* blockers → BLOCK / REQUIRES_ADAPTER |
| [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Protocol-not-executed → REQUIRES_STATISTICAL_VALIDATION |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix statuses + D-COMB-* → PASS/WARN/BLOCK |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | Bridge transitions → REQUIRES_BRIDGE / BLOCK |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | Readout targets → BLOCK mismatches |

Downstream consumers (experiment planning, suitability framework, TrustReport, CalibrationSignal, MMM, LLM explanation) must treat guardrail decisions as **binding policy** until runtime enforcement exists.

---

## 3. Why this artifact exists

| Gap | Guardrails address |
|-----|-------------------|
| Combination matrix statuses are descriptive | Need operational PASS/WARN/BLOCK for automation |
| Downstream systems need block/warn/pass decisions | Single policy surface for orchestration |
| LLM/experiment planning cannot reason from raw docs alone | Machine-consumable guardrail taxonomy + reason codes |
| **0/31 contract-complete designs** | Hard BLOCK before any governed consumption |
| Geometry/readout mismatches | BLOCK before suitability or product claims |
| Statistical protocol defined but not executed | REQUIRES_STATISTICAL_VALIDATION until D5-DES-STAT-* |

Without guardrails, matrix rows and contract blockers remain documentation-only and may be bypassed in planning or explanation flows.

---

## 4. Scope

Guardrails govern:

- Design artifact readiness (audit ladder completeness)  
- Design output contract field presence and semantics  
- Design implementation status (contract-complete, partial, adapter-required, ambiguous, helper-only)  
- Design statistical validation status (protocol-defined-not-executed, future pass/fail)  
- Combination matrix status per design × geometry × estimator × inference × readout  
- Geometry bridge status (direct, bridge-required, blocked)  
- Inference readout compatibility  
- Multi-cell / shared-control rules  
- Adapter-required designs (QuickBlock, MatchedPair, TrimmedMatch, Supergeo)  
- Trim/thinning and supergeo population transitions  
- Power/MDE planning-only restrictions  
- Downstream consumption controls (planning, suitability, TrustReport, CalibrationSignal, MMM, LLM)  

Applies to all DES-001–DES-031 inventory rows and future design methods.

---

## 5. Non-goals

- No runtime guardrail enforcement implementation (see §27)  
- No design, estimator, or inference code changes  
- No statistical validation execution or D5 archive regeneration  
- No design or combination promotion  
- No suitability role assignment  
- No TrustReport, CalibrationSignal, MMM, or LLM product authorization  

---

## 6. Guardrail status taxonomy

| Status | Meaning | Downstream default |
|--------|---------|-------------------|
| **PASS** | All required preconditions satisfied for the **requested use scope** | May proceed to suitability evaluation only — **not** production authorization |
| **WARN** | Limitation documented; use restricted to planning/characterization with explicit caveats | No causal/product claims |
| **BLOCK** | Hard stop for requested use; unsafe or contract-incomplete | No governed consumption |
| **NOT_EVALUATED** | Insufficient inputs or helper-only row | Treat as BLOCK for production paths |
| **DEFERRED** | Future method family (Bayesian, TROP, SARIMAX) — audit ladder incomplete | BLOCK until program exists |
| **REQUIRES_ADAPTER** | Non-standard design output; adapter artifact required | BLOCK for downstream until adapter |
| **REQUIRES_BRIDGE** | Geometry/readout transition needs bridge ADR | BLOCK for unsupported estimand/claim |
| **REQUIRES_STATISTICAL_VALIDATION** | Protocol or matrix requires executed D5-DES-STAT-* / D5-STAT-* | BLOCK for suitability/product |

**Clarification:** PASS here means **guardrail preconditions met** — not production-ready, not suitability-approved, not TrustReport-eligible.

---

## 7. Inputs required for guardrail evaluation

Every guardrail evaluation must assemble:

| Input | Source |
|-------|--------|
| `design_inventory_id` | DES-001–DES-031 from [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) |
| Design output contract status | [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) §6–§25 |
| `geometry_id` | Contract field + [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) |
| `forbidden_downstream_claims` | Contract field |
| `concurrent_multi_experiment_compatibility` | Contract field |
| Implementation status | [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) §9–§22 |
| Statistical validation status | [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) eligibility |
| Combination matrix status | [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) §6, §20 |
| Readout semantics | [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) |
| `target_population_status` | full / trimmed / supergeo / ambiguous |
| Multi-cell / shared-control metadata | `cell_ids`, `shared_control_policy`, `control_reuse_policy` |
| Bridge artifacts | F-GEO-003, F-GEO-004, pooling ADR, operator contract |
| Adapter artifacts | D5-DES-STAT-BLOCK-PAIR-001, trim/supergeo adapters |
| Future `D5-DES-STAT-*` outcomes | Not yet available — defaults to REQUIRES_STATISTICAL_VALIDATION |

---

## 8. Universal BLOCK rules

**BLOCK** (hard stop for requested downstream use) when any of the following hold:

| Rule ID | Condition |
|---------|-----------|
| DGR-U-B01 | Missing `geometry_id` |
| DGR-U-B02 | Missing treated/control labels (or undocumented pair structure) |
| DGR-U-B03 | Missing `forbidden_downstream_claims` |
| DGR-U-B04 | Missing `concurrent_multi_experiment_compatibility` |
| DGR-U-B05 | Missing `cell_ids` for multi-cell design (`n_test_grps > 1`) |
| DGR-U-B06 | Missing `shared_control_policy` / `control_reuse_policy` when shared control applies |
| DGR-U-B07 | Missing `block_ids` / `stratum_ids` / `pair_ids` when design family requires them |
| DGR-U-B08 | Missing trim/thin excluded-unit metadata (`excluded_units`, target population) |
| DGR-U-B09 | Missing `supergeo_source_unit_map` for supergeo designs |
| DGR-U-B10 | Hidden exclusions (trim/thin units not surfaced in evidence) |
| DGR-U-B11 | Silent pooling (multi-cell or aggregate lift without explicit pooling ADR) |
| DGR-U-B12 | Unsupported geometry transition (design geometry ≠ estimator geometry without bridge) |
| DGR-U-B13 | Readout mismatch (e.g., causal interval claimed from point-only / prediction / forecast interval) |
| DGR-U-B14 | Causal uncertainty claimed from point-only, prediction interval, or forecast interval |
| DGR-U-B15 | Adapter-required design has no adapter (QuickBlock, MatchedPair, TrimmedMatch, Supergeo) |
| DGR-U-B16 | Bridge-required transition attempted without bridge artifact |
| DGR-U-B17 | Combination matrix status is `blocked_*` for requested path |
| DGR-U-B18 | Downstream claim requested that appears in `forbidden_downstream_claims` |
| DGR-U-B19 | Downstream claim requested without suitability framework approval |
| DGR-U-B20 | TrustReport, CalibrationSignal, MMM, or LLM product use requested |

**Repo-wide at authoring:** DGR-U-B01 through DGR-U-B04 apply to **all** tier-1 geo-run designs (IV-DES-001–003).

---

## 9. Universal WARN rules

**WARN** (limited use with documented caveats — **does not authorize** causal or product claims):

| Rule ID | Condition |
|---------|-----------|
| DGR-U-W01 | Balance diagnostics partial but assignment valid |
| DGR-U-W02 | Contract fields present in documentation but validation harness not executed |
| DGR-U-W03 | MDE assumptions documented but not joined to final `DesignEvidence` |
| DGR-U-W04 | Design eligible for future validation per matrix but `D5-DES-STAT-*` not executed |
| DGR-U-W05 | Readout is descriptive/metadata only (no uncertainty authorization) |
| DGR-U-W06 | Concurrency compatibility is `constrained` but documented |
| DGR-U-W07 | Matrix status `allowed_for_future_validation` — planning/characterization only |
| DGR-U-W08 | Guardrail can explain limitation but cannot authorize use |

WARN never overrides BLOCK for the same claim scope.

---

## 10. PASS rules

**PASS** only when **all** of the following hold for the **requested use scope**:

1. All required contract fields present and validated  
2. Implementation status acceptable (contract-complete or adapter satisfied)  
3. Statistical validation executed and acceptable **in scope** (`D5-DES-STAT-*` + relevant D5-STAT)  
4. Combination matrix status not `blocked_*` / not `restricted_*` for requested path (or restriction explicitly waived by suitability — future)  
5. Bridge and adapter requirements satisfied  
6. Readout semantics compatible with requested claim  
7. No forbidden downstream claims requested  
8. [`DESIGN_SUITABILITY_FRAMEWORK_001`](DESIGN_SUITABILITY_FRAMEWORK_001.md) later approves final use (future gate)  

**Current repo assessment:** **0 downstream PASS** for production, suitability, TrustReport, CalibrationSignal, MMM, or LLM product use. Internal characterization with reference designs may WARN only.

---

## 11. Design artifact readiness guardrails

Audit ladder gates — each must be **Accepted** before suitability may consume guardrails as satisfied:

| Gate | Artifact | Guardrail if missing |
|------|----------|---------------------|
| G1 | `DESIGN_OUTPUT_CONTRACT_001` | BLOCK all governed consumption |
| G2 | `DESIGN_CODE_INVENTORY_001` | NOT_EVALUATED per design |
| G3 | `DESIGN_LITERATURE_ALIGNMENT_001` | WARN — conceptual gaps documented |
| G4 | `DESIGN_IMPLEMENTATION_VALIDATION_001` | BLOCK — blockers unknown |
| G5 | `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` | REQUIRES_STATISTICAL_VALIDATION |
| G6 | `DESIGN_COMBINATION_VALIDATION_MATRIX_001` | BLOCK combination-specific claims |
| G7 | `DESIGN_GUARDRAILS_001` | BLOCK automated policy (this artifact) |
| G8 | `DESIGN_SUITABILITY_FRAMEWORK_001` | BLOCK suitability role assignment |

**Current:** G1–G7 ✅ Accepted; G8 pending.

---

## 12. Contract field guardrails

| Contract field | Missing / partial | Guardrail |
|----------------|-------------------|-----------|
| `geometry_id` | missing | **BLOCK** (DGR-U-B01) |
| `design_method_id` | missing | **BLOCK** |
| treated/control labels | missing | **BLOCK** (DGR-U-B02) |
| `forbidden_downstream_claims` | missing | **BLOCK** (DGR-U-B03) |
| `concurrent_multi_experiment_compatibility` | missing | **BLOCK** (DGR-U-B04) |
| `cell_ids` | missing (multi-cell) | **BLOCK** (DGR-U-B05) |
| `shared_control_policy` | missing | **BLOCK** (DGR-U-B06) |
| `block_ids` / `stratum_ids` / `pair_ids` | missing when required | **BLOCK** (DGR-U-B07) |
| `excluded_units` / trim metadata | missing | **BLOCK** (DGR-U-B08) |
| `supergeo_source_unit_map` | missing | **BLOCK** (DGR-U-B09) |
| `assignment_probability` | missing | **WARN** |
| `reproducibility_hash` | incomplete | **WARN** |
| balance diagnostics | partial | **WARN** (DGR-U-W01) |
| power/MDE linkage | partial | **WARN** (DGR-U-W03) |

**Repo:** **0/31** contract-complete → universal BLOCK for governed downstream consumption.

---

## 13. Implementation status guardrails

| Implementation status | Guardrail | Downstream |
|----------------------|-----------|------------|
| `contract_complete` | Eligible for PASS precheck (none today) | Future suitability |
| `contract_mapping_partial` | **BLOCK** + **REQUIRES_STATISTICAL_VALIDATION** | Tier-1 DES-001–006, DES-011 |
| `contract_required` | **BLOCK** | Missing envelope |
| `adapter_required` | **REQUIRES_ADAPTER** → **BLOCK** without adapter | DES-007–010 |
| `implementation_ambiguous` | **BLOCK** | DES-005 ThinningDesign |
| `helper_only` / `not_emitted` | **NOT_EVALUATED** → **BLOCK** for matrix anchor | DES-016–025, validators |
| `superseded` / `historical` | **BLOCK** | Legacy paths |

Maps to IV-DES-001–017 from implementation validation §24–§25.

---

## 14. Statistical validation guardrails

| Stat status | Guardrail | Notes |
|-------------|-----------|-------|
| `protocol_defined_not_executed` | **REQUIRES_STATISTICAL_VALIDATION** | Current repo default |
| `future_validation_pass` | Eligible for PASS precheck (with other gates) | No archives yet |
| `pass_with_caveats` | **WARN** for scope; PASS only if caveats accepted in suitability | Future |
| `mixed_requires_followup` | **WARN** / **REQUIRES_STATISTICAL_VALIDATION** | Follow-up harness |
| `fail` | **BLOCK** for requested scope | Future |
| `blocked` | **BLOCK** | Protocol ineligible |

**Current:** All 31 designs → **REQUIRES_STATISTICAL_VALIDATION**; 0 executed `D5-DES-STAT-*`.

---

## 15. Combination matrix guardrails

Maps [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) §6 statuses to guardrail decisions:

| Matrix status | Guardrail | Downstream impact |
|---------------|-----------|-------------------|
| `allowed_for_future_validation` | **WARN** + **REQUIRES_STATISTICAL_VALIDATION** | Planning/OC queue only |
| `restricted_requires_contract_fields` | **BLOCK** (governed) + **WARN** (internal dev) | Contract emission required |
| `restricted_requires_statistical_validation` | **REQUIRES_STATISTICAL_VALIDATION** | No suitability |
| `adapter_required` | **REQUIRES_ADAPTER** → **BLOCK** | Adapter before matrix promotion |
| `bridge_required` | **REQUIRES_BRIDGE** → **BLOCK** for unsupported claim | Bridge ADR first |
| `blocked_due_to_geometry_mismatch` | **BLOCK** | DGR-U-B12 |
| `blocked_due_to_readout_mismatch` | **BLOCK** | DGR-U-B13 |
| `blocked_due_to_missing_contract_fields` | **BLOCK** | DGR-U-B01–B04 |
| `blocked_due_to_implementation_ambiguity` | **BLOCK** | Thinning semantics |
| `blocked_for_pooled_claim` | **BLOCK** | DGR-U-B11 |
| `helper_not_matrix_candidate` | **NOT_EVALUATED** | Not a combination anchor |
| `not_evaluated` | **NOT_EVALUATED** / **DEFERRED** | Future methods |

**Combinations promoted:** **0** — no matrix row yields downstream PASS today.

---

## 16. Geometry bridge guardrails

Per [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md):

| Transition | Guardrail | Reason code |
|------------|-----------|-------------|
| Trim/full-pop bridge | **REQUIRES_BRIDGE** for original-population claims | D-COMB-GEOMETRY-BRIDGE-REQUIRED |
| Supergeo/original-geo bridge | **REQUIRES_BRIDGE** + **REQUIRES_ADAPTER** | D-COMB-GEOMETRY-BRIDGE-REQUIRED |
| Aggregate/unit-panel bridge | **REQUIRES_BRIDGE** or **BLOCK** | D-COMB-GEOMETRY-BRIDGE-REQUIRED |
| Per-cell/pooled bridge | **BLOCK** for pooled without ADR | D-COMB-POOLED-CLAIM-BLOCKED |
| Time-series operator/causal interval bridge | **BLOCK** readout mismatch without operator contract | D-COMB-READOUT-MISMATCH |

Direct transitions (matching geometry_id) may WARN + REQUIRES_STATISTICAL_VALIDATION only.

---

## 17. Readout semantics guardrails

Per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md):

| Readout target | Guardrail for causal claim |
|----------------|---------------------------|
| Point-only | **BLOCK** uncertainty / significance claims |
| Prediction interval | **BLOCK** causal interval authorization |
| Forecast interval | **BLOCK** causal uncertainty |
| Null decision | **REQUIRES_STATISTICAL_VALIDATION** + explicit null semantics |
| Causal interval candidate | **REQUIRES_STATISTICAL_VALIDATION** |
| Causal interval validated in scope | Eligible for PASS precheck (with other gates) |

Directional sign-only without null calibration → **WARN** at best; **BLOCK** for TrustReport/MMM.

---

## 18. Multi-cell / shared-control guardrails

| Rule | Guardrail |
|------|-----------|
| `cell_ids` required | **BLOCK** if missing (DGR-U-B05) |
| `shared_control_policy` required | **BLOCK** if missing (DGR-U-B06) |
| No silent pooling | **BLOCK** (DGR-U-B11) |
| Per-cell vs pooled distinction | Per-cell only without bridge; pooled → **BLOCK** |
| Portfolio lift claims | **BLOCK** without pooling bridge (F-MCELL-001) |
| Control reuse burden | **WARN** if documented; **BLOCK** if omitted |

DCM-006, DCM-007 in combination matrix.

---

## 19. Trim / thinning guardrails

| Rule | Guardrail |
|------|-----------|
| `excluded_units` required | **BLOCK** (DGR-U-B08) |
| Target-population shift documented | **WARN** if partial; **BLOCK** if hidden |
| Original population claims without bridge | **BLOCK** (REQUIRES_BRIDGE) |
| Thinning semantics ambiguity (DES-005) | **BLOCK** until ADR (D-COMB-IMPLEMENTATION-AMBIGUOUS) |
| TrimmedMatch (DES-009) | **REQUIRES_ADAPTER** + **REQUIRES_BRIDGE** |

---

## 20. Supergeo guardrails

| Rule | Guardrail |
|------|-----------|
| `supergeo_source_unit_map` required | **BLOCK** (DGR-U-B09) |
| Aggregation distortion diagnostics required | **WARN** if partial; **REQUIRES_STATISTICAL_VALIDATION** |
| Original geo claims without bridge | **BLOCK** (F-GEO-003) |
| Concurrent multi-experiment without bridge | **BLOCK** (DGR-U-B04 + bridge) |
| SupergeoModel (DES-010) | **REQUIRES_ADAPTER** + **REQUIRES_BRIDGE** |

---

## 21. Power / MDE guardrails

| Rule | Guardrail |
|------|-----------|
| Power/MDE does not authorize causal readout | **BLOCK** causal claims from PowerAnalysis alone |
| Aggregate-vs-unit geometry must be explicit | **BLOCK** on mismatch (D-COMB-POWER-GEOMETRY-MISMATCH) |
| MDE assumptions linked to design evidence | **WARN** if unlinked (DGR-U-W03) |
| Planning-only use | **WARN** — experiment planning rank only |

DES-014, DES-015; DCM-015.

---

## 22. Future Bayesian / TROP / SARIMAX guardrails

| Method family | Guardrail | Next artifacts |
|---------------|-----------|----------------|
| Bayesian | **DEFERRED** → **BLOCK** | BAYESIAN_METHOD_SPECIFICATION_001 + audit ladder |
| TROP / triply robust | **DEFERRED** → **NOT_EVALUATED** | TRIPLY_ROBUST_* audit program |
| SARIMAX / Auto-SARIMAX | **DEFERRED** → **BLOCK** (readout) | TBR_SARIMAX_OPERATOR_CONTRACT_001 |

Reason code: **D-COMB-FUTURE-METHOD-DEFERRED**. No promotion until full audit program + implementation + statistical validation + readout semantics exist.

---

## 23. Downstream consumption guardrails

| Consumer | Policy |
|----------|--------|
| **Experiment planning** | Filter **BLOCK** first; **REQUIRES_*** rows not normal candidates; **WARN** only for documented planning scope |
| **Design candidate ranking** | Rank only among non-BLOCK rows; adapter/bridge rows deprioritized below contract-complete |
| **Suitability framework** | Consumes guardrail decisions; no suitability on BLOCK / REQUIRES_* without resolution |
| **TrustReport** | **BLOCK** — all designs today |
| **CalibrationSignal** | **BLOCK** — all designs today |
| **MMM calibration** | **BLOCK** — all designs today |
| **LLM explanation** | May explain BLOCK/WARN/PASS/reason codes; **cannot override** guardrails |

LLM and orchestration layers must surface guardrail status and D-COMB-* codes; they must not infer production readiness from D5 estimator characterization alone.

---

## 24. Reason-code mapping

Maps D-COMB reason codes from [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) §21 to guardrail decisions:

| Reason code | Guardrail decision | Notes |
|-------------|-------------------|-------|
| D-COMB-MISSING-GEOMETRY-ID | **BLOCK** | DGR-U-B01 |
| D-COMB-MISSING-CONTRACT-FIELDS | **BLOCK** | DGR-U-B01–B09 as applicable |
| D-COMB-ADAPTER-REQUIRED | **REQUIRES_ADAPTER** → **BLOCK** downstream | Until adapter exists |
| D-COMB-GEOMETRY-BRIDGE-REQUIRED | **REQUIRES_BRIDGE** → **BLOCK** for unsupported claim | F-GEO-003/004 |
| D-COMB-READOUT-MISMATCH | **BLOCK** | DGR-U-B13 |
| D-COMB-STAT-VALIDATION-REQUIRED | **REQUIRES_STATISTICAL_VALIDATION** | D5-DES-STAT-* |
| D-COMB-IMPLEMENTATION-AMBIGUOUS | **BLOCK** | Thinning DES-005 |
| D-COMB-POOLED-CLAIM-BLOCKED | **BLOCK** | DGR-U-B11 |
| D-COMB-SHARED-CONTROL-METADATA-MISSING | **BLOCK** | DGR-U-B05, B06 |
| D-COMB-BLOCK-PAIR-INFERENCE-REQUIRED | **BLOCK** | Unadjusted inference on block/pair designs |
| D-COMB-POWER-GEOMETRY-MISMATCH | **BLOCK** | Power vs readout geometry |
| D-COMB-FUTURE-METHOD-DEFERRED | **DEFERRED** → **BLOCK** | Bayesian/TROP/SARIMAX |

---

## 25. Master guardrail table

Compact policy register (key rows; full DES inventory inherits universal rules):

| Guardrail ID | Condition | Decision | Reason code(s) | Affected groups | Downstream impact | Next artifact |
|--------------|-----------|----------|----------------|-----------------|-------------------|---------------|
| DGR-001 | Missing `geometry_id` | BLOCK | D-COMB-MISSING-GEOMETRY-ID | All geo designs | No governed consumption | Contract implementation |
| DGR-002 | Missing contract envelope (forbidden claims, concurrency) | BLOCK | D-COMB-MISSING-CONTRACT-FIELDS | DES-001–006, 011 | No suitability | IV-DES-002, 003 |
| DGR-003 | Tier-1 × SCM-JK unit-panel | WARN + REQUIRES_STAT | D-COMB-MISSING-CONTRACT-FIELDS; D-COMB-STAT-VALIDATION-REQUIRED | DCM-001 | OC queue only | D5-DES-STAT-TIER1-001 |
| DGR-004 | Tier-1 × TBR aggregate (geometry mismatch) | BLOCK | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-003 | No aggregate path | Geometry bridge ADR |
| DGR-005 | Tier-1 × DID bootstrap (geometry mismatch) | BLOCK | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-004 | No pooled DID | Geometry bridge ADR |
| DGR-006 | Multi-cell pooled lift | BLOCK | D-COMB-POOLED-CLAIM-BLOCKED | DCM-007 | No portfolio claim | Pooling ADR |
| DGR-007 | QuickBlock / MatchedPair | REQUIRES_ADAPTER → BLOCK | D-COMB-ADAPTER-REQUIRED | DCM-009 | No downstream | Adapter + D5-DES-STAT-BLOCK-PAIR |
| DGR-008 | Block/pair + unadjusted bootstrap | BLOCK | D-COMB-BLOCK-PAIR-INFERENCE-REQUIRED | DCM-010 | No inference | Block-aware inference |
| DGR-009 | TrimmedMatch trimmed scope | REQUIRES_BRIDGE + REQUIRES_ADAPTER | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-011 | Trim-only readout | F-GEO-004 |
| DGR-010 | TrimmedMatch full-pop SCM-JK | REQUIRES_BRIDGE → BLOCK | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-012 | No full-pop claim | F-GEO-004 |
| DGR-011 | Supergeo scope readout | REQUIRES_BRIDGE + REQUIRES_ADAPTER | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-013 | Supergeo-only | F-GEO-003 |
| DGR-012 | Supergeo → original-geo SCM-JK | BLOCK | D-COMB-GEOMETRY-BRIDGE-REQUIRED | DCM-014 | No original-geo | F-GEO-003 |
| DGR-013 | ThinningDesign SCM-JK | BLOCK | D-COMB-IMPLEMENTATION-AMBIGUOUS | DCM-016 | Ambiguous population | Thinning ADR |
| DGR-014 | Power/MDE planning rank | WARN | D-COMB-POWER-GEOMETRY-MISMATCH | DCM-015 | Planning only | D5-DES-STAT-POWER-MDE-001 |
| DGR-015 | Power → causal readout | BLOCK | D-COMB-READOUT-MISMATCH | DES-014 | No causal from power | — |
| DGR-016 | Bayesian / TROP / SARIMAX | DEFERRED → BLOCK | D-COMB-FUTURE-METHOD-DEFERRED | DCM-017–019 | Parked | Method audit programs |
| DGR-017 | TrustReport / CalibrationSignal / MMM / LLM product | BLOCK | (governance) | All | No product use | DESIGN_SUITABILITY_FRAMEWORK_001 |
| DGR-018 | Suitability role without framework | BLOCK | (governance) | All | No role assignment | DESIGN_SUITABILITY_FRAMEWORK_001 |
| DGR-019 | `validate_design` PASS only | WARN | — | All | Does not clear contract BLOCK | Implementation fixes |
| DGR-020 | Executed D5-STAT on reference design only | WARN | D-COMB-STAT-VALIDATION-REQUIRED | Estimator paths | Not design validation | D5-DES-STAT-* |

---

## 26. Current repo guardrail assessment

Conservative assessment at authoring (2026-06-10):

| Metric | Value |
|--------|-------|
| Downstream **PASS** | **0** |
| Tier-1 unit-panel designs | **BLOCK** (contract) + **WARN** (internal) + **REQUIRES_STATISTICAL_VALIDATION** |
| Adapter-required designs (DES-007–010) | **REQUIRES_ADAPTER** → **BLOCK** downstream |
| Trim / supergeo | **REQUIRES_BRIDGE** (+ adapter for trim/supergeo outputs) |
| Pooled / portfolio claims | **BLOCK** |
| Future Bayesian / TROP / SARIMAX | **DEFERRED** / **BLOCK** |
| Contract field grep in `panel_exp/` | **0 matches** for `geometry_id`, `forbidden_downstream_claims`, `concurrent_multi_experiment_compatibility`, `shared_control_policy` |

**Verdict:** `design_guardrails_defined_no_downstream_pass`

---

## 27. Relationship to future runtime enforcement

Guardrails defined here are **policy-only**. Future runtime enforcement may be implemented via:

- **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** — documentation artifact defining code integration points (`geo_runner`, `DesignEvidence`, experiment planning orchestrator), or  
- Direct integration into `panel_exp/evidence.py`, `panel_exp/geo_runner.py`, and validation generators after suitability framework exists.

Until enforcement lands, consumers must apply this document manually or via future register generators.

---

## 28. Relationship to design suitability

**Suitability framework:** [`DESIGN_SUITABILITY_FRAMEWORK_001`](DESIGN_SUITABILITY_FRAMEWORK_001.md) ✅ **Accepted** (design-side; distinct from estimator-focused [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)).

**This suitability framework consumes guardrail decisions** (PASS/WARN/BLOCK/REQUIRES_*) and maps them to design-side suitability categories. Guardrail verdicts in this artifact are **unchanged** — suitability does not weaken BLOCK or REQUIRES_* decisions.

1. Suitability consumes guardrail decisions  
2. Maps to categories (`contract_blocked`, `stat_validation_required`, `adapter_required`, `bridge_required`, `planning_only`, `blocked`, …)  
3. Only assigns positive categories after guardrails satisfied + executed statistical validation  

**No suitability row may advance on BLOCK or unresolved REQUIRES_* status.** Verdict: `design_suitability_framework_defined_no_downstream_suitable_designs`.

**Enforcement plan:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) ✅ **Accepted** — **prerequisite for runtime guardrail enforcement** (`DESIGN_GUARDRAIL_ENFORCEMENT_001`). Guardrail verdicts unchanged until contract fields are emitted and validated.

**Schema:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) ✅ **Accepted** — **future guardrail runtime enforcement should consume this schema** for field validation.

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — **runtime guardrails still wait on emission + validation tests**; verdicts unchanged; 0 downstream PASS.

**Next artifact:** `DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`.

---

## 29. Governance gates

| Gate | Status |
|------|--------|
| Guardrails defined | ✅ This artifact |
| Runtime enforcement | ❌ Not implemented |
| Designs validated | ❌ 0 statistically validated |
| Combinations promoted | ❌ 0 |
| Suitability assigned (design-side) | ❌ None |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCK** |

This artifact does **not** validate or promote designs. It does **not** authorize causal claims. It does **not** authorize TrustReport, CalibrationSignal, MMM, or LLM product use. Future validation execution and suitability gates are required.

---

## 30. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_guardrails_defined_no_downstream_pass` |
| Master guardrail rows | 20 key policies (+ universal rules) |
| Downstream PASS | **0** |
| Reason codes mapped | 12 D-COMB-* codes |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_COMBINATION_VALIDATION_MATRIX_001\|DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001\|DESIGN_IMPLEMENTATION_VALIDATION_001" -n docs
grep -R "D-COMB-\|blocked_due_to\|adapter_required\|bridge_required\|restricted_requires" -n docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "PASS\|WARN\|BLOCK\|guardrail\|suitability\|TrustReport\|CalibrationSignal\|MMM\|LLM" -n docs tests panel_exp
find docs -iname "*GUARDRAIL*" -o -iname "*COMBINATION*" -o -iname "*SUITABILITY*" -o -iname "*TRUST*" -o -iname "*CALIBRATION*"
```

**Code inspected (read-only):** `panel_exp/design/`, `panel_exp/geo_runner.py`, `panel_exp/evidence.py`, `panel_exp/spec.py`, `tests/test_design_registry.py`, `tests/test_public_api.py`, `tests/track_d/test_design_inventory_001.py`, `tests/track_d/test_d5_des_trim_001.py`, `tests/track_d/test_d5_des_supergeo_001.py`, `tests/track_d/test_d5_pow_001e_design_geometry.py`, validation doc tests, Track D D5 design tests.

---

## 31. Roadmap

**Next artifact:** **`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`**

Schema ✅ · Tier-1 emission plan ✅ · Enforcement plan ✅ · Suitability framework ✅.

---

## 32. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Combination matrix consumed | ✅ |
| Reason codes mapped | ✅ §24 |
| BLOCK/WARN/PASS rules defined | ✅ §8–§10 |
| Downstream policies defined | ✅ §23 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 33. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Guardrails Accepted; next = suitability |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Guardrails converts matrix to policy |
| [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Guardrails block until validation outcomes |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Hard blockers feed guardrails |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Missing fields = BLOCK |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability blocked until guardrails satisfied |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Guardrails complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Guardrails prerequisite for suitability |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Unresolved guardrail blockers |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning filters through guardrails |

---

*DESIGN-GUARDRAILS-001 v1.0.4 — Accepted; runtime guardrails wait on emission + validation tests; next = DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.*
