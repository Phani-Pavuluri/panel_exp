# STRATIFIED_POOLED_ESTIMAND_CONTRACT_001

**Artifact ID:** STRATIFIED_POOLED_ESTIMAND_CONTRACT_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/stratified_pooled_estimand.py`  
**Validation:** `panel_exp/validation/stratified_pooled_estimand_contract_001.py`  
**Summary:** [`archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json`](archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json)

---

## 1. Artifact ID

`STRATIFIED_POOLED_ESTIMAND_CONTRACT_001`

---

## 2. Purpose

Define the governed estimand contract layer for stratified and pooled GeoX readouts. Specifies when a stratified or pooled effect is a coherent causal estimand versus an invalid aggregation of heterogeneous cell/stratum effects.

---

## 3. Prior roadmap context

Built after `MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`, which blocked global/winner/pooled multi-cell decisions pending explicit multiplicity and shared-control dependence handling. This artifact addresses the stratified/pooled estimand gap identified in `INFERENCE_REPLACEMENT_SCOUT_001` and deferred investigation `INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001`.

---

## 4. Stratified vs pooled estimand problem

A pooled number is invalid if it is merely an average of available cell effects, a winner-selected aggregate, a post-hoc weighted summary, a mix of incompatible metrics/scales, or a global claim from per-cell marginal readouts. Per-cell marginal readouts do not imply a pooled or global causal effect.

---

## 5. Stratum-level readout boundary

`STRATUM_LEVEL_READOUT` is allowed only as stratum-level readout. Multiple compatible stratum readouts do not become a pooled effect. Warnings state: stratum-level readout only; not pooled/global inference; no aggregate causal claim.

---

## 6. Pooled estimand contract

A stratified aggregate can be a **contract candidate** (not production inference) only when all hold: compatible strata, common metric/effect scale/time window/target population, valid pooled estimand statement, pre-specified non-negative weights summing to 1, explicit heterogeneity policy with assessment, valid pooling inference, and resolved multiplicity/dependence where required.

---

## 7. Weighting contract

Allowed: pre-specified population, spend, exposure, or equal weights. Blocked: post-hoc effect-size weights, winner-selected weights, unknown weights, missing weights, ID mismatches, negative/non-finite/zero-sum weights.

---

## 8. Heterogeneity policy

If heterogeneity is not assessed, return `HETEROGENEITY_REVIEW_REQUIRED`. If material heterogeneity is detected with `BLOCK_IF_MATERIAL_HETEROGENEITY`, block pooling. If `REPORT_SEPARATELY`, return diagnostic/stratum-level only — not a pooled candidate.

---

## 9. Compatible vs incompatible strata

Block when strata differ in metric, effect scale, time window, target population, or estimand definitions. The `is_compatible` flag on each stratum is also enforced.

---

## 10. Multi-cell pooled effect boundary

`POOLED_MULTICELL_EFFECT` is blocked by default. Shared-control multicell geometry without dependence resolution remains blocked. This preserves the prior blocked status of pooled multi-cell effects.

---

## 11. Global / winner-selected blocked configurations

`GLOBAL_SUMMARY` and `WINNER_SELECTED_SUMMARY` use cases are blocked. Winner-selected summaries require selection-adjusted inference not provided here.

---

## 12. Required evidence for future promotion

Valid pooling inference, multiplicity or dependence resolution, pre-registered pooled estimand, heterogeneity assessment, and pre-specified heterogeneity policy.

---

## 13. Scenario results

34 deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact defines stratified/pooled estimand contracts only.  
Stratum-level readouts do not imply a pooled or global causal effect.  
Stratified aggregate summaries remain diagnostic unless a valid pooled estimand, weighting, heterogeneity, and pooling-inference contract exists.  
Pooled multi-cell effects, global summaries, and winner-selected summaries remain blocked.  
This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary authorization flags are `false`. Stratified SCM + JK aggregate remains diagnostic-only. No production p-values or causal confidence intervals are produced.

---

## 16. Final verdict

`stratified_pooled_estimand_contract_defined_no_downstream_authorization`

---

## 17. Recommended next artifact

**`AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`**

Alternatives: `MULTICELL_MAX_T_RESEARCH_SCOUT_001`, `CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.stratified_pooled_estimand_contract_001 --overwrite
```
