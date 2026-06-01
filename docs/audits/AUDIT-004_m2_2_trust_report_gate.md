# AUDIT-004 — M2.2 production TrustReport sidecar gate

**Audit ID:** AUDIT-004  
**Date:** 2026-05-28  
**Auditor:** MIP periodic audit (committed-code review + test evidence)  
**Milestone reviewed:** M2.2 production TrustReport sidecar wiring  
**Commit / branch:** `ec2d351` on `fix-kfold-multitreated-geometry`  
**Scope:** `panel_exp/track_b/trust_report.py`, `dual_write.py`, `export.py`; `panel_exp/artifacts/run_bundle.py`, `geo_run_export.py`; `panel_exp/design/geo_experiment_design.py`; `tests/track_b/test_m2_2_trust_report_export.py`; B5 boundary tests  

**Gate purpose:** Confirm production-wired, opt-in TrustReport on `track_b_views` before Track D D1 (research lane) or further Track B promotion work.

---

## Gate checklist (AUDIT-004 key checks)

| Check | Result | Evidence |
|-------|--------|----------|
| TrustReport verdicts only under `trust_report_view.scenarios` | **Yes** | `test_verdicts_only_on_trust_report_view`; `geo_adapter` `must_not`; REP/M2.1 boundary tests |
| Missing scenarios → explicit omit (no guess) | **Yes** | `trust_report_omit_reason: missing_trust_scenarios`; `test_missing_scenarios_explicit_omit` |
| Legacy export defaults remain off | **Yes** | `build_run_artifact_bundle` / `export_geo_run_bundle` default `include_track_b_views=False`, `include_trust_report=False`; `test_legacy_bundle_default_unchanged` |
| Representative complete/partial/blocked still work | **Yes** | M2.1 REP suite + M2.2 blocked/partial TrustReport paths (`test_blocked_adapter_not_assessable`, `test_partial_export_lift_unsupported`) |
| Main GeoX export path wired | **Yes** | `export_geo_run_bundle`; `GeoExperimentDesign.export_run_readout_bundle` |
| No estimator/scoring/eligibility/maturity changes | **Yes** | Diff scope Track B + artifacts export only; no changes under `methods/`, `policy/`, eligibility registry |
| Track D still not started | **Yes** | D1–D8 **Planned** in roadmap; no Track D implementation on branch |

---

## 1. North Star Alignment

| # | Answer |
|---|--------|
| 1 | **Platform capability:** Opt-in Geo RunBundle export can attach governed `track_b_views` with adapter facts and TrustReport verdicts on declared scenarios. |
| 2 | **Decision risk reduced:** Trust outcomes leaking onto evidence/adapter layers; silent TrustReport when scenarios are unknown. |
| 3 | **Artifacts:** `trust_report_view` on sidecar; production `panel_exp/track_b/trust_report.py`; consumes M2/M2.1 adapter output. |
| 4 | **Improves:** Trust (bounded verdict layer), explainability (explicit omit reasons), governance (opt-in composition). |
| 5 | **Still missing:** Decision-grade product UI consuming TrustReport; full live GeoX run coverage beyond REP/GOLD; Track D statistical evidence. |
| 6 | **Component drift?** No — TrustReport is opt-in and scenario-gated; legacy bundle unchanged by default. |

**Verdict:** `aligned`

**Required follow-up:** Product consumers must opt in explicitly; Track D D1 may start under research lane; optional `__init__.py` re-exports for public API ergonomics.

---

## 2. Current Implementation Inventory

| Item | Type | Mode | Prod-eligible? | Track | Status | Limitations |
|------|------|------|----------------|-------|--------|-------------|
| M2.2 production TrustReport | trust composition | implemented + test | opt-in only | B | **Complete** | Requires scenarios; not decision UI |
| `export_geo_run_bundle` | Geo export | implemented + test | opt-in | B | **Complete** | Defaults off |
| `GeoExperimentDesign.export_run_readout_bundle` | Geo hook | implemented | opt-in | B | **Complete** | Needs `last_evidence` |
| B5c test composer wrapper | tests | delegates to prod | n/a | B | Complete | Oracle unchanged |
| M2 / M2.1 sidecar | integration | complete | opt-in | B | Complete | Unchanged behavior |
| Track D D1+ | research | doc-only | no | D | **Not started** | Eligible post-gate |

---

## 3. Architecture Soundness Audit

| # | Finding |
|---|---------|
| 1 | Interpretation rules live in `panel_exp/track_b/trust_report.py`; tests delegate — single source of truth. |
| 2 | `attach_trust_report_to_views` mutates sidecar only; adapter/evidence views unchanged. |
| 3 | Verdict fields confined to `trust_report_view.scenarios[]`. |
| 4 | `include_trust_report` without scenarios records omit reason — no fabricated verdicts. |
| 5 | Core `build_run_artifact_bundle` defaults preserve pre-M2.2 behavior. |

**Verdict:** `architecture_sound`

---

## 4. Conceptual and Causal Validity Audit

M2.2 does not change estimands, estimators, or inference. TrustReport interprets existing adapter facts per B5c rules (GOLD oracles still authoritative in tests).

**Verdict:** `causally_clear`

---

## 5. Statistical Robustness Audit

No statistical claims added. Trust outcomes are governance interpretations, not power/OC results.

**Verdict:** `research_only` (unchanged)

---

## 6. Literature and Cutting-Edge Grounding Audit

Inherits B2/B5 contract docs; no new methods.

**Verdict:** `literature_grounded`

---

## 7. Product and Decision Usefulness Audit

TrustReport is exportable but not yet surfaced in product decision UI. Opt-in sidecar is infrastructure for downstream consumers.

**Verdict:** `not_actionable_yet` at UI layer (expected); export path is **actionable for integrators** who opt in.

---

## 8. Governance and Safety Audit

| # | Finding | Evidence |
|---|---------|----------|
| 1 | AUDIT-003 follow-ups closed (TrustReport prod + Geo export hook) | This audit |
| 2 | Trust boundary preserved | M2.2 + B5 tests |
| 3 | Eligibility/maturity/release gates untouched | Scope diff |
| 4 | 338 Track B + artifact tests pass | `ec2d351` |
| 5 | Track D not started | Roadmap + branch scan |

**Verdict:** `governed`

### M2.2 stop-condition checklist

| Criterion | Met? | Evidence |
|-----------|------|----------|
| Opt-in TrustReport on `track_b_views` | Yes | `include_trust_report=True` |
| Verdicts only on TrustReport scenarios | Yes | M2.2 + boundary tests |
| Missing scenarios explicit omit | Yes | `missing_trust_scenarios` |
| Legacy default off | Yes | export defaults + schema test |
| GOLD-001 oracle parity via export | Yes | `test_gold_001_export_matches_oracle` |
| GeoX export entry wired | Yes | `geo_run_export` + `GeoExperimentDesign` |
| No estimator/scoring changes | Yes | Scope |

---

## 9. Missing Dimensions / Gap Discovery

| Gap | Severity | Type | Risk | Action | Track |
|-----|----------|------|------|--------|-------|
| Public `__init__.py` re-exports not in `ec2d351` | low | packaging | Import ergonomics | Commit `track_b/__init__.py`, `artifacts/__init__.py` | B |
| Product UI / card does not read TrustReport | medium | product | Users ignore sidecar | Consumer wiring post-M2.2 | B/C |
| Live GeoX runs without `trust_scenarios` hints | medium | integration | Omit-by-default | Document scenario contract for exporters | B |
| Track D D1+ | high | statistical | Math lies undetected | D1 under research lane | D |

---

## 10. Recommendations

| # | Class | Recommendation |
|---|-------|----------------|
| 1 | `production_path` | Commit remaining `__init__.py` / M2.1 test default alignment if not on branch |
| 2 | `research_lane` | **May begin Track D D1** (design/matching) — parallel, not blocking |
| 3 | `governance_fix` | Keep TrustReport opt-in until product consumer and scenario catalog are defined |

---

## 11. Final Audit Verdict

**Overall verdict:** `continue_with_minor_corrections`

**Gate outcome:** **AUDIT-004 passed** — M2.2 delivers production-wired, opt-in, bounded TrustReport on the Track B sidecar.

**Post-gate decision**

| Path | Recommendation |
|------|----------------|
| **Track D D1** (research) | Allowed in parallel |
| **Track B consumer wiring** | Next product integration when ready |
| **Promotion / eligibility** | Not until Track D + promotion bridge |

**Top 3 strengths**

1. Trust boundary enforced in production module, not test-only.  
2. Explicit omit path when scenarios missing.  
3. Geo export path unified (`export_geo_run_bundle` + design hook).

**Top 3 risks**

1. Integrators may enable sidecar without supplying scenarios (omit-only).  
2. Statistical validity still pre–Track D.  
3. Minor packaging files may lag commit `ec2d351`.

**Next 3 actions**

1. Close M2.2 on roadmap; schedule **AUDIT-005** (or registry row) for Track D D1 when started.  
2. Optionally commit `__init__.py` re-exports.  
3. Begin Track D D1 under research lane when resourced.

---

*Audit AUDIT-004 closed 2026-05-28.*
