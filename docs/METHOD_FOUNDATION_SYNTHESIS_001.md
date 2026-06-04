# METHOD-FOUNDATION-SYNTHESIS-001

**Document ID:** METHOD-FOUNDATION-SYNTHESIS-001  
**Type:** Foundation synthesis / decision checkpoint — **evidence consolidation only**  
**Status:** **complete** (docs-only)  
**Date:** 2026-06-03  
**Verdict:** Prior design, estimator, inference, and AugSynth/ASCM audits are **sufficient to sequence next work**; remaining gaps are **targeted** (literature, bridges, narrow OC) — not a new framework layer and **not promotion**.

**Primary inputs:** [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md) · [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) · [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) · [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md) · [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) · [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) · [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md) · [`track_d/D5_DES_SUPERGEO_001_REPORT.md`](track_d/D5_DES_SUPERGEO_001_REPORT.md) · [`track_d/D5_INST_TBR_001_REPORT.md`](track_d/D5_INST_TBR_001_REPORT.md) · [`track_d/archives/D5_POW_001c_results.json`](track_d/archives/D5_POW_001c_results.json) · [`F_INF_003_INTERVAL_ORIENTATION_FIX.md`](F_INF_003_INTERVAL_ORIENTATION_FIX.md) · [`GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md`](GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md)

**Related governance:** F-DECISION-001 · AUDIT-010 · ADR-001 · F-P0-006 · F-GEO-001 · E-DES-MCELL-011

---

## 1. Purpose

Consolidate **prior audits and OC artifacts** into one **foundation map** (design × estimator × inference × geometry) before further method development or broad OC expansion.

This document:

1. **Reuses** existing evidence — no re-audit, no new OC, no new eligibility decisions  
2. States **stable conclusions** already proved in-repo  
3. Registers **remaining** conceptual, implementation, literature-alignment, and OC gaps only where evidence is missing or blocked  
4. Decides whether **`D5-INST-AUGSYNTH-MULTICELL-001`** should proceed as **ADR-gate validation only**

**This is not:** a new framework layer, a promotion artifact, a literature review, or permission to change TrustReport / F-DECISION / CalibrationSignal / MMM / governed-uncertainty policy.

**Why this step now:** Enough audits exist that a full re-review would be wasteful; not enough reconciled synthesis exists to justify a broad “use this combo” product framework. Sequence: **existing audits → synthesis → targeted gaps → narrow next validation**.

---

## 2. Evidence inventory reused

| Artifact | Type | What it contributes to this synthesis |
|----------|------|--------------------------------------|
| [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) | Phase plan | LLM paused; hardening before decision layer; gap IDs GAP-* |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Inventory + lanes | Estimator/inference/design tables; A01–A30; DL-0–DL-8 sequencing |
| [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) | Checkpoint | DL-1 AugSynth lane selected; D5-DIAG first code PR |
| [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) | Design audit | Matching vs readout period alignment; MAT-004 deferral |
| [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) | Execution roadmap | P1–P6 PR sequence and gap table |
| [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md) | Fidelity audit | G1/G4/G7/G8 implementation caveats; ASCM cleared |
| [`track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md) | Diagnostics code | D5-DIAG field schema |
| [`track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md) | OC | 19-world stratified point/JK; `promising_needs_inference_calibration` |
| [`track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md) | Inference OC | `jk_unsafe_under_diagnostics`; W8 unsafe |
| [`track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md) | Failure analysis | `conformal_blocked_pending_new_design` |
| [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) | Compatibility | Per-cell only; bridges; greedy OC-validated |
| [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md) | Lane closeout | DL-1 closed; blockers BLK-*; ordered ADRs before MCELL OC |
| [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) | ADR | S0 default; S1 descriptive v0; no pooled causal/uncertainty |
| [`track_d/D5_DES_SUPERGEO_001_REPORT.md`](track_d/D5_DES_SUPERGEO_001_REPORT.md) | Design OC | Supergeo separate geometry; MILP scope mismatch |
| [`track_d/D5_INST_TBR_001_REPORT.md`](track_d/D5_INST_TBR_001_REPORT.md) | OC | Aggregate 1×1 TBR restricted diagnostic |
| [`track_d/archives/D5_POW_001c_results.json`](track_d/archives/D5_POW_001c_results.json) | OC archive | 2-row aggregate power path; TBRRidge agg2 vs SCM+JK readout |
| [`F_INF_003_INTERVAL_ORIENTATION_FIX.md`](F_INF_003_INTERVAL_ORIENTATION_FIX.md) | Fix | Conformal/TS-Kfold orientation; not governed export |
| [`GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md`](GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md) | Governance | F-DECISION / TrustReport boundaries unchanged |
| [`track_d/D5_MCELL_001_REPORT.md`](track_d/D5_MCELL_001_REPORT.md) | OC | SCM+JK per-cell; k≥3 degraded; pooled blocked pre-ADR |

---

## 3. Current stable conclusions

Reconciled from inputs above — **no new decisions**.

| Conclusion | Evidence hook |
|------------|---------------|
| **SCM + UnitJackKnife (A26)** is the **safest governed baseline** for unit-panel geo designs | AUDIT-010 A26 · D5-POW-001e · F-DECISION-001 |
| A26 is **null-monitor only** — not lift/MDE/CalibrationSignal primary | AUDIT-010 · ADR-001 |
| **AugSynthCVXPY point** is **promising as diagnostic comparator** on greedy unit-panel geometry | ASCM-003 · lane closeout |
| **AugSynth + UnitJackKnife** is **diagnostic-only** — unsafe stratum `W8_post_period_shock` (elevated null FPR) | JK calibration-001 · ADR-001 |
| **AugSynth + Conformal** is **blocked** pending **new interval design** (construction + exchangeability), not geometry-only fix | Conformal failure-001 · ADR-001 |
| **Multi-cell AugSynth** is **per-cell diagnostic by default (S0)** | P6 · pooling ADR §13 |
| **Descriptive pooling** allowed only under **`pooling_rule_id=MULTICELL_AUGSYNTH_DESCRIPTIVE_V0`** with §9–§10 gates (equal-cell level mean; **non-causal**) | Pooling ADR |
| **Pooled causal lift** and **pooled uncertainty** remain **forbidden** for AugSynth multi-cell | Pooling ADR §8 · P4/P5 |
| **TBR / TBRRidge aggregate paths** are **diagnostic/restricted** — **not** unit-panel SCM/AugSynth substitutes | TBR-001 · POW-001c · COMBO audit |
| **2-row aggregate proxy** (agg2 / PowerAnalysis default) is **not equivalent** to unit-level governed readout (SCM+JK / AugSynth diagnostic) | D5-POW-001a/c · METHOD-SOUNDNESS §2.C |
| **Supergeo** and **trimmedmatch** require **geometry/estimand bridges** before SCM/AugSynth claims | SUPERGEO-001 · TRIM-001 · P6 |
| **Only `greedy_match_markets`** is **OC-validated** for AugSynth at ASCM-003 depth; other tier-1 geo methods structurally compatible but **not OC-validated** | P6 compatibility table |
| **Promotion audit** not opened; AugSynth role **`diagnostic_comparator`** unchanged | ASCM-003 · lane closeout |
| **F-INF-003** fixed interval **orientation** for Conformal/TS-Kfold — bands remain **not governed uncertainty** | F-INF-003 · POSTFIX context |
| **INV-D1-001** (pre-period matching leakage) **fixed** for characterized OC baselines when `pre_treatment_period` passed | D5-DES-001a · POW-001c JSON |

---

## 4. Combination map

Columns summarize **repo evidence today**. `literature_alignment_status`: **aligned** = no open targeted lit check for this tuple; **needs_targeted_review** = queue §5; **blocked** = no valid tuple without bridge ADR.

| design_geometry | estimator | inference | estimand_supported | internal_evidence | literature_alignment_status | implementation_gap | OC_gap | current_allowed_use | blocker | recommended_next_action |
|-----------------|-----------|-----------|------------------|-------------------|----------------------------|--------------------|--------|---------------------|---------|-------------------------|
| **greedy unit-panel single-cell** | SCM | UnitJackKnife | Unit-level ATT / null-monitor framing (A26) | 001e · POW-001e · ASCM-002/003 reference | **aligned** (baseline) | `full_model` post-fit risk (D2); weak-fit labels provisional | Failure-mode metadata hardening | **Governed null-monitor** (`ready_limited_governed_use`) | Not lift/MDE/CS primary | Maintain A26; SCM diagnostic threshold calibration |
| **greedy unit-panel single-cell** | AugSynthCVXPY | point | Level point diagnostic (G7 caveat) | ASCM-003 · D5-DIAG | **needs_targeted_review** (augmented SCM estimand) | G4 D1 SCM leg; G7 level vs relative; G8 hull proxy; G1 unused penalty | Non-greedy designs not OC-validated | **Diagnostic comparator** | Outside-hull W3 unreliable; scale vs A26 | **D5-MCELL** N/A; estimand bridge ADR; optional design-compat OC |
| **greedy unit-panel single-cell** | AugSynthCVXPY | UnitJackKnife | Same point path + JK intervals (not A26-equivalent) | JK calibration-001 | **needs_targeted_review** (JK on augmented SCM) | Same G4/G7/G8; JK targets AugSynth point path | W8 unsafe stratum; small n_mc | **Diagnostic-only** | `jk_unsafe_under_diagnostics` | No promotion; per-cell only in multi-cell |
| **greedy unit-panel single-cell** | AugSynthCVXPY | Conformal | Effect-scale bands → outcome (post F-INF-003) | Conformal failure-001 · AUGSYNTH-003 | **needs_targeted_review** (panel conformal) | Band construction / exchangeability mismatch | Degenerate/over-wide bands | **Blocked** | `conformal_blocked_pending_new_design` | New interval design PR — not rerun old battery |
| **multi-cell unit-panel (per cell)** | AugSynthCVXPY | point | Per-cell level point (S0) | P6 · D5-MCELL (SCM+JK) · pooling ADR | **needs_targeted_review** (multi-arm geo) | Same G4/G7/G8 per cell | **No AugSynth multi-cell OC at ASCM-003 depth** | **Per-cell diagnostic** (S0) | Pooling ADR gates | **`D5-INST-AUGSYNTH-MULTICELL-001`** gate validation only |
| **multi-cell unit-panel (per cell)** | AugSynthCVXPY | UnitJackKnife | Per-cell JK diagnostic | P4 · pooling ADR | **needs_targeted_review** | Per-cell W8 class | No pooled JK OC | **Per-cell diagnostic-only** | No pooled uncertainty rule | MCELL OC: per-cell JK arms only; forbid pooled FPR |
| **multi-cell unit-panel (pooled descriptive)** | AugSynthCVXPY | point (aggregate) | Equal-cell **level** mean — **non-causal** (S1) | Pooling ADR §7–§10 | **needs_targeted_review** | Harness `pooling_rule_id` wiring | S1 metadata regression tests | **Conditional descriptive** | Any §9 cell fail → no S1 | MCELL OC assert S1 metadata; never headline lift |
| **multi-cell unit-panel (pooled)** | AugSynthCVXPY | Conformal / pooled JK | — | Pooling ADR §8 | **blocked** | — | Forbidden outputs | **Forbidden** | No inference pooling ADR | Do not test in MCELL OC |
| **aggregate 2-row (1 treated + 1 control)** | TBR | point | Aggregate post contrast | TBR-001 | **needs_targeted_review** (TBR geo lift) | Unit TBR blocked by assert | Aggregate-only OC done | **Restricted diagnostic** | ≠ unit SCM estimand | TBR aggregate charter; no unit-panel promotion |
| **aggregate 2-row / agg2 power path** | TBRRidge | Kfold / BRB / TS-Kfold | Pooled CF / agg contrast | TBRRIDGE-001/003 · POW-001c | **needs_targeted_review** (TBRRidge vs TBR) | TBR vs TBRRidge product conflation | JK/JKP high null FPR (A16/A21) | **Restricted diagnostic** | Scale ≠ SCM+JK | POW/readout alignment ADR; JK calibration doc |
| **aggregate 2-row / agg2** | TBRRidge | UnitJackKnife / JKP | Pooled-CF semantics | TBRRIDGE-003 | **needs_targeted_review** | F-INF-002 pooled-CF path | ~79% / ~29% null FPR characterization | **Callable unverified** | Not governed | Failure-mode doc; not MMM |
| **aggregate 2-row** | SCM / AugSynth | UnitJackKnife | — | COMBO-001 · D3 | **blocked** | Invalid 2-row tensor for unit SCM JK | Not characterized | **Invalid by interface** | Geometry mismatch | Catalog clarity only |
| **supergeo MILP output** | SCM / AugSynth | any | Supergeo contrast TBD | SUPERGEO-001 · A29 | **needs_targeted_review** (aggregation estimand) | No panel builder; MILP scope mismatch | No valid 001e-style OC | **Blocked** | F-GEO-003 bridge absent | Supergeo bridge charter before any AugSynth claim |
| **trimmedmatch (Tp/Te)** | SCM / AugSynth | any | Trim-pair population | TRIM-001 · A30 | **needs_targeted_review** (trimmed matching) | No flat unit panel | No AugSynth OC | **Blocked** | F-GEO-004 bridge absent | Trim bridge charter |
| **tier-1 geo (stratified / balanced / thinning / rerandomization)** | SCM + JK | UnitJackKnife | Same as greedy when pre-period honored | POW-001e · D1 | **aligned** (design randomization lit) | Design-stage vs readout-stage (MAT-004) | AugSynth not OC-validated | **Governed (SCM+JK)** / AugSynth **structural only** | Readout bridge | **D5-INST-AUGSYNTH-DESIGN-COMPAT-001** optional |
| **tier-1 geo + multi-cell** | SCM + JK | UnitJackKnife | Per-cell null monitor | D5-MCELL-001 | **needs_targeted_review** | k≥3 degraded | AugSynth per-cell OC gap | **Per-cell governed (SCM+JK)** | Pooled SCM claims need separate policy | MCELL OC for AugSynth only (not SCM promotion) |
| **completerandomization / rerandomization_wrapper** | SCM / AugSynth | point / JK | Same as base design | 001e · D1 | **needs_targeted_review** (rerandomization inference) | Wrapper vs bare greedy sensitivity | Bare vs wrapped OC thin | **SCM+JK governed**; AugSynth diagnostic on greedy path only | Non-greedy AugSynth OC | Design-compat OC if extending AugSynth |
| **unit-panel** | DID | native bootstrap | Relative ATT (cumulative CI partial) | A25 · COMBO | **needs_targeted_review** (DID panel) | Relative CI deferred (DEF-003) | Partial characterization | **Restricted diagnostic** | Not geo SCM estimand | DID interval policy — parallel lane |
| **unit-panel** | SyntheticDID / TROP / MTGP | various | Research estimands | D2 inventory | **needs_targeted_review** | **evidence_missing** OC | No governed path | **Research only** | No production metadata | Defer — not foundation-critical |

---

## 5. Literature alignment queue

**Not a full paper review.** Targeted checks only where internal evidence is blocked, ambiguous, or extrapolating beyond characterized DGPs.

| Topic | Why needed | Feeds |
|-------|------------|-------|
| **SCM inference / placebo / jackknife assumptions** | A26 governed as null-monitor; placebo scope A27/A28; JK validity under panel dependence | Maintain A26 labels; placebo taxonomy ADR |
| **Augmented synthetic control inference** | AugSynth point promising but estimand ≠ A26; JK unsafe on shock stratum | `METHOD_LITERATURE_GAP_REVIEW_001`; estimand bridge ADR |
| **Conformal inference for panel / time-series synthetic controls** | Conformal blocked — exchangeability + construction mismatch | New interval design spec (post P5) |
| **Multi-arm / multi-cell geo experiments** | Per-cell vs pooled semantics now in pooling ADR; need external support for S0/S1 v0 | MCELL OC interpretation; future causal pool ADR |
| **TBR / time-based regression geo lift** | Aggregate 1×1 restricted; conflation with TBRRidge | TBR aggregate strengthening; POW alignment |
| **Supergeo / aggregation estimand** | MILP output ≠ unit panel; no bridge | F-GEO-003 / supergeo charter |
| **Trimmed matching / donor selection** | Tp/Te population ≠ SCM donor pool | F-GEO-004 / trim charter |
| **Rerandomization-based inference** | Wrapper vs bare design for inference calibration | Design-compat OC prioritization |

---

## 6. Implementation gap register

Exact gaps **already documented** — status as of synthesis date.

| gap_id | Description | Status | Source | Next artifact |
|--------|-------------|--------|--------|---------------|
| **IMPL-D1-001** | Default pipeline may still pass full panel to matching if caller omits `pre_treatment_period` | **Mitigated** when pre-period passed; **caller responsibility** remains | D1 audit · INV-D1-001 | Document in design-compat harness; not silent fix in synthesis PR |
| **IMPL-G1-001** | `penalty` / `penalty_strength` stored but **not applied** on OSQP SCM leg | **Open** (low) | Fidelity G1 | Metadata disclosure; optional API cleanup |
| **IMPL-G4-001** | D5-DIAG `scm_pre_rmse` uses **SciPy SCM** while AugSynth inner leg is **CVXPY** | **Open** (medium disclosure) | Fidelity G4 | Optional harness: CVXPY SCM for D1 baseline |
| **IMPL-G7-001** | Level point readout vs relative `summary` / percent injection mismatch | **Open** | Fidelity G7 · D5-AS-FIND-004 | `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` |
| **IMPL-G8-001** | Hull diagnostic = z-distance **proxy**, not convex hull | **Open** | Fidelity G8 | ASCM-003 threshold calibration (ongoing) |
| **IMPL-JK-001** | AugSynth+JK unsafe on **post-period shock** stratum | **Open** — blocks promotion | JK calibration-001 | Inference repair lane decision (later) |
| **IMPL-CONF-001** | Conformal band construction / residual exchangeability mismatch | **Open** — blocked | Conformal failure-001 | New conformal design PR |
| **IMPL-MCELL-001** | Pooled causal estimand absent except **descriptive v0** | **Governed** by pooling ADR | Pooling ADR | Wire `pooling_rule_id` in harness when MCELL OC lands |
| **IMPL-SGEO-001** | Supergeo MILP / panel bridge; no `control`/`test_*` dict | **Open** | SUPERGEO-001 | F-GEO-003 adapter / charter |
| **IMPL-TRIM-001** | Trim design flat SCM tensor invalid | **Open** | TRIM-001 | F-GEO-004 bridge |
| **IMPL-TBR-001** | TBR vs TBRRidge naming and product conflation | **Open** (documentation) | CV-EST-TBR · D2 | Maintain labels in LLM-ready facets |
| **IMPL-POW-001** | PowerAnalysis **TBRRidge agg2** vs final **SCM+JK** readout | **Open** | POW-001a/c | `POWER_READOUT_ALIGNMENT_ADR_001` |
| **IMPL-FINF-003** | Conformal orientation fix applied | **Resolved** | F-INF-003 | Does not unblock governed export |
| **IMPL-UJK-002** | TBRRidge pooled-CF multi-treated JK interface | **Resolved** (structural); semantics **unverified** | F-INF-002 · TBRRIDGE-003 | Separate from AugSynth lane |

**UnitJK “target” issue:** No open **AugSynth-path** target bug documented post F-INF-002 for TBRRidge pooled-CF. AugSynth+JK risk is **calibration / stratum safety** (IMPL-JK-001), not a missing JK target implementation on the greedy unit-panel path.

---

## 7. Development sequencing decision

### Question

Continue immediately with **`D5-INST-AUGSYNTH-MULTICELL-001`**, or pause for **`METHOD_LITERATURE_GAP_REVIEW_001`**?

### Decision

**Proceed with `D5-INST-AUGSYNTH-MULTICELL-001`** — **only** as **narrow ADR-gate validation**, not as AugSynth promotion or broad multi-cell characterization.

| Allowed in MCELL OC | Forbidden in MCELL OC |
|---------------------|------------------------|
| **S0** per-cell AugSynth point + full D5-DIAG per cell | Pooled **causal** lift / ATT / MMM-ready effect |
| **S1** descriptive pooled row when **all** §9–§10 gates pass + metadata schema | Pooled JK / Conformal **uncertainty** or FPR |
| Regression: reject pooled output without `pooling_rule_id`; no partial pool | Promotion narrative; TrustReport / F-DECISION change |
| Per-cell A26 vs AugSynth comparator; k=2 primary | Using results to claim AugSynth **governed** baseline |
| Verdict taxonomy: `per_cell_only`, `descriptive_pool_eligible`, `blocked_cell_failures` | k≥3 as production-default without degraded label |

**Do not pause DL-1 follow-on for a full literature review first** — BLK-MCELL-001 is addressed by the **ordered** [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) (per [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md)); land that ADR before or in parallel with MCELL OC. Literature review is **parallel** ([`METHOD_LITERATURE_GAP_REVIEW_001`](#8-next-roadmap)) and targets inference/design assumptions that MCELL OC **does not resolve**.

**Do not use D5-MCELL to claim AugSynth promotion** — promotion audit remains closed (ASCM-003, lane closeout).

---

## 8. Next roadmap

| Order | Artifact | Role |
|-------|----------|------|
| **1** | ✅ **`METHOD_FOUNDATION_SYNTHESIS_001`** (this doc) | Single foundation map + sequencing decision |
| **2** | **`D5-INST-AUGSYNTH-MULTICELL-001`** | ADR-gate validation only (S0/S1; no pooled causal/uncertainty) |
| **3** | **`METHOD_LITERATURE_GAP_REVIEW_001`** | Targeted §5 queue — **not** blocking MCELL gate OC |
| **4** | **`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`** | Level/relative + aggregate/unit (G7) — recommended before causal language expands |
| **5** | **`D5-INST-AUGSYNTH-DESIGN-COMPAT-001`** | Non-greedy tier-1 geo AugSynth OC parity (optional) |
| **6** | **Decision checkpoint** | After MCELL + lit review: remain **diagnostic-only** vs open **Conformal repair lane** |

**Parallel foundation (not DL-1 immediate):** supergeo/trim bridge charters · `POWER_READOUT_ALIGNMENT_ADR_001` · `INFERENCE_ROLE_TAXONOMY_ADR_001`.

---

## 9. Guardrails

- **No promotion** of AugSynth or any inference arm  
- **No eligibility** or F-DECISION-001 change  
- **No governed-uncertainty allowlist** change  
- **No TrustReport / F-DECISION** behavior change  
- **No CalibrationSignal / MMM** change  
- **No LLM integration** (AUDIT-011 paused)  
- **No new OC** in this PR  
- **No new framework categories** unless reconciling existing evidence (this doc **consolidates**, does not add layers)  
- **No pooled multi-cell causal claim** without future ADR + OC  
- **No pooled uncertainty** until separate JK/Conformal decisions  

---

## 10. Stop condition

| Criterion | Status |
|-----------|--------|
| Single synthesis artifact maps design × estimator × inference | ✅ §4 |
| Prior audits reused without redoing work | ✅ §2 |
| Stable conclusions stated | ✅ §3 |
| Remaining gaps enumerated (conceptual / implementation / lit / OC) | ✅ §5–§6 |
| MCELL proceed / pause decision recorded | ✅ §7 — **proceed as gate validation only** |
| Roadmap docs updated | ✅ companion PR updates |

---

*METHOD-FOUNDATION-SYNTHESIS-001 v1.0.0 — checkpoint only; authoritative eligibility remains F-DECISION-001 and AUDIT-010.*
