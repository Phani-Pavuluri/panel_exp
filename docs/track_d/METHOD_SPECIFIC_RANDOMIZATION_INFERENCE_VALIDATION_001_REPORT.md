# METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001

**Artifact ID:** METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/method_specific_randomization.py`  
**Validation:** `panel_exp/validation/method_specific_randomization_inference_validation_001.py`  
**Summary:** [`archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json`](archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json)

---

## 1. Artifact ID

`METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001`

---

## 2. Purpose

Move from generic treated-set/randomization/placebo framework semantics into **method-specific readiness classification** for SCM, DID, AugSynth, TBRRidge, TBR, and related estimators.

This artifact validates whether observed and pseudo-treated-set statistics can be validly compared under the design-aware assignment framework — and if not, why paths are diagnostic-only, sensitivity-only, research-deferred, or blocked.

---

## 3. Prior roadmap context

Completed spine:

- Design-aware assignment generators
- Multi-treated treated-set placebo framework
- SCM placebo governed semantics
- Method roadmap alignment audit (downstream integration blocked)

---

## 4. Relationship to design-aware assignment generators

`AssignmentRole` from `assignment_generators.py` gates design-based vs falsification-only vs blocked pseudo-assignments. Method-specific validation **cannot** upgrade falsification-only designs to candidates.

---

## 5. Relationship to treated-set placebo framework

`treated_set_placebo.py` supplies framework-level placebo rank and empirical tail fraction (not production p-values). This artifact classifies **which estimators** may use that framework under comparable statistic contracts.

---

## 6. Relationship to SCM placebo governed semantics

`scm_placebo_semantics.py` defines SCM-specific use cases. `classify_method_from_scm_semantics()` bridges SCM semantics into the method-specific matrix without forcing fragile coupling for other estimators.

---

## 7. Method-specific validation contract

`validate_method_randomization_inference(spec)` returns:

- `RandomizationValidationRole` — candidate, falsification, sensitivity, diagnostic, deferred, blocked
- `MethodSpecificDecision` — parallel decision enum
- `required_next_evidence` — e.g. TBRRidge replacement, AugSynth estimand bridge
- Governance flags (all downstream authorization **false**)

A method is a **design-based randomization candidate** only when:

- Assignment role is design-based
- Sufficient valid pseudo-assignments
- Observed and pseudo statistics exist and use the **same statistic definition**
- Geometry is compatible
- Method is not terminally diagnostic/blocked
- No platform overclaim requests

---

## 8. Method readiness matrix

See `build_method_randomization_readiness_matrix()` and summary JSON `method_readiness_matrix`.

---

## 9. Candidate configurations

| Method | Statistic | Geometry | Conditions |
|--------|-----------|----------|------------|
| SCM | signed/relative effect | multi-treated | design-based assignments + comparable stats |
| DID | signed effect | multi-treated | design-based + comparable stats (not bootstrap-only) |
| AugSynthCVXPY | point statistic | multi-treated | design-based + comparable stats |
| SCM/DID | per-cell marginal | multicell shared-control | no global/winner claim |

All candidates carry warning: **framework candidate only — not final production p-value or CI**.

---

## 10. Diagnostic-only configurations

| Method | Path |
|--------|------|
| SCM single-treated placebo | null-monitor / falsification |
| DID bootstrap-only | no randomization validity from bootstrap alone |
| AugSynth JK | estimand/scale bridge open |
| TBRRidge BRB/KFold/Placebo | terminal diagnostic paths |
| TBRRidge JK | blocked (known failure mode) |

---

## 11. Research-deferred configurations

| Method | Reason |
|--------|--------|
| BayesianTBR | no method-specific validation evidence |
| SyntheticDID | adapter DCM-009+ insufficient evidence |
| TROP | adapter insufficient evidence |

---

## 12. Blocked configurations

- TBR aggregate geometry mismatch
- Missing or mismatched observed/pseudo statistics
- Falsification-only or blocked assignment roles (for candidate claims)
- Multicell global/winner/pooled claims
- DCM-009–019 adapter qualification requests
- All platform overclaims (TrustReport, CalibrationSignal, MMM, LLM, production, live API, scheduler, budget)

---

## 13. Scenario results

29 deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact validates method-specific randomization inference readiness only.  
It does not produce final production p-values or confidence intervals.  
It does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary authorization flags are `false`. No production p-value or CI semantics. Placebo tail fractions remain framework-level diagnostics.

---

## 16. Final verdict

`method_specific_randomization_inference_validated_no_downstream_authorization`

---

## 17. Recommended next artifact

**`SCM_TREATED_SET_PLACEBO_INTEGRATION_001`** — wire SCM estimator statistics into the treated-set placebo framework under these semantics.

Alternatives if integration blockers emerge:

- `STUDENTIZED_PLACEBO_RANK_INFERENCE_001`
- `MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.method_specific_randomization_inference_validation_001 --overwrite
```

---

## Residual Issues and Handoff

### Advanced in this artifact

- Method-specific readiness matrix for nine method families
- `INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001` method-specific validation layer

### Deferred unchanged

- Multicell multiplicity and shared-control investigations
- TBRRidge replacement inference
- AugSynth estimand/scale bridge

### Next artifact

`SCM_TREATED_SET_PLACEBO_INTEGRATION_001`
