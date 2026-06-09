# D5-STAT-MCELL-PERCELL-001 — Level B characterization (multi-cell per-cell execution)

**Artifact ID:** D5-STAT-MCELL-PERCELL-001
**Type:** Level B per-cell execution characterization — **not** pooled multi-cell causal inference
**Overall verdict:** `characterization_pass_with_caveats`

**Archive:** [`archives/D5_STAT_MCELL_PERCELL_001_results.json`](archives/D5_STAT_MCELL_PERCELL_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_mcell_percell_001.py`
**Regenerate:** `python -m panel_exp.validation.track_d_d5_stat_mcell_percell_001`

## 1. Purpose

Characterize **independent per-cell execution** for multi-cell designs using smoke-validated paths **MCELL-PERCELL-SCM-JK** and **MCELL-AUGSYNTH-POINT**. Verifies cell identity, method identity, one result per cell per method, and explicit **no-pooling** guardrails.

## 2. Relationship to prior D5-STAT artifacts

Builds on smoke callable evidence and Level B context from SCM-JK, AugSynth point, TBR aggregate, and DID bootstrap. Prior artifacts do **not** authorize pooled multi-cell causal readouts.

## 3. Relationship to suitability framework

`MCELL-PERCELL-SCM-JK` remains `suitability_candidate_pending_oc`. This artifact is structural/execution characterization only — no suitability tier movement.

## 4. Scope and exclusions

**In scope:** per-cell SCM-JK and AugSynth point on shared-control multi-cell assignments.

**Out of scope:** pooled causal effects, pooled intervals, cross-cell shrinkage, portfolio lift, supergeo, trim, TrustReport roles, CalibrationSignal, MMM, LLM, production promotion.

## 5. Multi-cell per-cell geometry definition

`greedy_match_markets` assignment with `n_test_grps` ∈ {2, 3}. Each cell `test_k` is evaluated on an isolated panel: **shared control + that cell's treated units only**. Other test cells are excluded from the readout panel.

## 6. Why per-cell is not pooled causal inference

World-level aggregates are **metadata summaries** (`metadata_summary_only: true`) — counts, rates, and per-method error summaries. No cross-cell causal pooling, no portfolio interval, no single pooled lift estimand.

## 7. Fixture world design

| world | cells | design |
|-------|-------|--------|
| `two_cell_clean_null` | 2 | null both cells |
| `two_cell_mixed_effect` | 2 | test_0 +8%, test_1 null |
| `three_cell_heterogeneous_effect` | 3 | 8% / 4% / 0% |
| `one_bad_cell` | 2 | trend-mismatch stress, thinner geos |
| `post_shock_one_cell` | 2 | +18 shock on test_1 treated post only |

12 replicates/world, fixed seeds.

## 8. Execution paths

- **MCELL-PERCELL-SCM-JK:** `SyntheticControlCVXPY(inference="UnitJackKnife")` per cell
- **MCELL-AUGSYNTH-POINT:** `AugSynthCVXPY(inference=None)` per cell

Percent injection is **cell-scoped** via `cell_effects` map.

## 9. Cell identity and method identity checks

- `cell_identity_preserved_rate`: **1.0** all worlds (no other test-cell units in panel)
- `method_identity_preserved_rate`: **1.0** all worlds
- Estimator classes verified: `SyntheticControlCVXPY`, `AugSynthCVXPY`

## 10. Results by world

| world | expected | observed | callable fail | cell ID | method ID | pooled effect | pooled interval |
|-------|----------|----------|---------------|---------|-----------|---------------|-----------------|
| `two_cell_clean_null` | 48 | 48 | 0.000 | 1.0 | 1.0 | false | false |
| `two_cell_mixed_effect` | 48 | 48 | 0.000 | 1.0 | 1.0 | false | false |
| `three_cell_heterogeneous_effect` | 72 | 72 | 0.000 | 1.0 | 1.0 | false | false |
| `one_bad_cell` | 48 | 48 | 0.000 | 1.0 | 1.0 | false | false |
| `post_shock_one_cell` | 48 | 48 | 0.000 | 1.0 | 1.0 | false | false |

**264** per-cell results total; **0** failures in failure register.

## 11. Cell-level failure behavior

No silent drops: `missing_cell_result_rate` **0** and `silent_pooling_detected` **false** in every world. Stress worlds remain callable/finite in this battery (cell-scoped failures would be recorded explicitly).

## 12. Silent pooling checks

`pooled_effect_emitted`: **false** · `pooled_interval_emitted`: **false** · `cross_cell_shrinkage_detected`: **false** across all worlds.

## 13. Forbidden-claim checks

All extended `forbidden_flags` false, including `pooled_causal_claim_allowed`, `pooled_interval_allowed`, `portfolio_effect_allowed`, `cross_cell_shrinkage_allowed`.

## 14. Overall verdict

`characterization_pass_with_caveats`

**Rationale:** Per-cell structural guardrails pass (identity, no pooling, full cell coverage). `post_shock_one_cell` shows elevated per-cell sign-error rates (~0.63) — characterization caveat, not authorization failure.

## 15. What this artifact does not authorize

No pooled multi-cell causal inference, portfolio effects, TrustReport/F-DECISION roles, CalibrationSignal/MMM, promotion, suitability, or governed uncertainty claims.

## 16. Recommended next artifacts

Per generated JSON `next_recommended_artifacts` and Layer 5 queue:

- **`D5-STAT-TBRRIDGE-INF-001`**

Post-Level-B enhancement synthesis: [`METHOD_ENHANCEMENT_ROADMAP_001.md`](../METHOD_ENHANCEMENT_ROADMAP_001.md) (lane **H** — MCELL guard hardening).

## 17. Roadmap and audit updates checked

Updated and verified:

- `METHOD_VALIDATION_PROGRAM_001.md`
- `ROADMAP_V4.md`
- `MIP_AUDIT_REGISTRY.md`
- `METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`
- `METHOD_COMBINATION_VALIDATION_MATRIX_001.md`
- `METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`
- `D5_STAT_DID_BOOTSTRAP_001_REPORT.md` (next-artifact section)

## 18. Guardrails

Per-cell only; metadata summaries non-causal; Level B characterization only; no estimator/inference/design code changes in this artifact.
