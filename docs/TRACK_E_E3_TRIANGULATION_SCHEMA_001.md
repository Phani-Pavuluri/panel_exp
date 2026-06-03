# Track E E3 — Triangulation Schema 001

**Document ID:** TRACK-E-E3-TRIANGULATION-SCHEMA-001  
**Type:** Governance contract (triangulation schema)  
**Status:** **complete** (documentation only)  
**Date:** 2026-06-01  
**Lane:** Research / governance bridge (pre-implementation)  
**Baseline:** E1/E2 @ `68e0fcd` · D5-POW-001a–e · Track B B2 contract draft

**Related:** [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) · [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md) · [`TRACK_B_CONTRACT_SCHEMA_DRAFT_001.md`](TRACK_B_CONTRACT_SCHEMA_DRAFT_001.md)

---

## 1. Purpose

E3 defines the **multi-instrument evidence profile** schema: how design-method × geometry-mode × measurement-instrument outputs are represented **together** for triangulation, without naive averaging or unsafe MMM ingestion.

**Verdicts live in TrustReport only.** ExperimentEvidence carries **facts**; this schema is the **Track E triangulation layer** consumed by TrustReport composition (future E6 implementation).

### Canonical rules (non-negotiable)

| Rule | Statement |
|------|-----------|
| **No naive averaging** | Do not compute a single headline point from conflicting instruments. |
| **No pooled multi-cell** | Per-cell rows only; no pooled lift/null without governed pooling rule (`E-DES-MCELL-011`). |
| **No incompatible compare** | Different estimands or geometries are **non_comparable** — not “disagreement”. |
| **Diagnostic agreement ≠ lift** | Diagnostic-only agreement cannot create decision-grade lift. |
| **Restricted cannot override** | Restricted instruments may add warnings/context; they **cannot** override governed primary instruments. |
| **Blocked → no CalibrationSignal** | Blocked suitability excludes CalibrationSignal eligibility for that row. |
| **TrustReport only** | Agreement/conflict **dispositions** are TrustReport outputs. |
| **MMM ingress** | **CalibrationSignal** is the **only** MMM path. |

---

## 2. Profile envelope (`TriangulationProfile`)

One profile per **experiment run** (or governed snapshot of a run) under triangulation review.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profile_id` | string | yes | Stable ID, e.g. `tri-{study_id}-{run_id}` |
| `profile_version` | string | yes | Schema version, e.g. `1.0.0` |
| `generated_at` | ISO8601 | yes | Profile assembly time |
| `experiment_id` | string | yes | Study / experiment identifier |
| `run_id` | string | yes | Run bundle or analysis execution ID |
| `modality` | enum | yes | `geo` (extensible) |
| `design_method_id` | string | yes | From E2, e.g. `greedy_match_markets` |
| `geometry_mode` | enum | yes | `single_cell` \| `multi_cell` \| `supergeo` \| `trimmed_population` |
| `n_test_grps` | int | yes | 1 for single_cell; >1 for multi_cell |
| `declared_estimand_id` | string | yes | From ExperimentSpec / registry |
| `declared_claim_type` | enum | yes | e.g. `null_viability`, `positive_lift_detection`, `planning_mde` |
| `pre_period_window` | object | recommended | `{start, end}` fixed windows |
| `post_period_window` | object | recommended | `{start, end}` |
| `evidence_rows` | array | yes | List of `TriangulationEvidenceRow` (§3) |
| `triangulation_summary` | object | yes | Aggregated agreement state (§4) |
| `governance_refs` | array | recommended | E1/E2 doc IDs, D5 archive paths |

**Must not appear on profile:** averaged `combined_point_estimate`; pooled multi-cell headline metrics; MMM export flags (TrustReport derives those).

---

## 3. Evidence row (`TriangulationEvidenceRow`)

One row per **(measurement_instrument_id, cell_id)** slice. Multi-cell requires **separate rows per cell** — never one pooled row unless a governed pooling rule ID is attached.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `row_id` | string | yes | Unique within profile |
| `cell_id` | string | yes | `test_0` … `test_{k-1}`; use `test_0` for single_cell |
| `design_method_id` | string | yes | May match profile or note rerandomization wrapper |
| `geometry_mode` | string | yes | Must match profile or justify partial |
| `estimand_id` | string | yes | Exported/scored estimand for this row |
| `measurement_instrument_id` | string | yes | Full catalog ID |
| `config_alias` | string | optional | e.g. `SCM_UnitJackKnife` |
| `suitability_status` | enum | yes | From E2: `suitable` \| `suitable_with_caveats` \| `diagnostic_only` \| `restricted` \| `blocked` \| `characterization_required` |
| `evidence_role` | enum | yes | `primary` \| `secondary` \| `diagnostic` \| `restricted` \| `blocked` |
| `point_estimate` | number \| null | yes | Governed point on `estimand_id` |
| `uncertainty` | object \| null | conditional | §3.1 — required if interval-backed claims considered |
| `interval_semantics` | enum | yes | `confidence_interval` \| `placebo_band` \| `cumulative_att_interval` \| `none` |
| `claim_type` | enum | yes | What this row supports, e.g. `null_monitor`, `lift_point`, `planning_mde` |
| `allowed_claim_types` | string[] | yes | From E2 card |
| `disallowed_claim_types` | string[] | yes | From E2 card |
| `diagnostic_flags` | string[] | recommended | E1 IDs, e.g. `E-DES-MCELL-008` |
| `comparability_group` | string | yes | §3.2 |
| `conflict_group` | string | yes | §3.3 |
| `calibration_signal_eligibility` | object | yes | §3.4 |
| `trust_report_row_disposition` | enum | optional | Row-level hint; **profile disposition authoritative** |
| `evidence_ref` | object | recommended | Pointers to ExperimentEvidence / D5 archive |
| `freshness` | object | recommended | `{stale: bool, age_days: number}` |

### 3.1 Uncertainty object

Present only when `interval_semantics != none`.

```json
{
  "interval_estimand_id": "geo.relative_att_post.pooled_path.relative",
  "lower": -0.02,
  "upper": 0.04,
  "covers_zero": true,
  "semantics": "confidence_interval"
}
```

**Rules:** Placebo bands use `placebo_band` semantics — not comparable to CI lift intervals (E-ESTIMAND-004). DID cumulative intervals use `cumulative_att_interval` — not comparable to relative ATT post without bridge.

### 3.2 Comparability group

Instruments in the **same comparability group** may be evaluated for **directional agreement** on the **same estimand and geometry**.

| Group ID pattern | Members may compare? |
|------------------|----------------------|
| `rel_att_post_unit_single_cell` | SCM+JK, restricted TBR on same unit estimand + single_cell |
| `rel_att_post_unit_multi_cell_{cell_id}` | Per-cell only — **no cross-cell pool** |
| `planning_diagnostic_agg` | Geo PowerAnalysis MDE — **not** lift comparability |
| `non_comparable_estimand` | Row isolated — no directional compare |
| `non_comparable_geometry` | Row isolated — geometry blocks compare |
| `blocked_instrument` | Record only — excluded from agreement math |

**Assignment algorithm (normative):**

1. If `suitability_status` ∈ `{blocked, characterization_required}` → `blocked_instrument` or `non_comparable_geometry`.  
2. If `estimand_id` ≠ profile `declared_estimand_id` and no registry bridge → `non_comparable_estimand`.  
3. If geometry out of instrument card scope → `non_comparable_geometry`.  
4. If multi_cell → group suffix **must** include `cell_id`.  
5. Else assign instrument-specific group per E2 matrix.

### 3.3 Conflict group

Conflict groups cluster rows that **may** produce an E-CONFLICT class when compared within the same comparability group.

| Group ID | Typical conflict class |
|----------|------------------------|
| `governed_primary` | SCM+JK primary null-monitor |
| `restricted_secondary` | TBRRidge, DID restricted |
| `diagnostic_only` | Placebo, geo power |
| `blocked` | Blocked geometry / uncharacterized design |

**Rule:** Compare **governed_primary** vs **restricted_secondary** only for **context warnings** — restricted cannot flip primary disposition to lift.

### 3.4 CalibrationSignal eligibility (row-level)

```json
{
  "eligible": false,
  "reason_code": "null_monitor_only",
  "blocked_by": [],
  "requires_fresh_signal": true,
  "mmm_ingress_allowed": false
}
```

| `reason_code` | Meaning |
|---------------|---------|
| `governed_null_monitor` | SCM+JK null-monitor signal may bind (not lift) |
| `null_monitor_only` | Instrument card forbids lift CalibrationSignal |
| `diagnostic_only` | No CalibrationSignal for this claim |
| `restricted` | Excluded from MMM |
| `blocked_suitability` | E2 blocked |
| `characterization_required` | No signal until D5 follow-up |
| `estimand_mismatch` | Signal estimand ≠ row estimand |
| `stale_or_missing` | E-MMM-006 |
| `triangulation_conflict` | Profile summary blocks (§4) |

**MMM ingress:** `mmm_ingress_allowed` is **true** only when row + profile pass E-MMM-* **and** TrustReport disposition allows (never from Track D JSON alone).

---

## 4. Triangulation summary (`triangulation_summary`)

Profile-level aggregation of agreement across **comparable** rows only.

### 4.1 Agreement states (normative enum)

| State | Definition | Typical TrustReport disposition |
|-------|------------|-------------------------------|
| `aligned_agreement` | Same comparability group; same sign; intervals overlap or both null-compatible | `supported` / `supported_with_limitations` (claim-type dependent) |
| `directional_agreement_magnitude_differs` | Same sign; magnitudes differ beyond noise; same estimand | `supported_with_limitations` or note |
| `magnitude_agreement_direction_conflict` | Similar magnitude; **opposite sign** | `method_conflict_warning` |
| `uncertainty_overlap_only` | Intervals overlap; points differ; underpowered | `inconclusive` |
| `diagnostic_only_agreement` | Diagnostic instruments agree; no governed primary | **No lift** — TrustReport-only |
| `non_comparable_estimand` | Estimand mismatch | `non_comparable_estimand` — no combined estimate |
| `non_comparable_geometry` | Geometry scope mismatch | `not_assessable` / blocked row |
| `restricted_method_conflict` | Restricted positive vs primary null-compatible | `restricted_method_positive_but_primary_null_compatible` |
| `high_trust_conflict` | Governed primaries disagree on sign | `method_conflict_warning` / expert review |
| `blocked_by_suitability` | Any primary blocked | `blocked_by_geometry` / exclude |
| `missing_uncertainty` | Claim needs interval; row has `none` | `missing_uncertainty_warning` |
| `stale_or_freshness_blocked` | Stale/missing CalibrationSignal | `stale_downweight_or_exclude` |

**Priority (first match wins for profile headline):**

1. `blocked_by_suitability`  
2. `non_comparable_estimand` / `non_comparable_geometry` (if affects declared claim)  
3. `stale_or_freshness_blocked`  
4. `high_trust_conflict`  
5. `restricted_method_conflict`  
6. `magnitude_agreement_direction_conflict`  
7. `missing_uncertainty`  
8. Remaining agreement states  

### 4.2 Summary object fields

| Field | Type | Description |
|-------|------|-------------|
| `agreement_state` | enum | §4.1 |
| `comparable_row_ids` | string[] | Rows included in agreement evaluation |
| `excluded_row_ids` | string[] | Rows excluded with reason |
| `exclusion_reasons` | object | `{row_id: reason_code}` |
| `conflict_class` | string | E-CONFLICT-001…009 from E1 |
| `trust_report_disposition` | string | E4 disposition ID |
| `calibration_signal_profile_eligibility` | object | `{eligible: bool, reason: string}` |
| `forbidden_actions` | string[] | e.g. `no_averaging`, `no_mmm_feed`, `no_pooled_multi_cell` |

---

## 5. Evidence role assignment (normative)

| Instrument (E2) | Default `evidence_role` | May be `primary`? |
|-----------------|-------------------------|-------------------|
| SCM_UnitJackKnife | `primary` | Yes — **null_monitor claims only** |
| TBRRidge_Kfold / BRB | `restricted` | No |
| DID_Bootstrap | `restricted` | No |
| SCM_Placebo | `diagnostic` | No |
| Geo PowerAnalysis | `diagnostic` | No |
| AugSynth point | `diagnostic` | No |
| Blocked / characterization_required | `blocked` | No |

**Multi-instrument rule:** At most **one** `primary` row per comparability group per cell for a given claim type. Secondary/diagnostic rows **must not** upgrade disposition.

---

## 6. Multi-cell triangulation

| Rule | Requirement |
|------|-------------|
| **Row cardinality** | One row per `(instrument, cell_id)` |
| **Compare scope** | Agreement computed **within cell_id** only |
| **Cross-cell conflict** | If `test_0` and `test_1` disagree → `cell_level_conflict` (E4 fixture 5) |
| **Profile headline** | Must **not** pool cells; may report `cell_level_conflict` if any cell pair conflicts on declared claim |
| **Pooling rule** | Optional `pooling_rule_id` on profile — if absent, pooling **forbidden** |

---

## 7. Mapping to Track B contracts

| Track B object | E3 relationship |
|----------------|-----------------|
| **ExperimentSpec** | Supplies `declared_estimand_id`, `declared_claim_type`, design intent |
| **ExperimentEvidence** | Source for row point/interval facts — **no trust outcome** |
| **DiagnosticSummary** | Feeds `diagnostic_flags` |
| **CalibrationSignal** | Row-level eligibility binding — not computed in E3 |
| **TrustReport** | Consumes `triangulation_summary` → disposition (E4) |

E3 is **not** a replacement for B2 fields; it is the **multi-row triangulation overlay**.

---

## 8. JSON schema sketch (informative)

See [`tests/fixtures/track_e_conflicts/manifest.json`](../../tests/fixtures/track_e_conflicts/manifest.json) for executable fixture shapes. Minimal row:

```json
{
  "row_id": "row-scm-jk-test0",
  "cell_id": "test_0",
  "design_method_id": "greedy_match_markets",
  "geometry_mode": "single_cell",
  "estimand_id": "geo.relative_att_post.pooled_path.relative",
  "measurement_instrument_id": "geo.synthetic_control.unit_jackknife.relative_att_post.multi_treated_default.confidence_interval",
  "suitability_status": "suitable_with_caveats",
  "evidence_role": "primary",
  "point_estimate": 0.015,
  "uncertainty": {"lower": -0.01, "upper": 0.04, "covers_zero": true, "interval_estimand_id": "geo.relative_att_post.pooled_path.relative", "semantics": "confidence_interval"},
  "interval_semantics": "confidence_interval",
  "claim_type": "null_monitor",
  "allowed_claim_types": ["null_monitor", "null_viability"],
  "disallowed_claim_types": ["positive_lift_detection", "planning_mde", "mmm_lift"],
  "comparability_group": "rel_att_post_unit_single_cell",
  "conflict_group": "governed_primary",
  "calibration_signal_eligibility": {"eligible": true, "reason_code": "governed_null_monitor", "mmm_ingress_allowed": false}
}
```

---

## 9. Non-goals

- No production TrustReport code changes in E3  
- No Track B schema changes  
- No instrument promotion  
- No weakening E1/E2 statuses  

---

## 10. Sign-off

| Deliverable | Status |
|-------------|--------|
| E3 schema (this document) | ✅ |
| E4 fixtures | ✅ [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md) |
| E6 implementation | Deferred |

---

*TRACK-E-E3-TRIANGULATION-SCHEMA-001 v1.0.0 — 2026-06-01*
