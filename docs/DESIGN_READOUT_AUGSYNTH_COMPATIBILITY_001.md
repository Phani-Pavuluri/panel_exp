# DESIGN-READOUT-AUGSYNTH-COMPATIBILITY-001

**Document ID:** DESIGN-READOUT-AUGSYNTH-COMPATIBILITY-001  
**Type:** Design / readout compatibility audit — **AugSynth/ASCM scoped**  
**Status:** **complete** (docs-only)  
**Date:** 2026-06-03  
**Branch context:** `audit/design-readout-augsynth-compatibility-001` (after P3–P5 stack)

**Overall verdict:** `compatible_per_cell_only_pooling_blocked`  
**Co-verdict (geometry bridges):** `bridge_required_before_broader_use`

**Primary inputs:** [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) · [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md) · [`track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md) · [`track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md`](track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md) · [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md)

**Code references:** [`panel_exp/design/registry.py`](../panel_exp/design/registry.py) · [`panel_exp/design/modes/__init__.py`](../panel_exp/design/modes/__init__.py) · [`panel_exp/validation/scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py) · [`panel_exp/validation/track_d_d5_inst_augsynth_ascm_003.py`](../panel_exp/validation/track_d_d5_inst_augsynth_ascm_003.py)

---

## 1. Purpose

Map **actual repo-supported design geometries** to **AugSynthCVXPY / ASCM readout** validity after D5-DIAG, ASCM-003, JK calibration (P4), and Conformal failure analysis (P5).

This audit answers where AugSynth/ASCM may be used as **diagnostic unit-panel readout**, where use is **per-cell only**, where **bridges or pooling rules** are required, and where readout is **blocked** — without promoting AugSynth, changing eligibility, changing F-DECISION, or wiring anything into TrustReport, CalibrationSignal, or MMM.

**This is not another OC battery.** It classifies compatibility from registry, inventory, harness patterns, and completed validation artifacts.

---

## 2. Evidence base

| Source | Role in this audit |
|--------|-------------------|
| **Design registry** (`get_design_registry().list_names()`, `geo_supported_names()`) | Authoritative design names and geo-run allowlist |
| **TRACK-D-DESIGN-INVENTORY-001** | Tier buckets, multi-cell geometry definition, supergeo/trim exclusions for SCM+JK |
| **D5-DIAG** (`scm_augsynth_diagnostics.py`) | Required diagnostic field schema for AugSynth panels |
| **ASCM-003** | Point + JK OC on `greedy_match_markets` unit panels; W11 multi-treated; verdict `promising_needs_inference_calibration` |
| **JK calibration (P4)** | Verdict `jk_unsafe_under_diagnostics`; unsafe stratum `W8_post_period_shock` |
| **Conformal failure (P5)** | Verdict `conformal_blocked_pending_new_design`; interval miscalibration / over-wide bands |
| **Fidelity audit** | G7 estimand (level vs relative); G4 donor rules; no silent promotion path |
| **METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001** | Aggregate agg2 vs unit-panel split; TBRRidge power path |

**OC evidence scope:** All P3–P5 batteries use **`greedy_match_markets`** (or `rerandomization_wrapper` over greedy in 001e-style paths) → `_build_unit_panel` → `AugSynthCVXPY`. Other tier-1 geo methods are **structurally analogous** (unit assignment dict) but **not yet OC-validated** for AugSynth.

---

## 3. Scope and non-goals

### In scope

- Registered design methods and production orchestration paths (`GeoExperimentDesign` / `run_design`)
- Geometry modes: single-cell unit panel, multi-treated unit panel, multi-cell per-cell, aggregate power paths, supergeo, trimmed match
- AugSynth readout tiers: **point**, **UnitJackKnife**, **Conformal** (compatibility only — not safety certification)
- D5-DIAG diagnostic availability per geometry
- Estimand and scale risks vs A26 / MMM

### Out of scope (explicit non-goals)

| Non-goal | Reason |
|----------|--------|
| **Promotion** or role upgrade | F-DECISION-001 / AUDIT-010 unchanged |
| **Eligibility or governed-uncertainty allowlist change** | No F-INF amendment |
| **Threshold finalization** | Provisional labels only |
| **Estimator or inference code change** | Docs-only PR |
| **TrustReport / F-DECISION / CalibrationSignal / MMM wiring** | Guardrailed |
| **New OC runs** for every design × geometry | Separate harness PRs if needed |
| **Pooled multi-cell claims** without governed pooling ADR | Blocked by policy |
| **Foundation-wide DESIGN_READOUT_COMPATIBILITY_AUDIT_001** | Parallel P2 artifact; this doc is **AugSynth-scoped** |

---

## 4. AugSynth readout requirements

AugSynth/ASCM readout in repo validation assumes the following **unit-panel contract**:

| Requirement | Source | Notes |
|-------------|--------|-------|
| **Wide unit × time panel** | ASCM-003 harness | One treated unit (or explicit multi-treated loop) vs donor pool |
| **Donor pool ≥ `min_donors`** | Default **5** in P3–P5 harnesses | Below threshold → `blocked_insufficient_donors` |
| **Fixed pre / post window** | 001e / ASCM-003 | Consistent with D5-DIAG fields |
| **Per-unit SCM fit** | `AugSynthCVXPY.fit_data` | Multi-treated = repeat per treated unit, not pooled CF by default |
| **D5-DIAG emission** | `compute_panel_scm_augsynth_diagnostics` | Pre RMSE, hull distance, weight concentration, scale bridge, disagreement, instrument flags |
| **CVXPY available** | `method_metadata` | Optional dependency; blocked if missing |

**Inference posture (from P4/P5, unchanged here):**

| Readout | Compatibility | Governed use |
|---------|---------------|--------------|
| **Point** | Callable on valid unit panels | `diagnostic_comparator` only |
| **UnitJackKnife** | Callable but **diagnostic only** | **Not** governed uncertainty; unsafe under shock stratum |
| **Conformal** | Callable in harness but **blocked for product claims** | `conformal_blocked_pending_new_design` |
| **Kfold** | Callable (ASCM-003 secondary arm) | Diagnostic only — out of table columns |

**Metadata gap:** Harnesses use `UnitJackKnife` on AugSynth; `method_metadata.inference_support` lists `point_estimate`, `Kfold`, `Conformal` only — catalog alignment is **`implementation_review_required`**, not a geometry block.

---

## 5. Design inventory inspected

### Registry (`get_design_registry().list_names()`)

| design_method | geo_run_supported | repo_entrypoint |
|---------------|-------------------|-----------------|
| `greedy_match_markets` | yes | `GeoExperimentDesign.run_design` → `run_geo_experiment_design` |
| `thinningdesign` | yes | same |
| `balancedrandomization` | yes | same |
| `completerandomization` | yes | same |
| `stratifiedrandomization` | yes | same |
| `quickblock` | no | design class direct; registry row only |
| `matchedpair` | no | design class direct; registry row only |
| `trimmedmatch` | no | `TrimmedMatchDesign` direct (`D5-DES-TRIM-001`) |
| `supergeos` | no | `SupergeoModel` direct (`D5-DES-SUPERGEO-001`) |

### Production orchestration (not a registry row)

| method_id | repo_entrypoint | Notes |
|-----------|-----------------|-------|
| `rerandomization_wrapper` | `GeoExperimentDesign.create_design()` → `Rerandomization(base_randomizer_cls=…)` in [`assign.py`](../panel_exp/design/assign.py) | Used in D5-POW-001e inventory; distinct from bare greedy in OC |

### Geometry modes (not separate design classes)

| Geometry | How produced | Repo name |
|----------|--------------|-----------|
| **Single-cell unit panel** | `n_test_grps=1` on tier-1 geo assignment | Default ASCM-003 path |
| **Multi-treated unit panel** | Multiple treated units, one test group | W11 in ASCM-003 (`fit_class=multi_treated`) |
| **Multi-cell per-cell** | `n_test_grps > 1` on tier-1 geo methods | Documented in DESIGN-INVENTORY; **not** a `multi_cell_multi_treated` class |
| **Aggregate 2-row (power / TBRRidge)** | D5-POW agg2 transform on designed units | **Not** AugSynth-native geometry |
| **Supergeo cluster** | `supergeos` MILP / cluster output | Separate geometry |
| **Trimmed pair population** | `trimmedmatch` Tp/Te pairs | Separate population |

---

## 6. Compatibility table

**Legend — readout columns:** `yes` = structurally callable on repo path with donors ≥ min; `diag_only` = callable for validation diagnostics, not governed/product; `blocked` = do not claim compatibility; `na` = geometry does not apply.

| design_method | repo_entrypoint | geometry | treatment_structure | compatible_with_augsynth_point | compatible_with_augsynth_jk | compatible_with_augsynth_conformal | required_diagnostics_available | estimand_risk | scale_risk | compatibility_status | required_next_artifact | notes |
|---------------|-----------------|----------|---------------------|-------------------------------|------------------------------|-----------------------------------|-------------------------------|---------------|------------|----------------------|------------------------|-------|
| `greedy_match_markets` | `GeoExperimentDesign.run_design` | single_cell unit panel | 1 test group vs shared control | yes | diag_only | blocked | yes (D5-DIAG on harness path) | medium — level ATT vs A26 relative path | high — systematic `conflict_vs_a26` at null | `compatible_unit_panel_single_cell` | — | **Only design OC-validated** for AugSynth P3–P5 |
| `rerandomization_wrapper` | `GeoExperimentDesign` + `Rerandomization` | single_cell unit panel | 1 test group; balance-constrained rerandomized assign | yes (structural) | diag_only | blocked | yes when panel builds | medium | high | `compatible_unit_panel_single_cell` | `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` | 001e confirms unit dict; AugSynth OC not rerun vs bare greedy |
| `completerandomization` | `GeoExperimentDesign.run_design` | single_cell unit panel | Bernoulli assign + constraints | yes (structural) | diag_only | blocked | yes when panel builds | medium | high | `compatible_unit_panel_single_cell` | `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` | Geo-run supported; no AugSynth OC yet |
| `balancedrandomization` | `GeoExperimentDesign.run_design` | single_cell unit panel | volume-balanced assign | yes (structural) | diag_only | blocked | yes when panel builds | medium | high | `compatible_unit_panel_single_cell` | `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` | Same as completerandomization |
| `stratifiedrandomization` | `GeoExperimentDesign.run_design` | single_cell unit panel | stratified + volume balance | yes (structural) | diag_only | blocked | yes when panel builds | medium | high | `compatible_unit_panel_single_cell` | `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` | Strata may affect donor composition — review in OC |
| `thinningdesign` | `GeoExperimentDesign.run_design` | single_cell unit panel | kernel-thinned assign | yes (structural) | diag_only | blocked | yes when panel builds | medium | high | `compatible_unit_panel_single_cell` | `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` | May reduce effective donors — watch `blocked_insufficient_donors` |
| `greedy_match_markets` (and tier-1 geo bases) | `GeoExperimentDesign.run_design` | multi_cell unit panel (`n_test_grps>1`) | test_0…test_k vs shared control | yes **per cell** | diag_only **per cell** | blocked | yes per cell if donors OK | **high** if pooled | high | `compatible_unit_panel_per_cell_only` | `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` · `D5-INST-AUGSYNTH-MULTICELL-001` | Partial harness in `track_d_d5_inst_augsynth_001/003`; **no pooled claim** |
| tier-1 geo (any) | power / MDE pipeline | aggregate_2row_tbrridge | treated vs control **aggregate series** | blocked | blocked | blocked | partial (unit diagnostics N/A on 2-row) | **high** — aggregate ATT ≠ unit AugSynth estimand | **high** — TBRRidge scale vs SCM | `requires_aggregate_to_unit_bridge` | `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` · `POWER_READOUT_ALIGNMENT_ADR_001` | D5-POW-001a agg2 path; planning readout ≠ AugSynth readout |
| `greedy_match_markets` | ASCM-003 harness | multi_treated unit panel | multiple treated units, single test group | yes (per treated unit) | diag_only | blocked | yes (W11 in ASCM-003) | medium — must not pool treated units | high | `compatible_unit_panel_single_cell` | — | W11 characterized; not multi-cell |
| `supergeos` | `SupergeoModel` direct | supergeo cluster / pair | cluster-level treatment | blocked | blocked | blocked | no on flat unit dict | high | high | `requires_supergeo_bridge` | `SUPERGEO_AUGSYNTH_BRIDGE_CHARTER_001` | D5-DES-SUPERGEO-001: separate geometry; not flat SCM panel |
| `trimmedmatch` | `TrimmedMatchDesign` direct | trimmed pair population | Tp/Te pairs post trim | blocked | blocked | blocked | no without bridge | high — trimmed estimand | high | `requires_trimmed_design_bridge` | `TRIMMED_DESIGN_AUGSYNTH_BRIDGE_CHARTER_001` | D5-DES-TRIM-001; own power semantics |
| `quickblock` | registry only | legacy block assign | block structure | na | na | na | no | unknown | unknown | `implementation_review_required` | — | Registered; **not** `geo_run_supported`; no production geo path |
| `matchedpair` | registry only | matched pairs | pair-level | na | na | na | no | unknown | unknown | `implementation_review_required` | — | Registered; **not** `geo_run_supported` |
| tier-1 geo (sparse draw) | any supported path | single_cell unit panel | 1 test group | blocked if donors < 5 | blocked if donors < 5 | blocked | blocked | — | — | `blocked_insufficient_donors` | — | Harness enforces `min_donors_augsynth=5`; W4s ultra-sparse stratum |
| any design | n/a | non-unit transformed panel | TBR 1×1 aggregate | blocked | blocked | blocked | no | **high** | **high** | `requires_estimand_bridge` | `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` | Class TBR aggregate ≠ AugSynth unit panel |
| tier-1 multi_cell | any | pooled multi_cell summary | cross-cell pooled ATT | blocked | blocked | blocked | no | **high** | high | `requires_multi_cell_pooling_rule` | `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` | Explicit policy block pending F-MCELL ADR |

---

## 7. Single-cell unit-panel compatibility

**Finding:** All **five geo-run-supported** registry designs plus **`rerandomization_wrapper`** produce assignment outputs that map to the **unit-panel** contract used in AugSynth validation harnesses (`_build_unit_panel` pattern in ASCM-003 / 001e).

| Status | Designs |
|--------|---------|
| **OC-validated** | `greedy_match_markets` only (P3–P5) |
| **Structurally compatible, OC pending** | `rerandomization_wrapper`, `completerandomization`, `balancedrandomization`, `stratifiedrandomization`, `thinningdesign` |
| **Point readout** | `compatible_unit_panel_single_cell` when donors ≥ 5 |
| **JK readout** | Callable **`diag_only`** — P4 `jk_unsafe_under_diagnostics` on `W8_post_period_shock` |
| **Conformal readout** | **`blocked`** — P5 `conformal_blocked_pending_new_design` |
| **MMM / CalibrationSignal** | **No claim** — scale and estimand mismatch vs A26 |

**Multi-treated (W11):** Still single-cell geometry (one test group, multiple treated units). Compatible **per treated unit** fit; do not pool treated units into one synthetic control target without an estimand ADR.

---

## 8. Multi-treated / multi-cell compatibility

### Multi-treated (single test group, multiple treated units)

- **Supported in repo:** yes — ASCM-003 world `W11_multi_treated_unit_panel`
- **Readout:** per-unit AugSynth fits; status `compatible_unit_panel_single_cell` (treatment structure is multi-unit, geometry is not multi-cell)
- **Pooling:** pooling treated units → `requires_estimand_bridge`

### Multi-cell (`n_test_grps > 1`)

- **Not a design class** — geometry flag on tier-1 geo methods (DESIGN-INVENTORY § Multi-cell)
- **Per-cell AugSynth:** `compatible_unit_panel_per_cell_only` — each test_k vs shared control is a valid unit panel if donors suffice
- **Pooled multi-cell claim:** **`requires_multi_cell_pooling_rule`** — no governed pooling rule in repo (`F-MCELL-001` / `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` not materialized)
- **OC status:** `track_d_d5_inst_augsynth_001.py` / `003.py` include `multi_cell_k2_per_cell` slices; **no** ASCM-003-scale multi-cell battery

---

## 9. Aggregate geometry incompatibilities

AugSynthCVXPY requires **unit-level** wide panels. The following are **not** directly compatible:

| Geometry | Typical path | Status |
|----------|--------------|--------|
| **TBRRidge agg2 (2-row power)** | D5-POW-001a / geo `PowerAnalysis` | `requires_aggregate_to_unit_bridge` |
| **Class TBR 1×1 aggregate** | Two aggregate series | `requires_estimand_bridge` |
| **Pooled counterfactual on TBRRidge** | A16/A21 paths | `blocked_unsupported_geometry` for AugSynth |

**Risk:** Using power/MDE instruments (agg2) as if they were AugSynth readout creates **planning vs measurement confusion** (GAP-ASCM-POW-001). Power planning may remain on agg2; AugSynth diagnostic readout must stay on **designed unit panels** unless a bridge ADR exists.

---

## 10. Supergeo and trimmed design bridge requirements

| Design | Why blocked for flat AugSynth | Bridge artifact |
|--------|------------------------------|-----------------|
| **`supergeos`** | Cluster/MILP pairing; output is not a flat unit assignment dict for SCM+AugSynth (D5-DES-SUPERGEO-001) | `SUPERGEO_AUGSYNTH_BRIDGE_CHARTER_001` |
| **`trimmedmatch`** | Tp/Te trimmed population; pair-level randomization and trim semantics (D5-DES-TRIM-001) | `TRIMMED_DESIGN_AUGSYNTH_BRIDGE_CHARTER_001` |

**No AugSynth product claim** on supergeo or trimmed designs until a charter defines: unit-panel extraction (or alternative estimand), donor rules, D5-DIAG mapping, and OC plan.

---

## 11. Inference compatibility

| Inference arm | Single-cell unit panel | Multi-cell per-cell | Governed export | Evidence |
|---------------|------------------------|---------------------|-----------------|----------|
| **AugSynth point** | Compatible (diagnostic) | Per-cell only | **No** | ASCM-003 `promising_needs_inference_calibration` |
| **AugSynth + UnitJackKnife** | Callable; **diag only** | Per-cell only | **No** | P4 `jk_unsafe_under_diagnostics`; W8 shock |
| **AugSynth + Conformal** | Callable in harness; **blocked for claims** | Per-cell only | **No** | P5 `conformal_blocked_pending_new_design`; over-wide bands |
| **A26 SCM + JK** | Reference null monitor | Per-cell in 001e | Governed baseline | Unchanged by this audit |

**Conclusion:** Even where geometry is compatible, **only point diagnostics** have partial positive OC; JK remains diagnostic-only with known unsafe strata; Conformal remains **blocked pending new design** (interval construction / exchangeability), not a geometry-only fix.

---

## 12. Estimand and scale risks

| Risk ID | Description | Affected designs / geometries | Mitigation artifact |
|---------|-------------|------------------------------|---------------------|
| **E1 — Level vs relative** | AugSynth point effect level vs A26 / geo relative ATT (fidelity G7) | All unit-panel paths | `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` |
| **E2 — Aggregate vs unit** | agg2 / TBR aggregate vs unit SCM | Power pipeline, TBR class | Estimand bridge + power alignment ADR |
| **E3 — Multi-cell pooling** | Cross-cell pooled ATT without rule | `n_test_grps > 1` | `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` |
| **E4 — Multi-treated pooling** | Multiple treated units summarized as one | W11-style designs | Per-unit fits only until ADR |
| **S1 — Scale vs A26** | Systematic point disagreement at null (`conflict_vs_a26`) | All compatible unit panels | D5-DIAG scale bridge; **not MMM-ready** |
| **S2 — MMM / CalibrationSignal** | AugSynth lift scale ≠ CS contract | All | **Blocked** — no CS/MMM claim from this lane |

---

## 13. Decision / verdict

### Primary verdict: `compatible_per_cell_only_pooling_blocked`

**Rationale:**

1. **Unit-panel single-cell** designs (tier-1 geo + rerandomization wrapper) are **structurally compatible** with AugSynth **point** diagnostic readout when donors ≥ 5; only **`greedy_match_markets`** is OC-validated today.
2. **Multi-cell** geometry supports **per-cell only** AugSynth diagnostics; **pooled multi-cell claims are blocked** pending a governed pooling rule.
3. **Inference:** JK is **diagnostic-only** with unsafe diagnostic strata (P4); Conformal is **blocked** (P5) regardless of compatible geometry.
4. **No MMM, CalibrationSignal, TrustReport, or F-DECISION** upgrade from this audit.

### Co-verdict: `bridge_required_before_broader_use`

Supergeo, trimmed match, aggregate/power (agg2), and cross-estimand comparisons require **explicit bridge charters/ADRs** before any broader AugSynth readout claim beyond tier-1 unit-panel diagnostics.

### Audit answers (core questions)

| # | Question | Answer |
|---|----------|--------|
| 1 | Unit-panel compatible designs? | Five geo-run methods + `rerandomization_wrapper` |
| 2 | Incompatible without bridge? | agg2/TBR aggregate, `supergeos`, `trimmedmatch` |
| 3 | Single-treated vs multi-treated? | Single-treated default; multi-treated per-unit (W11) |
| 4 | Per-cell multi-cell? | Yes, per-cell only |
| 5 | Pooling rule required? | Yes, for any pooled multi-cell claim |
| 6 | Donor sufficiency? | ≥ 5 controls (harness default); sparse → blocked |
| 7 | D5-DIAG available? | Yes on validated harness path; not on supergeo/trim/aggregate |
| 8 | Estimand mismatch? | Level vs relative; aggregate; pooling — see §12 |
| 9 | Scale mismatch vs MMM/CS? | High — no CS/MMM path |
| 10 | More work before ASCM-003-style OC on other designs? | Yes — recommend `D5-INST-AUGSYNTH-DESIGN-COMPAT-001` for non-greedy tier-1 |

---

## 14. Required next artifacts

Recommend **only where supported by this audit:**

| Artifact | Trigger | Priority |
|----------|---------|----------|
| **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** | Multi-cell pooled claims blocked | **High** |
| **`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`** | Level/relative + aggregate/unit gaps | **High** |
| **`SUPERGEO_AUGSYNTH_BRIDGE_CHARTER_001`** | `supergeos` separate geometry | Medium |
| **`TRIMMED_DESIGN_AUGSYNTH_BRIDGE_CHARTER_001`** | `trimmedmatch` separate population | Medium |
| **`D5-INST-AUGSYNTH-MULTICELL-001`** | Per-cell multi-cell OC at ASCM-003 depth | Medium |
| **`D5-INST-AUGSYNTH-DESIGN-COMPAT-001`** | OC parity for non-greedy tier-1 geo methods | Medium |

**Not recommended here:** Promotion audit, F-DECISION amendment, Conformal repair PR (pending P5 isolation — separate inference design work).

**Deferred (foundation P2, not duplicated):** `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` (all readouts), `POWER_READOUT_ALIGNMENT_ADR_001`, `F-MCELL-001`.

---

## 15. Guardrails

This audit and any follow-on work must **not**:

- Promote AugSynth or change method roles
- Change F-DECISION-001 eligibility or TrustReport behavior
- Add AugSynth to governed-uncertainty allowlist or CalibrationSignal / MMM
- Finalize diagnostic thresholds
- Change estimator or inference implementation
- Make **pooled multi-cell** AugSynth claims without `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`
- Make **aggregate-to-unit** AugSynth claims without `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`
- Make **supergeo** or **trimmed-design** AugSynth claims without respective bridge charters
- Invent design names not present in registry / inventory

**Stop condition met:** Repo now has a design/readout compatibility audit stating where AugSynth/ASCM is valid as diagnostic unit-panel readout, where per-cell only, where bridges are required, and where blocked.
