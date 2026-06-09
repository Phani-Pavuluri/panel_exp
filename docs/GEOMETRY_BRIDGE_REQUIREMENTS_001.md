# Geometry Bridge Requirements 001

**Document ID:** GEOMETRY-BRIDGE-REQUIREMENTS-001  
**Title:** Geometry Bridge Requirements 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` post-D5 geometry contract  
**Artifact type:** Documentation / governance — **no code changes**  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Companion:** [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) (readout / interval / coverage semantics)

**Guardrails:** No promotion · no TrustReport role · no CalibrationSignal/MMM/LLM authorization · no geometry generalization without bridge · no code changes in this artifact

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Geometry Bridge Requirements 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` post-D5 geometry contract |
| Artifact type | Documentation / governance |

This document is the second post-D5 enhancement artifact. It defines **which data layouts and assignment structures** may be consumed by which estimators and inference paths, and **what bridge is required** before any result may be compared, pooled, summarized across geometries, or considered for future product integration.

---

## 2. Purpose

[`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) standardizes **how outputs are interpreted** (effect scale, interval target, null vs directional rules). This artifact standardizes **where those outputs apply** — the experimental geometry.

Before any method may be upgraded, rerun for suitability framework v2, assigned a TrustReport role, or considered under future CalibrationSignal eligibility policy, validators and product layers must know:

- Which **geometry_id** was used for assignment, estimation, inference, and reporting.
- Whether a transition to another geometry is **direct**, **bridge-required**, or **blocked**.
- Whether pooled, trimmed, or supergeo summaries are **metadata-only** or **causal claims**.

This artifact does **not** promote any method.

---

## 3. Why this artifact exists

D5 Level B characterized methods on **specific geometries**. Silent generalization across incompatible layouts is the primary integration risk.

| D5 artifact | Geometry finding |
|-------------|------------------|
| **SCM-JK** | **`unit_panel_single_cell`** — unit-level donors + treated units; not aggregate 2-row. |
| **AugSynth point** | Same **`unit_panel_single_cell`**; point-only, no cross-geometry inference. |
| **TBR aggregate** | **`aggregate_two_row`** only — summed treated vs summed control; not unit-panel. |
| **DID bootstrap** | **`pooled_treated_control_panel`** with pooled DID readout; parallel-trends assumptions explicit; not a generic pooling bridge. |
| **MCELL per-cell** | **`multi_cell_per_cell`** — cell identity preserved; **no pooled causal/interval** outputs. |
| **TBRRidge inference** | **`unit_panel_single_cell`** with time-series operator readout; split/leakage caveats; Conformal blocked on multi-treated shape. |

Readout semantics are now defined; **geometry compatibility must be defined separately**. Without this contract, aggregate TBR recovery could be mistaken for unit-panel SCM evidence, or per-cell results could be silently pooled into portfolio lift.

---

## 4. Definitions

| Term | Definition |
|------|------------|
| **Geometry** | The full specification of experimental units, assignment structure, aggregation, and reporting layout consumed by design → estimator → inference. |
| **Unit** | Atomic geo/market/entity row in a panel (when unit-level geometry applies). |
| **Treated unit** | Unit assigned to treatment in the stated cell/window. |
| **Control unit** | Unit serving as donor or comparison arm per assignment policy. |
| **Donor unit** | Control unit eligible to contribute to counterfactual for a treated unit (SCM/TBRRidge). |
| **Cell** | Independent test arm in multi-cell designs (`test_0`, `test_1`, …). |
| **Market / geo** | Identifier for a unit in wide-panel data. |
| **Aggregate 2-row panel** | Panel with exactly two series rows (treated aggregate, control aggregate). |
| **Unit-panel single-cell** | Multiple unit rows; one test cell; shared control donors + treated units. |
| **Multi-cell per-cell** | Multiple cells; each analyzed on its own unit-panel sub-geometry. |
| **Pooled multi-cell** | Multiple cells combined into one causal estimand — **blocked** without bridge. |
| **Supergeo** | Constructed/combined geos treated as larger experimental units — bridge required. |
| **Trimmed geometry** | Geography after exclusion/trimming — target population changes; bridge for generalization. |
| **Shared control** | Control donors shared across treated units (or cells) under explicit policy. |
| **Donor pool** | Set of units eligible as donors for a given treated unit/cell. |
| **Assignment geometry** | Layout produced by design/assignment (who is treated, when, in which cell). |
| **Estimator input geometry** | Panel shape and unit labels the estimator consumes. |
| **Inference geometry** | Layout required by inference wrapper (e.g., multi-treated columns for TBRRidge). |
| **Reporting geometry** | Layout on which product readout is displayed. |
| **Bridge** | Documented artifact + validation defining a permitted transition between geometries with estimand mapping. |
| **Bridge-required transition** | Transition not allowed until a named bridge artifact is **Accepted** and validated. |
| **Blocked transition** | Transition forbidden regardless of bridge until implementation and policy change. |

---

## 5. Canonical geometry types

### A. `unit_panel_single_cell`

- One experiment cell; multiple units/markets.
- Explicit treated/control (and donor) labels.
- Used by SCM-JK, AugSynth point, TBRRidge (D5 scope), and related unit-panel paths.

### B. `aggregate_two_row`

- One treated aggregate time series + one control aggregate time series.
- Used by class TBR aggregate point (D5 scope).

### C. `pooled_treated_control_panel`

- Multiple treated units pooled into treated group; multiple controls into control group.
- Used by DID bootstrap characterization when `multiple_treated="pooled"` and parallel-trends assumptions are explicit.
- **Not** a license for arbitrary cross-method pooling.

### D. `multi_cell_per_cell`

- Multiple cells; each cell evaluated on independent unit-panel sub-geometry.
- Cross-cell outputs are **metadata** unless pooling bridge exists.

### E. `pooled_multi_cell`

- Multiple cells combined into one causal estimand.
- **Blocked** unless `bridge_artifact_id` names an accepted pooling bridge.

### F. `supergeo`

- Combined/constructed geos as experimental units.
- **Bridge required** before unit-level estimators or cross-geo pooling claims.

### G. `trimmed_geometry`

- Panel after geographic exclusion or trim rules.
- Claims apply to **trimmed target population** only unless bridge to original population.

### H. `time_series_operator_geometry`

- Time-series counterfactual setting: outcome series, exogenous/control series, forecast path.
- Relevant for TBRRidge, future SARIMAX/Auto-SARIMAX operators.
- Distinct from static unit-panel SCM geometry when operator semantics differ.

---

## 6. Required geometry metadata

Every future validation artifact must declare:

| Field | Description |
|-------|-------------|
| `geometry_id` | Canonical ID from §5 |
| `assignment_geometry` | Post-design layout |
| `estimator_input_geometry` | Panel passed to estimator |
| `inference_geometry` | Layout inference expects |
| `reporting_geometry` | Product/report layout |
| `n_units` | Total unit rows (if applicable) |
| `n_treated_units` | Count treated |
| `n_control_units` | Count control/donors |
| `n_cells` | Cell count |
| `cell_ids` | Cell identifiers |
| `donor_pool_definition` | Donor eligibility rule |
| `shared_control_policy` | Shared vs cell-private controls |
| `aggregation_policy` | Sum/mean/none before estimation |
| `pooling_policy` | Pooled vs per-unit vs per-cell |
| `trimming_policy` | None or documented exclusion |
| `supergeo_policy` | None or documented construction |
| `target_population` | Population estimand refers to |
| `generalization_claim_allowed` | Boolean — default **false** in D5 |
| `bridge_status` | `direct` · `bridge_required` · `blocked` |
| `bridge_artifact_id` | If bridged |
| `blocked_reason` | If blocked |

---

## 7. Allowed direct geometry mappings

**Direct characterization scope only** — not suitability, trust, or promotion.

| Source geometry | Method / path | Scope note |
|-----------------|---------------|------------|
| `unit_panel_single_cell` | SCM-JK (D5) | Level B unit-panel only |
| `unit_panel_single_cell` | AugSynth point (D5) | Point-only; no interval geometry |
| `aggregate_two_row` | TBR aggregate point (D5) | 2-row guard enforced |
| `multi_cell_per_cell` | Per-cell SCM-JK / AugSynth point (D5) | Independent cells only |
| `pooled_treated_control_panel` | DID + embedded bootstrap (D5) | Within DID characterization; no generic pooling export |
| `unit_panel_single_cell` + operator readout | TBRRidge KFold/TSKFold/BRB (D5) | Split/leakage caveats; Conformal blocked |

---

## 8. Blocked mappings

The following are **explicitly blocked** without an accepted bridge artifact:

| Blocked mapping | Reason |
|-----------------|--------|
| Unit-panel result → aggregate 2-row causal claim | Different estimand and donor structure |
| Aggregate TBR result → unit-panel causal claim | No disaggregation bridge |
| Multi-cell per-cell → pooled causal effect | D5: `pooled_causal_claim_allowed: false` |
| Multi-cell per-cell → pooled interval | D5: `pooled_interval_allowed: false` |
| Supergeo → unit-level SCM/TBRRidge without bridge | Experimental unit changed |
| Trimmed geometry → original full population | Target population changed |
| TBRRidge prediction/forecast bands → causal interval | Requires readout + geometry bridge ([`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) §12) |
| SARIMAX forecast geometry → causal geometry | Requires `TBR_SARIMAX_OPERATOR_CONTRACT_001` + bridge |
| Bayesian hierarchical pooling → cross-geo pooled claim | Requires `BAYESIAN_METHOD_SPECIFICATION_001` + geometry bridge |

---

## 9. Bridge-required transitions

Not permanently blocked, but **require a named bridge artifact** (Accepted + validation):

| Transition | Typical bridge artifact lane |
|------------|------------------------------|
| `multi_cell_per_cell` → `pooled_multi_cell` | Pooling ADR + `MCELL_*` bridge (future) |
| `unit_panel_single_cell` → `supergeo` | Supergeo bridge (future) |
| `trimmed_geometry` → original target population | Trim generalization bridge |
| `aggregate_two_row` → market/channel disaggregation | Aggregate disaggregation bridge |
| `pooled_treated_control_panel` → cell-specific causal readout | DID cell bridge (future) |
| `time_series_operator_geometry` → causal interval reporting | Operator contract + readout bridge |
| Bayesian hierarchical geometry → cross-cell pooled claim | Bayesian spec + bridge |
| Any geometry → future CalibrationSignal eligibility | Readout + geometry + suitability v2 |

---

## 10. Bridge artifact requirements

A valid geometry bridge artifact must specify:

| Requirement | Content |
|-------------|---------|
| Source / target geometry | Canonical IDs from §5 |
| Estimand before / after bridge | Named quantities |
| Aggregation rule | Sum, mean, weighted, etc. |
| Weighting rule | If applicable |
| Target population | Before and after |
| Donor/control inclusion | Who enters panel |
| Exclusion/trimming policy | Documented |
| Uncertainty propagation | How intervals propagate (or block) |
| Readout semantics reference | [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) |
| Validation worlds | Required D5/Level C worlds |
| Diagnostics | Pre-bridge checks |
| Failure/blocking conditions | When bridge aborts |
| Forbidden claims | Explicit negatives |
| Downstream eligibility | Still gated — bridge ≠ promotion |

---

## 11. Method-family implications

### A. SCM-JK

- D5 scope: **`unit_panel_single_cell` only**.
- Supergeo, trimmed, or pooled multi-cell use → **bridge required**.

### B. AugSynth point

- D5 scope: unit-panel point recovery only.
- Inference paths blocked until **inference bridge + geometry bridge** exist.

### C. TBR aggregate

- D5 scope: **`aggregate_two_row` only**.
- No unit-panel or multi-cell generalization without bridge.

### D. DID bootstrap

- **`pooled_treated_control_panel`** within DID characterization only.
- Not reusable as generic pooling bridge for SCM/TBR/MCELL.
- Cumulative readout mismatch governed by readout semantics artifact.

### E. MCELL per-cell

- Per-cell identity preserved; pooled causal/interval **blocked**.
- Cross-cell tables = **metadata_summary_only**.

### F. TBRRidge inference

- Declare **`time_series_operator_geometry`** or documented unit-panel operator layout.
- Split/leakage caveats remain; geometry support ≠ causal uncertainty support.

### G. Future SARIMAX / Auto-SARIMAX

- **`time_series_operator_geometry`** required.
- Forecast target ≠ causal target; auto-selection policy before causal reporting bridge.

### H. Future Bayesian

- Hierarchical geometry declared explicitly.
- Pooling/shrinkage **not** automatic valid bridge.

---

## 12. Multi-cell rules

| Rule | Requirement |
|------|-------------|
| **Per-cell result** | Causal/point/interval scoped to one `cell_id` |
| **Cross-cell metadata summary** | Allowed — counts, feasibility, diagnostics; **not** pooled causal |
| **Pooled causal effect** | **Blocked** without bridge |
| **Pooled interval** | **Blocked** without bridge |
| **Portfolio effect** | **Blocked** without bridge |
| **Shared-control handling** | Other test cells' units must not enter treated panel (D5 guard) |
| **Cell failure handling** | Record explicit failure; **no silent cell dropping** |
| **Pooled causal claim** | Forbidden in D5 and until bridge Accepted |
| **Pooled interval claim** | Forbidden in D5 and until bridge Accepted |

---

## 13. Supergeo rules

- **Supergeo** = experimental unit is a constructed aggregate of base geos (markets combined, regions merged, etc.).
- Changes **unit of analysis** → donor weights, support, and inference assumptions may change.
- **Required diagnostics:** construction map, base-geo membership, support overlap.
- **Status:** `bridge_required` for all estimator/inference use from unit-panel D5 evidence.
- **No silent supergeo promotion** in product readout.

---

## 14. Trimmed geometry rules

- Trimming/exclusion is a **geometry-changing** operation.
- Must record **target population before/after** trim.
- Must report **excluded units** and exclusion rule.
- **Allowed claims:** trimmed-scope estimands only.
- **Blocked:** generalization to original full population without bridge.

---

## 15. Aggregate vs unit-panel rules

| Concept | Aggregate 2-row | Unit-panel |
|---------|-----------------|------------|
| **Estimand** | ATT on summed treated vs summed control series | Unit-level counterfactual / ATT with donor weights |
| **Donor structure** | Single control aggregate series | Many control unit donors |
| **Interchangeable?** | **No** — different identification and support |
| **Aggregation allowed** | Upfront sum to two rows (TBR path) | Per-unit then optional declared aggregation |
| **Disaggregation blocked** | Aggregate → unit claims without bridge | Unit → aggregate without bridge |
| **Cross-geometry comparison** | Requires **bridge artifact** + matched readout semantics |

---

## 16. Geometry and readout interaction

Per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md):

1. **Readout target must match geometry target** — cumulative DID readout on pooled geometry ≠ unit-panel period-level SCM readout.
2. **Interval target must match reporting geometry** — intervals on aggregate series cannot validate unit-panel claims.
3. **Coverage target must match geometry** — scoring truth on wrong geometry = `blocked_due_to_readout_mismatch` (readout doc) or `blocked_geometry_mismatch` (this doc).
4. **Directional signal must name geometry** — high TBR aggregate directional FPR does not apply to SCM unit-panel null rules.
5. **Causal interval claim** requires **both** readout semantics support **and** geometry direct scope or accepted bridge.

---

## 17. Required metadata contract for future validation artifacts

| Field | Required |
|-------|----------|
| `artifact_id` | Yes |
| `method_family` | Yes |
| `estimator` | Yes |
| `inference_method` | Yes |
| `geometry_id` | Yes |
| `assignment_geometry` | Yes |
| `estimator_input_geometry` | Yes |
| `inference_geometry` | Yes |
| `reporting_geometry` | Yes |
| `bridge_status` | Yes |
| `bridge_artifact_id` | If bridged |
| `n_units` / `n_treated_units` / `n_control_units` | Yes when unit-panel |
| `n_cells` / `cell_ids` | When multi-cell |
| `donor_pool_definition` | When donor-based |
| `pooling_policy` | Yes |
| `aggregation_policy` | Yes |
| `trimming_policy` | Yes or `none` |
| `supergeo_policy` | Yes or `none` |
| `target_population` | Yes |
| `generalization_claim_allowed` | Yes — default false |
| `geometry_generalization_allowed` | Yes — default false (D5) |
| `pooled_causal_claim_allowed` | Yes — default false |
| `pooled_interval_allowed` | Yes — default false |
| `portfolio_effect_allowed` | Yes — default false |

---

## 18. Classification taxonomy

| Classification | Meaning |
|----------------|---------|
| `direct_characterization_scope` | D5/validation applied on this geometry only — **not** suitability |
| `bridge_required` | Use on other geometry requires accepted bridge |
| `blocked_geometry_mismatch` | Source/estimator/reporting geometry incompatible |
| `blocked_pooling_without_bridge` | Pooling claim without bridge |
| `blocked_trim_generalization` | Trimmed → full population without bridge |
| `blocked_supergeo_without_bridge` | Supergeo use without bridge |
| `metadata_summary_only` | Cross-cell or cross-unit summary — non-causal |
| `future_operator_geometry` | Planned operator layout — **not** current support claim |
| `future_bayesian_hierarchical_geometry` | Planned hierarchical layout — **not** current support claim |

---

## 19. Current D5 geometry backfill assessment

| D5 artifact | `geometry_id` | Classification | Notes |
|-------------|---------------|----------------|-------|
| **SCM-JK** | `unit_panel_single_cell` | `direct_characterization_scope` | No aggregate/MCELL pooling |
| **AugSynth point** | `unit_panel_single_cell` | `direct_characterization_scope` | Point-only |
| **TBR aggregate** | `aggregate_two_row` | `direct_characterization_scope` | 2-row guard; high null directional FPR (readout) |
| **DID bootstrap** | `pooled_treated_control_panel` | `direct_characterization_scope` (DID-limited) | Not generic pooling bridge |
| **MCELL per-cell** | `multi_cell_per_cell` | `direct_characterization_scope` + `metadata_summary_only` cross-cell | No pooled readout |
| **TBRRidge inference** | `unit_panel_single_cell` + operator readout | `direct_characterization_scope` with leakage caveats | No causal interval geometry claim; Conformal blocked |

**No row assigns** production readiness, trust, CalibrationSignal, MMM, or suitability.

---

## 20. Decision rules

| Decision | Allowed when | Blocked when |
|----------|--------------|--------------|
| **Direct geometry use** | `geometry_id` matches characterized scope; metadata complete | Mismatch or missing metadata |
| **Bridge required** | Transition listed §9; bridge artifact Accepted + validated | Bridge missing or rejected |
| **Geometry mismatch blocks method** | — | Estimator input ≠ declared geometry |
| **Pooling blocked** | — | No accepted pooling bridge |
| **Trim generalization blocked** | — | Trimmed → full population without bridge |
| **Supergeo blocked** | — | Without supergeo bridge |
| **TrustReport / CalibrationSignal / MMM / LLM** | **Blocked today** for all D5 artifacts | Until readout + geometry + suitability v2 + role assignment |

---

## 21. Relationship to future artifacts

This artifact **feeds**:

1. **`DESIGN_OUTPUT_CONTRACT_001`** — assignment geometry metadata from design layer  
2. **`TBR_READOUT_SEMANTICS_001`** — aggregate readout within `aggregate_two_row`  
3. **`TBRRIDGE_OPERATOR_CONTRACT_001`** — operator geometry + split policy  
4. **`SCM_JK_STRESS_NULL_CALIBRATION_001`**  
5. **`AUGSYNTH_INFERENCE_BRIDGE_001`**  
6. **`DID_BOOTSTRAP_CUMULATIVE_READOUT_FIX_001`**  
7. **`MCELL_PERCELL_GUARD_HARDENING_001`**  
8. **`TBR_SARIMAX_OPERATOR_CONTRACT_001`** · **`TBR_AUTO_SARIMAX_MODEL_SELECTION_POLICY_001`**  
9. **`BAYESIAN_METHOD_SPECIFICATION_001`**  
10. **Suitability framework v2** · **Matrix v2** · **Protocol v2**  
11. **Future TrustReport / CalibrationSignal / MMM integration**

---

## 22. Governance gates

- Does **not** promote any method.  
- Does **not** authorize TrustReport role.  
- Does **not** authorize CalibrationSignal eligibility.  
- Does **not** authorize MMM or LLM recommendation use.  
- Future eligibility requires: validation evidence + [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) + this geometry contract + suitability v2 + explicit role assignment.

---

## 23. Non-goals

- No estimator, design, or inference code changes  
- No new simulations or D5 archive regeneration  
- No validation harness changes  
- No method promotion or suitability claim  
- No governed-readout claim  
- No Bayesian, SARIMAX, supergeo, trim, or pooled multi-cell shortcuts  

---

## 24. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | GEOMETRY_BRIDGE_REQUIREMENTS_001 **complete**; next = DESIGN_OUTPUT_CONTRACT_001 |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Post-D5 sequence updated |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Status / next item adjusted |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Artifact registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Geometry controller cross-link |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability v2 dependency (readout + geometry) |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix v2 geometry bridge note |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Protocol v2 geometry declarations |

**D5 reports inspected:** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference.

---

*GEOMETRY-BRIDGE-REQUIREMENTS-001 v1.0.0 — Accepted post-D5 geometry contract; next enhancement = DESIGN_OUTPUT_CONTRACT_001.*
