# Design Combination Validation Matrix 001

**Document ID:** DESIGN-COMBINATION-VALIDATION-MATRIX-001  
**Title:** Design Combination Validation Matrix 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design × geometry × estimator × inference × readout × concurrency combinations  
**Artifact type:** Documentation / governance / combination matrix — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Inputs:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md)

**Guardrails:** No validation execution · no code changes · no design/estimator/inference promotion · no suitability assignment · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Combination Validation Matrix 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design × geometry × estimator × inference × readout combinations |
| Artifact type | Documentation / governance / combination matrix |

Fifth concrete design audit artifact. Defines governed **matrix statuses** for design-layer combinations before suitability, experiment recommendation, TrustReport, CalibrationSignal, MMM, or LLM use.

**This artifact defines matrix rules only. No combination has been validated or promoted.**

---

## 2. Purpose

This artifact answers:

1. Which **design × geometry × estimator × inference × readout** combinations may enter future validation?  
2. Which combinations are **restricted**, **adapter-required**, **bridge-required**, or **blocked**?  
3. What **reason codes** and **next artifacts** apply per row?  
4. How does the design layer extend [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) (estimator/inference Layer 5)?

**Matrix definition ≠ combination validation ≠ suitability approval.**

---

## 3. Why this artifact exists

| Gap | This artifact addresses |
|-----|-------------------------|
| Design names alone | Insufficient — must use DES inventory IDs + observed behavior |
| Method combination matrix v1 | 30 rows use **reference designs** only; lacks design-layer governance |
| Implementation validation | **0/31 contract-complete**; adapter-required and ambiguous designs |
| Statistical protocol | `protocol_defined_not_executed`; future `D5-DES-STAT-*` required |
| Literature alignment | G-DES-001–014 conceptual gaps affect pairing semantics |
| D5 characterization | SCM-JK, AugSynth, TBR, DID, MCELL, TBRRidge on **specific geometries** — not all design paths |

Without this matrix, unsafe design × estimator × inference pairings could be treated as normal OC or suitability candidates.

---

## 4. Scope

Includes matrix rules for:

- Registered designs and DES-001–DES-031 inventory rows  
- Canonical geometry IDs from [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)  
- Estimator/inference/readout groups from D5 Level B + readout semantics  
- Multi-cell / shared-control modes (`n_test_grps`, MCELL per-cell)  
- Trim/supergeo / bridge-required geometries  
- Power/MDE planning combinations  
- Future experiment recommendation candidate filtering  

**Evidence basis (not matrix validation):** D5-STAT-SCM-JK-001 · D5-STAT-AUGSYNTH-POINT-001 · D5-STAT-TBR-AGG-001 · D5-STAT-DID-BOOTSTRAP-001 · D5-STAT-MCELL-PERCELL-001 · D5-STAT-TBRRIDGE-INF-001 · D5-DES-TRIM-001 · D5-DES-SUPERGEO-001 · D5-POW-001e.

---

## 5. Non-goals

- No new validation execution or D5 archive regeneration  
- No design, estimator, or inference code changes  
- No combination promotion or production-ready claim  
- No suitability role assignment  
- No TrustReport, CalibrationSignal, MMM, or LLM authorization  

---

## 6. Matrix status taxonomy

| Status | Meaning |
|--------|---------|
| `allowed_for_future_validation` | Pairing auditable; may enter future OC after contract/stat preconditions |
| `restricted_requires_contract_fields` | Callable path exists but missing required contract metadata |
| `restricted_requires_statistical_validation` | Protocol defined; `D5-DES-STAT-*` or D5-STAT execution required |
| `adapter_required` | Non-standard design output; adapter before matrix promotion |
| `bridge_required` | Geometry/readout bridge ADR required |
| `blocked_due_to_geometry_mismatch` | Design geometry ≠ estimator/inference geometry |
| `blocked_due_to_readout_mismatch` | Readout semantics incompatible |
| `blocked_due_to_missing_contract_fields` | Hard contract blockers |
| `blocked_due_to_implementation_ambiguity` | Population/geometry semantics unclear |
| `blocked_for_pooled_claim` | Pooled/portfolio lift without bridge |
| `helper_not_matrix_candidate` | Helper/output object — not a combination row anchor |
| `not_evaluated` | Reserved |

**None of these statuses imply suitability-approved, promoted, or TrustReport-eligible.**

---

## 7. Required dimensions

Every governed matrix row must declare:

| Dimension | Description |
|-----------|-------------|
| `design_inventory_id` | DES-001–DES-031 |
| `design_name` | Registry/inventory name |
| `design_family` | Literature-aligned family |
| `implementation_status` | From implementation validation |
| `stat_protocol_status` | From statistical protocol eligibility |
| `geometry_id` | Canonical geometry |
| `target_population_status` | Full vs trimmed vs supergeo |
| `contract_status` | contract_mapping_partial / contract_required / missing |
| `estimator_family` | SCM, AugSynth, TBR, DID, TBRRidge, … |
| `inference_family` | UnitJackknife, point-only, bootstrap, KFold, … |
| `readout_semantics` | Point, interval, cumulative, directional |
| `interval_target` | If applicable |
| `multi_cell_mode` | single / per_cell / pooled |
| `shared_control_mode` | shared / independent / unspecified |
| `bridge_status` | direct / bridge_required / blocked |
| `combination_status` | Taxonomy from §6 |
| `blocked_reason_codes` | D-COMB-* registry §21 |
| `future_validation_required` | D5-DES-STAT-* or D5-STAT-* artifact |
| `downstream_status` | not_validated · not_suitability_approved |

---

## 8. Canonical design groups

| Group | DES rows | Notes |
|-------|----------|-------|
| Tier-1 geo-run dict-path | DES-001–006 | Assignment dict; contract-incomplete |
| Multi-cell / shared-control | DES-011 | `n_test_grps`; cell metadata partial |
| Stratified / blocking / pairing | DES-004, 007, 008 | Stratum/block/pair metadata gaps |
| Thinning / trimmed | DES-005, 009 | Ambiguity + bridge |
| Supergeo | DES-010 | MILP output; F-GEO-003 |
| Power / MDE | DES-014, 015 | Planning only; not causal readout |
| Output / helpers | DES-012–031 | Not matrix anchors |

---

## 9. Canonical estimator/inference/readout groups

| Group | D5 / protocol scope | Readout |
|-------|---------------------|---------|
| SCM + UnitJackknife | `unit_panel_single_cell` · D5-STAT-SCM-JK-001 | Causal interval candidate (mixed null) |
| AugSynth point-only | `unit_panel_single_cell` · D5-STAT-AUGSYNTH-POINT-001 | Point-only — no uncertainty claim |
| TBR aggregate point | `aggregate_two_row` · D5-STAT-TBR-AGG-001 | Point-only; high null directional FPR |
| DID + bootstrap | `pooled_treated_control_panel` · D5-STAT-DID-BOOTSTRAP-001 | Cumulative interval — target mismatch caveat |
| MCELL per-cell SCM-JK / AugSynth | `multi_cell_per_cell` · D5-STAT-MCELL-PERCELL-001 | Per-cell only; no pooling |
| TBRRidge KFold / TSKFold / BRB / Conformal | `unit_panel_single_cell` + operator · D5-STAT-TBRRIDGE-INF-001 | Mixed; Conformal blocked multi-treated |
| Bayesian (future) | Deferred | Posterior readout TBD |
| TROP / triply robust (future) | `research_only` | Parked audit program |
| SARIMAX / Auto-SARIMAX (future) | `time_series_operator_geometry` | Forecast ≠ causal interval |

All statuses **conservative** — D5 characterization ≠ combination promotion.

---

## 10. Geometry compatibility rules

Per [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md):

| Transition | Matrix rule |
|------------|-------------|
| `unit_panel_single_cell` design → unit-panel estimator | `allowed_for_future_validation` or `restricted_requires_contract_fields` |
| `aggregate_two_row` design → aggregate estimator | `allowed_for_future_validation` if aggregate assignment path exists |
| Aggregate design → unit-panel estimator | `blocked_due_to_geometry_mismatch` without bridge |
| Unit-panel design → aggregate estimator | `bridge_required` |
| `multi_cell_per_cell` → pooled readout | `blocked_for_pooled_claim` |
| `trimmed_geometry` → full-population readout | `bridge_required` |
| `supergeo` → original-geo unit-panel | `bridge_required` |
| `time_series_operator_geometry` → causal interval | `blocked_due_to_readout_mismatch` without operator bridge |

---

## 11. Readout compatibility rules

Per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md):

| Rule | Matrix effect |
|------|---------------|
| Point-only readout | Cannot authorize governed uncertainty |
| Prediction/forecast interval | Not causal interval |
| Forecast stability | Not causal uncertainty |
| Null decision | Requires explicit null-decision semantics |
| Directional sign-only | Not causal significance |
| Causal interval | `restricted_requires_statistical_validation` |

---

## 12. Contract-field compatibility rules

Hard blockers (repo-wide at authoring — **0** contract-complete designs):

| Missing field | Matrix status |
|---------------|---------------|
| `geometry_id` | `blocked_due_to_missing_contract_fields` |
| Treated/control labels | `blocked_due_to_missing_contract_fields` |
| `forbidden_downstream_claims` | `blocked_due_to_missing_contract_fields` |
| `concurrent_multi_experiment_compatibility` | `blocked_due_to_missing_contract_fields` |
| Cell IDs (multi-cell) | `blocked_due_to_missing_contract_fields` |
| Shared-control policy | `blocked_due_to_missing_contract_fields` |
| Block/stratum/pair IDs | `restricted_requires_contract_fields` |
| Trim/excluded-unit metadata | `blocked_due_to_missing_contract_fields` |
| Supergeo source map | `blocked_due_to_missing_contract_fields` |
| Power/MDE linkage (planning) | `restricted_requires_contract_fields` |

---

## 13. Tier-1 design matrix

Tier-1 geo-run dict-path designs (DES-001–006) vs estimator/inference groups:

| Design group | Estimator/inference/readout | Geometry | Status | Reason codes |
|--------------|----------------------------|----------|--------|--------------|
| tier-1 (greedy, complete, balanced, stratified, rerandomization) | SCM + UnitJackknife | `unit_panel_single_cell` | `restricted_requires_contract_fields` | D-COMB-MISSING-CONTRACT-FIELDS; D-COMB-STAT-VALIDATION-REQUIRED |
| tier-1 | AugSynth point-only | `unit_panel_single_cell` | `restricted_requires_contract_fields` | Same + point-only readout restriction |
| tier-1 | TBR aggregate point | `aggregate_two_row` | `blocked_due_to_geometry_mismatch` | D-COMB-GEOMETRY-BRIDGE-REQUIRED |
| tier-1 | DID bootstrap | `pooled_treated_control_panel` | `blocked_due_to_geometry_mismatch` | D-COMB-GEOMETRY-BRIDGE-REQUIRED |
| tier-1 | TBRRidge KFold/BRB/Conformal | `unit_panel_single_cell` | `restricted_requires_statistical_validation` | D-COMB-STAT-VALIDATION-REQUIRED; readout caveats |
| tier-1 | MCELL per-cell (n_test_grps>1) | `multi_cell_per_cell` | `restricted_requires_contract_fields` | D-COMB-SHARED-CONTROL-METADATA-MISSING |

**Expected:** Most unit-panel paths are future-validation candidates with contract restrictions; no downstream suitability.

---

## 14. Multi-cell / shared-control matrix

| Combination | Status | Rules |
|-------------|--------|-------|
| DES-011 per-cell × SCM-JK per cell | `restricted_requires_contract_fields` | cell_ids; shared-control policy |
| DES-011 per-cell × AugSynth point per cell | `restricted_requires_contract_fields` | Same |
| DES-011 × pooled SCM-JK | `blocked_for_pooled_claim` | D-COMB-POOLED-CLAIM-BLOCKED |
| DES-011 × portfolio lift | `blocked_for_pooled_claim` | F-MCELL-001 ADR |
| DES-011 × MCELL per-cell readout (cross-cell summary) | `restricted_requires_statistical_validation` | Metadata only across cells |

---

## 15. Stratified / blocking / pairing matrix

| Design | Combination | Status |
|--------|-------------|--------|
| StratifiedRandomization (DES-004) | SCM-JK without stratum metadata | `restricted_requires_contract_fields` |
| StratifiedRandomization | Block-aware inference (future) | `restricted_requires_statistical_validation` |
| QuickBlock (DES-007) | Any unit-panel estimator | `adapter_required` |
| MatchedPair (DES-008) | Any unit-panel estimator | `adapter_required` |
| QuickBlock / MatchedPair | Unadjusted i.i.d. inference | `blocked_due_to_readout_mismatch` | D-COMB-BLOCK-PAIR-INFERENCE-REQUIRED |

---

## 16. Trim / thinning matrix

| Design | Readout scope | Status |
|--------|---------------|--------|
| ThinningDesign (DES-005) | Unit-panel SCM-JK | `blocked_due_to_implementation_ambiguity` |
| ThinningDesign | Trimmed-scope only (future) | `restricted_requires_statistical_validation` |
| TrimmedMatchDesign (DES-009) | Trimmed-scope readout | `bridge_required` + `adapter_required` |
| TrimmedMatchDesign (DES-009) | Full-population SCM-JK | `bridge_required` | F-GEO-004 |

---

## 17. Supergeo matrix

| Combination | Status |
|-------------|--------|
| SupergeoModel × supergeo-scope readout | `bridge_required` + `adapter_required` |
| SupergeoModel × original-geo unit-panel SCM-JK | `blocked_due_to_geometry_mismatch` |
| SupergeoModel × concurrent multi-experiment | `blocked_due_to_missing_contract_fields` |
| SupergeoModel × unit-panel estimator without bridge | `bridge_required` | F-GEO-003 |

---

## 18. Power / MDE matrix

| Combination | Status |
|-------------|--------|
| PowerAnalysis × experiment planning (unit-panel design) | `restricted_requires_contract_fields` |
| PowerAnalysis aggregate MDE × unit-panel evidence | `blocked_due_to_geometry_mismatch` | D-COMB-POWER-GEOMETRY-MISMATCH |
| PowerAnalysis × causal readout authorization | `blocked_due_to_readout_mismatch` |
| PowerContract without DesignEvidence linkage | `restricted_requires_contract_fields` |

---

## 19. Future Bayesian / TROP / SARIMAX parking

| Method family | Status | Next artifacts |
|---------------|--------|----------------|
| Bayesian | `blocked_due_to_readout_mismatch` | BAYESIAN_METHOD_SPECIFICATION_001 + validation ladder |
| TROP / triply robust | `not_evaluated` | TRIPLY_ROBUST_* audit program |
| SARIMAX / Auto-SARIMAX | `blocked_due_to_readout_mismatch` | TBR_SARIMAX_OPERATOR_CONTRACT_001 + model-selection policy |

Reason code: **D-COMB-FUTURE-METHOD-DEFERRED**

---

## 20. Master combination matrix

Compact master table — key combinations (all `downstream_status`: not_validated · not_suitability_approved):

| Row ID | Design group | Geometry | Estimator / inference / readout | Status | Reason codes | Next artifact |
|--------|--------------|----------|--------------------------------|--------|--------------|---------------|
| DCM-001 | tier-1 (DES-001–006) | `unit_panel_single_cell` | SCM + UnitJackknife | `restricted_requires_contract_fields` | D-COMB-MISSING-CONTRACT-FIELDS; D-COMB-STAT-VALIDATION-REQUIRED | D5-DES-STAT-TIER1-001 + D5-STAT-SCM-JK |
| DCM-002 | tier-1 | `unit_panel_single_cell` | AugSynth point-only | `restricted_requires_contract_fields` | D-COMB-MISSING-CONTRACT-FIELDS | D5-DES-STAT-TIER1-001 |
| DCM-003 | tier-1 | `aggregate_two_row` | TBR aggregate point | `blocked_due_to_geometry_mismatch` | D-COMB-GEOMETRY-BRIDGE-REQUIRED | Aggregate design bridge |
| DCM-004 | tier-1 | `unit_panel_single_cell` | DID bootstrap | `blocked_due_to_geometry_mismatch` | D-COMB-GEOMETRY-BRIDGE-REQUIRED | Geometry bridge ADR |
| DCM-005 | tier-1 | `unit_panel_single_cell` | TBRRidge KFold/BRB | `restricted_requires_statistical_validation` | D-COMB-STAT-VALIDATION-REQUIRED | D5-STAT-TBRRIDGE-INF + operator contract |
| DCM-006 | multi-cell (DES-011) | `multi_cell_per_cell` | MCELL per-cell SCM-JK | `restricted_requires_contract_fields` | D-COMB-SHARED-CONTROL-METADATA-MISSING | D5-DES-STAT-MULTICELL-001 |
| DCM-007 | multi-cell | `pooled_multi_cell` | Pooled SCM-JK / lift | `blocked_for_pooled_claim` | D-COMB-POOLED-CLAIM-BLOCKED | Pooling ADR |
| DCM-008 | stratified (DES-004) | `unit_panel_single_cell` | SCM-JK | `restricted_requires_contract_fields` | D-COMB-MISSING-CONTRACT-FIELDS | stratum_ids emission |
| DCM-009 | QuickBlock / MatchedPair | `unit_panel_single_cell` | Block-aware inference | `adapter_required` | D-COMB-ADAPTER-REQUIRED | D5-DES-STAT-BLOCK-PAIR-001 |
| DCM-010 | QuickBlock / MatchedPair | `unit_panel_single_cell` | Unadjusted bootstrap | `blocked_due_to_readout_mismatch` | D-COMB-BLOCK-PAIR-INFERENCE-REQUIRED | — |
| DCM-011 | TrimmedMatch (DES-009) | `trimmed_geometry` | Trimmed-scope readout | `bridge_required` | D-COMB-GEOMETRY-BRIDGE-REQUIRED; D-COMB-ADAPTER-REQUIRED | F-GEO-004 + D5-DES-STAT-TRIM-001 |
| DCM-012 | TrimmedMatch | `unit_panel_single_cell` | Full-population SCM-JK | `bridge_required` | D-COMB-GEOMETRY-BRIDGE-REQUIRED | F-GEO-004 |
| DCM-013 | Supergeo (DES-010) | `supergeo` | Supergeo-scope readout | `bridge_required` | D-COMB-GEOMETRY-BRIDGE-REQUIRED; D-COMB-ADAPTER-REQUIRED | F-GEO-003 + D5-DES-STAT-SUPERGEO-001 |
| DCM-014 | Supergeo | `unit_panel_single_cell` | Original-geo SCM-JK | `blocked_due_to_geometry_mismatch` | D-COMB-GEOMETRY-BRIDGE-REQUIRED | F-GEO-003 |
| DCM-015 | Power/MDE (DES-014) | planning | Experiment planning rank | `restricted_requires_contract_fields` | D-COMB-POWER-GEOMETRY-MISMATCH | D5-DES-STAT-POWER-MDE-001 |
| DCM-016 | Thinning (DES-005) | `unit_panel_single_cell` | SCM-JK | `blocked_due_to_implementation_ambiguity` | D-COMB-IMPLEMENTATION-AMBIGUOUS | Thinning semantics ADR |
| DCM-017 | Bayesian (future) | TBD | Posterior readout | `not_evaluated` | D-COMB-FUTURE-METHOD-DEFERRED | BAYESIAN_METHOD_SPECIFICATION_001 |
| DCM-018 | TROP (future) | TBD | Triply robust | `not_evaluated` | D-COMB-FUTURE-METHOD-DEFERRED | TRIPLY_ROBUST audit program |
| DCM-019 | SARIMAX (future) | `time_series_operator_geometry` | Forecast interval | `blocked_due_to_readout_mismatch` | D-COMB-FUTURE-METHOD-DEFERRED | TBR_SARIMAX_OPERATOR_CONTRACT_001 |

**Combinations promoted:** **0**

---

## 21. Reason-code registry

| Code | Meaning |
|------|---------|
| D-COMB-MISSING-GEOMETRY-ID | `geometry_id` not emitted |
| D-COMB-MISSING-CONTRACT-FIELDS | Required contract envelope incomplete |
| D-COMB-ADAPTER-REQUIRED | Non-dict or non-standard design output |
| D-COMB-GEOMETRY-BRIDGE-REQUIRED | Geometry transition needs bridge ADR |
| D-COMB-READOUT-MISMATCH | Readout/interval semantics incompatible |
| D-COMB-STAT-VALIDATION-REQUIRED | Design or estimator OC not executed for scope |
| D-COMB-IMPLEMENTATION-AMBIGUOUS | Thinning or population semantics unclear |
| D-COMB-POOLED-CLAIM-BLOCKED | Pooled/portfolio lift without ADR |
| D-COMB-SHARED-CONTROL-METADATA-MISSING | cell_ids or shared-control policy absent |
| D-COMB-BLOCK-PAIR-INFERENCE-REQUIRED | Inference ignores block/pair structure |
| D-COMB-POWER-GEOMETRY-MISMATCH | MDE geometry ≠ final readout geometry |
| D-COMB-FUTURE-METHOD-DEFERRED | Bayesian/TROP/SARIMAX parked |

---

## 22. Downstream consumption policy

| Policy | Rule |
|--------|------|
| `allowed_for_future_validation` | **Not** production-allowed |
| `restricted_*` | Planning/characterization only with caveats |
| `blocked_*` / `bridge_required` / `adapter_required` | No normal candidate ranking |
| Promotion | Requires executed validation + guardrails + suitability |
| TrustReport / CalibrationSignal / MMM / LLM | **Blocked** by this artifact |

---

## 23. Relationship to future design guardrails

[`DESIGN_GUARDRAILS_001`](DESIGN_GUARDRAILS_001.md) converts this matrix into **enforceable** PASS/WARN/BLOCK policies referencing D-COMB-* reason codes and `forbidden_downstream_claims`.

---

## 24. Relationship to design suitability framework

[`DESIGN_SUITABILITY_FRAMEWORK_001`](DESIGN_SUITABILITY_FRAMEWORK_001.md) ✅ **Accepted** consumes:

- Design output contract status  
- Inventory / literature / implementation statuses  
- Statistical validation outcomes (`D5-DES-STAT-*`)  
- **This matrix** combination statuses → suitability categories (§14 mapping)  
- Guardrail policies  

**Matrix statuses feed suitability categories** per [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) §14. Suitability rows may not advance on `blocked_*` or `adapter_required` without resolution.

---

## 25. Relationship to experiment planning

Per [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md):

- Candidate ranking must **filter blocked rows first**  
- Adapter-required and bridge-required rows are **not normal candidates**  
- LLM may explain blocks but **cannot override** matrix status  

---

## 26. Governance gates

| Gate | Status |
|------|--------|
| Matrix defined | ✅ This artifact |
| Combinations validated | ❌ None |
| Combinations promoted | ❌ None |
| Suitability assigned | ❌ None |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ Blocked |

---

## 27. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_combination_matrix_defined_no_combinations_promoted` |
| Master rows defined | 19 key combinations (+ DES inventory rules) |
| Combinations promoted | **0** |
| Suitability-approved combinations | **0** |

---

## 28. Roadmap

**Guardrails:** [`DESIGN_GUARDRAILS_001`](DESIGN_GUARDRAILS_001.md) ✅ **Accepted** — converts matrix statuses and D-COMB-* reason codes into PASS/WARN/BLOCK policy. **Runtime evaluator:** [`DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001`](DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md) ✅ — consumes contract metadata; **does not auto-upgrade matrix row statuses**. **Reassessment:** [`DESIGN_SUITABILITY_REASSESSMENT_001`](DESIGN_SUITABILITY_REASSESSMENT_001.md) ✅ — metadata validity ≠ matrix promotion.

**Enforcement plan:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) ✅ **Accepted** — **matrix statuses remain advisory until contract fields are emitted and validated** in code.

**Schema:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) ✅ — **matrix statuses remain advisory until contract fields are emitted and validated** per schema.

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — matrix remains advisory until fields emitted and validated.

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — matrix integration tests planned; matrix remains advisory until validator passes.

**Next artifact:** **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001`**

Suitability framework ✅ [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) consumes matrix statuses.

---

## 29. Completion checklist

| Item | Status |
|------|--------|
| Prior artifacts inspected | ✅ |
| DES inventory consumed | ✅ |
| Implementation statuses consumed | ✅ |
| Statistical protocol statuses consumed | ✅ |
| Geometry bridge consumed | ✅ |
| Readout semantics consumed | ✅ |
| Method combination matrix cross-linked | ✅ |
| Master matrix defined | ✅ §20 |
| Reason codes defined | ✅ §21 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 30. Search methodology (2026-06-10)

```bash
grep -R "DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001\|DESIGN_IMPLEMENTATION_VALIDATION_001\|DESIGN_COMBINATION_VALIDATION_MATRIX_001" -n docs
grep -R "GEOMETRY_BRIDGE_REQUIREMENTS_001\|INFERENCE_READOUT_SEMANTICS_001\|METHOD_COMBINATION_VALIDATION_MATRIX_001" -n docs
grep -R "SCM\|UnitJackknife\|AugSynth\|TBR\|DID\|TBRRidge\|KFold\|Conformal\|BRB\|Placebo" -n docs panel_exp tests | head -80
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "CompleteRandomization\|BalancedRandomization\|StratifiedRandomization\|ThinningDesign\|Rerandomization\|QuickBlock\|MatchedPair\|TrimmedMatch\|Supergeo\|greedy_match_markets" -n panel_exp tests docs | head -40
find docs -iname "*D5*STAT*" -o -iname "*D5*DES*" -o -iname "*D5*POW*" -o -iname "*COMBINATION*" -o -iname "*GEOMETRY*" -o -iname "*READOUT*"
find tests/track_d -iname "*d5*" -o -iname "*design*" -o -iname "*pow*"
poetry run python -c "from panel_exp.design.registry import get_design_registry; print(sorted(get_design_registry().list_names()))"
```

**Contract field grep:** **0 matches** in `panel_exp/` for `geometry_id`, `forbidden_downstream_claims`, `concurrent_multi_experiment_compatibility`, `shared_control_policy`.

---

## 31. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Combination matrix Accepted; next = guardrails |
| [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Matrix consumes protocol eligibility |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Matrix consumes impl statuses |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | Matrix uses literature semantics |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | DES IDs as row identifiers |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Contract fields or blocked |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability blocked until matrix + guardrails |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Design-layer extension cross-link |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Design protocol + matrix cross-link |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Matrix complete; next = guardrails |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Design combination prerequisite |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Combination blockers |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Ranking consumes matrix |

---

*DESIGN-COMBINATION-VALIDATION-MATRIX-001 v1.0.5 — Accepted; validation test plan defined; next = DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.*
