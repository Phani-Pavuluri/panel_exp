# AUDIT-008 — Track D D4 power and MDE gate

**Audit ID:** AUDIT-008  
**Date:** 2026-06-01  
**Lane:** Research / robustness  
**Baseline commit:** `24beae8`  
**Primary report:** [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](../TRACK_D_D4_POWER_MDE_AUDIT_001.md)

---

## Scope

Track D D4 — power/MDE methods (POW-001–006), estimand alignment, design geometry, inference/readout coupling, Track E suitability links.

## Stop conditions

| Criterion | Met |
|-----------|-----|
| D4 ADR audit committed | Yes |
| POW rows explicit statuses | Yes |
| D5 power OC specs defined | Yes |
| No production behavior changes | Yes |

## Verdict

**`continue_with_characterization_required`**

## Top findings

1. **D4-FIND-001** — Default geo power uses TBRRidge+Kfold, not SCM JK readout.  
2. **D4-FIND-002** — Two-row treated/control aggregation.  
3. **D4-FIND-003** — `mde_percent` ≠ registry relative ATT without bridge.

## Next

D5-POW-001a; Track E E1; broader D5 OC — not MMM integration.

---

*AUDIT-008 v1.0.0 — closed (research lane)*
