# CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001

**Artifact ID:** CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/calibration_signal_method_gate_draft.py`  
**Validation:** `panel_exp/validation/calibration_signal_method_gate_draft_001.py`  
**Summary:** [`archives/CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001_summary.json`](archives/CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001_summary.json)

---

## 1. Artifact ID

`CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001`

---

## 2. Purpose

Define a draft-only CalibrationSignal method gate mapping Method Readiness Matrix V2 tiers into future CalibrationSignal eligibility rules. Answers which tiers could be considered for future review, which are categorically excluded, and what evidence is required before any promotion.

---

## 3. Prior roadmap context

Built after `METHOD_READINESS_MATRIX_V2_001`, which consolidated the method-validity spine into 25 governed readiness rows.

---

## 4. Source Method Readiness Matrix V2

One draft gate row per matrix row (`METHOD_READINESS_MATRIX_V2_001`). Row count must match source matrix (25 rows).

---

## 5. Draft gate schema

Each row defines `method_id`, source readiness tier, gate status, draft use boundary, required evidence, exclusion reasons, allowed draft outputs, forbidden outputs, and source evidence refs.

---

## 6. Gate status definitions

Statuses: eligible for future review, conditionally reviewable after additional evidence, not eligible (diagnostic/sensitivity/contract/unresolved/deferred/blocked).

---

## 7. Tier-to-gate mapping

| Readiness tier | Gate status |
|----------------|-------------|
| restricted_research_mode_usable | eligible_for_future_review |
| framework_level_randomization_candidate | conditionally_reviewable_after_additional_evidence |
| per_cell_marginal_only | conditionally_reviewable_after_additional_evidence |
| contract_candidate | not_eligible_contract_only |
| diagnostic_only | not_eligible_diagnostic_only |
| sensitivity_only | not_eligible_sensitivity_only |
| heterogeneity_review_required | conditionally_reviewable_after_additional_evidence |
| multiplicity_or_dependence_unresolved | not_eligible_unresolved_multiplicity_dependence |
| research_deferred | not_eligible_research_deferred |
| blocked | not_eligible_blocked |

---

## 8. Future-review eligible rows

`scm_unit_jackknife_restricted_research`, `did_bootstrap_restricted_research` — future review only; full evidence checklist required; no current authorization.

---

## 9. Conditionally reviewable rows

Framework candidates, per-cell marginal, heterogeneity review — not signal-ready; require additional evidence before any CalibrationSignal review.

---

## 10. Categorically excluded rows

Diagnostic-only, sensitivity-only, contract-only, unresolved multiplicity/dependence, research-deferred, and blocked rows cannot produce CalibrationSignal.

---

## 11. Required evidence before review

Eligible rows require final method validation, TrustReport authorization, estimand/lift-scale compatibility, uncertainty/freshness/conflict policies, method version provenance, downstream consumption policy, and production review signoff — all as future prerequisites, not satisfied by this draft.

---

## 12. Forbidden outputs

Every row forbids: actual CalibrationSignal creation, export, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, and budget optimization.

---

## 13. Scenario results

35+ deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact defines a draft CalibrationSignal method gate only.  
It does not create, export, authorize, or ingest CalibrationSignal records.  
Future-review eligible does not mean signal-ready.  
Conditionally reviewable does not mean signal-ready.  
Diagnostic-only, sensitivity-only, contract-only, unresolved, research-deferred, and blocked rows cannot produce CalibrationSignal.  
This artifact does not authorize TrustReport expansion, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary and row authorization flags are `false`, including `calibration_signal_allowed` and `calibration_signal_authorized`.

---

## 16. Final verdict

`calibration_signal_method_gate_draft_defined_no_authorization`

---

## 17. Recommended next artifact

**`CALIBRATION_SIGNAL_SCHEMA_ALIGNMENT_DRAFT_001`**

Alternatives: `METHOD_READINESS_MATRIX_V2_AUDIT_001`, `TRUSTREPORT_METHOD_GATE_DRAFT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.calibration_signal_method_gate_draft_001 --overwrite
```
