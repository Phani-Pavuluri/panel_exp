# AUDIT-006 — Track D D2 estimator and donor gate

**Audit ID:** AUDIT-006  
**Date:** 2026-05-28  
**Lane:** Research / robustness  
**Baseline commit:** `1a31e69` (post INV-D1-001 + D5-DES-001a rerun)  
**Primary report:** [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](../TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md)

---

## Scope

Track D D2 — SCM estimator assumptions, donor-pool construction (MAT-004/005), estimator vs inference separation, Track B instrument compatibility, CalibrationSignal governance boundary.

## Stop conditions

| Criterion | Met |
|-----------|-----|
| D2 ADR audit document committed | Yes |
| MAT-004 / MAT-005 explicit statuses | Yes (`characterization_required`) |
| EST-001–004 reviewed with dispositions | Yes |
| Findings tracked (no silent fixes) | Yes — D2-FIND-001 → INV-D2-001 proposed |
| No production behavior changes | Yes |
| No eligibility / maturity / TrustReport changes | Yes |

## Verdict

**`continue_with_characterization_required`**

Research lane only. Not production-promotion evidence.

## Top finding

**D2-FIND-001:** `full_model=True` SCM paths may fit weights on post-period columns. Proposed **INV-D2-001** — fix in separate governed PR (same pattern as INV-D1-001).

## Next

1. **D3** — inference audit (INF-002, INF-006, TBR inference rows).  
2. **D5** — D5-EST-002a (post perturbation invariant on default configs).  
3. **INV-D2-001** — open investigation doc + governed fix when prioritized.

---

*AUDIT-006 v1.0.0 — closed (research lane)*
