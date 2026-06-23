# METHOD_READINESS_MATRIX_V2_001

**Artifact ID:** METHOD_READINESS_MATRIX_V2_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/method_readiness_matrix_v2.py`  
**Validation:** `panel_exp/validation/method_readiness_matrix_v2_001.py`  
**Summary:** [`archives/METHOD_READINESS_MATRIX_V2_001_summary.json`](archives/METHOD_READINESS_MATRIX_V2_001_summary.json)

---

## 1. Artifact ID

`METHOD_READINESS_MATRIX_V2_001`

---

## 2. Purpose

Consolidate the full method-validity spine into a single governed, test-backed readiness matrix across method family, estimator, inference mode, geometry, estimand scope, interval/tail semantics, readiness tier, usage boundary, blocked reasons, required next evidence, and downstream authorization flags.

---

## 3. Prior roadmap context

Built after `AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`, incorporating evidence from design-aware assignment generators through stratified/pooled estimand contracts and AugSynth point randomization integration.

---

## 4. Matrix schema

Each row defines `method_id`, family, estimator, inference mode, geometry, estimand scope, interval/tail semantics, readiness tier, usage boundary, allowed/forbidden outputs, blocked reasons, required next evidence, and evidence references.

---

## 5. Readiness tier definitions

Tiers: restricted research-mode usable, framework-level randomization candidate, per-cell marginal only, contract candidate, diagnostic-only, sensitivity-only, heterogeneity review required, multiplicity/dependence unresolved, research-deferred, blocked.

---

## 6. Usage boundary definitions

Boundaries: research-mode reporting only, framework-level candidate only, diagnostic summary only, sensitivity review only, per-cell only no global claim, contract only no inference authorization, blocked from downstream.

---

## 7. Restricted research-mode rows

`scm_unit_jackknife_restricted_research`, `did_bootstrap_restricted_research` — research-mode reporting only; no downstream authorization.

---

## 8. Framework-level candidate rows

`scm_treated_set_placebo_candidate`, `scm_studentized_treated_set_placebo_candidate`, `augsynth_point_randomization_candidate` — framework candidates only; no final p-value or causal CI.

---

## 9. Per-cell / contract candidate rows

`multicell_per_cell_marginal_only`, `stratified_pooled_estimand_contract_candidate` — per-cell or contract-level only; no global/winner/pooled inference authorization.

---

## 10. Diagnostic-only rows

SCM single-treated placebo null monitor, AugSynth JK, TBRRidge BRB/KFold/Placebo, stratified SCM+JK aggregate — diagnostic summary only.

---

## 11. Sensitivity-only rows

`scm_leave_one_treated_out_sensitivity_only` — sensitivity review only; not placebo inference substitute.

---

## 12. Multiplicity/dependence unresolved rows

`multicell_shared_control_unresolved`, `multicell_multiple_cell_family_adjustment_required` — blocked from downstream until dependence/multiplicity evidence exists.

---

## 13. Blocked rows

TBR aggregate geometry, TBRRidge JK, multicell global/winner/pooled, stratified post-hoc pooling, AugSynth JK production inference — not allowed for governed causal evidence.

---

## 14. Evidence reference map

Each row cites at least one artifact with `artifact_id`, optional `summary_json`/`report_path`, and `evidence_note` from the completed method-validity spine.

---

## 15. Scenario results

32+ deterministic scenarios — all pass under `--strict`. Matrix contains 25 required rows.

---

## 16. Downstream integration boundaries

This artifact defines the method-readiness matrix only.  
It does not authorize TrustReport expansion, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.  
Framework-level candidates are not final production p-values or causal confidence intervals.  
Per-cell marginal rows do not imply global, winner, or pooled multi-cell inference.  
Contract candidates are not inference authorization.  
Diagnostic-only and sensitivity-only rows are not governed causal evidence for downstream systems.

---

## 17. Safety checks

All matrix and summary authorization flags are `false`.

---

## 18. Final verdict

`method_readiness_matrix_v2_defined_no_downstream_authorization`

---

## 19. Recommended next artifact

**`CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001`**

Alternatives: `METHOD_READINESS_MATRIX_V2_AUDIT_001`, `AUGSYNTH_STUDENTIZED_RANDOMIZATION_INTEGRATION_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.method_readiness_matrix_v2_001 --overwrite
```
