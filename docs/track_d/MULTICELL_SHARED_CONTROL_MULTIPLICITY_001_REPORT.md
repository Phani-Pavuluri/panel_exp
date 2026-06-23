# MULTICELL_SHARED_CONTROL_MULTIPLICITY_001

**Artifact ID:** MULTICELL_SHARED_CONTROL_MULTIPLICITY_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/multicell_multiplicity.py`  
**Validation:** `panel_exp/validation/multicell_shared_control_multiplicity_001.py`  
**Summary:** [`archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json`](archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json)

---

## 1. Artifact ID

`MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`

---

## 2. Purpose

Define governed multiplicity and shared-control dependence boundaries for multi-cell GeoX experiments. Explains why global, winner, and pooled multi-cell decisions remain blocked.

---

## 3. Prior roadmap context

Built after SCM studentized treated-set placebo integration. Addresses deferred investigations `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001` and `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`.

---

## 4. Multi-cell decision problem

Multiple per-cell readouts, shared controls, and global/winner/pooled claims create dependence and multiplicity that simple per-comparison alpha does not resolve.

---

## 5. Independent familywise false-positive proxy

`FWER_independent = 1 - (1 - alpha)^m` — e.g. alpha=0.10, m=3 → 0.271. Proxy only.

---

## 6. Shared-control dependence issue

Independent FWER does not authorize shared-control global/winner/pooled inference. Dependence model and joint null required.

---

## 7. Per-cell marginal boundary

Per-cell marginal readouts allowed as separate readouts only when cell-level estimand contracts exist. Not global decisions.

---

## 8. Global / winner / pooled blocked configurations

Global decision, winner selection, and pooled multi-cell effects remain blocked in this artifact.

---

## 9. Required evidence for future promotion

Joint null distribution, shared-control dependence model, max-T or closed-testing validation, pre-registered hypothesis family.

---

## 10. Scenario results

27 deterministic scenarios — all pass under `--strict`.

---

## 11. Downstream integration boundaries

This artifact defines multi-cell shared-control multiplicity boundaries only.  
Per-cell marginal readouts are not global multi-cell decisions.  
Independent FWER is a proxy and does not authorize shared-control global/winner/pooled inference.  
Global decisions, winner selection, and pooled multi-cell effects remain blocked.  
This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 12. Safety checks

All summary authorization flags are `false`.

---

## 13. Final verdict

`multicell_shared_control_multiplicity_defined_no_downstream_authorization`

---

## 14. Recommended next artifact

**`STRATIFIED_POOLED_ESTIMAND_CONTRACT_001`**

Alternatives: `AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`, `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.multicell_shared_control_multiplicity_001 --overwrite
```
