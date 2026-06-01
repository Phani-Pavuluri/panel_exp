# AUDIT-003 — M2.1 representative RunBundle wire-up gate

**Audit ID:** AUDIT-003  
**Date:** 2026-05-28  
**Auditor:** MIP periodic audit (committed-code review + test evidence)  
**Milestone reviewed:** M2.1 adapter production wire-up  
**Commit / branch:** `5000fc5` on `fix-kfold-multitreated-geometry` (M2.1 code `4a8f0ca`, roadmap `5000fc5`)  
**Scope:** `panel_exp/track_b/bundle_extract.py`, `export.py`, `geo_adapter.py`, `dual_write.py`; `tests/fixtures/representative_run_bundles/`; `tests/track_b/test_m2_1_representative_bundles.py`; B5 boundary tests  

**Gate purpose:** Confirm AUDIT-002 follow-up (representative non-fixture RunBundles) before choosing M2.2 production TrustReport, Track D D1 (research lane), or additional M2.1 hardening.

---

## Gate checklist (AUDIT-003 key checks)

| Check | Result | Evidence |
|-------|--------|----------|
| M2.1 satisfies AUDIT-002 follow-up | **Yes** | `bundle_extract.py` + `resolve_geo_adapter_output_from_bundle`; REP-001–005; extraction sidecar on dual-write |
| ≥3 representative non-fixture RunBundles | **Yes** | 5 cases in `tests/fixtures/representative_run_bundles/manifest.json` |
| Incomplete metadata → explicit blocked/partial (no guess) | **Yes** | REP-003 `blocked` (`unmapped_config_alias`); REP-004 `partial` (placebo geometry); no `declared_estimand_id` from estimator name |
| Default legacy behavior unchanged | **Yes** | `build_run_artifact_bundle(..., include_track_b_views=False)` default; `test_legacy_default_unchanged_without_opt_in` |
| Trust verdicts absent outside TrustReport | **Yes** | `test_no_trust_verdicts_on_adapter_output` (all REP); B5c composer test-only; `geo_adapter` `must_not` lists |
| Production TrustReport intentionally deferred | **Yes** | Roadmap M2.2 **Next**; composer remains `tests/track_b/trust_report_composer.py` only |
| Track D non-production; D1+ not started | **Yes** | `ROADMAP_V4.md` D1–D8 **Planned**; no Track D implementation packages on branch |

---

## 1. North Star Alignment

| # | Answer |
|---|--------|
| 1 | **Platform capability:** Legacy Geo RunBundle evidence can be extracted into governed adapter inputs and optional `track_b_views` without fixture slices. |
| 2 | **Decision risk reduced:** Silent ID guessing on incomplete live metadata; fixture–production adapter gap (AUDIT-002 risk #1). |
| 3 | **Artifacts:** `BundleExtractionResult`, `track_b_views.extraction` provenance, `build_geo_run_artifact_bundle`; consumes B4 registry + explicit `track_b_export_hints`. |
| 4 | **Improves:** Trust boundary (blocked/partial tiers), explainability (extraction notes), governance (cataloged estimator+inference → config_alias only). |
| 5 | **Still missing:** Product GeoX export calling `build_geo_run_artifact_bundle`; production TrustReport (M2.2); Track D statistical audits. |
| 6 | **Component drift?** No — helper export defaults `include_track_b_views=True` but core `build_run_artifact_bundle` remains opt-in `False`. |

**Verdict:** `aligned`

**Required follow-up:** Wire `build_geo_run_artifact_bundle` into primary GeoX export path (or document explicit deferral in M2.2); M2.2 TrustReport product path; Track D D1 only under research lane after team prioritization.

---

## 2. Current Implementation Inventory

| Item | Type | Mode | Prod-eligible? | Track | Status | Limitations |
|------|------|------|----------------|-------|--------|-------------|
| M2.1 bundle extraction | adapter input | implemented + test | no | B | **Complete** | REP fixtures; not all live GeoX shapes |
| M2.1 `build_geo_run_artifact_bundle` | integration helper | implemented + test | no | B | **Complete** | Not yet called from main GeoX export module |
| Representative REP bundles | fixtures | representative shapes | no | B | **Complete** | 5 cases: 3 complete, 1 blocked, 1 partial |
| M2 dual-write / GOLD compare | integration | implemented + test | no | B | Complete | Unchanged by M2.1 |
| B5c TrustReport composer | trust logic | test-only | no | B | Complete | M2.2 target |
| Production TrustReport | trust | not started | no | B | **Deferred** | Roadmap next |
| Track D D1+ | research | doc-only | no | D | **Not started** | Eligible post-gate; research lane |

---

## 3. Architecture Soundness Audit

| # | Finding |
|---|---------|
| 1 | Extraction layer separated from resolution; adapter still facts-only. |
| 2 | No trust verdicts on evidence or adapter output (REP tests + existing B5d F7/F9). |
| 3 | `config_alias` from explicit hint, metadata field, or cataloged `(estimator, inference_mode)` — never from estimand inference. |
| 4 | Missing `config_alias` → extraction `blocked` and adapter `bundle_extraction_incomplete` before registry lookup. |
| 5 | `track_b_views` still sidecar; legacy keys unchanged when opt-out. |

**Verdict:** `architecture_sound`

---

## 4. Conceptual and Causal Validity Audit

M2.1 does not change estimands, estimators, or scoring. Extraction maps existing legacy fields to B4 resolve inputs.

| Case | M2.1 handling |
|------|----------------|
| REP-001 explicit hints | `complete`; explicit `config_alias` |
| REP-002 inference_mode → catalog | `complete`; `estimator+inference_mode` source |
| REP-003 unknown estimator | `blocked`; no alias guess |
| REP-004 placebo + geometry mismatch | `partial`; explicit `partial_reason` path |
| REP-005 legacy target estimand | `complete`; `legacy_mapping_applied` |

**Verdict:** `causally_clear` (export semantics only)

---

## 5. Statistical Robustness Audit

No estimator or inference behavior changed. Track D D1+ not executed.

**Verdict:** `research_only` (unchanged from AUDIT-002)

---

## 6. Literature and Cutting-Edge Grounding Audit

No new methods. Estimator+inference catalog is explicit lookup table in `bundle_extract.py`.

**Verdict:** `literature_grounded` (inherits prior Track B / D0 docs)

---

## 7. Product and Decision Usefulness Audit

Sidecar and extraction are infrastructure. Product decisions still rely on legacy card until M2.2 and GeoX export hook.

**Verdict:** `not_actionable_yet` (expected for M2.1)

---

## 8. Governance and Safety Audit

| # | Finding | Evidence |
|---|---------|----------|
| 1 | AUDIT-002 adapter follow-up closed | This audit + REP suite |
| 2 | Alignment gate M2.1 stop condition met | ≥3 REP bundles; blocked/partial/complete explicit |
| 3 | Eligibility / maturity / release gates untouched | No registry edits in M2.1 commits |
| 4 | Track D remains research lane | Roadmap + no D1 code |
| 5 | 331 tests pass on audited commits | `tests/track_b/` + `test_artifact_schema_compatibility.py` |

**Verdict:** `governed`

### M2.1 stop-condition checklist

| Criterion | Met? | Evidence |
|-----------|------|----------|
| ≥3 representative non-fixture bundles | Yes | 5 REP cases |
| Explicit complete / partial / blocked | Yes | manifest + parametrized tests |
| No trust verdicts on adapter/evidence | Yes | `test_no_trust_verdicts_on_adapter_output` |
| Legacy default unchanged | Yes | `include_track_b_views=False` on `build_run_artifact_bundle` |
| AUDIT-002 follow-up (real-bundle path) | Yes | `extract_resolve_input_from_bundle` + `resolve_geo_adapter_output_from_bundle` |
| Production TrustReport deferred | Yes | M2.2 roadmap; test-only composer |
| Track D D1+ not started | Yes | Planned only |

---

## 9. Missing Dimensions / Gap Discovery

| Gap | Severity | Type | Risk | Action | Track | Blocked by |
|-----|----------|------|------|--------|-------|------------|
| GeoX main export not calling `build_geo_run_artifact_bundle` | medium | integration | Sidecar unused in live export | Hook in GeoX export or M2.2 bundle work | B | M2.2 / export wiring |
| Production TrustReport | high | implementation | Decisions without governed trust layer | M2.2 composer in product path | B | AUDIT-003 gate **passed** |
| Live GeoX shape coverage beyond REP-005 | medium | implementation | Unseen metadata combinations | Add REP cases as discovered | B | Optional M2.1+ |
| Track D D1 design/matching audit | high | statistical | Math/stat claims un audited | Start D1 under **research lane** | D | Team priority (gate open) |
| CalibrationSignal live registry sync | medium | governance | Static `_registry.py` | M2.1+ or catalog sync | B | — |

---

## 10. Recommendations

| # | Class | Recommendation | Stop condition |
|---|-------|----------------|--------------|
| 1 | `production_path` | **Proceed M2.2** — production TrustReport export path (composer behind product boundary) | TrustReport scenarios in product JSON behind feature flag; no verdicts on evidence |
| 2 | `production_path` | Wire `build_geo_run_artifact_bundle` into primary GeoX RunBundle export | One production export path emits `track_b_views` when hints present |
| 3 | `research_lane` | **May begin Track D D1** (design/matching) in parallel — do not treat as production promotion | D1 report + matrix row updates under research lane |
| 4 | `governance_fix` | Defer additional M2.1 hardening unless new live GeoX shapes fail extraction | New REP fixture + test per failure mode |

**Not recommended now:** Broad M2.1 rework — stop conditions met on committed REP coverage.

---

## 11. Final Audit Verdict

**Overall verdict:** `continue_with_minor_corrections`

**Gate outcome:** **AUDIT-003 passed** — M2.1 closes AUDIT-002 follow-up for representative RunBundle adapter wire-up. Track D D1 is **eligible** under research lane but **not required** before M2.2.

**Decision (post-gate):**

| Option | Recommendation |
|--------|----------------|
| **M2.2 production TrustReport** | **Primary** — next production-lane item per roadmap |
| **Track D D1 research start** | **Allowed in parallel** — research lane only; no production promotion |
| **More M2.1 hardening** | **Only if** new live GeoX metadata shapes fail REP-style tests |

**Summary:** M2.1 adds explicit bundle extraction, five representative RunBundle shapes, and a Geo export helper while preserving legacy defaults and the trust boundary. Gaps are narrow: main GeoX export hook and M2.2 remain ahead.

**Top 3 strengths**

1. AUDIT-002 risk #1 addressed with explicit extraction tiers and tests.  
2. No estimand-from-estimator guessing; blocked path preserved.  
3. Committed, test-backed evidence (331 tests) for audit review.

**Top 3 risks**

1. REP fixtures may not exhaust production GeoX metadata variants.  
2. `build_geo_run_artifact_bundle` not yet on main export path.  
3. Statistical validity still pre–Track D D1.

**Top 3 missing pieces**

1. Production TrustReport (M2.2).  
2. GeoX production dual-write hook.  
3. Track D D1 execution (research).

**Next 3 actions**

1. Start **M2.2** — TrustReport in product export (production lane).  
2. Optionally parallel **Track D D1** under research lane (inventory/design audit).  
3. When GeoX export is wired, add one live-shape REP case if metadata differs from REP-001–005.

---

*Audit AUDIT-003 closed 2026-05-28.*
