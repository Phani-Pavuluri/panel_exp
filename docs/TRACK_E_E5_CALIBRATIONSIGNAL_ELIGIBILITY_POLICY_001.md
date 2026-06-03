# Track E E5 — CalibrationSignal Eligibility Policy 001

**Document ID:** TRACK-E-E5-CALIBRATIONSIGNAL-ELIGIBILITY-POLICY-001  
**Type:** Governance contract (CalibrationSignal eligibility)  
**Status:** **complete** (documentation only)  
**Date:** 2026-06-01  
**Lane:** Research / governance bridge (pre-MMM implementation)  
**Baseline:** E3/E4 @ `a9ab794` · Track B CalibrationSignal architecture

**Related:** [`TRACK_E_E3_TRIANGULATION_SCHEMA_001.md`](TRACK_E_E3_TRIANGULATION_SCHEMA_001.md) · [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md) · [`TRACK_B_CALIBRATION_SIGNAL_001.md`](TRACK_B_CALIBRATION_SIGNAL_001.md) · [`TRACK_B_TRUST_REPORT_001.md`](TRACK_B_TRUST_REPORT_001.md)

**Test oracle:** [`panel_exp/track_b/triangulation.py`](../../panel_exp/track_b/triangulation.py) (production) · E6 [`tests/track_e/test_e6_e4_conflict_fixtures.py`](../../tests/track_e/test_e6_e4_conflict_fixtures.py) · E7 [`tests/track_b/test_e7_track_e_trust_report.py`](../../tests/track_b/test_e7_track_e_trust_report.py)

---

## 1. Purpose

E5 defines how **Track E triangulation outcomes** map to **CalibrationSignal eligibility** and **TrustReport-only** paths. It is the policy layer between E3/E4 dispositions and MMM ingress.

### Canonical boundaries

| Layer | Role |
|-------|------|
| **ExperimentEvidence** | Facts only — no trust verdict |
| **TriangulationProfile (E3)** | Multi-instrument assembly — no averaged headline |
| **TrustReport** | **Only** agreement/conflict verdict layer |
| **CalibrationSignal** | **Only** MMM ingress path |
| **MMM / planning optimizer** | **No** direct feed from Evidence, Track D JSON, or TrustReport |

**No promotion in E5:** SCM+JK, TBR, DID, BRB, placebo, Geo PowerAnalysis, supergeos, trimmedmatch statuses from E1/E2 are unchanged.

---

## 2. Eligibility vocabulary

| Term | Meaning |
|------|---------|
| **eligible** | May bind existing CalibrationSignal for permitted claim scope |
| **conditional** | Eligible only if Track B estimand + uncertainty + freshness gates pass |
| **weak** | Null-monitor or diagnostic scope only; explicit caveats required |
| **trust_report_only** | TrustReport narrative/warnings; **no** new or expanded CalibrationSignal for declared claim |
| **excluded** | Do not bind CalibrationSignal for this profile/claim |
| **blocked** | Fail-closed; record only |
| **downweighted** | Stale signal may appear with freshness warning; **no** MMM until refreshed |

---

## 3. Disposition → CalibrationSignal policy map

| TrustReport disposition (E4) | CalibrationSignal | TrustReport | MMM ingress |
|------------------------------|-------------------|-------------|-------------|
| `directional_support_with_caveats` | **Conditional / weak** — null-monitor scope only if primary row passes estimand + uncertainty + freshness | Supported with limitations for null; restricted adds context | **No lift MMM**; null-monitor bind only if Track B gates pass |
| `restricted_method_positive_but_primary_null_compatible` | **TrustReport-only** | Inconclusive for lift; note restricted positive | **Excluded** |
| `method_conflict_warning` | **Excluded** (fail-closed for lift) | Warning facet; divergent/inconclusive | **Excluded** |
| `non_comparable_estimand` | **No combined signal** | `unsupported` for compare | **Excluded** |
| `cell_level_conflict` | **Per-cell only**; **no pooled** | Per-cell dispositions; profile inconclusive for pooled claim | **No pooled MMM** |
| `blocked_by_geometry` | **Excluded** | `not_assessable` | **Excluded** |
| `planning_diagnostic_only` | **Excluded** for MDE/planning claims | Diagnostic note only | **Forbidden** (E-MMM-010) |
| `characterization_required` | **Excluded** until D5 follow-up | `not_assessable` | **Excluded** |
| `missing_uncertainty_warning` | **Weak / excluded** for interval-backed claims | `unsupported` or downgrade per Track B | **Excluded** for interval claims |
| `stale_downweight_or_exclude` | **Downweight or exclude** bind | `not_assessable` for calibration-backed claims | **Excluded** until fresh |

---

## 4. Policy rules (normative)

### 4.1 Primary vs restricted vs diagnostic

| Rule ID | Rule |
|---------|------|
| **E5-R-001** | Only **`evidence_role: primary`** rows with E2 status ∈ `{suitable, suitable_with_caveats}` may drive **eligible** CalibrationSignal binding. |
| **E5-R-002** | **`restricted`** rows may add TrustReport context; they **must not** upgrade disposition to lift `supported` or set `mmm_ingress_allowed: true`. |
| **E5-R-003** | **`diagnostic`** rows (Placebo, Geo PowerAnalysis, AugSynth point) are **TrustReport-only**; never MMM ingress. |
| **E5-R-004** | **`blocked`** / **`characterization_required`** rows are excluded from triangulation math and CalibrationSignal. |

### 4.2 Diagnostic-only agreement

| Rule ID | Rule |
|---------|------|
| **E5-R-010** | If agreement is only among **diagnostic** rows → `diagnostic_only_agreement`; **no** decision-grade lift; **no** lift CalibrationSignal. |
| **E5-R-011** | Diagnostic agreement with governed primary null-compatible → `directional_support_with_caveats` at most; restricted cannot create lift. |

### 4.3 Uncertainty and freshness

| Rule ID | Rule |
|---------|------|
| **E5-R-020** | Interval-backed claims require valid `uncertainty` with matching `interval_semantics` on primary row (Track B ALIGN rules). |
| **E5-R-021** | Missing uncertainty → `missing_uncertainty_warning`; CalibrationSignal **excluded** for interval claims. |
| **E5-R-022** | `freshness.stale: true` on bound instrument → `stale_downweight_or_exclude`; **no MMM** until signal refreshed (E-MMM-006). |
| **E5-R-023** | Missing CalibrationSignal bind when required → `not_assessable`; not auto-eligible. |

### 4.4 Multi-cell

| Rule ID | Rule |
|---------|------|
| **E5-R-030** | Multi-cell profiles emit **per-cell** TrustReport and optional per-cell signal keys only. |
| **E5-R-031** | **Pooled multi-cell CalibrationSignal is forbidden** without explicit `pooling_rule_id` on profile (E-DES-MCELL-011). |
| **E5-R-032** | Cross-cell directional conflict → `cell_level_conflict`; profile-level pooled claim **excluded**. |

### 4.5 Conflict fail-closed

| Rule ID | Rule |
|---------|------|
| **E5-R-040** | `method_conflict_warning` → CalibrationSignal **excluded** for lift unless future governed rule (none today). |
| **E5-R-041** | `non_comparable_estimand` → **no combined** CalibrationSignal; do not average points. |
| **E5-R-042** | Opposite-sign governed primaries → expert-review posture; MMM **excluded**. |

### 4.6 MMM ingress

| Rule ID | Rule |
|---------|------|
| **E5-R-050** | **Only** CalibrationSignal may cross MMM boundary — never raw Evidence, TrustReport, or Track D archives. |
| **E5-R-051** | `mmm_ingress_allowed: true` requires: eligible disposition + primary row + estimand match + fresh signal + conflict pass + claim type allowed on instrument card. |
| **E5-R-052** | SCM+JK today: **`null_monitor_only`** usage boundary — **no lift MMM** (DEF-013, D5-POW-001b). |
| **E5-R-053** | Geo PowerAnalysis **`planning_diagnostic_only`** — **never** MMM calibration (D5-POW-001a). |

---

## 5. Weak / conditional eligibility representation

When disposition is `directional_support_with_caveats` and primary row passes gates:

```json
{
  "calibration_signal_eligibility": {
    "eligible": true,
    "strength": "conditional_weak",
    "scope": "null_monitor_only",
    "lift_mmm_allowed": false,
    "bind_requires": [
      "declared_estimand_id_match",
      "interval_semantics_match",
      "fresh_calibration_signal",
      "no_triangulation_conflict"
    ],
    "caveats": ["restricted_instrument_context_only", "not_lift_detection"]
  }
}
```

When conditional gates fail → downgrade to `trust_report_only` with `eligible: false`.

---

## 6. Per-disposition worked examples (E4 fixtures)

| Fixture | Disposition | CalibrationSignal outcome |
|---------|-------------|---------------------------|
| E4-001 | `directional_support_with_caveats` | Conditional weak null-monitor bind; **no lift MMM** |
| E4-002 | `restricted_method_positive_but_primary_null_compatible` | **Excluded** for lift |
| E4-003 | `method_conflict_warning` | **Excluded** fail-closed |
| E4-004 | `non_comparable_estimand` | **No combined** signal |
| E4-005 | `cell_level_conflict` | Per-cell only; `pooled_allowed: false` |
| E4-006 | `blocked_by_geometry` | **Excluded** |
| E4-007 | `planning_diagnostic_only` | **Excluded**; geo MDE not MMM |
| E4-008 | `characterization_required` | **Excluded** |
| E4-009 | `missing_uncertainty_warning` | **Excluded** for interval claim |
| E4-010 | `stale_downweight_or_exclude` | **Excluded** bind until fresh |

---

## 7. Forbidden actions (E5 enforcement)

Any triangulation evaluator or future composer **must not**:

- Emit `combined_point_estimate` or pooled multi-cell headline  
- Set `mmm_ingress_allowed: true` when disposition ∈ excluded set (§3)  
- Promote diagnostic-only agreement to lift `supported`  
- Allow restricted/blocked row to override primary null-compatible disposition  
- Feed MMM from non-CalibrationSignal paths  

E6 tests assert these via [`triangulation_contract.py`](../../tests/track_e/triangulation_contract.py).

---

## 8. Relationship to Track B

| Track B artifact | E5 uses |
|------------------|---------|
| **CalibrationSignal.usage_boundary** | Caps eligible scope (`null_monitor_only`, etc.) |
| **ExperimentSpec.declared_estimand_id** | Bind gate |
| **Evidence interval fields** | Uncertainty gate |
| **TrustReport composer** | Consumes disposition — E6 tests contract oracle first |

E5 does **not** change Track B schemas or production `trust_report.py`.

---

## 9. Non-goals

- No production MMM ingestion  
- No optimizer/planning feed  
- No instrument promotion  
- No production TrustReport code changes in E5  

---

## 10. Sign-off

| Deliverable | Status |
|-------------|--------|
| E5 policy (this document) | ✅ |
| E6 fixture tests | ✅ [`test_e6_e4_conflict_fixtures.py`](../../tests/track_e/test_e6_e4_conflict_fixtures.py) |
| E7 production implementation | ✅ TrustReport composer [`trust_report.py`](../../panel_exp/track_b/trust_report.py) |

---

*TRACK-E-E5-CALIBRATIONSIGNAL-ELIGIBILITY-POLICY-001 v1.0.0 — 2026-06-01*
