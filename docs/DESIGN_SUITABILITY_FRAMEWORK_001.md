# Design Suitability Framework 001

**Document ID:** DESIGN-SUITABILITY-FRAMEWORK-001  
**Title:** Design Suitability Framework 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design-side suitability classification  
**Artifact type:** Documentation / governance / suitability framework — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Inputs:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) · [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Distinct from:** [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) — estimator/inference × geometry suitability surface; **not replaced by this artifact**.

**Guardrails:** No code implementation · no validation execution · no runtime enforcement · no design promotion · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Suitability Framework 001 |
| Status | **Accepted** |
| Scope | Design-side suitability classification |
| Artifact type | Documentation / governance / suitability framework |

Seventh concrete design audit artifact. Classifies design methods and design × estimator × inference combinations for **structural suitability** after consuming contract completeness, implementation status, statistical validation readiness, combination matrix compatibility, and guardrail decisions.

**No suitability category defined here grants downstream production use, TrustReport eligibility, CalibrationSignal eligibility, MMM readiness, or LLM product authorization at authoring.**

---

## 2. Purpose

This artifact defines **how design methods receive suitability categories** based on:

| Input | Role in classification |
|-------|------------------------|
| Design output contract | Contract completeness → `contract_blocked` |
| Implementation validation | Adapter/ambiguous/helper statuses |
| Statistical validation protocol | `stat_validation_required` until `D5-DES-STAT-*` executed |
| Combination matrix | Geometry/estimator/readout compatibility |
| Guardrails | PASS/WARN/BLOCK/REQUIRES_* gates |
| Geometry bridge | Population/geometry scope |
| Readout semantics | Causal vs planning readout boundaries |

**Suitability classification ≠ validation execution ≠ product authorization.**

---

## 3. Why this artifact exists

| Gap | This framework addresses |
|-----|--------------------------|
| Guardrails block unsafe cases | Planning also needs **ranked suitability categories** |
| Experiment recommendation needs filtered candidates | Separates eligible-for-future-validation from production-safe |
| Estimator/inference suitability exists separately | Design-side structural suitability is a **distinct layer** |
| **0 downstream PASS** in guardrails | Conservative categories prevent false promotion |
| D5-STAT used reference designs only | Design evidence suitability must not inherit estimator OC |

Without this framework, guardrail BLOCK decisions lack a structured vocabulary for experiment planning, documentation review, and future product gates.

---

## 4. Scope

Applies to:

- All DES-001–DES-031 inventory rows from [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md)  
- Design output contract readiness per design family  
- Implementation status from [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md)  
- Statistical validation readiness/outcomes from [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md)  
- Combination matrix status from [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md)  
- Guardrail decisions from [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md)  
- Geometry bridge and readout compatibility  
- Multi-cell / shared-control metadata status  
- Downstream planning and explanation surfaces (blocked until product gates)  

---

## 5. Non-goals

- No design, estimator, or inference code implementation  
- No statistical validation execution or D5 archive regeneration  
- No runtime guardrail or contract enforcement  
- No design or combination promotion  
- No TrustReport, CalibrationSignal, MMM, or LLM product authorization  
- No replacement of [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)  

---

## 6. Suitability taxonomy

| Category | Meaning | Grants production use? |
|----------|---------|------------------------|
| `suitable_after_validation` | May become structurally suitable **after** executed `D5-DES-STAT-*` pass + guardrails PASS | **No** until all gates + product charter |
| `conditionally_suitable_with_caveats` | Limited scope with documented gaps (WARN guardrails) | **No** |
| `research_only` | Characterization/planning research path only | **No** |
| `planning_only` | Experiment planning rank / MDE exploration only | **No** causal/product |
| `adapter_required` | Non-standard output; adapter before advancement | **No** |
| `bridge_required` | Geometry/population bridge before scoped claims | **No** |
| `contract_blocked` | Missing required contract fields | **No** |
| `stat_validation_required` | Protocol defined; execution required | **No** |
| `implementation_ambiguous` | Population/semantics unclear in code | **No** |
| `helper_not_suitable` | Helper/registry/output object — not design anchor | **No** |
| `deferred_future_method` | Bayesian/TROP/SARIMAX parked | **No** |
| `blocked` | Hard guardrail BLOCK or matrix `blocked_*` | **No** |

**At authoring: no category grants TrustReport, CalibrationSignal, MMM, or LLM product use.**

---

## 7. Required inputs for suitability

Every suitability evaluation must declare:

| Input | Source |
|-------|--------|
| `design_inventory_id` | DES-001–DES-031 |
| `design_name` | Registry / inventory |
| `design_family` | Literature alignment |
| `design_output_contract_status` | complete / partial / missing |
| `implementation_status` | Implementation validation §9–§22 |
| `literature_alignment_status` | Literature alignment verdict |
| `statistical_validation_status` | Protocol eligibility |
| `combination_matrix_status` | DCM rows |
| `guardrail_decision` | PASS / WARN / BLOCK / REQUIRES_* |
| `geometry_id` | Contract + geometry bridge |
| `target_population_status` | full / trimmed / supergeo / ambiguous |
| `bridge_status` | direct / bridge_required / blocked |
| `adapter_status` | none / required / satisfied |
| `multi_cell_mode` | single / per_cell / pooled |
| `shared_control_status` | documented / missing / n/a |
| `readout_semantics` | point / interval / planning metadata |
| `downstream_request_type` | §23 request taxonomy |

---

## 8. Suitability decision logic

**Ordered evaluation** — earlier rules dominate; positive categories never override hard blocks:

```text
1. Hard BLOCK (guardrail BLOCK, matrix blocked_*, forbidden claims, product layers)
2. DEFERRED future methods (Bayesian, TROP, SARIMAX)
3. REQUIRES_ADAPTER → adapter_required
4. REQUIRES_BRIDGE → bridge_required
5. Contract completeness → contract_blocked if required fields missing
6. Implementation ambiguous → implementation_ambiguous
7. Helper-only rows → helper_not_suitable
8. REQUIRES_STATISTICAL_VALIDATION → stat_validation_required
9. Combination matrix restricted_* → contract_blocked or stat_validation_required
10. Guardrail WARN → conditionally_suitable_with_caveats or research_only
11. Guardrail PASS (precheck only) → may evaluate suitable_after_validation AFTER step 8 cleared
12. Downstream product authorization (TrustReport, CalibrationSignal, MMM, LLM) → ALWAYS separate; BLOCKED today
```

**Rule:** Steps 1–10 apply today. Step 11 has **zero** satisfied rows at authoring. Step 12 remains blocked for all designs.

---

## 9. Current repo assessment

Conservative summary (2026-06-10):

| Metric | Value |
|--------|-------|
| Production/downstream suitable designs | **0** |
| TrustReport/CalibrationSignal/MMM/LLM eligible | **0** |
| Contract-complete designs | **0 / 31** |
| Statistically validated designs | **0 / 31** |
| Tier-1 geo-run (DES-001–006) | `contract_blocked` + `stat_validation_required` |
| QuickBlock / MatchedPair | `adapter_required` |
| TrimmedMatch / Supergeo | `adapter_required` + `bridge_required` |
| ThinningDesign | `implementation_ambiguous` |
| multi_test_groups | `contract_blocked` (metadata) |
| PowerAnalysis / PowerContract | `planning_only` |
| Helpers/output objects | `helper_not_suitable` |
| Future Bayesian / TROP / SARIMAX | `deferred_future_method` |

**Verdict precursor:** `design_suitability_framework_defined_no_downstream_suitable_designs`

---

## 10. Design-group suitability table

| Design group | DES IDs | Guardrail | Suitability category | Reason codes | Next artifact/action | Allowed current use | Blocked current use |
|--------------|---------|-----------|---------------------|--------------|---------------------|---------------------|---------------------|
| greedy_match_markets | DES-001 | BLOCK + REQUIRES_STAT | `contract_blocked` + `stat_validation_required` | D-SUIT-CONTRACT-BLOCKED; D-SUIT-STAT-VALIDATION-REQUIRED | Contract emission + D5-DES-STAT-TIER1-001 | Doc review; validation planning | Production; TrustReport; MMM |
| CompleteRandomization | DES-002 | BLOCK + REQUIRES_STAT | `contract_blocked` + `stat_validation_required` | D-SUIT-CONTRACT-BLOCKED | Same as tier-1 | Doc review | Production |
| BalancedRandomization | DES-003 | BLOCK + REQUIRES_STAT | `contract_blocked` + `stat_validation_required` | D-SUIT-CONTRACT-BLOCKED | Same | Doc review | Production |
| StratifiedRandomization | DES-004 | BLOCK + REQUIRES_STAT | `contract_blocked` + `stat_validation_required` | D-SUIT-CONTRACT-BLOCKED | + stratum_ids emission | Doc review | Production |
| Rerandomization | DES-006 | BLOCK + REQUIRES_STAT | `contract_blocked` + `stat_validation_required` | D-SUIT-CONTRACT-BLOCKED | + rerandomization identity in evidence | Doc review | Production |
| ThinningDesign | DES-005 | BLOCK | `implementation_ambiguous` | D-SUIT-IMPLEMENTATION-AMBIGUOUS | Thinning semantics ADR | Doc review only | All governed use |
| QuickBlock | DES-007 | REQUIRES_ADAPTER → BLOCK | `adapter_required` | D-SUIT-ADAPTER-REQUIRED | D5-DES-STAT-BLOCK-PAIR-001 + adapter | API smoke | Downstream pairing |
| MatchedPair | DES-008 | REQUIRES_ADAPTER → BLOCK | `adapter_required` | D-SUIT-ADAPTER-REQUIRED | Same | API smoke | Downstream pairing |
| TrimmedMatchDesign | DES-009 | REQUIRES_ADAPTER + REQUIRES_BRIDGE | `adapter_required` + `bridge_required` | D-SUIT-ADAPTER-REQUIRED; D-SUIT-BRIDGE-REQUIRED | F-GEO-004 + D5-DES-STAT-TRIM-001 | Trim characterization (D5-DES) | Full-pop claims |
| SupergeoModel | DES-010 | REQUIRES_ADAPTER + REQUIRES_BRIDGE | `adapter_required` + `bridge_required` | D-SUIT-ADAPTER-REQUIRED; D-SUIT-BRIDGE-REQUIRED | F-GEO-003 + D5-DES-STAT-SUPERGEO-001 | Supergeo characterization | Original-geo claims |
| multi_test_groups | DES-011 | BLOCK | `contract_blocked` | D-SUIT-MULTICELL-METADATA-MISSING | cell_ids + shared-control policy | Per-cell planning docs | Pooled lift |
| PowerAnalysis | DES-014 | WARN | `planning_only` | D-SUIT-STAT-VALIDATION-REQUIRED | D5-DES-STAT-POWER-MDE-001 + MDE linkage | Planning rank | Causal readout; MMM |
| PowerContract | DES-015 | WARN | `planning_only` | D-SUIT-CONTRACT-BLOCKED | Join to DesignEvidence | Planning metadata | Causal claims |
| GeoExperimentDesign / geo_runner | DES-012–013 | BLOCK | `contract_blocked` | D-SUIT-CONTRACT-BLOCKED | Orchestration contract envelope | Internal dev | Governed orchestration |
| DesignEvidence / ExperimentEvidence | DES-026–027 | BLOCK | `contract_blocked` | D-SUIT-CONTRACT-BLOCKED | DesignOutputContract implementation | Schema reference | Suitability claims |
| Helpers (constraints, metrics, rng, …) | DES-016–025, 028–029 | NOT_EVALUATED | `helper_not_suitable` | D-SUIT-HELPER-NOT-SUITABLE | N/A | Internal use | Matrix anchor |
| DesignRegistry | DES-022 | n/a | `helper_not_suitable` | D-SUIT-HELPER-NOT-SUITABLE | N/A | Registry lookup | Suitability row |
| Bayesian (future) | — | DEFERRED | `deferred_future_method` | D-SUIT-FUTURE-METHOD-DEFERRED | BAYESIAN_METHOD_SPECIFICATION_001 | — | All |
| TROP (future) | — | DEFERRED | `deferred_future_method` | D-SUIT-FUTURE-METHOD-DEFERRED | TRIPLY_ROBUST audit program | — | All |
| SARIMAX (future) | — | DEFERRED | `deferred_future_method` | D-SUIT-FUTURE-METHOD-DEFERRED | TBR_SARIMAX_OPERATOR_CONTRACT_001 | — | All |

---

## 11. Contract-driven suitability

Missing required contract fields force **`contract_blocked`** (guardrail BLOCK per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) §12):

| Field | Suitability effect |
|-------|-------------------|
| `geometry_id` | `contract_blocked` — all geo designs today (IV-DES-001) |
| `forbidden_downstream_claims` | `contract_blocked` (IV-DES-002) |
| `concurrent_multi_experiment_compatibility` | `contract_blocked` (IV-DES-003) |
| Unit universe / eligible population | `contract_blocked` if undocumented |
| Treated/control labels | `contract_blocked` |
| `cell_ids` (multi-cell) | `contract_blocked` → D-SUIT-MULTICELL-METADATA-MISSING |
| `shared_control_policy` | `contract_blocked` |
| `block_ids` / `stratum_ids` / `pair_ids` | `contract_blocked` when family requires |
| Trim/thin `excluded_units` | `contract_blocked` |
| `supergeo_source_unit_map` | `contract_blocked` |
| Power/MDE linkage to DesignEvidence | `planning_only` until linked |

**Positive suitability requires contract completeness** — prerequisite for `suitable_after_validation` path.

---

## 12. Implementation-driven suitability

| Implementation status | Suitability category |
|----------------------|---------------------|
| `contract_complete` | May advance to `stat_validation_required` → future `suitable_after_validation` |
| `contract_mapping_partial` | `contract_blocked` + `stat_validation_required` |
| `contract_required` | `contract_blocked` |
| `adapter_required` | `adapter_required` |
| `implementation_ambiguous` | `implementation_ambiguous` |
| `helper_only` / `not_emitted` | `helper_not_suitable` |
| `superseded` / `historical` | `helper_not_suitable` or `blocked` |

Maps IV-DES-001–017 from [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md).

---

## 13. Statistical-validation-driven suitability

| Stat status | Suitability category |
|-------------|---------------------|
| `protocol_defined_not_executed` | `stat_validation_required` — **current default for all designs** |
| Future `validation_pass` | Eligible for `suitable_after_validation` subject to guardrails PASS |
| `pass_with_caveats` | `conditionally_suitable_with_caveats` |
| `mixed_requires_followup` | `research_only` |
| `fail` | `blocked` |
| `blocked` (protocol) | `blocked` |

**Strong positive suitability categories require executed `D5-DES-STAT-*` archives** — none exist at authoring.

---

## 14. Combination-matrix-driven suitability

Maps [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) §6:

| Matrix status | Suitability category |
|---------------|---------------------|
| `allowed_for_future_validation` | `stat_validation_required` |
| `restricted_requires_contract_fields` | `contract_blocked` |
| `restricted_requires_statistical_validation` | `stat_validation_required` |
| `adapter_required` | `adapter_required` |
| `bridge_required` | `bridge_required` |
| `blocked_due_to_*` | `blocked` |
| `blocked_for_pooled_claim` | `blocked` (D-SUIT-POOLED-CLAIM-BLOCKED) |
| `helper_not_matrix_candidate` | `helper_not_suitable` |
| `not_evaluated` | `deferred_future_method` or `research_only` |

Matrix statuses **feed** suitability categories; guardrails remain authoritative for BLOCK.

---

## 15. Guardrail-driven suitability

Maps [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) decisions:

| Guardrail | Suitability category |
|-----------|---------------------|
| PASS (precheck) | May evaluate `suitable_after_validation` after stat validation — **0 rows today** |
| WARN | `conditionally_suitable_with_caveats` or `research_only` or `planning_only` |
| BLOCK | `blocked` |
| REQUIRES_ADAPTER | `adapter_required` |
| REQUIRES_BRIDGE | `bridge_required` |
| REQUIRES_STATISTICAL_VALIDATION | `stat_validation_required` |
| DEFERRED | `deferred_future_method` |
| NOT_EVALUATED | `helper_not_suitable` |

This framework **consumes** guardrail decisions; it does not weaken them.

---

## 16. Geometry-driven suitability

Per [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) — suitability applies **only within validated geometry scope**:

| Geometry ID | Current design suitability scope |
|-------------|----------------------------------|
| `unit_panel_single_cell` | Tier-1 designs — `contract_blocked` until fields emitted; future per-cell SCM-JK scope |
| `aggregate_two_row` | Not produced by tier-1 designs without bridge — `blocked` for mismatch |
| `pooled_treated_control_panel` | Not produced by tier-1 without bridge — `blocked` |
| `multi_cell_per_cell` | DES-011 — `contract_blocked` until cell metadata |
| `pooled_multi_cell` | `blocked` — D-SUIT-POOLED-CLAIM-BLOCKED |
| `supergeo` | DES-010 — `bridge_required` + `adapter_required` |
| `trimmed_geometry` | DES-009 — `bridge_required`; full-pop `blocked` |
| `time_series_operator_geometry` | Future SARIMAX — `deferred_future_method` |

---

## 17. Readout-driven suitability

Per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md):

| Readout | Suitability |
|---------|-------------|
| Point-only | No uncertainty suitability; `research_only` at best |
| Prediction interval | Not causal — `blocked` for causal suitability |
| Forecast interval | Not causal uncertainty — `blocked` |
| Null decision | `stat_validation_required` + null semantics |
| Causal interval candidate | `stat_validation_required` |
| Causal interval validated in scope | Future `suitable_after_validation` only if all gates pass |

Power/MDE outputs: **`planning_only`** — never causal readout suitability.

---

## 18. Multi-cell / shared-control suitability

| Rule | Suitability |
|------|-------------|
| Per-cell suitability | Requires `cell_ids` + `shared_control_policy` — **missing today** → `contract_blocked` |
| Pooled/portfolio suitability | `blocked` without pooling bridge |
| Cross-cell metadata summary | Does not imply pooled causal suitability — `research_only` metadata |

DCM-006, DCM-007 from combination matrix.

---

## 19. Trim / thinning suitability

| Rule | Suitability |
|------|-------------|
| Trimmed-scope suitability | Possible only after adapter + metadata + `D5-DES-STAT-TRIM-001` |
| Original-population suitability | `blocked` without F-GEO-004 bridge |
| ThinningDesign (DES-005) | `implementation_ambiguous` until semantics ADR |

---

## 20. Supergeo suitability

| Rule | Suitability |
|------|-------------|
| Supergeo-scope suitability | After adapter + source map + distortion diagnostics + validation |
| Original-geo suitability | `blocked` without F-GEO-003 bridge |
| Concurrent multi-experiment suitability | `blocked` without bridge + concurrency metadata |

Evidence: D5-DES-SUPERGEO-001 (characterization only — not suitability promotion).

---

## 21. Power / MDE suitability

| Rule | Suitability |
|------|-------------|
| Planning-only | `planning_only` when geometry-aligned MDE documented |
| Causal readout suitability | `blocked` |
| CalibrationSignal / MMM suitability | `blocked` (D-SUIT-DOWNSTREAM-BLOCKED) |
| MDE not linked to DesignEvidence | `contract_blocked` component within `planning_only` |

Evidence: D5-POW-001e (geometry/null FPR — not design suitability proof).

---

## 22. Future Bayesian / TROP / SARIMAX suitability

| Family | Suitability | Prerequisites |
|--------|-------------|---------------|
| Bayesian | `deferred_future_method` | Method spec + impl + stat validation + posterior readout |
| TROP / triply robust | `deferred_future_method` | Audit program + nuisance/positivity/cross-fitting/inference validation |
| SARIMAX / Auto-SARIMAX | `deferred_future_method` | Operator contract + model selection + readout semantics |

D-SUIT-FUTURE-METHOD-DEFERRED

---

## 23. Downstream request type policy

| Request type | Policy at authoring |
|--------------|---------------------|
| Design exploration | `research_only` / doc review for non-blocked helpers; tier-1 `contract_blocked` but documentable |
| Experiment planning | Consume suitability categories; filter `blocked` first; `planning_only` for PowerAnalysis rank only |
| Production experiment recommendation | **BLOCKED** — all designs |
| Estimator/inference pairing | Requires design `stat_validation_required` clearance + [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) |
| TrustReport generation | **BLOCKED** — D-SUIT-DOWNSTREAM-BLOCKED |
| CalibrationSignal creation | **BLOCKED** |
| MMM calibration input | **BLOCKED** |
| LLM explanation | May describe suitability categories and reason codes; **cannot upgrade** category |

---

## 24. Suitability reason-code registry

| Code | Meaning |
|------|---------|
| D-SUIT-CONTRACT-BLOCKED | Required contract fields missing |
| D-SUIT-STAT-VALIDATION-REQUIRED | `D5-DES-STAT-*` not executed or not passed |
| D-SUIT-ADAPTER-REQUIRED | Non-standard design output path |
| D-SUIT-BRIDGE-REQUIRED | Geometry/population bridge ADR required |
| D-SUIT-GEOMETRY-MISMATCH | Design geometry ≠ requested estimator/readout geometry |
| D-SUIT-READOUT-MISMATCH | Readout semantics incompatible with claim |
| D-SUIT-IMPLEMENTATION-AMBIGUOUS | Thinning or population semantics unclear |
| D-SUIT-MULTICELL-METADATA-MISSING | cell_ids or shared-control policy absent |
| D-SUIT-POOLED-CLAIM-BLOCKED | Pooled/portfolio lift without ADR |
| D-SUIT-HELPER-NOT-SUITABLE | Helper/output object — not design anchor |
| D-SUIT-FUTURE-METHOD-DEFERRED | Bayesian/TROP/SARIMAX parked |
| D-SUIT-DOWNSTREAM-BLOCKED | TrustReport/CalibrationSignal/MMM/LLM/production blocked |

Maps from D-COMB-* and DGR-* per guardrails §24.

---

## 25. Master suitability table

| Row ID | Design / group | Category | Guardrail | Reason code(s) | Allowed current use | Blocked current use | Next artifact |
|--------|----------------|----------|-----------|----------------|---------------------|---------------------|---------------|
| DSU-001 | tier-1 (DES-001–006) | `contract_blocked` + `stat_validation_required` | BLOCK + REQUIRES_STAT | D-SUIT-CONTRACT-BLOCKED; D-SUIT-STAT-VALIDATION-REQUIRED | Doc review; validation planning | Production; TrustReport | DESIGN_CONTRACT_ENFORCEMENT_PLAN_001 |
| DSU-002 | StratifiedRandomization | `contract_blocked` | BLOCK | D-SUIT-CONTRACT-BLOCKED | Doc review | Stratum-aware inference | stratum_ids emission |
| DSU-003 | ThinningDesign | `implementation_ambiguous` | BLOCK | D-SUIT-IMPLEMENTATION-AMBIGUOUS | Doc review | Governed use | Thinning ADR |
| DSU-004 | QuickBlock / MatchedPair | `adapter_required` | REQUIRES_ADAPTER | D-SUIT-ADAPTER-REQUIRED | API smoke | Downstream pairing | Adapter + D5-DES-STAT-BLOCK-PAIR |
| DSU-005 | TrimmedMatchDesign | `adapter_required` + `bridge_required` | REQUIRES_ADAPTER + REQUIRES_BRIDGE | D-SUIT-ADAPTER-REQUIRED; D-SUIT-BRIDGE-REQUIRED | Trim D5 characterization | Full-pop claims | F-GEO-004 |
| DSU-006 | SupergeoModel | `adapter_required` + `bridge_required` | REQUIRES_ADAPTER + REQUIRES_BRIDGE | D-SUIT-ADAPTER-REQUIRED; D-SUIT-BRIDGE-REQUIRED | Supergeo D5 characterization | Original-geo | F-GEO-003 |
| DSU-007 | multi_test_groups | `contract_blocked` | BLOCK | D-SUIT-MULTICELL-METADATA-MISSING | Planning docs | Pooled lift | Cell metadata emission |
| DSU-008 | PowerAnalysis / PowerContract | `planning_only` | WARN | D-SUIT-STAT-VALIDATION-REQUIRED | Planning rank | Causal; MMM | D5-DES-STAT-POWER-MDE-001 |
| DSU-009 | Helpers DES-016–025 | `helper_not_suitable` | NOT_EVALUATED | D-SUIT-HELPER-NOT-SUITABLE | Internal | Matrix anchor | — |
| DSU-010 | tier-1 × SCM-JK combo | `stat_validation_required` | BLOCK + REQUIRES_STAT | D-SUIT-STAT-VALIDATION-REQUIRED | Future OC planning | Suitability claim | D5-DES-STAT-TIER1-001 |
| DSU-011 | pooled multi-cell | `blocked` | BLOCK | D-SUIT-POOLED-CLAIM-BLOCKED | — | All pooled claims | Pooling ADR |
| DSU-012 | Bayesian / TROP / SARIMAX | `deferred_future_method` | DEFERRED | D-SUIT-FUTURE-METHOD-DEFERRED | — | All | Method audit programs |
| DSU-013 | All designs × TrustReport | `blocked` | BLOCK | D-SUIT-DOWNSTREAM-BLOCKED | — | TrustReport | Product gates |
| DSU-014 | All designs × CalibrationSignal/MMM/LLM | `blocked` | BLOCK | D-SUIT-DOWNSTREAM-BLOCKED | Explain only | Product use | Suitability + validation |

**Downstream suitable designs:** **0**

---

## 26. Current allowed uses

Conservative allowed uses at authoring:

- Documentation and audit review  
- Research and validation **planning** (not execution claims)  
- Explaining blocked/restricted design status to humans or LLM  
- Internal API/registry smoke tests  
- D5-DES characterization evidence review (trim, supergeo, POW) — **not** suitability promotion  

**Blocked:** production decisioning · experiment recommendation · TrustReport · CalibrationSignal · MMM calibration input · LLM override of suitability category

---

## 27. Relationship to estimator/inference suitability

| Layer | Artifact | Decides |
|-------|----------|---------|
| **Design-side** (this artifact) | `DESIGN_SUITABILITY_FRAMEWORK_001` | Whether **design evidence** is structurally suitable (contract, geometry, population, adapter/bridge) |
| **Estimator/inference-side** | [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Whether **design × estimator × inference × geometry** readout path is suitable |
| **Final product suitability** | Future gates | Requires **both** layers + guardrails PASS + executed validation + product charter |

**Do not collapse** these artifacts. Estimator D5-STAT on reference designs does not satisfy design-side suitability.

---

## 28. Relationship to experiment planning orchestration

Per [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md):

1. Candidate ranking must **consume suitability categories** after guardrails filter  
2. `blocked` designs filtered first  
3. `adapter_required` / `bridge_required` are not normal ranked candidates  
4. `planning_only` limited to PowerAnalysis rank with geometry alignment  
5. LLM explains categories but **cannot override**  

Future `EXPERIMENT_RECOMMENDATION_CONTRACT_001` and `DESIGN_CANDIDATE_RANKING_POLICY_001` depend on this framework.

---

## 29. Future enforcement requirements

Governance sequence after this artifact:

1. **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`** ✅ **Accepted** — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md)  
2. **`DESIGN_CONTRACT_SCHEMA_001`** ✅ **Accepted** — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) — **necessary but insufficient** for positive suitability  
3. **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** ✅ **Accepted** — Phase 2 emission plan (**not implemented**)  
4. **`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`** ✅ **Accepted** — validation test plan (**tests not implemented**)  
5. **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001`** ✅ **Accepted** — validator architecture (**not implemented**)  
6. **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`** ✅ — validator module implemented  
7. **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001`** ✅ — emission wiring plan  
8. **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`** ✅ — runtime emission code  
9. **`DESIGN_CONTRACT_GOLDEN_FIXTURES_001`** ✅ — fixture stabilization  
10. **`DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001`** ✅ — runtime guardrail evaluator (metadata only; no downstream promotion)  
11. **`DESIGN_SUITABILITY_REASSESSMENT_001`** ✅ — post-runtime reassessment; metadata improved, downstream still blocked  
12. **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** *(follow-on)* — runtime enforcement per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) §27  

**Post-reassessment:** [`DESIGN_SUITABILITY_REASSESSMENT_001.md`](DESIGN_SUITABILITY_REASSESSMENT_001.md) ✅ — tier-1 metadata validity measurable; **0 downstream suitable designs**; verdict `design_metadata_suitability_improved_statistical_and_downstream_suitability_still_blocked`.

---

## 30. Governance gates

| Gate | Status |
|------|--------|
| Suitability framework defined | ✅ This artifact |
| Designs with metadata-valid tier-1 contracts | **4 fixture-backed + DES-001 path** (not production suitable) |
| Designs structurally suitable for production | ❌ **0** |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCKED** |
| Statistical validation executed | ❌ **0** `D5-DES-STAT-*` |
| Contract enforcement in code | ✅ Metadata guardrail evaluator; suitability still blocked |

This artifact does **not** validate or promote designs. It does **not** authorize causal claims or product layers. Contract enforcement and validation execution are required before any positive production suitability.

---

## 31. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_suitability_framework_defined_no_downstream_suitable_designs` (reassessment: `design_metadata_suitability_improved_statistical_and_downstream_suitability_still_blocked`) |
| Master suitability rows | 14 key policies (DSU-001–DSU-014) |
| Downstream suitable designs | **0** |
| Reason codes defined | 12 D-SUIT-* codes |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_GUARDRAILS_001\|DESIGN_COMBINATION_VALIDATION_MATRIX_001\|DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001" -n docs
grep -R "suitability\|suitable\|eligible\|PASS\|WARN\|BLOCK\|TrustReport\|CalibrationSignal\|MMM\|LLM" -n docs tests panel_exp
grep -R "D-COMB-\|DGR-\|blocked_due_to\|adapter_required\|bridge_required\|restricted_requires" -n docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "CompleteRandomization\|BalancedRandomization\|StratifiedRandomization\|ThinningDesign\|Rerandomization\|QuickBlock\|MatchedPair\|TrimmedMatch\|Supergeo\|greedy_match_markets" -n panel_exp tests docs
find docs -iname "*SUITABILITY*" -o -iname "*GUARDRAIL*" -o -iname "*COMBINATION*" -o -iname "*GEOMETRY*" -o -iname "*READOUT*"
```

**Code inspected (read-only):** `panel_exp/design/`, `geo_runner.py`, `evidence.py`, `spec.py`, design registry tests, validation doc tests, Track D design/D5 tests.

**D5 evidence reviewed (characterization only):** D5-STAT-SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference; D5-DES-TRIM, D5-DES-SUPERGEO; D5-POW-001e.

---

## 32. Roadmap

**Enforcement plan:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) ✅ **Accepted** — **positive suitability requires contract enforcement implementation** (Phases 1–3 minimum). All designs remain `contract_blocked` until emission + validation land.

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — **tier-1 designs remain `contract_blocked` until emission is implemented and validation tests pass**; 0 downstream suitable designs.

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — **positive suitability requires passing validation tests**; 0 downstream suitable designs.

**Validator implementation plan:** [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) ✅ **Accepted** — **positive suitability requires validator PASS plus separate statistical validation**; 0 downstream suitable designs.

**Golden fixtures:** ✅ shape stabilized. **Suitability remains blocked** — fixture stabilization ≠ statistical validation or downstream promotion.

**Tier-1 statistical execution:** ✅ [`D5_DES_STAT_TIER1_001_REPORT.md`](track_d/D5_DES_STAT_TIER1_001_REPORT.md) — 5 families characterized; verdict `tier1_designs_mixed_requires_method_specific_followup`; **0 downstream suitable**.

**Next artifact:** **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** (tier-1 recharacterization pending)

Then: adapter lanes · block/pair/trim design audits.

---

## 33. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Guardrails consumed | ✅ §15 |
| Combination matrix consumed | ✅ §14 |
| Suitability taxonomy defined | ✅ §6 |
| Current suitability assessment completed | ✅ §9–§10 |
| Downstream request policy defined | ✅ §23 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 34. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Suitability Accepted; next = contract enforcement plan |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | Framework consumes guardrail decisions |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix feeds suitability categories |
| [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Strong suitability requires D5-DES-STAT |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Blockers prevent downstream-ready suitability |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Contract completeness prerequisite |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Cross-link; distinct layers |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Suitability complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Suitability governance layer |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Remaining suitability blockers |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning consumes suitability |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane complete through suitability |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |

---

*DESIGN-SUITABILITY-FRAMEWORK-001 v1.1.1 — Accepted; post-runtime reassessment complete; 0 downstream suitable; next = D5-DES-STAT-TIER1-001.*
