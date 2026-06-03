# Track E E4 — TrustReport Conflict Fixtures 001

**Document ID:** TRACK-E-E4-TRUSTREPORT-CONFLICT-FIXTURES-001  
**Type:** Governance contract (golden conflict fixtures)  
**Status:** **complete** (documentation + JSON fixtures)  
**Date:** 2026-06-01  
**Lane:** Research / governance bridge (pre-TrustReport implementation)  
**Schema:** [`TRACK_E_E3_TRIANGULATION_SCHEMA_001.md`](TRACK_E_E3_TRIANGULATION_SCHEMA_001.md)

**Related:** [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) · [`TRACK_B_TRUST_REPORT_001.md`](TRACK_B_TRUST_REPORT_001.md) · [`TRACK_B_CONTRACT_TEST_PLAN_001.md`](TRACK_B_CONTRACT_TEST_PLAN_001.md)

**JSON index:** [`tests/fixtures/track_e_conflicts/manifest.json`](../../tests/fixtures/track_e_conflicts/manifest.json)

---

## 1. Purpose

E4 defines **golden triangulation + TrustReport conflict scenarios** for future implementation (E6). Each fixture specifies:

- Input evidence rows (E3 shape)  
- Expected comparability classification  
- Expected conflict class (E1 E-CONFLICT-*)  
- Expected TrustReport disposition  
- Expected CalibrationSignal eligibility  
- **Forbidden behaviors** (no averaging, no promotion, no MMM if blocked, no pooled multi-cell, no decision-grade from diagnostic-only agreement)

**TrustReport is the only verdict layer.** CalibrationSignal is the only MMM ingress.

---

## 2. Disposition vocabulary (E4)

| Disposition ID | TrustReport mapping (informative) | CalibrationSignal |
|----------------|-----------------------------------|-------------------|
| `directional_support_with_caveats` | Context note; primary governs | Conditional / TrustReport-only for lift |
| `restricted_method_positive_but_primary_null_compatible` | Restricted context only | **No lift** signal |
| `method_conflict_warning` | Warning facet; no combined estimate | Blocked for conflicting lift |
| `non_comparable_estimand` | `unsupported` / incompatible compare | No combined signal |
| `cell_level_conflict` | Per-cell warnings; no pooled headline | Per-cell only if policy exists |
| `blocked_by_geometry` | Row excluded from triangulation | Excluded |
| `planning_diagnostic_only` | Diagnostic note; not readout MDE | **Forbidden** (E-MMM-010) |
| `characterization_required` | Record blocked; no universe claim | Excluded |
| `missing_uncertainty_warning` | Downgrade interval claims | Blocked until uncertainty present |
| `stale_downweight_or_exclude` | `not_assessable` / stale facet | Excluded until fresh |

---

## 3. Fixture catalog

| ID | File | Scenario | Disposition |
|----|------|----------|-------------|
| **E4-001** | `e4_001_scm_jk_tbr_same_direction.json` | SCM+JK null-monitor compatible + TBR diagnostic same direction | `directional_support_with_caveats` |
| **E4-002** | `e4_002_primary_null_restricted_tbr_positive.json` | SCM+JK null-compatible + TBR strong positive restricted | `restricted_method_positive_but_primary_null_compatible` |
| **E4-003** | `e4_003_scm_did_opposite_sign.json` | SCM+JK positive + DID opposite restricted | `method_conflict_warning` |
| **E4-004** | `e4_004_same_direction_different_estimands.json` | Same direction, different estimands | `non_comparable_estimand` |
| **E4-005** | `e4_005_multi_cell_cell_conflict.json` | test_1 positive, test_2 null/negative | `cell_level_conflict` |
| **E4-006** | `e4_006_placebo_multi_treated_blocked.json` | SCM placebo multi-treated | `blocked_by_geometry` |
| **E4-007** | `e4_007_geo_power_planning_only.json` | Geo PowerAnalysis feasible; readout not lift-eligible | `planning_diagnostic_only` |
| **E4-008** | `e4_008_supergeo_uncharacterized.json` | Supergeo output without D5-DES-SUPERGEO-001 | `characterization_required` |
| **E4-009** | `e4_009_missing_uncertainty.json` | Missing SE / interval | `missing_uncertainty_warning` |
| **E4-010** | `e4_010_stale_evidence.json` | Stale CalibrationSignal / freshness | `stale_downweight_or_exclude` |

---

## 4. Fixture summaries

### E4-001 — SCM+JK + TBR same direction

**Intent:** Restricted TBR agrees directionally with SCM+JK null-monitor-compatible primary — **caveats only**.

| Expected | Value |
|----------|-------|
| Comparability | Same `rel_att_post_unit_single_cell` |
| Agreement state | `directional_agreement_magnitude_differs` or `diagnostic_only_agreement` for TBR row |
| Conflict class | E-CONFLICT-001 benign or restricted tier |
| TrustReport | `directional_support_with_caveats` — **no lift promotion** |
| CalibrationSignal | Null-monitor bind OK; **lift MMM blocked** (DEF-013) |
| Forbidden | Averaging points; TBR upgrading disposition to `supported` lift |

---

### E4-002 — Primary null-compatible + restricted TBR strong positive

**Intent:** Governed SCM+JK interval covers zero; TBR shows strong positive — restricted **must not** create lift.

| Expected | Value |
|----------|-------|
| Agreement state | `restricted_method_conflict` |
| TrustReport | `restricted_method_positive_but_primary_null_compatible` |
| CalibrationSignal | **No lift** CalibrationSignal |
| Forbidden | Lift claim; silent average |

---

### E4-003 — SCM+JK vs DID opposite sign

**Intent:** Governed primary vs restricted opposite direction — warning, no average.

| Expected | Value |
|----------|-------|
| Agreement state | `high_trust_conflict` or `magnitude_agreement_direction_conflict` |
| Conflict class | E-CONFLICT-008 |
| TrustReport | `method_conflict_warning` |
| CalibrationSignal | Blocked for lift |
| Forbidden | Combined estimate; MMM feed |

---

### E4-004 — Same direction, different estimands

**Intent:** SCM relative ATT vs DID cumulative — **non-comparable**, not disagreement.

| Expected | Value |
|----------|-------|
| Comparability | `non_comparable_estimand` on DID row |
| Agreement state | `non_comparable_estimand` |
| Conflict class | E-CONFLICT-003 |
| TrustReport | `non_comparable_estimand` |
| Forbidden | Combined estimate; “methods agree” narrative |

---

### E4-005 — Multi-cell cell conflict

**Intent:** `test_1` positive, `test_2` null/negative — per-cell only.

| Expected | Value |
|----------|-------|
| Agreement state | `cell_level_conflict` (profile) |
| TrustReport | Per-cell dispositions; **no pooled headline** |
| Forbidden | Pooled multi-cell lift/null claim (`E-DES-MCELL-011`) |

---

### E4-006 — Placebo multi-treated blocked

**Intent:** SCM Placebo on multi-treated default — blocked geometry.

| Expected | Value |
|----------|-------|
| Suitability | `blocked` |
| Comparability | `blocked_instrument` |
| TrustReport | `blocked_by_geometry` — diagnostic record only |
| Forbidden | Triangulation compare as lift |

---

### E4-007 — Geo PowerAnalysis planning only

**Intent:** Low MDE / feasible power; SCM+JK not lift-detection eligible.

| Expected | Value |
|----------|-------|
| Agreement state | `diagnostic_only_agreement` (planning row isolated) |
| TrustReport | `planning_diagnostic_only` |
| CalibrationSignal | **Forbidden** for MDE (E-MMM-010, D5-POW-001a) |
| Forbidden | MMM planning from geo MDE; treating as readout OC |

---

### E4-008 — Supergeo / trimmed uncharacterized

**Intent:** Output present without D5-DES-SUPERGEO-001 / D5-DES-TRIM-001.

| Expected | Value |
|----------|-------|
| Suitability | `characterization_required` |
| TrustReport | `characterization_required` |
| Forbidden | Full-universe claim; SCM+JK 001e transfer |

---

### E4-009 — Missing uncertainty

**Intent:** Point-only or missing SE when interval claim requested.

| Expected | Value |
|----------|-------|
| Agreement state | `missing_uncertainty` |
| TrustReport | `missing_uncertainty_warning` per Track B policy |
| Forbidden | Interval-backed lift without uncertainty |

---

### E4-010 — Stale evidence

**Intent:** CalibrationSignal stale or missing when calibration-backed claim requested.

| Expected | Value |
|----------|-------|
| Agreement state | `stale_or_freshness_blocked` |
| TrustReport | `stale_downweight_or_exclude` |
| Forbidden | MMM ingress; treating stale as fresh |

---

## 5. Implementation contract (E6 preview)

Future TrustReport composer tests should:

1. Load fixture JSON → build `TriangulationProfile`.  
2. Run triangulation evaluator (not in E4 scope).  
3. Assert `triangulation_summary.agreement_state`, `trust_report_disposition`, `calibration_signal_profile_eligibility`.  
4. Assert all `forbidden_actions` negated.  

Track B contract tests (`GOLD-*`) remain authoritative for **single-instrument** export; E4 fixtures extend to **multi-instrument** profiles.

---

## 6. Non-goals

- No `trust_report.py` changes in E4  
- No instrument promotion  
- No weakening E1/E2  

---

## 7. Sign-off

| Deliverable | Status |
|-------------|--------|
| E4 fixture spec (this document) | ✅ |
| JSON fixtures (10) | ✅ `tests/fixtures/track_e_conflicts/` |
| E6 composer tests | Planned |

---

*TRACK-E-E4-TRUSTREPORT-CONFLICT-FIXTURES-001 v1.0.0 — 2026-06-01*
