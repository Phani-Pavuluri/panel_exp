# Track D D1 — Design and matching correctness audit 001

**Document ID:** TRACK-D-D1-DESIGN-MATCHING-001  
**Type:** Research-lane audit / ADR  
**Status:** **complete (D1 package v1)** — findings are **not** production-promotion evidence  
**Date:** 2026-05-28  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ `7af9ef9` (post AUDIT-004 / M2.2)  
**Lane:** **Research / robustness** per [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D  

**Authoritative inputs:**

| Document | Role |
|----------|------|
| [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) | Lane rules, stop conditions, forbidden promotions |
| [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) | Inventory rows DES-*, MAT-*, DG-007 |
| [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) | Literature families §3.3, §3.8 (rerandomization / geo design) |
| [`audits/AUDIT-004_m2_2_trust_report_gate.md`](audits/AUDIT-004_m2_2_trust_report_gate.md) | Production Track B gate passed; D1 eligible |

**Related code (read-only review):** `panel_exp/design/` · [`assign.py`](../panel_exp/design/assign.py) · [`geo_runner.py`](../panel_exp/design/geo_runner.py) · [`validation.py`](../panel_exp/design/validation.py) · [`constraints.py`](../panel_exp/design/constraints.py) · [`registry.py`](../panel_exp/design/registry.py) · [`trimmed_match.py`](../panel_exp/design/trimmed_match.py) · [`supergeos.py`](../panel_exp/design/supergeos.py)

---

## ADR decision record

| Field | Value |
|-------|--------|
| **Context** | Track B contracts (M2.2) govern identity and TrustReport boundaries but do not prove design/matching correctness. |
| **Decision** | Execute D1 as a **documented audit package** with governed findings; **no** code changes to assignment, matching, estimators, inference, eligibility, maturity, or release gates in D1. |
| **Consequences** | Inventory robustness statuses updated for design/matching rows; several findings escalated to `investigating` / `deferred`; D5 design OC and D2 donor-pool audits required before promotion discussion. |
| **Alternatives rejected** | Silent fixes during audit (forbidden); promoting DES-001/TBR path from literature alone (forbidden); feeding MMM/planning (forbidden). |

---

## 1. Executive summary

D1 reviewed **geo-run-supported design methods** (DES-001–005, DES-010–011, DES-013) and **design-phase matching** (MAT-001–003, MAT-007). **Estimator-embedded donor matching** (MAT-004, MAT-005) is **out of scope** — deferred to **D2** per matrix.

**Headline:** Constraint handling and post-assignment validation (DG-007) are **partially sound**, but **design–analysis period alignment** for market matching is **not guaranteed** on the default GeoX pipeline: `run_geo_experiment_design` calls `assign(..., treatment_period=None, pre_treatment_period=None)`, while `greedy_match_markets` balances using **full-panel** KPI trajectories unless callers pass an explicit pre-period slice.

**Overall D1 verdict (research lane):** `continue_with_characterization_required` — no method promotion; no TrustReport or eligibility changes.

| Metric | Count |
|--------|-------|
| Design rows in scope | 9 active + 3 deferred (DES-014–015, non-geo) |
| Matching rows in scope | 4 (MAT-001–003, MAT-007) |
| Findings registered | 9 (see §8) |
| Rows advanced to `characterization_required` | 4 |
| Rows remaining `unreviewed` | 5 (non-geo or thin usage) |

---

## 2. Scope and non-goals

### In scope

- Assignment algorithms used by `GeoExperimentDesign` / `run_geo_experiment_design`
- Greedy market matching and constraint semantics
- Rerandomization wrapper behavior (DES-010)
- Post-assignment validation gate (DES-013 / DG-007)
- Literature cross-check **requirements** for design/matching (not full D0b re-execution)
- Robustness status updates on inventory rows
- Required **D5** simulations (specified, not run in D1)

### Out of scope (explicit)

| Exclusion | Owner |
|-----------|--------|
| Estimator / inference code changes | — forbidden in D1 |
| Matching behavior changes | — forbidden in D1 |
| MAT-004, MAT-005 (SCM donors) | D2 |
| EST-*, INF-* | D2, D3 |
| POW-* | D4 |
| Instrument promotion / demotion | D7 |
| MMM / planning / CalibrationSignal feed | Forbidden |
| TrustReport rule changes | Track B only |
| Production decision eligibility | Not granted by D1 |

---

## 3. Audit method

1. **Inventory join** — Map each DES/MAT row to implementation entry points (D0 matrix §5–6).  
2. **Code trace** — Assignment → validation → evidence → spec (`geo_runner`, `assign.py`, `validation.py`, `constraints.py`).  
3. **Literature checklist** — Apply D0b §3.3 (TBR/matched markets), §3.8 (rerandomization/geo design) as pass/fail/unknown.  
4. **Test cross-check** — `tests/test_design_validation_gate.py`, `tests/test_design_registry.py` (structural only; not OC).  
5. **Risk classification** — R5 design risks per matrix Appendix B.  
6. **Governance** — Every finding gets disposition per matrix §13.

**No runtime OC** was executed in D1; simulation requirements are specified for D5.

---

## 4. Design method audit inventory

**Geo-run allowlist:** `greedy_match_markets`, `thinningdesign`, `balancedrandomization`, `completerandomization`, `stratifiedrandomization` ([`registry.py`](../panel_exp/design/registry.py) `LEGACY_GEO_RUN_DESIGN_SUPPORTED`).

| ID | Implementation | D1 review depth | Correctness checks (summary) | Literature (D0b) | **Robustness status (post-D1)** |
|----|----------------|-----------------|------------------------------|------------------|--------------------------------|
| **DES-001** | `greedy_match_markets` | Deep | See §5.1 | §3.3 TBR / matched markets | **characterization_required** |
| **DES-002** | `thinningdesign` | Light (code scan) | Pre-period params exist; geo path same null-period call | Geo design (generic) | **implementation_review_required** |
| **DES-003** | `balancedrandomization` | Light | Unit-level balance; rerandomization wrapper | Randomization §3.8 | **implementation_review_required** |
| **DES-004** | `completerandomization` | Light | IID assignment; constraint-aware | Randomization §3.8 | **implementation_review_required** |
| **DES-005** | `stratifiedrandomization` | Light | Strata assignment; not geo-audited end-to-end | Stratified §3.8 | **unreviewed** |
| **DES-006–009** | QuickBlock, MatchedPair, TrimmedMatch, Supergeos | N/A (not geo-run) | Registry only | Per family | **unreviewed** (defer until productized) |
| **DES-010** | `Rerandomization` wrapper | Medium | Wraps base design; imbalance on eval period | Rerandomization §3.8 | **characterization_required** |
| **DES-011** | Whitelist / blacklist | Medium | `constraints.py` semantics tested indirectly | Constraint validity | **restricted** |
| **DES-012** | TC ratio optimization | Not audited | — | D4 | **unreviewed** |
| **DES-013** | `validate_design` | Medium | PASS/WARN/FAIL; SRM, SMD, constraints | Eligibility / design validity | **restricted** |
| **DES-014–015** | Heavy-up, multi-cell | Deferred | Track C | — | **unreviewed** |

---

## 5. Matching algorithm audit inventory

| ID | Description | D1 depth | **Robustness status (post-D1)** | D0b / next |
|----|-------------|----------|-----------------------------------|------------|
| **MAT-001** | Greedy market matching (in DES-001) | Deep | **characterization_required** | §3.3 |
| **MAT-002** | Trimmed match pairing | Registry / skim | **unreviewed** | §3.3 (defer; DES-008 not geo-run) |
| **MAT-003** | Correlation / pre-period KPI matching | Partial | **implementation_review_required** | §3.3 |
| **MAT-004** | SCM donor pool | Out of scope | **math_review_required** | §3.1 → **D2** |
| **MAT-005** | SCM CVXPY weights | Out of scope | **math_review_required** | §3.1 → **D2** |
| **MAT-006** | Supergeo cluster | Skim | **unreviewed** | Defer with DES-009 |
| **MAT-007** | Spend/outcome covariate matching | Docs / product | **unreviewed** | §3.3 |

---

## 6. Per-method audit cards

### 6.1 DES-001 / MAT-001 — `greedy_match_markets`

**Intent (literature):** Matched-market style geo experiments pair markets on pre-treatment outcomes before treatment; analysis (TBR) assumes design–analysis alignment ([`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) §3.3).

**Implementation facts:**

- Greedily adds DMAs to control/test to optimize correlation, DTW, or L2 imbalance on **aggregated unit time series** (`assign.py`, `corr_func` / `sales_df = wide.T`).
- `treatment_probability` enforced via **KPI mass share** (`test_grps_share`), not unit count — intentional for media geo but changes classical “50% of units” interpretation.
- Constraints: `prepare_constraint_context` pins whitelists; blacklists exclude units ([`constraints.py`](../panel_exp/design/constraints.py)).

**Correctness checklist**

| Check | Status | Notes |
|-------|--------|-------|
| Units assigned exactly once | **pass** | Enforced by constraint prep + validation |
| Whitelist/blacklist respected | **pass** | `constraints.py` + tests |
| Pre-treatment-only matching | **unknown / fail-risk** | Geo runner passes `pre_treatment_period=None`; matching uses full `wide` unless caller overrides |
| Design before outcomes (causal timing) | **unknown** | Same period issue |
| Reproducible with `random_state` | **pass** | `self._rng` on design instance |
| Multi-test-group geometry | **partial** | `n_test_grps` supported; Track B geometry rules apply at analysis (GOLD-010) |
| Spillover reviewed | **warn** | Spec interference field; not estimated in design |

**Mathematical / conceptual risks**

| Risk | Severity | Description |
|------|----------|-------------|
| R5-01 | **high** | Full-panel matching when post-treatment data present in `wide_data` → **look-ahead** in market selection |
| R5-02 | medium | KPI-mass vs unit-count treatment fraction mismatch vs classical randomization |
| R5-03 | medium | Greedy local optimum; no global optimality guarantee |
| R5-04 | low | Correlation on summed series hides unit heterogeneity |

**Literature grounding needs (D0b)**

- Complete §3.3 record for DES-001: `decision` target **`needs_characterization`** until D5 design OC.
- Document deviation: mass-based treatment share vs unit randomization.

**Required simulations (D5 — not executed in D1)**

| Sim ID | Purpose |
|--------|---------|
| D5-DES-001a | Pre-period-only vs full-panel matching → bias in post-period ATT read |
| D5-DES-001b | Constraint stress (whitelist/blacklist saturation) |
| D5-DES-001c | Multi-test-group balance vs Track B `geometry_class` exports |

---

### 6.2 DES-010 — `Rerandomization` wrapper

**Implementation:** `GeoExperimentDesign.create_design()` always returns `Rerandomization` around `base_randomizer_cls` ([`geo_experiment_design.py`](../panel_exp/design/geo_experiment_design.py)).

**Correctness checklist**

| Check | Status | Notes |
|-------|--------|-------|
| Iteration cap / target imbalance | **pass** | `max_iter`, `target_imbalance` |
| Eval period for imbalance | **unknown** | Inherits base `assign` period semantics |
| Seed propagation | **partial** | `random_state` forwarded via kwargs |

**Risks:** R5-05 medium — rerandomization improves balance on chosen metric but does not fix pre-period leakage if eval period includes post-treatment data.

**D5:** D5-DES-010a — rerandomization gain distribution vs no-rerandomization under geo DGP.

---

### 6.3 DES-011 — Assignment constraints

**Semantics (documented in `constraints.py`):** Pin whitelists; exclude blacklists; reject impossible overlaps.

| Check | Status |
|-------|--------|
| Conflicting whitelist | **pass** (raises) |
| `control_test_blacklist` | **pass** |
| Free-pool feasibility | **pass** (raises when exhausted) |

**Status:** **restricted** — usable with explicit constraint documentation in ExperimentSpec / design evidence.

---

### 6.4 DES-013 / DG-007 — `validate_design`

**Checks observed:** duplicate assignment, unknown units, SRM unit share, KPI mass balance, SMD thresholds, min units, interference WARN paths ([`validation.py`](../panel_exp/design/validation.py)).

| Check | Status | Notes |
|-------|--------|-------|
| Blocks invalid assignments | **pass** | `test_design_validation_gate.py` |
| Detects gross imbalance | **pass** | SRM WARN |
| Validates pre-period-only design | **fail-gap** | No check that matching used pre-period only |
| Spillover | **warn-only** | Appropriate for design stage |

**Status:** **restricted** — diagnostic gate, not proof of causal design validity.

**Literature:** Eligibility / design validity (not matched-market completeness).

---

### 6.5 DES-002–005 — Other geo-run randomizers

**Light review:** Thinning, balanced, complete, and stratified designs use the same `Design.assign` contract; geo pipeline still passes **null** treatment/pre-treatment periods.

| ID | Post-D1 status | Next |
|----|----------------|------|
| DES-002 | implementation_review_required | Deep D1b or D5 |
| DES-003 | implementation_review_required | D5 |
| DES-004 | implementation_review_required | D5 |
| DES-005 | unreviewed | D1b pass |

---

### 6.6 MAT-002, MAT-006, MAT-007 — Non-geo or product-only

No geo-run path audited. Remain **unreviewed** until registered for `GeoExperimentDesign` or documented product API.

---

## 7. Cross-cutting findings

### 7.1 Design–analysis period alignment (platform-level)

| Item | Detail |
|------|--------|
| **Observation** | `run_geo_experiment_design` → `assign(..., treatment_period=None, pre_treatment_period=None)` while `ExperimentSpec` records `pre_period=TimePeriod(0, train_length)` |
| **Impact** | Market matching and imbalance metrics may use post-treatment columns if present in `panel_data.wide_data` |
| **Track B** | Does not detect this; adapter/export can still be `complete` with wrong design |
| **TrustReport** | Must not claim design validity without explicit scenario — **no change in D1** |
| **Disposition** | **investigating** → propose INV or DEF in follow-up (no code change in D1) |

### 7.2 Rerandomization + greedy match stack

Default geo path: `Rerandomization` → `greedy_match_markets`. Literature expects balance on **pre-treatment** features; platform must document actual eval window.

### 7.3 Validation vs matching

DG-007 validates **assignment integrity**, not **matching algorithm correctness** relative to TBR literature.

### 7.4 Track B handoff (no bypass)

| Track B artifact | D1 relationship |
|----------------|-----------------|
| `ExperimentSpec.design_method` | Records chosen DES-* ID |
| `ExperimentEvidence` validation_summary | Carries DG-007 output |
| TrustReport | **Does not** infer design validity; scenarios must be declared |
| `measurement_instrument_id` | Unchanged by D1 |

---

## 8. Finding register (governance)

| Finding ID | Summary | Severity | Disposition | Owner package |
|------------|---------|----------|-------------|---------------|
| **D1-FIND-001** | Geo runner null `pre_treatment_period` → full-panel matching risk | high | **investigating** | D1 → DEF/INV + design fix proposal (not in D1) |
| **D1-FIND-002** | KPI-mass treatment share vs unit-count semantics | medium | **accepted_deviation** | Document in D0b §3.3 for DES-001 |
| **D1-FIND-003** | DG-007 does not assert pre-period-only matching | medium | **deferred** | D6 or D1b validation extension |
| **D1-FIND-004** | Greedy match local optimum / no global pairing guarantee | low | **accepted_deviation** | Literature + D5 |
| **D1-FIND-005** | DES-005 stratified geo path not deeply reviewed | low | **deferred** | D1b |
| **D1-FIND-006** | MAT-004/005 donor logic un audited (SCM) | high | **deferred** | **D2** |
| **D1-FIND-007** | Non-geo designs (TrimmedMatch, Supergeos) un audited | low | **deferred** | When productized |
| **D1-FIND-008** | Rerandomization eval period inherits full-panel risk | medium | **investigating** | Linked to D1-FIND-001 |
| **D1-FIND-009** | No design-phase OC archive | medium | **deferred** | **D5** D5-DES-* sims |

**Promotion rule:** None of the above may advance instrument or decision eligibility. Dispositions feed matrix only.

---

## 9. Literature cross-check requirements (D0b execution backlog)

Fill or update YAML records in [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) §4 index:

| Inventory ID | Required D0b action | Target decision (after D5) |
|--------------|---------------------|----------------------------|
| DES-001 | Complete §3.3 checklist + deviation note (KPI mass) | `needs_characterization` → `aligned_with_deviation` or `restricted` |
| DES-010 | Add rerandomization record §3.8 | `needs_characterization` |
| DES-011 | Constraint validity mini-record | `aligned` |
| DES-013 | Design validation gate record | `aligned_with_deviation` |
| MAT-001 | Alias of DES-001 §3.3 | Same as DES-001 |
| MAT-003 | Correlation matching record | `needs_characterization` |

**Forbidden:** Setting `aligned` or `decision_eligible` from literature alone.

---

## 10. Required simulations (D5 specification)

| Sim ID | Methods | Success criteria (draft) |
|--------|---------|-------------------------|
| D5-DES-001a | DES-001 | ATT bias |pre-only − full-panel| < ε under synthetic DGP |
| D5-DES-001b | DES-001 | Zero blacklist violations; 100% whitelist compliance |
| D5-DES-001c | DES-001 | Multi-test export geometry matches assignment |
| D5-DES-010a | DES-010 | Imbalance distribution vs baseline randomization |
| D5-DG-007a | DES-013 | Validation catches injected assignment bugs (regression) |

Archive results under future `TRACK_D_OC_ARCHIVE_*` — not part of D1.

---

## 11. Robustness matrix updates (D1)

Updates applied in [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) §5–6 (2026-05-28 D1 pass).

**Summary**

| Status | Design (geo) | Matching (D1 scope) |
|--------|--------------|---------------------|
| characterization_required | DES-001, DES-010 | MAT-001 |
| restricted | DES-011, DES-013 | — |
| implementation_review_required | DES-002, DES-003, DES-004 | MAT-003 |
| unreviewed | DES-005–009, DES-012, DES-014–015 | MAT-002, MAT-006, MAT-007 |
| math_review_required (D2) | — | MAT-004, MAT-005 |

**Coverage matrix (design family):** Reviewed **9** / 15 inventoried; **0** decision-eligible.

---

## 12. Next actions

| Priority | Action | Lane | Stop condition |
|----------|--------|------|----------------|
| P0 | Open DEF/INV for D1-FIND-001 (pre-period matching) | Research → fix proposal | Documented root cause + approved fix plan |
| P1 | Run D5-DES-001a/b/c OC | Research | Archived OC + matrix row update |
| P1 | Complete D0b YAML for DES-001, MAT-001 | Research | `decision` field set with evidence refs |
| P2 | **D2** estimator audit (MAT-004, MAT-005, EST-*) | Research | D2 package |
| P2 | D1b light pass on DES-005 | Research | Row not `unreviewed` |
| P3 | Track D D1b or D6: extend DG-007 pre-period check | Research | D1-FIND-003 closed or deferred with ADR |

**Forbidden next actions:** Promote TBR/SCM instruments; change TrustReport rules; enable MMM feed; modify estimators under D1 guise.

---

## 13. Sign-off

| Role | Statement |
|------|-----------|
| **D1 audit** | Package complete; research-lane only |
| **Production lane** | Unchanged — Track B M2.2 opt-in export remains bounded |
| **Track D D2** | **Authorized to start** (estimator/matching math) in parallel with D5 design OC |

---

*TRACK-D-D1-DESIGN-MATCHING-001 v1.0.0 — research lane — 2026-05-28*
