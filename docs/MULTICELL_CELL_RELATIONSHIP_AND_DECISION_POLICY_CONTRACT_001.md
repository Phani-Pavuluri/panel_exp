# MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001

## 1. Purpose

Define governed semantic enums and derived flags for multi-cell design readouts so
DCM-006 does not over-block valid marginal platform/cell readouts and does not
over-authorize winner-selection, any-cell success, ranking, or pooled claims.

Implementation: `panel_exp/validation/multicell_decision_policy_contract_001.py`

## 2. Problem statement

`D5-TRUST-MULTICELL-PERCELL-INFERENCE-001` established that marginal per-cell SCM+JK
coverage is ~92.6% while familywise null type-I is ~27.2% under shared controls.
The statistical conclusion is directionally right but semantically incomplete:

- Multiplicity is required when cells are used for any-cell success, winner selection,
  ranking, global pass/fail, or pooled causal readout.
- Multiplicity is **not** automatically required when cells are parallel marginal
  business questions reported separately without ranking or global decisioning.

## 3. Non-goals

This contract does not solve multiplicity or simultaneous inference.
It prevents semantic over-claiming from multi-cell readouts.
It does not implement Bonferroni, Holm, or max-stat procedures.
It does not modify SCM, UnitJackknife, TBR, DID, AugSynth, or design assignment.
It does not perform full TrustReport eligibility reassessment.
It does not authorize TrustReport.

Marginal per-cell readouts are not equivalent to any-cell success, winner selection,
ranked selection, pooled causal readouts, or global TrustReport decisions.

## 4. Relationship to DCM-006

DCM-006 (`multicell_percell_multiplicity_unresolved`) remains **per-cell restricted**:
marginal per-cell readouts may be shown under `PARALLEL_MARGINAL_CELLS +
REPORT_EACH_CELL_ONLY` with shared-control warnings. Familywise decisioning,
winner selection, and pooled causal claims remain blocked pending
`INV-MULTICELL-MULTIPLICITY-CALIBRATION-001` and
`INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`.

## 5. Enum definitions

### `cell_relationship`

| Value | Meaning |
|-------|---------|
| `SINGLE_CELL` | One cell only; ordinary single-cell semantics |
| `PARALLEL_MARGINAL_CELLS` | Separate marginal business questions per cell |
| `COMPETING_CELLS` | Alternatives in one decision problem (spend levels, creatives, platforms) |
| `POOLED_COMPONENT_CELLS` | Components of one aggregate estimand |
| `UNKNOWN` | Fail closed to diagnostic-only |

### `decision_policy`

| Value | Meaning |
|-------|---------|
| `REPORT_EACH_CELL_ONLY` | Marginal per-cell reporting only |
| `DECLARE_ANY_CELL_SUCCESS` | Global success if any cell passes |
| `SELECT_OR_RANK_CELLS` | Choose or rank cells statistically |
| `POOL_CELLS` | Emit one aggregate multi-cell causal effect |

### `shared_control_policy` (optional metadata)

| Value | Meaning |
|-------|---------|
| `COMMON_CONTROL` | Shared donor/control pool across cells |
| `DISJOINT_CONTROL` | Disjoint donor pools |
| `PARTIAL_OVERLAP` | Partial donor overlap |
| `UNKNOWN` | Treat overlap as unresolved |

## 6. Derived governance flags

From `(cell_relationship, decision_policy)` plus optional shared-control metadata:

- `multiplicity_required`
- `selection_adjustment_required`
- `pooled_estimand_required`
- `shared_control_warning_required`
- `cross_cell_selection_allowed`
- `pooled_readout_allowed`
- `global_success_claim_allowed`
- `trustreport_global_decision_allowed` (always false in current contract)
- `diagnostic_only`
- `marginal_per_cell_readout_allowed`
- `allowed_claims` / `blocked_claims`
- `warnings`
- `readout_label`

## 7. Valid combinations

| Relationship | Policy | Marginal readout | Multiplicity | Notes |
|--------------|--------|------------------|--------------|-------|
| `PARALLEL_MARGINAL_CELLS` | `REPORT_EACH_CELL_ONLY` | Allowed | Not required | Shared-control warning when donors overlap |
| `COMPETING_CELLS` | `REPORT_EACH_CELL_ONLY` | Descriptive only | Not for display | Selection adjustment flagged |
| `COMPETING_CELLS` | `SELECT_OR_RANK_CELLS` | Descriptive only | Required | Selection blocked until corrected inference |
| `POOLED_COMPONENT_CELLS` | `POOL_CELLS` | Diagnostic display | Pooled estimand required | Pooled readout blocked until pooled inference |
| `SINGLE_CELL` | `REPORT_EACH_CELL_ONLY` | Allowed | Not required | Ordinary single-cell path |

## 8. Invalid / fail-closed combinations

- `SINGLE_CELL` + `SELECT_OR_RANK_CELLS`
- `SINGLE_CELL` + `DECLARE_ANY_CELL_SUCCESS`
- `SINGLE_CELL` + `POOL_CELLS`
- `POOLED_COMPONENT_CELLS` + `SELECT_OR_RANK_CELLS` without component-selection scope
- `UNKNOWN` + any non-diagnostic downstream use
- `PARALLEL_MARGINAL_CELLS` + `POOL_CELLS` (pooled causal not authorized)

## 9. Platform marginal example

```json
{
  "cell_relationship": "PARALLEL_MARGINAL_CELLS",
  "decision_policy": "REPORT_EACH_CELL_ONLY",
  "shared_control_policy": "COMMON_CONTROL"
}
```

Expected: marginal per-cell readout allowed; `multiplicity_required=false`;
`shared_control_warning_required=true`; winner/any-cell/pooled/TrustReport global
decision blocked.

## 10. Spend-level competing-arm example

```json
{
  "cell_relationship": "COMPETING_CELLS",
  "decision_policy": "SELECT_OR_RANK_CELLS",
  "shared_control_policy": "COMMON_CONTROL"
}
```

Expected: `multiplicity_required=true`; `selection_adjustment_required=true`;
winner selection blocked until corrected inference exists.

## 11. Segment marginal example

```json
{
  "cell_relationship": "PARALLEL_MARGINAL_CELLS",
  "decision_policy": "REPORT_EACH_CELL_ONLY"
}
```

Expected: separate segment claims only; no best-segment or any-segment success claim.

## 12. Pooled regional/national example

```json
{
  "cell_relationship": "POOLED_COMPONENT_CELLS",
  "decision_policy": "POOL_CELLS"
}
```

Expected: `pooled_estimand_required=true`; pooled readout blocked until pooled
inference exists; per-cell intervals insufficient for aggregate causal claim.

## 13. Shared-control warning policy

When `shared_control_policy` is `COMMON_CONTROL` or `PARTIAL_OVERLAP`, or
`control_overlap_fraction > 0`, set `shared_control_warning_required=true` and
append dependent-evidence-stream language to the readout label.

## 14. Readout labeling requirements

**PARALLEL_MARGINAL_CELLS + REPORT_EACH_CELL_ONLY:**

> Readout mode: marginal per-cell readout. Cells answer separate business questions.
> Cross-cell winner selection is not authorized. Any-cell success claims are not
> authorized. Pooled multi-cell causal readout is not authorized. Cells share
> control/donor references: interpret estimates as dependent evidence streams.

**COMPETING_CELLS + SELECT_OR_RANK_CELLS:**

> Readout mode: competing-cell selection. Per-cell marginal intervals are
> insufficient for selection. Multiplicity/selection-aware inference is required
> before choosing or ranking cells.

**POOLED_COMPONENT_CELLS + POOL_CELLS:**

> Readout mode: pooled component cells. A pooled estimand and pooled inference are
> required. Per-cell intervals alone do not authorize an aggregate causal claim.

## 15. TrustReport implications

This contract does not authorize TrustReport.
`trustreport_global_decision_allowed` remains false for all combinations.

## 16. Roadmap status

Registered as semantic guardrail after `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`.
Next core statistical lane: `D5-TRUST-STRATIFIED-SCM-JK-001`.

## 17. Residual issues and handoff

**Resolved:** `INV-MULTICELL-CELL-RELATIONSHIP-DECISION-POLICY-001` →
`SEMANTIC_GUARDRAIL_ADDED`

**Deferred (unchanged):**

- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`
- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`

**Next artifact:** `D5-TRUST-STRATIFIED-SCM-JK-001`
