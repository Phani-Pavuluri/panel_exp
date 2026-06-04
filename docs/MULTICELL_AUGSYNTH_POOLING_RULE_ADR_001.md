# MULTICELL-AUGSYNTH-POOLING-RULE-ADR-001

**Document ID:** MULTICELL-AUGSYNTH-POOLING-RULE-ADR-001  
**Type:** Architecture Decision Record — **multi-cell AugSynth/ASCM pooling semantics**  
**Status:** **accepted** (docs-only)  
**Date:** 2026-06-03  
**Supersedes:** implicit per-cell-only posture in P6 / F-P0-006 / E-DES-MCELL-011 (AugSynth-scoped specialization)

**Governed `pooling_rule_id` (this ADR):** `MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` — **descriptive summary only**; not a causal lift or uncertainty rule.

**Primary inputs:** [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) · [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md) · [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md) · [`track_d/D5_MCELL_001_REPORT.md`](track_d/D5_MCELL_001_REPORT.md) · [`ROADMAP_DESIGN_READOUT_UPDATE_001.md`](ROADMAP_DESIGN_READOUT_UPDATE_001.md)

**Related governance:** F-P0-006 · F-GEO-001 · AUDIT-010 · E-DES-MCELL-011 · F-DECISION-001

---

## 1. Purpose

Define **governed semantics** for any future **pooled multi-cell AugSynth/ASCM claim**.

P6 ([`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md)) found multi-cell AugSynth readout is **`compatible_unit_panel_per_cell_only`** and pooled claims are **`requires_multi_cell_pooling_rule`**. This ADR must land **before** [`D5-INST-AUGSYNTH-MULTICELL-001`](track_d/) so multi-cell OC does not produce impressive numbers without a defined estimand.

**This ADR does not:** promote AugSynth, authorize governed uncertainty, or open an OC battery.

---

## 2. Background from P6

| Finding | Implication |
|---------|-------------|
| Verdict `compatible_per_cell_only_pooling_blocked` | Per-cell unit-panel AugSynth is structurally valid; pooled claims blocked |
| Multi-cell = `n_test_grps > 1` on tier-1 geo methods | Not a separate design class |
| Donor pool per cell = **shared control only** (other test cells excluded) | Same contract as D5-POW-001e / D5-MCELL-001 |
| Only **`greedy_match_markets`** OC-validated for AugSynth | Multi-cell AugSynth OC not yet run at ASCM-003 depth |
| JK = `jk_unsafe_under_diagnostics` (P4) | No pooled JK uncertainty |
| Conformal = `conformal_blocked_pending_new_design` (P5) | No pooled Conformal uncertainty |
| Estimand G7 (level vs relative) unresolved | Pooling must not mix estimands |

Existing repo policy (F-P0-006, E-DES-MCELL-011) already blocks pooled multi-cell claims without `pooling_rule_id`. This ADR supplies the **AugSynth-specific rule** that ID may reference.

---

## 3. Scope and non-goals

### In scope

- Multi-cell geometry (`n_test_grps > 1`) on **tier-1 geo-run-supported** designs
- AugSynthCVXPY **point** readout per cell
- Optional **descriptive** pooled summary under strict gates
- Per-cell D5-DIAG + E-DES-MCELL diagnostic requirements
- Implications for future **`D5-INST-AUGSYNTH-MULTICELL-001`**

### Out of scope

| Non-goal | Notes |
|----------|-------|
| **SCM+JK / A26 pooled multi-cell** | Separate instrument; 001e/MCELL characterized under SCM+JK |
| **TBRRidge agg2 / power pooled metrics** | Requires [`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) |
| **supergeos / trimmedmatch** | Separate bridge charters |
| **Promotion, eligibility, TrustReport, CS/MMM** | Guardrailed |
| **OC execution** | Next PR after this ADR |
| **Code / harness changes** | Unless later PR wires `pooling_rule_id` |

---

## 4. Definitions

| Term | Definition |
|------|------------|
| **Cell** | One test group `test_k` (k ∈ {0,…,K−1}) vs shared **control** in multi-cell assignment |
| **Multi-cell geometry** | Design output with `n_test_grps > 1` |
| **Per-cell panel** | Unit-level wide panel for one cell: treated units in `test_k`, donors = control units only |
| **Multi-cell AugSynth claim** | Any statement about AugSynth readout spanning more than one cell |
| **Per-cell diagnostic readout** | AugSynth point (± D5-DIAG) reported independently per `test_k` |
| **Pooled descriptive summary** | Non-causal aggregate of per-cell **point** diagnostics (see §7) |
| **Pooled causal / lift claim** | Any pooled ATT, lift %, significance, or MMM-ready effect |
| **Pooled uncertainty** | Any interval, CI, null FPR, or coverage claim on a pooled multi-cell statistic |
| **`pooling_rule_id`** | Governed identifier on DesignProfile / readout hints authorizing a specific pooling semantics (F-GEO-001) |

### Core questions — short answers

| # | Question | Answer |
|---|----------|--------|
| 1 | What is a “multi-cell AugSynth claim”? | Any AugSynth statement beyond a single `test_k` panel |
| 2 | Independent, family, or pooled estimand? | **Family of per-cell diagnostics by default**; one optional **descriptive** pool (not causal) |
| 3 | What pooled estimand allowed? | **None for causal lift**; optional **equal-weight mean of per-cell level point effects** for descriptive triangulation only |
| 4 | Pool across channels/strategies/geos? | **No** unless cells share one design draw, one estimand, one pre/post window, and one donor contract |
| 5 | Allowed weighting? | Descriptive pool: **equal-cell only** in v0; all other weights **forbidden** |
| 6 | Per-cell diagnostics before pooled summary? | Full D5-DIAG + E-DES-MCELL gates (§9) |
| 7 | One cell passes, one fails? | **No pooled summary**; report per-cell only |
| 8 | Uncertainty if JK diag-only, Conformal blocked? | **No pooled uncertainty**; per-cell JK diagnostic-only if at all |
| 9 | Forbidden claims? | §8 |
| 10 | What must MCELL OC test? | §12 |

---

## 5. Candidate pooling semantics

| ID | Semantics | Status |
|----|-----------|--------|
| **S0 — Per-cell only (default)** | Each cell is an independent diagnostic readout; no cross-cell aggregation | **Accepted — default** |
| **S1 — Descriptive equal-cell mean (v0)** | `mean_k(point_effect_k)` on **level** point effects; label `descriptive_not_causal`; requires §9–§10 gates | **Accepted — conditional** under `pooling_rule_id=MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` |
| **S2 — Treated-unit-weighted mean** | Weight cells by treated unit count or spend | **Rejected** (v0) — see §6 |
| **S3 — Pre-period outcome-weighted** | Weight by pre-period scale | **Rejected** (v0) — estimand ambiguity vs G7 |
| **S4 — Pooled causal ATT** | Single estimand for experiment-wide lift | **Rejected** — requires separate estimand ADR + OC |
| **S5 — Pooled JK / Conformal uncertainty** | Interval on pooled statistic | **Rejected** — inference blocked |

---

## 6. Rejected pooling semantics

| Semantics | Reason |
|-----------|--------|
| **Spend-weighted / revenue-weighted pooling** | Confounds design balance with business weights; not identified in geo SCM panel |
| **Treated-unit-weighted pooling** | Cells with more treated markets dominate; hides per-cell failure (D5-MCELL shared-control stress) |
| **Pre-period outcome-weighted pooling** | Mixes scale normalization with treatment effect; conflicts with fidelity audit G7 (level vs relative) |
| **Pooling across unrelated experiments** | Cells from different design draws, windows, or design methods |
| **Pooling across channels/strategies without design co-assignment** | Not a single multi-cell geometry; estimand undefined |
| **Implicit “overall lift” from cell means** | Product-facing causal language forbidden without estimand bridge + OC |
| **Pooled null FPR / coverage** | No `pooling_rule_id` exists for inference; JK unsafe strata (P4); Conformal blocked (P5) |
| **Pooling when any cell fails §9 gates** | Would aggregate incompatible or failed diagnostics |
| **k ≥ 3 without D5-MCELL re-characterization** | D5-MCELL-001: k≥3 degrades per-cell null behavior |

---

## 7. Allowed claims

### Always allowed (default: S0)

| Claim | Conditions |
|-------|------------|
| **Per-cell AugSynth point effect** | Unit panel per cell; donors ≥ 5; D5-DIAG emitted |
| **Per-cell diagnostic labels** | Provisional threshold categories; not finalized |
| **Per-cell comparison to A26** | Diagnostic comparator; note `conflict_vs_a26` |
| **Per-cell “promising / caution / block” narrative** | ASCM-003-style; not promotion |
| **Family-of-cells report** | Table of per-cell rows; **no** single pooled headline number |

### Conditionally allowed (S1 — descriptive only)

**Requires** `pooling_rule_id: MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` **and** all §9–§10 gates.

| Claim | Wording requirement |
|-------|---------------------|
| **Equal-cell mean of per-cell level point effects** | Must include: `descriptive_not_causal`, `pooling_rule_id`, `per_cell_gates_passed` |
| **Directional triangulation summary** | e.g. “m of n cells show positive point comparator” — counts only, not lift |

**Hard limits on S1:**

- **k ≤ 2** unless D5-MCELL-001 (or successor) re-characterizes higher k for the design method
- Same **design_method**, **pre/post window**, **percent_effect calibration** (if any), **estimand=level point** across cells
- **No** interval, **no** “significant overall effect”, **no** MMM ingress

---

## 8. Forbidden claims

Until a **future** causal pooling ADR + OC exist, the following are **forbidden** for AugSynth multi-cell:

| Forbidden claim | Policy hook |
|-----------------|-------------|
| **Pooled lift / ATT / incremental revenue** | No causal estimand defined |
| **Pooled null FPR or “experiment-wide null rejected”** | No inference pooling rule |
| **Pooled confidence / credible / conformal interval** | JK diagnostic-only; Conformal blocked |
| **CalibrationSignal or MMM-ready pooled effect** | Scale + estimand mismatch |
| **TrustReport primary or governed uncertainty export** | F-DECISION unchanged |
| **Promotion of AugSynth based on pooled multi-cell OC** | Promotion audit not opened |
| **Pooling when `pooling_rule_id` absent** | F-P0-006 / E-DES-MCELL-011 |
| **Pooling across supergeo / trim / aggregate geometries** | P6 bridge required |
| **Headline “overall AugSynth result” without rule ID and gates** | Misleading estimand |

---

## 9. Required per-cell diagnostics

Before **any** multi-cell AugSynth output (per-cell or pooled descriptive), **each cell** must emit:

### D5-DIAG (AugSynth panel — [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py))

| Field / check | Gate |
|---------------|------|
| `diagnostics_feasible == 1` | Required |
| `donor_sparsity_n_control >= 5` | Required (harness default) |
| `scm_pre_rmse`, `augsynth_pre_rmse`, `fit_improvement_rmse` | Required numeric |
| `hull_min_donor_z_distance` | Required; **severe outside-hull** → cell fails |
| Weight concentration / effective donors | Required when weights available |
| `scale_bridge_pre_std_ratio`, `conflict_vs_a26` | Required for cross-method context |
| `false_confidence_flag`, `narrow_interval_poor_fit_flag` | Required when inference arms run |
| **Blocked run** (`blocked_reason` set) | Cell **fails** — no contribution to pool |

**Severe failure (cell fails, no pool):**

- `blocked_insufficient_donors` or CVXPY unavailable
- Outside-hull stress beyond provisional “caution” band (ASCM-003 W3 class)
- `false_confidence_flag == 1` on that cell
- Post-period shock stratum unsafe for JK on that cell (P4 W8 class) — blocks JK on cell; does not alone block point if other gates pass

### E-DES-MCELL (design geometry — Track E inventory)

| ID | Requirement |
|----|-------------|
| E-DES-MCELL-001 | Method supports requested k |
| E-DES-MCELL-004 | Shared-control adequacy |
| E-DES-MCELL-005 | Donors = control only per cell |
| E-DES-MCELL-007 | Per-cell null behavior characterized (001e/MCELL) where null OC run |
| E-DES-MCELL-008 | Treatment-cell conflict flagged if directional disagreement |
| E-DES-MCELL-009 | Multiple-comparison warning when k > 1 |
| E-DES-MCELL-010 | Minimum viable controls per cell |
| E-DES-MCELL-012 | k within recommended max (typically **≤ 2**) |

---

## 10. Required pooled-summary diagnostics

Pooled descriptive summary (S1) is **reportable only if**:

| Gate | Rule |
|------|------|
| **All cells pass §9** | 100% of included cells |
| **Homogeneous estimand** | All cells: level point effect from same AugSynth summary path |
| **Homogeneous geometry** | Same design draw, window, design_method |
| **`pooling_rule_id` set** | `MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` |
| **Explicit non-causal label** | `descriptive_not_causal: true` in metadata |
| **Cell inclusion manifest** | List `test_k` included/excluded with reason |
| **Conflict disclosure** | E-DES-MCELL-008 status across cells |
| **No uncertainty fields** | Pooled row must not include CI, p-value, FPR, coverage |

**Pooled-summary metadata (required):**

```yaml
pooling_rule_id: MULTICELL_AUGSYNTH_DESCRIPTIVE_V0
pooling_semantics: equal_cell_mean_level_point
descriptive_not_causal: true
n_cells_requested: K
n_cells_included: m
n_cells_failed_gates: K - m
weighting: equal_cell_only
uncertainty: none
```

If **any** cell fails §9 → **omit pooled row entirely** (do not partial-pool).

---

## 11. Failure handling

| Scenario | Required behavior |
|----------|-------------------|
| **Cell A passes, Cell B fails §9** | Report A only; **no** S1 pooled row |
| **Cells disagree in sign (E-DES-MCELL-008)** | Per-cell report; S1 allowed only with conflict flag in metadata; **forbid** causal interpretation |
| **One cell outside hull (W3-class)** | Exclude from pool; if only one cell remains, no pool |
| **JK unsafe on one cell (W8-class)** | JK diagnostic for that cell only; **does not** authorize pooled JK |
| **Conformal run on any cell** | Diagnostic context only; **no** pooled conformal band |
| **k > recommended max (D5-MCELL)** | Per-cell research-only; **no** S1 |
| **Missing `pooling_rule_id`** | Per-cell only (S0); governance block on pooled fields |

**Product narrative rule:** Never substitute a pooled descriptive mean for a failed cell.

---

## 12. Implications for OC

**`D5-INST-AUGSYNTH-MULTICELL-001`** (next code PR, not this ADR) must:

| Test obligation | Detail |
|-----------------|--------|
| **Default arm** | S0 per-cell AugSynth point + full D5-DIAG on k=2 (and optionally k=1 baseline) |
| **Design methods** | Start with **`greedy_match_markets`**; extend only after design-compat OC |
| **Donor contract** | Control-only donors per cell (match 001e) |
| **Worlds** | ASCM-003-relevant strata: hull, weak-fit, sparse donor, shock (per-cell) |
| **S1 descriptive arm** | Only emit pooled row when **all** §9–§10 gates pass; assert metadata schema |
| **Forbidden OC outputs** | Pooled lift claim; pooled JK FPR; pooled Conformal coverage |
| **Regression checks** | Harness rejects pooled output without `pooling_rule_id`; partial-pool forbidden |
| **Comparison** | Per-cell A26 vs AugSynth point; JK per-cell diagnostic-only |
| **k sweep** | Align with D5-MCELL-001 (k=2 primary; k≥3 labeled degraded) |
| **Verdict taxonomy** | e.g. `per_cell_only`, `descriptive_pool_eligible`, `blocked_cell_failures` — not promotion |

**Must not test before this ADR:** Any pooled causal estimand or pooled uncertainty.

---

## 13. Decision

**Accepted:**

1. **Multi-cell AugSynth is per-cell diagnostic by default (S0).**
2. **No pooled lift / causal claim is allowed** under this ADR.
3. **Pooled descriptive summary (S1)** may be reported **only if** every included cell has compatible geometry, donors ≥ 5, matching **level** point estimand, passes §9, and k ≤ characterized max — under `pooling_rule_id=MULTICELL_AUGSYNTH_DESCRIPTIVE_V0`.
4. **Pooled uncertainty is not allowed** — JK remains diagnostic-only (P4); Conformal blocked (P5).
5. **Any future pooled causal claim** requires a **new ADR**, [`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md), and its **own OC** — not implied by S1.

**Default posture for F-DECISION / TrustReport / catalog:** Unchanged — AugSynth `diagnostic_comparator`; multi-cell remains **per-cell only** in product unless profile explicitly sets `pooling_rule_id=MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` **and** readout metadata satisfies §10 (descriptive-only path).

---

## 14. Required next artifact

**`D5-INST-AUGSYNTH-MULTICELL-001`** — stratified multi-cell AugSynth OC harness implementing S0 default and S1 gated descriptive arm per this ADR.

**Prerequisite chain:**

1. ✅ This ADR  
2. **`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`** (recommended before causal language expands; not blocking S0 per-cell OC)  
3. **`D5-INST-AUGSYNTH-MULTICELL-001`**

---

## 15. Guardrails

- **No promotion** of AugSynth or inference arms
- **No eligibility** or F-DECISION-001 change
- **No governed-uncertainty allowlist** change
- **No TrustReport / F-DECISION** behavior change in this PR
- **No CalibrationSignal / MMM** change
- **No LLM integration**
- **No OC** in this PR
- **No code** unless required for doc generation
- **No pooled multi-cell causal claim** without future ADR + OC
- **No pooled uncertainty** until JK/Conformal lanes unblock with separate decisions

**Stop condition met:** Governed semantics for future pooled multi-cell AugSynth claims are defined; multi-cell OC may proceed without inventing estimands at runtime.
