# METHOD-VALIDATION-PROGRAM-001

**Document ID:** METHOD-VALIDATION-PROGRAM-001  
**Type:** Authoritative method-foundation validation program — **roadmap pivot**  
**Status:** **active** (docs-only)  
**Date:** 2026-06-04  
**Authority:** **Supersedes sequencing** from [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md), AugSynth closeout “next OC” chains, and any doc that treats hardcoded design × estimator × inference tuples as final suitability authority — **without deleting prior evidence**.

**Primary inputs (evidence, not final authority):** [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) · [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · Track D D1–D5 audits · Track F inference/interface work · AugSynth P1–P6 · [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md) · [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) (if on main) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md)

**Related governance (paused for expansion):** F-DECISION-001 · AUDIT-010 · TrustReport · CalibrationSignal · MMM · ADR-001 (pairing roles **frozen** until this program completes layers 1–5)

---

## 1. Purpose

Validate **method foundations** before assigning trust roles, product eligibility, or “primary / secondary / directional / diagnostic” narratives.

The program ensures every **implemented** design, estimator, and inference method is:

1. **Inventoried** from code (not from a legacy combo shortlist)  
2. **Aligned** to literature-prescribed identity, estimand, assumptions, and geometry  
3. **Validated** for implementation and architecture fidelity  
4. **Characterized** statistically under explicit OC protocols  
5. **Combined** only after per-method layers pass — in a governed combination matrix  

**Only after layers 1–5:** build or revise [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`](#9-required-next-artifacts) and **then** allow TrustReport / F-DECISION / CalibrationSignal role expansion.

**This program is not:** a promotion path, a new TrustReport layer, an OC battery in this PR, or permission to change production behavior.

---

## 2. Problem statement

Prior work produced valuable **evidence** — especially AugSynth P1–P6, Track D audits, and Track F interface fixes — but sequencing sometimes **reasoned backward** from repo-native combinations (e.g. SCM+UnitJackKnife, AugSynth+JK, TBRRidge+Kfold) and moved quickly toward **downstream** artifacts (`D5-INST-AUGSYNTH-MULTICELL-001`, combination suitability tables, trust-framework readiness).

That approach is **useful but insufficient**:

| Limitation | Why it matters |
|------------|----------------|
| Hardcoded combo matrix as implicit authority | Treats “what we run today” as “what is valid” before per-method literature + implementation proof |
| Role labels ahead of foundation validation | F-DECISION / AUDIT-010 tuples describe **governance posture**, not completed method-foundation proof |
| AugSynth/multi-cell path too downstream | MCELL OC validates ADR metadata gates, not full multi-cell statistical validity |
| Inventory docs partially stale | [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) and cousins need **code-first** refresh |

**Correction:** Begin from **method identity** and literature assumptions; end at **validated combinations**; assign trust roles last.

---

## 3. Layered validation model

```text
Layer 1 CODE_INVENTORY          →  what exists in repo (complete)
Layer 2 LITERATURE_ALIGNMENT    →  what each family should be
Layer 3 IMPLEMENTATION_VALIDATION →  code matches literature + architecture
Layer 4 STATISTICAL_VALIDATION  →  OC / synthetic worlds per family
Layer 5 COMBINATION_VALIDATION  →  design × estimator × inference matrix
        ↓
DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001
        ↓
TrustReport / F-DECISION / CalibrationSignal / MMM (paused until above)
```

### Layer 1 — Code inventory (`METHOD_CODE_INVENTORY_001`)

| Requirement | Detail |
|-------------|--------|
| **Scope** | All designs, estimators, inference modes, wrappers, orchestration entrypoints, aliases |
| **No hardcoded shortlist** | Discovery from `panel_exp/` code + tests + registry metadata |
| **Per-row fields** | Method name · type · module path · entrypoint · inputs · outputs · geometry · tests · docs · implementation status |
| **Output** | Machine- and human-readable inventory; feeds layers 2–5 |

### Layer 2 — Literature alignment (`METHOD_LITERATURE_ALIGNMENT_001`)

| Requirement | Detail |
|-------------|--------|
| **Per family** | Canonical identity · target estimand · assumptions · supported geometry · valid inference companions · known failure modes · expected diagnostics |
| **Comparison** | Repo implementation vs literature — gaps labeled `literature_aligned` or `literature_mismatch` |
| **References** | Primary papers / canonical texts where possible; cite in alignment register |

### Layer 3 — Implementation and architecture validation (`METHOD_IMPLEMENTATION_VALIDATION_001`)

| Check class | Examples |
|-------------|----------|
| **Algorithm fidelity** | Objective, penalties, weight constraints, outcome leg |
| **Silent estimand shifts** | Level vs relative · aggregate vs unit · percent vs level readout |
| **Data / period leakage** | Pre-period design vs post-period fit · `full_model` paths |
| **Geometry** | Donor restrictions · 2-row aggregate vs unit panel · supergeo/trim bridges |
| **Inference plumbing** | Interval orientation · JK target · pooled-CF semantics · wrapper dispatch |
| **Output** | Per-method `implementation_validated` or `implementation_gap` with evidence links |

### Layer 4 — Statistical validation / OC protocol (`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001`)

| Requirement | Detail |
|-------------|--------|
| **Per method family** | Defined synthetic worlds and batteries |
| **Metrics (family-dependent)** | Bias · MAE · null FPR · coverage · interval width · degeneracy · pre-fit quality · donor stress · shock/outlier sensitivity · placebo behavior · multi-treated behavior |
| **Archives** | JSON + report per battery; no promotion from OC alone |
| **Output** | `statistically_validated` or `statistical_gap` with stratum notes |

### Layer 5 — Combination validation (`METHOD_COMBINATION_VALIDATION_MATRIX_001`)

| Requirement | Detail |
|-------------|--------|
| **Prerequisite** | Layers 1–4 complete for **each** leg of the tuple (or explicit `geometry_limited` / `research_only`) |
| **Per combination** | Geometry · estimand · treatment structure · diagnostics · uncertainty semantics · allowed use (foundation status only) |
| **Explicitly not in layer 5** | Primary/secondary/directional **trust roles** — deferred to suitability framework |
| **Reuse** | Prior D5 combo audits (A01–A30) as **inputs**; reconcile, do not copy roles |

---

## 4. Method universe

Layer 1 must inventory from **code**, including:

| Category | Discovery targets (examples only — not exhaustive) |
|----------|-----------------------------------------------------|
| **Designs** | `panel_exp/design/` registry · geo modes · supergeo · trim · quickblock · matchedpair |
| **Estimators** | `panel_exp/methods/` · `method_metadata.py` catalog · aliases (`SCM` → CVXPY path) |
| **Inference** | `panel_exp/inference/` · registry modes · estimator-embedded bootstrap |
| **Wrappers** | AugSynth classes · rerandomization wrapper · inference dispatch |
| **Orchestration** | `run_design` · `GeoExperimentDesign` · validation harness entrypoints |
| **Research / archived** | TROP · MTGP · SyntheticDID · Bayesian paths · skipped runner methods |
| **Duplicates** | TBR vs TBRRidge · AugSynth vs AugSynthCVXPY · registry vs production names |

**Rule:** The final universe list lives in **`METHOD_CODE_INVENTORY_001`**, not in this program doc.

---

## 5. Evidence reuse policy

Prior artifacts are classified — **not deleted**.

| Artifact / category | Classification | Notes |
|---------------------|----------------|-------|
| **AugSynth P1–P6** (D5-DIAG … P6 design compat) | `evidence_input` | Implementation facts, OC strata, failure modes — **not** final combo suitability |
| **`AUGSYNTH_ASCM_LANE_CLOSEOUT_001`** | `evidence_input` · `superseded_for_sequencing` | Historical closeout; MCELL-first chain superseded by this program |
| **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** | `evidence_input` · `still_authoritative` (semantics only) | **Semantic guardrail** for pooled claims — **not** statistical validity proof |
| **`METHOD_FOUNDATION_SYNTHESIS_001`** | `evidence_input` · `superseded_for_sequencing` | Retained combination map; **do not** use §7 MCELL proceed as roadmap authority |
| **`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001`** | `evidence_input` · `needs_reconciliation` | Inventory tables refreshed under Layer 1 |
| **`METHOD_SOUNDNESS_ROADMAP_REVIEW_001`** | `superseded_for_sequencing` | DL-1 “active lane” prioritization superseded |
| **`METHOD_FOUNDATION_HARDENING_001`** | `evidence_input` | Gap taxonomy; LLM pause remains valid |
| **Track D D1–D5 audits** | `evidence_input` | Design, estimator, inference, power, conceptual validity |
| **Track D D5 OC archives** | `evidence_input` | Stratified metrics; reconcile into Layer 4 protocol |
| **Track F F-INF / interface fixes** | `evidence_input` · `still_authoritative` (contract) | Interval semantics contract remains — **no new role expansion** |
| **`F_DECISION_001` / AUDIT-010 / TrustReport package** | `paused_downstream` | **Frozen** for new method-role expansion until layers 1–5 |
| **`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001`** | `still_authoritative` (pairing guardrail) | Diagnostic pairing — not promotion |
| **TBR / TBRRidge audits** | `evidence_input` | Aggregate vs unit; JK FPR characterization |
| **Supergeo / trim investigations** | `evidence_input` | Bridge required before combo claims |
| **Design/matching audits (D1, INV-D1-001)** | `evidence_input` | Leakage findings; caller obligations |
| **Method inventory/matrix docs** | `needs_reconciliation` | Superseded as **complete** inventory until CODE_INVENTORY lands |

**Rule:** No prior **role/suitability framework** is authoritative for **new** method expansion until **`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`** is built on validated layers 1–5.

---

## 6. Superseded / retained / paused artifacts

| Status | Meaning |
|--------|---------|
| **`retained`** | Keep in repo; cite as evidence; may contain facts, simulations, failure modes |
| **`superseded_for_sequencing`** | Do not use “next step” or “proceed to OC X” from this doc as roadmap authority |
| **`paused_downstream`** | No expansion until this program completes required layers |
| **`still_authoritative`** | Narrow scope only (e.g. pooling semantics, F-INF contract, pairing ADR guardrails) |
| **`needs_reconciliation`** | Must be merged into Layer 1–5 outputs |

**Explicit:** D5 / Track F / AugSynth audits are **evidence**, not final authority for method suitability.

---

## 7. Validation status taxonomy

Use **foundation** statuses only — **not** primary/secondary/directional trust roles.

| Status | Meaning |
|--------|---------|
| `not_inventoried` | Not yet in CODE_INVENTORY |
| `inventoried_unreviewed` | Listed in code; no literature row |
| `literature_aligned` | Literature row matches intended method |
| `literature_mismatch` | Documented gap vs canonical method |
| `implementation_validated` | Layer 3 pass for stated scope |
| `implementation_gap` | Layer 3 failure or caveat blocking claims |
| `statistically_validated` | Layer 4 OC pass for stated scope/strata |
| `statistical_gap` | OC failure, unsafe stratum, or missing battery |
| `geometry_limited` | Valid only on named geometry (e.g. aggregate 2-row) |
| `research_only` | Not production-validation target |
| `deprecated_or_quarantine` | Do not use in new product paths |

Combination rows add: `combination_validated` · `combination_blocked` · `combination_needs_battery` (defined in Layer 5 artifact).

---

## 8. Explicit pause rules

Until **`METHOD_COMBINATION_VALIDATION_MATRIX_001`** completes and suitability framework is drafted:

| Paused activity | Rationale |
|-----------------|-----------|
| **New TrustReport method-role expansion** | Roles require validated combinations |
| **New F-DECISION method-role expansion** | Same |
| **New CalibrationSignal eligibility expansion** | Same |
| **MMM ingestion expansion** | Same |
| **LLM decision-layer method recommendations** | AUDIT-011 remains paused |
| **Promotion audit** for any combination | No promotion without Layer 4–5 proof |
| **Default next step = `D5-INST-AUGSYNTH-MULTICELL-001`** | Demoted — see §9 |

**Not paused:** Bug fixes · contract fixes (e.g. F-INF) · docs that **do not** expand roles · running existing archived OC for evidence · narrow ADR semantic guardrails already merged.

---

## 9. Treatment of AugSynth / multi-cell work

| Topic | Posture under this program |
|-------|----------------------------|
| **AugSynth P1–P6** | **Retained** as rich `evidence_input` (diagnostics, fidelity, ASCM-003, JK, Conformal, design compat) |
| **AugSynth point** | Still **promising** in characterized strata — **not promoted** |
| **AugSynth + JK** | **Unresolved** inference (`jk_unsafe_under_diagnostics`); diagnostic-only |
| **AugSynth + Conformal** | **Blocked** pending new interval design |
| **Pooling ADR** | If on main: **semantic guardrail** for S0/S1 wording — **not** proof of statistical validity |
| **`D5-INST-AUGSYNTH-MULTICELL-001`** | **Paused** as default next step; may reopen later as **optional** ADR metadata gate regression only — **not** method-suitability validation |
| **DL-1 lane** | **Closed** historically; no new DL-1 execution without explicit program scope |

---

## 10. Required next artifacts

**Authoritative sequence:**

| Order | Artifact | Layer |
|-------|----------|-------|
| **1** | **`METHOD_CODE_INVENTORY_001`** | 1 |
| **2** | **`METHOD_LITERATURE_ALIGNMENT_001`** | 2 |
| **3** | **`METHOD_IMPLEMENTATION_VALIDATION_001`** | 3 |
| **4** | **`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001`** | 4 |
| **5** | **`METHOD_COMBINATION_VALIDATION_MATRIX_001`** | 5 |
| **6** | **`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`** | Post-5 — role-ready combo map |
| **7** | TrustReport / F-DECISION / CalibrationSignal integration | After 6 |

**Layer 1:** ✅ [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) + [`track_d/archives/METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json) (regenerate: `python -m panel_exp.validation.method_code_inventory_001`).

**Layer 2:** ✅ [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) + [`track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json`](track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json) (regenerate: `python -m panel_exp.validation.method_literature_alignment_001`).

**Layer 3:** ✅ [`METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md) + [`track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json`](track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json) (regenerate: `python -m panel_exp.validation.method_implementation_validation_001`).

**Layer 4:** ✅ [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) + [`track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json`](track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json) (regenerate: `python -m panel_exp.validation.method_statistical_validation_protocol_001`).

**Layer 5:** ✅ [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) + [`track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json`](track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json) (regenerate: `python -m panel_exp.validation.method_combination_validation_matrix_001`).

**Suitability framework:** ✅ [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) + [`track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json`](track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json) (regenerate: `python -m panel_exp.validation.design_estimator_inference_suitability_framework_001`).

**First D5-STAT smoke execution:** ✅ [`docs/track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) + [`track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json`](track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json) (regenerate: `python -m panel_exp.validation.track_d_d5_stat_smoke_callable_001`).

**SCM+JK Level B characterization:** ✅ [`docs/track_d/D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) + [`track_d/archives/D5_STAT_SCM_JK_001_results.json`](track_d/archives/D5_STAT_SCM_JK_001_results.json) (regenerate: `python -m panel_exp.validation.track_d_d5_stat_scm_jk_001`).

**AugSynth point Level B:** ✅ [`docs/track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) + [`track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json`](track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json) (regenerate: `python -m panel_exp.validation.track_d_d5_stat_augsynth_point_001`).

**Immediate next concrete work:** **`D5-STAT-TBR-AGG-001`** per Layer 5 queue (no TrustReport/F-DECISION wiring until further OC evidence exists).

---

## 11. Roadmap implications

| Prior roadmap text | New posture |
|------------------|-------------|
| Foundation synthesis → MCELL OC | **Superseded** — synthesis retained as evidence map only |
| Closeout → pooling ADR → MCELL | Pooling ADR **retained** if merged; MCELL **not** default |
| DL-1 “active lane” | **Complete** — no longer authoritative for repo-wide sequencing |
| METHOD-SOUNDNESS “next = MCELL” | **Replaced** by Layer 1–5 table above |
| Trust-framework / role expansion | **Paused** per §8 |

---

## 12. Guardrails

- **No code behavior change** in this PR  
- **No estimator / inference changes**  
- **No OC execution** in this PR  
- **No promotion** or demotion  
- **No eligibility / governed-uncertainty allowlist change**  
- **No TrustReport / F-DECISION / CalibrationSignal / MMM change**  
- **No LLM integration**  
- **Docs / roadmap only**  

---

## 13. Stop condition

| Criterion | Status |
|-----------|--------|
| Authoritative program doc exists | ✅ |
| Prior artifacts classified (§5–§6) | ✅ |
| Layered model defined (§3) | ✅ |
| Trust-framework expansion paused (§8) | ✅ |
| Roadmap/registry updated to point to Layer 1 next | ✅ (companion doc edits) |
| MCELL demoted from default next step | ✅ |

---

*METHOD-VALIDATION-PROGRAM-001 v1.0.0 — roadmap authority for method-foundation work; evidence artifacts retained.*
