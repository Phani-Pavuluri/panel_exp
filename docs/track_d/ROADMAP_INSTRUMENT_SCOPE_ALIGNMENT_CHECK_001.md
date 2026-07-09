# ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `ROADMAP_INSTRUMENT_SCOPE_ALIGNMENT_CHECK_001` |
| **Artifact type** | `roadmap_instrument_scope_alignment_check` |
| **Status** | `completed` |
| **Scope** | `roadmap_instrument_scope_and_milestones_aligned_no_method_promotion_or_catalog_unblock` |
| **Base commit** | `1fab4ad` (Add method pairing value prioritization audit) |
| **Final verdict** | `roadmap_instrument_scope_and_milestones_aligned_no_method_promotion_or_catalog_unblock` |

**Depends on:** `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` · `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` · `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` · `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001`

---

## 2. Source files inspected

- `docs/ROADMAP_V4.md`
- `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`
- `docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md`
- `docs/track_d/METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001.md`
- `docs/track_d/METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001.md`
- `docs/track_d/METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001.md`

---

## 3. Audit purpose

**Core question:** Are the roadmap docs now correctly scoped, internally consistent, and safe to follow milestone-by-milestone?

This check goes beyond wording: it verifies milestone order, followability, separation of platform policy vs TBRRidge lane milestones, and absence of stale/skipped/wrong-next references after recent instrument-scoping corrections.

---

## 4. Roadmap scope verdict

| Check | Result |
|-------|--------|
| Promote instruments, not estimator families | **Pass** — ROADMAP_V4 §554, classification policy referenced |
| No global TBRRidge/SCM/AugSynth/DID promotion implied | **Pass** — TBRRidge lane scoped to KFold instrument identity |
| Exact instrument identity required for future promotion | **Pass** — platform policy chain documented |
| Missing pairings require reason codes | **Pass** — pairing coverage audit referenced |
| Pairing value prioritization reflected | **Pass** — AugSynth KFold/Conformal correction noted |
| No new PURSUE_NOW beyond TBRRidge × KFold | **Pass** — value prioritization audit |
| AugSynth JK save-for-later | **Pass** — alternative lane |
| Production compatibility deferred | **Pass** — gate-triggered |
| Geometry taxonomy optional | **Pass** — not blocking |

**`roadmap_scope_aligned`: true**

---

## 5. Milestone followability verdict

**Safe milestone order (verified):**

1. Platform policy: `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` ✅
2. Catalog triage: `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` ✅
3. Pairing coverage: `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` ✅
4. Pairing value prioritization: `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` ✅
5. **Next:** TBRRidge claim authorization boundary (instrument-scoped)
6. Evidence packet assembly / promotion review (existing TBRRidge battery — in progress)
7. Production compatibility review runtime — **deferred** until exact instrument review + RANK_4 candidate

Claim authorization and evidence assembly precede production compatibility. Production compatibility applies only after exact instrument review.

**`roadmap_milestones_followable`: true**

---

## 6. Platform policy milestone review

| Artifact | ROADMAP | METHOD_SOUNDNESS | MIP | OPEN_INVESTIGATIONS |
|----------|---------|----------------|-----|---------------------|
| Classification policy | ✅ complete | ✅ | ✅ | Lane complete |
| Catalog triage | ✅ complete | ✅ (corrected) | ✅ | Lane complete |
| Pairing coverage | ✅ complete | ✅ | ✅ | Lane complete |
| Pairing value prioritization | ✅ complete | ✅ | ✅ | Lane complete |
| Scope alignment check | ✅ complete (this) | ✅ (corrected) | ✅ (added) | Lane complete |

Platform milestones are **sequential and complete**. No platform artifact incorrectly marked as next after completion.

---

## 7. TBRRidge restricted-review lane milestone review

| Element | Status |
|---------|--------|
| Instrument scope | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| Evidence battery | Scoped to KFold identity (not global TBRRidge) |
| Completed TBRRidge audits | Interval semantics through metric estimand alignment ✅ |
| **Next** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` — consistent across ROADMAP, METHOD_SOUNDNESS, MIP, governance |
| Posture | RANK_0 / BLOCKED / STAGE_2 — not promoted |

TBRRidge lane milestones are **separated** from platform policy chain and **correctly ordered** before production compatibility.

---

## 8. Alternative AugSynth lane review

| Element | Status |
|---------|--------|
| AugSynth × JK | **Save-for-later** — `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` as alternative |
| AugSynth × KFold/Conformal | Implemented-but-not-governed; diagnostic only — not described as unimplemented |
| AugSynth × Placebo/Bootstrap | Blocked — not future candidate |
| PURSUE_NOW | None for AugSynth |

Alternative lane does not block TBRRidge claim authorization boundary.

---

## 9. Deferred production compatibility review

`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` remains **deferred** in ROADMAP_V4, METHOD_SOUNDNESS, MIP registry, and governance lanes. Gate: STAGE_6 / RANK_4 candidate after exact instrument review.

---

## 10. Stale wording scan

| Finding | Location | Disposition |
|---------|----------|-------------|
| `CLAIM_AUTHORIZATION_RUNTIME_001` marked `next P0` while complete | ROADMAP_V4 artifact table | **Fixed** → `complete` |
| Duplicate `CLAIM_AUTHORIZATION_RUNTIME_001` table row | ROADMAP_V4 artifact table | **Fixed** — removed duplicate |
| `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001` missing from active lanes | METHOD_SOUNDNESS §443 | **Fixed** — added to platform chain |
| Historical "not production-ready" framing for TBRRidge investigation | ROADMAP_V4 §1030 | **Acceptable** — explicitly negates production-ready claims |
| `METHOD_FAMILY_PRODUCTION_COMPATIBILITY` (9 families) | ROADMAP_V4 §373 | **Acceptable** — historical artifact; superseded by instrument-scoped policy for new work |

No estimator-family promotion language requiring correction found in current next-artifact sections.

---

## 11. Missing milestone scan

| Expected milestone | Present |
|--------------------|---------|
| Platform policy chain (4 artifacts) | ✅ |
| Scope alignment check | ✅ (this artifact) |
| TBRRidge claim boundary as next | ✅ |
| Geometry taxonomy as optional | ✅ (added to ROADMAP/METHOD_SOUNDNESS) |
| Production compatibility deferred | ✅ |

No required milestone missing from roadmap docs.

---

## 12. Wrong-order milestone scan

| Issue | Verdict |
|-------|---------|
| Claim authorization before platform scoping | **No** — platform chain complete first |
| Production compatibility before claim boundary | **No** — deferred |
| TBRRidge promotion before evidence battery | **No** — battery audits complete; claim boundary next |
| AugSynth JK before TBRRidge lane closure | **No** — JK is alternative only |

No wrong-order milestones found after corrections.

---

## 13. Roadmap corrections made

| File | Correction |
|------|------------|
| `docs/ROADMAP_V4.md` | Fixed stale `CLAIM_AUTHORIZATION_RUNTIME_001` next P0 → complete; removed duplicate row; added platform policy chain summary; separated TBRRidge lane next; added optional geometry taxonomy |
| `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` | Added missing catalog triage + scope alignment check; clarified platform vs TBRRidge lane next |

No strategic direction changed beyond consistency.

---

## 14. Authorization boundary

**Verdict flags (all true where applicable):** `roadmap_scope_aligned` · `roadmap_milestones_followable` · `estimator_family_promotion_blocked` · `exact_instrument_scope_required` · `tbrridge_kfold_lane_current` · `pairing_reason_codes_required` · `pairing_value_prioritization_reflected` · `no_new_pursue_now_pairing` · `augsynth_jk_save_for_later` · `production_compatibility_deferred` · `geometry_taxonomy_optional_followup` · `next_artifact_confirmed`: `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`

**Forbidden:** all promotion/unblock/production/uncertainty/inference/implementation flags remain false.

---

## 15. Validation results

| Check | Result |
|-------|--------|
| Audit document complete | Pass |
| Summary JSON valid | Pass |
| Governance tests | Pass |

---

## 16. Known limitations

- **Docs-only** — Does not re-audit artifact content, only roadmap consistency
- **Historical sections** — Older ROADMAP family-level artifacts retained for lineage
- **OPEN_INVESTIGATIONS** — Large file; spot-checked lane bindings for platform/TBRRidge next artifacts

---

## 17. Recommended next artifact

**`TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`** — confirmed across all roadmap surfaces.

**Alternative:** `METHOD_INSTRUMENT_GEOMETRY_TAXONOMY_AUDIT_001` (optional) · `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` (save-for-later)

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
