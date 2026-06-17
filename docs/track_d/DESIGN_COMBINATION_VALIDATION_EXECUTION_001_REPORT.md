# Design Combination Validation Execution 001 — Report

**Artifact ID:** DESIGN-COMBINATION-VALIDATION-EXECUTION-001  
**Version:** 001  
**Status:** Characterization complete — **no promotion**  
**Summary archive:** `docs/track_d/archives/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_summary.json`  
**Harness:** `panel_exp/validation/track_d_design_combination_validation_execution_001.py`

**Design baseline:** D5-DES-STAT-TIER1-RECHARACTERIZATION-001

**Verdict:** `design_combinations_mixed_with_method_specific_restrictions`

See summary JSON for git commit, run counts, aggregate results, pairwise comparisons, and `matrix_row_updates`.

---

## 1. Executive summary

Executes DCM-001–019 combination rows using design assignment → `PanelDataset` → estimator paths. Primary unit-panel rows (SCM+JK, AugSynth point) characterized with restrictions. TBR aggregate blocked by geometry (24/24). DID bootstrap mechanically compatible on unit-panel (24/24). Multi-cell pooled claims blocked. No production or downstream authorization.

## 2–10. Context

Governing matrix: `docs/DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`. Corrected designs DES-001–006 + DES-011 per-cell. 1,680 records; 59s runtime; 18 worlds; seeds 101/202; 2 replicates; effects 0.0/0.08.

## 11. DCM-001

670/720 mechanical success → `characterized_with_restrictions`. Failures in infeasibility/exhaustion worlds.

## 12. DCM-002

670/720 → `compatible_point_only`. Interval claims blocked.

## 13. DCM-003

24/24 `blocked_due_to_geometry_mismatch` (unit panel ≠ aggregate two-row).

## 14. DCM-004

24/24 mechanical success → `characterized_with_restrictions`; supersedes conservative matrix geometry block for unit-panel DID.

## 15–16. Multi-cell

DCM-006 per-cell lane; DCM-007 pooled blocked 16/16.

## 17–19. Lanes E/C

Adapter/bridge rows classified only. Readout mismatch controls all enforce blocks.

## 20–22. Pairwise

SCM+JK: stratified_corrected median abs-error delta −0.30 vs complete_randomization (272 paired worlds).

## 23–31. Governance

Failures preserved. Contract/guardrail evaluated; downstream blocked. Next: DESIGN-GUARDRAIL-ENFORCEMENT-001.

```bash
poetry run python -m panel_exp.validation.track_d_design_combination_validation_execution_001 \
  --output-local /tmp/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_results.json \
  --summary-output docs/track_d/archives/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_summary.json \
  --overwrite
```
