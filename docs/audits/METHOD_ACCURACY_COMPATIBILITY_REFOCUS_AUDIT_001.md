# METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001

**Artifact ID:** METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/method_accuracy_compatibility_refocus_audit_001.py`  
**Summary:** [`../track_d/archives/METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001_summary.json`](../track_d/archives/METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001_summary.json)

---

## 1. Artifact ID

`METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001`

---

## 2. Purpose

Convert the current method-readiness state into a concrete, ranked remediation backlog for improving designs, estimators, and inference. Pause downstream drift and refocus on method accuracy and compatibility.

---

## 3. Why this audit exists

Method-readiness matrix v2 and CalibrationSignal method-gate draft defined classifications but downstream schema/ingestion work was advancing ahead of empirical null calibration, estimator adapters, and inference remediation. This audit stops that drift.

---

## 4. Current state summary

25 method-readiness rows span restricted research-mode, framework candidates, per-cell/contract candidates, diagnostic/sensitivity, multiplicity unresolved, and blocked paths. Framework candidates exist for SCM treated-set placebo, SCM studentized placebo, and AugSynth point randomization — but empirical null calibration is not established. TBRRidge and AugSynth JK remain diagnostic or blocked. Multi-cell shared-control dependence is unresolved.

---

## 5. Evidence sources inspected

Method Readiness Matrix V2, CalibrationSignal method-gate draft, stratified/pooled estimand contract, multicell multiplicity, SCM/AugSynth randomization integrations, studentized placebo rank, method-specific randomization validation, and associated summary JSON archives.

---

## 6. Drift assessment

Downstream drafts (CalibrationSignal schema alignment, TrustReport expansion, MMM, LLM) were queued before P0 null calibration and adapter contracts completed. Governance layers outpaced empirical method evidence.

---

## 7. Refocus decisions

1. Pause downstream schema, ingestion, and decisioning artifacts.
2. Prioritize empirical null calibration for candidate randomization methods.
3. Prioritize estimator/statistic adapter compatibility for SCM and AugSynth.
4. Treat TBRRidge inference as remediation-or-retirement, not incremental governance.
5. Treat shared-control multicell as research prototype work, not downstream-ready.
6. Keep AugSynth JK diagnostic-only until retired or replaced.
7. Keep all CalibrationSignal / TrustReport / MMM / LLM flags false.

---

## 8. Work bucket definitions

| Bucket | Meaning |
|--------|---------|
| null_calibration | Empirical type-I / tail-fraction calibration under null |
| estimator_statistic_adapter | Shared observed/pseudo statistic comparability |
| inference_remediation | Replace or fix broken inference paths |
| design_compatibility | Assignment generator stress and degeneracy |
| geometry_estimand_compatibility | Geometry/estimand alignment |
| multicell_dependence_research | Shared-control / max-T research |
| pooling_heterogeneity_research | Stratified pooling and heterogeneity |
| retire_or_permanent_block | Retirement or permanent block |
| downstream_pause | Pause downstream until checkpoints pass |

---

## 9. P0 backlog

- `STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001`
- `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`
- `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`

---

## 10. P1 backlog

- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `AUGSYNTH_JK_RETIREMENT_OR_REPLACEMENT_AUDIT_001`

---

## 11. P2 backlog

- `STRATIFIED_POOLING_INFERENCE_SCOUT_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

---

## 12. P3/deferred backlog

- `DCM_009_019_ADAPTER_DISPOSITION_AUDIT_001`

---

## 13. Per-method issue table

| Item ID | Affected methods | Current status | Root issue | Work bucket | Fixability | Priority | Required evidence | Recommended next artifact | Stop/go criteria |
|---------|------------------|----------------|------------|-------------|------------|----------|-------------------|---------------------------|------------------|
| studentized_randomization_null_calibration | scm_studentized, studentized_placebo_rank | framework candidate | type-I not validated under null sims | null_calibration | needs_empirical_evidence | P0 | null grid, assignment coverage, type-I, tail calibration | STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001 | continue if type-I controlled; else diagnostic-only |
| scm_treated_set_placebo_null_calibration | scm_treated_set_placebo_candidate | framework candidate | empirical null not established | null_calibration | needs_empirical_evidence | P0 | null sims, tail under null | SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001 | continue if tails behave; else framework-only |
| scm_augsynth_statistic_adapter_contract | scm/augsynth candidates | framework candidate | statistic-first without shared adapter | estimator_statistic_adapter | fixable_now | P0 | common interface, recomputation contract | SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001 | continue if comparable; block if not |
| multicell_max_t_research_scout | multicell unresolved/blocked | multiplicity unresolved | FWER proxy insufficient | multicell_dependence_research | research_prototype | P1 | joint null, max-T, dependence sim | MULTICELL_MAX_T_RESEARCH_SCOUT_001 | continue if dependence prototype credible |
| tbrridge_inference_remediation_or_retirement | tbrridge diagnostic/blocked | diagnostic/blocked | prior null/type-I failures | inference_remediation | likely_retire | P1 | failure inventory, null reruns | TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001 | retire or remediate with evidence |
| augsynth_jk_retirement_or_replacement | augsynth_jk diagnostic/blocked | diagnostic-only | JK not production path | retire_or_permanent_block | permanent_block | P1 | diagnostic value, replacement path | AUGSYNTH_JK_RETIREMENT_OR_REPLACEMENT_AUDIT_001 | retire unless diagnostic justified |
| stratified_pooling_inference_scout | stratified pooled/heterogeneity | contract/diagnostic | pooling inference unvalidated | pooling_heterogeneity_research | research_prototype | P2 | weights, heterogeneity rule | STRATIFIED_POOLING_INFERENCE_SCOUT_001 | diagnostic until evidence |
| design_assignment_generator_stress_tests | design-based candidates | design candidate | generators untested for degeneracy | design_compatibility | fixable_now | P2 | support size, degeneracy checks | DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001 | block if degeneracy |
| dcm_009_019_adapter_disposition | dcm adapters deferred | research_deferred | adapters lack disposition | retire_or_permanent_block | likely_retire | P3 | qualification inventory | DCM_009_019_ADAPTER_DISPOSITION_AUDIT_001 | retire or explicit plan |
| downstream_work_pause_marker | CalibrationSignal, TrustReport, MMM, LLM | downstream pause | downstream ahead of methods | downstream_pause | permanent_block | P0 | P0 checkpoints | none until checkpoints pass | resume after explicit decision |

---

## 14. Recommended first implementation artifact

**`STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001`**

Alternative: `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`

Do not recommend CalibrationSignal schema alignment as next.

---

## 15. Stop/go criteria

Each backlog item defines explicit stop/go criteria. P0 null calibration must pass before framework candidates advance. Downstream work resumes only after P0 checkpoints and updated readiness matrix.

---

## 16. Downstream pause boundary

Paused: `CALIBRATION_SIGNAL_SCHEMA_ALIGNMENT_DRAFT_001`, `TRUSTREPORT_METHOD_GATE_DRAFT_001`, `MMM_INGESTION_DRAFT_001`, `LLM_DECISIONING_DRAFT_001`, live API/scheduler work.

---

## 17. Safety checks

All authorization flags false. No item authorizes CalibrationSignal, TrustReport, MMM, LLM, production decisioning, live API, scheduler, or budget optimization.

---

## 18. Final verdict

`refocus_on_method_accuracy_and_compatibility`

This audit pauses downstream schema, ingestion, and decisioning work. The next phase should focus on empirical method calibration, estimator/statistic adapter compatibility, inference remediation, and retirement decisions. This audit does not authorize CalibrationSignal, TrustReport expansion, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

Regenerate:

```bash
poetry run python -m panel_exp.validation.method_accuracy_compatibility_refocus_audit_001 --overwrite
```
