# AUDIT-002 — M2 dual-write on RunBundle

**Audit ID:** AUDIT-002  
**Date:** 2026-05-28  
**Auditor:** MIP periodic audit (automated evidence + engineering review)  
**Milestone reviewed:** M2 dual-write + geo adapter  
**Commit / branch:** `2754c0a` on `fix-kfold-multitreated-geometry`  
**Scope:** `panel_exp/track_b/`, `panel_exp/artifacts/run_bundle.py`, adapter compare tests, B5d validator on resolved output  

---

## 1. North Star Alignment

| # | Answer |
|---|--------|
| 1 | **Platform capability:** Real GeoX RunBundle exports can carry governed Track B `track_b_views` sidecar alongside legacy evidence/card. |
| 2 | **Decision risk reduced:** Silent reliance on legacy-only artifacts; estimand/instrument drift without auditable adapter layer. |
| 3 | **Artifacts:** Creates `track_b_views` (spec view, adapter_output, evidence/diagnostic views); consumes B2/B4 identity rules; validates against B5a oracles. |
| 4 | **Improves:** Trust (boundary), explainability (explicit IDs), governance (blocked/partial/complete export tiers). |
| 5 | **Still missing for production/decisioning:** Production TrustReport composer path; adapter extraction from all real GeoX run shapes; Track D statistical evidence. |
| 6 | **Component drift?** No — sidecar is explicitly opt-in and tied to contract tests. |

**Verdict:** `aligned`

**Required follow-up:** Production adapter wire-up on representative non-fixture RunBundles; AUDIT-003 before Track D D1 execution.

---

## 2. Current Implementation Inventory

| Item | Type | Mode | Prod-eligible? | Track | Status | Limitations |
|------|------|------|----------------|-------|--------|-------------|
| B5a golden fixtures | contracts | fixture-only | no | B | Complete | Oracle truth |
| B5c TrustReport composer | trust logic | test-only | no | B | Complete | Not in product export |
| B5d contract validator | governance | test-only | no | B | Complete | CLI on fixtures |
| M2 geo adapter | adapter | implemented + test | no | B | **Complete** | Fixture slice + bundle extract path |
| M2 dual-write on RunBundle | integration | implemented + test | no | B | **Complete** | Opt-in `include_track_b_views` |
| Live adapter compare | tests | test | n/a | B | **Complete** | 14/14 GOLD cases pass |
| Production TrustReport | trust | doc-only | no | B | Not started | M3+ |
| Track D D1+ audits | research | doc-only | no | D | Not started | Gated post-M2 |

---

## 3. Architecture Soundness Audit

| # | Finding |
|---|---------|
| 1 | **Separated:** Adapter emits facts only; TrustReport composer remains test-layer; no verdicts on evidence. |
| 2 | **No layer bleed observed** in M2 code paths. |
| 3 | **Identity explicit** via registry tables (`estimand_id`, `measurement_instrument_id`, `interval_semantics`, geometry). |
| 4 | **Non-breaking:** `track_b_views` omitted from bundle dict when absent; `test_run_bundle_schema_stable` passes. |
| 5 | **Restricted methods** unchanged; eligibility registry untouched. |
| 6 | **Registry:** This audit + `MIP_AUDIT_REGISTRY.md`; not chat-only. |

**Verdict:** `architecture_sound`

---

## 4. Conceptual and Causal Validity Audit

M2 does not change estimands or estimators. Adapter encodes existing GOLD semantics:

| Pairing | M2 handling |
|---------|-------------|
| Geo relative ATT vs MMM Δμ | MMM fields on evidence; intake blocked without transform (GOLD-004) |
| DID cumulative vs relative ATT | `scale_compatible=false` (GOLD-008) |
| Placebo band vs CI | `interval_semantics=placebo_band`; F3 guard |
| Point vs interval | `interval_semantics=none`; no fake CI (GOLD-003) |
| A/B aggregation drift | `aggregation_divergence_detected` (GOLD-009) |

**Verdict:** `causally_clear` (for contract export semantics; not re-auditing estimator math)

---

## 5. Statistical Robustness Audit

M2 does not claim statistical validity. No estimator behavior changed.

| Check | Result |
|-------|--------|
| OC / FPR / power | Unchanged — Track D D1+ not started |
| Method promotion | None |

**Verdict:** `research_only` (export layer only; statistical support remains Track D)

---

## 6. Literature and Cutting-Edge Grounding Audit

No new methods introduced. Registry maps mirror B3a/B5a fixtures.

**Verdict:** `literature_grounded` (inherits D0/D0b; no new claims)

---

## 7. Product and Decision Usefulness Audit

| # | Finding |
|---|---------|
| 1–7 | **Not decision-useful yet** at product surface — sidecar is infrastructure for future TrustReport/MMM consumers. |

**Verdict:** `not_actionable_yet` (infrastructure milestone — expected)

---

## 8. Governance and Safety Audit

| # | Finding | Evidence |
|---|---------|----------|
| 1 | No orphan findings from M2 | Tests + this audit |
| 2–3 | Deferred/investigations unchanged | No code changes |
| 4 | M2 stop conditions met | See checklist below |
| 5–7 | Lanes separated; gates unchanged | No eligibility/maturity edits |
| 8 | MMM/planning not fed | Adapter only |
| 9 | No LLM surface | N/A |

**Verdict:** `governed`

### M2 stop-condition checklist (alignment gate)

| Criterion | Met? | Evidence |
|-----------|------|----------|
| RunBundle carries governed `track_b_views` | Yes | `test_gold_001_representative_bundle_carries_track_b_views` |
| B5 adapter compare on live export | Yes | 14 parametrized tests in `TestAdapterOutputMatchesOracle` (0 skipped) |
| Legacy default unchanged | Yes | `test_run_bundle_schema_stable`; no `track_b_views` key when opt-out |
| Opt-in sidecar only | Yes | `include_track_b_views=False` default |
| No trust verdicts on adapter/evidence | Yes | B5c boundary + B5d F7/F9 |
| Unmapped config blocks | Yes | `unmapped_config_alias` block_reason in geo_adapter |
| 313 tests pass | Yes | `tests/track_b/` + artifact schema |

---

## 9. Missing Dimensions / Gap Discovery

| Gap | Severity | Type | Risk | Action | Track | Blocked by |
|-----|----------|------|------|--------|-------|------------|
| Production TrustReport path | high | implementation | Decisions still use legacy card only | Wire composer after adapter hardening | B | M3 scope |
| Adapter on all real RunBundle shapes | high | implementation | Fixture-only slice may miss GeoX metadata | Harden `extract_resolve_input_from_bundle` | B | Representative runs |
| Track D D1+ not started | high | statistical | Math/stat lies undetected | Begin D1 under research lane | D | AUDIT-002 complete |
| CalibrationSignal live registry | medium | governance | Static tables in `_registry.py` | Catalog sync / dual-write ref | B | M2.1 |
| MMM intake product path | medium | product | No user-facing transform flow | After B5 MMM fixtures in prod | C/B | TrustReport prod |

---

## 10. Recommendations

| # | Class | Recommendation | Stop condition |
|---|-------|----------------|--------------|
| 1 | `production_path` | Harden `resolve_adapter_output` on representative real RunBundles (not only GOLD slice) | ≥3 real bundles match or explicit partial/blocked |
| 2 | `production_path` | Hook GeoX export to `include_track_b_views=True` when spec+stub available | Opt-in dual-write in one production export path |
| 3 | `research_lane` | Start Track D D1 design/matching audit **after** item 1 | D1 package + matrix row updates |
| 4 | `governance_fix` | Keep TrustReport composer test-only until AUDIT-003 | No verdicts in product JSON |

---

## 11. Final Audit Verdict

**Overall verdict:** `continue_with_minor_corrections`

**Summary:** M2 successfully moves Track B from fixture-only to an opt-in RunBundle sidecar with live adapter oracle parity. Legacy behavior is preserved by default. Gaps are explicit and expected: production TrustReport and Track D robustness work remain ahead.

**Top 3 strengths**

1. Executable trust boundary preserved while adding real export path.  
2. Golden oracles drive adapter — no silent guessing (`unmapped_config_alias` blocks).  
3. Clean non-breaking bundle integration.

**Top 3 risks**

1. Fixture slice may not cover all GeoX inference_metadata shapes.  
2. Statistical validity still un audited (Track D).  
3. Product may ignore `track_b_views` until wire-up is explicit.

**Top 3 missing pieces**

1. Production TrustReport.  
2. Real-run adapter hardening.  
3. Track D D1+ execution.

**Next 3 actions**

1. Mark M2 complete on roadmap; set next item to adapter production wire-up.  
2. Run representative RunBundle adapter hardening.  
3. Schedule Track D D1 under research lane (do not skip AUDIT gate).

---

*Audit AUDIT-002 closed 2026-05-28.*
